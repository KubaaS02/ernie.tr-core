import pytest
from tests import BusinessError, MissingCalculationDataError


class TestMissingCalculationDataError:
    """Testy przeprowadzanych operacji związanych z kalkulacjami kosztów"""

    def test_MissingCalculationDataError_error_id(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_ID = ERR-DATA-01"""
        assert MissingCalculationDataError.error_id == "ERR-DATA-01"

    def test_MissingCalculationDataError_error_code(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_CODE = missing_calculation_data"""
        assert MissingCalculationDataError.error_code == "missing_calculation_data"

    def test_MissingCalculationDataError_http_status(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne HTTP_STATUS = 400"""
        assert MissingCalculationDataError.http_status == 400

    def test_MissingCalculationDataError_can_be_raised_and_caught(self) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy będzie brakowało duration_min"""
        details = {"missing_fields": "duration_min"}
        error = MissingCalculationDataError(details=details)

        assert isinstance(error, Exception)
        assert isinstance(error, BusinessError)
        assert isinstance(error, MissingCalculationDataError)

        with pytest.raises(MissingCalculationDataError):
            raise MissingCalculationDataError(
                details=details)

    def test_MissingCalculationDataError_details_are_stored(self) -> None:
        """Sprawdzenie, czy klasa poprawnie przechowuje details"""
        details = {"missing_fields": ["duration_min", "hourly_rate"]}
        error = MissingCalculationDataError(details=details)
        assert error.details == details

    def test_MissingCalculationDataError_default_message_used_when_no_message_given(self) -> None:
        """Sprawdzenie, czy klasa bierze default_message, gdy nie ma napisanej message"""
        error = MissingCalculationDataError(
            details={"missing_fields": ["duration_min", "hourly_rate"]})
        assert error.message == MissingCalculationDataError.default_message

    def test_MissingCalculationDataError_to_json_value_on_minus(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie, brakuje pól duration_min i hourly_rate"""
        details = {"missing_fields": ["duration_min", "hourly_rate"]}
        error = MissingCalculationDataError(details=details)
        result = error.to_json()
        assert result["error_code"] == "missing_calculation_data"
        assert result["http_status"] == 400
        assert result["message"] == MissingCalculationDataError.default_message
        assert result["details"] == details
