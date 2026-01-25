from datetime import datetime, time
from typing import Union


def _to_minutes_from_midnight(dt: datetime) -> int:
    """
    Konwertuje czas doby na minuty od północy (00:00).
    
    Args:
        dt: Obiekt datetime
        
    Returns:
        Liczba minut od północy (0-1440)
    """
    return dt.hour * 60 + dt.minute


def _parse_datetime(dt_input: Union[str, datetime]) -> datetime:
    """
    Parsuje wejście do formatu datetime.
    
    Obsługuje formaty:
    - "YYYY-MM-DD HH:MM"
    - "YYYY-MM-DD HH:MM:SS"
    - obiekt datetime
    
    Args:
        dt_input: String lub datetime
        
    Returns:
        Obiekt datetime
        
    Raises:
        ValueError: Jeśli format nie jest obsługiwany
    """
    if isinstance(dt_input, datetime):
        return dt_input
    
    if isinstance(dt_input, str):
        try:
            return datetime.strptime(dt_input, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass

        try:
            return datetime.strptime(dt_input, "%Y-%m-%d %H:%M")
        except ValueError:
            raise ValueError(
                f"Nieobsługiwany format czasu: {dt_input}. "
                f"Obsługiwane: 'YYYY-MM-DD HH:MM' lub 'YYYY-MM-DD HH:MM:SS'"
            )
    
    raise TypeError(f"Oczekiwano str lub datetime, otrzymano {type(dt_input)}")


def calculate_task_duration(
    task_start: Union[str, datetime],
    task_stop: Union[str, datetime]
) -> int:
    """
    Oblicza czas trwania tasku w minutach.
    
    Obsługuje:
    - Zwykłe taski (start i stop tego samego dnia)
    - Taski przechodzące przez północ (start dzisiaj, stop jutro)
    - Sekundy (są zaokrąglane do minut)
    - Minimalna jednostka = 1 minuta
    
    Args:
        task_start: Czas rozpoczęcia (str lub datetime)
                Format: "YYYY-MM-DD HH:MM" lub "YYYY-MM-DD HH:MM:SS"
        task_stop: Czas zakończenia (str lub datetime)
                Format: "YYYY-MM-DD HH:MM" lub "YYYY-MM-DD HH:MM:SS"
    
    Returns:
        Czas trwania tasku w minutach (minimum 1)
    
    Raises:
        ValueError: Jeśli task_start > task_stop
        TypeError: Jeśli format wejścia jest nieprawidłowy
    
    Examples:
        >>> # Zwykły task - 64 minuty
        >>> calculate_task_duration(
        ...     "2025-11-01 19:44",
        ...     "2025-11-01 20:48"
        ... )
        64
        
        >>> # Task przez północ - 45 minut
        >>> calculate_task_duration(
        ...     "2025-11-01 23:30",
        ...     "2025-11-02 00:15"
        ... )
        45
        
        >>> # Krótki task z sekundami - 1 minuta
        >>> calculate_task_duration(
        ...     "2025-11-01 09:00:00",
        ...     "2025-11-01 09:00:45"
        ... )
        1
    """
    start = _parse_datetime(task_start)
    stop = _parse_datetime(task_stop)
    
    if start > stop:
        raise ValueError(
            f"task_start ({start}) nie może być później niż task_stop ({stop})"
        )
    
    duration_raw = (stop - start).total_seconds() / 60
    
    if start.date() != stop.date() and duration_raw < 0:
        pass

    duration_minutes = round(duration_raw)
    
    return max(duration_minutes, 1)

def time_conversion(duration_min: int) -> str:
    """
    Konwertuje czas pracy z minut na format godzin i minut (HH:MM)
    
    Args:
        Czas pracy w minutach (int)
    
    Returns:
        Czas pracy w formacie string (HH:MM)
    
    Raises:
        TypeError: Jeśli format danych wejściowych jest niepoprawny
        ValueError: Jeśli duration_min < 0
    
    Examples:
        >>> # zwykły task 64 min
        >>> time_conversion(64)
        01:04
    """
    if not isinstance(duration_min, int):
        raise TypeError(
            f"{duration_min} musi być int a dostałem: {type(duration_min).__name__}"
        )
    if duration_min < 0:
        raise ValueError(
            f"{duration_min} musi być większe od 0"
        )
    hours = duration_min // 60
    minutes_remainder = duration_min % 60
    return print(f"{hours:02d}:{minutes_remainder:02d}")