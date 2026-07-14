"""Application entry point."""

from __future__ import annotations

import sys

from app.core.app import Application

__all__ = ["main"]


def main() -> int:
    """Create the application and execute its lifecycle."""
    application = Application()
    return application.execute()


if __name__ == "__main__":
    sys.exit(main())
