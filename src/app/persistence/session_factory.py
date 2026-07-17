"""SQLAlchemy session creation for the persistence layer."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker


class SessionFactory:
    """Create independent SQLAlchemy sessions bound to one engine."""

    def __init__(self, engine: Engine) -> None:
        """Configure session creation without defining transaction boundaries."""
        self._session_maker = sessionmaker(
            bind=engine,
            autoflush=False,
            expire_on_commit=False,
        )

    def create_session(self) -> Session:
        """Return a new SQLAlchemy session."""
        return self._session_maker()

    @contextmanager
    def session(self) -> Iterator[Session]:
        """Yield a new session and always close it without auto-committing."""
        db_session = self.create_session()
        try:
            yield db_session
        finally:
            db_session.close()
