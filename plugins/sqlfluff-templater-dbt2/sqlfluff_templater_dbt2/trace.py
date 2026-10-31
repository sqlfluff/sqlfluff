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


class Dbt2TemplatedFile(TemplatedFile):
    """Use proven literal spans without absorbing skipped Jinja at a boundary."""

    def templated_slice_to_source_slice(self, template_slice: slice) -> slice:
        """Map a replacement within one literal emission to its exact source."""
        if template_slice.start < template_slice.stop:
            for item in self.sliced_file:
                if (
                    item.slice_type == "literal"
                    and item.templated_slice.start <= template_slice.start
                    and template_slice.stop <= item.templated_slice.stop
                ):
                    offset = item.source_slice.start - item.templated_slice.start
                    return slice(
                        template_slice.start + offset, template_slice.stop + offset
                    )
        return super().templated_slice_to_source_slice(template_slice)


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


def _raw_slices(source: str, env: Environment) -> list[RawFileSlice]:
    """Retain source whitespace omitted by Jinja2's raw-end tokenization."""
    raw = JinjaAnalyzer(source, env).analyze(lambda _: "").raw_sliced
    result = []
    cursor = 0
    for item in raw:
        # The shared analyzer guesses that unknown extension tags open blocks.
        # Loop-control tags are standalone source-only statements.
        if item.tag in {"break", "continue"}:
            item = item._replace(slice_type="templated")
        start = source.index(item.raw, cursor)
        gap = source[cursor:start]
        if gap:
            if not gap.isspace():
                raise ValueError("Jinja lexical analysis omitted non-whitespace source")
            result.append(RawFileSlice(gap, "templated", cursor, item.block_idx))
        result.append(item._replace(source_idx=start))
        cursor = start + len(item.raw)
    if cursor < len(source):
        gap = source[cursor:]
        if not gap.isspace():
            raise ValueError("Jinja lexical analysis omitted non-whitespace source")
        result.append(RawFileSlice(gap, "templated", cursor))
    return result


def _validate_blocks(sliced: list[TemplatedFileSlice]) -> None:
    """Reject invalid layout before it can underflow the lexer's block stack."""
    depth = 0
    for item in sliced:
        if item.slice_type == "block_start":
            depth += 1
        elif item.slice_type == "block_end":
            if not depth:
                raise ValueError(
                    "unmatched block_end in dbt trace at source offset "
                    f"{item.source_slice.start}; update the dbt trace exporter"
                )
            depth -= 1
    if depth:
        raise ValueError("unclosed Jinja blocks in dbt trace")


def _protect_unrendered_tail(
    raw: list[RawFileSlice], sliced: list[TemplatedFileSlice], start: int
) -> list[RawFileSlice]:
    """Keep renderer-stripped text out of patches for wholly literal segments."""
    if not raw or raw[-1].slice_type != "literal":
        return raw
    tail = raw[-1]
    start = max(start, tail.source_idx)
    if start >= tail.end_source_idx() or any(
        item.source_slice.stop > start
        and item.templated_slice.stop > item.templated_slice.start
        for item in sliced
    ):
        return raw
    split = start - tail.source_idx
    prefix = [tail._replace(raw=tail.raw[:split])] if split else []
    return [
        *raw[:-1],
        *prefix,
        tail._replace(raw=tail.raw[split:], source_idx=start, slice_type="templated"),
    ]


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
    raw = _raw_slices(source, env)
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
        if kind == "templated" and src.start == src.stop and dst.start < dst.stop:
            # An empty producer anchor means no editable source origin. Core
            # treats empty source ranges as safe insertions, so use the whole
            # input as a conservative nonliteral diagnostic/fix boundary.
            src = slice(0, len(source))
        if kind == "macro":
            macros.append((src, dst))
        elif kind != "variable":
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
        elif kind == "loop_skipped":
            # Empty recursive invocations share their parent's source tag;
            # the explicit closing event cannot be inferred from source gaps.
            kind = "block_end"
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
        # dbt strips the final newline. It remains source text, but must not be
        # included in a literal patch whose replacement is only rendered SQL.
        raw = _protect_unrendered_tail(raw, sliced, source_cursor)
        omitted(len(source))
    if not sliced:
        sliced = [TemplatedFileSlice("literal", slice(0, 0), slice(0, 0))]
    _validate_blocks(sliced)
    return Dbt2TemplatedFile(
        source_str=source,
        fname=fname,
        templated_str=rendered,
        sliced_file=sliced,
        raw_sliced=raw or [RawFileSlice("", "literal", 0)],
    )
