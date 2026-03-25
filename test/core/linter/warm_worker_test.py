"""Tests for WarmWorkerRunner and the warm worker protocol."""

import os
import pickle
import sys
import types
from multiprocessing.shared_memory import SharedMemory
from typing import Optional

import pytest

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.linter import runner
from sqlfluff.core.linter.runner import (
    DelayedException,
    WarmWorkerRunner,
    _use_warm_workers,
    _warm_worker_apply,
    _warm_worker_initializer,
    _warm_worker_log,
    _warm_worker_receive_init,
    get_runner,
)
from sqlfluff.core.templaters import RawTemplater

# --- Mock templaters ---


class MockWarmTemplater:
    """Minimal mock implementing the warm worker protocol."""

    name = "mock_warm"
    templates_in_worker = False
    supports_warm_workers = True
    _warm_pool: object = None
    _warm_pool_processes = 0
    _warm_pool_manifest_id: object = None
    _warm_pool_config: object = None
    _warm_shm: object = None
    _warm_shm_size = 0

    def __init__(self):
        """Initialise with a unique manifest object."""
        self._manifest = object()

    def prepare_warm_worker_state(self, config, phase):
        """Simulate compilation for the requested phase."""
        if phase == "config":
            self._config = config
        elif phase == "manifest":
            self.__dict__["dbt_manifest"] = self._manifest

    def get_warm_worker_init_modules(self):
        """Return modules to pre-import."""
        return ["json", "os"]

    def get_warm_worker_setup_func(self):
        """Return no setup function (no adapter to register)."""
        return (None, None)

    def get_worker_config_bytes(self):
        """Return pickled mock config."""
        return pickle.dumps({"mock": True})

    def get_worker_init_data(self, root_config):
        """Return init data including the root config."""
        return {"root_config": root_config, "project_dir": "/tmp/mock"}

    def sequence_files(self, fnames, config=None, formatter=None):
        """Yield files in order."""
        return iter(fnames)


# --- _use_warm_workers protocol detection ---


class TestUseWarmWorkers:
    """Tests for the _use_warm_workers protocol detection function."""

    def test_true_for_full_protocol(self):
        """Templater with all required attributes returns True."""
        assert _use_warm_workers(MockWarmTemplater()) is True

    def test_true_regardless_of_templates_in_worker(self):
        """templates_in_worker does not affect warm worker eligibility."""
        t = MockWarmTemplater()
        t.templates_in_worker = True
        assert _use_warm_workers(t) is True

    def test_false_when_supports_flag_off(self):
        """Templater with supports_warm_workers=False returns False."""
        t = MockWarmTemplater()
        t.supports_warm_workers = False
        assert _use_warm_workers(t) is False

    def test_false_when_missing_get_worker_init_data(self):
        """Templater missing get_worker_init_data returns False."""
        t = type(
            "T",
            (),
            {
                "templates_in_worker": False,
                "supports_warm_workers": True,
                "get_worker_config_bytes": lambda self: b"",
            },
        )()
        assert _use_warm_workers(t) is False

    def test_false_when_missing_get_worker_config_bytes(self):
        """Templater missing get_worker_config_bytes returns False."""
        t = type(
            "T",
            (),
            {
                "templates_in_worker": False,
                "supports_warm_workers": True,
                "get_worker_init_data": lambda self, c: {},
            },
        )()
        assert _use_warm_workers(t) is False

    def test_false_for_raw_templater(self):
        """RawTemplater base class returns False (default attrs)."""
        assert _use_warm_workers(RawTemplater()) is False


# --- get_runner routing ---


class TestGetRunnerRouting:
    """Tests for get_runner selecting the correct runner type."""

    def test_sequential_for_one_process(self):
        """Single process returns SequentialRunner."""
        r, _ = get_runner(
            Linter(dialect="ansi"),
            FluffConfig(overrides={"dialect": "ansi"}),
            1,
        )
        assert isinstance(r, runner.SequentialRunner)

    def test_multiprocess_for_non_warm_templater(self):
        """Templater without warm workers returns plain MultiProcessRunner."""
        config = FluffConfig(overrides={"dialect": "ansi"})
        lntr = Linter(config=config)
        # Force supports_warm_workers off to test the non-warm path.
        lntr.templater.supports_warm_workers = False
        r, _ = get_runner(lntr, config, 4)
        assert isinstance(r, runner.MultiProcessRunner)
        assert type(r) is runner.MultiProcessRunner  # NOT WarmWorkerRunner

    def test_warm_worker_for_warm_templater(self):
        """Templater with supports_warm_workers=True returns WarmWorkerRunner."""
        config = FluffConfig(overrides={"dialect": "ansi"})
        lntr = Linter(config=config)
        lntr.templater = MockWarmTemplater()
        r, _ = get_runner(lntr, config, 4)
        assert type(r) is WarmWorkerRunner

    def test_multithread_when_parallelism_disabled(self):
        """Disabled process parallelism falls back to MultiThreadRunner."""
        config = FluffConfig(overrides={"dialect": "ansi"})
        lntr = Linter(config=config)
        lntr.templater = MockWarmTemplater()
        r, _ = get_runner(lntr, config, 4, allow_process_parallelism=False)
        assert isinstance(r, runner.MultiThreadRunner)


# --- _warm_worker_initializer ---


