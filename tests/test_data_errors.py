import pytest
from tests import BusinessError, MissingCalculationDataError, IncompleteChangeLogEntryError


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


class TestIncompleteChangeLogEntryError:
    """Testy błędu niekompletnego wpisu w historii zmian"""

    def test_IncompleteChangeLogEntryError_error_id(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_ID = ERR-DATA-04"""
        assert IncompleteChangeLogEntryError.error_id == "ERR-DATA-04"

    def test_IncompleteChangeLogEntryError_error_id_differs_from_other_data_errors(self) -> None:
        """Sprawdzenie, czy error_id nie koliduje z MissingCalculationDataError"""
        assert IncompleteChangeLogEntryError.error_id != MissingCalculationDataError.error_id

    def test_IncompleteChangeLogEntryError_error_code(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_CODE = incomplete_change_log_entry"""
        assert IncompleteChangeLogEntryError.error_code == "incomplete_change_log_entry"

    def test_IncompleteChangeLogEntryError_http_status(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne HTTP_STATUS = 500"""
        assert IncompleteChangeLogEntryError.http_status == 500

    def test_IncompleteChangeLogEntryError_can_be_raised_and_caught(self) -> None:
        """Sprawdzenie, czy błąd dziedziczy po BusinessError i da się go złapać"""
        error = IncompleteChangeLogEntryError(
            details={"missing_fields": ["field"]})

        assert isinstance(error, Exception)
        assert isinstance(error, BusinessError)
        assert isinstance(error, IncompleteChangeLogEntryError)

        with pytest.raises(IncompleteChangeLogEntryError):
            raise IncompleteChangeLogEntryError(
                details={"missing_fields": ["field"]})

    def test_IncompleteChangeLogEntryError_default_message_used_when_no_message_given(self) -> None:
        """Sprawdzenie, czy klasa bierze default_message, gdy nie ma napisanej message"""
        error = IncompleteChangeLogEntryError(
            details={"missing_fields": ["field"]})
        assert error.message == IncompleteChangeLogEntryError.default_message

    def test_IncompleteChangeLogEntryError_to_json(self) -> None:
        """Sprawdzenie, czy metoda to_json zwraca poprawny słownik"""
        details = {"task_id": "task_123", "action": "field_change",
                   "missing_fields": ["old_value"]}
        error = IncompleteChangeLogEntryError(details=details)
        result = error.to_json()
        assert result["error_code"] == "incomplete_change_log_entry"
        assert result["http_status"] == 500
        assert result["message"] == IncompleteChangeLogEntryError.default_message
        assert result["details"] == details
