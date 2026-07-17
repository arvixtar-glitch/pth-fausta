"""Tests for the repository layer foundation."""

from __future__ import annotations

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import app.repositories as repositories_package
from app.repositories import BaseRepository as ExportedBaseRepository
from app.repositories.base_repository import BaseRepository


def test_base_repository_can_be_instantiated() -> None:
    repository = BaseRepository()

    assert isinstance(repository, BaseRepository)


def test_base_repository_is_exported_from_repositories_package() -> None:
    assert ExportedBaseRepository is BaseRepository
    assert repositories_package.__all__ == ["BaseRepository"]


def test_base_repository_has_no_assumed_crud_operations() -> None:
    public_attributes = {
        name for name in vars(BaseRepository) if not name.startswith("_")
    }

    assert public_attributes == set()


def test_base_repository_has_no_external_layer_dependencies() -> None:
    source = (
        ROOT / "src" / "app" / "repositories" / "base_repository.py"
    ).read_text(encoding="utf-8")
    tree = ast.parse(source)
    imported_modules = {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    imported_modules.update(
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module is not None
    )
    forbidden_dependencies = (
        "app.controllers",
        "app.services",
        "app.views",
        "PySide6",
        "sqlalchemy",
        "sqlite3",
    )

    assert not any(
        module == dependency or module.startswith(f"{dependency}.")
        for module in imported_modules
        for dependency in forbidden_dependencies
    )
