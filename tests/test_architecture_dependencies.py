"""Architecture tests for application layer dependency boundaries."""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = ROOT / "src" / "app"
QT_MODULES = ("PySide", "PyQt", "qtpy")

LAYER_RULES = (
    (
        "repositories",
        ("app.controllers", "app.services", "app.views", *QT_MODULES),
    ),
    ("services", ("app.controllers", "app.views", *QT_MODULES)),
    ("controllers", ("app.repositories",)),
    ("models", ("app.views", *QT_MODULES)),
    ("views", ("app.repositories",)),
)


def _module_name(path: Path) -> str:
    relative_path = path.relative_to(APP_ROOT.parent).with_suffix("")
    return ".".join(relative_path.parts)


def _imports_from(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    imports: set[str] = set()
    package = _module_name(path).rpartition(".")[0]

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                module = importlib.util.resolve_name(
                    f"{'.' * node.level}{module}", package
                )
            if module:
                imports.add(module)

    return imports


def _matches(imported_module: str, forbidden_module: str) -> bool:
    if forbidden_module in QT_MODULES:
        return imported_module == forbidden_module or imported_module.startswith(
            forbidden_module
        )
    return imported_module == forbidden_module or imported_module.startswith(
        f"{forbidden_module}."
    )


@pytest.mark.parametrize(("layer", "forbidden_modules"), LAYER_RULES)
def test_layer_has_no_forbidden_dependencies(
    layer: str, forbidden_modules: tuple[str, ...]
) -> None:
    violations: list[str] = []

    for path in sorted((APP_ROOT / layer).rglob("*.py")):
        for imported_module in sorted(_imports_from(path)):
            for forbidden_module in forbidden_modules:
                if _matches(imported_module, forbidden_module):
                    relative_path = path.relative_to(ROOT)
                    violations.append(f"{relative_path}: {imported_module}")

    assert violations == [], "Forbidden layer dependencies:\n" + "\n".join(
        violations
    )