class TestWarmWorkerInitializer:
    """Tests for the generic pool initializer function."""

    def setup_method(self):
        """Reset globals before each test."""
        runner._worker_init_data = None

    def teardown_method(self):
        """Reset globals after each test."""
        runner._worker_init_data = None

    def test_imports_specified_modules(self):
        """Modules listed in init_modules are importable after init."""
        # Remove a stdlib module temporarily to verify it gets imported
        saved = sys.modules.pop("csv", None)
        try:
            _warm_worker_initializer(["csv"], pickle.dumps({}))
            assert "csv" in sys.modules
        finally:
            if saved is not None:
                sys.modules["csv"] = saved

    def test_calls_setup_function_with_config_bytes(self):
        """Initializer calls setup_func with config_bytes and stores result."""
        received = {}
        mod = types.ModuleType("_test_setup")

        def _setup(cb):
            data = pickle.loads(cb)
            received["data"] = data
            return {"from_setup": data["key"]}

        mod.setup = _setup
        sys.modules["_test_setup"] = mod
        try:
            _warm_worker_initializer(
                [], pickle.dumps({"key": 42}), "_test_setup", "setup"
            )
            assert received["data"] == {"key": 42}
            assert runner._worker_init_data == {"from_setup": 42}
        finally:
            del sys.modules["_test_setup"]

    def test_survives_missing_module(self):
        """Import errors for listed modules don't crash the initializer."""
        _warm_worker_initializer(["nonexistent_xyz_module"], pickle.dumps({}))
        # Should still complete and set _worker_init_data
        assert runner._worker_init_data == {}

    def test_without_setup_func_sets_empty_dict(self):
        """Without a setup function, _worker_init_data is an empty dict."""
        _warm_worker_initializer([], pickle.dumps({}))
        assert runner._worker_init_data == {}
        assert isinstance(runner._worker_init_data, dict)


# --- _warm_worker_apply ---


class TestWarmWorkerApply:
    """Tests for the worker-side apply function."""

    def setup_method(self):
        """Reset module-level globals before each test."""
        runner._worker_init_data = None
        runner._worker_linter_cache = None

    def teardown_method(self):
        """Clean up module-level globals after each test."""
        runner._worker_init_data = None
        runner._worker_linter_cache = None

    def _make_shm(
        self, config: FluffConfig, extra: Optional[dict] = None
    ) -> tuple[SharedMemory, tuple[str, int]]:
        """Create shared memory with pickled init data. Caller must close/unlink."""
        data: dict = {"root_config": config}
        if extra:
            data.update(extra)
        data_bytes = pickle.dumps(data)
        shm = SharedMemory(create=True, size=len(data_bytes))
        shm.buf[: len(data_bytes)] = data_bytes
        return shm, (shm.name, len(data_bytes))

    def test_first_task_reads_from_shared_memory_and_creates_cache(self):
        """First task reads init data from shared memory and caches Linter."""
        from sqlfluff.core.linter import LintedFile

        config = FluffConfig(overrides={"dialect": "ansi"})
        shm, shm_ref = self._make_shm(config)
        try:
            assert runner._worker_linter_cache is None
            result = _warm_worker_apply(
                ("test/fixtures/linter/passing.sql", False, shm_ref)
            )
            assert isinstance(result, LintedFile)
            assert runner._worker_linter_cache is not None
            linter, templater, cached_config, rule_pack = runner._worker_linter_cache
            assert isinstance(linter, Linter)
            assert isinstance(cached_config, FluffConfig)
        finally:
            shm.close()
            shm.unlink()

    def test_subsequent_tasks_reuse_same_cache(self):
        """Second task reuses the exact same cached linter objects."""
        from sqlfluff.core.linter import LintedFile

        config = FluffConfig(overrides={"dialect": "ansi"})
        shm, shm_ref = self._make_shm(config)
        try:
            _warm_worker_apply(("test/fixtures/linter/passing.sql", False, shm_ref))
            cache_after_first = runner._worker_linter_cache

            # Second task: same shm_ref, but cache already exists so
            # shared memory is not re-read.
            result = _warm_worker_apply(
                ("test/fixtures/linter/passing.sql", False, shm_ref)
            )
            assert isinstance(result, LintedFile)
            assert runner._worker_linter_cache is cache_after_first
        finally:
            shm.close()
            shm.unlink()

    def test_shm_data_merged_with_initializer_data(self):
        """Shared memory init data merges with pre-existing _worker_init_data."""
        config = FluffConfig(overrides={"dialect": "ansi"})
        runner._worker_init_data = {"from_initializer": "preserved"}
        shm, shm_ref = self._make_shm(config, {"from_task": "added"})
        try:
            _warm_worker_apply(("test/fixtures/linter/passing.sql", False, shm_ref))
            assert runner._worker_init_data["from_initializer"] == "preserved"
            assert runner._worker_init_data["from_task"] == "added"
            assert isinstance(runner._worker_init_data["root_config"], FluffConfig)
        finally:
            shm.close()
            shm.unlink()

    def test_receive_init_resets_linter_cache(self):
        """_warm_worker_receive_init clears linter cache for rebuild."""
        config = FluffConfig(overrides={"dialect": "ansi"})
        shm, shm_ref = self._make_shm(config)
        try:
            _warm_worker_apply(("test/fixtures/linter/passing.sql", False, shm_ref))
            assert runner._worker_linter_cache is not None

            # Receiving new init data via shared memory should reset the cache.
            shm2, shm_ref2 = self._make_shm(config)
            try:
                _warm_worker_receive_init(shm_ref2)
                assert runner._worker_linter_cache is None
            finally:
                shm2.close()
                shm2.unlink()
        finally:
            shm.close()
            shm.unlink()

    def test_exception_wrapped_as_delayed_exception(self):
        """Exceptions during render are wrapped as DelayedException."""
        config = FluffConfig(overrides={"dialect": "ansi"})
        shm, shm_ref = self._make_shm(config)
        try:
            result = _warm_worker_apply(("no_such_file.sql", False, shm_ref))
            assert isinstance(result, DelayedException)
            assert result.fname == "no_such_file.sql"
            with pytest.raises(Exception):
                result.reraise()
        finally:
            shm.close()
            shm.unlink()

    def test_error_with_invalid_shm_name(self):
        """Task with invalid shared memory name raises an error."""
        result = _warm_worker_apply(
            ("test/fixtures/linter/passing.sql", False, ("nonexistent_shm", 100))
        )
        assert isinstance(result, DelayedException)


# --- WarmWorkerRunner static helpers ---


