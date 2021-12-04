"""'Trace' Jinja template execution to map output back to the raw template.

This is a newer slicing algorithm that handles cases heuristic.py does not.
"""

import logging
import regex
import uuid
from itertools import chain
from typing import Callable, cast, Dict, List, NamedTuple, Optional

from jinja2 import Environment
from jinja2.environment import Template

from sqlfluff.core.templaters.base import (
    RawFileSlice,
    TemplatedFileSlice,
)


# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")


class JinjaTrace(NamedTuple):
    """Returned by JinjaTracer.process()."""

    # Template output
    templated_str: str
    # Raw (i.e. before rendering) Jinja template sliced into tokens
    raw_sliced: List[RawFileSlice]
    # Rendered Jinja template (i.e. output) mapped back to rwa_str source
    sliced_file: List[TemplatedFileSlice]


class RawSliceInfo(NamedTuple):
    """JinjaTracer-specific info about each RawFileSlice."""

    unique_alternate_id: Optional[str]
    alternate_code: Optional[str]
    next_slice_indices: List[int]


class JinjaTracer:
    """Deduces and records execution path of a Jinja template."""

    re_open_tag = regex.compile(r"^\s*({[{%])[\+\-]?\s*")
    re_close_tag = regex.compile(r"\s*[\+\-]?([}%]})\s*$")

    def __init__(
        self, raw_str: str, env: Environment, make_template: Callable[[str], Template]
    ):
        self.raw_str: str = raw_str
        self.env = env
        self.make_template: Callable[[str], Template] = make_template
        self.program_counter: int = 0
        self.raw_slice_info: Dict[RawFileSlice, RawSliceInfo] = {}
        self.raw_sliced: List[RawFileSlice] = self._slice_template()
        self.sliced_file: List[TemplatedFileSlice] = []
        self.source_idx: int = 0

    def trace(self) -> JinjaTrace:
        """Executes raw_str. Returns template output and trace."""
        trace_template_str = "".join(
            cast(str, self.raw_slice_info[rs].alternate_code)
            if self.raw_slice_info[rs].alternate_code is not None
            else rs.raw
            for rs in self.raw_sliced
        )
        trace_template = self.make_template(trace_template_str)
        trace_template_output = trace_template.render()
        # Split output by section. Each section has two possible formats.
        for p in trace_template_output.split("\0"):
            if not p:
                continue
            m_id = regex.match(r"^([0-9a-f]+)(_(\d+))?", p)
            if not m_id:
                raise ValueError(  # pragma: no cover
                    "Internal error. Trace template output does not match expected format."
                )
            if m_id.group(3):
                # E.g. "2e8577c1d045439ba8d3b9bf47561de3_83". The number after
                # "_" is the length (in characters) of a corresponding literal
                # in raw_str.
                value = [m_id.group(1), int(m_id.group(3)), True]
            else:
                # E.g. "adc15d2a41d14ead97411bce3fb55e32 a < 10". The characters
                # after the UUID are executable code from raw_str.
                value = [m_id.group(0), p[len(m_id.group(0)) + 1 :], False]
            alt_id, content_info, literal = value
            target_slice_idx = self.find_slice_index(alt_id)
            if literal:
                self.move_to_slice(target_slice_idx, content_info)
            else:
                self.move_to_slice(target_slice_idx, len(str(content_info)))
        return JinjaTrace(
            self.make_template(self.raw_str).render(), self.raw_sliced, self.sliced_file
        )

    def find_slice_index(self, slice_identifier) -> int:
        """Given a slice identifier (UUID string), return its index."""
        raw_slices_search_result = [
            idx
            for idx, rs in enumerate(self.raw_sliced)
            if self.raw_slice_info[rs].unique_alternate_id == slice_identifier
        ]
        if len(raw_slices_search_result) != 1:
            raise ValueError(  # pragma: no cover
                f"Internal error. Unable to locate slice for {slice_identifier}."
            )
        return raw_slices_search_result[0]

    def move_to_slice(self, target_slice_idx, target_slice_length):
        """Given a template location, walk execution to that point."""
        while self.program_counter < len(self.raw_sliced):
            self.record_trace(
                target_slice_length if self.program_counter == target_slice_idx else 0
            )
            current_raw_slice = self.raw_sliced[self.program_counter]
            if self.program_counter == target_slice_idx:
                # Reached the target slice. Go to next location and stop.
                self.program_counter += 1
                break
            elif not self.raw_slice_info[current_raw_slice].next_slice_indices:
                # No choice available. Go to next location.
                self.program_counter += 1
            else:
                # We have choices. Which to choose?
                candidates = []
                for next_slice_idx in chain(
                    self.raw_slice_info[current_raw_slice].next_slice_indices,
                    [self.program_counter + 1],
                ):
                    if next_slice_idx > target_slice_idx:
                        # Takes us past the target. No good.
                        continue
                    candidates.append(next_slice_idx)
                # Choose the path that lands us closest to the target.
                candidates.sort(key=lambda c: abs(target_slice_idx - c))
                self.program_counter = candidates[0]

    def record_trace(self, target_slice_length):
        """Add the current location to the trace."""
        slice_type = self.raw_sliced[self.program_counter].slice_type
        self.sliced_file.append(
            TemplatedFileSlice(
                slice_type,
                slice(
                    self.raw_sliced[self.program_counter].source_idx,
                    self.raw_sliced[self.program_counter + 1].source_idx
                    if self.program_counter + 1 < len(self.raw_sliced)
                    else len(self.raw_str),
                ),
                slice(self.source_idx, self.source_idx + target_slice_length),
            )
        )
        if slice_type in ("literal", "templated"):
            self.source_idx += target_slice_length

    def _slice_template(self) -> List[RawFileSlice]:
        """Slice template in jinja.

        NB: Starts and ends of blocks are not distinguished.
        """
        str_buff = ""
        idx = 0
        # We decide the "kind" of element we're dealing with
        # using it's _closing_ tag rather than it's opening
        # tag. The types here map back to similar types of
        # sections in the python slicer.
        block_types = {
            "variable_end": "templated",
            "block_end": "block",
            "comment_end": "comment",
            # Raw tags should behave like blocks. Note that
            # raw_end and raw_begin are whole tags rather
            # than blocks and comments where we get partial
            # tags.
            "raw_end": "block",
            "raw_begin": "block",
        }

        # https://jinja.palletsprojects.com/en/2.11.x/api/#jinja2.Environment.lex
        stack = []
        result = []
        set_idx = None
        unique_alternate_id: Optional[str]
        alternate_code: Optional[str]
        for _, elem_type, raw in self.env.lex(self.raw_str):
            # Replace literal text with a unique ID, except for "set"
            # statements, which don't emit output and thus don't need this
            # treatment.
            if elem_type == "data":
                if set_idx is None:
                    unique_alternate_id = uuid.uuid4().hex
                    alternate_code = f"{unique_alternate_id}_{len(raw)}\0"
                else:
                    unique_alternate_id = None
                    alternate_code = None
                result.append(
                    RawFileSlice(
                        raw,
                        "literal",
                        idx,
                    )
                )
                self.raw_slice_info[result[-1]] = RawSliceInfo(
                    unique_alternate_id, alternate_code, []
                )
                idx += len(raw)
                continue
            str_buff += raw

            if elem_type.endswith("_begin"):
                # When a "begin" tag (whether block, comment, or data) uses
                # whitespace stripping
                # (https://jinja.palletsprojects.com/en/3.0.x/templates/#whitespace-control),
                # the Jinja lex() function handles this by discarding adjacent
                # whitespace from in_str. For more insight, see the tokeniter()
                # function in this file:
                # https://github.com/pallets/jinja/blob/main/src/jinja2/lexer.py
                # We want to detect and correct for this in order to:
                # - Correctly update "idx" (if this is wrong, that's a
                #   potential DISASTER because lint fixes use this info to
                #   update the source file, and incorrect values often result in
                #   CORRUPTING the user's file so it's no longer valid SQL. :-O
                # - Guarantee that the slices we return fully "cover" the
                #   contents of in_str.
                #
                # We detect skipped characters by looking ahead in in_str for
                # the token just returned from lex(). The token text will either
                # be at the current 'idx' position (if whitespace stripping did
                # not occur) OR it'll be farther along in in_str, but we're
                # GUARANTEED that lex() only skips over WHITESPACE; nothing else.

                # Find the token returned. Did lex() skip over any characters?
                num_chars_skipped = self.raw_str.index(raw, idx) - idx
                if num_chars_skipped:
                    # Yes. It skipped over some characters. Compute a string
                    # containing the skipped characters.
                    skipped_str = self.raw_str[idx : idx + num_chars_skipped]

                    # Sanity check: Verify that Jinja only skips over
                    # WHITESPACE, never anything else.
                    if not skipped_str.isspace():  # pragma: no cover
                        templater_logger.warning(
                            "Jinja lex() skipped non-whitespace: %s", skipped_str
                        )
                    # Treat the skipped whitespace as a literal.
                    result.append(RawFileSlice(skipped_str, "literal", idx))
                    self.raw_slice_info[result[-1]] = RawSliceInfo("", "", [])
                    idx += num_chars_skipped

            # raw_end and raw_begin behave a little differently in
            # that the whole tag shows up in one go rather than getting
            # parts of the tag at a time.
            unique_alternate_id = None
            alternate_code = None
            trimmed_content = ""
            if elem_type.endswith("_end") or elem_type == "raw_begin":
                block_type = block_types[elem_type]
                block_subtype = None
                # Handle starts and ends of blocks
                if block_type in ("block", "templated"):
                    # Trim off the brackets and then the whitespace
                    m_open = self.re_open_tag.search(str_buff)
                    m_close = self.re_close_tag.search(str_buff)
                    if m_open and m_close:
                        trimmed_content = str_buff[
                            len(m_open.group(0)) : -len(m_close.group(0))
                        ]
                    if block_type == "block":
                        if trimmed_content.startswith("end"):
                            block_type = "block_end"
                        elif trimmed_content.startswith("el"):
                            # else, elif
                            block_type = "block_mid"
                        else:
                            block_type = "block_start"
                            if trimmed_content.split()[0] == "for":
                                block_subtype = "loop"
                    else:
                        # For "templated", evaluate the content in case of side
                        # effects, but return a UUID.
                        if trimmed_content:
                            assert m_open and m_close
                            unique_id = uuid.uuid4().hex
                            unique_alternate_id = unique_id
                            alternate_code = f"{unique_alternate_id} {m_open.group(1)} {trimmed_content} {m_close.group(1)}\0"
                if block_type == "block_start" and trimmed_content.split()[0] == "set":
                    # Jinja supports two forms of {% set %}:
                    # - {% set variable = value %}
                    # - {% set variable %}value{% endset %}
                    # https://jinja.palletsprojects.com/en/2.10.x/templates/#block-assignments
                    # When the second format is used, leave the value "as is".
                    # It won't be rendered directly to the template output
                    # anyway, so substituting our special UUID values would just
                    # confuse things.
                    trimmed_content_parts = trimmed_content.split(maxsplit=2)
                    if len(trimmed_content_parts) <= 2 or not trimmed_content_parts[
                        2
                    ].startswith("="):
                        set_idx = len(result)
                elif block_type == "block_end" and set_idx is not None:
                    set_idx = None
                m = regex.search(r"\s+$", raw, regex.MULTILINE | regex.DOTALL)
                if raw.startswith("-") and m:
                    # Right whitespace was stripped. Split off the trailing
                    # whitespace into a separate slice. The desired behavior is
                    # to behave similarly as the left stripping case above.
                    # Note that the stakes are a bit different, because lex()
                    # hasn't *omitted* any characters from the strings it
                    # returns, it has simply grouped them differently than we
                    # want.
                    trailing_chars = len(m.group(0))
                    result.append(
                        RawFileSlice(
                            str_buff[:-trailing_chars],
                            block_type,
                            idx,
                            block_subtype,
                        )
                    )
                    self.raw_slice_info[result[-1]] = RawSliceInfo(
                        unique_alternate_id, alternate_code, []
                    )
                    block_idx = len(result) - 1
                    idx += len(str_buff) - trailing_chars
                    result.append(
                        RawFileSlice(
                            str_buff[-trailing_chars:],
                            "literal",
                            idx,
                        )
                    )
                    self.raw_slice_info[result[-1]] = RawSliceInfo("", "", [])
                    idx += trailing_chars
                else:
                    result.append(
                        RawFileSlice(
                            str_buff,
                            block_type,
                            idx,
                            block_subtype,
                        )
                    )
                    self.raw_slice_info[result[-1]] = RawSliceInfo(
                        unique_alternate_id, alternate_code, []
                    )
                    block_idx = len(result) - 1
                    idx += len(str_buff)
                if block_type == "block_start" and trimmed_content.split()[0] in (
                    "for",
                    "if",
                ):
                    stack.append(block_idx)
                elif block_type == "block_mid":
                    # Record potential forward jump over this block.
                    self.raw_slice_info[result[stack[-1]]].next_slice_indices.append(
                        block_idx
                    )
                    stack.pop()
                    stack.append(block_idx)
                elif block_type == "block_end" and trimmed_content.split()[0] in (
                    "endfor",
                    "endif",
                ):
                    # Record potential forward jump over this block.
                    self.raw_slice_info[result[stack[-1]]].next_slice_indices.append(
                        block_idx
                    )
                    if result[stack[-1]].slice_subtype == "loop":
                        # Record potential backward jump to the loop beginning.
                        self.raw_slice_info[
                            result[block_idx]
                        ].next_slice_indices.append(stack[-1] + 1)
                    stack.pop()
                str_buff = ""
        return result
