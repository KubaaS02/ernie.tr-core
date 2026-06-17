from exceptions import BusinessError
from typing import Optional

"""Grupa błędów związanych z harmonogramem i czasem trwania"""


class InvalidTaskTimeRangeError(BusinessError):
    """Klasa błędu związanego z niepoprawnym czasem zadania. Task_start > Task_stop"""

    error_id: Optional[str] = "ERR-TIME-01"
    error_code: Optional[str] = "invalid_task_time_range"
    http_status: Optional[int] = 400
    default_message: Optional[str] = "The start time of a task cannot be later than stop time"


class TaskOverlapError(BusinessError):
    """Klasa błędu związanego z pokrywającym się czasem zadań. Nowe zadanie czasowo pokrywa się z już istniejącym zadaniem użytkownika"""
    error_id: Optional[str] = "ERR-TIME-02"
    error_code: Optional[str] = "task_overlap"
    http_status: Optional[int] = 409
    default_message: Optional[str] = "One task overlaps with another"
