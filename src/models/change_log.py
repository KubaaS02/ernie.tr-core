
from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from exceptions.data_errors import IncompleteChangeLogEntryError
from helper.enums import ChangeLogActions
from helper.text import is_blank

CLEARABLE_FIELDS: frozenset[str] = frozenset({"comment"})

# Fields whose values must not appear in logs or error reports (4.0.3)
RESTRICTED_FIELDS: frozenset[str] = frozenset({
    "comment",
    "cost_approx_pln",
    "cost_approx_eur",
    "cost_actual_pln",
    "cost_actual_eur",
    "rate_pln_per_h",
    "diff",
})


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

    Raises:
        TypeError: Gdy timestamp nie jest obiektem datetime albo gdy field,
            old_value lub new_value nie jest str. ani None
        ValueError: Gdy action nie jest jedną z wartości ChangeLogActions
        IncompleteChangeLogEntryError: Gdy action = field_change oraz:
            - brakuje field, old_value lub new_value (None),
            - field jest pusty lub składa się z samych białych znaków,
            - new_value składa się z samych białych znaków,
            - new_value = "" dla pola spoza CLEARABLE_FIELDS
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

        if not isinstance(self.timestamp, datetime):
            raise TypeError(
                f"timestamp must be datetime, got {type(self.timestamp).__name__}"
            )

        self.action = ChangeLogActions(self.action)

        change_fields = ("field", "old_value", "new_value")
        for name in change_fields:
            value = getattr(self, name)
            if value is not None and not isinstance(value, str):
                raise TypeError(
                    f"{name} must be str or None, got {type(value).__name__}"
                )
        if self.action is ChangeLogActions.field_change:
            missing = [name for name in change_fields
                       if self._is_missing(name)]
            if missing:
                raise IncompleteChangeLogEntryError(
                    details={
                        "task_id": self.task_id,
                        "action": self.action,
                        "missing_fields": missing
                    }
                )

    def _is_missing(self, name: str) -> bool:
        """
        Sprawdza, czy pole zmiany nie niesie wymaganych danych.

        Reguły dla poszczególnych pól:
            - field: brak, gdy None albo pusty / same białe znaki
            - old_value: brak tylko, gdy None (zapis stanu z przeszłości)
            - new_value: brak, gdy None albo pusty / same białe znaki;
              wyjątek: "" dla pól z CLEARABLE_FIELDS oznacza wyczyszczenie pola

        Args:
            name: Nazwa pola zmiany ("field", "old_value" lub "new_value")

        Returns:
            True, gdy pole należy zgłosić jako brakujące, w przeciwnym razie False
        """
        value = getattr(self, name)
        if value is None:
            return True

        if name == "field":
            return is_blank(value)

        if name == "new_value":
            is_cleared = value == "" and self.field in CLEARABLE_FIELDS
            return is_blank(value) and not is_cleared

        return False

    def __repr__(self) -> str:
        if self.field in RESTRICTED_FIELDS:
            new_value = "<Restricted field representation>"
        else:
            new_value = repr(self.new_value)
        return (
            f"ChangeLogEntry(task_id={self.task_id}, action={self.action}, "
            f"field={self.field}, new_value={new_value}, "
            f"timestamp={self.timestamp})"
        )

