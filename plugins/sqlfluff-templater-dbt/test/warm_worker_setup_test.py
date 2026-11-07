"""Isolated tests for dbt warm-worker version-specific setup."""

import json
import multiprocessing
import pickle
import subprocess
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from sqlfluff.core import FluffConfig
from sqlfluff_templater_dbt.templater import DbtTemplater, warm_worker_setup


@pytest.mark.parametrize("version", [(1, 7), (1, 8)])
def test_warm_worker_setup_uses_supported_version_api(version, monkeypatch):
    """Use the same initialization and adapter signatures as dbt_config."""
    monkeypatch.setattr(DbtTemplater, "dbt_version_tuple", version)
    config = SimpleNamespace(credentials=SimpleNamespace(type="postgres"))
    modules = {
        "dbt.flags": MagicMock(),
        "dbt.adapters.factory": MagicMock(),
        "dbt.tracking": MagicMock(),
        "dbt_common.clients.system": MagicMock(),
        "dbt_common.context": MagicMock(),
        "dbt.mp_context": MagicMock(),
    }
    imports = []

    def import_module(name):
        imports.append(name)
        if version < (1, 8) and (
            name.startswith("dbt_common") or name == "dbt.mp_context"
        ):
            raise ModuleNotFoundError(name)
        return modules[name]

    with (
        patch("importlib.import_module", side_effect=import_module),
        patch.object(DbtTemplater, "try_silence_dbt_logs") as silence_logs,
    ):
        result = warm_worker_setup(pickle.dumps(config))

    silence_logs.assert_called_once_with()
    restored = result["dbt_config"]
    assert restored.credentials.type == "postgres"
    modules["dbt.tracking"].do_not_track.assert_called_once_with()
    modules["dbt.flags"].set_from_args.assert_called_once_with(restored, None)
    factory = modules["dbt.adapters.factory"]
    factory.FACTORY.load_plugin.assert_called_once_with("postgres")
    if version >= (1, 8):
        context = modules["dbt_common.context"]
        system = modules["dbt_common.clients.system"]
        context.set_invocation_context.assert_called_once_with(
            system.get_env.return_value
        )
        factory.register_adapter.assert_called_once_with(
            restored, modules["dbt.mp_context"].get_mp_context.return_value
        )
    else:
        assert not any(name.startswith("dbt_common") for name in imports)
        assert "dbt.mp_context" not in imports
        factory.register_adapter.assert_called_once_with(restored)


def _initialize_real_dbt_in_worker(config_bytes, result):
    """Register a real adapter inside a fresh spawned process."""
    from dbt.adapters.factory import get_adapter

    config = warm_worker_setup(config_bytes)["dbt_config"]
    result.put((config.credentials.type, type(get_adapter(config)).__name__))


def test_warm_worker_setup_with_real_dbt(tmp_path):
    """Initialize from a real dbt config without connecting to a database."""
    (tmp_path / "dbt_project.yml").write_text(
        "name: smoke\nversion: '1.0'\nconfig-version: 2\nprofile: smoke\n",
        encoding="utf-8",
    )
    (tmp_path / "profiles.yml").write_text(
        "smoke:\n  target: dev\n  outputs:\n    dev:\n      type: postgres\n"
        "      host: localhost\n      user: smoke\n      password: smoke\n"
        "      port: 5432\n      dbname: smoke\n      schema: public\n"
        "      threads: 1\n",
        encoding="utf-8",
    )
    templater = DbtTemplater()
    templater.sqlfluff_config = FluffConfig(
        configs={"core": {"dialect": "postgres"}, "templater": {"dbt": {}}}
    )
    templater.project_dir = str(tmp_path)
    templater.profiles_dir = str(tmp_path)
    config_bytes = pickle.dumps(templater.dbt_config)

    ctx = multiprocessing.get_context("spawn")
    queue = ctx.Queue()
    process = ctx.Process(
        target=_initialize_real_dbt_in_worker, args=(config_bytes, queue)
    )
    process.start()
    process.join(timeout=45)
    if process.is_alive():
        process.terminate()
        process.join()
        pytest.fail("dbt worker did not finish initialization")
    assert process.exitcode == 0
    assert queue.get(timeout=5) == ("postgres", "PostgresAdapter")

    # A fresh interpreter captures dbt's actual stdout stream, including loggers
    # that retain a reference to the stream before Python-level redirection.
    config_path = tmp_path / "config.pickle"
    config_path.write_bytes(config_bytes)
    script = (
        "import json, pathlib, sys; "
        "from sqlfluff_templater_dbt.templater import warm_worker_setup; "
        "config = warm_worker_setup(pathlib.Path(sys.argv[1]).read_bytes()); "
        "print(json.dumps({'adapter': config['dbt_config'].credentials.type}))"
    )
    child = subprocess.run(
        [sys.executable, "-c", script, str(config_path)],
        capture_output=True,
        text=True,
        check=True,
        timeout=45,
    )
    assert json.loads(child.stdout) == {"adapter": "postgres"}
