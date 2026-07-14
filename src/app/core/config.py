from app.core.logger import configure_logging, get_logger
from app.core.paths import ProjectPaths
from app.core.settings import SettingsManager

__all__ = ["AppConfig"]


class AppConfig:
    """Initialize and expose core application components."""

    def __init__(self) -> None:
        """Initialize core components and configure application logging."""
        self.paths = ProjectPaths()
        self.paths.validate()

        self.settings_manager = SettingsManager(self.paths)
        self.settings = self.settings_manager.load()

        configure_logging(self.paths)
        self.logger = get_logger("config")
        self.logger.info("Configuration initialized.")

    def save_settings(self) -> None:
        """Save current settings and log the operation."""
        self.logger.info("Saving settings.")
        self.settings_manager.save(self.settings)
        self.logger.info("Settings saved.")
