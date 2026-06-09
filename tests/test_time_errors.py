import pytest
from tests import BusinessError, InvalidTaskTimeRangeError


class TestInvalidTaskTimeRangeError:
    """Testy przeprowadzanych działań na czasie"""

    def test_error_id(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_ID = ERR-TIME-01"""
        assert InvalidTaskTimeRangeError.error_id == "ERR-TIME-01"

    def test_error_code(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_CODE = invalid_task_time_range"""
        assert InvalidTaskTimeRangeError.error_code == "invalid_task_time_range"

    def test_http_status(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne HTTP_STATUS = 400"""
        assert InvalidTaskTimeRangeError.http_status == 400

    def test_can_be_raised_and_caught(self) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy godzina rozpoczęcia będzie późniejsza niż rozpoczęcia"""
        with pytest.raises(InvalidTaskTimeRangeError):
            raise InvalidTaskTimeRangeError(
                details={"start": "20:48", "stop": "19:44"})

    def test_details_are_stored(self) -> None:
        """Sprawdzenie, czy klasa poprawnie przechowuje details"""
        details = {"start": "19:57", "stop": "18:44"}
        error = InvalidTaskTimeRangeError(details=details)
        assert error.details == details

    def test_default_message_used_when_no_message_given(self) -> None:
        """Sprawdzenie, czy klasa bierze default_message, gdy nie ma napisanej message"""
        error = InvalidTaskTimeRangeError(
            details={"start": "20:01", "stop": "19:23"})
        assert error.message == InvalidTaskTimeRangeError.default_message

    def test_to_JSON(self) -> None:
        """Sprawdzenie, czy metoda to_JSON działa popranie"""
        details = {"start": "19:57", "stop": "18:44"}
        error = InvalidTaskTimeRangeError(details=details)
        assert error.to_JSON()["error_code"] == "invalid_task_time_range"
        assert error.to_JSON()["http_status"] == 400
        assert error.to_JSON()[
            "message"] == InvalidTaskTimeRangeError.default_message
        assert error.to_JSON()["details"] == details
