"""Implements runner classes used internally by the Linter class.

Implements various runner types for SQLFluff:
- Serial
- Parallel
  - Multiprocess
  - Multithread (used only by automated tests)
"""

import bdb
import logging
import multiprocessing
import multiprocessing.dummy
import multiprocessing.pool
import signal
import sys
import traceback
from abc import ABC, abstractmethod
from collections import defaultdict, deque
from collections.abc import Iterable, Iterator
from types import TracebackType
from typing import TYPE_CHECKING, Callable, NamedTuple, Optional, Union

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLFluffSkipFile
from sqlfluff.core.linter import LintedFile, RenderedFile
from sqlfluff.core.linter.common import DeferredRenderTask, RenderedLintTask
from sqlfluff.core.plugin.host import is_main_process

linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.formatter import FormatterInterface
    from sqlfluff.core.templaters import RawTemplater

LintTask = Union[RenderedLintTask, DeferredRenderTask]


class PreparedFile(NamedTuple):
    """A file paired with its effective configuration."""

    discovery_index: int
    fname: str
    config: FluffConfig


class BaseRunner(ABC):
    """Base runner class."""

    def __init__(
        self,
        linter: Linter,
        config: FluffConfig,
    ) -> None:
        self.linter = linter
        self.config = config
        self.skipped_file_count: int = 0

    def _file_groups(
        self, fnames: list[str], start_index: int = 0
    ) -> list[tuple["RawTemplater", FluffConfig, list[PreparedFile]]]:
        """Group files by invocation-scoped templater in discovery order."""
        groups: list[tuple["RawTemplater", FluffConfig, list[PreparedFile]]] = []
        group_indexes: dict[int, int] = {}
        for index, fname in enumerate(fnames, start=start_index):
            file_config = self.config.make_child_from_path(fname)
            prepared = PreparedFile(index, fname, file_config)
            templater = self.linter.templater_for_config(file_config)
            templater_id = id(templater)
            if templater_id not in group_indexes:
                group_indexes[templater_id] = len(groups)
                groups.append((templater, file_config, []))
            group_index = group_indexes[templater_id]
            groups[group_index][2].append(prepared)
        return groups

    def _render_group(
        self,
        templater: "RawTemplater",
        file_config: FluffConfig,
        group_files: list[PreparedFile],
        formatter: Optional["FormatterInterface"],
    ) -> Iterator[tuple[PreparedFile, RenderedFile]]:
        """Render one templater group in its required file order."""
        files_by_name: dict[str, deque[PreparedFile]] = defaultdict(deque)
        for prepared in group_files:
            files_by_name[prepared.fname].append(prepared)
        for fname in templater.sequence_files(
            [prepared.fname for prepared in group_files],
            config=file_config,
            formatter=formatter,
        ):
            prepared = files_by_name[fname].popleft()
            try:
                source_str, encoding = self.linter.load_raw_file(
                    prepared.fname, prepared.config
                )
                yield (
                    prepared,
                    self.linter._render_string(
                        source_str,
                        prepared.fname,
                        prepared.config,
                        encoding,
                    ),
                )
            except SQLFluffSkipFile as error:
                linter_logger.warning(str(error))
                self.skipped_file_count += 1

    def iter_rendered(self, fnames: list[str]) -> Iterator[tuple[str, RenderedFile]]:
        """Iterate through rendered files ready for linting."""
        from sqlfluff.core.templaters import RawTemplater

        for index, fname in enumerate(fnames):
            file_config = self.config.make_child_from_path(fname)
            templater = self.linter.templater_for_config(file_config)
            prepared = PreparedFile(index, fname, file_config)
            if type(templater).sequence_files is RawTemplater.sequence_files:
                yield from (
                    (rendered.fname, rendered)
                    for _, rendered in self._render_group(
                        templater,
                        file_config,
                        [prepared],
                        self.linter.formatter,
                    )
                )
                continue

            groups = [(templater, file_config, [prepared])]
            group_indexes = {id(templater): 0}
            for remaining_group in self._file_groups(
                fnames[index + 1 :], start_index=index + 1
            ):
                remaining_templater, remaining_config, remaining_files = remaining_group
                group_index = group_indexes.get(id(remaining_templater))
                if group_index is None:
                    group_indexes[id(remaining_templater)] = len(groups)
                    groups.append(remaining_group)
                else:
                    groups[group_index][2].extend(remaining_files)
            yield from self._iter_rendered_groups(groups)
            return

    def _iter_rendered_groups(
        self,
        groups: list[tuple["RawTemplater", FluffConfig, list[PreparedFile]]],
    ) -> Iterator[tuple[str, RenderedFile]]:
        """Iterate through already grouped files ready for linting."""
        rendered_files: dict[int, RenderedFile] = {}
        completed_indexes: set[int] = set()
        next_index = min(
            prepared.discovery_index
            for _, _, group_files in groups
            for prepared in group_files
        )
        for templater, file_config, group_files in groups:
            try:
                for prepared, rendered in self._render_group(
                    templater,
                    file_config,
                    group_files,
                    self.linter.formatter,
                ):
                    rendered_files[prepared.discovery_index] = rendered
                    completed_indexes.add(prepared.discovery_index)
                    while next_index in rendered_files:
                        next_rendered = rendered_files.pop(next_index)
                        yield next_rendered.fname, next_rendered
                        next_index += 1
            finally:
                self.linter.release_templater(templater)
            completed_indexes.update(
                prepared.discovery_index for prepared in group_files
            )
            while next_index in completed_indexes:
                if next_index in rendered_files:
                    rendered = rendered_files.pop(next_index)
                    yield rendered.fname, rendered
                next_index += 1

    @abstractmethod
    def run(self, fnames: list[str], fix: bool) -> Iterator[LintedFile]:
        """Run linting on the specified list of files."""
        ...

    @classmethod
    def _init_global(cls) -> None:
        """Initializes any global state.

        May be overridden by subclasses to apply global configuration, initialize
        logger state in child processes, etc.
        """
        pass

    @staticmethod
    def _handle_lint_path_exception(fname: Optional[str], e: BaseException) -> None:
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

    def run(self, fnames: list[str], fix: bool) -> Iterator[LintedFile]:
        """Sequential implementation."""
        with self.linter.templater_session():
            for fname, rendered in self.iter_rendered(fnames):
                try:
                    rule_pack = self.linter.get_rulepack(config=rendered.config)
                    yield self.linter.lint_rendered(
                        rendered, rule_pack, fix, self.linter.formatter
                    )
                except (bdb.BdbQuit, KeyboardInterrupt):  # pragma: no cover
                    raise
                except Exception as e:
                    self._handle_lint_path_exception(fname, e)


