"""This is a modified log capture mechanism which reliably works.

So that logs are handled appropriately by the CLI, sqlfluff
modifies the root logger in a way that can conflict with pytest.

See: https://github.com/pytest-dev/pytest/issues/3697

This fixture returns a context manager to handle them better
and enable testing of logs while working around the restrictions
of setting the `propagate` attribute of the logger in each test.

Code adapted from:
https://github.com/pytest-dev/pytest/issues/3697#issuecomment-792129636

"""

import logging
from contextlib import contextmanager
from typing import Iterator

from _pytest.logging import LogCaptureHandler, _remove_ansi_escape_sequences


class FluffLogHandler(LogCaptureHandler):
    """A modified LogCaptureHandler which also exposes some helper functions.

    The aim is to mimic some of the methods available on caplog.

    See:
    https://docs.pytest.org/en/7.1.x/_modules/_pytest/logging.html
    """

    @property
    def text(self) -> str:
        """The formatted log text."""
        return _remove_ansi_escape_sequences(self.stream.getvalue())


@contextmanager
def fluff_log_catcher(level: int, logger_name: str) -> Iterator[FluffLogHandler]:
    """Context manager that sets the level for capturing of logs.

    After the end of the 'with' statement the level is restored to its
    original value.

    Args:
        level (int): The lowest logging level to capture.
        logger_name (str): The name of the logger to capture.
    """
    assert logger_name.startswith(
        "sqlfluff"
    ), "This should only be used with a SQLFluff logger."
    logger = logging.getLogger(logger_name)
    handler = FluffLogHandler()
    orig_level = logger.level
    logger.setLevel(level)
    logger.addHandler(handler)
    try:
        yield handler
    finally:
        logger.setLevel(orig_level)
        logger.removeHandler(handler)
