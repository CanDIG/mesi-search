# -*- coding: utf-8 -*-
"""MESI application, main"""

import json
import logging

from flasgger import swag_from, Swagger
from flask import Flask, jsonify, render_template, request
from mesi_search import candig

logger = logging.getLogger(__name__)
APP = Flask(__name__)
SWAGGER_CONFIG = {
    "swagger": "2.0",
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/api"
}
SWAGGER = Swagger(APP, config=SWAGGER_CONFIG)


# TODO: Set the budget tied to session
# TODO: Set the budget dynamically if possible


@APP.route('/', methods=['GET'])
def home():
    """Home page"""
    return render_template("home.html")


@APP.route('/api/candig/patient', methods=['POST'])
@swag_from('resources/discovery.yaml', validation=True)
def discover_candig_patient():
    """Search endpoint to discover possible data sets available"""
    logger.info("Request for patient discovery endpoint")

    result = {}
    incoming_post_data = json.loads(request.data.decode("utf-8"))  # receives as bytes
    attribute_of_interest = incoming_post_data.get("attributesOfInterest", [])

    logger.debug("Chosen attributes of interest are {}".format(attribute_of_interest))

    # TODO: filter out results even prior for this view for better privacy
    candig_datasets = candig.datasets()
    raw_results = candig.raw_results(candig_datasets)
    # get the private data for attribute of interest
    private_filtered_data = candig.private_data_filter(data=raw_results,
                                                       terms=attribute_of_interest,
                                                       path="/results/patients")
    result = {"datasets": private_filtered_data}
    return jsonify(result)


if __name__ == '__main__':
    APP.run()