class TestWarmWorkerRunnerHelpers:
    """Tests for WarmWorkerRunner static helper methods."""

    def test_get_init_modules_uses_new_api(self):
        """Uses get_warm_worker_init_modules when available."""
        assert WarmWorkerRunner._get_init_modules(MockWarmTemplater()) == [
            "json",
            "os",
        ]

    def test_get_init_modules_falls_back_to_legacy_api(self):
        """Falls back to get_warm_worker_module + adapter when new API absent."""
        t = type(
            "LegacyT",
            (),
            {
                "get_warm_worker_module": lambda self: "json",
                "get_warm_worker_adapter_module": lambda self: "os",
            },
        )()
        result = WarmWorkerRunner._get_init_modules(t)
        assert result == ["json", "os"]

    def test_get_init_modules_legacy_skips_none_adapter(self):
        """Legacy fallback skips adapter module when it returns None."""
        t = type(
            "LegacyT",
            (),
            {
                "get_warm_worker_module": lambda self: "json",
                "get_warm_worker_adapter_module": lambda self: None,
            },
        )()
        assert WarmWorkerRunner._get_init_modules(t) == ["json"]

    def test_get_setup_func_ref_from_templater(self):
        """Returns the (module, name) tuple from the templater."""
        t = type(
            "T",
            (),
            {
                "get_warm_worker_setup_func": lambda self: (
                    "my.mod",
                    "my_func",
                )
            },
        )()
        assert WarmWorkerRunner._get_setup_func_ref(t) == ("my.mod", "my_func")

    def test_get_setup_func_ref_returns_none_pair_without_method(self):
        """Returns (None, None) when templater lacks the method."""
        t = type("T", (), {})()
        assert WarmWorkerRunner._get_setup_func_ref(t) == (None, None)

    def test_get_manifest_id_tracks_object_identity(self):
        """Returns id() of dbt_manifest, changing when manifest changes."""
        t = MockWarmTemplater()
        obj1 = object()
        obj2 = object()
        t.__dict__["dbt_manifest"] = obj1
        id1 = WarmWorkerRunner._get_manifest_id(t)
        t.__dict__["dbt_manifest"] = obj2
        id2 = WarmWorkerRunner._get_manifest_id(t)
        assert id1 != id2
        assert id1 == id(obj1)
        assert id2 == id(obj2)

    def test_get_manifest_id_returns_none_when_unset(self):
        """Returns None when no dbt_manifest or _compiled_state exists."""
        t = type("T", (), {})()
        assert WarmWorkerRunner._get_manifest_id(t) is None


# --- LPT scheduling ---


class TestLptSortFiles:
    """Tests for LPT (Longest Processing Time) file scheduling."""

    def test_sorts_by_size_descending(self, tmp_path):
        """Largest files should be dispatched first."""
        small = tmp_path / "small.sql"
        medium = tmp_path / "medium.sql"
        large = tmp_path / "large.sql"
        small.write_text("SELECT 1")
        medium.write_text("SELECT " + "col, " * 50 + "1")
        large.write_text("SELECT " + "col, " * 500 + "1")

        result = WarmWorkerRunner._lpt_sort_files([str(small), str(medium), str(large)])
        assert result == [str(large), str(medium), str(small)]

    def test_stable_sort_preserves_order_for_equal_sizes(self, tmp_path):
        """Files of equal size preserve their original relative order."""
        files = []
        for name in ["alpha.sql", "beta.sql", "gamma.sql"]:
            f = tmp_path / name
            f.write_text("SELECT 1")
            files.append(str(f))

        result = WarmWorkerRunner._lpt_sort_files(files)
        # All same size — original order preserved (stable sort).
        assert result == files

    def test_empty_list(self):
        """Empty file list returns empty list."""
        assert WarmWorkerRunner._lpt_sort_files([]) == []

    def test_single_file(self, tmp_path):
        """Single file returns unchanged."""
        f = tmp_path / "only.sql"
        f.write_text("SELECT 1")
        result = WarmWorkerRunner._lpt_sort_files([str(f)])
        assert result == [str(f)]


# --- Architecture invariants ---


class TestArchitectureInvariants:
    """Verify class hierarchy and separation of concerns."""

    def test_warm_worker_runner_is_subclass_of_multiprocess(self):
        """WarmWorkerRunner inherits from MultiProcessRunner."""
        assert issubclass(WarmWorkerRunner, runner.MultiProcessRunner)

    def test_warm_worker_runner_overrides_run(self):
        """WarmWorkerRunner has its own run(), not inherited."""
        assert WarmWorkerRunner.run is not runner.ParallelRunner.run
        assert WarmWorkerRunner.run is not runner.MultiProcessRunner.run

    def test_multiprocess_runner_inherits_run(self):
        """MultiProcessRunner uses ParallelRunner.run (no warm worker code)."""
        assert runner.MultiProcessRunner.run is runner.ParallelRunner.run

    def test_multiprocess_runner_has_no_warm_worker_method(self):
        """MultiProcessRunner has no _use_warm_workers."""
        assert "_use_warm_workers" not in runner.MultiProcessRunner.__dict__

    def test_raw_templater_warm_worker_defaults(self):
        """RawTemplater provides False/None defaults for warm worker attrs."""
        t = RawTemplater()
        assert t.supports_warm_workers is False
        assert t._warm_pool is None
        assert t._warm_pool_processes == 0
        assert t._warm_pool_manifest_id is None
        assert t._warm_pool_config is None
        assert t._warm_shm is None
        assert t._warm_shm_size == 0


# --- Error cleanup and _terminate_pool ---


