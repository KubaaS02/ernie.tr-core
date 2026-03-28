from datetime import datetime, timedelta, date
from dataclasses import dataclass
from typing import Optional, Literal
from core.time.task_duration import calculate_task_duration
@dataclass
class Task:
    """
    Model reprezentujący pojedyncze zadanie (task).
    
    Attributes:
        task_id: Unikatowy identyfikator taska
        task_start: Data i czas rozpoczęcia pracy (format: YYYY-MM-DD HH:MM lub HH:MM:SS)
        task_stop: Data i czas zakończenia pracy (format: YYYY-MM-DD HH:MM lub HH:MM:SS)
        comment: Opis/nazwa projektu
        status: Status płatności (Zapłacone, Oczekuje, W trakcie)
        payment_date: Data faktycznej płatności (opcjonalnie)
        exchange_rate_eur: Kurs euro
        duration_min: Czas trwania taska
        payment_date: Data zapłacenia za taska
        rate_pln_per_h: Godzinowa stawka za zadanie w złotówkach
        description: Opis taska
        cost_approx_pln: Przewidywany koszt w złotówkach
        cost_approx_eur: Przewidywany koszt w euro
        cost_actual_pln: Faktyczny koszt w złotówkach
        cost_actual_eur: Faktyczny koszt w euro
        title: Tytuł taska
        task_date: Data taska
        created_at: Data stworzenia taska
        updated_at: Data zaaktualizowania taska
        is_locked: Informacja, czy task jest zablokowany, czy nie
        diff: Różnica pieniężna taska
    """
    
    task_start: datetime
    task_stop: datetime
    task_id: str
    comment: str = ""
    exchange_rate_eur: float = 0.0
    duration_min: int = 1
    status: Literal["Zapłacone", "Oczekuje", "W trakcie"] = "Oczekuje"
    payment_date: Optional[datetime] = None
    rate_pln_per_h: Optional[float] = None
    description: Optional[str] = None
    cost_approx_pln: Optional[float] = None
    cost_approx_eur: Optional[float] = None
    cost_actual_pln: Optional[float] = None
    cost_actual_eur: Optional[float] = None
    title: Optional[str] = None
    task_date: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_locked: Optional[bool] = None
    diff: Optional[float] = None
    def __post_init__(self) -> None:
        """Walidacja danych po inicjalizacji"""
        if self.task_start > self.task_stop:
            raise ValueError(
                f"task_start ({self.task_start}) nie może być później niż task_stop ({self.task_stop})"
            )
        self.duration_min = calculate_task_duration(self.task_start, self.task_stop)
    
    def __repr__(self) -> str:
        return (
            f"Task(id={self.task_id}, start={self.task_start}, "
            f"stop={self.task_stop}, status={self.status})"
        )