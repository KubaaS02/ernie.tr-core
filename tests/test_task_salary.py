import pytest
from tests import Task, day
from tests import (
    get_approx_cost_pln,
    get_approx_cost_from_pln_to_euro,
    get_actual_cost_pln,
    get_actual_cost_euro_from_pln,
    get_actual_approx_cost_diff,
    get_diff_day, get_diff_month,
    get_approx_day_cost,
    get_actual_day_cost,
    get_approx_month_cost,
    get_actual_month_cost)
from datetime import datetime, date
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


def _make_day_with_tasks(day_id: str = "2025-11-01", tasks: list[Task] | None = None) -> day:
    """Tworzy dzień testowy z podaną listą tasków"""
    return day(
        day_id=day_id,
        user_id="user_01",
        date=date(2025, 11, 1),
        tasks=tasks if tasks is not None else [],
        total_duration_min=0,
        total_duration_hm="00:00",
        cost_approx_day_pln=0.0,
        cost_approx_day_eur=0.0,
        cost_actual_day_pln=0.0,
        cost_actual_day_eur=0.0,
    )


class TestGetDiffMonth:
    """Testy sumowania rozbieżności miesięcznych (FR-421-13)"""

    def test_example(self) -> None:
        """Test przykładu (-21.53) + 10.00 + (dzień bez płatności) = -11.53"""
        days = [
            _make_day_with_tasks("2025-11-01", [
                _make_task_with_diff("1", -26.53),
                _make_task_with_diff("2", 5.00),
            ]),
            _make_day_with_tasks("2025-11-02", [
                _make_task_with_diff("3", 10.00),
            ]),
            _make_day_with_tasks("2025-11-03", [
                _make_task_with_diff("4", None),
            ]),
        ]
        assert get_diff_month(days) == (-11.53, "Negative")

    def test_empty_list(self) -> None:
        """Test pustej listy dni - miesiąc oczekujący"""
        assert get_diff_month([]) == (None, "Pending")

    def test_all_days_unpaid(self) -> None:
        """Test gdy żaden dzień nie ma płatności - miesiąc oczekujący"""
        days = [
            _make_day_with_tasks(
                "2025-11-01", [_make_task_with_diff("1", None)]),
            _make_day_with_tasks(
                "2025-11-02", [_make_task_with_diff("2", None)]),
        ]
        assert get_diff_month(days) == (None, "Pending")

    def test_overpayment_positive_status(self) -> None:
        """Test nadpłaty w skali miesiąca - status dodatni"""
        days = [
            _make_day_with_tasks(
                "2025-11-01", [_make_task_with_diff("1", 120.00)]),
            _make_day_with_tasks(
                "2025-11-02", [_make_task_with_diff("2", 35.50)]),
        ]
        assert get_diff_month(days) == (155.50, "Positive")

    def test_single_paid_day_among_empty_days(self) -> None:
        """Test gdy tylko jeden dzień z całego miesiąca ma płatność"""
        days = [
            _make_day_with_tasks(
                "2025-11-01", [_make_task_with_diff("1", None)]),
            _make_day_with_tasks(
                "2025-11-02", [_make_task_with_diff("2", -12.30)]),
            _make_day_with_tasks("2025-11-03"),
        ]
        assert get_diff_month(days) == (-12.30, "Negative")

    def test_days_cancel_out_zero_status(self) -> None:
        """Test gdy rozbieżności dni się znoszą - status Zero, nie Pending"""
        days = [
            _make_day_with_tasks(
                "2025-11-01", [_make_task_with_diff("1", -21.53)]),
            _make_day_with_tasks(
                "2025-11-02", [_make_task_with_diff("2", 21.53)]),
        ]
        assert get_diff_month(days) == (0.0, "Zero")

    def test_partially_paid_day_sums_only_paid_tasks(self) -> None:
        """Test że dzień z częścią tasków opłaconych wnosi tylko sumę opłaconych"""
        days = [
            _make_day_with_tasks("2025-11-01", [
                _make_task_with_diff("1", -26.53),
                _make_task_with_diff("2", None),
                _make_task_with_diff("3", 5.00),
            ]),
        ]
        assert get_diff_month(days) == (-21.53, "Negative")

    def test_result_is_not_negative_zero(self) -> None:
        """Test że wynik nie jest -0.0"""
        days = [_make_day_with_tasks(
            "2025-11-01", [_make_task_with_diff("1", -0.001)])]
        diff_month, _ = get_diff_month(days)
        assert str(diff_month) == "0.0"


