
from exceptions import BusinessError
from typing import Optional

"""Grupa błędów związana z autoryzacją"""

class TaskLockedError(BusinessError):
    """Klasa błędu, który powinien zostać wywołany, gdy task będzie zablokowany, tzn is_locked=True"""

    error_id: Optional[str] = "ERR-AUTH-01"
    error_code: Optional[str] = "task_locked"
    http_status: Optional[int] = 403
    default_message: Optional[str] = "The task is locked. It cannot be modified."