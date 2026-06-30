import pytest
from tests import Task
from tests import get_approx_cost_pln, get_approx_cost_from_pln_to_euro
from datetime import datetime
from exceptions.finance_errors import InvalidExchangeRateError, InvalidHourdlyRateError


class TestCalculateTaskSalary:
    """Testy obliczania operacji pieniężnych tasku"""

    def test_approx_cost_pln(self) -> None:
        """ Test, czy funkcja działa poprawnie"""
        task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),
                    task_stop=datetime(2025, 11, 1, 11, ), rate_pln_per_h=60)
        result: float = get_approx_cost_pln(task, rate_pln_per_h=60)
        assert result == 120.0  # 120 zł

    def test_approx_cost_pln_correct_rate(self) -> None:
        """ Test, czy funkcja zaciąga poprawny rate"""
        task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),
                    task_stop=datetime(2025, 11, 1, 11, ), rate_pln_per_h=60)
        result: float = get_approx_cost_pln(task, rate_pln_per_h=999)
        assert result == 120.0  # 120 zł

    def test_approx_cost_pln_rate_from_function(self) -> None:
        """ Test, czy funkcja zaciągnie rate_pln_per_h z funkcji, gdy nie ma podanego tego przy tworzeniu taska"""
        task = Task(task_id="1", task_start=datetime(
            2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 11, ))
        result: float = get_approx_cost_pln(task, rate_pln_per_h=120)
        assert result == 240.0  # 240 zł

    def test_test_approx_cost_pln_is0(self) -> None:
        """Test, czy funkcja pokaże błąd, gdy stawka godzinowa wynosi 0"""
        task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),
                    task_stop=datetime(2025, 11, 1, 11, ), rate_pln_per_h=0)
        with pytest.raises(InvalidHourdlyRateError):
            get_approx_cost_pln(task, rate_pln_per_h=0)

    def test_approx_cost_from_PLN_to_EURO(self) -> None:
        """Test, czy funkcja działa poprawnie"""
        task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(
            2025, 11, 1, 11, ), cost_approx_pln=1500, exchange_rate_eur=4.50)
        result: float = get_approx_cost_from_pln_to_euro(task)
        assert result == 333.33

    def test_approx_cost_from_PLN_to_EURO_is0(self) -> None:
        """Test, czy funkcja pokaże błąd, gdy kurs dla euro wynosi 0"""
        task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(
            2025, 11, 1, 11, ), cost_approx_pln=1500, exchange_rate_eur=0.00)
        with pytest.raises(InvalidExchangeRateError):
            get_approx_cost_from_pln_to_euro(task)
