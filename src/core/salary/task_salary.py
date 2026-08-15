from models.task import Task
from models.day import day
import requests
from exceptions.finance_errors import InvalidHourdlyRateError, InvalidExchangeRateError
from exceptions.data_errors import MissingCalculationDataError
from datetime import datetime
from typing import Literal, List, Tuple, Optional
from helper.types import DiffStatus


def get_approx_cost_pln(task: Task, rate_pln_per_h: float) -> float:
    """
    Algorytm oblicza przybliżony koszt tasku w PLN na podstawie czasu pracy i stawki godzinowej.

    Args:
        task: Pojedyńczy task (Task)
        rate_pln_per_h: Kwota na godzinę w złotówkach (float)

    Returns:
        Przybliżony koszt tasku w PLN (float)

    Raises:
        InvalidHourdlyRateError: Stawka za godzinę musi być większa niż 0

    Examples:
        # Stawka za godzinę jest ustalona przy tworzeniu Taska
        >>> task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 11, ), rate_pln_per_h = 60)
        >>> approx_cost_pln(task, rate_pln_per_h=999)
        (120.0)

        # Stawka za godzinę nie jest ustalona przy tworzeniu Taska. Funkcja bierze kwotę na godzinę z argumentu funkcji
        >>> task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 11, ))
        >>> approx_cost_pln(task, rate_pln_per_h=120)
        (240.0)
    """
    rate = task.rate_pln_per_h if task.rate_pln_per_h is not None else rate_pln_per_h

    if rate <= 0.0:
        raise InvalidHourdlyRateError(
            details={
                "hourly_rate": rate
            }
        )

    duration_hours = task.duration_min / 60
    cost_approx_pln_raw = duration_hours * rate
    cost_approx_pln = round(cost_approx_pln_raw, 2)
    return cost_approx_pln


def get_approx_cost_from_pln_to_euro(task: Task) -> float:
    """
    Algorytm przelicza koszt przybliżony z PLN na EUR na podstawie aktualnego kursu.

    Args:
        task: Pojedyńczy task (Task)

    Returns:
        Przybliżony koszt tasku w EUR (float)

    Raises:
        InvalidExchangeRateError: Kurs przewalutowania z PLN na EUR musi być > 0

    Example:
        >>> task = Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),  task_stop=datetime(2025, 11, 1, 11, ), cost_approx_pln = 1500)
        >>> approx_cost_pln(task, rate_euro_pln=4.50)
        (333.33)
    """
    rate_euro_pln = task.exchange_rate_eur
    if task.cost_approx_pln is None:
        #! TODO: Zmienić w przyszłości ValueError na własny wyjątek błędu
        raise ValueError("Brak cost_approx_pln")

    if rate_euro_pln <= 0:
        raise InvalidExchangeRateError(
            details={
                "rate": rate_euro_pln
            }
        )
    cost_approx_eur_raw: float = task.cost_approx_pln / rate_euro_pln
    cost_approx_eur: float = round(cost_approx_eur_raw, 2)
    return cost_approx_eur


def get_nbp_euro_rate(task: Task) -> float:
    exchange_rate: float = 0.0

    def get_exchange_rate():
        #! TODO: Jak będzie udostępnione API do bazy danych to:
        #! Pobrac ostatni task, jeżeli jest to możliwe, to wziąć z niego kurs z pola exchange_rate_eur
        #! Jeżeli baza danych nie będzie posidać task, to użyć global_exchange_rate_eur
        #! jezeli brak global_exchange_rate_eur to zwracamy 0
        #! cała logika powinna być w funkcji wewnętrznej get_exchange_rate()
        pass

    date = task.created_at
    url = f"https://api.nbp.pl/api/exchangerates/rates/A/EUR/{date}?format=json"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        return round(float(data["rates"][0]["mid"]), 2)

    except requests.exceptions.RequestException:
        #! TODO: Jak będzie udostępnione API do bazy danych to:
        #! Pobrac ostatni task, jeżeli jest to możliwe, to wziąć z niego kurs z pola exchange_rate_eur
        #! Jeżeli baza danych nie będzie posidać task, to użyć global_exchange_rate_eur
        #! jezeli brak global_exchange_rate_eur to zwracamy 0
        #! cała logika powinna być w funkcji wewnętrznej get_exchange_rate()
        # fallback = task.last_rate if task.last_rate is not None else const_rate
        # if fallback is None:
        #     raise ValueError("Brak fallbacku: Podaj const_rate")
        exchange_rate = get_exchange_rate()
    finally:
        #! TODO: Jak będzie udostępnione API do bazy danych to:
        #! Pobrac ostatni task, jeżeli jest to możliwe, to wziąć z niego kurs z pola exchange_rate_eur
        #! Jeżeli baza danych nie będzie posidać task, to użyć global_exchange_rate_eur
        #! jezeli brak global_exchange_rate_eur to zwracamy 0
        #! cała logika powinna być w funkcji wewnętrznej get_exchange_rate()
        exchange_rate = get_exchange_rate()

    return exchange_rate


