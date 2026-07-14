import json
from dataclasses import dataclass

from app.core.paths import ProjectPaths

__all__ = ["AppSettings", "SettingsManager", "SettingsError"]


class SettingsError(Exception):
    """Raised when application settings cannot be loaded or saved."""


@dataclass(slots=True)
class AppSettings:
    """Represent application settings with validation and JSON conversion."""

    language: str = "lt"
    theme: str = "system"
    auto_save: bool = True

    def validate(self) -> None:
        """Validate the application settings values."""
        allowed_languages = {"lt", "en"}
        allowed_themes = {"system", "light", "dark"}

        if not isinstance(self.language, str):
            raise ValueError(
                f"language must be a str, got {type(self.language).__name__}: {self.language}"
            )
        if self.language not in allowed_languages:
            raise ValueError(
                f"language must be one of {sorted(allowed_languages)}, got: {self.language}"
            )

        if not isinstance(self.theme, str):
            raise ValueError(
                f"theme must be a str, got {type(self.theme).__name__}: {self.theme}"
            )
        if self.theme not in allowed_themes:
            raise ValueError(
                f"theme must be one of {sorted(allowed_themes)}, got: {self.theme}"
            )

        if type(self.auto_save) is not bool:
            raise ValueError(
                f"auto_save must be a bool, got {type(self.auto_save).__name__}: {self.auto_save}"
            )

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable dict representation of the settings."""
        return {
            "language": self.language,
            "theme": self.theme,
            "auto_save": self.auto_save,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "AppSettings":
        """Create AppSettings from a dictionary while validating values."""
        if not isinstance(data, dict):
            raise ValueError(
                f"settings data must be a dict, got {type(data).__name__}"
            )

        default = cls()
        language = data.get("language", default.language)
        theme = data.get("theme", default.theme)
        auto_save = data.get("auto_save", default.auto_save)

        settings = cls(language=language, theme=theme, auto_save=auto_save)
        settings.validate()
        return settings


class SettingsManager:
    """Manage loading and saving application settings to a JSON file."""

    def __init__(self, paths: ProjectPaths) -> None:
        """Initialize the settings manager with project paths."""
        self.paths = paths
        self.file_path = paths.database / "settings.json"

    def load(self) -> AppSettings:
        """Load application settings from the JSON file."""
        if not self.file_path.exists():
            return AppSettings()

        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except json.JSONDecodeError as exc:
            raise SettingsError(
                f"Invalid JSON in settings file: {self.file_path}"
            ) from exc
        except OSError as exc:
            raise SettingsError(
                f"Unable to read settings file: {self.file_path}"
            ) from exc

        if not isinstance(data, dict):
            raise SettingsError(
                f"Settings JSON root must be an object in file: {self.file_path}"
            )

        try:
            return AppSettings.from_dict(data)
        except (ValueError, TypeError) as exc:
            raise SettingsError(
                f"Invalid settings values in file: {self.file_path}"
            ) from exc

    def save(self, settings: AppSettings) -> None:
        """Save application settings to the JSON file atomically."""
        settings.validate()

        database_dir = self.file_path.parent
        if not database_dir.exists() or not database_dir.is_dir():
            raise SettingsError(
                f"Database directory does not exist: {database_dir}"
            )

        temp_path = database_dir / "settings.json.tmp"
        try:
            with temp_path.open("w", encoding="utf-8") as file:
                json.dump(settings.to_dict(), file, ensure_ascii=False, indent=4)
                file.write("\n")
            temp_path.replace(self.file_path)
        except (OSError, TypeError, ValueError) as exc:
            try:
                if temp_path.exists():
                    temp_path.unlink()
            except OSError:
                pass
            raise SettingsError(
                f"Unable to save settings to file: {self.file_path}"
            ) from exc

    def reset(self) -> AppSettings:
        """Reset settings to defaults and save them."""
        settings = AppSettings()
        self.save(settings)
        return settings
