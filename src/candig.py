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
    result = candig_request("/datasets/search", {"pageSize": 1000, "pageToken": 0})
    return result


def candig_request(url, data, headers=DEFAULT_HEADERS):
    """CanDIG API request"""
    request_url = CANDIG_UPSTREAM_API + url
    result = requests.post(request_url, json=json.dumps(data), headers=headers)
    return result
