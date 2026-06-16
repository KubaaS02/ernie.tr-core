import pytest
from tests import BusinessError, InvalidTaskTimeRangeError, TaskOverlapError, Task
from datetime import datetime

class TestInvalidTaskTimeRangeError:
    """Testy przeprowadzanych działań na czasie"""

    def test_InvalidTaskTimeRangeError_error_id(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_ID = ERR-TIME-01"""
        assert InvalidTaskTimeRangeError.error_id == "ERR-TIME-01"

    def test_InvalidTaskTimeRangeError_error_code(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_CODE = invalid_task_time_range"""
        assert InvalidTaskTimeRangeError.error_code == "invalid_task_time_range"

    def test_InvalidTaskTimeRangeError_http_status(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne HTTP_STATUS = 400"""
        assert InvalidTaskTimeRangeError.http_status == 400

    def test_InvalidTaskTimeRangeError_can_be_raised_and_caught(self) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy godzina rozpoczęcia będzie późniejsza niż rozpoczęcia"""
        details = {"start": "20:48", "stop": "19:44"}
        error = InvalidTaskTimeRangeError(details=details)

        assert isinstance(error, Exception)
        assert isinstance(error, BusinessError)
        assert isinstance(error, InvalidTaskTimeRangeError)
        assert not isinstance(error, ValueError)

        with pytest.raises(InvalidTaskTimeRangeError):
            raise InvalidTaskTimeRangeError(
                details=details)

    def test_InvalidTaskTimeRangeError_details_are_stored(self) -> None:
        """Sprawdzenie, czy klasa poprawnie przechowuje details"""
        details = {"start": "19:57", "stop": "18:44"}
        error = InvalidTaskTimeRangeError(details=details)
        assert error.details == details

    def test_InvalidTaskTimeRangeError_default_message_used_when_no_message_given(self) -> None:
        """Sprawdzenie, czy klasa bierze default_message, gdy nie ma napisanej message"""
        error = InvalidTaskTimeRangeError(
            details={"start": "20:01", "stop": "19:23"})
        assert error.message == InvalidTaskTimeRangeError.default_message

    def test_InvalidTaskTimeRangeError_to_json(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie"""
        details = {"start": "19:57", "stop": "18:44"}
        error = InvalidTaskTimeRangeError(details=details)
        result = error.to_json()
        assert result["error_code"] == "invalid_task_time_range"
        assert result["http_status"] == 400
        assert result["message"] == InvalidTaskTimeRangeError.default_message
        assert result["details"] == details

    def test_TaskOverlapError_error_id(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_ID = "ERR-TIME-02"""
        assert TaskOverlapError.error_id == "ERR-TIME-02"

    def test_TaskOverlapError_error_code(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_CODE = task_overlap"""
        assert TaskOverlapError.error_code == "task_overlap"

    def test_TaskOverlapError_http_status(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne HTTP_STATUS = 409"""
        assert TaskOverlapError.http_status == 409

    def test_TaskOverlapError_details_are_stored(self) -> None:
        """Sprawdzenie, czy klasa poprawnie przechowuje details"""
        details = {"conflicting_task_id": "task1", "range": "10:00-11:00"}
        error = TaskOverlapError(details=details)
        assert error.details == details

    def test_TaskOverlapError_default_message_used_when_no_message_given(self) -> None:
        """Sprawdzenie, czy klasa bierze default_message, gdy nie ma napisanej message"""
        error = TaskOverlapError(
            details={"conflicting_task_id": "task1", "range": "10:00-11:00"})
        assert error.message == TaskOverlapError.default_message

    def test_TaskOverlapError_to_json(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie"""
        details = {"conflicting_task_id": "task1", "range": "10:00-11:00"}
        error = TaskOverlapError(details=details)
        result = error.to_json()
        assert result["error_code"] == "task_overlap"
        assert result["http_status"] == 409
        assert result["message"] == TaskOverlapError.default_message
        assert result["details"] == details
#TODO dopisać test sprawdzający overlap Tasków
    def test_TaskOverlapError_raise(self):
        """Sprawdzenie, czy TaskOverlapError zostanie rzucony przy nakładaniu się zakresów czasu"""
        task1 = Task(
            task_id="task1",
            task_start=datetime(2026,1,1,10,0),
            task_stop=datetime(2026,1,1,12,0)
        )
        
        task2 = Task(
            task_id="task2",
            task_start=datetime(2026,1,1,11,0),
            task_stop=datetime(2026,1,1,13,0)
        )
        
        def check_overlap(t1:Task, t2:Task) -> None:
            if t1.task_start < t2.task_stop and t2.task_start < t2.task_stop:
                raise TaskOverlapError(
                    details=
                        {"conflicting_task_id": t2.task_id,
                        "range": f"{t2.task_start.strftime('%H:%M')} - {t2.task_stop.strftime('%H:%M')}"
                        }
                )
            with pytest.raises(TaskOverlapError):
                check_overlap(task1,task2) 