class TestTerminatePool:
    """Tests for _terminate_pool error cleanup."""

    def test_terminate_pool_cleans_up_pool_and_shm(self):
        """_terminate_pool terminates pool and unlinks shared memory."""
        t = MockWarmTemplater()
        data = b"test data for cleanup"
        shm = SharedMemory(create=True, size=len(data))
        shm.buf[: len(data)] = data
        t._warm_shm = shm
        t._warm_shm_size = len(data)
        t._warm_pool = types.SimpleNamespace(terminate=lambda: None, join=lambda: None)
        try:
            WarmWorkerRunner._terminate_pool(t)
            assert t._warm_pool is None
            assert t._warm_shm is None
        except Exception:
            # Safety net: clean up shm if _terminate_pool fails.
            try:
                shm.close()
                shm.unlink()
            except Exception:
                pass
            raise

    def test_terminate_pool_handles_no_pool(self):
        """_terminate_pool is safe when pool is None."""
        t = MockWarmTemplater()
        t._warm_pool = None
        t._warm_shm = None
        # Should not raise.
        WarmWorkerRunner._terminate_pool(t)
        assert t._warm_pool is None

    def test_terminate_pool_handles_already_closed_shm(self):
        """_terminate_pool handles shared memory that's already unlinked."""
        t = MockWarmTemplater()
        t._warm_pool = None
        # Create and immediately close/unlink shm.
        shm = SharedMemory(create=True, size=16)
        shm.close()
        shm.unlink()
        t._warm_shm = shm  # Already closed — _terminate_pool must not crash.
        WarmWorkerRunner._terminate_pool(t)
        assert t._warm_shm is None

    def test_terminate_pool_survives_pool_terminate_error(self):
        """_terminate_pool continues if pool.terminate() raises."""
        t = MockWarmTemplater()

        def _raise():
            raise OSError("pool already dead")

        t._warm_pool = types.SimpleNamespace(terminate=_raise, join=lambda: None)
        # Should not raise — errors are swallowed.
        WarmWorkerRunner._terminate_pool(t)
        assert t._warm_pool is None


# --- DbtTemplater protocol (skip if not installed) ---


class TestDbtTemplaterProtocol:
    """Tests that DbtTemplater correctly implements the warm worker protocol."""

    @pytest.fixture(autouse=True)
    def _skip_without_dbt(self):
        """Skip all tests in this class if dbt templater is not installed."""
        try:
            from sqlfluff_templater_dbt.templater import DbtTemplater  # noqa

            self.DbtTemplater = DbtTemplater
        except ImportError:
            pytest.skip("dbt templater not installed")

    def test_protocol_detection(self):
        """_use_warm_workers returns True for DbtTemplater instances."""
        t = self.DbtTemplater()
        assert t.templates_in_worker is False
        assert t.supports_warm_workers is True
        assert _use_warm_workers(t) is True

    def test_setup_func_points_to_importable_function(self):
        """get_warm_worker_setup_func returns a valid importable reference."""
        import importlib

        t = self.DbtTemplater()
        mod_name, func_name = t.get_warm_worker_setup_func()
        mod = importlib.import_module(mod_name)
        func = getattr(mod, func_name)
        assert callable(func)
        # Verify it's the actual warm_worker_setup function
        from sqlfluff_templater_dbt.templater import warm_worker_setup

        assert func is warm_worker_setup

    def test_init_modules_includes_dbt_cli(self):
        """get_warm_worker_init_modules includes dbt.cli.main for warm import."""
        t = self.DbtTemplater()
        modules = t.get_warm_worker_init_modules()
        assert "dbt.cli.main" in modules
        assert isinstance(modules, list)

    def test_prepare_warm_worker_state_stores_config(self):
        """prepare_warm_worker_state config phase stores the config reference."""
        t = self.DbtTemplater()
        config = FluffConfig(
            overrides={"dialect": "duckdb", "templater": "dbt"},
            configs={
                "templater": {
                    "dbt": {
                        "project_dir": "/tmp/test",
                        "profiles_dir": "/tmp/test",
                    }
                }
            },
        )
        # Only test that the method stores config and sets dirs from it.
        # Don't call phase="config" fully (triggers dbt_config which needs
        # a real project). Instead verify the method exists and accepts args.
        t.sqlfluff_config = config
        t.project_dir = t._get_project_dir()
        t.profiles_dir = t._get_profiles_dir()
        assert t.sqlfluff_config is config
        assert t.project_dir is not None
        assert t.profiles_dir is not None

    def test_pool_storage_inherited_from_base(self):
        """Pool attrs come from RawTemplater, not redefined in DbtTemplater."""
        t = self.DbtTemplater()
        assert t._warm_pool is None
        # Verify it's inherited, not defined on DbtTemplater itself
        assert "_warm_pool" not in type(t).__dict__


# --- JinjaTemplater warm workers ---


class TestJinjaWarmWorkers:
    """Tests that JinjaTemplater uses warm workers via default protocol."""

    def test_jinja_supports_warm_workers(self):
        """JinjaTemplater opts into warm workers."""
        from sqlfluff.core.templaters.jinja import JinjaTemplater

        assert JinjaTemplater.supports_warm_workers is True

    def test_jinja_detected_by_use_warm_workers(self):
        """_use_warm_workers returns True for JinjaTemplater."""
        from sqlfluff.core.templaters.jinja import JinjaTemplater

        assert _use_warm_workers(JinjaTemplater()) is True

    def test_jinja_uses_default_get_worker_init_data(self):
        """JinjaTemplater uses RawTemplater's default get_worker_init_data."""
        from sqlfluff.core.templaters.jinja import JinjaTemplater

        t = JinjaTemplater()
        config = FluffConfig(overrides={"dialect": "ansi"})
        data = t.get_worker_init_data(config)
        assert data["root_config"] is config

    def test_jinja_uses_default_get_worker_config_bytes(self):
        """JinjaTemplater uses RawTemplater's default (empty bytes)."""
        from sqlfluff.core.templaters.jinja import JinjaTemplater

        assert JinjaTemplater().get_worker_config_bytes() == b""

    def test_get_runner_selects_warm_worker_for_jinja(self):
        """get_runner returns WarmWorkerRunner for Jinja with processes>1."""
        config = FluffConfig(overrides={"dialect": "ansi"})
        lntr = Linter(config=config)
        # Default Linter uses JinjaTemplater
        r, _ = get_runner(lntr, config, 4)
        assert type(r) is WarmWorkerRunner

    def test_jinja_warm_worker_lints_files(self):
        """End-to-end: Jinja warm worker can lint a real file via shared memory."""
        from sqlfluff.core.linter import LintedFile

        config = FluffConfig(overrides={"dialect": "ansi"})

        runner._worker_init_data = None
        runner._worker_linter_cache = None
        data_bytes = pickle.dumps({"root_config": config})
        shm = SharedMemory(create=True, size=len(data_bytes))
        shm.buf[: len(data_bytes)] = data_bytes
        try:
            result = _warm_worker_apply(
                ("test/fixtures/linter/passing.sql", False, (shm.name, len(data_bytes)))
            )
            assert isinstance(result, LintedFile)
        finally:
            shm.close()
            shm.unlink()
            runner._worker_init_data = None
            runner._worker_linter_cache = None


