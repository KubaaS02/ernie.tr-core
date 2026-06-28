
from exceptions import BusinessError
from typing import Optional

"""Błąd ogólny nie związany z projektem, a z interpreterem Python."""


class GenericSystemError(BusinessError):
    """Wewnętrzny błąd systemu"""

    error_id: Optional[str] = "ERR-GENERIC-01"
    error_code: Optional[str] = "internal_error"
    http_status: Optional[int] = 500
    default_message: Optional[str] = "System error"
