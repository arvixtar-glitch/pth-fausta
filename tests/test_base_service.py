"""Tests for the service layer foundation."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.services import BaseService as ExportedBaseService
from app.services.base_service import BaseService


def test_base_service_can_be_instantiated() -> None:
    service = BaseService()

    assert isinstance(service, BaseService)


def test_base_service_is_exported_from_services_package() -> None:
    assert ExportedBaseService is BaseService


def test_base_service_has_no_domain_operations() -> None:
    public_attributes = {
        name for name in vars(BaseService) if not name.startswith("_")
    }

    assert public_attributes == set()


def test_base_service_has_no_external_layer_dependencies() -> None:
    source = (ROOT / "src" / "app" / "services" / "base_service.py").read_text(
        encoding="utf-8"
    )

    assert "app.views" not in source
    assert "PySide6" not in source
    assert "sqlalchemy" not in source.lower()
    assert "app.repositories" not in source
