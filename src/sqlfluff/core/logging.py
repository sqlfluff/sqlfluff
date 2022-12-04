"""Functions for setting up logging."""
import logging
import os


def set_logging_verbosity(verbosity):
    """Set up SQLFluff loggers with specified verbosity."""
    fluff_logger = logging.getLogger("sqlfluff")

    # NB: We treat the parser logger slightly differently because it's noisier.
    # It's important that we set levels for all each time so
    # that we don't break tests by changing the granularity
    # between tests.
    parser_logger = logging.getLogger("sqlfluff.parser")
    if verbosity < 3:
        fluff_logger.setLevel(logging.WARNING)
        parser_logger.setLevel(logging.NOTSET)
    elif verbosity == 3:
        fluff_logger.setLevel(logging.INFO)
        parser_logger.setLevel(logging.WARNING)
    elif verbosity == 4:
        fluff_logger.setLevel(logging.DEBUG)
        parser_logger.setLevel(logging.INFO)
    elif verbosity > 4:
        fluff_logger.setLevel(logging.DEBUG)
        parser_logger.setLevel(logging.DEBUG)


def initialize_worker_logging(verbosity):
    """Called for each worker process to set up logging.

    We need to do this because the worker processes are
    spawned by the main process, and so don't inherit the
    logging configuration.
    """
    # Initialize logging to a file, whose name is the process ID. Based on:
    # https://docs.python.org/3/howto/logging-cookbook.html#logging-cookbook
    logger = logging.getLogger()
    fh = logging.FileHandler(f"{os.getpid()}.log")
    logger.addHandler(fh)
    set_logging_verbosity(verbosity)