def _make_task_with_approx(
    task_id: str = "1",
    cost_approx_pln: float | None = 128.53,
    cost_approx_eur: float | None = 30.47,
) -> Task:
    """Tworzy task testowy z ustawionymi (lub nie) kosztami przybliżonymi"""
    return Task(
        task_start=datetime(2025, 11, 1, 9, 0),
        task_stop=datetime(2025, 11, 1, 11, 0),
        task_id=task_id,
        cost_approx_pln=cost_approx_pln,
        cost_approx_eur=cost_approx_eur,
    )


class TestGetApproxDayCost:
    """Testy sumowania kosztów przybliżonych dziennych (FR-421-14)"""

    def test_example(self) -> None:
        """Test przykładu ze specyfikacji: 128.53 + 237.50 = 366.03 PLN, 30.47 + 56.28 = 86.75 EUR"""
        tasks = [
            _make_task_with_approx("1", 128.53, 30.47),
            _make_task_with_approx("2", 237.50, 56.28),
        ]
        assert get_approx_day_cost(tasks) == (366.03, 86.75)

    def test_empty_list(self) -> None:
        """Test pustej listy tasków - obie sumy zerowe"""
        assert get_approx_day_cost([]) == (0.0, 0.0)

    def test_single_task(self) -> None:
        """Test dnia z jednym taskiem - suma równa kosztowi taska"""
        tasks = [_make_task_with_approx("1", 128.53, 30.47)]
        assert get_approx_day_cost(tasks) == (128.53, 30.47)

    def test_zero_cost_task(self) -> None:
        """Test taska o koszcie zerowym - poprawna wartość, nie brak danych"""
        tasks = [_make_task_with_approx("1", 0.0, 0.0)]
        assert get_approx_day_cost(tasks) == (0.0, 0.0)

    def test_many_tasks(self) -> None:
        """Test sumowania wielu tasków w jednym dniu"""
        tasks = [
            _make_task_with_approx("1", 100.00, 23.70),
            _make_task_with_approx("2", 200.00, 47.39),
            _make_task_with_approx("3", 300.00, 71.09),
            _make_task_with_approx("4", 50.50, 11.97),
        ]
        assert get_approx_day_cost(tasks) == (650.50, 154.15)

    def test_unpaid_task_is_included(self) -> None:
        """Test, że task ze statusem 'Oczekuje' też wchodzi do sumy przybliżonej"""
        task = _make_task_with_approx("1", 128.53, 30.47)
        task.status = "Oczekuje"
        assert get_approx_day_cost([task]) == (128.53, 30.47)

    def test_mixed_statuses_all_included(self) -> None:
        """Test, że taski o różnych statusach są sumowane tak samo"""
        paid = _make_task_with_approx("1", 128.53, 30.47)
        paid.status = "Zapłacone"
        pending = _make_task_with_approx("2", 237.50, 56.28)
        pending.status = "Oczekuje"
        assert get_approx_day_cost([paid, pending]) == (366.03, 86.75)

    def test_missing_approx_pln_raises_error(self) -> None:
        """Test gdy task nie ma ustawionego cost_approx_pln"""
        tasks = [_make_task_with_approx("1", None, 30.47)]
        with pytest.raises(MissingCalculationDataError):
            get_approx_day_cost(tasks)

    def test_missing_approx_eur_raises_error(self) -> None:
        """Test gdy task nie ma ustawionego cost_approx_eur"""
        tasks = [_make_task_with_approx("1", 128.53, None)]
        with pytest.raises(MissingCalculationDataError):
            get_approx_day_cost(tasks)

    def test_error_details_contain_context_pln(self) -> None:
        """Test zawartości details w wyjątku - task_id i brakujące cost_approx_pln"""
        tasks = [_make_task_with_approx("task_dev_07", None, 30.47)]
        with pytest.raises(MissingCalculationDataError) as exc_info:
            get_approx_day_cost(tasks)
        assert exc_info.value.details["task_id"] == "task_dev_07"
        assert exc_info.value.details["missing_field"] == "cost_approx_pln"

    def test_error_details_contain_context_eur(self) -> None:
        """Test zawartości details w wyjątku - task_id i brakujące cost_approx_eur"""
        tasks = [_make_task_with_approx("task_dev_08", 128.53, None)]
        with pytest.raises(MissingCalculationDataError) as exc_info:
            get_approx_day_cost(tasks)
        assert exc_info.value.details["task_id"] == "task_dev_08"
        assert exc_info.value.details["missing_field"] == "cost_approx_eur"

    def test_error_points_to_first_incomplete_task(self) -> None:
        """Test, że wyjątek wskazuje pierwszy niekompletny task w dniu"""
        tasks = [
            _make_task_with_approx("1", 128.53, 30.47),
            _make_task_with_approx("2", None, 30.47),
            _make_task_with_approx("3", None, None),
        ]
        with pytest.raises(MissingCalculationDataError) as exc_info:
            get_approx_day_cost(tasks)
        assert exc_info.value.details["task_id"] == "2"

    def test_incomplete_task_is_not_silently_skipped(self) -> None:
        """Test, że brakujący koszt nie jest pomijany kosztem zaniżenia sumy dnia"""
        tasks = [
            _make_task_with_approx("1", 128.53, 30.47),
            _make_task_with_approx("2", None, None),
        ]
        with pytest.raises(MissingCalculationDataError):
            get_approx_day_cost(tasks)

    def test_does_not_mutate_input_tasks(self) -> None:
        """Test, że funkcja nie zmienia stanu przekazanych tasków"""
        tasks = [
            _make_task_with_approx("1", 128.53, 30.47),
            _make_task_with_approx("2", 237.50, 56.28),
        ]
        get_approx_day_cost(tasks)
        assert tasks[0].cost_approx_pln == 128.53
        assert tasks[0].cost_approx_eur == 30.47
        assert tasks[1].cost_approx_pln == 237.50
        assert tasks[1].cost_approx_eur == 56.28

    def test_does_not_modify_input_list(self) -> None:
        """Test, że funkcja nie zmienia długości przekazanej listy"""
        tasks = [_make_task_with_approx("1"), _make_task_with_approx("2")]
        get_approx_day_cost(tasks)
        assert len(tasks) == 2


