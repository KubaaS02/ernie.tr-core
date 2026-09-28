import pytest

from exceptions.finance_errors import InvalidHourlyRateError
from tests import Task
from tests import get_approx_cost_pln, get_approx_cost_from_pln_to_euro, get_actual_cost_pln, get_actual_cost_euro_from_pln
from datetime import datetime
from tests import InvalidExchangeRateError, MissingCalculationDataError


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

    ## This doesnt seem right
    def test_test_approx_cost_pln_is0(self) -> None:
        """Test, czy funkcja pokaże błąd, gdy stawka godzinowa wynosi 0"""
        task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),
                    task_stop=datetime(2025, 11, 1, 11, ), rate_pln_per_h=0)
        with pytest.raises(InvalidHourlyRateError):
            get_approx_cost_pln(task, rate_pln_per_h=0)

    ## I would write it this way
    def test_get_approx_cost_pln_raises_for_zero_hourly_rate(self) -> None:
        task = Task(
            task_id="1",
            task_start=datetime(2025, 11, 1, 9),
            task_stop=datetime(2025, 11, 1, 11),
            rate_pln_per_h=0,
        )

        with pytest.raises(InvalidHourlyRateError) as exc_info:
            get_approx_cost_pln(task, rate_pln_per_h=100)

        assert exc_info.value.details["hourly_rate"] == 0

    ## And right after, which should be sufficient
    def test_get_approx_cost_pln_raises_for_negative_hourly_rate(self) -> None:
        task = Task(
            task_id="1",
            task_start=datetime(2025, 11, 1, 9),
            task_stop=datetime(2025, 11, 1, 11),
            rate_pln_per_h=-50,
        )

        with pytest.raises(InvalidHourlyRateError):
            get_approx_cost_pln(task, rate_pln_per_h=100)

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

    ## Additional tests

    def test_get_actual_cost_pln_rounds_input_to_two_decimal_places(self) -> None:
        task = _make_task(cost_approx_pln=100)

        result = get_actual_cost_pln(
            task,
            123.4567,
            datetime(2025, 11, 20),
        )

        assert result == 123.46
        assert task.cost_actual_pln == 123.46

    def test_get_actual_cost_pln_calculates_diff_using_rounded_actual_cost(self) -> None:
        task = _make_task(cost_approx_pln=100)

        get_actual_cost_pln(
            task,
            123.456,
            datetime(2025, 11, 20),
        )

        assert task.diff == 23.46

    def test_get_actual_cost_pln_does_not_mutate_task_when_amount_is_zero(self) -> None:
        task = _make_task()

        with pytest.raises(ValueError):
            get_actual_cost_pln(
                task,
                0,
                datetime(2025, 11, 20),
            )

        assert task.cost_actual_pln is None
        assert task.payment_date is None
        assert task.status == "Oczekuje"
        assert task.diff is None


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

    ## Additional tests PLN -> EUR

    def test_get_approx_cost_from_pln_to_euro_raises_when_cost_is_missing(self) -> None:
        task = Task(
            task_id="1",
            task_start=datetime(2025, 11, 1, 9),
            task_stop=datetime(2025, 11, 1, 11),
            cost_approx_pln=None,
            exchange_rate_eur=4.5,
        )

        with pytest.raises(ValueError):
            get_approx_cost_from_pln_to_euro(task)

    @pytest.mark.parametrize(
        "exchange_rate",
        [
            0,
            -1,
            -4.5,
        ],
    )
    def test_get_approx_cost_from_pln_to_euro_rejects_invalid_exchange_rate(
            self,
            exchange_rate: float,
    ) -> None:
        task = Task(
            task_id="1",
            task_start=datetime(2025, 11, 1, 9),
            task_stop=datetime(2025, 11, 1, 11),
            cost_approx_pln=100,
            exchange_rate_eur=exchange_rate,
        )

        with pytest.raises(InvalidExchangeRateError):
            get_approx_cost_from_pln_to_euro(task)



    @pytest.mark.parametrize(
        "cost_actual_pln",
        [
            0,
            -0.01,
            -100,
        ],
    )
    def test_get_actual_cost_euro_from_pln_rejects_non_positive_cost(
            self,
            cost_actual_pln: float,
    ) -> None:
        with pytest.raises(ValueError):
            get_actual_cost_euro_from_pln(
                cost_actual_pln,
                4.22,
            )