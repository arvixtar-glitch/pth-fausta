"""Application entry point."""

from __future__ import annotations

import sys

from app.bootstrap import bootstrap

__all__ = ["main"]


def main() -> int:
    """Create the application and execute its lifecycle."""
    application = bootstrap()
    return application.execute()


if __name__ == "__main__":
    sys.exit(main())
