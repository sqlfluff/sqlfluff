"""Implements runner classes used internally by the Linter class.

Implements various runner types for SQLFluff:
- Serial
- Parallel
  - Multiprocess (pipelined: template in main, lint in workers)
  - WarmWorker (persistent pool: template + lint in workers)
  - Multithread (used only by automated tests)
"""

import bdb
import functools
import logging
import multiprocessing
import multiprocessing.dummy
import multiprocessing.pool
import os
import pickle
import signal
import sys
import traceback
from abc import ABC, abstractmethod
from collections.abc import Iterable, Iterator
from multiprocessing.shared_memory import SharedMemory
from types import TracebackType
from typing import Any, Callable, Optional, Union

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLFluffSkipFile
from sqlfluff.core.linter import LintedFile, RenderedFile
from sqlfluff.core.linter.common import DeferredRenderTask
from sqlfluff.core.plugin.host import is_main_process

linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")

PartialLintCallable = Callable[[], LintedFile]

# Module-level globals for warm worker state.
# Required because multiprocessing spawn creates fresh processes —
# the pool initializer and task functions share state only via
# module-level globals within each worker process.
_worker_init_data: Optional[dict[str, Any]] = None
_worker_linter_cache: Optional[Any] = None

# Enable verbose warm worker logging via environment variable.
_WARM_WORKER_DEBUG = os.environ.get("SQLFLUFF_WARM_WORKER_DEBUG", "").lower() in (
    "1",
    "true",
    "yes",
)


def _warm_worker_log(msg: str) -> None:
    """Log from a worker process. Only active when SQLFLUFF_WARM_WORKER_DEBUG=1."""
    if _WARM_WORKER_DEBUG:
        print(f"[warm_worker {os.getpid()}] {msg}", file=sys.stderr, flush=True)


def _warm_worker_initializer(  # pragma: no cover
    init_modules: list[str],
    config_bytes: bytes,
    setup_func_module: Optional[str] = None,
    setup_func_name: Optional[str] = None,
) -> None:
    """Generic pool initializer for warm workers.

    Phase 1: Import specified modules to warm up the Python import cache.
    Phase 2: If a setup function is specified, call it with config_bytes
             for templater-specific initialization (e.g., register adapter).

    This function is templater-agnostic. Templater-specific logic lives
    in the setup function provided by the plugin (e.g., dbt's
    ``warm_worker_setup`` in the dbt templater module).
    """
    import importlib
    import time

    global _worker_init_data

    t0 = time.perf_counter()
    is_main_process.set(False)
    signal.signal(signal.SIGINT, signal.SIG_IGN)

    # Phase 1: Pre-import modules to warm up the import cache.
    for mod_name in init_modules:
        try:
            importlib.import_module(mod_name)
        except ImportError:
            _warm_worker_log(f"initializer: could not import {mod_name}")

    # Phase 2: Call templater-specific setup function.
    if setup_func_module and setup_func_name:
        try:
            setup_mod = importlib.import_module(setup_func_module)
            setup_func = getattr(setup_mod, setup_func_name)
            _worker_init_data = setup_func(config_bytes)
        except Exception as e:
            _warm_worker_log(f"initializer: setup function failed: {e}")
            _worker_init_data = {}
    else:
        _worker_init_data = {}

    _warm_worker_log(f"initializer: total {time.perf_counter() - t0:.3f}s")


def _warm_worker_receive_init(shm_info: tuple[str, int]) -> bool:  # pragma: no cover
    """Receive and merge init data from shared memory in a worker process.

    Called via pool.map to broadcast init data to every worker before
    dispatching real tasks. This guarantees all workers are initialized
    regardless of imap_unordered scheduling.
    """
    global _worker_init_data, _worker_linter_cache

    # Reset cache so the next real task rebuilds with fresh init data.
    _worker_linter_cache = None

    shm_name, shm_size = shm_info
    shm = SharedMemory(name=shm_name, create=False)
    try:
        assert shm.buf is not None
        init_data_update = pickle.loads(shm.buf[:shm_size])
    finally:
        shm.close()
    if _worker_init_data is not None:
        _worker_init_data.update(init_data_update)
    else:
        _worker_init_data = init_data_update
    _warm_worker_log(f"received init data ({shm_size / 1024:.1f} KB) via shared memory")
    return True


