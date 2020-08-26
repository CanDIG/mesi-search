import logging
from functools import wraps

import jwt
from flask import request, Response, session

logger = logging.getLogger(__name__)


def flask_limiter_key():
    limiter_key = None
    sub = session.get("sub", None)
    if sub:
        limiter_key = sub
    return limiter_key


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


def decode_jwt(req):
    decoded_jwt = {}
    req_jwt = get_jwt(req)

    if req_jwt != "":
        try:
            # TODO: need to verify JWT with pub key
            # TODO: need to check for claims that Vault sends in JWT
            decoded_jwt = jwt.decode(req_jwt, verify=False,
                                     options={'require': ['iat', 'sub']})
        except jwt.InvalidIssuedAtError as iisa:
            logger.error("JWT has invalid Issued-At datetime ", str(iisa))
        except jwt.ExpiredSignatureError as es:
            logger.error("JWT has invalid or expired signature ", str(es))
        except jwt.DecodeError as d:
            logger.error("JWT could not be decoded for reasons ", str(d))
    return decoded_jwt


def is_jwt_valid(req):
    """Check for JWT's validity

    @param req: Flask `request` object
    @return: boolean
    """
    is_request_authorized = False
    if decode_jwt(req):
        is_request_authorized = True
    return is_request_authorized


def authorize(f):
    """Decorator to check if request is authorized

    @param f: function that needs to be wrapped
    @return: wrapped function
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not is_jwt_valid(request):
            return Response("Missing valid authentication token. Please provide your "
                            "JWT in the Authorization header as Bearer token.", 401)
        else:
            logger.info("Authorized to make requests to the API")
            token = decode_jwt(request)
            session["authorized"] = True
            session["user"] = token["sub"]
            session["sub"] = token["sub"]
        return f(*args, **kwargs)

    return decorated_function
