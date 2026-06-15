
from typing import Optional

class BusinessError(Exception):
    """
    Abstrakcyjna klasa bazowa dla wszystkich błędów domenowych Ernie.tr.
    Każda podklasa MUSI definiować unikalny error_id.
    """

    abstract: bool = True

    error_id: Optional[str] = "ERR-GENERIC"
    error_code: Optional[str] = "GENERIC_ERROR"
    http_status: Optional[int] = 500
    default_message: Optional[str] = "Unexpected business error"

    _registered_ids: set[str] = set()

    def __init_subclass__(cls) -> None:
        super().__init_subclass__()
        if getattr(cls, "abstract", False):
            return
        cls.abstract = False
        if not hasattr(cls, "error_id") or cls.error_id == "ERR-GENERIC":
            raise TypeError(
                f"{cls.__name__} must define his it's own error_id")
        if cls.error_id in cls._registered_ids:
            raise ValueError(f"Duplicate error_id detected:{cls.error_id}")

        cls._registered_ids.add(str(cls.error_id))

    def __init__(self, message: str | None = None, details: Optional[dict] = None, error_code: str | None = None):
        actual_message = message or self.default_message
        super().__init__(actual_message)
        self.message = actual_message
        self.details = details or {}
        self.error_code = error_code or self.error_code

    def to_json(self) -> dict:
        return {
            "error_code": self.error_code,
            "http_status": self.http_status,
            "message": self.message,
            "details": self.details
        }
