from exceptions import BusinessError
from typing import Optional

"""Grupa błędów związanych z harmonogramem i czasem trwania"""
#TODO: dopisać opisy błędów
class InvalidTaskTimeRangeError(BusinessError):
    """Grupa błędów związanych z harmonogramem i czasem trwania"""

    error_id: Optional[str] = "ERR-TIME-01"
    error_code: Optional[str] = "invalid_task_time_range"
    http_status: Optional[int] = 400
    default_message: Optional[str] = "The start time of a task cannot be later than stop time"

class TaskOverlapError(BusinessError):
    
    error_id: Optional[str] = "ERR-TIME-02"
    error_code: Optional[str] = "task_overlap"
    http_status: Optional[int] = 409
    default_message: Optional[str] = "One task overlaps with another"
    #TODO: Zrobić commita; "Add class TaskOverlapError"