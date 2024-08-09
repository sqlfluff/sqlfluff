"""Implements runner classes used internally by the Linter class.

Implements various runner types for SQLFluff:
- Serial
- Parallel
  - Multiprocess
  - Multithread (used only by automated tests)
"""

import bdb
import functools
import logging
import multiprocessing
import multiprocessing.dummy
import signal
import sys
import traceback
from abc import ABC
from typing import Callable, Iterator, List, Tuple

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLFluffSkipFile
from sqlfluff.core.linter import LintedFile, RenderedFile
from sqlfluff.core.plugin.host import is_main_process

linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")


class BaseRunner(ABC):
    """Base runner class."""

    def __init__(
        self,
        linter: Linter,
        config: FluffConfig,
    ) -> None:
        self.linter = linter
        self.config = config

    pass_formatter = True

    def iter_rendered(self, fnames: List[str]) -> Iterator[Tuple[str, RenderedFile]]:
        """Iterate through rendered files ready for linting."""
        for fname in self.linter.templater.sequence_files(
            fnames, config=self.config, formatter=self.linter.formatter
        ):
            try:
                yield fname, self.linter.render_file(fname, self.config)
            except SQLFluffSkipFile as s:
                linter_logger.warning(str(s))

    def iter_partials(
        self,
        fnames: List[str],
        fix: bool = False,
    ) -> Iterator[Tuple[str, Callable]]:
        """Iterate through partials for linted files.

        Generates filenames and objects which return LintedFiles.
        """
        for fname, rendered in self.iter_rendered(fnames):
            # Generate a fresh ruleset
            rule_pack = self.linter.get_rulepack(config=rendered.config)
            yield (
                fname,
                functools.partial(
                    self.linter.lint_rendered,
                    rendered,
                    rule_pack,
                    fix,
                    # Formatters may or may not be passed. They don't pickle
                    # nicely so aren't appropriate in a multiprocessing world.
                    self.linter.formatter if self.pass_formatter else None,
                ),
            )

    def run(self, fnames: List[str], fix: bool):
        """Run linting on the specified list of files."""
        raise NotImplementedError  # pragma: no cover

    @classmethod
    def _init_global(cls, config) -> None:
        """Initializes any global state.

        May be overridden by subclasses to apply global configuration, initialize
        logger state in child processes, etc.
        """
        pass

    @staticmethod
    def _handle_lint_path_exception(fname, e) -> None:
        if isinstance(e, IOError):
            # IOErrors are caught in commands.py, so propagate it
            raise (e)  # pragma: no cover
        linter_logger.warning(
            f"""Unable to lint {fname} due to an internal error. \
Please report this as an issue with your query's contents and stacktrace below!
To hide this warning, add the failing file to .sqlfluffignore
{traceback.format_exc()}""",
        )


class SequentialRunner(BaseRunner):
    """Simple runner that does sequential processing."""

    def run(self, fnames: List[str], fix: bool) -> Iterator[LintedFile]:
        """Sequential implementation."""
        for fname, partial in self.iter_partials(fnames, fix=fix):
            try:
                yield partial()
            except (bdb.BdbQuit, KeyboardInterrupt):  # pragma: no cover
                raise
            except Exception as e:
                self._handle_lint_path_exception(fname, e)


