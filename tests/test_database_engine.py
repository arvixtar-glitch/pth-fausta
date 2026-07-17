"""Tests for the SQLAlchemy database engine infrastructure."""

from __future__ import annotations

import sys
from pathlib import Path

from sqlalchemy import Engine, text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.persistence import DatabaseConfig, DatabaseEngine


def test_database_engine_exposes_one_engine_with_configured_url(
    tmp_path: Path,
) -> None:
    config = DatabaseConfig.default(tmp_path)
    database_engine = DatabaseEngine(config)
    try:
        assert isinstance(database_engine.engine, Engine)
        assert database_engine.engine is database_engine.engine
        assert str(database_engine.engine.url) == config.database_url
    finally:
        database_engine.dispose()


def test_engine_creation_does_not_create_database_file(tmp_path: Path) -> None:
    config = DatabaseConfig.default(tmp_path)
    config.ensure_directories()
    database_engine = DatabaseEngine(config)
    try:
        assert config.database_path.exists() is False
    finally:
        database_engine.dispose()


def test_connect_creates_database_file_and_executes_sql(tmp_path: Path) -> None:
    config = DatabaseConfig.default(tmp_path)
    config.ensure_directories()
    database_engine = DatabaseEngine(config)
    try:
        with database_engine.engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar_one()

        assert result == 1
        assert config.database_path.is_file()
    finally:
        database_engine.dispose()


def test_foreign_keys_are_enabled_for_every_connection(tmp_path: Path) -> None:
    config = DatabaseConfig.default(tmp_path)
    config.ensure_directories()
    database_engine = DatabaseEngine(config)
    try:
        with database_engine.engine.connect() as connection:
            first_result = connection.execute(
                text("PRAGMA foreign_keys")
            ).scalar_one()

        database_engine.dispose()

        with database_engine.engine.connect() as connection:
            second_result = connection.execute(
                text("PRAGMA foreign_keys")
            ).scalar_one()

        assert first_result == 1
        assert second_result == 1
    finally:
        database_engine.dispose()


def test_dispose_can_be_called_more_than_once(tmp_path: Path) -> None:
    config = DatabaseConfig.default(tmp_path)
    database_engine = DatabaseEngine(config)

    database_engine.dispose()
    database_engine.dispose()


def test_engine_supports_database_path_with_spaces(tmp_path: Path) -> None:
    config = DatabaseConfig.default(tmp_path / "directory with spaces")
    config.ensure_directories()
    database_engine = DatabaseEngine(config)
    try:
        with database_engine.engine.connect() as connection:
            assert connection.execute(text("SELECT 1")).scalar_one() == 1

        assert config.database_path.is_file()
    finally:
        database_engine.dispose()
