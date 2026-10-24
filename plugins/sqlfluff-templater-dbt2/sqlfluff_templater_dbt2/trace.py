"""Translate dbt's byte-based execution trace into SQLFluff source slices."""

from __future__ import annotations

from typing import Any

from jinja2 import Environment
from packaging.version import Version

from sqlfluff.core.errors import SQLTemplaterError
from sqlfluff.core.templaters.base import (
    RawFileSlice,
    TemplatedFile,
    TemplatedFileSlice,
)
from sqlfluff.core.templaters.slicers.tracer import JinjaAnalyzer


def normalize_newlines(value: str) -> str:
    """Follow SQLFluff's source loader when crossing the Rust file boundary."""
    return value.replace("\r\n", "\n").replace("\r", "\n")


def _byte_positions(value: str) -> dict[int, int]:
    positions = {0: 0}
    byte = 0
    index = 0
    previous = ""
    for char in value:
        byte += len(char.encode("utf-8"))
        if not (previous == "\r" and char == "\n"):
            index += 1
        positions[byte] = index
        previous = char
    return positions


def trace_to_templated_file(
    trace: dict[str, Any], source: str, fname: str
) -> TemplatedFile:
    """Validate provenance before making any source region eligible for fixing."""
    try:
        return _convert_trace(trace, source, fname)
    except (KeyError, TypeError, ValueError, AssertionError) as error:
        raise SQLTemplaterError(f"Invalid dbt2 render trace: {error}") from error


def _convert_trace(trace: dict[str, Any], source: str, fname: str) -> TemplatedFile:
    if not isinstance(trace, dict) or not isinstance(trace["source"], str):
        raise TypeError("trace must be an object containing string source")
    if type(trace["protocol_version"]) is not int or trace["protocol_version"] != 1:
        raise ValueError("unsupported trace protocol")
    if Version(trace["dbt_version"]).major < 2:
        raise ValueError("trace requires dbt v2")
    if trace["render_stage"] != "jinja_before_ephemeral_injection":
        raise ValueError("unsupported trace render stage")
    source = normalize_newlines(source)
    if normalize_newlines(trace["source"]) != source:
        raise ValueError("source differs from the compiled source; recompile the model")
    raw_rendered = trace["rendered"]
    if not isinstance(raw_rendered, str):
        raise TypeError("rendered SQL must be a string")
    rendered = normalize_newlines(raw_rendered)
    source_positions = _byte_positions(trace["source"])
    rendered_positions = _byte_positions(raw_rendered)
    # Only lexical analysis is done in Python. Rendering and control flow are
    # exclusively dbt MiniJinja's, including ambiguous identical branch output.
    env = Environment(
        extensions=["jinja2.ext.do", "jinja2.ext.loopcontrols"],
        keep_trailing_newline=True,
    )
    raw = JinjaAnalyzer(source, env).analyze(lambda _: "").raw_sliced
    events: list[tuple[str, slice, slice]] = []
    macros: list[tuple[slice, slice]] = []
    for event in trace["events"]:
        kind = event["kind"]
        if kind not in {
            "literal",
            "templated",
            "macro",
            "block_start",
            "block_mid",
            "block_end",
            "block_standalone",
            "comment",
            "variable",
            "loop_iteration",
            "loop_skipped",
        }:
            raise ValueError(f"unknown event kind {kind!r}")
        values = [
            event[key]
            for key in ("source_start", "source_end", "rendered_start", "rendered_end")
        ]
        if any(type(value) is not int for value in values):
            raise TypeError("span offsets must be integers")
        source_start, source_end, rendered_start, rendered_end = values
        if source_start > source_end or rendered_start > rendered_end:
            raise ValueError("reversed trace span")
        src = slice(source_positions[source_start], source_positions[source_end])
        dst = slice(
            rendered_positions[rendered_start], rendered_positions[rendered_end]
        )
        if kind == "macro":
            macros.append((src, dst))
        elif kind not in {"variable", "loop_skipped"}:
            events.append((kind, src, dst))

    sliced: list[TemplatedFileSlice] = []
    cursor = 0
    source_cursor = 0

    def omitted(stop: int) -> None:
        """Include skipped source text and tags at the current output position."""
        nonlocal source_cursor
        for item in raw:
            start = max(source_cursor, item.source_idx)
            end = min(stop, item.end_source_idx())
            if start < end:
                sliced.append(
                    TemplatedFileSlice(
                        item.slice_type, slice(start, end), slice(cursor, cursor)
                    )
                )
        source_cursor = stop

    def fill_gap(stop: int) -> None:
        """Treat unexposed capture/call output as generated, never as literal."""
        nonlocal cursor, source_cursor
        if stop == cursor:
            return
        candidates = [
            (src, dst)
            for src, dst in macros
            if dst.start <= cursor and dst.stop >= stop
        ]
        if not candidates:
            raise ValueError(f"output [{cursor}:{stop}] has no render provenance")
        src, _ = min(candidates, key=lambda pair: pair[0].stop - pair[0].start)
        sliced.append(TemplatedFileSlice("templated", src, slice(cursor, stop)))
        cursor = stop
        source_cursor = src.stop

    for kind, src, dst in events:
        if dst.start < cursor:
            # Layout callbacks within a captured string can observe a location
            # before its eventual emission. They must not create writable spans.
            if dst.start == dst.stop:
                continue
            raise ValueError("overlapping emitted spans")
        fill_gap(dst.start)
        if src.start > source_cursor:
            omitted(src.start)
        if kind == "loop_iteration":
            kind = "block_start"
        elif kind == "block_standalone":
            kind = "templated"
        if kind == "literal":
            if source[src] != rendered[dst]:
                raise ValueError("literal source and rendered text differ")
        sliced.append(TemplatedFileSlice(kind, src, dst))
        cursor = dst.stop
        source_cursor = src.stop
    fill_gap(len(rendered))
    if source_cursor < len(source):
        omitted(len(source))
    if not sliced:
        sliced = [TemplatedFileSlice("literal", slice(0, 0), slice(0, 0))]
    return TemplatedFile(
        source_str=source,
        fname=fname,
        templated_str=rendered,
        sliced_file=sliced,
        raw_sliced=raw or [RawFileSlice("", "literal", 0)],
    )
