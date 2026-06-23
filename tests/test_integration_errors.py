import pytest
from tests import BusinessError, NbpApiUnavailableError


class TestNbpApiUnavailableError:
    """Testy związane z grupą błędów komunikacji z zewnętrznymi usługami"""

    def test_NbpApiUnavailableError_error_id(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_ID = ERR-INT-01"""
        assert NbpApiUnavailableError.error_id == "ERR-INT-01"

    def test_NbpApiUnavailableError_error_code(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_CODE = nbp_api_unavailable"""
        assert NbpApiUnavailableError.error_code == "nbp_api_unavailable"

    def test_NbpApiUnavailableError_http_status(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne HTTP_STATUS = 503"""
        assert NbpApiUnavailableError.http_status == 503

    def test_NbpApiUnavailableError_can_be_raised_and_caught(self) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy nie uda się połączyć z NBP API"""
        details = {
            "endpoint": "https://api.nbp.pl/api/exchangerates/...", "fallback_used": False}
        error = NbpApiUnavailableError(details=details)

        assert isinstance(error, Exception)
        assert isinstance(error, BusinessError)
        assert isinstance(error, NbpApiUnavailableError)

        with pytest.raises(NbpApiUnavailableError):
            raise NbpApiUnavailableError(
                details=details)

    def test_NbpApiUnavailableError_details_are_stored(self) -> None:
        """Sprawdzenie, czy klasa poprawnie przechowuje details"""
        details = {
            "endpoint": "https://api.nbp.pl/api/exchangerates/...", "fallback_used": False}
        error = NbpApiUnavailableError(details=details)
        assert error.details == details

    def test_NbpApiUnavailableError_default_message_used_when_no_message_given(self) -> None:
        """Sprawdzenie, czy klasa bierze default_message, gdy nie ma napisanej message"""
        error = NbpApiUnavailableError(
            details={"endpoint": "https://api.nbp.pl/api/exchangerates/...", "fallback_used": False})
        assert error.message == NbpApiUnavailableError.default_message

    def test_NbpApiUnavailableError_to_json_value_on_minus(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie, gdy nie uda się połączyć z NBP API"""
        details = {
            "endpoint": "https://api.nbp.pl/api/exchangerates/...", "fallback_used": False}
        error = NbpApiUnavailableError(details=details)
        result = error.to_json()
        assert result["error_code"] == "nbp_api_unavailable"
        assert result["http_status"] == 503
        assert result["message"] == NbpApiUnavailableError.default_message
        assert result["details"] == details
