
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from exceptions.data_errors import IncompleteChangeLogEntryError
from helper.types import ChangeLogActions


@dataclass
class ChangeLogEntry:
    """
    Model reprezentujący pojedynczy wpis w historii zmian (change log)

    Attributes:
        task_id: Identyfikator zadania, do którego odnosi się wpis
        user_id: Identyfikator użytkownika wykonującego akcję
        timestamp: Znacznik czasu wykonania akcji
        action: Typ akcji (unlock, delete, field_change)
        field: Nazwa zmienionego pola (wyłącznie dla action = "field_change")
        old_value: Wartość pola przed zmianą (wyłącznie dla action = "field_change")
        new_value: Wartość pola po zmianie (wyłącznie dla action = "field_change")
        reason: Uzasadnienie akcji (opcjonalnie, głównie dla "unlock")
    """

    task_id: str
    user_id: str
    timestamp: datetime
    action: ChangeLogActions
    field: Optional[str] = None
    old_value: Optional[str] = None
    new_value: Optional[str] = None
    reason: Optional[str] = None

    def __post_init__(self) -> None:
        """Walidacja danych po inicjalizacji"""
        change_fields = ("field", "old_value", "new_value")
        filled = [name for name in change_fields
                  if getattr(self, name) is not None]

        if self.action == "field_change":
            missing = [name for name in change_fields if name not in filled]
            if missing:
                raise IncompleteChangeLogEntryError(
                    details={
                        "task_id": self.task_id,
                        "action": self.action,
                        "missing_fields": missing
                    }
                )
        elif filled:
            raise IncompleteChangeLogEntryError(
                details={
                    "task_id": self.task_id,
                    "action": self.action,
                    "unexpected_fields": filled
                }
            )

    def __repr__(self) -> str:
        return (
            f"ChangeLogEntry(task_id={self.task_id}, action={self.action}, "
            f"timestamp={self.timestamp})"
        )
