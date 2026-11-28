"""Distinguish deliberately disabled models from failed or missing render output."""

import logging

import pytest
from sqlfluff_templater_dbt2.artifacts import RenderArtifacts
from sqlfluff_templater_dbt2.templater import Dbt2Templater

from sqlfluff.core import FluffConfig, Linter
from sqlfluff.core.errors import SQLFluffSkipFile, SQLTemplaterError


def manifest_for(path="model.sql", enabled=False):
    """Use the disabled-node convention emitted by the actual dbt runtime."""
    return {
        "metadata": {"invocation_id": "invocation"},
        "nodes": {},
        "disabled": {
            "model.example.model": [
                {
                    "original_file_path": path,
                    "config": {"enabled": enabled},
                    "resource_type": "model",
                }
            ]
        },
    }


def test_disabled_model_skips_without_stub_trace(tmp_path):
    """An explicit disabled entry is sufficient; no synthetic render is needed."""
    artifacts = RenderArtifacts(tmp_path, manifest_for(), {})
    with pytest.raises(SQLFluffSkipFile, match="disabled dbt model"):
        artifacts.trace_for(tmp_path / "model.sql", "select 1")


@pytest.mark.parametrize("mutation", ["enabled", "unrelated", "absent", "missing_flag"])
def test_missing_enabled_or_unrelated_output_remains_error(tmp_path, mutation):
    """Never infer disabled status merely because a model did not produce a trace."""
    manifest = manifest_for()
    node = manifest["disabled"]["model.example.model"][0]
    if mutation == "enabled":
        node["config"]["enabled"] = True
    elif mutation == "unrelated":
        node["original_file_path"] = "another/model.sql"
    elif mutation == "absent":
        manifest["disabled"] = {}
    else:
        node["config"] = {}
    with pytest.raises(SQLTemplaterError, match="exactly one render trace"):
        RenderArtifacts(tmp_path, manifest, {}).trace_for(
            tmp_path / "model.sql", "select 1"
        )


def test_inconsistent_existing_trace_is_not_skipped(tmp_path, traces):
    """A producer contradiction remains an identity error, rather than a silent skip."""
    model = tmp_path / "model.sql"
    artifacts = RenderArtifacts(tmp_path, manifest_for(), {model: [traces["literal"]]})
    with pytest.raises(SQLTemplaterError, match="identity does not match"):
        artifacts.trace_for(model, traces["literal"]["source"])


def test_linter_reports_disabled_as_warning(tmp_path, monkeypatch, caplog):
    """Match the legacy templater's skip path instead of emitting TMP violations."""
    artifacts = RenderArtifacts(tmp_path, manifest_for(), {})
    model = tmp_path / "model.sql"
    monkeypatch.setattr(
        Dbt2Templater, "_runtime", lambda *_: artifacts.trace_for(model, "select 1")
    )
    config = FluffConfig(overrides={"dialect": "ansi", "templater": "dbt2"})
    with caplog.at_level(logging.WARNING, logger="sqlfluff.linter"):
        result = Linter(config=config).lint_string("select 1", fname=str(model))
    assert not result.get_violations(types=SQLTemplaterError)
    assert "Skipped disabled dbt model" in caplog.text