class ParallelRunner(BaseRunner):
    """Base class for parallel runner implementations (process or thread)."""

    POOL_TYPE: Callable[..., multiprocessing.pool.Pool]

    def __init__(self, linter: Linter, config: FluffConfig, processes: int) -> None:
        super().__init__(linter, config)
        self.processes = processes

    def iter_partials(
        self,
        fnames: list[str],
        fix: bool = False,
    ) -> Iterator[tuple[str, LintTask]]:
        """Iterate through partials or deferred tasks for parallel linting.

        When the active templater supports worker-side rendering
        (``templates_in_worker = True``), we emit a lightweight
        ``DeferredRenderTask`` containing only the filename and root config.
        The worker process calls ``render_file`` itself, keeping the full
        ``RenderedFile`` off the IPC boundary.

        For templaters that require main-process state (e.g. dbt), we fall
        back to the base-class behaviour and template in the main process.
        """
        with self.linter.templater_session():
            for templater, file_config, group_files in self._file_groups(fnames):
                try:
                    files_by_name: dict[str, deque[PreparedFile]] = defaultdict(deque)
                    for prepared in group_files:
                        files_by_name[prepared.fname].append(prepared)
                    if templater.templates_in_worker:
                        sequenced_files = templater.sequence_files(
                            [prepared.fname for prepared in group_files],
                            config=file_config,
                            formatter=None,
                        )
                        for fname in sequenced_files:
                            prepared = files_by_name[fname].popleft()
                            yield (
                                prepared.fname,
                                DeferredRenderTask(
                                    prepared.fname,
                                    self.config,
                                    fix,
                                    tuple(self.linter.user_rules),
                                ),
                            )
                    else:
                        for prepared, rendered in self._render_group(
                            templater, file_config, group_files, None
                        ):
                            yield (
                                prepared.fname,
                                RenderedLintTask(
                                    rendered, fix, tuple(self.linter.user_rules)
                                ),
                            )
                finally:
                    self.linter.release_templater(templater)

    def run(self, fnames: list[str], fix: bool) -> Iterator[LintedFile]:
        """Parallel implementation.

        Note that the partials are generated one at a time then
        passed directly into the pool as they're ready. This means
        the main thread can do the IO work while passing the parsing
        and linting work out to the threads.
        """
        # NOTE: We avoid using `with pool:` here because Pool.__exit__
        # calls pool.terminate() but NOT pool.join(). Without join(), worker
        # processes may still be alive when Python's resource_tracker runs at
        # shutdown, causing "leaked semaphore objects" warnings from the named
        # POSIX semaphores used by the pool's internal SimpleQueue locks.
        pool = self._create_pool(self.processes, self._init_global)
        try:
            for lint_result in self._map(
                pool,
                self._apply,
                self.iter_partials(fnames, fix=fix),
            ):
                if isinstance(lint_result, DelayedException):
                    if isinstance(lint_result.ee, SQLFluffSkipFile):
                        # A file was skipped (e.g. exceeded
                        # large_file_skip_byte_limit). Log a plain warning,
                        # not the "please report as bug" message.
                        linter_logger.warning(str(lint_result.ee))
                        self.skipped_file_count += 1
                    else:
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
        finally:
            try:
                pool.terminate()
            finally:
                pool.join()

    @staticmethod
    def _apply(
        partial_tuple: tuple[str, LintTask],
    ) -> Union["DelayedException", LintedFile]:
        """Shim function used in parallel mode."""
        fname, task = partial_tuple
        try:
            if isinstance(task, DeferredRenderTask):
                # Worker-side rendering: reconstruct a Linter from the root
                # config and do render + lint in one step, keeping the full
                # RenderedFile off the IPC boundary.
                linter = Linter(
                    config=task.root_config, user_rules=list(task.user_rules)
                )
                rendered = linter.render_file(task.fname, task.root_config)
                rule_pack = linter.get_rulepack(config=rendered.config)
                return Linter.lint_rendered(rendered, rule_pack, task.fix, None)
            linter = Linter(
                config=task.rendered.config, user_rules=list(task.user_rules)
            )
            rule_pack = linter.get_rulepack(config=task.rendered.config)
            return Linter.lint_rendered(task.rendered, rule_pack, task.fix, None)
        # Capture any exceptions and return as delayed exception to handle
        # in the main thread.
        except Exception as e:
            return DelayedException(e, fname=fname)

    @classmethod
    def _init_global(cls) -> None:  # pragma: no cover
        """For the parallel runners indicate that we're not in the main thread."""
        is_main_process.set(False)
        super()._init_global()

    @classmethod
    def _create_pool(
        cls, processes: int, initializer: Callable[[], None]
    ) -> multiprocessing.pool.Pool:
        return cls.POOL_TYPE(processes=processes, initializer=initializer)

    @classmethod
    @abstractmethod
    def _map(
        cls,
        pool: multiprocessing.pool.Pool,
        func: Callable[
            [tuple[str, LintTask]],
            Union["DelayedException", LintedFile],
        ],
        iterable: Iterable[tuple[str, LintTask]],
    ) -> Iterable[Union["DelayedException", LintedFile]]:  # pragma: no cover
        """Class-specific map method.

        NOTE: Must be overridden by an implementation.
        """
        ...


