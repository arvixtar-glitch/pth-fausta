"""Application lifecycle management."""

from __future__ import annotations

from app.core.config import AppConfig
from app.core.lifecycle import (
    ApplicationStatePort,
    ControllerPort,
    EventLoopPort,
    NavigationPort,
)
from app.core.version import APP_DISPLAY_NAME, APP_VERSION

__all__ = ["Application"]


class Application:
    """Manage the application's lifecycle and startup sequence."""

    def __init__(
        self,
        app_state: ApplicationStatePort,
        navigation_service: NavigationPort,
        app_controller: ControllerPort,
        event_loop: EventLoopPort,
        config: AppConfig | None = None,
    ) -> None:
        """Initialize the application with its lifecycle dependencies."""
        self.app_state = app_state
        self.navigation_service = navigation_service
        self.app_controller = app_controller
        self.event_loop = event_loop
        self.config: AppConfig = config if config is not None else AppConfig()
        self.logger = self.config.logger

    def run(self) -> int:
        """Run the application startup sequence and return a success code."""
        self.logger.info(f"Starting {APP_DISPLAY_NAME} {APP_VERSION}.")
        self.app_state.start()
        self.navigation_service.navigate_to(self.app_controller)
        return self.event_loop.run()

    def shutdown(self) -> None:
        """Perform application shutdown tasks and log the completion."""
        self.navigation_service.close_current()
        self.app_state.stop()
        self.event_loop.quit()
        self.logger.info("Application shutdown completed.")

    def execute(self) -> int:
        """Execute the application lifecycle and always run shutdown."""
        try:
            return self.run()
        finally:
            self.shutdown()
