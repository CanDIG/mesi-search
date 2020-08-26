# -*- coding: utf-8 -*-
import pytest


@pytest.fixture(scope="module")
def candig_raw_results():
    test_data = {
        "dataset-1": {
            "results": {
                "patients": [
                    {
                        "causeOfDeath": {
                            "Cancer": 32,
                            "Heart": 23,
                        }
                    }
                ]
            }
        },

        "dataset-2": {
            "results": {
                "patients": [
                    {
                        "causeOfDeath": {
                            "Cancer": 11,
                            "Heart": 33,
                        }
                    }
                ]
            }
        }
    }
    return test_data
