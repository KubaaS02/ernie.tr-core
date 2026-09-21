import pytest

from core.helpers.task_helpers import check_is_locked
from tests import BusinessError, TaskLockedError, Task
from datetime import datetime


class TestTaskLockedError:
    """Grupa testów związanych z błędami autoryzacji"""

    def test_TaskLockedError_error_id(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_ID = ERR-AUTH-01"""
        assert TaskLockedError.error_id == "ERR-AUTH-01"

    def test_TaskLockedError_error_code(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne ERROR_CODE = task_locked"""
        assert TaskLockedError.error_code == "task_locked"

    def test_TaskLockedError_http_status(self) -> None:
        """Sprawdzenie, czy klasa ma poprawne HTTP_STATUS = 403"""
        assert TaskLockedError.http_status == 403

    def test_TaskLockedError_can_be_raised_and_caught(self) -> None:
        """Sprawdzenie, czy wyrzuci błąd, gdy task będzie zablokowany, tzn is_blocked=True"""
        details = {"is_locked": True}
        error = TaskLockedError(details=details)

        assert isinstance(error, Exception)
        assert isinstance(error, BusinessError)
        assert isinstance(error, TaskLockedError)

        with pytest.raises(TaskLockedError):
            raise TaskLockedError(
                details=details)

    def test_TaskLockedError_details_are_stored(self) -> None:
        """Sprawdzenie, czy klasa poprawnie przechowuje details"""
        details = {"taks_id": "task123", "is_locked": True}
        error = TaskLockedError(details=details)
        assert error.details == details

    def test_TaskLockedError_default_message_used_when_no_message_given(self) -> None:
        """Sprawdzenie, czy klasa bierze default_message, gdy nie ma napisanej message"""
        error = TaskLockedError(
            details={"is_locked": True})
        assert error.message == TaskLockedError.default_message

    def test_TaskLockedError_to_json_value_on_minus(self) -> None:
        """Sprawdzenie, czy metoda to_json działa popranie, gdy is_locked: True"""
        details = {"is_locked": True}
        error = TaskLockedError(details=details)
        result = error.to_json()
        assert result["error_code"] == "task_locked"
        assert result["http_status"] == 403
        assert result["message"] == TaskLockedError.default_message
        assert result["details"] == details

    ## Not right (With fix of check_is_locked from helpers
    def test_TaskLockedError_is_locked(self) -> None:
        """Sprawdzenie, czy klasa błędu wyrzuci wyjątek kiedy is_locked:True"""
        task1 = Task(
            task_id="task1",
            task_start=datetime(2026, 1, 1, 10, 0),
            task_stop=datetime(2026, 1, 1, 12, 0),
            is_locked=True
        )
        from src.core.helpers.task_helpers import check_is_locked
        with pytest.raises(TaskLockedError):
            check_is_locked(task1)

    ## Right, if check_is_locked does not exist, but we still want to test functionality
    def test_task_locked_error_can_be_raised_with_task_context(self) -> None:
        task = Task(
            task_id="task1",
            task_start=datetime(2026, 1, 1, 10, 0),
            task_stop=datetime(2026, 1, 1, 12, 0),
            is_locked=True,
        )

        with pytest.raises(TaskLockedError) as exc_info:
            raise TaskLockedError(
                details={
                    "task_id": task.task_id,
                    "is_locked": task.is_locked,
                }
            )

        assert exc_info.value.details == {
            "task_id": "task1",
            "is_locked": True,
        }

    ## Even more right, when check_is_locked exists, but with additional asserts
    def test_TaskLockedError_is_locked_correct(self) -> None:
        task = Task(
            task_id="task1",
            task_start=datetime(2026, 1, 1, 10, 0),
            task_stop=datetime(2026, 1, 1, 12, 0),
            is_locked=True,
        )

        with pytest.raises(TaskLockedError) as exc_info:
            check_is_locked(task)

        assert exc_info.value.details["task_id"] == "task1"
        assert exc_info.value.details["is_locked"] is True

    ## Not right
    def test_TaskLockedError_is_not_locked(self) -> None:
        """Sprawdzenie, czy klasa zadziała poprawnie, gdy is_locked:False"""
        task1 = Task(
            task_id="task1",
            task_start=datetime(2026, 1, 1, 10, 0),
            task_stop=datetime(2026, 1, 1, 12, 0),
            is_locked=False
        )

        def check_is_locked(task: Task) -> None:
            if task.is_locked:
                raise TaskLockedError(
                    details = {"task_id": task.task_id, "is_locked": True}
                )
        check_is_locked(task1)

    ## Right
    def test_TaskLockedError_is_not_locked_correct(self) -> None:
        """Sprawdzenie, czy klasa zadziała poprawnie, gdy is_locked:False"""
        task1 = Task(
            task_id="task1",
            task_start=datetime(2026, 1, 1, 10, 0),
            task_stop=datetime(2026, 1, 1, 12, 0),
            is_locked=False
        )

        check_is_locked(task1)
