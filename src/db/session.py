import os
from collections.abc import AsyncGenerator

from sqlalchemy import event
from sqlalchemy.engine import URL
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import ConnectionPoolEntry

DB_PATH_ENV_VAR = "EARNI_DB_PATH"
DEFAULT_DB_PATH = "earni.db"


def get_db_path() -> str:
    """Zwraca ścieżkę do pliku bazy SQLite ze zmiennej środowiskowej.

    Wartość jest czytana z EARNI_DB_PATH. Jeżeli zmienna nie jest
    ustawiona albo jest pusta, zwracana jest ścieżka domyślna earni.db
    (względna wobec katalogu, z którego uruchomiono aplikację). Pusta
    wartość nie może przejść dalej - pusta ścieżka oznacza dla SQLite bazę
    w pamięci, która znika po restarcie aplikacji.

    Returns:
        Ścieżka do pliku bazy, np. "earni.db" lub ":memory:".

    Examples:
        >>> os.environ[DB_PATH_ENV_VAR] = "/data/earni.db"
        >>> get_db_path()
        '/data/earni.db'
        >>> os.environ[DB_PATH_ENV_VAR] = ""
        >>> get_db_path()
        'earni.db'
        >>> del os.environ[DB_PATH_ENV_VAR]
        >>> get_db_path()
        'earni.db'
    """
    return os.environ.get(DB_PATH_ENV_VAR) or DEFAULT_DB_PATH


def _enable_sqlite_foreign_keys(
    dbapi_connection: DBAPIConnection,
    connection_record: ConnectionPoolEntry, #potrzebny dodatkowy argument, bo SQLAlchemy przy connect zawsze zwraca 2 argumenty
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


def create_db_engine(db_path: str, secret_key: str | None = None) -> AsyncEngine:
    """Tworzy asynchroniczny silnik bazy SQLite (FR-413-5).

    Dla każdego nowego połączenia włącza egzekwowanie kluczy obcych.
    URL budowany jest przez URL.create, więc znaki specjalne w ścieżce
    (np. ?) nie są interpretowane jako parametry połączenia.

    Args:
        db_path: Ścieżka do pliku bazy (względna lub bezwzględna) albo
            ":memory:" dla bazy w pamięci (testy).
        secret_key: Klucz szyfrowania At Rest (FR-413-5, krok 2). Wariant
            szyfrowany nie jest jeszcze zaimplementowany - dziś musi być
            None.

    Returns:
        Skonfigurowany obiekt AsyncEngine.

    Raises:
        NotImplementedError: Gdy podano secret_key - szyfrowanie nie jest
            jeszcze zaimplementowane (FR-413-5 w In clarification).

    Examples:
        >>> create_db_engine(":memory:").url.database
        ':memory:'
    """
    if secret_key is not None:
        raise NotImplementedError(
            "Szyfrowanie bazy (FR-413-5, krok 2; 4.0.3) nie jest jeszcze "
            "zaimplementowane - wymaganie ma status In clarification."
        )

    db_engine = create_async_engine(URL.create("sqlite+aiosqlite", database=db_path))
    event.listen(db_engine.sync_engine, "connect", _enable_sqlite_foreign_keys)
    return db_engine


engine: AsyncEngine = create_db_engine(get_db_path())

async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dostarcza sesję ORM na czas jednego żądania HTTP (FR-415-4).

    Yields:
        Nowa instancja AsyncSession powiązana z silnikiem aplikacji.
    """
    async with async_session_maker() as session:
        yield session