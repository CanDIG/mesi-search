# -*- coding: utf-8 -*-
"""MESI application, main
TODO: Send only the data from attrs_of_interest back to avoid sending changing data
TODO: Add Dockerfile, docker-compose
"""

import json
import logging

from flasgger import swag_from, Swagger
from flask import Flask, jsonify, render_template, request, session
from flask_limiter import Limiter
from mesi_search import candig
from mesi_search.swagger import SWAGGER_TEMPLATE, SWAGGER_CONFIG
from mesi_search.utils import authorize, flask_limiter_key

APP = Flask(__name__)
logger = logging.getLogger(__name__)
limiter = Limiter(APP)
SWAGGER = Swagger(APP, config=SWAGGER_CONFIG, decorators=[], template=SWAGGER_TEMPLATE)


@APP.route('/', methods=['GET'])
def home():
    """Home page"""
    return render_template("home.html")


@APP.route('/api/candig/patient', methods=['POST'])
@limiter.limit("10/minute", key_func=flask_limiter_key)
@swag_from('resources/discovery.yaml', validation=True)
@authorize
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
    # save attributes of interest to session, as well as result this is to save
    # recalculation and send different data for the same user.
    # TODO: Save the session in persistent storage
    attrs_of_interest_from_session = set(session.get("attributes_of_interest", []))
    attrs_of_interest_from_session.update(attribute_of_interest)
    session["attributes_of_interest"] = list(attrs_of_interest_from_session)

    result = {"datasets": private_filtered_data}
    session["result"] = result

    return jsonify(result)


if __name__ == '__main__':
    APP.run()
