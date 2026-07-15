import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.core import ServiceContainer, ServiceNotRegisteredError  # noqa: E402


class BaseService:
    pass


class ConcreteService(BaseService):
    pass


class AnotherConcreteService(BaseService):
    pass


def test_new_container_is_empty() -> None:
    container = ServiceContainer()

    assert container.service_count == 0


def test_initial_service_count_is_zero() -> None:
    container = ServiceContainer()

    assert container.service_count == 0


def test_service_can_be_registered_by_type() -> None:
    container = ServiceContainer()
    service = BaseService()

    container.register(BaseService, service)

    assert container.is_registered(BaseService) is True


def test_service_count_increases_after_registration() -> None:
    container = ServiceContainer()

    container.register(BaseService, BaseService())

    assert container.service_count == 1


def test_resolve_returns_the_same_instance() -> None:
    container = ServiceContainer()
    service = BaseService()

    container.register(BaseService, service)

    assert container.resolve(BaseService) is service


def test_try_resolve_returns_registered_instance() -> None:
    container = ServiceContainer()
    service = BaseService()

    container.register(BaseService, service)

    assert container.try_resolve(BaseService) is service


def test_try_resolve_returns_none_for_unknown_type() -> None:
    container = ServiceContainer()

    assert container.try_resolve(BaseService) is None


def test_resolve_unknown_type_raises_service_not_registered_error() -> None:
    container = ServiceContainer()

    with pytest.raises(ServiceNotRegisteredError) as exc_info:
        container.resolve(BaseService)

    assert "BaseService" in str(exc_info.value)


def test_duplicate_registration_raises_value_error() -> None:
    container = ServiceContainer()
    container.register(BaseService, BaseService())

    with pytest.raises(ValueError):
        container.register(BaseService, BaseService())


def test_duplicate_registration_does_not_replace_previous_instance() -> None:
    container = ServiceContainer()
    first = BaseService()
    second = BaseService()
    container.register(BaseService, first)

    with pytest.raises(ValueError):
        container.register(BaseService, second)

    assert container.resolve(BaseService) is first


def test_registration_with_incorrect_instance_type_raises_type_error() -> None:
    container = ServiceContainer()

    with pytest.raises(TypeError):
        container.register(BaseService, object())


def test_registration_with_non_type_service_type_raises_type_error() -> None:
    container = ServiceContainer()

    with pytest.raises(TypeError):
        container.register("not-a-type", object())  # type: ignore[arg-type]


def test_service_can_be_registered_by_base_class() -> None:
    container = ServiceContainer()
    service = ConcreteService()

    container.register(BaseService, service)

    assert container.resolve(BaseService) is service


def test_registration_by_base_class_does_not_resolve_concrete_class_automatically() -> None:
    container = ServiceContainer()
    service = ConcreteService()

    container.register(BaseService, service)

    assert container.is_registered(ConcreteService) is False


def test_registration_by_concrete_class_does_not_resolve_base_class_automatically() -> None:
    container = ServiceContainer()
    service = ConcreteService()

    container.register(ConcreteService, service)

    assert container.is_registered(BaseService) is False


def test_same_instance_can_be_registered_for_two_compatible_types() -> None:
    container = ServiceContainer()
    service = ConcreteService()

    container.register(BaseService, service)
    container.register(ConcreteService, service)

    assert container.resolve(BaseService) is service
    assert container.resolve(ConcreteService) is service


def test_replace_updates_existing_instance() -> None:
    container = ServiceContainer()
    first = BaseService()
    second = BaseService()
    container.register(BaseService, first)

    container.replace(BaseService, second)

    assert container.resolve(BaseService) is second


def test_replace_preserves_service_count() -> None:
    container = ServiceContainer()
    container.register(BaseService, BaseService())

    container.replace(BaseService, BaseService())

    assert container.service_count == 1


def test_replace_unknown_type_raises_service_not_registered_error() -> None:
    container = ServiceContainer()

    with pytest.raises(ServiceNotRegisteredError):
        container.replace(BaseService, BaseService())


def test_replace_with_incorrect_instance_type_raises_type_error() -> None:
    container = ServiceContainer()
    container.register(BaseService, BaseService())

    with pytest.raises(TypeError):
        container.replace(BaseService, object())  # type: ignore[arg-type]


def test_unregister_removes_registration_and_returns_true() -> None:
    container = ServiceContainer()
    container.register(BaseService, BaseService())

    assert container.unregister(BaseService) is True
    assert container.is_registered(BaseService) is False


def test_unregister_unknown_type_returns_false() -> None:
    container = ServiceContainer()

    assert container.unregister(BaseService) is False


def test_resolve_fails_after_unregister() -> None:
    container = ServiceContainer()
    container.register(BaseService, BaseService())

    container.unregister(BaseService)

    with pytest.raises(ServiceNotRegisteredError):
        container.resolve(BaseService)


def test_clear_removes_all_registrations() -> None:
    container = ServiceContainer()
    container.register(BaseService, BaseService())
    container.register(ConcreteService, ConcreteService())

    container.clear()

    assert container.service_count == 0
    assert container.is_registered(BaseService) is False
    assert container.is_registered(ConcreteService) is False


def test_clear_twice_is_safe() -> None:
    container = ServiceContainer()
    container.clear()
    container.clear()

    assert container.service_count == 0


def test_service_count_property_is_read_only() -> None:
    container = ServiceContainer()

    with pytest.raises(AttributeError):
        container.service_count = 5


def test_service_container_can_be_imported_from_app_core() -> None:
    from app.core import ServiceContainer as ImportedContainer

    assert ImportedContainer is ServiceContainer


def test_service_not_registered_error_can_be_imported_from_app_core() -> None:
    from app.core import ServiceNotRegisteredError as ImportedError

    assert ImportedError is ServiceNotRegisteredError
