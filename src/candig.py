# -*- coding: utf-8 -*-
"""CanDIG API Requests"""

import json

import requests
from config import CANDIG_UPSTREAM_API


async def raw_results():
    task_datasets = candig_request("/datasets/search",  {"pageSize": 1000, "pageToken": 0})
    result = await task_datasets

    return result


async def candig_request(url, data, headers={"Accept": "application/json", "Content-Type": "application/json"}):
    """CanDIG API request"""
    request_url = CANDIG_UPSTREAM_API + url
    result = requests.post(request_url, json=json.dumps(data), headers=headers)
    return result
