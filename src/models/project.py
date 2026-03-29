from datetime import datetime
from dataclasses import dataclass


@dataclass
class project:
    """
    Model reprezentujący jeden projekt (project)

    Attributes:
        project_id: Unikatowy identyfikator projektu
        user_id: Identyfikator użytkownika
        name: Nazwa projektu
        description: Opis projektu
        rate_project_pln_per_h: Kwota na godzinę podawana w zł w danym projekcie
        created_at: Data stworzenia projektu
        is_active: Informacja, czy dany projekt jest aktywny
    """

    project_id: str
    user_id: str
    name: str
    description: str
    created_at: datetime
    is_active: bool
    rate_project_pln_per_h: float = 0.0

    def is_project_id_unique(self):
        raise NotImplementedError(
            "This validation method must be implemented after succes bridge with Database")

    def correct_rate_project_pln_per_h(self):
        raise NotImplementedError(
            "This validation method must be implemented after succes bridge with Database")

    def created_at_is_real(self):
        raise NotImplementedError(
            "This validation method must be implemented after succes bridge with Database")

    def is_active_have_only_True_or_False(self):
        raise NotImplementedError(
            "This validation method must be implemented after succes bridge with Database")
