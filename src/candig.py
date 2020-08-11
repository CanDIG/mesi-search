# -*- coding: utf-8 -*-
"""CanDIG API Requests"""

import json

import diffprivlib as dp
import dpath.util
import requests
from config import CANDIG_UPSTREAM_API

DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def percentage(data={}, private_data={}, term=None):
    """finds the percentage of the term within the data,
    if the term exists"""
    perc = {}
    if data and private_data and term:
        for k in data:
            if term in data[k].keys():
                term_val = data[k].get(term, 0)
                priv_sum = private_data[k]
                if float(priv_sum) != 0.0:
                    perc[k] = 100 * term_val / priv_sum
                else:
                    perc[k] = 0
            else:
                pass
    return perc


def private_sum(data={}, term=None, path=""):
    priv_sum = {}
    acc = dp.BudgetAccountant(epsilon=12, delta=0.1)
    normal = filter(data, term, path)
    print("normal: ", normal)
    for k in normal:
        print("dataset: ", k)
        print("remaining priv: ", acc.remaining())
        print("spent budget: ", acc.spent_budget)
        upper_bound = sum(list(normal[k].values()))
        priv_sum[k] = dp.tools.sum(list(normal[k].values()), bounds=(0, upper_bound), accountant=acc)
        # print(normal[k].values())
        print("sum: ", upper_bound)
        print("private sum: ", priv_sum[k])
        print("===========================\n")
    print("\n\n")
    print(priv_sum)
    return priv_sum


def filter(data={}, term=None, path=""):
    """Return the subset of the key/value within a nested
    CanDIG data
    Uses `dpath` package that makes it easy to work with
    dicts using path-based access
    """
    filtered_result = {}
    if data and term:
        for k in data:
            patients_data = dpath.util.get(data[k], path)
            if patients_data and len(patients_data) == 1:  # TODO: check for >1
                filtered_result[k] = dpath.util.get(patients_data[0], term)
    return filtered_result


def raw_results():
    """Fetch raw results from CanDIG API"""
    dataset_query = json.dumps({"pageSize": 1000, "pageToken": 0})
    result = candig_request(url="/datasets/search", json=dataset_query)
    result = result.json()  # result as dict
    datasets_id = candig_datasets(result)

    collective_counts = {}
    for did in datasets_id:
        query = prepare_count_query(did)
        if query is not {}:
            count_result = candig_request(url="/count", json=query)
            collective_counts[did] = count_result.json()
    return collective_counts


def prepare_count_query(dataset_id=None):
    """CanDIG count endpoint needs some specific JSON"""
    base_query = {
        "logic": {
            "and": [
                {
                    "id": "A"
                }
            ]
        },
        "components": [
            {
                "id": "A",
                "outcomes": {
                    "filters": [
                        {
                            "field": "diseaseResponseOrStatus",
                            "operator": "==",
                            "value": "Complete Response"
                        }
                    ]
                }
            }
        ],
        "results": [
            {
                "table": "patients",
                "fields": [
                    "dateOfBirth",
                    "gender",
                    "ethnicity",
                    "race",
                    "provinceOfResidence",
                    "dateOfDeath",
                    "causeOfDeath",
                    "autopsyTissueForResearch",
                    "dateOfPriorMalignancy",
                    "familyHistoryAndRiskFactors",
                    "familyHistoryOfPredispositionSyndrome",
                    "detailsOfPredispositionSyndrome",
                    "geneticCancerSyndrome",
                    "otherGeneticConditionOrSignificantComorbidity",
                    "occupationalOrEnvironmentalExposure"
                ]
            }
        ]
    }

    if dataset_id:
        base_query.update({"datasetId": dataset_id})
    else:
        base_query = {}
    return base_query


def candig_datasets(dataset_search={}):
    datasets = dataset_search.get("results", {}).get("datasets", {})
    dataset_ids = [d.get("id", None) for d in datasets if datasets]
    return dataset_ids


def candig_request(url="/", json={}, headers=DEFAULT_HEADERS):
    """CanDIG API request"""
    request_url = CANDIG_UPSTREAM_API + url
    result = requests.post(request_url, json=json, headers=headers)
    return result
