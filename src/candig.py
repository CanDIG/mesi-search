# -*- coding: utf-8 -*-
"""CanDIG API Requests"""

import json

import requests
from config import CANDIG_UPSTREAM_API

DEFAULT_HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


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
