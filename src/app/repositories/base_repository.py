"""Base definitions for the repository layer."""

from __future__ import annotations


class BaseRepository:
    """Provide a common foundation for data access repositories.

    The repository layer is responsible for data access, while business logic
    belongs in the service layer. Concrete repositories may use a persistence
    technology and must receive their dependencies through their constructors.
    This foundation intentionally defines no common CRUD operations until the
    application has a confirmed repository contract.
    """