def get_actual_cost_pln(task: Task, cost_actual_pln_input: float, payment_date: datetime) -> float:
    """
    Algorytm oblicza faktyczny koszt taska w PLN.

    Args:
        task_id: Identyfikator taska
        cost_actual_pln_input: kwota podana przez użytkownika
        payment_date: data kiedy otrzymano płatność

    Returns:
        cost_actual_pln: Obliczony faktyczny koszt w PLN (float)

    Raises:
        ValueError: cost_actual_pln_input musi być > 0
        ValueError: pole task.cost_approx_pln musi być uzupełnione

    Example:
        >>> Task(
        ... task_start=datetime(2025, 11, 1, 19, 44),
        ... task_stop=datetime(2025, 11, 1, 20, 48),
        ... task_id="task_dev_01",
        ... comment="Development",
        ... cost_approx_pln=128.53
        ... )
        >>> result = get_actual_cost_pln(task, 102.00, datetime(2025, 11, 20))
        (102.0)
    """
    if cost_actual_pln_input <= 0.0:
        raise ValueError(
            f"cost_actual_pln_input: {cost_actual_pln_input} must be positive"
        )
    if task.cost_approx_pln is None:
        raise ValueError(
            f"Task {task.task_id} cost_approx_pln has not been set"
        )

    task.cost_actual_pln = round(cost_actual_pln_input, 2)
    task.status = "Zapłacone"
    task.payment_date = payment_date
    task.diff = round(task.cost_actual_pln - task.cost_approx_pln, 2)

    return task.cost_actual_pln


def get_actual_cost_euro_from_pln(cost_actual_pln: float, rate_eur_pln: float) -> float:
    """Algorytm przelicza koszt faktyczny z PLN na EUR na podstawie kursu z tasku.

    Args:
        cost_actual_pln: Aktualny koszt taska PLN
        rate_eur_pln: Kurs przewalutowania z PLN na EUR

    Returns:
        cost_actual_eur: Obliczony faktyczny koszt tasku w EUR (float)

    Raises:
        ValueError: Gdy cost_actual_pln <=0
        InvalidExchangeRateError: Gdy rate_eur_pln <=0

    Example:
        >>> get_actual_cost_euro_from_pln(cost_actual_pln: 100.00, rate_eur_pln: 4.22)
        (23.7)
    """

    if cost_actual_pln <= 0.0:
        raise ValueError(
            f"cost_actual_pln: {cost_actual_pln} must be positive"
        )
    if rate_eur_pln <= 0.0:
        raise InvalidExchangeRateError(
            details={"rate_eur_pln": rate_eur_pln}
        )
    cost_actual_eur_raw = cost_actual_pln / rate_eur_pln
    cost_actual_eur = round(cost_actual_eur_raw, 2)
    return cost_actual_eur


def get_actual_approx_cost_diff(task: Task) -> float | None:
    """Algorytm oblicza różnicę między kosztem faktycznym a przybliżonym (w PLN).

    Ustawia na tasku pola diff oraz diff_status.

    Args:
        task: Pojedyńczy task (Task)

    Returns:
        task.diff: Różnica między faktycznym a szacowanym kosztem taska (float),
            zaokrąglona do 2 miejsc po przecinku. Wartość dodatnia oznacza
            nadpłatę, ujemna niedopłatę.
            None, gdy task nie ma jeszcze faktycznej płatności.

    Raises:
        MissingCalculationDataError: task.cost_approx_pln jest puste

    Example:
        # Nadpłata
        >>> task = Task(
        ... task_start=datetime(2025, 11, 1, 19, 44),
        ... task_stop=datetime(2025, 11, 1, 20, 48),
        ... task_id="task_dev_01",
        ... comment="Development",
        ... cost_approx_pln=128.53,
        ... cost_actual_pln=130.00
        ... )
        >>> get_actual_approx_cost_diff(task)
        (1.47)

        # Niedopłata
        >>> task = Task(
                ... task_start=datetime(2025, 11, 1, 19, 44),
                ... task_stop=datetime(2025, 11, 1, 20, 48),
                ... task_id="task_dev_01",
                ... comment="Development",
                ... cost_approx_pln=128.53,
                ... cost_actual_pln=120.00
                ... )
                >>> get_actual_approx_cost_diff(task)
                (-8.53)

        # Brak płatności
        >>> task = Task(
        ... task_start=datetime(2025, 11, 1, 19, 44),
        ... task_stop=datetime(2025, 11, 1, 20, 48),
        ... task_id="task_dev_01",
        ... cost_approx_pln=128.53
        ... )
        >>> get_actual_approx_cost_diff(task)
        (None)
    """
    if task.cost_approx_pln is None:
        raise MissingCalculationDataError(
            details={
                "task_id": task.task_id,
                "missing_field": "cost_approx_pln"
            }
        )
    if task.cost_actual_pln is None:
        return None

    task.diff = round(task.cost_actual_pln - task.cost_approx_pln, 2)

    if task.diff > 0.0:
        task.diff_status = "Positive"
    elif task.diff < 0.0:
        task.diff_status = "Negative"
    else:
        task.diff_status = "Zero"

    return task.diff


