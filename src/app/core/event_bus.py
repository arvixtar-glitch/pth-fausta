"""Simple synchronous event bus for loosely coupled communication."""

from __future__ import annotations

from collections.abc import Callable

EventName = str
EventHandler = Callable[..., None]


class EventBus:
    """Register handlers and publish events synchronously."""

    def __init__(self) -> None:
        """Initialize an empty subscription registry."""
        self._subscriptions: dict[EventName, list[EventHandler]] = {}

    @property
    def subscription_count(self) -> int:
        """Return the total number of registered handlers."""
        return sum(len(handlers) for handlers in self._subscriptions.values())

    def _validate_event_name(self, event_name: EventName) -> None:
        """Validate that an event name is a non-empty string."""
        if not isinstance(event_name, str):
            raise TypeError("event_name must be a string")
        if not event_name.strip():
            raise ValueError("event_name must not be empty")

    def subscribe(self, event_name: EventName, handler: EventHandler) -> None:
        """Register a handler for an event if it is not already subscribed."""
        self._validate_event_name(event_name)
        if not callable(handler):
            raise TypeError("handler must be callable")

        handlers = self._subscriptions.setdefault(event_name, [])
        if handler not in handlers:
            handlers.append(handler)

    def unsubscribe(self, event_name: EventName, handler: EventHandler) -> bool:
        """Remove a handler from an event and return whether it was removed."""
        self._validate_event_name(event_name)
        if not callable(handler):
            raise TypeError("handler must be callable")

        handlers = self._subscriptions.get(event_name)
        if handlers is None:
            return False

        try:
            handlers.remove(handler)
        except ValueError:
            return False

        if not handlers:
            del self._subscriptions[event_name]
        return True

    def publish(self, event_name: EventName, **payload: object) -> None:
        """Synchronously call all handlers registered for an event."""
        self._validate_event_name(event_name)

        handlers = self._subscriptions.get(event_name)
        if not handlers:
            return

        snapshot = list(handlers)
        for handler in snapshot:
            live_handlers = self._subscriptions.get(event_name)
            if not live_handlers or handler not in live_handlers:
                continue
            handler(**payload)

    def clear(self, event_name: EventName | None = None) -> None:
        """Remove all subscriptions or only those for a specific event."""
        if event_name is None:
            self._subscriptions.clear()
            return

        self._validate_event_name(event_name)
        self._subscriptions.pop(event_name, None)