def _make_task_with_actual(
    task_id: str = "1",
    cost_actual_pln: float | None = 102.00,
    cost_actual_eur: float | None = 24.17,
    status: str = "Zapłacone",
) -> Task:
    """Tworzy task testowy z ustawionymi (lub nie) kosztami faktycznymi"""
    return Task(
        task_start=datetime(2025, 11, 1, 9, 0),
        task_stop=datetime(2025, 11, 1, 11, 0),
        task_id=task_id,
        status=status,
        cost_actual_pln=cost_actual_pln,
        cost_actual_eur=cost_actual_eur,
    )


class TestGetActualDayCost:
    """Testy sumowania kosztów faktycznych dziennych (FR-421-15)"""

    def test_example(self) -> None:
        """Test przykładu ze specyfikacji: 102.00 + 110.50 = 212.50 PLN, 24.17 + 26.18 = 50.35 EUR"""
        tasks = [
            _make_task_with_actual("1", 102.00, 24.17),
            _make_task_with_actual("2", None, None, status="Oczekuje"),
            _make_task_with_actual("3", 110.50, 26.18),
        ]
        assert get_actual_day_cost(tasks) == (212.50, 50.35)

    def test_empty_list(self) -> None:
        """Test pustej listy tasków - obie sumy zerowe"""
        assert get_actual_day_cost([]) == (0.0, 0.0)

    def test_single_paid_task(self) -> None:
        """Test dnia z jednym opłaconym taskiem - suma równa kosztowi taska"""
        tasks = [_make_task_with_actual("1", 102.00, 24.17)]
        assert get_actual_day_cost(tasks) == (102.00, 24.17)

    def test_no_paid_tasks(self) -> None:
        """Test dnia bez opłaconych tasków - obie sumy zerowe, nie None"""
        tasks = [
            _make_task_with_actual("1", None, None, status="Oczekuje"),
            _make_task_with_actual("2", None, None, status="W trakcie"),
        ]
        assert get_actual_day_cost(tasks) == (0.0, 0.0)

    def test_pending_task_is_ignored(self) -> None:
        """Test, że task ze statusem 'Oczekuje' nie wchodzi do sumy"""
        tasks = [
            _make_task_with_actual("1", 102.00, 24.17),
            _make_task_with_actual("2", None, None, status="Oczekuje"),
        ]
        assert get_actual_day_cost(tasks) == (102.00, 24.17)

    def test_in_progress_task_is_ignored(self) -> None:
        """Test, że task ze statusem 'W trakcie' nie wchodzi do sumy"""
        tasks = [
            _make_task_with_actual("1", 102.00, 24.17),
            _make_task_with_actual("2", None, None, status="W trakcie"),
        ]
        assert get_actual_day_cost(tasks) == (102.00, 24.17)

    def test_unpaid_task_with_costs_is_ignored(self) -> None:
        """Test, że task nieopłacony jest pomijany mimo wypełnionych kosztów faktycznych"""
        tasks = [
            _make_task_with_actual("1", 102.00, 24.17),
            _make_task_with_actual("2", 500.00, 118.48, status="Oczekuje"),
        ]
        assert get_actual_day_cost(tasks) == (102.00, 24.17)

    def test_zero_cost_paid_task(self) -> None:
        """Test opłaconego taska o koszcie zerowym - poprawna wartość, nie brak danych"""
        tasks = [_make_task_with_actual("1", 0.0, 0.0)]
        assert get_actual_day_cost(tasks) == (0.0, 0.0)

    def test_many_paid_tasks(self) -> None:
        """Test sumowania wielu opłaconych tasków w jednym dniu"""
        tasks = [
            _make_task_with_actual("1", 100.00, 23.70),
            _make_task_with_actual("2", 200.00, 47.39),
            _make_task_with_actual("3", 300.00, 71.09),
            _make_task_with_actual("4", 50.50, 11.97),
        ]
        assert get_actual_day_cost(tasks) == (650.50, 154.15)

    def test_missing_actual_pln_raises_error(self) -> None:
        """Test gdy opłacony task nie ma ustawionego cost_actual_pln"""
        tasks = [_make_task_with_actual("1", None, 24.17)]
        with pytest.raises(MissingCalculationDataError):
            get_actual_day_cost(tasks)

    def test_missing_actual_eur_raises_error(self) -> None:
        """Test gdy opłacony task nie ma ustawionego cost_actual_eur"""
        tasks = [_make_task_with_actual("1", 102.00, None)]
        with pytest.raises(MissingCalculationDataError):
            get_actual_day_cost(tasks)

    def test_error_details_contain_context_pln(self) -> None:
        """Test zawartości details w wyjątku - task_id i brakujące cost_actual_pln"""
        tasks = [_make_task_with_actual("task_dev_09", None, 24.17)]
        with pytest.raises(MissingCalculationDataError) as exc_info:
            get_actual_day_cost(tasks)
        assert exc_info.value.details["task_id"] == "task_dev_09"
        assert exc_info.value.details["missing_field"] == "cost_actual_pln"

    def test_error_details_contain_context_eur(self) -> None:
        """Test zawartości details w wyjątku - task_id i brakujące cost_actual_eur"""
        tasks = [_make_task_with_actual("task_dev_10", 102.00, None)]
        with pytest.raises(MissingCalculationDataError) as exc_info:
            get_actual_day_cost(tasks)
        assert exc_info.value.details["task_id"] == "task_dev_10"
        assert exc_info.value.details["missing_field"] == "cost_actual_eur"

    def test_error_points_to_first_incomplete_paid_task(self) -> None:
        """Test, że wyjątek wskazuje pierwszy niekompletny opłacony task w dniu"""
        tasks = [
            _make_task_with_actual("1", 102.00, 24.17),
            _make_task_with_actual("2", None, 24.17),
            _make_task_with_actual("3", None, None),
        ]
        with pytest.raises(MissingCalculationDataError) as exc_info:
            get_actual_day_cost(tasks)
        assert exc_info.value.details["task_id"] == "2"

    def test_incomplete_unpaid_task_does_not_raise(self) -> None:
        """Test, że nieopłacony task bez kosztów nie powoduje błędu - jest po prostu pomijany"""
        tasks = [
            _make_task_with_actual("1", 102.00, 24.17),
            _make_task_with_actual("2", None, None, status="Oczekuje"),
        ]
        assert get_actual_day_cost(tasks) == (102.00, 24.17)

    def test_incomplete_paid_task_is_not_silently_skipped(self) -> None:
        """Test, że brakujący koszt opłaconego taska nie jest pomijany kosztem zaniżenia sumy dnia"""
        tasks = [
            _make_task_with_actual("1", 102.00, 24.17),
            _make_task_with_actual("2", None, None),
        ]
        with pytest.raises(MissingCalculationDataError):
            get_actual_day_cost(tasks)

    def test_does_not_mutate_input_tasks(self) -> None:
        """Test, że funkcja nie zmienia stanu przekazanych tasków"""
        tasks = [
            _make_task_with_actual("1", 102.00, 24.17),
            _make_task_with_actual("2", 110.50, 26.18),
        ]
        get_actual_day_cost(tasks)
        assert tasks[0].cost_actual_pln == 102.00
        assert tasks[0].cost_actual_eur == 24.17
        assert tasks[1].cost_actual_pln == 110.50
        assert tasks[1].cost_actual_eur == 26.18

    def test_does_not_change_task_status(self) -> None:
        """Test, że funkcja nie modyfikuje statusu płatności tasków"""
        pending = _make_task_with_actual("1", None, None, status="Oczekuje")
        get_actual_day_cost([pending])
        assert pending.status == "Oczekuje"

    def test_does_not_modify_input_list(self) -> None:
        """Test, że funkcja nie zmienia długości przekazanej listy"""
        tasks = [_make_task_with_actual("1"), _make_task_with_actual("2")]
        get_actual_day_cost(tasks)
        assert len(tasks) == 2


