import logging

from app.core.paths import ProjectPaths

__all__ = ["configure_logging", "get_logger"]

_APP_LOGGER_NAME = "app"
_APP_HANDLER_FLAG = "_app_core_logger_handler"
_LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging(
    paths: ProjectPaths,
    *,
    level: int = logging.INFO,
    console_enabled: bool = True,
) -> None:
    """Configure the application logging system.

    The function is safe to call multiple times and will not add duplicate
    handlers created by this module.

    Args:
        paths: ProjectPaths instance used to resolve the log directory.
        level: Logging level for the application logger.
        console_enabled: If True, logs are also written to the terminal.
    """
    paths.create_runtime_directories()

    logger = logging.getLogger(_APP_LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    _remove_managed_handlers(logger)

    formatter = logging.Formatter(_LOG_FORMAT, datefmt=_DATE_FORMAT)
    log_file = paths.logs / "app.log"

    file_handler = logging.FileHandler(log_file, encoding="utf-8", mode="a")
    file_handler.setFormatter(formatter)
    setattr(file_handler, _APP_HANDLER_FLAG, True)
    logger.addHandler(file_handler)

    if console_enabled:
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        setattr(stream_handler, _APP_HANDLER_FLAG, True)
        logger.addHandler(stream_handler)


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the application logger.

    Args:
        name: Logger name relative to the application logger or a full logger
            name beginning with "app".

    Returns:
        A configured logger for the application.
    """
    sanitized_name = name.strip(".")
    if not sanitized_name:
        return logging.getLogger(_APP_LOGGER_NAME)
    if sanitized_name == _APP_LOGGER_NAME or sanitized_name.startswith(f"{_APP_LOGGER_NAME}."):
        return logging.getLogger(sanitized_name)
    return logging.getLogger(f"{_APP_LOGGER_NAME}.{sanitized_name}")


def _remove_managed_handlers(logger: logging.Logger) -> None:
    """Remove and close handlers created by this module from the given logger."""
    managed_handlers = [
        handler for handler in logger.handlers if getattr(handler, _APP_HANDLER_FLAG, False)
    ]
    for handler in managed_handlers:
        logger.removeHandler(handler)
        handler.close()
