from models.task import Task
import requests
from exceptions.finance_errors import InvalidHourdlyRateError, InvalidExchangeRateError


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

    if rate <= 0:
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
