import pytest
from tests import BusinessError, InvalidExchangeRateError, InvalidHourdlyRateError


class TestInvalidExchangeRateError:
    """Testy przeprowadzanych operacji związanych z finansami"""

    def test_InvalidExchangeRateError_error_id(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_ID = ERR-FIN-01"""
        assert InvalidExchangeRateError.error_id == "ERR-FIN-01"

    def test_InvalidExchangeRateError_error_code(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_CODE = invalid_exchange_rate"""
        assert InvalidExchangeRateError.error_code == "invalid_exchange_rate"

    def test_InvalidExchangeRateError_http_status(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne HTTP_STATUS = 422"""
        assert InvalidExchangeRateError.http_status == 422

    def test_InvalidExchangeRateError_can_be_raised_and_caught(self) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy kurs wymiany waluty będzie < 0"""
        details = {"value": -1}
        error = InvalidExchangeRateError(details=details)

        assert isinstance(error, Exception)
        assert isinstance(error, BusinessError)
        assert isinstance(error, InvalidExchangeRateError)
        assert not isinstance(error, ValueError)

        with pytest.raises(InvalidExchangeRateError):
            raise InvalidExchangeRateError(
                details=details)

    def test_InvalidExchangeRateError_details_are_stored(self) -> None:
        """Sprawdzenie, czy klasa poprawnie przechowuje details"""
        details = {"value": 10}
        error = InvalidExchangeRateError(details=details)
        assert error.details == details

    def test_InvalidExchangeRateError_default_message_used_when_no_message_given(self) -> None:
        """Sprawdzenie, czy klasa bierze default_message, gdy nie ma napisanej message"""
        error = InvalidExchangeRateError(
            details={"value": -1})
        assert error.message == InvalidExchangeRateError.default_message

    def test_InvalidExchangeRateError_to_json_value_on_minus(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie, gdy value = -1"""
        details = {"value": -1}
        error = InvalidExchangeRateError(details=details)
        result = error.to_json()
        assert result["error_code"] == "invalid_exchange_rate"
        assert result["http_status"] == 422
        assert result["message"] == InvalidExchangeRateError.default_message
        assert result["details"] == details

    def test_InvalidExchangeRateError_to_json_value_0(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie, gdy value = 0"""
        details = {"value": 0}
        error = InvalidExchangeRateError(details=details)
        result = error.to_json()
        assert result["error_code"] == "invalid_exchange_rate"
        assert result["http_status"] == 422
        assert result["message"] == InvalidExchangeRateError.default_message
        assert result["details"] == details

# błędy InvalidHourlyRateError
    def test_InvalidHourdlyRateError_error_id(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_ID = ERR-FIN-02"""
        assert InvalidHourdlyRateError.error_id == "ERR-FIN-02"

    def test_InvalidHourdlyRateError_error_code(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_CODE = invalid_hourly_rate"""
        assert InvalidHourdlyRateError.error_code == "invalid_hourly_rate"

    def test_InvalidHourdlyRateError_http_status(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne HTTP_STATUS = 422"""
        assert InvalidHourdlyRateError.http_status == 422

    def test_InvalidHourdlyRateError_can_be_raised_and_caught(self) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy stawka godzinowa będzie < 0"""
        details = {"hourly_rate": -120}
        error = InvalidHourdlyRateError(details=details)

        assert isinstance(error, Exception)
        assert isinstance(error, BusinessError)
        assert isinstance(error, InvalidHourdlyRateError)
        assert not isinstance(error, ValueError)

        with pytest.raises(InvalidHourdlyRateError):
            raise InvalidHourdlyRateError(
                details=details)

    def test_InvalidHourdlyRateError_details_are_stored(self) -> None:
        """Sprawdzenie, czy klasa poprawnie przechowuje details"""
        details = {"hourly_rate": 100}
        error = InvalidHourdlyRateError(details=details)
        assert error.details == details

    def test_InvalidHourdlyRateError_default_message_used_when_no_message_given(self) -> None:
        """Sprawdzenie, czy klasa bierze default_message, gdy nie ma napisanej message"""
        error = InvalidHourdlyRateError(
            details={"value": -120})
        assert error.message == InvalidHourdlyRateError.default_message

    def test_InvalidHourdlyRateError_to_json_value_on_minus(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie, gdy hourly_rate = -100"""
        details = {"value": -100}
        error = InvalidHourdlyRateError(details=details)
        result = error.to_json()
        assert result["error_code"] == "invalid_hourly_rate"
        assert result["http_status"] == 422
        assert result["message"] == InvalidHourdlyRateError.default_message
        assert result["details"] == details

    def test_InvalidHourdlyRateError_to_json_value_0(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie, gdy value = 0"""
        details = {"value": 0}
        error = InvalidHourdlyRateError(details=details)
        result = error.to_json()
        assert result["error_code"] == "invalid_hourly_rate"
        assert result["http_status"] == 422
        assert result["message"] == InvalidHourdlyRateError.default_message
        assert result["details"] == details