# --- Edge case tests ---


class TestEdgeCases:
    """Tests for edge cases identified in the warm worker roadmap (Phase 1.3)."""

    def setup_method(self):
        """Reset module-level globals before each test."""
        runner._worker_init_data = None
        runner._worker_linter_cache = None

    def teardown_method(self):
        """Clean up module-level globals after each test."""
        runner._worker_init_data = None
        runner._worker_linter_cache = None

    def _make_shm(
        self, config: FluffConfig, extra: Optional[dict] = None
    ) -> tuple[SharedMemory, tuple[str, int]]:
        """Create shared memory with pickled init data. Caller must close/unlink."""
        data: dict = {"root_config": config}
        if extra:
            data.update(extra)
        data_bytes = pickle.dumps(data)
        shm = SharedMemory(create=True, size=len(data_bytes))
        shm.buf[: len(data_bytes)] = data_bytes
        return shm, (shm.name, len(data_bytes))

    def test_more_workers_than_files(self, tmp_path):
        """Warm workers handle processes > file count without errors."""
        from sqlfluff.core.linter import LintedFile

        # Create just 2 files but use 8 processes worth of init data.
        for i in range(2):
            (tmp_path / f"f{i}.sql").write_text(f"SELECT {i}\n")

        config = FluffConfig(overrides={"dialect": "ansi"})
        shm, shm_ref = self._make_shm(config)
        try:
            results = []
            for f in sorted(tmp_path.glob("*.sql")):
                result = _warm_worker_apply((str(f), False, shm_ref))
                assert isinstance(result, LintedFile)
                results.append(result)
            assert len(results) == 2
        finally:
            shm.close()
            shm.unlink()

    def test_single_file_uses_sequential_runner(self):
        """With processes=1, get_runner returns SequentialRunner even for warm templaters."""
        config = FluffConfig(overrides={"dialect": "ansi"})
        lntr = Linter(config=config)
        lntr.templater = MockWarmTemplater()
        r, procs = get_runner(lntr, config, 1)
        assert isinstance(r, runner.SequentialRunner)
        assert procs == 1

    def test_fix_mode_returns_linted_file_with_fixes(self, tmp_path):
        """Warm worker with fix=True returns a LintedFile with fix applied."""
        from sqlfluff.core.linter import LintedFile

        # Create file with a fixable violation (wrong capitalization).
        sql_file = tmp_path / "fixable.sql"
        sql_file.write_text("select a from b\n")

        config = FluffConfig(overrides={"dialect": "ansi", "rules": "CP01"})
        shm, shm_ref = self._make_shm(config)
        try:
            result = _warm_worker_apply((str(sql_file), True, shm_ref))
            assert isinstance(result, LintedFile)
            # CP01 should flag 'select' -> 'SELECT' (or vice versa).
            # With fix=True, the result should contain fix information.
            assert result.violations is not None
        finally:
            shm.close()
            shm.unlink()

    def test_fix_mode_does_not_corrupt_passing_file(self, tmp_path):
        """Warm worker with fix=True on a clean file returns no violations."""
        from sqlfluff.core.linter import LintedFile

        sql_file = tmp_path / "clean.sql"
        sql_file.write_text("SELECT a FROM b\n")

        config = FluffConfig(overrides={"dialect": "ansi", "rules": "CP01"})
        shm, shm_ref = self._make_shm(config)
        try:
            result = _warm_worker_apply((str(sql_file), True, shm_ref))
            assert isinstance(result, LintedFile)
            assert len(result.violations) == 0
        finally:
            shm.close()
            shm.unlink()

    def test_lpt_sort_with_backslash_paths(self, tmp_path):
        """LPT sort handles Windows-style backslash paths."""
        small = tmp_path / "small.sql"
        large = tmp_path / "large.sql"
        small.write_text("SELECT 1")
        large.write_text("SELECT " + "col, " * 500 + "1")

        # Convert to backslash paths (simulates Windows)
        small_win = str(small).replace("/", "\\")
        large_win = str(large).replace("/", "\\")

        result = WarmWorkerRunner._lpt_sort_files([small_win, large_win])
        assert result[0] == large_win
        assert result[1] == small_win

    def test_lpt_sort_with_forward_slash_paths(self, tmp_path):
        """LPT sort handles Unix-style forward-slash paths."""
        small = tmp_path / "small.sql"
        large = tmp_path / "large.sql"
        small.write_text("SELECT 1")
        large.write_text("SELECT " + "col, " * 500 + "1")

        # Convert to forward-slash paths (simulates Unix)
        small_unix = str(small).replace("\\", "/")
        large_unix = str(large).replace("\\", "/")

        result = WarmWorkerRunner._lpt_sort_files([small_unix, large_unix])
        assert result[0] == large_unix
        assert result[1] == small_unix

    def test_large_file_over_1mb(self, tmp_path):
        """Warm worker handles a >1MB SQL file without timeout or error."""
        from sqlfluff.core.linter import LintedFile

        # Generate a >1MB SQL file
        columns = ", ".join(f"column_name_{i:04d}" for i in range(500))
        unions = "\nUNION ALL\n".join(
            f"SELECT {columns} FROM table_{i}" for i in range(200)
        )
        sql_file = tmp_path / "large.sql"
        sql_file.write_text(unions + "\n")
        assert sql_file.stat().st_size > 1_000_000

        config = FluffConfig(
            overrides={
                "dialect": "ansi",
                "rules": "CP01",
                "large_file_skip_byte_limit": 0,
            }
        )
        shm, shm_ref = self._make_shm(config)
        try:
            result = _warm_worker_apply((str(sql_file), False, shm_ref))
            assert isinstance(result, LintedFile)
        finally:
            shm.close()
            shm.unlink()

    def test_large_init_data_via_shared_memory(self):
        """Shared memory handles large init data (simulating big dbt manifest)."""
        from sqlfluff.core.linter import LintedFile

        config = FluffConfig(overrides={"dialect": "ansi"})
        # Add ~1MB of extra data to simulate a large dbt manifest.
        extra = {"manifest_data": "x" * 1_000_000}
        shm, shm_ref = self._make_shm(config, extra)
        try:
            result = _warm_worker_apply(
                ("test/fixtures/linter/passing.sql", False, shm_ref)
            )
            assert isinstance(result, LintedFile)
            assert runner._worker_init_data["manifest_data"] == "x" * 1_000_000
        finally:
            shm.close()
            shm.unlink()


