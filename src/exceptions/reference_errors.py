from exceptions import BusinessError
from typing import Optional

"""Błędy relacji (referencji) między obiektami"""


class ProjectInUseError(BusinessError):
    error_id: Optional[str] = "ERR-REF-01"
    error_code: Optional[str] = "project_in_use"
    http_status: Optional[int] = 409
    default_message: Optional[str] = "You cannot delete the project. It is in use in another task."


class EntityNotFoundError(BusinessError):
    error_id: Optional[str] = "ERR-REF-02"
    error_code: Optional[str] = "entity_not_found"
    http_status: Optional[int] = 404
    default_message: Optional[str] = "The entity was not found."