def _make_task_with_approx_cost(task_id: str,
                                cost_approx_pln: float | None,
                                cost_approx_eur: float | None) -> Task:
    """Tworzy task testowy z podanymi kosztami przybliżonymi"""
    return Task(
        task_id=task_id,
        task_start=datetime(2025, 11, 1, 9, 0),
        task_stop=datetime(2025, 11, 1, 11, 0),
        cost_approx_pln=cost_approx_pln,
        cost_approx_eur=cost_approx_eur,
    )


class TestGetApproxMonthCost:
    """Testy sumowania kosztów przybliżonych miesięcznych (FR-421-16)"""

    def test_example(self) -> None:
        """Test przykładu z wymagań: 366.03 + 240.00 = 606.03 PLN"""
        days = [
            _make_day_with_tasks("2025-11-01", [
                _make_task_with_approx_cost("1", 128.53, 30.47),
                _make_task_with_approx_cost("2", 237.50, 56.28),
            ]),
            _make_day_with_tasks("2025-11-02", [
                _make_task_with_approx_cost("3", 240.00, 56.87),
            ]),
        ]
        assert get_approx_month_cost(days) == (606.03, 143.62)

    def test_empty_list(self) -> None:
        """Test pustej listy dni - sumy zerowe"""
        assert get_approx_month_cost([]) == (0.0, 0.0)

    def test_days_without_tasks(self) -> None:
        """Test miesiąca złożonego wyłącznie z dni bez tasków"""
        days = [_make_day_with_tasks("2025-11-01"),
                _make_day_with_tasks("2025-11-02")]
        assert get_approx_month_cost(days) == (0.0, 0.0)

    def test_empty_days_do_not_affect_sum(self) -> None:
        """Test że dni bez tasków nie zmieniają sumy miesiąca"""
        days = [
            _make_day_with_tasks(
                "2025-11-01", [_make_task_with_approx_cost("1", 128.53, 30.47)]),
            _make_day_with_tasks("2025-11-02"),
            _make_day_with_tasks("2025-11-03"),
        ]
        assert get_approx_month_cost(days) == (128.53, 30.47)

    def test_single_day_single_task(self) -> None:
        """Test miesiąca z jednym dniem i jednym taskiem"""
        days = [_make_day_with_tasks(
            "2025-11-01", [_make_task_with_approx_cost("1", 100.00, 23.70)])]
        assert get_approx_month_cost(days) == (100.00, 23.70)

    def test_unpaid_tasks_are_included(self) -> None:
        """Test że taski nieopłacone wchodzą do sumy przybliżonej"""
        task = _make_task_with_approx_cost("1", 128.53, 30.47)
        task.status = "Oczekuje"
        days = [_make_day_with_tasks("2025-11-01", [task])]
        assert get_approx_month_cost(days) == (128.53, 30.47)

    def test_zero_cost_tasks(self) -> None:
        """Test miesiąca z taskami o zerowym koszcie"""
        days = [_make_day_with_tasks(
            "2025-11-01", [_make_task_with_approx_cost("1", 0.0, 0.0)])]
        assert get_approx_month_cost(days) == (0.0, 0.0)

    def test_result_is_float_for_empty_month(self) -> None:
        """Test że pusty miesiąc zwraca float, nie int"""
        cost_approx_month_pln, cost_approx_month_eur = get_approx_month_cost([
        ])
        assert isinstance(cost_approx_month_pln, float)
        assert isinstance(cost_approx_month_eur, float)

    def test_missing_approx_pln_raises_error(self) -> None:
        """Test błędu, gdy task w miesiącu ma puste cost_approx_pln"""
        days = [_make_day_with_tasks(
            "2025-11-01", [_make_task_with_approx_cost("1", None, 30.47)])]
        with pytest.raises(MissingCalculationDataError):
            get_approx_month_cost(days)

    def test_error_points_to_first_incomplete_task(self) -> None:
        """Test że błąd wskazuje pierwszy niekompletny task w miesiącu"""
        days = [
            _make_day_with_tasks(
                "2025-11-01", [_make_task_with_approx_cost("1", 128.53, 30.47)]),
            _make_day_with_tasks("2025-11-02", [
                _make_task_with_approx_cost("2", None, 30.47),
                _make_task_with_approx_cost("3", None, 30.47),
            ]),
        ]
        with pytest.raises(MissingCalculationDataError) as exc_info:
            get_approx_month_cost(days)
        assert exc_info.value.details["task_id"] == "2"
        assert exc_info.value.details["missing_field"] == "cost_approx_pln"

    def test_does_not_modify_input_list(self) -> None:
        """Test że funkcja nie modyfikuje listy dni"""
        days = [_make_day_with_tasks(
            "2025-11-01", [_make_task_with_approx_cost("1", 128.53, 30.47)])]
        get_approx_month_cost(days)
        assert len(days) == 1
        assert len(days[0].tasks) == 1


