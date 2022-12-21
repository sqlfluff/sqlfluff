import logging
from functools import lru_cache
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional, Union

from rich.logging import RichHandler

# Log File Format
LOG_FILE_FORMAT = "%(asctime)s — %(name)s — %(levelname)s — %(message)s"

# Log File Path
LOG_PATH = Path.home().absolute() / ".dbt-osmosis" / "logs"

# Console Output Level
LOGGING_LEVEL = logging.INFO


def rotating_log_handler(
    name: str,
    path: Path,
    formatter: str,
) -> RotatingFileHandler:
    """This handler writes warning and higher level outputs to logs in a home .dbt-osmosis directory rotating them as needed"""
    path.mkdir(parents=True, exist_ok=True)
    handler = RotatingFileHandler(
        str(path / "{log_name}.log".format(log_name=name)),
        maxBytes=int(1e6),
        backupCount=3,
    )
    handler.setFormatter(logging.Formatter(formatter))
    handler.setLevel(logging.WARNING)
    return handler


@lru_cache(maxsize=10)
def logger(
    name: str = "dbt-osmosis",
    level: Optional[Union[int, str]] = None,
    path: Optional[Path] = None,
    formatter: Optional[str] = None,
) -> logging.Logger:
    """Builds and caches loggers. Can be configured with module level attributes or on a call by call basis.
    Simplifies logger management without having to instantiate separate pointers in each module.

    Args:
        name (str, optional): Logger name, also used for output log file name in `~/.dbt-osmosis/logs` directory.
        level (Union[int, str], optional): Logging level, this is explicitly passed to console handler which effects what level of log messages make it to the console. Defaults to logging.INFO.
        path (Path, optional): Path for output warning level+ log files. Defaults to `~/.dbt-osmosis/logs`
        formatter (str, optional): Format for output log files. Defaults to a "time — name — level — message" format

    Returns:
        logging.Logger: Prepared logger with rotating logs and console streaming. Can be executed directly from function.
    """
    if isinstance(level, str):
        level = getattr(logging, level, logging.INFO)
    if level is None:
        level = LOGGING_LEVEL
    if path is None:
        path = LOG_PATH
    if formatter is None:
        formatter = LOG_FILE_FORMAT
    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    _logger.addHandler(rotating_log_handler(name, path, formatter))
    _logger.addHandler(
        RichHandler(
            level=level,
            rich_tracebacks=True,
            markup=True,
            show_time=False,
        )
    )
    _logger.propagate = False
    return _logger
