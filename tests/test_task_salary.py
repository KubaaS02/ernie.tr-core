import pytest
from tests import Task
from tests import get_approx_cost_pln, get_approx_cost_from_pln_to_euro, get_actual_cost_pln
from datetime import datetime
from tests import InvalidExchangeRateError, InvalidHourdlyRateError, MissingCalculationDataError


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

# ========== TESTY get_actual_cost_pln() ==========


def _make_task(cost_approx_pln: float | None = 128.53) -> Task:
    """Tworzy task testowy z ustawionym kosztem przybliżonym"""
    return Task(
        task_start=datetime(2025, 11, 1, 19, 44),
        task_stop=datetime(2025, 11, 1, 20, 48),
        task_id="task_dev_01",
        comment="Development",
        cost_approx_pln=cost_approx_pln,
    )


class TestGetActualCostPln:
    """Testy rejestrowania kosztu faktycznego (FR-421-9)"""

    def test_spec_example_underpayment(self) -> None:
        """Test przykładu ze spec - approx 128.53, wpłata 102.00, diff -26.53"""
        task = _make_task()
        result: float = get_actual_cost_pln(
            task, 102.00, datetime(2025, 11, 20))
        assert result == 102.00
        assert task.diff == -26.53

    def test_exact_payment_zero_diff(self) -> None:
        """Test płatności równej przybliżeniu - różnica zero"""
        task = _make_task()
        get_actual_cost_pln(task, 128.53, datetime(2025, 11, 20))
        assert task.diff == 0.0

    def test_overpayment_positive_diff(self) -> None:
        """Test nadpłaty - różnica dodatnia"""
        task = _make_task()
        get_actual_cost_pln(task, 150.00, datetime(2025, 11, 20))
        assert task.diff == 21.47

    def test_underpayment_negative_diff(self) -> None:
        """Test niedopłaty - różnica ujemna"""
        task = _make_task()
        get_actual_cost_pln(task, 100.00, datetime(2025, 11, 20))
        assert task.diff == -28.53

    def test_sets_cost_actual_pln(self) -> None:
        """Test zapisu faktycznej kwoty na tasku"""
        task = _make_task()
        get_actual_cost_pln(task, 102.00, datetime(2025, 11, 20))
        assert task.cost_actual_pln == 102.00

    def test_sets_status_to_paid(self) -> None:
        """Test zmiany statusu na 'Zapłacone'"""
        task = _make_task()
        get_actual_cost_pln(task, 102.00, datetime(2025, 11, 20))
        assert task.status == "Zapłacone"

    def test_sets_payment_date(self) -> None:
        """Test zapisu daty płatności na tasku"""
        task = _make_task()
        get_actual_cost_pln(task, 102.00, datetime(2025, 11, 20))
        assert task.payment_date == datetime(2025, 11, 20)

    def test_return_matches_task_field(self) -> None:
        """Test zgodności wartości zwróconej z polem tasku"""
        task = _make_task()
        result: float = get_actual_cost_pln(
            task, 102.00, datetime(2025, 11, 20))
        assert result == task.cost_actual_pln

    def test_zero_amount_raises_error(self) -> None:
        """Test gdy kwota = 0 (powinien rzucić błąd)"""
        task = _make_task()
        with pytest.raises(ValueError):
            get_actual_cost_pln(task, 0, datetime(2025, 11, 20))

    def test_negative_amount_raises_error(self) -> None:
        """Test gdy kwota ujemna (powinien rzucić błąd)"""
        task = _make_task()
        with pytest.raises(ValueError):
            get_actual_cost_pln(task, -50.00, datetime(2025, 11, 20))

    def test_error_does_not_mutate_task(self) -> None:
        """Test że błąd walidacji nie zmienia stanu tasku"""
        task = _make_task()
        with pytest.raises(ValueError):
            get_actual_cost_pln(task, -50.00, datetime(2025, 11, 20))
        assert task.status == "Oczekuje"
        assert task.cost_actual_pln is None
        assert task.payment_date is None

    def test_missing_approx_cost_raises_error(self) -> None:
        """Test gdy task nie ma ustawionego cost_approx_pln"""
        task = _make_task(cost_approx_pln=None)
        with pytest.raises(ValueError):
            get_actual_cost_pln(task, 102.00, datetime(2025, 11, 20))