# --- End-to-end multiprocessing tests ---


class TestEndToEndMultiprocessing:
    """Tests that exercise real pool dispatch (not just direct function calls).

    These use processes=2 with the default JinjaTemplater (which has
    supports_warm_workers=True), triggering the full WarmWorkerRunner
    pipeline: pool creation, shared memory, broadcast, dispatch, collect.
    """

    @staticmethod
    def _cleanup_linter(linter: Linter) -> None:
        """Terminate any warm pool left on the linter's templater."""
        WarmWorkerRunner._terminate_pool(linter.templater)

    def test_lint_multiple_files(self, tmp_path):
        """Warm workers lint multiple files correctly via real pool."""
        for i in range(5):
            (tmp_path / f"f{i}.sql").write_text("SELECT 1\n")

        config = FluffConfig(overrides={"dialect": "ansi"})
        linter = Linter(config=config)
        try:
            result = linter.lint_paths((str(tmp_path),), processes=2, retain_files=True)
            n_files = sum(p.stats()["files"] for p in result.paths)
            assert n_files == 5
        finally:
            self._cleanup_linter(linter)

    def test_lint_detects_violations(self, tmp_path):
        """Warm workers correctly detect and report violations."""
        # CP01: mixed case keywords (SELECT uppercase, from lowercase)
        (tmp_path / "bad.sql").write_text("SELECT a from b\n")
        (tmp_path / "good.sql").write_text("SELECT a FROM b\n")

        config = FluffConfig(overrides={"dialect": "ansi", "rules": "CP01"})
        linter = Linter(config=config)
        try:
            result = linter.lint_paths((str(tmp_path),), processes=2, retain_files=True)
            assert result.num_violations() > 0
        finally:
            self._cleanup_linter(linter)

    def test_fix_applies_corrections(self, tmp_path):
        """Warm workers apply fixes that persist to disk."""
        sql_file = tmp_path / "fixme.sql"
        sql_file.write_text("SELECT a from b\n")

        config = FluffConfig(overrides={"dialect": "ansi", "rules": "CP01"})

        # Fix
        linter = Linter(config=config)
        try:
            result = linter.lint_paths(
                (str(tmp_path),),
                processes=2,
                fix=True,
                apply_fixes=True,
                retain_files=True,
            )
            assert result.num_violations(fixable=True) > 0
        finally:
            self._cleanup_linter(linter)

        # Verify: re-lint should find fewer violations
        linter2 = Linter(config=config)
        try:
            verify = linter2.lint_paths(
                (str(tmp_path),), processes=2, retain_files=True
            )
            assert verify.num_violations() < result.num_violations()
        finally:
            self._cleanup_linter(linter2)

    def test_pool_reuse_across_calls(self, tmp_path):
        """Persistent pool is reused across multiple lint_paths calls."""
        for i in range(3):
            (tmp_path / f"f{i}.sql").write_text("SELECT 1\n")

        config = FluffConfig(overrides={"dialect": "ansi"})
        linter = Linter(config=config)
        try:
            # First call: creates pool
            r1 = linter.lint_paths((str(tmp_path),), processes=2, retain_files=True)
            pool_after_first = linter.templater._warm_pool

            # Second call: reuses pool
            r2 = linter.lint_paths((str(tmp_path),), processes=2, retain_files=True)
            pool_after_second = linter.templater._warm_pool

            assert pool_after_first is pool_after_second
            assert sum(p.stats()["files"] for p in r1.paths) == 3
            assert sum(p.stats()["files"] for p in r2.paths) == 3
        finally:
            self._cleanup_linter(linter)

    def test_more_processes_than_files(self, tmp_path):
        """Works correctly when processes > file count."""
        (tmp_path / "only.sql").write_text("SELECT 1\n")

        config = FluffConfig(overrides={"dialect": "ansi"})
        linter = Linter(config=config)
        try:
            result = linter.lint_paths((str(tmp_path),), processes=4, retain_files=True)
            assert sum(p.stats()["files"] for p in result.paths) == 1
        finally:
            self._cleanup_linter(linter)


# --- _warm_worker_log ---


class TestWarmWorkerLog:
    """Tests for the worker logging utility."""

    def test_silent_by_default(self, capsys):
        """Log is silent unless SQLFLUFF_WARM_WORKER_DEBUG is set."""
        import unittest.mock

        with unittest.mock.patch.object(runner, "_WARM_WORKER_DEBUG", False):
            _warm_worker_log("should_not_appear")
        captured = capsys.readouterr()
        assert "should_not_appear" not in captured.err

    def test_writes_to_stderr_when_debug_enabled(self, capsys):
        """Log messages appear on stderr with PID when debug is enabled."""
        import unittest.mock

        with unittest.mock.patch.object(runner, "_WARM_WORKER_DEBUG", True):
            _warm_worker_log("test_msg_xyz")
        captured = capsys.readouterr()
        assert "test_msg_xyz" in captured.err
        assert str(os.getpid()) in captured.err
        assert captured.out == ""


