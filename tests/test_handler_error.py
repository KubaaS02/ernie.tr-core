import pytest
from tests import BusinessError


def test_valid_subclass_registers_successfully() -> None:
    class SomeError(BusinessError):
        error_id = "ERR-TEST-REGISTER-01"

    assert "ERR-TEST-REGISTER-01" in SomeError._registered_ids


def test_abstract_subclass_skips_validation() -> None:
    """Podklasa z abstract=True powinna się tworzyć bez error_id"""
    class SomeError(BusinessError):
        abstract = True

    assert isinstance(SomeError(), BusinessError)


def test_subclass_without_error_id_raises_type_error() -> None:
    """Podklasa bez error_id i abstract=False powinna rzucić TypeError"""
    with pytest.raises(TypeError):
        class SomeError(BusinessError):
            abstract = False


def test_subclass_with_generic_error_id_raises_type_error() -> None:
    """Podklasa z error_id='ERR-GENERIC' powinna rzucić TypeError"""
    with pytest.raises(TypeError):
        class SomeError(BusinessError):
            abstract = False
            error_id = "ERR-GENERIC"


def test_duplicate_error_id_raises_value_error() -> None:
    """Podklasy ze zduplikowanym error_id powinny rzucić ValueError"""
    with pytest.raises(ValueError):
        class SomeError(BusinessError):
            abstract = False
            error_id = "ERR-SOME-SAME"

        class SecondError(BusinessError):
            abstract = False
            error_id = "ERR-SOME-SAME"


def test_default_message_used_when_none_passed() -> None:
    """Jeżeli nie ma message, podklasa bierze default_message"""
    class SomeError(BusinessError):
        abstract = False
        error_id = "ERR-SOME-UNIQUE"

    assert SomeError().message == SomeError.default_message


def test_custom_message_overrides_default_message() -> None:
    class SomeError(BusinessError):
        error_id = "ERR-SOME-UNIQUE1"

    error = SomeError("Nieznany error")

    assert error.message == "Nieznany error"


def test_to_json_contains_required_keys() -> None:
    """Wynik to_json musi zawierać: error_code, http_status, message, details"""
    class SomeError(BusinessError):
        abstract = False
        error_id = "SOME-ERR"

    result = SomeError().to_json()

    assert "error_code" in result
    assert "http_status" in result
    assert "message" in result
    assert "details" in result


def test_to_json_returns_complete_error_payload() -> None:
    class SomeError(BusinessError):
        error_id = "ERR-TEST-JSON-01"
        error_code = "test_error"
        http_status = 422
        default_message = "Test error"

    error = SomeError(details={"field": "name"})

    assert error.to_json() == {
        "error_code": "test_error",
        "http_status": 422,
        "message": "Test error",
        "details": {
            "field": "name",
        },
    }


def test_details_default_to_empty_dict() -> None:
    class SomeError(BusinessError):
        error_id = "ERR-TEST-DETAILS-01"

    error = SomeError()

    assert error.details == {}


def test_details_are_preserved() -> None:
    class SomeError(BusinessError):
        error_id = "ERR-TEST-DETAILS-02"

    details = {
        "task_id": "123",
        "reason": "invalid",
    }

    error = SomeError(details=details)

    assert error.details == details


def test_custom_error_code_overrides_class_error_code() -> None:
    class SomeError(BusinessError):
        error_id = "ERR-TEST-CODE-01"
        error_code = "default_code"

    error = SomeError(error_code="custom_code")

    assert error.error_code == "custom_code"


def test_exception_str_contains_message() -> None:
    class SomeError(BusinessError):
        error_id = "ERR-TEST-STR-01"
        default_message = "Something happened"

    error = SomeError()

    assert str(error) == "Something happened"
