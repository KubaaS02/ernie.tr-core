from typing import Literal

type DiffStatus = Literal["Positive", "Negative", "Zero", "Pending"]
type ChangeLogActions = Literal["unlock", "delete", "field_change"] #dodac do helpers.enum i zmienić z Literal i Enum