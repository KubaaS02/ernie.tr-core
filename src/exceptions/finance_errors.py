
from exceptions import BusinessError
from typing import Optional

"""Grupy błędów związane z finansami"""


class InvalidExchangeRateError(BusinessError):
    """Klasa błędu, który powinien zostać wywołany gdy kurs wymiany waluty będzie nieodpowiedni, tzn <=0"""

    error_id: Optional[str] = "ERR-FIN-01"
    error_code: Optional[str] = "invalid_exchange_rate"
    http_status: Optional[int] = 422
    default_message: Optional[str] = "The exchange rate is incorrect, <=0"