class MultiProcessRunner(ParallelRunner):
    """Runner that does parallel processing using multiple processes."""

    # NOTE: Python 3.13 deprecates calling `Pool` without first setting
    # the context. The default was already "spawn" for MacOS and Windows
    # but was previously "fork" for other Linux platforms. From python
    # 3.14 onwards, the default will not be "fork" anymore.
    # In testing we've found no significant difference between "fork"
    # and "spawn", and so settle on "spawn" for all operating system.
    # https://docs.python.org/3/library/multiprocessing.html#contexts-and-start-methods
    POOL_TYPE = multiprocessing.get_context("spawn").Pool

    @classmethod
    def _init_global(cls) -> None:  # pragma: no cover
        super()._init_global()

        # Disable signal handling in the child processes to let the parent
        # control all KeyboardInterrupt handling (Control C). This is
        # necessary in order for keyboard interrupts to exit quickly and
        # cleanly. Adapted from this post:
        # https://stackoverflow.com/questions/11312525/catch-ctrlc-sigint-and-exit-multiprocesses-gracefully-in-python
        signal.signal(signal.SIGINT, signal.SIG_IGN)

    @classmethod
    def _map(
        cls,
        pool: multiprocessing.pool.Pool,
        func: Callable[
            [tuple[str, LintTask]],
            Union["DelayedException", LintedFile],
        ],
        iterable: Iterable[tuple[str, LintTask]],
    ) -> Iterable[Union["DelayedException", LintedFile]]:
        """Map using imap unordered.

        Yield files as workers finish processing them.
        """
        return pool.imap_unordered(func=func, iterable=iterable)


class MultiThreadRunner(ParallelRunner):
    """Runner that does parallel processing using multiple threads.

    Used only by automated tests.
    """

    POOL_TYPE = multiprocessing.dummy.Pool

    @classmethod
    def _map(
        cls,
        pool: multiprocessing.pool.Pool,
        func: Callable[
            [tuple[str, LintTask]],
            Union["DelayedException", LintedFile],
        ],
        iterable: Iterable[tuple[str, LintTask]],
    ) -> Iterable[Union["DelayedException", LintedFile]]:
        """Map using imap.

        We use this so we can iterate through results as they arrive, and while other
        files are still being processed.
        """
        return pool.imap(func=func, iterable=iterable)


class DelayedException(Exception):
    """Multiprocessing process pool uses this to propagate exceptions."""

    def __init__(self, ee: BaseException, fname: Optional[str] = None):
        self.ee = ee
        self.tb: Optional[TracebackType]
        _, _, self.tb = sys.exc_info()
        self.fname = fname
        super().__init__(str(ee))

    def reraise(self) -> None:
        """Reraise the encapsulated exception."""
        raise self.ee.with_traceback(self.tb)


def get_runner(
    linter: Linter,
    config: FluffConfig,
    processes: int,
    allow_process_parallelism: bool = True,
) -> tuple[BaseRunner, int]:
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