class TestGetActualMonthCost:
    """Testy sumowania kosztów faktycznych miesięcznych (FR-421-17)"""

    def test_example(self) -> None:
        """Test przykładu z wymagań: 212.50 + 180.00 = 392.50 PLN, 50.35 + 42.65 = 93.00 EUR"""
        days = [
            _make_day_with_tasks("2025-11-01", [
                _make_task_with_actual("1", 102.00, 24.17),
                _make_task_with_actual("2", 110.50, 26.18),
            ]),
            _make_day_with_tasks("2025-11-02", [
                _make_task_with_actual("3", 180.00, 42.65),
            ]),
        ]
        assert get_actual_month_cost(days) == (392.50, 93.00)

    def test_empty_list(self) -> None:
        """Test pustej listy dni - sumy zerowe"""
        assert get_actual_month_cost([]) == (0.0, 0.0)

    def test_days_without_tasks(self) -> None:
        """Test miesiąca złożonego wyłącznie z dni bez tasków"""
        days = [_make_day_with_tasks("2025-11-01"),
                _make_day_with_tasks("2025-11-02")]
        assert get_actual_month_cost(days) == (0.0, 0.0)

    def test_empty_days_do_not_affect_sum(self) -> None:
        """Test że dni bez tasków nie zmieniają sumy miesiąca"""
        days = [
            _make_day_with_tasks(
                "2025-11-01", [_make_task_with_actual("1", 102.00, 24.17)]),
            _make_day_with_tasks("2025-11-02"),
            _make_day_with_tasks("2025-11-03"),
        ]
        assert get_actual_month_cost(days) == (102.00, 24.17)

    def test_single_day_single_task(self) -> None:
        """Test miesiąca z jednym dniem i jednym opłaconym taskiem"""
        days = [_make_day_with_tasks(
            "2025-11-01", [_make_task_with_actual("1", 100.00, 23.70)])]
        assert get_actual_month_cost(days) == (100.00, 23.70)

    def test_unpaid_tasks_are_excluded(self) -> None:
        """Test że taski nieopłacone nie wchodzą do sumy faktycznej miesiąca"""
        days = [
            _make_day_with_tasks("2025-11-01", [
                _make_task_with_actual("1", 102.00, 24.17),
                _make_task_with_actual(
                    "2", 500.00, 118.48, status="Oczekuje"),
            ]),
        ]
        assert get_actual_month_cost(days) == (102.00, 24.17)

    def test_month_without_paid_tasks(self) -> None:
        """Test miesiąca bez ani jednego opłaconego taska - sumy zerowe, nie None"""
        days = [
            _make_day_with_tasks(
                "2025-11-01", [_make_task_with_actual("1", None, None, status="Oczekuje")]),
            _make_day_with_tasks(
                "2025-11-02", [_make_task_with_actual("2", None, None, status="W trakcie")]),
        ]
        assert get_actual_month_cost(days) == (0.0, 0.0)

    def test_zero_cost_paid_task(self) -> None:
        """Test miesiąca z opłaconym taskiem o koszcie zerowym"""
        days = [_make_day_with_tasks(
            "2025-11-01", [_make_task_with_actual("1", 0.0, 0.0)])]
        assert get_actual_month_cost(days) == (0.0, 0.0)

    def test_missing_actual_pln_raises_error(self) -> None:
        """Test błędu, gdy opłacony task w miesiącu ma puste cost_actual_pln"""
        days = [_make_day_with_tasks(
            "2025-11-01", [_make_task_with_actual("1", None, 24.17)])]
        with pytest.raises(MissingCalculationDataError):
            get_actual_month_cost(days)

    def test_missing_actual_eur_raises_error(self) -> None:
        """Test błędu, gdy opłacony task w miesiącu ma puste cost_actual_eur"""
        days = [_make_day_with_tasks(
            "2025-11-01", [_make_task_with_actual("1", 102.00, None)])]
        with pytest.raises(MissingCalculationDataError):
            get_actual_month_cost(days)

    def test_error_points_to_first_incomplete_task(self) -> None:
        """Test że błąd wskazuje pierwszy niekompletny opłacony task w miesiącu"""
        days = [
            _make_day_with_tasks(
                "2025-11-01", [_make_task_with_actual("1", 102.00, 24.17)]),
            _make_day_with_tasks("2025-11-02", [
                _make_task_with_actual("task_dev_02", None, 26.18),
                _make_task_with_actual("task_dev_03", None, 26.18),
            ]),
        ]
        with pytest.raises(MissingCalculationDataError) as exc_info:
            get_actual_month_cost(days)
        assert exc_info.value.details["task_id"] == "task_dev_02"
        assert exc_info.value.details["missing_field"] == "cost_actual_pln"

    def test_does_not_modify_input_list(self) -> None:
        """Test że funkcja nie modyfikuje listy dni"""
        days = [_make_day_with_tasks(
            "2025-11-01", [_make_task_with_actual("1", 102.00, 24.17)])]
        get_actual_month_cost(days)
        assert len(days) == 1
        assert len(days[0].tasks) == 1
