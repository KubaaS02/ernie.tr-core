
class BusinessError(Exception):
    """
    Abstrakcyjna klasa bazowa dla wszystkich błędów domenowych Ernie.tr.
    Każda podklasa MUSI definiować unikalny error_id.
    """
    error_id: str = "ERR-GENERIC"
    abstract: bool = True
    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if getattr(cls, "abstract", False):
            return
        if not hasattr(cls, "error_id"):
            raise TypeError(f"{cls.__name__} must define his own error code")
        
    
    
    def __init__(self, message: str | None = None, details: dict | None =  None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
    
class FinanceError(BusinessError):
    """
    Grupa błędow związanych z obliczeniami i walutami
    """
    abstract: bool = True
    
    ...

class InvalidExchangeRateError(FinanceError):
    error_id: str = "ERR-FIN-01"
    error_code: str = "invalid_exchange_rate"
    http_status: int = 422
    message: str = "Nieprawidłowy kurs walut."
    details: dict = {}

class InvalidHourlyRateError(FinanceError):
    error_id: str = "ERR-FIN-02"
    error_code: str = "invalid_hourly_rate"
    http_status: int = 422
    message: str = "Nieprawidłowa stawka godzinowa."
    details: dict = {}

class TimeError(BusinessError):
    """
    Grupa błędów związanych z harmonogramem i czasem trwania.
    """
    abstract: bool = True
    ...

class InvalidTaskTimeRangeError(TimeError):
    error_id: str = "ERR-TIME-01"
    error_code: str = "invalid_task_time_range"
    http_status: int = 400
    message: str = "Data rozpoczęcia zadania, nie może być późniejsza niż jego zakończenie."
    details: dict = {}

class TaskOverlapError(BusinessError):
    error_id: str = "ERR-TIME-02"
    error_code: str = "task_overlap"
    http_status: int = 409
    message: str = "Data rozpoczęcia nowego zadania pokrywa się z istniejącym już zadaniem"
    details: dict = {}

class AuthorizationError(BusinessError):
    """
    Grupa błędów związana z uprawnieniami
    """
    abstract: bool = True
    ...

class TaskLockedError(AuthorizationError):
    error_id: str = "ERR-AUTH-01"
    error_code: str = "task_locked"
    http_status: int = 403
    message: str = "Próba zmiany zablokowanego zadania"
    details: dict = {}
    
    def __init__(self, task_id: int):
        msg:str = f"Zadanie o ID {task_id} jest zapłacone i zablokowane do edycji."
        super().__init__(msg: str, details: dict = {"task_id": task_id})

class ReferenceError(BusinessError):
    """
    Grupa błędów związana z relacjami
    """
    abstract: bool = True
    ...

class ProjectInUseError(ReferenceError):
    error_id: str = "ERR-REF-01"
    error_code: str = "project_in_use"
    http_status: int = 409
    message: str = "Próba usunięcia projektu, do którego są przypisane aktywane zadania"
    details: dict = {}

class EntityNotFoundError(ReferenceError):
    error_id: str = "ERR-REF-02"
    error_code: str = "entity_not_found"
    http_status: int = 404
    message: str = "Próba operacji po nieistniejącym ID"
    details: dict = {}

class DataError(BusinessError):
    """
    Grupa błędów związanych z błędami danych wejściowych
    """
    abstract: bool = True
    ...

class MissingCalculationDataError(DataError):
    error_id: str = "ERR-DATA-01"
    error_code: str = "missing_calculation_data"
    http_status: int = 400
    message: str = "Brakuje duration_min lub stawki przy próbie kalkulacji kosztów"
    details: dict = {}

class IntegrationError(BusinessError):
    """
    Grupa błędów związanych z komunikacji z zewnętrznymi usługami
    """
    abstract: bool = True
    ...

class NbpApiUnavailableError(IntegrationError):
    error_id: str = "ERR-INT-01"
    error_code: str = "nbp_api_unvailable"
    http_status: int = 503
    message: str = "PNI NBP ie odpowiada oraz brak kursu w pamięci podręcznej"
    details: dict = {}

