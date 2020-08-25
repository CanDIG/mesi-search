# -*- coding: utf-8 -*-
from mesi_search import utils
from requests.models import Request


def test_get_jwt_with_auth_header():
    r = Request()
    r.headers["Authorization"] = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." \
                                 "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9" \
                                 "lIiwiaWF0IjoxNTE2MjM5MDIyfQ." \
                                 "pXjao0FHh84o2WZn4jK6MH2T0EzSD671wNq-3Wq1AIk"
    j = utils.get_jwt(r)
    assert j == r.headers["Authorization"].split(" ")[1]


def test_get_jwt_empty_auth_header():
    r = Request()
    j = utils.get_jwt(r)
    assert j == ""


def test_check_jwt(mocker):
    def mock_get_jwt(req):
        j = "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." \
            "eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9" \
            "lIiwiaWF0IjoxNTE2MjM5MDIyfQ." \
            "pXjao0FHh84o2WZn4jK6MH2T0EzSD671wNq-3Wq1AIk"
        return j
    mocker.patch(
        "mesi_search.utils.get_jwt",
        mock_get_jwt
    )
    actual = utils.get_jwt({})
    assert actual


def test_check_jwt_no_jwt(mocker):
    def mock_get_jwt(req):
        j = ""
        return j
    mocker.patch(
        "mesi_search.utils.get_jwt",
        mock_get_jwt
    )
    actual = utils.get_jwt({})
    assert not actual
