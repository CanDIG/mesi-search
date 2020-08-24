# -*- coding: utf-8 -*-
"""CanDIG API Requests

This is a very crude style of writing utility functions
to make API requests to CanDIG server. This could easily be
a Flask middleware as long as we define the interface. That
means, then it can be extended easily for other APIs that
provide data. Or perhaps some GA4GH API based middleware.
"""

import copy
import json
import logging
import math

import diffprivlib as dp
import dpath.util
import requests
from mesi_search.settings import CANDIG_UPSTREAM_API, DP_DELTA, DP_EPSILON

logger = logging.getLogger(__name__)
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
    @return: object that returns differentially private data
    only for the said `terms` (attrs of interest)
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
    @return: object that returns data only for the said `terms` (attrs of interest)
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
    """Returns IBM diff priv library's Laplace Mechanism object with epsilon
    and delta set

    @param epsilon: Differential privacy main parameter for privacy;
    lower means more privacy but less utility
    @param delta: Differential privacy parameter for purity of diff priv
    @return: IBM differential privact library's mechanism object
    """
    mech = dp.mechanisms.Laplace()
    mech.set_epsilon_delta(epsilon, delta)
    return mech


def get_sensitivity(data):
    """Calculates sensitivity needed for Laplace mechanism
    This sensitivity is calculated per attribute-of-interest, per dataset
    as the numbers vary depending on the attribute type

    @param data: object containing data per attr of interest per dataset
    value of `causeOfDeath` or `gender` in this example:
    ```
    {
    'dataset1': {
        'causeOfDeath': {...},
        'gender': {...},
      }
    }
    ```
    @return integer that denotes the sensitivity of the dataset
    """
    result = 1
    value_list = []
    for k, v in data.items():
        value_list.append(v)
    if value_list is not []:
        result = max(value_list) - min(value_list)  # crude sensitivity
    if result == 0:
        result = 1  # difference of 1 when there is nothing much to do
    return result


def randomize(mechanism, data):
    """Using the `mechanism` send the randomized data

    @param mechanism: IBM diff priv library mechanism object
    @param data: CanDIG v1 data
    @return: object of filtered and private data for each dataset
    """
    result = copy.deepcopy(data)
    for term, term_specific_data in data.items():
        mechanism.set_sensitivity(get_sensitivity(term_specific_data))
        for item, val in term_specific_data.items():
            result[term][item] = math.ceil(mechanism.randomise(val))
    return result


def raw_results(candig_datasets):
    """Fetch raw results from CanDIG API

    @param candig_datasets: list of dataset IDs from CanDIG to fetch results from
    @return: all the data for each dataset ID
    """
    collective_counts = {}
    for did in candig_datasets:
        query = prepare_count_query(did)
        if query is not {}:
            count_result = request(url="/count", json_data=query)
            collective_counts[did] = count_result.json()
        else:
            logger.error("Empty query received. You are likely missing dataset ID.")
    return collective_counts


def prepare_count_query(dataset_id=None):
    """CanDIG count endpoint needs some specific JSON

    @param dataset_id: alphanumeric ID from CanDIG
    @return: fully formed query that CanDIG API expects as data
    """
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
        logger.error("Dataset ID is missing. Please provide a dataset ID. "
                     "Returning empty base query.")
        base_query = {}
    return base_query


def datasets():
    """Fetch datasets from the CanDIG API

    @return: list of dataset IDs
    """
    dataset_query = json.dumps({"pageSize": 1000, "pageToken": 0})
    result = request(url="/datasets/search", json_data=dataset_query)
    result = result.json()  # result as dict
    datasets = dpath.util.get(result, "/results/datasets")
    dataset_ids = [d.get("id", None) for d in datasets if datasets]
    return dataset_ids


def request(url="/", json_data={}, headers=DEFAULT_HEADERS):
    """CanDIG API request

    @param url: CanDIG API URL segment (not the base domain)
    @param json_data: data that CanDIG API endpoint expects
    @param headers: headers that CanDIG API endpoint expects
    @return: CanDIG API response object (`requests`)
    """
    # TODO: Write better API calls, bubble up errors from upstream
    logger.info("CanDIG API call for {}".format(url))

    request_url = CANDIG_UPSTREAM_API + url
    result = requests.post(request_url, json=json_data, headers=headers)
    logger.info("CanDIG server returned {}".format(result.status_code))

    return result
