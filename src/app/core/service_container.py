"""Simple service container for registering and resolving instances by type."""

from __future__ import annotations

from typing import TypeVar

T = TypeVar("T")


class ServiceNotRegisteredError(LookupError):
    """Raised when a requested service type is not registered."""

    def __init__(self, service_type: type[object]) -> None:
        """Initialize the error with the missing service type name."""
        self.service_type = service_type
        super().__init__(f"Service is not registered: {service_type.__name__}")


class ServiceContainer:
    """Store and retrieve service instances by exact registered type."""

    def __init__(self) -> None:
        """Initialize an empty container."""
        self._services: dict[type[object], object] = {}

    @property
    def service_count(self) -> int:
        """Return the number of registered services."""
        return len(self._services)

    def _validate_service_type(self, service_type: type[object]) -> None:
        """Validate that the provided service type is a proper type object."""
        if not isinstance(service_type, type):
            raise TypeError("service_type must be a type")

    def register(self, service_type: type[T], instance: T) -> None:
        """Register a service instance for an exact service type."""
        self._validate_service_type(service_type)
        if not isinstance(instance, service_type):
            raise TypeError("instance must be an instance of service_type")
        if service_type in self._services:
            raise ValueError(f"Service is already registered: {service_type.__name__}")
        self._services[service_type] = instance

    def replace(self, service_type: type[T], instance: T) -> None:
        """Replace an existing registered service instance for an exact type."""
        self._validate_service_type(service_type)
        if not isinstance(instance, service_type):
            raise TypeError("instance must be an instance of service_type")
        if service_type not in self._services:
            raise ServiceNotRegisteredError(service_type)
        self._services[service_type] = instance

    def resolve(self, service_type: type[T]) -> T:
        """Resolve a registered service instance by exact type."""
        self._validate_service_type(service_type)
        if service_type not in self._services:
            raise ServiceNotRegisteredError(service_type)
        return self._services[service_type]  # type: ignore[return-value]

    def try_resolve(self, service_type: type[T]) -> T | None:
        """Resolve a registered service instance by exact type or return None."""
        self._validate_service_type(service_type)
        if service_type not in self._services:
            return None
        return self._services[service_type]  # type: ignore[return-value]

    def is_registered(self, service_type: type[object]) -> bool:
        """Return whether a specific service type is registered."""
        self._validate_service_type(service_type)
        return service_type in self._services

    def unregister(self, service_type: type[object]) -> bool:
        """Remove a registered service instance by exact type."""
        self._validate_service_type(service_type)
        if service_type not in self._services:
            return False
        del self._services[service_type]
        return True

    def clear(self) -> None:
        """Remove all registered services."""
        self._services.clear()
