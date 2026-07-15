import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.views import BaseView


class DummyView(BaseView):
    def show(self) -> None:
        self.shown = True

    def close(self) -> None:
        self.closed = True


def test_base_view_cannot_be_instantiated_directly() -> None:
    with pytest.raises(TypeError):
        BaseView()


def test_concrete_view_can_be_created_and_methods_called() -> None:
    view = DummyView()

    view.show()
    view.close()

    assert view.shown is True
    assert view.closed is True
