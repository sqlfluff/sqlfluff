"""Validate real upstream provenance and reject unsafe source mappings."""

import copy
import json
from pathlib import Path

import pytest
from sqlfluff_templater_dbt2.trace import normalize_newlines, trace_to_templated_file

from sqlfluff.core.errors import SQLTemplaterError


@pytest.mark.parametrize(
    "case",
    [
        "literal",
        "expression",
        "branch_true",
        "branch_false",
        "loop",
        "skipped_loop",
        "capture",
        "inline_macro",
        "external_macro",
        "unicode_crlf",
        "whitespace",
        "comment",
        "layout",
        "project",
    ],
)
def test_upstream_traces(case, traces):
    """Translate actual dbt renders, preserving every writable literal region."""
    trace = traces[case]
    source = normalize_newlines(trace["source"])
    tf = trace_to_templated_file(trace, source, trace["filename"])
    assert tf.templated_str == normalize_newlines(trace["rendered"])
    for item in tf.sliced_file:
        if (
            item.slice_type == "literal"
            and item.templated_slice.start != item.templated_slice.stop
        ):
            assert source[item.source_slice] == tf.templated_str[item.templated_slice]


def test_identical_branch_provenance(traces):
    """Identical rendered SQL still identifies which original branch executed."""
    maps = [
        trace_to_templated_file(traces[name], traces[name]["source"], "model.sql")
        for name in ("branch_true", "branch_false")
    ]
    assert maps[0].templated_str == maps[1].templated_str
    positions = [
        next(
            item.source_slice.start
            for item in tf.sliced_file
            if item.slice_type == "literal" and item.templated_slice.stop > 0
        )
        for tf in maps
    ]
    source = traces["branch_true"]["source"]
    assert positions == [source.index("select"), source.rindex("select")]


def test_repeated_source(traces):
    """Multiple rendered loop iterations share a single source range."""
    trace = traces["loop"]
    tf = trace_to_templated_file(trace, trace["source"], "model.sql")
    repeated = [
        item
        for item in tf.sliced_file
        if trace["source"][item.source_slice] == "select "
    ]
    assert len(repeated) == 3
    assert len({item.source_slice.start for item in repeated}) == 1
    assert len({item.templated_slice.start for item in repeated}) == 3


@pytest.mark.parametrize(
    "mutation",
    ["source", "protocol", "producer", "stage", "literal", "offset", "gap", "kind"],
)
def test_reject_invalid_provenance(mutation, traces):
    """Malformed, incompatible and stale artifacts cannot enable source fixes."""
    trace = copy.deepcopy(traces["literal"])
    if mutation == "source":
        trace["source"] = "stale"
    elif mutation == "protocol":
        trace["protocol_version"] = 2
    elif mutation == "producer":
        trace["dbt_version"] = "1.10.0"
    elif mutation == "stage":
        trace["render_stage"] = "after_ephemeral_injection"
    elif mutation == "literal":
        trace["rendered"] = "SELECT 1"
    elif mutation == "offset":
        trace["events"][0]["source_end"] = 99999
    elif mutation == "gap":
        trace["events"] = []
    else:
        trace["events"][0]["kind"] = "unknown"
    with pytest.raises(SQLTemplaterError):
        trace_to_templated_file(trace, traces["literal"]["source"], "model.sql")


def test_utf8_boundary(traces):
    """A byte offset inside a multibyte character is never a writable boundary."""
    trace = traces["unicode_crlf"]
    trace["events"][0]["source_end"] = trace["source"].encode().index(b"\xc3") + 1
    with pytest.raises(SQLTemplaterError):
        trace_to_templated_file(trace, trace["source"], "model.sql")


def test_protocol_compatibility_not_commit_identity(traces):
    """Accept compatible protocol producers without pinning a dbt build or SHA."""
    trace = traces["literal"]
    trace["dbt_version"] = "2.99.0"
    trace["new_optional_metadata"] = True
    assert trace_to_templated_file(trace, trace["source"], "m.sql").templated_str


def test_elif_duplicate_close_is_a_templater_error():
    """The original producer bug must not reach the Rust lexer's block stack."""
    trace = json.loads(
        (Path(__file__).parent / "fixtures/elif_duplicate.json").read_text(
            encoding="utf-8"
        )
    )
    with pytest.raises(SQLTemplaterError, match="unmatched block_end"):
        trace_to_templated_file(trace, trace["source"], "model.sql")
