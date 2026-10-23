from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Klasa bazowa dla wszystkich modeli ORM"""

    pass


class TimestampMixin:
    """Wspólne pola created_at / updated_at uzupełniane przez bazę danych."""

    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), onupdate=func.now()
    )

