"""View package exports loaded lazily to keep shared widgets independent."""

from importlib import import_module
from typing import Any

from app.views.base_view import BaseView

__all__ = [
    "BaseView",
    "CompanyView",
    "CustomerDialog",
    "CustomerListView",
    "HomeView",
    "MainView",
    "ProductDialog",
    "ProductListView",
]

_EXPORTS = {
    "CompanyView": ("app.views.company_view", "CompanyView"),
    "CustomerDialog": ("app.views.customer_dialog", "CustomerDialog"),
    "CustomerListView": ("app.views.customer_list_view", "CustomerListView"),
    "HomeView": ("app.views.home_view", "HomeView"),
    "MainView": ("app.views.main_view", "MainView"),
    "ProductDialog": ("app.views.product_dialog", "ProductDialog"),
    "ProductListView": ("app.views.product_list_view", "ProductListView"),
}


def __getattr__(name: str) -> Any:
    """Load concrete Qt views only when the package export is requested."""
    if name not in _EXPORTS:
        raise AttributeError(name)
    module_name, attribute = _EXPORTS[name]
    value = getattr(import_module(module_name), attribute)
    globals()[name] = value
    return value
