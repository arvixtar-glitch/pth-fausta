"""Application lifecycle management."""

from __future__ import annotations

from app.core.config import AppConfig
from app.core.version import APP_DISPLAY_NAME, APP_VERSION

__all__ = ["Application"]


class Application:
    """Manage the application's lifecycle and startup sequence."""

    def __init__(self, config: AppConfig | None = None) -> None:
        """Initialize the application with the provided or default config."""
        self.config: AppConfig = config if config is not None else AppConfig()
        self.logger = self.config.logger

    def run(self) -> int:
        """Run the application startup sequence and return a success code."""
        self.logger.info(f"Starting {APP_DISPLAY_NAME} {APP_VERSION}.")
        self.logger.info("Application is ready.")
        return 0

    def shutdown(self) -> None:
        """Perform application shutdown tasks and log the completion."""
        self.logger.info("Application shutdown completed.")

    def execute(self) -> int:
        """Execute the application lifecycle and always run shutdown."""
        try:
            return self.run()
        finally:
            self.shutdown()
