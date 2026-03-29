from datetime import datetime
from dataclasses import dataclass


@dataclass
class User:
    """
    Model reprezentujący pojedyńczego uzytkownika (user)

    Attributes:
        user_id: Unikatowy identyfikator użytkownika
        email: Email użytkownika
        name: Imię użytkownika
        default_rate_pln_per_h: Domyślna stawka za godzine w złotówkach
        preferred_currency: Preferowana waluta (format: str ("PLN", "EUR"))
        timezone: Strefa czasowa użytkownika
        created_at: Data stworzenia użytkownika
    """

    user_id: str
    email: str
    name: str
    default_rate_pln_per_h: float
    preffered_currency: str
    timezone: str
    created_at: datetime

    def is_user_id_unique(self):
        return NotImplementedError("This validation method must be implemented after succes bridge with Database")
