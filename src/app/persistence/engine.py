"""SQLAlchemy engine lifecycle for the persistence layer."""

from __future__ import annotations

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.pool import ConnectionPoolEntry

from app.persistence.database_config import DatabaseConfig


def _enable_sqlite_foreign_keys(
    dbapi_connection: DBAPIConnection,
    _connection_record: ConnectionPoolEntry,
) -> None:
    """Enable SQLite foreign key enforcement for a new DBAPI connection."""
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("PRAGMA foreign_keys = ON")
    finally:
        cursor.close()


class DatabaseEngine:
    """Create and dispose one SQLAlchemy engine from database configuration."""

    def __init__(self, config: DatabaseConfig) -> None:
        """Create an engine without opening a database connection."""
        self._engine = create_engine(
            config.database_url,
            connect_args={"check_same_thread": False},
        )
        event.listen(self._engine, "connect", _enable_sqlite_foreign_keys)

    @property
    def engine(self) -> Engine:
        """Return the managed SQLAlchemy engine."""
        return self._engine

    def dispose(self) -> None:
        """Release connections currently held by the engine pool."""
        self._engine.dispose()
