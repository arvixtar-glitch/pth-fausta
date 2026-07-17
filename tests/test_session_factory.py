"""Tests for SQLAlchemy session creation infrastructure."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.persistence import DatabaseConfig, DatabaseEngine, SessionFactory


def test_session_factory_creates_distinct_configured_sessions() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    factory = SessionFactory(engine)
    session_a = factory.create_session()
    session_b = factory.create_session()
    try:
        assert session_a is not session_b
        assert session_a.bind is engine
        assert session_b.bind is engine
        assert session_a.autoflush is False
        assert session_a.expire_on_commit is False
    finally:
        session_a.close()
        session_b.close()
        engine.dispose()


def test_session_executes_sql() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    factory = SessionFactory(engine)
    session = factory.create_session()
    try:
        assert session.execute(text("SELECT 1")).scalar_one() == 1
    finally:
        session.close()
        engine.dispose()


def test_session_context_closes_session_without_committing() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    factory = SessionFactory(engine)
    session = Mock(spec=Session)
    try:
        with patch.object(factory, "create_session", return_value=session):
            with factory.session() as yielded_session:
                assert yielded_session is session

        session.close.assert_called_once_with()
        session.commit.assert_not_called()
        session.rollback.assert_not_called()
    finally:
        engine.dispose()


def test_session_context_propagates_exception_and_closes_session() -> None:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    factory = SessionFactory(engine)
    session = Mock(spec=Session)
    try:
        with patch.object(factory, "create_session", return_value=session):
            with pytest.raises(RuntimeError, match="failure"):
                with factory.session():
                    raise RuntimeError("failure")

        session.close.assert_called_once_with()
    finally:
        engine.dispose()


def test_config_engine_session_integration(tmp_path: Path) -> None:
    config = DatabaseConfig.default(tmp_path)
    config.ensure_directories()
    database_engine = DatabaseEngine(config)
    session_factory = SessionFactory(database_engine.engine)
    session = session_factory.create_session()
    try:
        assert session.execute(text("SELECT 1")).scalar_one() == 1
        assert config.database_path.is_file()
    finally:
        session.close()
        database_engine.dispose()
