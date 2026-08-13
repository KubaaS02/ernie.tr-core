import pytest
from tests import Task
from tests import get_approx_cost_pln, get_approx_cost_from_pln_to_euro, get_actual_cost_pln, get_actual_cost_euro_from_pln, get_actual_approx_cost_diff, get_diff_day
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


def _make_task(cost_approx_pln: float | None = 128.53, cost_actual_pln: float | None = None) -> Task:
    """Tworzy task testowy z ustawionym kosztem przybliżonym"""
    return Task(
        task_start=datetime(2025, 11, 1, 19, 44),
        task_stop=datetime(2025, 11, 1, 20, 48),
        task_id="task_dev_01",
        comment="Development",
        cost_approx_pln=cost_approx_pln,
        cost_actual_pln=cost_actual_pln
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


class TestGetActualCostEuroFromPln:
    """Testy przeliczania kosztu faktyczne z PLN na EUR (FR-421-10)"""

    def test_get_acutal_cost_euro_from_pln(self) -> None:
        """Test, czy funkcja działa poprawnie dla danych 102.00 PLN / 4.22 = 24.17 EUR"""
        assert get_actual_cost_euro_from_pln(102.00, 4.22) == 24.17

    def test_exact_division(self) -> None:
        """Test dzielenia bez reszty"""
        assert get_actual_cost_euro_from_pln(42.20, 4.22) == 10.00

    def test_zero_rate(self) -> None:
        """Test przechwycenia błędu, gdy rate_eur_pln = 0"""
        with pytest.raises(InvalidExchangeRateError):
            get_actual_cost_euro_from_pln(102.00, 0.00)

    def test_negative_rate(self) -> None:
        """Test przechwycenia błędu, gdy cost_actual_pln < 0"""
        with pytest.raises(InvalidExchangeRateError):
            # TODO: Czy trzeba zrobić wyjątek dedykowany, gdy acutal_cost < 0
            get_actual_cost_euro_from_pln(102.00, -4.22)

    def test_string_rate(self) -> None:
        """Test, gdy wartość rate_eur_pln jest string zamiast float"""
        with pytest.raises(TypeError):
            get_actual_cost_euro_from_pln(102.00, "4.22")


class TestGetActualApproxCostDiff:
    """Testy obliczenia rozbieżności (FR-421-11)"""

    def test_spec_example_underpayment(self) -> None:
        """Test, czy funkcja działa poprawnie - approx 128.53, wpłata 102.00, diff -26.53"""
        task = _make_task(cost_approx_pln=128.53, cost_actual_pln=102.00)
        result: float | None = get_actual_approx_cost_diff(task)
        assert result == -26.53

    def test_spec_example_underpayment_status(self) -> None:
        """Test statusu dla niedopłaty - Negative"""
        task = _make_task(cost_approx_pln=128.53, cost_actual_pln=102.00)
        get_actual_approx_cost_diff(task)
        assert task.diff_status == "Negative"

    def test_spec_example_overpayment(self) -> None:
        """Test, czy funkcja działa poprawnie - approx 100.00, wpłata 110.50, diff 10.50"""
        task = _make_task(cost_approx_pln=100.00, cost_actual_pln=110.50)
        result: float | None = get_actual_approx_cost_diff(task)
        assert result == 10.50

    def test_spec_example_overpayment_status(self) -> None:
        """Test statusu dla nadpłaty - Positive"""
        task = _make_task(cost_approx_pln=100.00, cost_actual_pln=110.50)
        get_actual_approx_cost_diff(task)
        assert task.diff_status == "Positive"

    def test_spec_example_no_payment(self) -> None:
        """Test, czy funkcja działa poprawnie - brak faktycznej płatności, diff None"""
        task = _make_task(cost_approx_pln=128.53, cost_actual_pln=None)
        result: float | None = get_actual_approx_cost_diff(task)
        assert result is None

    def test_spec_example_no_payment_status(self) -> None:
        """Test statusu przy braku płatności - Pending (domyślna wartość modelu)"""
        task = _make_task(cost_approx_pln=128.53, cost_actual_pln=None)
        get_actual_approx_cost_diff(task)
        assert task.diff_status == "Pending"

    def test_exact_payment_returns_zero(self) -> None:
        """Test płatności równej przybliżeniu - różnica zero"""
        task = _make_task(cost_approx_pln=128.53, cost_actual_pln=128.53)
        result: float | None = get_actual_approx_cost_diff(task)
        assert result == 0.0

    def test_exact_payment_status_zero(self) -> None:
        """Test statusu przy płatności równej przybliżeniu - Zero"""
        task = _make_task(cost_approx_pln=128.53, cost_actual_pln=128.53)
        get_actual_approx_cost_diff(task)
        assert task.diff_status == "Zero"

    def test_sets_diff_on_task(self) -> None:
        """Test zapisu rozbieżności na polu task.diff"""
        task = _make_task(cost_approx_pln=128.53, cost_actual_pln=102.00)
        get_actual_approx_cost_diff(task)
        assert task.diff == -26.53

    def test_return_matches_task_field(self) -> None:
        """Test zgodności wartości zwróconej z polem tasku"""
        task = _make_task(cost_approx_pln=128.53, cost_actual_pln=102.00)
        result: float | None = get_actual_approx_cost_diff(task)
        assert result == task.diff

    def test_repeated_call_is_idempotent(self) -> None:
        """Test, czy powtórne wywołanie daje ten sam wynik i status"""
        task = _make_task(cost_approx_pln=128.53, cost_actual_pln=102.00)
        first: float | None = get_actual_approx_cost_diff(task)
        second: float | None = get_actual_approx_cost_diff(task)
        assert first == second
        assert task.diff_status == "Negative"

    def test_zero_approx_cost_is_allowed(self) -> None:
        """Test, gdy koszt przybliżony wynosi 0 - cała wpłata jest nadpłatą"""
        task = _make_task(cost_approx_pln=0.0, cost_actual_pln=50.00)
        result: float | None = get_actual_approx_cost_diff(task)
        assert result == 50.00
        assert task.diff_status == "Positive"

    def test_missing_approx_cost_raises_error(self) -> None:
        """Test gdy task nie ma ustawionego cost_approx_pln"""
        task = _make_task(cost_approx_pln=None, cost_actual_pln=102.00)
        with pytest.raises(MissingCalculationDataError):
            get_actual_approx_cost_diff(task)

    def test_error_details_contain_context(self) -> None:
        """Test zawartości details w wyjątku - task_id i nazwa brakującego pola"""
        task = _make_task(cost_approx_pln=None)
        with pytest.raises(MissingCalculationDataError) as exc_info:
            get_actual_approx_cost_diff(task)
        assert exc_info.value.details["task_id"] == "task_dev_01"
        assert exc_info.value.details["missing_field"] == "cost_approx_pln"

    def test_error_does_not_mutate_task(self) -> None:
        """Test, że błąd walidacji nie zmienia stanu tasku"""
        task = _make_task(cost_approx_pln=None, cost_actual_pln=102.00)
        with pytest.raises(MissingCalculationDataError):
            get_actual_approx_cost_diff(task)
        assert task.diff is None
        assert task.diff_status == "Pending"

    def test_no_payment_does_not_raise(self) -> None:
        """Test, że brak płatności to poprawny stan, a nie błąd"""
        task = _make_task(cost_approx_pln=128.53, cost_actual_pln=None)
        assert get_actual_approx_cost_diff(task) is None


def _make_task_with_diff(task_id: str = "1", diff: float | None = None) -> Task:
    """Tworzy task testowy z ustawioną (lub nie) rozbieżnością"""
    return Task(
        task_start=datetime(2025, 11, 1, 9, 0),
        task_stop=datetime(2025, 11, 1, 11, 0),
        task_id=task_id,
        diff=diff,
    )


class TestGetDiffDay:
    """Testy sumowania rozbieżności dziennych (FR-421-12)"""

    def test_example(self) -> None:
        """Test przykładu (-26.53) + 5.00 + (task bez płatności) = -21.53"""
        tasks = [
            _make_task_with_diff("1", -26.53),
            _make_task_with_diff("2", 5.00),
            _make_task_with_diff("3", None),
        ]
        assert get_diff_day(tasks) == (-21.53, "Negative")

    def test_all_tasks_unpaid(self) -> None:
        """Test gdy żaden task nie ma płatności - dzień oczekujący"""
        tasks = [_make_task_with_diff("1"), _make_task_with_diff("2")]
        assert get_diff_day(tasks) == (None, "Pending")

    def test_empty_list(self) -> None:
        """Test pustej listy tasków - dzień oczekujący"""
        assert get_diff_day([]) == (None, "Pending")

    def test_overpayment_positive_status(self) -> None:
        """Test nadpłaty - status dodatni"""
        tasks = [_make_task_with_diff(
            "1", 10.00), _make_task_with_diff("2", 5.50)]
        assert get_diff_day(tasks) == (15.50, "Positive")

    def test_single_paid_among_unpaid(self) -> None:
        """Test gdy tylko jeden task z całego dnia ma płatność"""
        tasks = [
            _make_task_with_diff("1", None),
            _make_task_with_diff("2", -12.30),
            _make_task_with_diff("3", None),
        ]
        assert get_diff_day(tasks) == (-12.30, "Negative")

    def test_diffs_cancel_out_zero_status(self) -> None:
        """Test gdy rozbieżności się znoszą - status Zero, nie Pending"""
        tasks = [_make_task_with_diff(
            "1", -26.53), _make_task_with_diff("2", 26.53)]
        assert get_diff_day(tasks) == (0.0, "Zero")

    def test_single_zero_diff_is_not_pending(self) -> None:
        """Test że diff == 0 to płatność, a nie brak płatności"""
        assert get_diff_day([_make_task_with_diff("1", 0.0)]) == (0.0, "Zero")

    def test_result_is_not_negative_zero(self) -> None:
        """Test że wynik nie jest -0.0"""
        diff_day, _ = get_diff_day([_make_task_with_diff("1", -0.001)])
        assert str(diff_day) == "0.0"

    def test_does_not_mutate_input_tasks(self) -> None:
        """Test że funkcja nie zmienia stanu przekazanych tasków"""
        tasks = [_make_task_with_diff(
            "1", -26.53), _make_task_with_diff("2", 5.00)]
        get_diff_day(tasks)
        assert tasks[0].diff == -26.53
        assert tasks[1].diff == 5.00