def _warm_worker_apply(
    args: tuple[str, bool, tuple[str, int]],
) -> Union["DelayedException", LintedFile]:
    """Worker function for warm workers that caches the templater.

    Tasks carry ``(fname, fix, shm_ref)`` where ``shm_ref`` is a
    ``(name, size)`` pair for fallback shared memory access. Normally
    ``_worker_init_data`` is already populated by the broadcast call
    to ``_warm_worker_receive_init`` before any tasks are dispatched.
    The shared memory fallback handles replacement workers spawned by
    the pool after a crash.
    """
    import time

    global _worker_init_data, _worker_linter_cache

    fname, fix, shm_ref = args
    try:
        if _worker_linter_cache is None:
            # Rebuild linter cache. Normally _worker_init_data was
            # already populated by _warm_worker_receive_init broadcast.
            t0 = time.perf_counter()
            if _worker_init_data is None or "root_config" not in _worker_init_data:
                # Fallback: read from shared memory (replacement worker
                # that missed the broadcast).
                shm_name, shm_size = shm_ref
                shm = SharedMemory(name=shm_name, create=False)
                try:
                    assert shm.buf is not None
                    init_data_update = pickle.loads(shm.buf[:shm_size])
                finally:
                    shm.close()
                if _worker_init_data is not None:
                    _worker_init_data.update(init_data_update)
                else:
                    _worker_init_data = init_data_update
                _warm_worker_log("fallback: read init data from shared memory")

            root_config: FluffConfig = _worker_init_data["root_config"]
            linter = Linter(config=root_config)
            templater = root_config.get_templater()
            if hasattr(templater, "init_from_worker_data"):
                templater.init_from_worker_data(  # pragma: no cover
                    _worker_init_data, root_config
                )
            linter.templater = templater
            # Pre-build and cache the rule pack for the root config.
            rule_pack = linter.get_rulepack(config=root_config)
            _worker_linter_cache = (linter, templater, root_config, rule_pack)
            _warm_worker_log(f"worker initialized in {time.perf_counter() - t0:.3f}s")
        else:
            linter, templater, root_config, rule_pack = _worker_linter_cache
            linter.templater = templater

        t_render = time.perf_counter()
        rendered = linter.render_file(fname, root_config)
        t_lint = time.perf_counter()
        # Reuse cached rule pack when file config matches root config.
        # Per-file overrides (inline noqa, directory .sqlfluff) get
        # a fresh pack; the common case skips get_rulepack entirely.
        if rendered.config is not root_config:
            rule_pack = linter.get_rulepack(config=rendered.config)
        result = Linter.lint_rendered(rendered, rule_pack, fix, None)
        t_done = time.perf_counter()
        _warm_worker_log(
            f"{os.path.basename(fname)}: "
            f"render={t_lint - t_render:.3f}s "
            f"lint={t_done - t_lint:.3f}s"
        )
        # Strip the parsed tree and templated file before pickling
        # to reduce IPC size by ~90%. The tree is only needed when
        # --fix mode has violations to persist (fix_string() asserts
        # both tree and templated_file). Clean files and all lint-only
        # results skip the tree entirely.
        if not fix or not result.violations:
            result = result._replace(tree=None, templated_file=None)
        return result
    except Exception as e:
        return DelayedException(e, fname=fname)


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

    def iter_rendered(self, fnames: list[str]) -> Iterator[tuple[str, RenderedFile]]:
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
        fnames: list[str],
        fix: bool = False,
    ) -> Iterator[tuple[str, Union[PartialLintCallable, DeferredRenderTask]]]:
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
        for fname, partial in self.iter_partials(fnames, fix=fix):
            try:
                if isinstance(partial, DeferredRenderTask):  # pragma: no cover
                    # DeferredRenderTask is normally only emitted by
                    # ParallelRunner.iter_partials.  Handle it here as a
                    # safety net: render + lint in one step in the main process.
                    rendered = self.linter.render_file(
                        partial.fname, partial.root_config
                    )
                    rule_pack = self.linter.get_rulepack(config=rendered.config)
                    yield self.linter.lint_rendered(
                        rendered, rule_pack, partial.fix, self.linter.formatter
                    )
                else:
                    yield partial()
            except (bdb.BdbQuit, KeyboardInterrupt):  # pragma: no cover
                raise
            except Exception as e:
                self._handle_lint_path_exception(fname, e)


