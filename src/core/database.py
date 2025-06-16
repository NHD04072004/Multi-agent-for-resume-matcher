from functools import lru_cache
from typing import AsyncGenerator, Generator

from pydantic_core.core_schema import InvalidSchema
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, AsyncSession, create_async_engine

from src.models import Base
from .config import settings


class _DatabaseSettings:
    """Pulled from environment once at import-time."""

    SYNC_DATABASE_URL: str = settings.SYNC_DATABASE_URL
    ASYNC_DATABASE_URL: str = settings.ASYNC_DATABASE_URL
    DB_ECHO: bool = settings.DB_ECHO

    DB_CONNECT_ARGS = {}


settings = _DatabaseSettings()


def _configure_database(engine: Engine) -> None:
    if engine.dialect.name != "postgresql":
        return

    @event.listens_for(engine, "connect", insert=True)
    def set_search_path(dbapi_conn, _):
        try:
            existing_autocommit = dbapi_conn.autocommit
            dbapi_conn.autocommit = True
            cursor = dbapi_conn.cursor()
            cursor.execute("SET search_path TO public")
            cursor.execute("SET client_encoding = 'UTF8'")
            cursor.close()
            dbapi_conn.autocommit = existing_autocommit
        except InvalidSchema:
            pass


@lru_cache(maxsize=1)
def _make_sync_engine() -> Engine:
    """Create (or return) the global synchronous Engine."""
    engine = create_engine(
        settings.SYNC_DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_pre_ping=True,
        connect_args=settings.DB_CONNECT_ARGS,
        future=True,
    )
    _configure_database(engine)
    return engine


@lru_cache(maxsize=1)
def _make_async_engine() -> AsyncEngine:
    """Create (or return) the global asynchronous Engine."""
    engine = create_async_engine(
        settings.ASYNC_DATABASE_URL,
        echo=settings.DB_ECHO,
        pool_pre_ping=True,
        connect_args=settings.DB_CONNECT_ARGS,
        future=True,
    )
    _configure_database(engine.sync_engine)
    return engine


sync_engine: Engine = _make_sync_engine()
async_engine: AsyncEngine = _make_async_engine()

SessionLocal: sessionmaker[Session] = sessionmaker(
    bind=sync_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
)


def get_sync_db_session() -> Generator[Session, None, None]:
    """
    Yield a *transactional* synchronous ``Session``.

    Commits if no exception was raised, otherwise rolls back. Always closes.
    Useful for CLI scripts or rare sync paths.
    """
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_models(Base: Base) -> None:
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
