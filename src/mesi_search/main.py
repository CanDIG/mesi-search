# -*- coding: utf-8 -*-
"""MESI application, main"""

import json

import candig
from flasgger import swag_from, Swagger
from flask import Flask, jsonify, render_template, request

swagger_config = {
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

app = Flask(__name__)
swagger = Swagger(app, config=swagger_config)


# TODO: Logging

@app.route('/', methods=['GET'])
def home():
    """Home page"""
    return render_template("home.html")


@app.route('/api/discover', methods=['POST'])
@swag_from('resources/discovery.yaml', validation=True)
def discover():
    """Search endpoint to discover possible data sets available"""
    incoming_post_data = json.loads(request.data.decode("utf-8"))
    attribute_of_interest = incoming_post_data.get("attributeOfInterest", None)
    search_term = incoming_post_data.get("term", None)

    # TODO: filter out results even prior for this view for better privacy
    raw_results = candig.raw_results()
    # get the data for attribute of interest
    filtered_data = candig.filter(raw_results, attribute_of_interest, "/results/patients")
    # get the private sum
    private_sum = candig.private_sum(raw_results, attribute_of_interest, "/results/patients")
    # calculate the percentage
    x = candig.percentage(filtered_data, private_sum, search_term)
    print("percentage: ", x)

    result = raw_results
    return jsonify(x)


if __name__ == '__main__':
    app.run()
