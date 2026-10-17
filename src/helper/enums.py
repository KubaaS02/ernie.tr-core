from enum import StrEnum

class ChangeLogActions(StrEnum):
    unlock = "unlock"
    delete = "delete"
    field_change = "field_change"