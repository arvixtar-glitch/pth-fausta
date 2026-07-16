"""Base definitions for the service layer."""

from __future__ import annotations


class BaseService:
    """Provide a common foundation for application services.

    The service layer contains business logic between controllers and the
    repository layer. Concrete services must receive their dependencies
    through their constructors.
    """
