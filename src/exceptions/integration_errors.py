
from exceptions import BusinessError
from typing import Optional

"""Błędy komunikacji z zewnętrznymi usługami, w tym przypadku głównie z API NBP."""

class NbpApiUnavailableError(BusinessError):
    """Klasa błędu, który powinien zostać wywołany, gdy nie uda się połączyć z API NBP"""
    
    error_id: Optional[str] = "ERR-INT-01"
    error_code: Optional[str] = "nbp_api_unavailable"
    http_status: Optional[int] = 503
    default_message: Optional[str] = "Unable to connect to the NBP API"