import pytest
from datetime import date, timedelta

from validation_middleware import (
    ValidationError,
    validate_required,
    validate_email,
    validate_weight,
    validate_birthday,
)

# Basic happy-path and failure cases for validation helpers.
def test_validate_required_ok():
    validate_required("John", "Name")

def test_validate_required_empty():
    with pytest.raises(ValidationError):
        validate_required("", "Name")

def test_validate_email_ok():
    validate_email("test@example.com")

def test_validate_email_invalid():
    with pytest.raises(ValidationError):
        validate_email("not-an-email")

def test_validate_weight_ok():
    validate_weight("80")

def test_validate_weight_invalid():
    with pytest.raises(ValidationError):
        validate_weight("-5")

def test_validate_birthday_ok():
    validate_birthday(date.today() - timedelta(days=365*20))

def test_validate_birthday_future():
    with pytest.raises(ValidationError):
        validate_birthday(date.today() + timedelta(days=1))
