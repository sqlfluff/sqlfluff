"""Implements runner classes used internally by the Linter class.

Implements various runner types for SQLFluff:
- Serial
- Parallel
  - Multiprocess
  - Multithread (used only by automated tests)
"""
from abc import ABC
import functools
import logging
import multiprocessing.dummy
import signal
import sys
import traceback
from typing import List, Type

from sqlfluff.core.dialects import dialect_selector
from sqlfluff.core.parser import Lexer


linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")


class BaseRunner(ABC):
    """Base runner class."""

    def __init__(
        self,
        linter_cls: Type,
        linter,
        config,
        dialect: str,
    ):
        self.linter_cls = linter_cls
        self.linter = linter
        self.config = config
        self.dialect = dialect

    def run(self, fnames: List[str], fix: bool):
        """Run linting on the specified list of files."""
        raise NotImplementedError

    @classmethod
    def _init_global(cls, config, dialect):
        """Initializes any global state.

        May be overridden by subclasses to apply global configuration, initialize
        logger state in child processes, etc.
        """
        Lexer(dialect=dialect)
        dialect_selector(dialect)

    @classmethod
    def _base_run(cls, config, linter, fname, fix):
        """Core linting functionality."""
        config = config.make_child_from_path(fname)
        # Handle unicode issues gracefully
        with open(
            fname, "r", encoding="utf8", errors="backslashreplace"
        ) as target_file:
            return linter.lint_string(
                target_file.read(), fname=fname, fix=fix, config=config
            )

    @staticmethod
    def _handle_lint_path_exception(fname, e):
        if isinstance(e, IOError):
            # IOErrors are caught in commands.py, so propagate it
            raise (e)
        linter_logger.warning(
            f"""Unable to lint {fname} due to an internal error. \
Please report this as an issue with your query's contents and stacktrace below!
To hide this warning, add the failing file to .sqlfluffignore
{traceback.format_exc()}""",
        )


class SequentialRunner(BaseRunner):
    """Simple runner that does sequential processing."""

    def run(self, fnames, fix):
        """Sequential implementation."""
        for fname in fnames:
            try:
                yield self._base_run(self.config, self.linter, fname, fix)
            except Exception as e:
                self._handle_lint_path_exception(fname, e)


class MultiProcessRunner(BaseRunner):
    """Runner that does parallel processing using multiprocessing.Pool."""

    def __init__(self, linter_cls, linter, config, dialect, parallel):
        super().__init__(linter_cls, linter, config, dialect)
        self.parallel = parallel

    @classmethod
    def _init_global(cls, config, dialect):
        super()._init_global(config, dialect)
        cls._disable_signal_handling()

    def run(self, fnames, fix):
        """Parallel implementation."""
        jobs = []
        for fname in fnames:
            jobs.append(
                functools.partial(
                    self._lint_path,
                    self.linter_cls,
                    self.config,
                    fname,
                    fix,
                )
            )
        with self._create_pool(
            self.parallel,
            self._init_global,
            (
                self.config,
                self.dialect,
            ),
        ) as pool:
            try:
                # From this point forward, any keyboard interrupt will raise an
                # exception, and the context handler managing the pool will
                # automatically terminate child processes for us.
                for lint_result in self._map(pool, self._apply, jobs):
                    if isinstance(lint_result, DelayedException):
                        try:
                            lint_result.reraise()
                        except Exception as e:
                            self._handle_lint_path_exception(lint_result.fname, e)
                    else:
                        # It's a LintedPath.
                        if self.linter.formatter:
                            self.linter.formatter.dispatch_file_violations(
                                lint_result.path, lint_result, only_fixable=fix
                            )
                        yield lint_result
            except KeyboardInterrupt:
                print("Received keyboard interrupt. Cleaning up and shutting down...")
                pool.terminate()

    @classmethod
    def _disable_signal_handling(cls):
        # Disable signal handling in the child processes to let the parent
        # control all KeyboardInterrupt handling (Control C). This is
        # necessary in order for keyboard interrupts to exit quickly and
        # cleanly. Adapted from this post:
        # https://stackoverflow.com/questions/11312525/catch-ctrlc-sigint-and-exit-multiprocesses-gracefully-in-python
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    @classmethod
    def _create_pool(cls, *args, **kwargs):
        return multiprocessing.Pool(*args, **kwargs)

    @classmethod
    def _lint_path(cls, linter_cls, config, fname, fix=False):
        """Lint a file in parallel mode.

        Creates new Linter object to avoid multiprocessing-related pickling
        errors.
        """
        try:
            linter = linter_cls(config=config)
            return cls._base_run(config, linter, fname, fix)
        except Exception as e:
            result = DelayedException(e)
            result.fname = fname
            return result

    @classmethod
    def _map(cls, pool, *args, **kwargs):
        """Runs a class-appropriate version of the general map() function."""
        return pool.imap_unordered(*args, **kwargs)

    @staticmethod
    def _apply(f):
        """Shim function used in parallel mode."""
        return f()


class MultiThreadRunner(MultiProcessRunner):
    """Subclasses the multiprocess runner. Used only by automated tests."""

    @classmethod
    def _disable_signal_handling(cls):
        """Prevent disabling signal handling behavior with threads.

        Reason: All threads share the same signal handling behavior, so it's not
        appropriate to disable it in child threads as it is with processes.
        """
        pass

    @classmethod
    def _create_pool(cls, *args, **kwargs):
        return multiprocessing.dummy.Pool(*args, **kwargs)

    @classmethod
    def _map(cls, pool, *args, **kwargs):
        """Runs a class-appropriate version of the general map() function."""
        return pool.imap(*args, **kwargs)


class DelayedException(Exception):
    """Multiprocessing process pool uses this to propagate exceptions."""

    def __init__(self, ee):
        self.ee = ee
        __, __, self.tb = sys.exc_info()
        self.fname = None
        super().__init__(str(ee))

    def reraise(self):
        """Reraise the encapsulated exception."""
        raise self.ee.with_traceback(self.tb)
