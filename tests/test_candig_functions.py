# -*- coding: utf-8 -*-

from mesi_search import candig
from requests.models import Response


def test_candig_datasets(mocker):
    """Testing the patching of the CanDIG API request with `datasets` call"""
    expected = ['WyJtb2NrMSJd', 'WyJtb2NrMiJd', 'WyJ0ZXN0MzAwIl0']

    def mock_req(url, json_data):  # mock api request for datasets call
        r = Response()
        r.status_code = 200
        r._content = b'{"status": {"Known peers": 1, "Queried peers": 1, ' \
                     b'"Successful communications": 1, "Valid response": true},' \
                     b' "results": {"datasets": [{"id": "WyJtb2NrMSJd", ' \
                     b'"name": "mock1", "description": "METADATA SERVER"}, ' \
                     b'{"id": "WyJtb2NrMiJd", "name": "mock2", ' \
                     b'"description": "METADATA SERVER"}, ' \
                     b'{"id": "WyJ0ZXN0MzAwIl0", "name": "test300", ' \
                     b'"description": "METADATA SERVER"}], "total": 3}}'
        return r

    mocker.patch(
        "mesi_search.candig.request",
        mock_req
    )

    actual = candig.datasets()
    assert expected == actual


def test_candig_raw_results(mocker):
    """Testing the patching CanDIG API request for `raw_results` call"""
    def mock_req(url, json_data):  # mock api request for raw results
        r = Response()
        r.status_code = 200
        r._content = b'{"status": {"Known peers": 1, "Queried peers": 1, ' \
                     b'"Successful communications": 1, "Valid response": true}, ' \
                     b'"results": {"patients": [{"dateOfBirth": {}, "causeOfDeath": ' \
                     b'{"Myocardial infarction": 4, "Sepsis": 3, "Cancer": 3, "Disease": 6, ' \
                     b'"Acute disease": 2, "Coronary artery disease": 3, "Diabetes mellitus": 3, ' \
                     b'"Infection": 5, "Lung cancer": 6, "Brain death": 3, "Complication": 2, ' \
                     b'"Cardiac arrest": 2, "Bleeding": 2, "Depression": 4, "Hypertension": 2, ' \
                     b'"Tuberculosis": 5, "Brainstem death": 2, "Stroke": 1, ' \
                     b'"Cardiovascular disease": 1, "Heart failure": 4, "Breast cancer": 2}, ' \
                     b'"autopsyTissueForResearch": {"n/a": 65}, "dateOfPriorMalignancy": ' \
                     b'{"n/a": 65}, "familyHistoryAndRiskFactors": {"n/a": 65}, ' \
                     b'"familyHistoryOfPredispositionSyndrome": {"n/a": 65}, ' \
                     b'"detailsOfPredispositionSyndrome": {"n/a": 66}, ' \
                     b'"geneticCancerSyndrome": {"n/a": 66}, ' \
                     b'"otherGeneticConditionOrSignificantComorbidity": {"n/a": 65}, ' \
                     b'"occupationalOrEnvironmentalExposure": {"Pollen": 8, "Formaldehyde": 1, ' \
                     b'"Lead": 7, "Ginkgo": 2, "Bisphenol A (BPA)": 6, "Radon": 3, ' \
                     b'"Climate Change": 2, "Mercury": 2, "Cockroaches": 1, "Water Pollution": 3,' \
                     b'"Harmful Algal Blooms": 2, "Cell Phones": 3,"Dust Mites": 3,"Dioxins": 2,' \
                     b'"Acrylamide": 3, "Electric & Magnetic Fields": 1, "Soy Infant Formula": 2,' \
                     b'"Styrene": 1, "Hazardous Material/Waste": 1, "Pets & Animals": 1, ' \
                     b'"Flame Retardants": 1, "Allergens & Irritants": 1, "Air Pollution": 1, ' \
                     b'"Arsenic": 2, "Nanomaterials": 2, "Perfluorinated Chemicals (PFCs)": 2, ' \
                     b'"Hexavalent Chromium": 1, "Essential Oils": 1}}]}}'
        return r

    mocker.patch(
        "mesi_search.candig.request",
        mock_req
    )

    actual = candig.raw_results(['WyJtb2NrMSJd', 'WyJtb2NrMiJd', 'WyJ0ZXN0MzAwIl0'])
    # check a couple of random keys in the response
    assert actual['WyJtb2NrMSJd']['results']['patients'][0]['causeOfDeath']['Cancer'] == 3
    assert actual['WyJtb2NrMSJd']['results']['patients'][0]['causeOfDeath']['Acute disease'] != 3

    assert actual['WyJtb2NrMiJd']['results']['patients'][0]['causeOfDeath']['Cancer'] == 3
    assert actual['WyJtb2NrMiJd']['results']['patients'][0]['causeOfDeath']['Acute disease'] != 3

    assert actual['WyJ0ZXN0MzAwIl0']['results']['patients'][0]['causeOfDeath']['Cancer'] == 3
    assert actual['WyJ0ZXN0MzAwIl0']['results']['patients'][0]['causeOfDeath']['Acute disease'] != 3


def test_candig_prepare_count_query():
    dataset_id = "qwerty123"
    query = candig.prepare_count_query(dataset_id)
    assert query["datasetId"] == dataset_id


def test_candig_filter():
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
    filtered_result = candig.data_filter(data=test_data, terms=["causeOfDeath"],
                                         path="/results/patients")
    assert filtered_result["dataset-1"]["causeOfDeath"]["Cancer"] == 32
    assert filtered_result["dataset-1"]["causeOfDeath"]["Heart"] == 23
    assert filtered_result["dataset-2"]["causeOfDeath"]["Cancer"] == 11
    assert filtered_result["dataset-2"]["causeOfDeath"]["Heart"] == 33


def test_candig_private_filter():
    """Test differentially private filter"""
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

    ps = candig.private_data_filter(data=test_data, terms=["causeOfDeath"],
                                    path="/results/patients")
    assert ps["dataset-1"]["causeOfDeath"]["Cancer"] != 0
    assert ps["dataset-2"]["causeOfDeath"]["Cancer"] != 0
