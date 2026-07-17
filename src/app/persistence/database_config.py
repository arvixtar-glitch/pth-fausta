"""Database configuration for the persistence layer."""

from __future__ import annotations

from dataclasses import dataclass
from os import PathLike
from pathlib import Path


def _as_directory_path(value: Path | str | PathLike[str], field_name: str) -> Path:
    """Return a directory value as a Path with a field-specific error."""
    if not isinstance(value, (str, PathLike)):
        raise TypeError(f"{field_name} must be a path")
    return Path(value)


def _sqlite_url_for_path(database_path: Path) -> str:
    """Return a SQLAlchemy-compatible SQLite URL for a filesystem path."""
    normalized_path = database_path.resolve().as_posix()
    return f"sqlite:///{normalized_path}"


@dataclass(frozen=True, slots=True)
class DatabaseConfig:
    """Describe database and persistence directory locations.

    Constructing this value does not modify the filesystem. Call
    ``ensure_directories`` explicitly when the configured directories should
    be created.
    """

    data_directory: Path
    database_filename: str
    documents_directory: Path
    exports_directory: Path
    backups_directory: Path

    def __post_init__(self) -> None:
        """Normalize path fields and validate the database filename."""
        directory_fields = (
            "data_directory",
            "documents_directory",
            "exports_directory",
            "backups_directory",
        )
        for field_name in directory_fields:
            value = getattr(self, field_name)
            object.__setattr__(
                self, field_name, _as_directory_path(value, field_name)
            )

        if not isinstance(self.database_filename, str):
            raise TypeError("database_filename must be a string")
        if not self.database_filename.strip():
            raise ValueError("database_filename must not be empty")

        filename_path = Path(self.database_filename)
        if filename_path.is_absolute():
            raise ValueError("database_filename must not be an absolute path")
        if filename_path.name != self.database_filename:
            raise ValueError("database_filename must not contain directories")
        if filename_path.suffix.lower() != ".db":
            raise ValueError("database_filename must have a .db extension")

    @classmethod
    def default(cls, base_directory: Path | str | PathLike[str]) -> DatabaseConfig:
        """Create the default directory layout below an explicit base path."""
        base_path = _as_directory_path(base_directory, "base_directory")
        data_directory = base_path / "data"
        return cls(
            data_directory=data_directory,
            database_filename="pth_fausta.db",
            documents_directory=data_directory / "documents",
            exports_directory=data_directory / "exports",
            backups_directory=data_directory / "backups",
        )

    @property
    def database_path(self) -> Path:
        """Return the configured database file path."""
        return self.data_directory / self.database_filename

    @property
    def database_url(self) -> str:
        """Return a SQLAlchemy-compatible SQLite database URL."""
        return _sqlite_url_for_path(self.database_path)

    def ensure_directories(self) -> None:
        """Create the configured persistence directories if needed."""
        directories = (
            self.data_directory,
            self.documents_directory,
            self.exports_directory,
            self.backups_directory,
        )
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