class ParallelRunner(BaseRunner):
    """Base class for parallel runner implementations (process or thread)."""

    POOL_TYPE: Callable[..., multiprocessing.pool.Pool]
    # Don't pass the formatter in a parallel world, they
    # don't pickle well.
    pass_formatter = False

    def __init__(self, linter: Linter, config: FluffConfig, processes: int) -> None:
        super().__init__(linter, config)
        self.processes = processes

    def iter_partials(
        self,
        fnames: list[str],
        fix: bool = False,
    ) -> Iterator[tuple[str, Union[PartialLintCallable, DeferredRenderTask]]]:
        """Iterate through partials or deferred tasks for parallel linting.

        When the active templater supports worker-side rendering
        (``templates_in_worker = True``), we emit a lightweight
        ``DeferredRenderTask`` containing only the filename and root config.
        The worker process calls ``render_file`` itself, keeping the full
        ``RenderedFile`` off the IPC boundary.

        For templaters that require main-process state (e.g. dbt), we fall
        back to the base-class behaviour and template in the main process.
        """
        if self.linter.templater.templates_in_worker:
            for fname in self.linter.templater.sequence_files(
                fnames, config=self.config, formatter=None
            ):
                yield fname, DeferredRenderTask(fname, self.config, fix)
        else:
            yield from super().iter_partials(fnames, fix=fix)

    def run(self, fnames: list[str], fix: bool) -> Iterator[LintedFile]:
        """Parallel implementation.

        Note that the partials are generated one at a time then
        passed directly into the pool as they're ready. This means
        the main thread can do the IO work while passing the parsing
        and linting work out to the threads.
        """
        with self._create_pool(
            self.processes,
            self._init_global,
            initargs=(),
        ) as pool:
            try:
                for lint_result in self._map(
                    pool,
                    self._apply,
                    self.iter_partials(fnames, fix=fix),
                ):
                    handled = self._handle_result(lint_result, fix)
                    if handled is not None:
                        yield handled
            except KeyboardInterrupt:  # pragma: no cover
                # On keyboard interrupt (Ctrl-C), terminate the workers.
                # Notify the user we've received the signal and are cleaning up,
                # in case it takes awhile.
                print("Received keyboard interrupt. Cleaning up and shutting down...")
                pool.terminate()

    @staticmethod
    def _apply(
        partial_tuple: tuple[str, Union[PartialLintCallable, DeferredRenderTask]],
    ) -> Union["DelayedException", LintedFile]:
        """Shim function used in parallel mode."""
        fname, task = partial_tuple
        try:
            if isinstance(task, DeferredRenderTask):
                # Worker-side rendering: reconstruct a Linter from the root
                # config and do render + lint in one step, keeping the full
                # RenderedFile off the IPC boundary.
                linter = Linter(config=task.root_config)
                # FluffConfig.__getstate__ strips templater_obj to None before
                # pickling (it's designed for main-process use only). Since we
                # are deliberately rendering here in the worker, re-instantiate
                # the templater from the config's templater name.
                linter.templater = task.root_config.get_templater()
                rendered = linter.render_file(task.fname, task.root_config)
                rule_pack = linter.get_rulepack(config=rendered.config)
                return Linter.lint_rendered(rendered, rule_pack, task.fix, None)
            return task()
        # Capture any exceptions and return as delayed exception to handle
        # in the main thread.
        except Exception as e:
            return DelayedException(e, fname=fname)

    def _handle_result(
        self,
        lint_result: Union["DelayedException", LintedFile],
        fix: bool,
    ) -> Optional[LintedFile]:
        """Process a single lint result, handling errors and formatting.

        Returns the LintedFile on success, None on error/skip.
        """
        if isinstance(lint_result, DelayedException):
            if isinstance(lint_result.ee, SQLFluffSkipFile):
                linter_logger.warning(str(lint_result.ee))
            else:
                try:
                    lint_result.reraise()
                except Exception as e:
                    self._handle_lint_path_exception(lint_result.fname, e)
            return None
        if self.linter.formatter:
            self.linter.formatter.dispatch_file_violations(
                lint_result.path,
                lint_result,
                only_fixable=fix,
                warn_unused_ignores=self.linter.config.get("warn_unused_ignores"),
            )
        return lint_result

    @classmethod
    def _init_global(cls) -> None:  # pragma: no cover
        """For the parallel runners indicate that we're not in the main thread."""
        is_main_process.set(False)
        super()._init_global()

    @classmethod
    def _create_pool(
        cls,
        processes: int,
        initializer: Callable[..., None],
        initargs: tuple[Any, ...] = (),
    ) -> multiprocessing.pool.Pool:
        return cls.POOL_TYPE(
            processes=processes, initializer=initializer, initargs=initargs
        )

    @classmethod
    @abstractmethod
    def _map(
        cls,
        pool: multiprocessing.pool.Pool,
        func: Callable[
            [tuple[str, Union[PartialLintCallable, DeferredRenderTask]]],
            Union["DelayedException", LintedFile],
        ],
        iterable: Iterable[tuple[str, Union[PartialLintCallable, DeferredRenderTask]]],
    ) -> Iterable[Union["DelayedException", LintedFile]]:  # pragma: no cover
        """Class-specific map method.

        NOTE: Must be overridden by an implementation.
        """
        ...


