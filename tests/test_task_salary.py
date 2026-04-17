import pytest
from src.models.task import Task
from src.core.salary.task_salary import approx_cost_pln
from datetime import datetime
class TestCalculateTaskSalary:
    """Testy obliczania operacji pieniężnych tasku"""
    
    
    def test_approx_cost_pln(self) -> None:
        """ Test, czy funkcja działa poprawnie"""
        task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 11, ), rate_pln_per_h = 60)
        result: float = approx_cost_pln(task, rate_pln_per_h=60)
        assert result == 120.0 # 120 zł
    
    def test_approx_cost_pln_correct_rate(self) -> None:
        """ Test, czy funkcja zaciąga poprawny rate"""
        task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 11, ), rate_pln_per_h = 60)
        result: float = approx_cost_pln(task, rate_pln_per_h=999)
        assert result == 120.0 # 120 zł
    
    def test_approx_cost_pln_rate_from_function(self) -> None:
        """ Test, czy funkcja zaciągnie rate_pln_per_h z funkcji, gdy nie ma podanego tego przy tworzeniu taska"""
        task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 11, ))
        result: float = approx_cost_pln(task, rate_pln_per_h= 120)
        assert result == 240.0 # 240 zł
    
    def test_test_approx_cost_pln_is0(self) -> None:
        task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 11, ), rate_pln_per_h = 0)
        with pytest.raises(ValueError):
            approx_cost_pln(task, rate_pln_per_h= 0)