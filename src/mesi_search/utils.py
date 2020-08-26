import logging
from functools import wraps

import jwt
from flask import request, Response, session

logger = logging.getLogger(__name__)


def get_jwt(req):
    """Checks Authorization: Bearer .... for JWT
    @param req: Flask `request` object
    @return: string of JWT or empty string
    """
    req_jwt = ""
    authorization_header = req.headers.get("Authorization", None)
    if authorization_header:
        try:
            req_jwt = authorization_header.split(" ")[1]  # first part is "Bearer "
        except IndexError as ie:
            logger.error("Authorization header is missing the JWT.", str(ie))
    return req_jwt


def check_jwt(req):
    """Check for JWT's validity

    @param req: Flask `request` object
    @return: boolean
    """
    is_request_authorized = False
    req_jwt = get_jwt(req)

    if req_jwt != "":
        try:
            _ = jwt.decode(req_jwt, verify=False)  # TODO: too bad, need to verify JWT
            is_request_authorized = True
        except jwt.InvalidIssuedAtError as iisa:
            logger.error("JWT has invalid Issued-At datetime ", str(iisa))
        except jwt.ExpiredSignatureError as es:
            logger.error("JWT has invalid or expired signature ", str(es))
        except jwt.DecodeError as d:
            logger.error("JWT could not be decoded for reasons ", str(d))
    return is_request_authorized


def authorize(f):
    """Decorator to check if request is authorized

    @param f: function that needs to be wrapped
    @return: wrapped function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_jwt(request):
            return Response("Missing valid authentication token. Please provide your "
                            "JWT in the Authorization header as Bearer token.", 401)
        else:
            logger.info("Authorized to make requests to the API")
            session["authorized"] = True
            session["user"] = get_jwt(request)
        return f(*args, **kwargs)

    return decorated_function
