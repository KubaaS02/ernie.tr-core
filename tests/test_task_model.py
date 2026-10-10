import pytest
from datetime import datetime
from tests import InvalidTaskTimeRangeError
from tests import get_task_time_duration
from tests import Task


class TestTaskModel:
    def test_task_model(self) -> None:
        """"""
        new_task = Task(datetime(2025, 11, 1, 10, 00),
                        datetime(2025, 11, 1, 10, 00), "task_123")
        result: int = get_task_time_duration(
            new_task.task_start,
            new_task.task_stop
        )
        assert result == 1

    def test_task_initialization_calculates_duration(self) -> None:
        task = Task(
            task_id="task_123",
            task_start=datetime(2025, 11, 1, 10),
            task_stop=datetime(2025, 11, 1, 11, 30),
        )

        assert task.duration_min == 90

    def test_task_initialization_overwrites_provided_duration(self) -> None:
        task = Task(
            task_id="task_123",
            task_start=datetime(2025, 11, 1, 10),
            task_stop=datetime(2025, 11, 1, 11),
            duration_min=999,
        )

        assert task.duration_min == 60

    # Below more edge-cases
    def test_task_start_after_stop_raises_domain_error(self) -> None:
        with pytest.raises(InvalidTaskTimeRangeError) as exc_info:
            Task(
                task_id="task_123",
                task_start=datetime(2025, 11, 1, 12),
                task_stop=datetime(2025, 11, 1, 10),
            )

        assert exc_info.value.details == {
            "task_start": datetime(2025, 11, 1, 12),
            "task_stop": datetime(2025, 11, 1, 10),
        }

    def test_task_start_equal_stop_creates_minimum_one_minute_duration(self) -> None:
        task = Task(
            task_id="task_123",
            task_start=datetime(2025, 11, 1, 10),
            task_stop=datetime(2025, 11, 1, 10),
        )

        assert task.duration_min == 1

    def test_task_default_payment_status_is_pending(self) -> None:
        task = Task(
            task_id="task_123",
            task_start=datetime(2025, 11, 1, 10),
            task_stop=datetime(2025, 11, 1, 11),
        )

        assert task.status == "Oczekuje"

    def test_task_default_diff_status_is_pending(self) -> None:
        task = Task(
            task_id="task_123",
            task_start=datetime(2025, 11, 1, 10),
            task_stop=datetime(2025, 11, 1, 11),
        )

        assert task.diff_status == "Pending"
        assert task.diff is None
