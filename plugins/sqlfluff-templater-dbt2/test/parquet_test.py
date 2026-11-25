"""Consume public nested Parquet snapshot without weakening provenance or freshness checks."""

import json
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from sqlfluff_templater_dbt2.artifacts import RenderArtifacts
from sqlfluff_templater_dbt2.trace import trace_to_templated_file

from sqlfluff.core.errors import SQLTemplaterError


def write_snapshot(target: Path, rows: list[dict]) -> Path:
    """Write the producer's nested event representation as an actual Parquet file."""
    path = target / "info_schema/v1/dbt.render_traces.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    pq.write_table(pa.Table.from_pylist(rows), path)
    return path


@pytest.fixture
def parquet_artifacts(tmp_path, traces):
    """Pair one fresh model trace with its compilation manifest."""
    target = tmp_path / "target"
    target.mkdir()
    model = tmp_path / "model.sql"
    trace = {
        **traces["literal"],
        "protocol_version": 2,
        "ingested_at": 10,
        "source_path": str(model),
        "filename": "model.sql",
        "unique_id": "model.example.model",
        "invocation_id": "fresh-invocation",
    }
    manifest = {
        "metadata": {"invocation_id": trace["invocation_id"]},
        "nodes": {trace["unique_id"]: {"original_file_path": "model.sql"}},
    }
    (target / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    return target, model, trace


@pytest.mark.parametrize(
    "case",
    [
        "literal",
        "expression",
        "branch_false",
        "loop",
        "capture",
        "comment",
        "unicode_crlf",
        "continued",
        "broken",
        "returned",
        "block_returned",
        "recursive",
        "recursive_transformed",
        "recursive_else",
    ],
)
def test_parquet_preserves_recorded_source_mappings(case, parquet_artifacts, traces):
    """JSON-v1 and Parquet-v2 yield the same mapping for real recorded renders."""
    target, model, identity = parquet_artifacts
    original = traces[case]
    trace = {
        **identity,
        **{key: original[key] for key in ("source", "rendered", "events")},
    }
    write_snapshot(target, [trace])
    loaded = RenderArtifacts.load(target, model.parent).trace_for(
        model, trace["source"]
    )
    assert loaded["events"] == original["events"]
    expected = trace_to_templated_file(original, original["source"], str(model))
    actual = trace_to_templated_file(loaded, trace["source"], str(model))
    assert actual.templated_str == expected.templated_str
    assert actual.sliced_file == expected.sliced_file
    assert actual.raw_sliced == expected.raw_sliced


def test_parquet_validates_duplicate_fresh_rows(parquet_artifacts):
    """Defensively select fresh rows even if a producer writes duplicate model IDs."""
    target, model, trace = parquet_artifacts
    newest = {**trace, "ingested_at": 20}
    stale = {**trace, "invocation_id": "older-invocation", "ingested_at": 100}
    write_snapshot(target, [newest, trace, stale])
    loaded = RenderArtifacts.load(target, model.parent).trace_for(
        model, trace["source"]
    )
    assert loaded == newest


def test_retained_trace_is_not_reused_for_another_invocation(parquet_artifacts):
    """An unselected node's last-known trace cannot authorize a fresh source fix."""
    target, model, trace = parquet_artifacts
    write_snapshot(target, [{**trace, "invocation_id": "older-invocation"}])
    with pytest.raises(SQLTemplaterError, match="exactly one render trace"):
        RenderArtifacts.load(target, model.parent).trace_for(model, trace["source"])


def test_conflicting_snapshot_rows_are_rejected(parquet_artifacts):
    """Equal timestamps with different contents are ambiguous, regardless of file order."""
    target, model, trace = parquet_artifacts
    write_snapshot(target, [trace, {**trace, "rendered": "select 2"}])
    with pytest.raises(SQLTemplaterError, match="Conflicting"):
        RenderArtifacts.load(target, model.parent)


def test_corrupt_snapshot_does_not_fall_back_to_json(parquet_artifacts):
    """Corrupt Parquet must surface an error even when another artifact is readable."""
    target, model, trace = parquet_artifacts
    write_snapshot(target, [trace])
    (target / "info_schema/v1/dbt.render_traces.parquet").write_bytes(b"broken")
    (target / "model.render_trace.json").write_text(json.dumps(trace), encoding="utf-8")
    with pytest.raises(SQLTemplaterError, match="Cannot read.*Parquet"):
        RenderArtifacts.load(target, model.parent)


@pytest.mark.parametrize(
    "mutation,match",
    [
        ({"protocol_version": 3}, "Unsupported"),
        ({"ingested_at": "invalid"}, "row identity"),
        ({"source_path": None}, "source identity"),
        ({"source": "stale"}, "source differs"),
        ({"unique_id": "model.example.other"}, "model/invocation identity"),
    ],
)
def test_invalid_parquet_provenance_is_rejected(parquet_artifacts, mutation, match):
    """Container migration preserves producer, source and model checks."""
    target, model, trace = parquet_artifacts
    write_snapshot(target, [{**trace, **mutation}])
    with pytest.raises(SQLTemplaterError, match=match):
        RenderArtifacts.load(target, model.parent).trace_for(model, trace["source"])


def test_private_epochs_are_not_a_consumer_contract(parquet_artifacts):
    """A corrupt private store cannot affect a valid public snapshot."""
    target, model, trace = parquet_artifacts
    write_snapshot(target, [trace])
    private = target / "private/metadata/compile/render_traces/v1_0.parquet"
    private.parent.mkdir(parents=True)
    private.write_bytes(b"broken")
    assert (
        RenderArtifacts.load(target, model.parent).trace_for(model, trace["source"])
        == trace
    )
