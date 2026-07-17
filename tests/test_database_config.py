"""Tests for persistence database configuration."""

from __future__ import annotations

import sys
from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.persistence import DatabaseConfig as ExportedDatabaseConfig
from app.persistence.database_config import DatabaseConfig


def test_database_config_stores_normalized_paths(tmp_path: Path) -> None:
    config = DatabaseConfig(
        data_directory=str(tmp_path / "data"),
        database_filename="custom.db",
        documents_directory=str(tmp_path / "documents"),
        exports_directory=tmp_path / "exports",
        backups_directory=tmp_path / "backups",
    )

    assert config.data_directory == tmp_path / "data"
    assert config.database_filename == "custom.db"
    assert config.documents_directory == tmp_path / "documents"
    assert config.exports_directory == tmp_path / "exports"
    assert config.backups_directory == tmp_path / "backups"


def test_database_config_is_immutable(tmp_path: Path) -> None:
    config = DatabaseConfig.default(tmp_path)

    with pytest.raises(FrozenInstanceError):
        config.database_filename = "changed.db"


def test_database_config_is_exported_from_persistence_package() -> None:
    assert ExportedDatabaseConfig is DatabaseConfig


def test_default_config_uses_expected_directory_layout(tmp_path: Path) -> None:
    config = DatabaseConfig.default(tmp_path)

    assert config.data_directory == tmp_path / "data"
    assert config.database_filename == "pth_fausta.db"
    assert config.documents_directory == tmp_path / "data" / "documents"
    assert config.exports_directory == tmp_path / "data" / "exports"
    assert config.backups_directory == tmp_path / "data" / "backups"


def test_constructing_config_does_not_create_directories(tmp_path: Path) -> None:
    config = DatabaseConfig.default(tmp_path)

    assert config.data_directory.exists() is False


def test_database_path_combines_directory_and_filename(tmp_path: Path) -> None:
    config = DatabaseConfig.default(tmp_path)

    assert config.database_path == config.data_directory / config.database_filename


def test_database_url_uses_normalized_absolute_sqlite_path(tmp_path: Path) -> None:
    config = DatabaseConfig.default(tmp_path)

    assert config.database_url == (
        f"sqlite:///{config.database_path.resolve().as_posix()}"
    )


def test_database_url_preserves_directory_names_with_spaces(tmp_path: Path) -> None:
    config = DatabaseConfig.default(tmp_path / "directory with spaces")

    assert config.database_url.startswith("sqlite:///")
    assert "directory with spaces" in config.database_url
    assert "\\" not in config.database_url


def test_ensure_directories_creates_only_directories(tmp_path: Path) -> None:
    config = DatabaseConfig.default(tmp_path)

    config.ensure_directories()
    config.ensure_directories()

    assert config.data_directory.is_dir()
    assert config.documents_directory.is_dir()
    assert config.exports_directory.is_dir()
    assert config.backups_directory.is_dir()
    assert config.database_path.exists() is False


@pytest.mark.parametrize(
    ("filename", "message"),
    (
        ("", "database_filename must not be empty"),
        ("   ", "database_filename must not be empty"),
        (str(Path.cwd().anchor + "absolute.db"), "absolute path"),
        (str(Path("nested") / "database.db"), "contain directories"),
        ("database.sqlite", ".db extension"),
    ),
)
def test_invalid_database_filename_is_rejected(
    tmp_path: Path, filename: str, message: str
) -> None:
    with pytest.raises(ValueError, match=message):
        DatabaseConfig(
            data_directory=tmp_path,
            database_filename=filename,
            documents_directory=tmp_path / "documents",
            exports_directory=tmp_path / "exports",
            backups_directory=tmp_path / "backups",
        )


def test_invalid_directory_value_identifies_field(tmp_path: Path) -> None:
    with pytest.raises(TypeError, match="documents_directory"):
        DatabaseConfig(
            data_directory=tmp_path,
            database_filename="database.db",
            documents_directory=object(),
            exports_directory=tmp_path / "exports",
            backups_directory=tmp_path / "backups",
        )
