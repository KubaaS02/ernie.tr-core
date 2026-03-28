import pytest
from datetime import datetime
from core.time.task_duration import calculate_task_duration
from models.task import Task

class TestTaskModel:
    def test_task_model(self) -> None:
            """"""
            new_task = Task(datetime(2025, 11, 1, 10, 00), datetime(2025, 11, 1, 10, 00), "task_123")
            result: int = calculate_task_duration(
                new_task.task_start,
                new_task.task_stop
            )
            assert result == 1
    
    def test_task_types(self) -> None:
        task = Task(datetime(2025, 11, 1, 10, 00), datetime(2025, 11, 1, 10, 00), "task_123")
        assert type(task.task_id) is str
        assert isinstance(task.task_id, str)
        assert type(task.task_start) is datetime
        assert isinstance(task.task_start, datetime)
        assert type(task.task_stop) is datetime
        assert isinstance(task.task_stop, datetime)
    
    