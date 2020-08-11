# -*- coding: utf-8 -*-
"""MESI application, main"""

import candig
from flasgger import swag_from, Swagger
from flask import Flask, jsonify, render_template

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
@swag_from('resources/discovery.yaml')
def discover():
    """Search endpoint to discover possible data sets available"""
    raw_results = candig.raw_results()
    result = raw_results
    return jsonify(result)


if __name__ == '__main__':
    app.run()
