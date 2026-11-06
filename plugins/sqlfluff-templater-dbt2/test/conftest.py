"""Recorded upstream artifacts keep ordinary tests independent of a dbt install."""

import copy
import json
import subprocess
from pathlib import Path

import pytest
from sqlfluff_templater_dbt2.templater import Dbt2Templater


@pytest.fixture
def traces():
    """Load real traces captured by scripts/record_traces.py."""
    path = Path(__file__).parent / "fixtures/traces.json"
    return copy.deepcopy(json.loads(path.read_text(encoding="utf-8")))


@pytest.fixture
def batch_runtime(tmp_path, monkeypatch, traces):
    """Emulate one dbt invocation emitting all selected models and a manifest."""
    monkeypatch.setattr("tempfile.tempdir", str(tmp_path))
    monkeypatch.setattr(Dbt2Templater, "_command", lambda *_: ["dbt"])
    paths = [tmp_path / "first.sql", tmp_path / "second.sql"]
    for path in paths:
        path.write_text(traces["literal"]["source"], encoding="utf-8")
    calls = []
    failures = []

    def run(command, **kwargs):
        calls.append(command)
        if failures:
            return subprocess.CompletedProcess(command, 1, "", "compile failed")
        target = Path(command[command.index("--target-path") + 1])
        target.mkdir()
        manifest = {"metadata": {"invocation_id": "invocation"}, "nodes": {}}
        selectors = command[command.index("--select") + 1 : command.index("--feature")]
        for selector in selectors:
            path = tmp_path / selector.removeprefix("path:")
            uid = f"model.example.{path.stem}"
            trace = {
                **traces["literal"],
                "source_path": str(path),
                "filename": str(path),
                "unique_id": uid,
                "invocation_id": "invocation",
            }
            (target / f"{path.stem}.render_trace.json").write_text(
                json.dumps(trace), encoding="utf-8"
            )
            manifest["nodes"][uid] = {
                "original_file_path": path.relative_to(tmp_path).as_posix()
            }
        (target / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
        return subprocess.CompletedProcess(
            command, 0, "dbt compile output\n", "dbt compile diagnostic\n"
        )

    monkeypatch.setattr(subprocess, "run", run)
    return paths, calls, failures