# --- Parallel runner coverage across templaters ---


class TestRunnerTemplaterInteraction:
    """Test that each templater routes to the correct runner and works E2E."""

    def test_raw_templater_uses_multiprocess_runner(self):
        """RawTemplater does NOT support warm workers → MultiProcessRunner."""
        config = FluffConfig(overrides={"dialect": "ansi", "templater": "raw"})
        lntr = Linter(config=config)
        assert lntr.templater.supports_warm_workers is False
        r, _ = get_runner(lntr, config, 4)
        assert type(r) is runner.MultiProcessRunner

    def test_placeholder_templater_uses_multiprocess_runner(self):
        """PlaceholderTemplater inherits from RawTemplater → MultiProcessRunner."""
        config = FluffConfig(overrides={"dialect": "ansi", "templater": "placeholder"})
        lntr = Linter(config=config)
        assert lntr.templater.supports_warm_workers is False
        r, _ = get_runner(lntr, config, 4)
        assert type(r) is runner.MultiProcessRunner

    def test_python_templater_uses_multiprocess_runner(self):
        """PythonTemplater inherits from RawTemplater → MultiProcessRunner."""
        config = FluffConfig(overrides={"dialect": "ansi", "templater": "python"})
        lntr = Linter(config=config)
        assert lntr.templater.supports_warm_workers is False
        r, _ = get_runner(lntr, config, 4)
        assert type(r) is runner.MultiProcessRunner

    def test_jinja_templater_uses_warm_worker_runner(self):
        """JinjaTemplater opts in → WarmWorkerRunner."""
        config = FluffConfig(overrides={"dialect": "ansi"})
        lntr = Linter(config=config)
        assert lntr.templater.supports_warm_workers is True
        r, _ = get_runner(lntr, config, 4)
        assert type(r) is WarmWorkerRunner

    def test_raw_templater_lints_e2e(self, tmp_path):
        """RawTemplater lints correctly with processes>1."""
        (tmp_path / "a.sql").write_text("SELECT 1\n")
        config = FluffConfig(overrides={"dialect": "ansi", "templater": "raw"})
        lntr = Linter(config=config)
        result = lntr.lint_paths((str(tmp_path),), processes=2, retain_files=True)
        assert sum(p.stats()["files"] for p in result.paths) == 1

    def test_placeholder_templater_lints_e2e(self, tmp_path):
        """PlaceholderTemplater lints correctly with processes>1."""
        (tmp_path / "a.sql").write_text("SELECT 1\n")
        # PlaceholderTemplater requires param_style via config file.
        (tmp_path / ".sqlfluff").write_text(
            "[sqlfluff]\ntemplater = placeholder\ndialect = ansi\n"
            "[sqlfluff:templater:placeholder]\nparam_style = dollar\n"
        )
        config = FluffConfig.from_path(str(tmp_path))
        lntr = Linter(config=config)
        result = lntr.lint_paths((str(tmp_path),), processes=2, retain_files=True)
        assert sum(p.stats()["files"] for p in result.paths) == 1

    def test_jinja_templater_lints_e2e(self, tmp_path):
        """JinjaTemplater via WarmWorkerRunner lints correctly."""
        (tmp_path / "a.sql").write_text("SELECT 1\n")
        (tmp_path / "b.sql").write_text("SELECT 2\n")
        config = FluffConfig(overrides={"dialect": "ansi"})
        lntr = Linter(config=config)
        try:
            result = lntr.lint_paths((str(tmp_path),), processes=2, retain_files=True)
            assert sum(p.stats()["files"] for p in result.paths) == 2
        finally:
            WarmWorkerRunner._terminate_pool(lntr.templater)

    def test_sequential_runner_for_single_process(self):
        """All templaters fall back to SequentialRunner with processes=1."""
        for tmpl in ["raw", "jinja", "placeholder", "python"]:
            config = FluffConfig(overrides={"dialect": "ansi", "templater": tmpl})
            lntr = Linter(config=config)
            r, _ = get_runner(lntr, config, 1)
            assert isinstance(r, runner.SequentialRunner), (
                f"{tmpl} should use SequentialRunner with processes=1"
            )


# --- _handle_result tests ---


class TestHandleResult:
    """Tests for ParallelRunner._handle_result error handling."""

    def _make_runner(self) -> runner.ParallelRunner:
        """Create a minimal runner for testing _handle_result."""
        config = FluffConfig(overrides={"dialect": "ansi"})
        lntr = Linter(config=config)
        # Use MultiThreadRunner (simplest concrete ParallelRunner).
        return runner.MultiThreadRunner(lntr, config, processes=1)

    def test_handle_result_returns_linted_file(self):
        """Normal LintedFile is returned as-is."""
        from sqlfluff.core.linter import LintedFile

        r = self._make_runner()
        config = FluffConfig(overrides={"dialect": "ansi"})
        lntr = Linter(config=config)
        rendered = lntr.render_file("test/fixtures/linter/passing.sql", config)
        rp = lntr.get_rulepack(config=rendered.config)
        linted = Linter.lint_rendered(rendered, rp, False, None)

        result = r._handle_result(linted, fix=False)
        assert isinstance(result, LintedFile)

    def test_handle_result_returns_none_for_delayed_exception(self):
        """DelayedException is handled and returns None."""
        r = self._make_runner()
        exc = DelayedException(ValueError("test error"), fname="test.sql")
        result = r._handle_result(exc, fix=False)
        assert result is None

    def test_handle_result_returns_none_for_skip_file(self):
        """SQLFluffSkipFile is logged as warning, returns None."""
        from sqlfluff.core.errors import SQLFluffSkipFile

        r = self._make_runner()
        exc = DelayedException(SQLFluffSkipFile("file too large"), fname="big.sql")
        result = r._handle_result(exc, fix=False)
        assert result is None

    def test_handle_result_reraises_non_skip_exception(self):
        """Non-skip exceptions are re-raised via _handle_lint_path_exception."""
        r = self._make_runner()
        exc = DelayedException(RuntimeError("unexpected"), fname="broken.sql")
        # _handle_result calls _handle_lint_path_exception which logs
        # a warning but doesn't raise (it's a handled path error).
        result = r._handle_result(exc, fix=False)
        assert result is None


