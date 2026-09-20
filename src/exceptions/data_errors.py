from exceptions.handler_error import BusinessError
from typing import Optional

"""Błędy spójności danych wejściowych, np. brak wymaganych pól do wykonania kalkulacji."""


class MissingCalculationDataError(BusinessError):
    """Błąd związany z brakującymi danymi potrzebnymi do kalkulacji kosztu"""

    error_id: Optional[str] = "ERR-DATA-01"
    error_code: Optional[str] = "missing_calculation_data"
    http_status: Optional[int] = 400
    default_message: Optional[str] = "Lack of data needed to calculate costs"


class IncompleteChangeLogEntryError(BusinessError):
    """Błąd związany z niekompletnym wpisem w historii zmian (change log)"""

    error_id: Optional[str] = "ERR-DATA-04"
    error_code: Optional[str] = "incomplete_change_log_entry"
    http_status: Optional[int] = 500
    default_message: Optional[str] = "The change log entry is incomplete."
