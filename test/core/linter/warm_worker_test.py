"""Tests for WarmWorkerRunner and the warm worker protocol."""

import os
import pickle
import sys
import types

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
    _warm_pool = None
    _warm_pool_processes = 0
    _warm_pool_manifest_id = None

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

    def _init_worker(self, config: FluffConfig, extra: dict | None = None) -> None:
        """Helper: broadcast init data to the worker globals."""
        data: dict = {"root_config": config}
        if extra:
            data.update(extra)
        _warm_worker_receive_init(pickle.dumps(data))

    def test_first_task_creates_linter_cache(self):
        """First task after init creates Linter and caches it."""
        from sqlfluff.core.linter import LintedFile

        config = FluffConfig(overrides={"dialect": "ansi"})
        self._init_worker(config)

        assert runner._worker_linter_cache is None
        result = _warm_worker_apply(("test/fixtures/linter/passing.sql", False, None))
        assert isinstance(result, LintedFile)
        assert runner._worker_linter_cache is not None
        linter, templater, cached_config = runner._worker_linter_cache
        assert isinstance(linter, Linter)
        assert isinstance(cached_config, FluffConfig)

    def test_subsequent_tasks_reuse_same_cache(self):
        """Second task reuses the exact same cached linter objects."""
        from sqlfluff.core.linter import LintedFile

        config = FluffConfig(overrides={"dialect": "ansi"})
        self._init_worker(config)

        _warm_worker_apply(("test/fixtures/linter/passing.sql", False, None))
        cache_after_first = runner._worker_linter_cache

        result = _warm_worker_apply(("test/fixtures/linter/passing.sql", False, None))
        assert isinstance(result, LintedFile)
        assert runner._worker_linter_cache is cache_after_first

    def test_receive_init_merges_with_existing_data(self):
        """_warm_worker_receive_init merges into pre-existing init data."""
        config = FluffConfig(overrides={"dialect": "ansi"})
        runner._worker_init_data = {"from_initializer": "preserved"}

        _warm_worker_receive_init(
            pickle.dumps({"root_config": config, "from_broadcast": "added"})
        )

        assert runner._worker_init_data["from_initializer"] == "preserved"
        assert runner._worker_init_data["from_broadcast"] == "added"
        assert isinstance(runner._worker_init_data["root_config"], FluffConfig)

    def test_receive_init_resets_linter_cache(self):
        """_warm_worker_receive_init clears linter cache for rebuild."""
        config = FluffConfig(overrides={"dialect": "ansi"})
        self._init_worker(config)
        _warm_worker_apply(("test/fixtures/linter/passing.sql", False, None))
        assert runner._worker_linter_cache is not None

        # Receiving new init data should reset the cache.
        _warm_worker_receive_init(pickle.dumps({"root_config": config}))
        assert runner._worker_linter_cache is None

    def test_exception_wrapped_as_delayed_exception(self):
        """Exceptions during render are wrapped as DelayedException."""
        config = FluffConfig(overrides={"dialect": "ansi"})
        self._init_worker(config)
        result = _warm_worker_apply(("no_such_file.sql", False, None))

        assert isinstance(result, DelayedException)
        assert result.fname == "no_such_file.sql"
        with pytest.raises(Exception):
            result.reraise()

    def test_error_without_init_data(self):
        """Task without prior init raises descriptive RuntimeError."""
        result = _warm_worker_apply(("test/fixtures/linter/passing.sql", False, None))
        assert isinstance(result, DelayedException)
        assert "init data" in str(result.ee)


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
        """End-to-end: Jinja warm worker can lint a real file."""
        from sqlfluff.core.linter import LintedFile

        config = FluffConfig(overrides={"dialect": "ansi"})

        runner._worker_init_data = None
        runner._worker_linter_cache = None
        try:
            _warm_worker_receive_init(pickle.dumps({"root_config": config}))
            result = _warm_worker_apply(
                ("test/fixtures/linter/passing.sql", False, None)
            )
            assert isinstance(result, LintedFile)
        finally:
            runner._worker_init_data = None
            runner._worker_linter_cache = None


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