class ParallelRunner(BaseRunner):
    """Base class for parallel runner implementations (process or thread)."""

    POOL_TYPE: Callable
    MAP_FUNCTION_NAME: str
    # Don't pass the formatter in a parallel world, they
    # don't pickle well.
    pass_formatter = False

    def __init__(self, linter, config, processes) -> None:
        super().__init__(linter, config)
        self.processes = processes

    def run(self, fnames: List[str], fix: bool):
        """Parallel implementation.

        Note that the partials are generated one at a time then
        passed directly into the pool as they're ready. This means
        the main thread can do the IO work while passing the parsing
        and linting work out to the threads.
        """
        with self._create_pool(
            self.processes,
            self._init_global,
            (self.config,),
        ) as pool:
            try:
                for lint_result in self._map(
                    pool,
                    self._apply,
                    self.iter_partials(fnames, fix=fix),
                ):
                    if isinstance(lint_result, DelayedException):
                        try:
                            lint_result.reraise()
                        except Exception as e:
                            self._handle_lint_path_exception(lint_result.fname, e)
                    else:
                        # It's a LintedDir.
                        if self.linter.formatter:
                            self.linter.formatter.dispatch_file_violations(
                                lint_result.path,
                                lint_result,
                                only_fixable=fix,
                                warn_unused_ignores=self.linter.config.get(
                                    "warn_unused_ignores"
                                ),
                            )
                        yield lint_result
            except KeyboardInterrupt:  # pragma: no cover
                # On keyboard interrupt (Ctrl-C), terminate the workers.
                # Notify the user we've received the signal and are cleaning up,
                # in case it takes awhile.
                print("Received keyboard interrupt. Cleaning up and shutting down...")
                pool.terminate()

    @staticmethod
    def _apply(partial_tuple):
        """Shim function used in parallel mode."""
        # Unpack the tuple and ditch the filename in this case.
        fname, partial = partial_tuple
        try:
            return partial()
        # Capture any exceptions and return as delayed exception to handle
        # in the main thread.
        except Exception as e:
            return DelayedException(e, fname=fname)

    @classmethod
    def _init_global(cls, config) -> None:  # pragma: no cover
        """For the parallel runners indicate that we're not in the main thread."""
        is_main_process.set(False)
        super()._init_global(config)

    @classmethod
    def _create_pool(cls, *args, **kwargs):
        return cls.POOL_TYPE(*args, **kwargs)

    @classmethod
    def _map(cls, pool, *args, **kwargs):
        """Runs a class-appropriate version of the general map() function."""
        return getattr(pool, cls.MAP_FUNCTION_NAME)(*args, **kwargs)


class MultiProcessRunner(ParallelRunner):
    """Runner that does parallel processing using multiple processes."""

    POOL_TYPE = multiprocessing.Pool
    MAP_FUNCTION_NAME = "imap_unordered"

    @classmethod
    def _init_global(cls, config) -> None:  # pragma: no cover
        super()._init_global(config)

        # Disable signal handling in the child processes to let the parent
        # control all KeyboardInterrupt handling (Control C). This is
        # necessary in order for keyboard interrupts to exit quickly and
        # cleanly. Adapted from this post:
        # https://stackoverflow.com/questions/11312525/catch-ctrlc-sigint-and-exit-multiprocesses-gracefully-in-python
        signal.signal(signal.SIGINT, signal.SIG_IGN)


class MultiThreadRunner(ParallelRunner):
    """Runner that does parallel processing using multiple threads.

    Used only by automated tests.
    """

    POOL_TYPE = multiprocessing.dummy.Pool
    MAP_FUNCTION_NAME = "imap"


class DelayedException(Exception):
    """Multiprocessing process pool uses this to propagate exceptions."""

    def __init__(self, ee, fname=None):
        self.ee = ee
        __, __, self.tb = sys.exc_info()
        self.fname = None
        super().__init__(str(ee))

    def reraise(self):
        """Reraise the encapsulated exception."""
        raise self.ee.with_traceback(self.tb)


def get_runner(
    linter: Linter,
    config: FluffConfig,
    processes: int,
    allow_process_parallelism: bool = True,
) -> Tuple[BaseRunner, int]:
    """Generate a runner instance based on parallel and system configuration.

    The processes argument can be positive or negative.
    - If positive, the integer is interpreted as the number of processes.
    - If negative or zero, the integer is interpreted as number_of_cpus - processes.

    e.g.
    -1 = all cpus but one.
    0 = all cpus
    1 = 1 cpu

    """
    if processes <= 0:
        processes = max(multiprocessing.cpu_count() + processes, 1)

    if processes > 1:
        # Process parallelism isn't really supported during testing
        # so this flag allows us to fall back to a threaded runner
        # in those cases.
        if allow_process_parallelism:
            return MultiProcessRunner(linter, config, processes=processes), processes
        else:
            return MultiThreadRunner(linter, config, processes=processes), processes
    else:
        return SequentialRunner(linter, config), processes
