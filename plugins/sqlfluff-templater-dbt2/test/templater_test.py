"""Exercise runtime selection, invocation identity and useful failure messages."""

import json
import subprocess
import sys
from importlib import metadata
from pathlib import Path

import pytest
from sqlfluff_templater_dbt2.templater import Dbt2Templater

from sqlfluff.core import FluffConfig
from sqlfluff.core.errors import SQLFluffUserError, SQLTemplaterError


def config(project, **settings):
    """Configure a project without loading dbt in the test process."""
    return FluffConfig(
        configs={
            "core": {"dialect": "ansi", "templater": "dbt2"},
            "templater": {"dbt2": {"project_dir": str(project), **settings}},
        }
    )


@pytest.mark.parametrize("version", ["1.4.1", "1.10.15", "1.11.0rc1"])
def test_legacy_distribution(version, monkeypatch):
    """Direct Python dbt users to the established dbt templater."""
    monkeypatch.setattr(metadata, "version", lambda _: version)
    with pytest.raises(
        SQLFluffUserError, match="sqlfluff-templater-dbt and set templater = dbt"
    ):
        Dbt2Templater()._command({})


def test_missing_distribution(monkeypatch):
    """Explain the unreleased upstream prerequisite if dbt is absent."""

    def missing(_):
        raise metadata.PackageNotFoundError("dbt-core")

    monkeypatch.setattr(metadata, "version", missing)
    with pytest.raises(SQLFluffUserError, match="dbt-labs/dbt/pull/16870"):
        Dbt2Templater()._command({})


@pytest.mark.parametrize("version", ["2.0.0rc9", "2.0.8", "2.99.0"])
def test_default_interpreter(version, monkeypatch):
    """Use the project's installed runtime rather than a bundled dbt binary."""
    monkeypatch.setattr(metadata, "version", lambda _: version)
    command = Dbt2Templater()._command({})
    assert command[:2] == [sys.executable, "-c"]
    assert "dbt.cli.main" in command[2]


@pytest.mark.parametrize(
    "output", ["Core:\n  - installed: 1.10.15", "dbt-core 1.10.15"]
)
def test_external_legacy_runtime(output, monkeypatch):
    """The external CLI option gives the same legacy-generation guidance."""
    monkeypatch.setattr(Dbt2Templater, "_execute", lambda *_: output)
    with pytest.raises(SQLFluffUserError, match="sqlfluff-templater-dbt and"):
        Dbt2Templater()._command({"runtime_path": "dbt"})


@pytest.mark.parametrize("case", ["stdin", "unsaved", "outside"])
def test_model_requirements(case, tmp_path):
    """Reject sources that cannot be identified as the exact compiled file."""
    model = tmp_path / "model.sql"
    model.write_text("select 1\n", encoding="utf-8")
    fname, source, project = str(model), "select 1\n", tmp_path
    if case == "stdin":
        fname = "stdin"
    elif case == "unsaved":
        source = "select 2\n"
    else:
        project = tmp_path / "other_project"
    with pytest.raises(SQLTemplaterError):
        Dbt2Templater().process(in_str=source, fname=fname, config=config(project))


def test_runtime_command_and_artifact(tmp_path, monkeypatch, traces):
    """Fresh target directories, explicit trace flag and manifest checks replace patches."""
    monkeypatch.setattr("tempfile.tempdir", str(tmp_path))
    monkeypatch.setattr(metadata, "version", lambda _: "2.0.8")
    model = tmp_path / "model.sql"
    source = traces["literal"]["source"]
    model.write_text(source, encoding="utf-8")
    calls = []

    def runtime(command, **kwargs):
        calls.append(command)
        target = Path(command[command.index("--target-path") + 1])
        target.mkdir()
        trace = {
            **traces["literal"],
            "source_path": str(model),
            "filename": str(model),
        }
        (target / "model.render_trace.json").write_text(
            json.dumps(trace), encoding="utf-8"
        )
        (target / "manifest.json").write_text(
            json.dumps(
                {
                    "metadata": {"invocation_id": trace["invocation_id"]},
                    "nodes": {trace["unique_id"]: {"original_file_path": "model.sql"}},
                }
            ),
            encoding="utf-8",
        )
        assert (
            "env" not in kwargs
        )  # No private exporter variables or forced log levels.
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr(subprocess, "run", runtime)
    templater = Dbt2Templater()
    cfg = config(tmp_path, profiles_dir=str(tmp_path), target="dev", context={"x": 1})
    for _ in range(2):
        tf, _ = templater.process(in_str=source, fname=str(model), config=cfg)
        assert tf.templated_str == traces["literal"]["rendered"]
    assert len(calls) == 2
    assert calls[0] != calls[1]
    assert calls[0][calls[0].index("--feature") + 1] == "write_render_trace"
    assert json.loads(calls[0][-1]) == {"x": 1}
    assert calls[0][calls[0].index("--target") + 1] == "dev"


@pytest.mark.parametrize(
    "mutation", ["invocation", "node", "source", "duplicate", "missing", "manifest"]
)
def test_reject_mismatched_artifacts(mutation, tmp_path, traces):
    """Never use a stale, ambiguous or unrelated artifact as a writable source map."""
    model = tmp_path / "model.sql"
    trace = {**traces["literal"], "source_path": str(model)}
    manifest = {
        "metadata": {"invocation_id": trace["invocation_id"]},
        "nodes": {trace["unique_id"]: {"original_file_path": "model.sql"}},
    }
    if mutation == "invocation":
        manifest["metadata"]["invocation_id"] = "other"
    elif mutation == "node":
        manifest["nodes"] = {}
    elif mutation == "source":
        trace["source"] = "stale"
    if mutation != "missing":
        (tmp_path / "trace.render_trace.json").write_text(
            json.dumps(trace), encoding="utf-8"
        )
    if mutation == "duplicate":
        (tmp_path / "second.render_trace.json").write_text(
            json.dumps(trace), encoding="utf-8"
        )
    if mutation != "manifest":
        (tmp_path / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    with pytest.raises(SQLTemplaterError):
        Dbt2Templater._read_trace(
            tmp_path, tmp_path, model, traces["literal"]["source"]
        )


@pytest.mark.parametrize("failure", ["exit", "missing", "timeout"])
def test_runtime_failures(failure, monkeypatch):
    """Translate subprocess failures into templater errors."""

    def run(*args, **kwargs):
        if failure == "missing":
            raise FileNotFoundError("dbt")
        if failure == "timeout":
            raise subprocess.TimeoutExpired("dbt", 300)
        return subprocess.CompletedProcess(
            args[0], 1, "", "unknown write_render_trace feature"
        )

    monkeypatch.setattr(subprocess, "run", run)
    if failure == "exit":
        with pytest.raises(SQLTemplaterError, match="dbt-labs/dbt/pull/16870"):
            Dbt2Templater._execute(["dbt", "compile"], 300)
    else:
        # process() owns the translation of OS and timeout errors.
        monkeypatch.setattr(
            Dbt2Templater, "_runtime", lambda *_: Dbt2Templater._execute(["dbt"], 300)
        )
        with pytest.raises(SQLTemplaterError, match="trace export failed"):
            Dbt2Templater().process(in_str="", fname="model.sql")
