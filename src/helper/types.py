from typing import Literal

type DiffStatus = Literal["Positive", "Negative", "Zero", "Pending"]
type ChangeLogActions = Literal["unlock", "delete", "field_change"]