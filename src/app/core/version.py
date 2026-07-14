"""Centralized application version and product metadata."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = [
    "APP_NAME",
    "APP_DISPLAY_NAME",
    "APP_VERSION",
    "AppVersion",
]

APP_NAME: str = "pth_fausta"
APP_DISPLAY_NAME: str = "PTH Fausta"
APP_VERSION: str = "0.1.0"


@dataclass(frozen=True, slots=True)
class AppVersion:
    """Immutable semantic version value object."""

    major: int
    minor: int
    patch: int

    def __post_init__(self) -> None:
        """Validate version component values on initialization."""
        for field_name, value in (("major", self.major), ("minor", self.minor), ("patch", self.patch)):
            if type(value) is not int:
                raise ValueError(f"{field_name} must be an integer, got {value!r}")
            if value < 0:
                raise ValueError(f"{field_name} must be non-negative, got {value!r}")

    @classmethod
    def parse(cls, version: str) -> "AppVersion":
        """Parse a semantic version string into an AppVersion instance."""
        if not isinstance(version, str):
            raise ValueError(f"Invalid version {version!r}; expected format MAJOR.MINOR.PATCH")

        parts = version.split(".")
        if len(parts) != 3:
            raise ValueError(f"Invalid version {version!r}; expected format MAJOR.MINOR.PATCH")

        parsed_parts: list[int] = []
        for part in parts:
            if not part:
                raise ValueError(f"Invalid version {version!r}; expected format MAJOR.MINOR.PATCH")
            if not part.isdigit():
                raise ValueError(f"Invalid version {version!r}; expected format MAJOR.MINOR.PATCH")
            parsed_parts.append(int(part))

        if any(value < 0 for value in parsed_parts):
            raise ValueError(f"Invalid version {version!r}; expected format MAJOR.MINOR.PATCH")

        return cls(major=parsed_parts[0], minor=parsed_parts[1], patch=parsed_parts[2])

    def __str__(self) -> str:
        """Return the version in MAJOR.MINOR.PATCH format."""
        return f"{self.major}.{self.minor}.{self.patch}"


_CURRENT_VERSION = AppVersion.parse(APP_VERSION)