class MultiProcessRunner(ParallelRunner):
    """Runner that does parallel processing using multiple processes.

    Uses the pipelined approach: main process templates files sequentially,
    workers lint them in parallel. For templaters that support warm workers,
    use WarmWorkerRunner instead (selected automatically by get_runner).
    """

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
            [tuple[str, Union[PartialLintCallable, DeferredRenderTask]]],
            Union["DelayedException", LintedFile],
        ],
        iterable: Iterable[tuple[str, Union[PartialLintCallable, DeferredRenderTask]]],
    ) -> Iterable[Union["DelayedException", LintedFile]]:
        """Map using imap unordered.

        We use this so we can iterate through results as they arrive, and while other
        files are still being processed.
        """
        return pool.imap_unordered(  # pragma: no cover
            func=func, iterable=iterable
        )


class WarmWorkerRunner(MultiProcessRunner):
    """Runner using a persistent process pool with pre-warmed workers.

    Workers pre-import heavy modules during pool creation (overlapped
    with main-process compilation), then receive init data once and
    cache templater state across tasks. The pool persists across
    lint_paths() calls via storage on the templater instance.

    Selected automatically by get_runner() when the templater sets
    ``supports_warm_workers = True`` and implements the warm worker
    protocol (see RawTemplater docstring in base.py).

    Performance characteristics (200-model dbt project):
    - Cold start: pool init overlapped with manifest compile (~2.2s hidden)
    - Warm reuse: 3-4.5x speedup with 4-8 processes
    - Lightweight IPC: ~100 bytes per task (no FluffConfig per file)
    """

    def run(
        self, fnames: list[str], fix: bool
    ) -> Iterator[LintedFile]:  # pragma: no cover
        """Warm worker implementation with persistent pool."""
        import time

        # Cast is safe: _use_warm_workers() in get_runner verified attrs.
        templater: Any = self.linter.templater

        t_start = time.perf_counter()

        # Step 1: Ensure templater config is compiled (fast, needed for
        # adapter type before pool creation).
        if hasattr(templater, "prepare_warm_worker_state"):
            templater.prepare_warm_worker_state(self.config, phase="config")

        # Step 2: Check if we can reuse the persistent pool.
        pool = templater._warm_pool
        pool_is_new = False

        if pool is None or templater._warm_pool_processes != self.processes:
            # Create a new persistent pool.
            if pool is not None:
                pool.terminate()
                pool.join()

            init_modules = self._get_init_modules(templater)
            config_bytes = templater.get_worker_config_bytes()
            setup_ref = self._get_setup_func_ref(templater)

            t_config = time.perf_counter()
            _warm_worker_log(
                f"main: creating persistent pool ({self.processes} workers), "
                f"config in {t_config - t_start:.3f}s"
            )

            pool = self.POOL_TYPE(
                processes=self.processes,
                initializer=_warm_worker_initializer,
                initargs=(init_modules, config_bytes, *setup_ref),
            )
            templater._warm_pool = pool
            templater._warm_pool_processes = self.processes
            pool_is_new = True

            t_pool = time.perf_counter()
            _warm_worker_log(
                f"main: pool created in {t_pool - t_config:.3f}s, compiling manifest..."
            )

        # Step 3: Ensure manifest/project state is compiled (overlapped
        # with pool init on first call, instant on subsequent calls).
        if hasattr(templater, "prepare_warm_worker_state"):
            templater.prepare_warm_worker_state(self.config, phase="manifest")

        t_manifest = time.perf_counter()

        # Steps 4-6 are wrapped in try/except so that any failure
        # (broadcast hang, worker crash, etc.) terminates the pool
        # and cleans up shared memory, ensuring the next call starts
        # fresh rather than reusing a broken pool.
        try:
            # Step 4: Broadcast init data if config/manifest changed.
            state_changed = not pool_is_new and (
                getattr(templater, "_warm_pool_config", None) is not self.config
                or self._get_manifest_id(templater) != templater._warm_pool_manifest_id
            )
            need_init_data = pool_is_new or state_changed

            if need_init_data:
                init_data = templater.get_worker_init_data(self.config)
                data_bytes = pickle.dumps(init_data)
                shm_size = len(data_bytes)

                if shm_size > 50 * 1024 * 1024:
                    linter_logger.warning(
                        f"Large warm worker init data "
                        f"({shm_size / 1024 / 1024:.1f} MB). "
                        f"Each of {self.processes} workers will cache "
                        f"this in memory."
                    )

                # Replace any existing shared memory block.
                old_shm = templater._warm_shm
                if old_shm is not None:
                    try:
                        old_shm.close()
                        old_shm.unlink()
                    except Exception:
                        pass

                shm = SharedMemory(create=True, size=shm_size)
                assert shm.buf is not None
                shm.buf[:shm_size] = data_bytes
                templater._warm_shm = shm
                templater._warm_shm_size = shm_size

                templater._warm_pool_manifest_id = self._get_manifest_id(templater)
                templater._warm_pool_config = self.config
                _warm_worker_log(
                    f"main: init data ({shm_size / 1024:.1f} KB) "
                    f"written to shared memory '{shm.name}', "
                    f"setup {t_manifest - t_start:.3f}s"
                )

                # Broadcast init data to all workers with a timeout
                # so a hung worker doesn't block the main process
                # forever. Workers are ready after this returns.
                _warm_worker_log("main: broadcasting init data to all workers")
                pool.map_async(
                    _warm_worker_receive_init,
                    [(shm.name, shm_size)] * self.processes,
                ).get(timeout=60)
            else:
                _warm_worker_log(
                    f"main: reusing pool + manifest, setup {t_manifest - t_start:.3f}s"
                )

            # Step 5: Materialize file list and apply LPT scheduling.
            file_list = list(
                templater.sequence_files(fnames, config=self.config, formatter=None)
            )
            file_list = self._lpt_sort_files(file_list)

            if file_list:
                _warm_worker_log(
                    f"main: dispatching {len(file_list)} files "
                    f"(largest={os.path.getsize(file_list[0])}B, "
                    f"smallest={os.path.getsize(file_list[-1])}B)"
                )

            # Step 6: Dispatch tasks and collect results.
            t_dispatch = time.perf_counter()
            shm_ref = (
                templater._warm_shm.name,
                templater._warm_shm_size,
            )
            task_iter = ((fname, fix, shm_ref) for fname in file_list)
            yield from self._dispatch_and_collect(pool, task_iter, fix)

        except KeyboardInterrupt:  # pragma: no cover
            print("Received keyboard interrupt. Cleaning up and shutting down...")
            self._terminate_pool(templater)
        except Exception:
            # Terminate pool on any error so next call starts fresh.
            self._terminate_pool(templater)
            raise
        else:
            _warm_worker_log(
                f"main: {len(file_list)} files completed in "
                f"{time.perf_counter() - t_dispatch:.3f}s"
            )

    def _dispatch_and_collect(
        self,
        pool: multiprocessing.pool.Pool,
        task_iter: Iterable[tuple[str, bool, tuple[str, int]]],
        fix: bool,
    ) -> Iterator[LintedFile]:
        """Send tasks to pool and yield results, handling errors."""
        for lint_result in pool.imap_unordered(
            func=_warm_worker_apply, iterable=task_iter
        ):
            handled = self._handle_result(lint_result, fix)
            if handled is not None:
                yield handled

    @staticmethod
    def _terminate_pool(templater: Any) -> None:
        """Terminate pool and shared memory, resetting templater state.

        Called on any error to ensure the next lint_paths() call
        starts with a fresh pool rather than reusing a broken one.

        Uses a join timeout to prevent deadlock if a worker is stuck
        in a C extension (pickle, Jinja) and doesn't respond to
        SIGTERM from pool.terminate().
        """
        pool = getattr(templater, "_warm_pool", None)
        if pool is not None:
            try:
                pool.terminate()
                pool.join(timeout=5)
            except Exception:
                pass
            templater._warm_pool = None
        shm = getattr(templater, "_warm_shm", None)
        if shm is not None:
            try:
                shm.close()
                shm.unlink()
            except Exception:
                pass
            templater._warm_shm = None

    @staticmethod
    def _lpt_sort_files(fnames: list[str]) -> list[str]:
        """Sort files by size descending (LPT scheduling).

        Largest files are dispatched first so heavy work starts early
        and all workers finish at similar times. Uses stable sort to
        preserve relative ordering from sequence_files for equal-size
        files (important for dbt ephemeral model dependencies).
        """
        return sorted(fnames, key=lambda f: os.path.getsize(f), reverse=True)

    @staticmethod
    def _get_init_modules(templater: Any) -> list[str]:
        """Get the list of modules to pre-import in warm workers."""
        if hasattr(templater, "get_warm_worker_init_modules"):
            result: list[str] = templater.get_warm_worker_init_modules()
            return result
        # Fallback to legacy single-module methods.
        modules: list[str] = [templater.get_warm_worker_module()]
        if hasattr(templater, "get_warm_worker_adapter_module"):
            adapter = templater.get_warm_worker_adapter_module()
            if adapter:
                modules.append(adapter)
        return modules

    @staticmethod
    def _get_setup_func_ref(
        templater: Any,
    ) -> tuple[Optional[str], Optional[str]]:
        """Get the (module, function_name) for worker setup."""
        if hasattr(templater, "get_warm_worker_setup_func"):
            ref: tuple[Optional[str], Optional[str]] = (
                templater.get_warm_worker_setup_func()
            )
            return ref
        return (None, None)

    @staticmethod
    def _get_manifest_id(templater: Any) -> Optional[int]:
        """Get an identity marker for the templater's compiled state."""
        for attr in ("dbt_manifest", "_compiled_state"):
            obj = templater.__dict__.get(attr)
            if obj is not None:
                return id(obj)
        return None


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
            [tuple[str, Union[PartialLintCallable, DeferredRenderTask]]],
            Union["DelayedException", LintedFile],
        ],
        iterable: Iterable[tuple[str, Union[PartialLintCallable, DeferredRenderTask]]],
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


def _use_warm_workers(templater: Any) -> bool:
    """Check if a templater supports the warm worker protocol.

    Returns True when the templater has opted in via
    ``supports_warm_workers = True`` and provides the required methods.
    Any templater can opt in regardless of ``templates_in_worker`` —
    WarmWorkerRunner bypasses iter_partials entirely.
    """
    return (
        getattr(templater, "supports_warm_workers", False)
        and hasattr(templater, "get_worker_init_data")
        and hasattr(templater, "get_worker_config_bytes")
    )


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
            if _use_warm_workers(linter.templater):
                return (
                    WarmWorkerRunner(linter, config, processes=processes),
                    processes,
                )
            return MultiProcessRunner(linter, config, processes=processes), processes
        else:
            return MultiThreadRunner(linter, config, processes=processes), processes
    else:
        return SequentialRunner(linter, config), processes
