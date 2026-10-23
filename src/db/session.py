import os
from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import ConnectionPoolEntry

DATABASE_URL_ENV_VAR = "EARNI_DATABASE_URL"
DEFAULT_DATABASE_URL = "sqlite+aiosqlite:///./earni.db"


def get_secure_dsn() -> str:
    """Zwraca connection string bazy danych ze zmiennej środowiskowej.

    Wartość jest czytana z EARNI_DATABASE_URL. Jeżeli zmienna nie jest
    ustawiona, zwracana jest lokalna baza SQLite (model lokalny z 4.0.3).
    Funkcja jest wspólna dla aplikacji i Alembic (FR-415-9).

    Returns:
        Connection string w formacie SQLAlchemy, np.
        "sqlite+aiosqlite:///./earni.db".

    Examples:
        >>> os.environ[DATABASE_URL_ENV_VAR] = "sqlite+aiosqlite:///:memory:"
        >>> get_secure_dsn()
        'sqlite+aiosqlite:///:memory:'
        >>> del os.environ[DATABASE_URL_ENV_VAR]
        >>> get_secure_dsn()
        'sqlite+aiosqlite:///./earni.db'
    """
    return os.environ.get(DATABASE_URL_ENV_VAR, DEFAULT_DATABASE_URL)

def _enable_sqlite_foreign_keys(
    dbapi_connection: DBAPIConnection,
    connection_record: ConnectionPoolEntry,
) -> None:
    """Włącza egzekwowanie kluczy obcych dla nowego połączenia SQLite.

    SQLite domyślnie ignoruje FOREIGN KEY oraz ondelete = "RESTRICT".
    Bez tego PRAGMA ochrona z FR-413-1 i FR-413-8 nie działa. Ustawienie
    obowiązuje tylko dla jednego połączenia, dlatego jest wykonywane przy
    każdym nowym połączeniu w puli.

    Args:
        dbapi_connection: Surowe połączenie DBAPI tworzone przez pulę.
        connection_record: Wpis puli połączeń (wymagany przez sygnaturę
            zdarzenia connect, nieużywany).
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()