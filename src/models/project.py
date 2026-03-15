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
    rate_project_pln_per_h: float = None
    created_at: datetime
    is_active: bool