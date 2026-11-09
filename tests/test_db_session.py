import asyncio
from collections.abc import AsyncGenerator
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

import db.session
from db.session import (
    DB_PATH_ENV_VAR,
    DEFAULT_DB_PATH,
    async_session_maker,
    create_db_engine,
    engine,
    get_db_path,
    get_db_session,
)

MEMORY_DB = ":memory:"


@pytest.fixture
async def memory_engine() -> AsyncGenerator[AsyncEngine, None]:
    """Silnik na pustej bazie w pamięci, zamykany po teście"""
    db_engine = create_db_engine(MEMORY_DB)
    yield db_engine
    await db_engine.dispose()


@pytest.fixture
async def file_engine(tmp_path: Path) -> AsyncGenerator[AsyncEngine, None]:
    """Silnik na pliku earni.db w katalogu tymczasowym testu, zamykany po teście"""
    db_engine = create_db_engine(str(tmp_path / "earni.db"))
    yield db_engine
    await db_engine.dispose()


class TestGetDbPath:
    """Testy wczytywania ścieżki do bazy ze zmiennej środowiskowej"""

    def test_returns_env_value_when_set(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Sprawdzenie, czy ścieżka jest czytana ze zmiennej środowiskowej"""
        monkeypatch.setenv(DB_PATH_ENV_VAR, "/data/earni.db")
        assert get_db_path() == "/data/earni.db"

    def test_returns_default_when_unset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Sprawdzenie, czy bez zmiennej środowiskowej używana jest ścieżka domyślna"""
        monkeypatch.delenv(DB_PATH_ENV_VAR, raising=False)
        assert get_db_path() == DEFAULT_DB_PATH

    def test_returns_default_when_empty(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Sprawdzenie, czy pusta zmienna nie zamienia bazy w ulotną bazę w pamięci"""
        monkeypatch.setenv(DB_PATH_ENV_VAR, "")
        assert get_db_path() == DEFAULT_DB_PATH


class TestCreateDbEngine:
    """Testy konfiguracji silnika (FR-413-5)"""

    def test_returns_async_engine(self) -> None:
        """Sprawdzenie, czy zwracany jest silnik asynchroniczny"""
        assert isinstance(create_db_engine(MEMORY_DB), AsyncEngine)

    def test_uses_aiosqlite_driver(self) -> None:
        """Sprawdzenie, czy silnik korzysta z asynchronicznego sterownika aiosqlite"""
        assert create_db_engine(MEMORY_DB).url.drivername == "sqlite+aiosqlite"

    def test_relative_path_is_preserved(self) -> None:
        """Sprawdzenie, czy ścieżka względna trafia do URL bez zmian"""
        assert create_db_engine("earni.db").url.database == "earni.db"

    def test_absolute_path_is_preserved(self, tmp_path: Path) -> None:
        """Sprawdzenie, czy ścieżka bezwzględna trafia do URL bez zmian"""
        db_file = str(tmp_path / "earni.db")
        assert create_db_engine(db_file).url.database == db_file

    def test_special_characters_in_path_are_preserved(self) -> None:
        """Sprawdzenie, czy znak '?' w ścieżce nie jest traktowany jako parametr URL"""
        assert create_db_engine("dane?v2.db").url.database == "dane?v2.db"

    async def test_file_is_created_on_first_query(
        self, file_engine: AsyncEngine, tmp_path: Path
    ) -> None:
        """Sprawdzenie, czy plik bazy powstaje dopiero przy pierwszym zapytaniu"""
        db_file = tmp_path / "earni.db"
        assert not db_file.exists()

        async with file_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        assert db_file.exists()

    async def test_foreign_keys_pragma_enabled(self, memory_engine: AsyncEngine) -> None:
        """Sprawdzenie, czy połączenie SQLite ma włączone klucze obce"""
        async with memory_engine.connect() as conn:
            result = await conn.execute(text("PRAGMA foreign_keys"))
            assert result.scalar_one() == 1

    async def test_rejects_orphan_record(self, memory_engine: AsyncEngine) -> None:
        """Sprawdzenie, czy baza blokuje rekord wskazujący na nieistniejącego rodzica"""
        async with memory_engine.begin() as conn:
            await conn.execute(text("CREATE TABLE users (user_id VARCHAR(36) PRIMARY KEY)"))
            await conn.execute(text(
                "CREATE TABLE tasks ("
                "task_id VARCHAR(36) PRIMARY KEY, "
                "user_id VARCHAR(36) NOT NULL REFERENCES users(user_id))"
            ))

        with pytest.raises(IntegrityError, match="FOREIGN KEY"):
            async with memory_engine.begin() as conn:
                await conn.execute(text("INSERT INTO tasks VALUES ('task-1', 'missing-user')"))

    def test_secret_key_not_implemented(self) -> None:
        """Sprawdzenie, czy wariant szyfrowany jest jawnie zablokowany do czasu implementacji"""
        with pytest.raises(NotImplementedError, match="FR-413-5"):
            create_db_engine(MEMORY_DB, secret_key="tajne")


class TestSessionFactory:
    """Testy fabryki sesji i zależności FastAPI (FR-415-4)"""

    def test_session_maker_does_not_expire_on_commit(self) -> None:
        """Sprawdzenie, czy obiekty nie wygasają po commit (brak lazy-load w async)"""
        assert async_session_maker.kw["expire_on_commit"] is False

    def test_session_maker_bound_to_app_engine(self) -> None:
        """Sprawdzenie, czy fabryka korzysta z jednego silnika aplikacji"""
        assert async_session_maker.kw["bind"] is engine

    async def test_get_db_session_yields_async_session(self) -> None:
        """Sprawdzenie, czy zależność zwraca AsyncSession i kończy się bez błędu"""
        generator = get_db_session()
        session = await anext(generator)
        await generator.aclose()

        assert isinstance(session, AsyncSession)

    async def test_get_db_session_closes_session_on_endpoint_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Sprawdzenie, czy sesja jest zamykana, gdy endpoint rzuci wyjątek"""
        closed: list[bool] = []

        async def _spy_close(self: AsyncSession) -> None:
            closed.append(True)

        monkeypatch.setattr(AsyncSession, "close", _spy_close)

        generator = get_db_session()
        await anext(generator)
        with pytest.raises(ValueError):
            await generator.athrow(ValueError("błąd w endpoincie"))

        assert closed == [True]

    async def test_get_db_session_returns_connection_when_request_cancelled(
        self, monkeypatch: pytest.MonkeyPatch, file_engine: AsyncEngine
    ) -> None:
        """Sprawdzenie, czy anulowanie żądania w trakcie close() nie gubi połączenia z puli"""
        monkeypatch.setattr(
            db.session, "async_session_maker",
            async_sessionmaker(bind=file_engine, expire_on_commit=False),
        )
        original_close = AsyncSession.close

        async def _slow_close(self: AsyncSession) -> None:
            await asyncio.sleep(0.05)
            await original_close(self)

        monkeypatch.setattr(AsyncSession, "close", _slow_close)

        async def _request() -> None:
            generator = get_db_session()
            session = await anext(generator)
            await session.execute(text("SELECT 1"))
            await generator.aclose()

        task = asyncio.create_task(_request())
        await asyncio.sleep(0.02)
        task.cancel()
        with pytest.raises(asyncio.CancelledError):
            await task
        await asyncio.sleep(0.1)

        assert file_engine.pool.checkedout() == 0  # type: ignore[attr-defined]