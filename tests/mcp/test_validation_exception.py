import pytest
from pydantic import ValidationError as RequestValidationError

from app.core.exceptions import ValidationError
from app.mcp.mcp_tools.miles_to_km import MilestoKmRequest, miles_to_kilometers_value

EXPECTED_KM = 1.609
CONVERSION_TOLERANCE = 0.001


def test_known_conversion():
    result = miles_to_kilometers_value(1)
    assert abs(result - EXPECTED_KM) < CONVERSION_TOLERANCE


def test_validation_error_is_exception():
    assert issubclass(ValidationError, Exception)


def test_negative_miles_raises_validation_error():
    with pytest.raises(ValidationError):
        miles_to_kilometers_value(-1)


def test_zero_miles_raises_validation_error():
    with pytest.raises(ValidationError, match="greater than zero"):
        miles_to_kilometers_value(0)


def test_request_model_rejects_zero_miles():
    with pytest.raises(RequestValidationError):
        MilestoKmRequest(miles=0)


def test_request_model_rejects_negative_miles():
    with pytest.raises(RequestValidationError):
        MilestoKmRequest(miles=-1)


def test_request_model_accepts_positive_miles():
    request = MilestoKmRequest(miles=1)
    assert request.miles == 1


def test_none_miles_raises_validation_error():
    with pytest.raises(ValidationError):
        miles_to_kilometers_value(None)


def test_too_large_miles_raises_validation_error():
    with pytest.raises(ValidationError):
        miles_to_kilometers_value(99999999)


def test_valid_miles_returns_float():
    result = miles_to_kilometers_value(1)
    assert isinstance(result, float)


def test_http_exception_not_raised():
    from fastapi import HTTPException

    with pytest.raises(ValidationError):
        try:
            miles_to_kilometers_value(-1)
        except HTTPException:
            pytest.fail("HTTPException should not be raised from core logic")
