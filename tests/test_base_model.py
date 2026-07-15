import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.models import BaseModel


def test_new_model_is_not_dirty() -> None:
    model = BaseModel()

    assert model.is_dirty is False


def test_mark_dirty_sets_state_to_true() -> None:
    model = BaseModel()

    model.mark_dirty()

    assert model.is_dirty is True


def test_mark_clean_resets_state_to_false() -> None:
    model = BaseModel()
    model.mark_dirty()

    model.mark_clean()

    assert model.is_dirty is False


def test_is_dirty_property_is_read_only() -> None:
    model = BaseModel()

    with pytest.raises(AttributeError):
        model.is_dirty = True
