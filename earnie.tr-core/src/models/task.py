from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, Literal

@dataclass
class Task:
    """
    Model reprezentujący pojedyncze zadanie (task).
    
    Attributes:
        task_id: Unikatowy identyfikator zadania
        task_start: Data i czas rozpoczęcia pracy (format: YYYY-MM-DD HH:MM lub HH:MM:SS)
        task_stop: Data i czas zakończenia pracy (format: YYYY-MM-DD HH:MM lub HH:MM:SS)
        comment: Opis/nazwa projektu
        status: Status płatności (Zapłacone, Oczekuje, W trakcie)
        payment_date: Data faktycznej płatności (opcjonalnie)
    """
    
    task_start: datetime
    task_stop: datetime
    task_id: str
    comment: str = ""
    status: Literal["Zapłacone", "Oczekuje", "W trakcie"] = "Oczekuje"
    payment_date: Optional[datetime] = None
    
    def __post_init__(self) -> None:
        """Walidacja danych po inicjalizacji"""
        if self.task_start > self.task_stop:
            raise ValueError(
                f"task_start ({self.task_start}) nie może być później niż task_stop ({self.task_stop})"
            )
        
    
    def __repr__(self) -> str:
        return (
            f"Task(id={self.task_id}, start={self.task_start}, "
            f"stop={self.task_stop}, status={self.status})"
        )
