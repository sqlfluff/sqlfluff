"""Share one fresh compilation across all files in a lint pass."""

import json
import subprocess
from pathlib import Path

import pytest
from sqlfluff_templater_dbt2.templater import Dbt2Templater

from sqlfluff.core import FluffConfig
from sqlfluff.core.errors import SQLTemplaterError


def make_config(project, target="dev"):
    """Configure a test pass without importing a dbt runtime."""
    return FluffConfig(
        configs={
            "core": {"dialect": "ansi", "templater": "dbt2"},
            "templater": {"dbt2": {"project_dir": str(project), "target": target}},
        }
    )


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
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(subprocess, "run", run)
    return paths, calls, failures


def test_one_compile_serves_multiple_files(batch_runtime):
    """Compile once, load artifacts once, then render every selected file from memory."""
    paths, calls, _ = batch_runtime
    cfg = make_config(paths[0].parent)
    templater = Dbt2Templater()
    fnames = list(map(str, paths))
    assert templater.sequence_files(fnames, cfg) == fnames
    for path in paths:
        tf, _ = templater.process(in_str=path.read_text(), fname=str(path), config=cfg)
        assert tf.templated_str == "select 1"
    assert len(calls) == 1
    assert calls[0][calls[0].index("--select") + 1 : calls[0].index("--feature")] == [
        "path:first.sql",
        "path:second.sql",
    ]
    assert not Path(calls[0][calls[0].index("--target-path") + 1]).exists()


def test_new_pass_recompiles(batch_runtime):
    """A later lint pass must never inherit stale artifacts or invocation identity."""
    paths, calls, _ = batch_runtime
    cfg = make_config(paths[0].parent)
    templater = Dbt2Templater()
    for _ in range(2):
        templater.sequence_files(list(map(str, paths)), cfg)
        for path in paths:
            templater.process(in_str=path.read_text(), fname=str(path), config=cfg)
    assert len(calls) == 2
    index = calls[0].index("--target-path") + 1
    assert calls[0][index] != calls[1][index]


def test_changed_settings_do_not_reuse_batch(batch_runtime):
    """Per-file targets or vars cannot accidentally consume another context's trace."""
    paths, calls, _ = batch_runtime
    templater = Dbt2Templater()
    original = make_config(paths[0].parent)
    templater.sequence_files(list(map(str, paths)), original)
    templater.process(
        in_str=paths[0].read_text(),
        fname=str(paths[0]),
        config=make_config(paths[0].parent, target="prod"),
    )
    templater.process(in_str=paths[1].read_text(), fname=str(paths[1]), config=original)
    assert len(calls) == 2
    assert calls[1][calls[1].index("--target") + 1] == "prod"


def test_batch_failure_uses_normal_file_error_path(batch_runtime):
    """A failed compile is reported per file without retrying it N times."""
    paths, calls, failures = batch_runtime
    failures.append(True)
    cfg = make_config(paths[0].parent)
    templater = Dbt2Templater()
    templater.sequence_files(list(map(str, paths)), cfg)
    for path in paths:
        with pytest.raises(SQLTemplaterError, match="compile failed"):
            templater.process(in_str=path.read_text(), fname=str(path), config=cfg)
    assert len(calls) == 1


def test_source_changed_after_batch_is_rejected(batch_runtime):
    """Never apply an old mapping to source edited during the same lint pass."""
    paths, calls, _ = batch_runtime
    cfg = make_config(paths[0].parent)
    templater = Dbt2Templater()
    templater.sequence_files(list(map(str, paths)), cfg)
    paths[0].write_text("select 2\n", encoding="utf-8")
    with pytest.raises(SQLTemplaterError, match="source differs"):
        templater.process(in_str=paths[0].read_text(), fname=str(paths[0]), config=cfg)
    assert len(calls) == 1


def test_empty_pass_does_not_compile(batch_runtime):
    """An empty input set creates no runtime work or lingering cache."""
    paths, calls, _ = batch_runtime
    assert Dbt2Templater().sequence_files([], make_config(paths[0].parent)) == []
    assert not calls
