# -*- coding: utf-8 -*-
"""CanDIG API Requests

This is a very crude style of writing utility functions
to make API requests to CanDIG server. This could easily be
a Flask middleware as long as we define the interface. That
means, then it can be extended easily for other APIs that
provide data. Or perhaps some GA4GH API based middleware.
"""

import json

import diffprivlib as dp
import dpath.util
import requests
from config import CANDIG_UPSTREAM_API, DP_EPSILON, DP_DELTA

DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def percentage(data={}, private_data={}, term=None):
    """finds the percentage of the term within the data,
    if the term exists"""
    result = {}
    term = str(term).lower()  # normalize

    if data and private_data and term:
        for dataset in data:
            # normalize keys to lowercase
            data[dataset] = {k.lower(): v for k, v in data[dataset].items()}

            if term in data[dataset].keys():  # checks for exact key for now
                term_val = data[dataset].get(term, 0)
                priv_sum = private_data[dataset]
                if float(priv_sum) != 0.0:
                    result[dataset] = 100 * term_val / priv_sum
                else:
                    result[dataset] = 0  # TODO: revisit because may impact utility
            else:
                pass
    return result


def private_sum(term=None, path="", data={}, dp_acc={}):
    """Calculate differentially private sum of the `attributeOfInterest`"""
    result = {}
    normal_data = filter(data, term, path)

    for attribute_item in normal_data:
        values = list(normal_data[attribute_item].values())
        lower_bound = min(values)
        upper_bound = sum(values)
        if dp_acc.remaining()[0] > 0:
            result[attribute_item] = dp.tools.sum(list(normal_data[attribute_item].values()),
                                                  bounds=(lower_bound, upper_bound), accountant=dp_acc)
        else:
            result[attribute_item] = 0
    return result


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
