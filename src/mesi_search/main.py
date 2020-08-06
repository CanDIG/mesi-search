# -*- coding: utf-8 -*-
"""MESI application, main
"""
from flask import Flask, jsonify, request, Response
from flasgger import swag_from, Swagger

app = Flask(__name__)
swagger = Swagger(app)


@swagger.definition('Pet')
class Pet(object):
    """
    Pet Object
    ---
    properties:
        name:
            type: string
    """
    def __init__(self, name):
        self.name = str(name)

    def dump(self):
        return dict(vars(self).items())


@app.route('/')
def home():
    return 'Welcome to MESI Search!'


@app.route('/discover', methods=['POST'])
@swag_from()
def discover():
    """
    aaaaaaaaaaaaaaaaaaaaaaaaaaaa
    ---
    description: Post a request body
    requestBody:
        content:
            application/json:
                schema:
                    $ref: '#/definitions/Pet'
        required: true
    responses:
        200:
            description: The posted request body
            content:
                application/json:
                    schema:
                        $ref: '#/definitions/Pet'
    """
    return jsonify(request.json)


if __name__ == '__main__':
    app.run()