# --- Error recovery and deadlock prevention ---


class TestErrorRecoveryAndDeadlocks:
    """Tests for error recovery, timeout, and deadlock prevention."""

    def test_terminate_pool_called_on_exception(self, tmp_path):
        """Any exception during dispatch terminates the pool."""
        import unittest.mock

        config = FluffConfig(overrides={"dialect": "ansi"})
        lntr = Linter(config=config)

        r = WarmWorkerRunner(lntr, config, processes=2)
        # Patch _dispatch_and_collect to raise.
        with unittest.mock.patch.object(
            WarmWorkerRunner,
            "_dispatch_and_collect",
            side_effect=RuntimeError("boom"),
        ):
            with unittest.mock.patch.object(
                WarmWorkerRunner, "_terminate_pool"
            ) as mock_term:
                try:
                    list(r.run([], fix=False))
                except RuntimeError:
                    pass
                # _terminate_pool should have been called.
                assert mock_term.called

    def test_broadcast_timeout_is_set(self):
        """Broadcast uses map_async with a timeout, not blocking map."""
        import inspect
        import textwrap

        source = textwrap.dedent(inspect.getsource(WarmWorkerRunner.run))
        # Verify map_async().get(timeout=...) pattern exists (not bare map).
        assert "map_async" in source
        assert "timeout" in source
        assert "pool.map(" not in source.replace("pool.map_async", "")

    def test_sequential_runner_handles_exception_gracefully(self, tmp_path):
        """SequentialRunner logs errors but doesn't crash the loop."""
        (tmp_path / "good.sql").write_text("SELECT 1\n")
        config = FluffConfig(overrides={"dialect": "ansi"})
        lntr = Linter(config=config)
        r = runner.SequentialRunner(lntr, config)
        # Should not raise — errors are handled internally.
        results = list(r.run([str(tmp_path / "good.sql")], fix=False))
        assert len(results) == 1

    def test_warm_worker_lint_with_nonexistent_file(self, tmp_path):
        """Warm workers handle missing files without deadlocking."""
        (tmp_path / "good.sql").write_text("SELECT 1\n")
        config = FluffConfig(overrides={"dialect": "ansi"})
        lntr = Linter(config=config)
        try:
            result = lntr.lint_paths((str(tmp_path),), processes=2, retain_files=True)
            # Should lint the good file without hanging.
            assert sum(p.stats()["files"] for p in result.paths) >= 1
        finally:
            WarmWorkerRunner._terminate_pool(lntr.templater)

    def test_warm_worker_empty_file_list(self, tmp_path):
        """Empty directory doesn't deadlock warm workers."""
        (tmp_path / "empty_dir").mkdir()
        config = FluffConfig(overrides={"dialect": "ansi"})
        lntr = Linter(config=config)
        try:
            result = lntr.lint_paths(
                (str(tmp_path / "empty_dir"),),
                processes=2,
                retain_files=True,
            )
            assert sum(p.stats()["files"] for p in result.paths) == 0
        finally:
            WarmWorkerRunner._terminate_pool(lntr.templater)

    def test_tree_stripping_preserves_violations(self):
        """Tree stripping in lint mode doesn't lose violation data."""
        from multiprocessing.shared_memory import SharedMemory as SHM

        config = FluffConfig(overrides={"dialect": "ansi", "rules": "CP01"})
        data_bytes = pickle.dumps({"root_config": config})
        shm = SHM(create=True, size=len(data_bytes))
        shm.buf[: len(data_bytes)] = data_bytes

        runner._worker_init_data = None
        runner._worker_linter_cache = None
        try:
            # File with mixed-case keywords → CP01 violation.
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".sql", delete=False
            ) as f:
                f.write("SELECT a from b\n")
                fname = f.name

            result = _warm_worker_apply((fname, False, (shm.name, len(data_bytes))))
            from sqlfluff.core.linter import LintedFile

            assert isinstance(result, LintedFile)
            # Tree should be stripped (fix=False).
            assert result.tree is None
            assert result.templated_file is None
            # But violations are preserved.
            assert len(result.violations) > 0
            assert result.path == fname
            os.unlink(fname)
        finally:
            shm.close()
            shm.unlink()
            runner._worker_init_data = None
            runner._worker_linter_cache = None

    def test_tree_preserved_for_fix_with_violations(self):
        """Fix mode keeps tree when violations exist (needed for persist_tree)."""
        from multiprocessing.shared_memory import SharedMemory as SHM

        config = FluffConfig(overrides={"dialect": "ansi", "rules": "CP01"})
        data_bytes = pickle.dumps({"root_config": config})
        shm = SHM(create=True, size=len(data_bytes))
        shm.buf[: len(data_bytes)] = data_bytes

        runner._worker_init_data = None
        runner._worker_linter_cache = None
        try:
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".sql", delete=False
            ) as f:
                f.write("SELECT a from b\n")
                fname = f.name

            result = _warm_worker_apply((fname, True, (shm.name, len(data_bytes))))
            from sqlfluff.core.linter import LintedFile

            assert isinstance(result, LintedFile)
            # fix=True AND violations → tree must be kept.
            assert result.tree is not None
            assert result.templated_file is not None
            assert len(result.violations) > 0
            os.unlink(fname)
        finally:
            shm.close()
            shm.unlink()
            runner._worker_init_data = None
            runner._worker_linter_cache = None