def get_diff_day(tasks_day: List[Task]) -> Tuple[Optional[float], DiffStatus]:
    """
    Algorytm oblicza łączną rozbieżność dla danego dnia na podstawie rozbieżności
    poszczególnych tasków.

    Sumowane są wyłącznie taski z faktyczną płatnością, tzn. takie, dla których
    pole diff zostało już wyliczone. Taski bez płatności są pomijane. Jeżeli żaden
    task w dniu nie ma płatności, dzień pozostaje w stanie oczekiwania.

    Args:
        tasks_day: Lista tasków przypisanych do jednego dnia

    Returns:
        Krotka (diff_day, diff_day_status):
            diff_day: Łączna rozbieżność dnia w PLN (float) lub None, gdy brak płatności
            diff_day_status: Status rozbieżności dnia ("Pending", "Positive", "Negative", "Zero")

    Examples:
        >>> # Dzień z dwoma opłaconymi taskami i jednym bez płatności
        >>> tasks = [
        ...     Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),
        ...          task_stop=datetime(2025, 11, 1, 11, 0), diff=-26.53),
        ...     Task(task_id="2", task_start=datetime(2025, 11, 1, 12, 0),
        ...          task_stop=datetime(2025, 11, 1, 13, 0), diff=5.00),
        ...     Task(task_id="3", task_start=datetime(2025, 11, 1, 14, 0),
        ...          task_stop=datetime(2025, 11, 1, 15, 0)),
        ... ]
        >>> get_diff_day(tasks)
        (-21.53, 'Negative')

        >>> # Rozbieżności znoszą się wzajemnie
        >>> tasks = [
        ...     Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),
        ...          task_stop=datetime(2025, 11, 1, 11, 0), diff=-26.53),
        ...     Task(task_id="2", task_start=datetime(2025, 11, 1, 12, 0),
        ...          task_stop=datetime(2025, 11, 1, 13, 0), diff=26.53),
        ... ]
        >>> get_diff_day(tasks)
        (0.0, 'Zero')

        >>> # Żaden task nie ma jeszcze płatności
        >>> get_diff_day([Task(task_id="1", task_start=datetime(2025, 11, 1, 9, 0),
        ...                    task_stop=datetime(2025, 11, 1, 11, 0))])
        (None, 'Pending')
    """
    paid_diffs: List[float] = []
    diff_day_status: DiffStatus = "Pending"
    for task in tasks_day:
        if task.diff is None:
            continue
        paid_diffs.append(task.diff)

    if not paid_diffs:
        return None, "Pending"

    diff_day = round(sum(paid_diffs), 2)

    if diff_day > 0:
        diff_day_status = "Positive"
    elif diff_day < 0:
        diff_day_status = "Negative"
    elif diff_day == 0:
        diff_day_status = "Zero"
        diff_day = 0.0

    return diff_day, diff_day_status


def get_diff_month(days_in_month: List[day]) -> Tuple[Optional[float], DiffStatus]:
    """
    Algorytm oblicza łączną rozbieżność dla danego miesiąca na podstawie
    rozbieżności poszczególnych dni.

    Sumowane są wyłącznie dni, dla których udało się wyliczyć rozbieżność, tzn. takie,
    które mają co najmniej jeden task z faktyczną płatnością.
    Jeżeli żaden dzień w miesiącu nie ma płatności, miesiąc pozostaje w stanie oczekiwania.

    Args:
        days_in_month: Lista dni wchodzących w skład jednego miesiąca

    Returns:
        Krotka (diff_month, diff_month_status):
            diff_month: Łączna rozbieżność miesiąca w PLN (float) lub None, gdy brak płatności
            diff_month_status: Status rozbieżności miesiąca ("Pending", "Positive", "Negative", "Zero")
    """
    paid_diffs_day: List[float] = []
    diff_month_status: DiffStatus = "Pending"
    for day_in_month in days_in_month:
        diff_day, _ = get_diff_day(day_in_month.tasks)
        if diff_day is None:
            continue
        paid_diffs_day.append(diff_day)

    if not paid_diffs_day:
        return None, "Pending"

    diff_month = round(sum(paid_diffs_day), 2)

    if diff_month > 0:
        diff_month_status = "Positive"
    elif diff_month < 0:
        diff_month_status = "Negative"
    elif diff_month == 0:
        diff_month_status = "Zero"
        diff_month = 0.0

    return diff_month, diff_month_status
