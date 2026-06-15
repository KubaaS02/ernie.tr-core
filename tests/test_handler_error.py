import pytest
from tests import BusinessError


def test_valid_subclass_registers_successfuly() -> None:
    """Podklasa z unikalnym error_id powinna zarejestrować się bez błędu"""
    class SomeError(BusinessError):
        error_id = "ERR-SOME-UNIQUE"

    assert isinstance(SomeError(), BusinessError)


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


def test_custom_message_overrides_default():
    """Podany message powinien nadpisać default_message"""
    class SomeError(BusinessError):
        abstract = False
        error_id = "ERR-SOME-UNIQUE1"

    assert SomeError("Nieznany error").message != SomeError.default_message


def test_to_dict_contains_required_keys() -> None:
    """Wynik to_dict musi zawierać: error_code, http_status, message, details"""
    class SomeError(BusinessError):
        abstract = False
        error_id = "SOME-ERR"

    result = SomeError().to_json()

    assert "error_code" in result
    assert "http_status" in result
    assert "message" in result
    assert "details" in result