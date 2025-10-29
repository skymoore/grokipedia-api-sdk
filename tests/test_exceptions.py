import pytest

from grokipedia_api_sdk.exceptions import (
    GrokipediaAPIError,
    GrokipediaBadRequestError,
    GrokipediaError,
    GrokipediaNetworkError,
    GrokipediaNotFoundError,
    GrokipediaRateLimitError,
    GrokipediaServerError,
    GrokipediaValidationError,
)


def test_base_exception():
    error = GrokipediaError("test error")
    assert str(error) == "test error"
    assert isinstance(error, Exception)


def test_api_error():
    error = GrokipediaAPIError("api error", status_code=500, response_body="error body")
    assert str(error) == "api error"
    assert error.status_code == 500
    assert error.response_body == "error body"
    assert isinstance(error, GrokipediaError)


def test_api_error_without_optional_params():
    error = GrokipediaAPIError("api error")
    assert str(error) == "api error"
    assert error.status_code is None
    assert error.response_body is None


def test_bad_request_error():
    error = GrokipediaBadRequestError("bad request", status_code=400)
    assert str(error) == "bad request"
    assert error.status_code == 400
    assert isinstance(error, GrokipediaAPIError)


def test_not_found_error():
    error = GrokipediaNotFoundError("not found", status_code=404)
    assert str(error) == "not found"
    assert error.status_code == 404
    assert isinstance(error, GrokipediaAPIError)


def test_rate_limit_error():
    error = GrokipediaRateLimitError("rate limit", status_code=429)
    assert str(error) == "rate limit"
    assert error.status_code == 429
    assert isinstance(error, GrokipediaAPIError)


def test_server_error():
    error = GrokipediaServerError("server error", status_code=500)
    assert str(error) == "server error"
    assert error.status_code == 500
    assert isinstance(error, GrokipediaAPIError)


def test_network_error():
    error = GrokipediaNetworkError("network error")
    assert str(error) == "network error"
    assert isinstance(error, GrokipediaError)


def test_validation_error():
    error = GrokipediaValidationError("validation error")
    assert str(error) == "validation error"
    assert isinstance(error, GrokipediaError)


def test_exception_hierarchy():
    assert issubclass(GrokipediaAPIError, GrokipediaError)
    assert issubclass(GrokipediaBadRequestError, GrokipediaAPIError)
    assert issubclass(GrokipediaNotFoundError, GrokipediaAPIError)
    assert issubclass(GrokipediaRateLimitError, GrokipediaAPIError)
    assert issubclass(GrokipediaServerError, GrokipediaAPIError)
    assert issubclass(GrokipediaNetworkError, GrokipediaError)
    assert issubclass(GrokipediaValidationError, GrokipediaError)


def test_catch_specific_exception():
    try:
        raise GrokipediaNotFoundError("test", status_code=404)
    except GrokipediaNotFoundError as e:
        assert e.status_code == 404


def test_catch_parent_exception():
    try:
        raise GrokipediaNotFoundError("test", status_code=404)
    except GrokipediaAPIError as e:
        assert isinstance(e, GrokipediaNotFoundError)


def test_catch_base_exception():
    try:
        raise GrokipediaNotFoundError("test", status_code=404)
    except GrokipediaError as e:
        assert isinstance(e, GrokipediaNotFoundError)
