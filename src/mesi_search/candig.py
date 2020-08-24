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
from mesi_search.settings import CANDIG_UPSTREAM_API, DP_DELTA, DP_EPSILON
import copy
import math


DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def private_data_filter(data={}, terms=[], path=""):
    """Calculates the differentially private results for given attributes
    of interest in CanDIG data

    @param data: entire patient dataset for CanDIG v1
    @param terms: a list of attributes of interest to look for in the `data`
    @param path: path that represents the JSON data structure
    """
    filtered_results = data_filter(data, terms, path)
    private_filtered_results = {}

    mech = create_laplace_mechanism(DP_EPSILON, DP_DELTA)

    for dataset_id, dataset in filtered_results.items():
        private_filtered_results[dataset_id] = randomize(mech, dataset)
    return private_filtered_results


def data_filter(data={}, terms=[], path=""):
    """Return the subset of the key/value within a nested CanDIG data
    Uses `dpath` package that makes it easy to work with
    dicts using path-based access

    @param data: entire patient dataset for CanDIG v1
    @param terms: a list of attributes of interest to look for in the `data`
    @param path: path that represents the JSON data structure
    """
    filtered_result = {}
    if data and terms:
        for dataset_id in data:
            patients_data = dpath.util.get(data[dataset_id], path)
            if patients_data and len(patients_data) == 1:  # TODO: check for `>1`
                term_results = {}
                for term in terms:
                    term_results[term] = dpath.util.get(patients_data[0], term)
                filtered_result[dataset_id] = term_results
    return filtered_result


def create_laplace_mechanism(epsilon, delta=0.0):
    """Returns IBM diff priv library's Laplace Mechanism object"""
    mech = dp.mechanisms.Laplace()
    mech.set_epsilon_delta(epsilon, delta)
    return mech


def get_sensitivity(data):
    """Calculates sensitivity needed for Laplace mechanism
    This sensitivity is calculated per attribute-of-interest, per dataset
    as the numbers vary depending on the attribute type
    """
    result = 1
    value_list = []
    for k, v in data.items():
        value_list.append(v)
    if value_list is not []:
        result = max(value_list) - min(value_list)  # crude sensitivity
    if result == 0:
        result = 1
    return result


def randomize(mechanism, data):
    """Using the `mechamism` send the randomized data

    @param mechanism: IBM diff priv library mechanism object
    @param data: CanDIG v1 data
    """
    result = copy.deepcopy(data)
    for term, term_specific_data in data.items():
        mechanism.set_sensitivity(get_sensitivity(term_specific_data))
        for item, val in term_specific_data.items():
            result[term][item] = math.ceil(mechanism.randomise(val))
    return result


def raw_results(candig_datasets):
    """Fetch raw results from CanDIG API"""
    collective_counts = {}
    for did in candig_datasets:
        query = prepare_count_query(did)
        if query is not {}:
            count_result = request(url="/count", json_data=query)
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


def datasets():
    """Fetch datasets from the CanDIG API"""
    dataset_query = json.dumps({"pageSize": 1000, "pageToken": 0})
    result = request(url="/datasets/search", json_data=dataset_query)
    result = result.json()  # result as dict
    datasets = dpath.util.get(result, "/results/datasets")
    dataset_ids = [d.get("id", None) for d in datasets if datasets]
    return dataset_ids


def request(url="/", json_data={}, headers=DEFAULT_HEADERS):
    """CanDIG API request"""
    # TODO: Write better API calls, bubble up errors from upstream
    request_url = CANDIG_UPSTREAM_API + url
    result = requests.post(request_url, json=json_data, headers=headers)
    return result
