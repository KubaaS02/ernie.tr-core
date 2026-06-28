import pytest
from tests import BusinessError, GenericSystemError


class TestGenericSystemError:
    """Testy przeprowadzanych operacji systemowych"""

    def test_GenericSystemError_error_id(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_ID = ERR-GENERIC-01"""
        assert GenericSystemError.error_id == "ERR-GENERIC-01"

    def test_GenericSystemError_error_code(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_CODE = internal_error"""
        assert GenericSystemError.error_code == "internal_error"

    def test_GenericSystemError_http_status(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne HTTP_STATUS = 500"""
        assert GenericSystemError.http_status == 500

    def test_GenericSystemError_can_be_raised_and_caught(self) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy będzie jakiś błąd systemowy"""
        details = {"context": "db connection failed"}
        error = GenericSystemError(details=details)

        assert isinstance(error, Exception)
        assert isinstance(error, BusinessError)
        assert isinstance(error, GenericSystemError)
        assert not isinstance(error, ValueError)

        with pytest.raises(GenericSystemError):
            raise GenericSystemError(
                details=details)

    def test_GenericSystemError_details_are_stored(self) -> None:
        """Sprawdzenie, czy klasa poprawnie przechowuje details"""
        details = {"context": "db connection failed"}
        error = GenericSystemError(details=details)
        assert error.details == details

    def test_GenericSystemError_default_message_used_when_no_message_given(self) -> None:
        """Sprawdzenie, czy klasa bierze default_message, gdy nie ma napisanej message"""
        error = GenericSystemError(
            details={"context": "db connection failed"})
        assert error.message == GenericSystemError.default_message
