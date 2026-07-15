import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from app.core import EventBus


def test_new_event_bus_has_no_subscriptions() -> None:
    event_bus = EventBus()

    assert event_bus.subscription_count == 0


def test_handler_can_be_registered() -> None:
    event_bus = EventBus()
    calls: list[str] = []

    def handler() -> None:
        calls.append("called")

    event_bus.subscribe("event", handler)

    event_bus.publish("event")

    assert calls == ["called"]


def test_subscription_count_is_calculated_correctly() -> None:
    event_bus = EventBus()

    event_bus.subscribe("event_a", lambda: None)
    event_bus.subscribe("event_a", lambda: None)
    event_bus.subscribe("event_b", lambda: None)

    assert event_bus.subscription_count == 3


def test_publish_calls_handler() -> None:
    event_bus = EventBus()
    calls: list[str] = []

    def handler() -> None:
        calls.append("called")

    event_bus.subscribe("event", handler)
    event_bus.publish("event")

    assert calls == ["called"]


def test_payload_is_passed_as_keyword_arguments() -> None:
    event_bus = EventBus()
    received: list[dict[str, object]] = []

    def handler(**payload: object) -> None:
        received.append(payload)

    event_bus.subscribe("event", handler)
    event_bus.publish("event", foo="bar", count=2)

    assert received == [{"foo": "bar", "count": 2}]


def test_multiple_handlers_run_in_registration_order() -> None:
    event_bus = EventBus()
    order: list[str] = []

    def first() -> None:
        order.append("first")

    def second() -> None:
        order.append("second")

    event_bus.subscribe("event", first)
    event_bus.subscribe("event", second)
    event_bus.publish("event")

    assert order == ["first", "second"]


def test_same_handler_is_not_registered_twice_for_same_event() -> None:
    event_bus = EventBus()
    calls: list[int] = []

    def handler() -> None:
        calls.append(1)

    event_bus.subscribe("event", handler)
    event_bus.subscribe("event", handler)
    event_bus.publish("event")

    assert calls == [1]


def test_same_handler_can_be_registered_for_different_events() -> None:
    event_bus = EventBus()
    calls: list[str] = []

    def handler() -> None:
        calls.append("called")

    event_bus.subscribe("event_a", handler)
    event_bus.subscribe("event_b", handler)
    event_bus.publish("event_a")
    event_bus.publish("event_b")

    assert calls == ["called", "called"]


def test_unsubscribe_removes_existing_handler_and_returns_true() -> None:
    event_bus = EventBus()
    calls: list[str] = []

    def handler() -> None:
        calls.append("called")

    event_bus.subscribe("event", handler)

    assert event_bus.unsubscribe("event", handler) is True
    event_bus.publish("event")

    assert calls == []


def test_unsubscribe_returns_false_for_missing_handler() -> None:
    event_bus = EventBus()

    def handler() -> None:
        return None

    assert event_bus.unsubscribe("event", handler) is False


def test_removing_last_handler_clears_subscription_entry() -> None:
    event_bus = EventBus()

    def handler() -> None:
        return None

    event_bus.subscribe("event", handler)
    event_bus.unsubscribe("event", handler)

    assert event_bus.subscription_count == 0
    assert "event" not in event_bus._subscriptions


def test_clear_specific_event_removes_only_that_event_subscriptions() -> None:
    event_bus = EventBus()

    event_bus.subscribe("event_a", lambda: None)
    event_bus.subscribe("event_b", lambda: None)

    event_bus.clear("event_a")

    assert event_bus.subscription_count == 1
    assert "event_a" not in event_bus._subscriptions
    assert "event_b" in event_bus._subscriptions


def test_clear_removes_all_subscriptions() -> None:
    event_bus = EventBus()

    event_bus.subscribe("event_a", lambda: None)
    event_bus.subscribe("event_b", lambda: None)

    event_bus.clear()

    assert event_bus.subscription_count == 0
    assert event_bus._subscriptions == {}


def test_publish_to_unknown_event_does_not_raise() -> None:
    event_bus = EventBus()

    event_bus.publish("missing")


def test_empty_event_name_raises_value_error() -> None:
    event_bus = EventBus()

    with pytest.raises(ValueError):
        event_bus.subscribe("", lambda: None)


def test_whitespace_event_name_raises_value_error() -> None:
    event_bus = EventBus()

    with pytest.raises(ValueError):
        event_bus.subscribe("   ", lambda: None)


def test_non_callable_handler_raises_type_error() -> None:
    event_bus = EventBus()

    with pytest.raises(TypeError):
        event_bus.subscribe("event", "not callable")


def test_handler_exception_is_not_swallowed() -> None:
    event_bus = EventBus()

    def failing_handler() -> None:
        raise RuntimeError("boom")

    event_bus.subscribe("event", failing_handler)

    with pytest.raises(RuntimeError, match="boom"):
        event_bus.publish("event")


def test_publish_stops_after_handler_exception() -> None:
    event_bus = EventBus()
    calls: list[str] = []

    def failing_handler() -> None:
        calls.append("first")
        raise RuntimeError("boom")

    def next_handler() -> None:
        calls.append("second")

    event_bus.subscribe("event", failing_handler)
    event_bus.subscribe("event", next_handler)

    with pytest.raises(RuntimeError, match="boom"):
        event_bus.publish("event")

    assert calls == ["first"]


def test_handler_can_unsubscribe_during_publish_without_breaking_iteration() -> None:
    event_bus = EventBus()
    order: list[str] = []

    def first() -> None:
        order.append("first")
        event_bus.unsubscribe("event", second)

    def second() -> None:
        order.append("second")

    event_bus.subscribe("event", first)
    event_bus.subscribe("event", second)

    event_bus.publish("event")

    assert order == ["first"]


def test_handler_can_subscribe_new_handler_during_publish_but_new_handler_is_not_called() -> None:
    event_bus = EventBus()
    calls: list[str] = []

    def first() -> None:
        calls.append("first")
        event_bus.subscribe("event", second)

    def second() -> None:
        calls.append("second")

    event_bus.subscribe("event", first)

    event_bus.publish("event")

    assert calls == ["first"]


def test_subscription_count_property_is_read_only() -> None:
    event_bus = EventBus()

    with pytest.raises(AttributeError):
        event_bus.subscription_count = 5
