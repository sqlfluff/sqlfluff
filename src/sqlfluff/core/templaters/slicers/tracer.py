"""'Trace' Jinja template execution to map output back to the raw template.

This is a newer slicing algorithm that handles cases heuristic.py does not.
"""

# Import annotations for py 3.7 to allow `regex.Match[str]`
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List, NamedTuple, Optional, Tuple, Union, cast

import regex
from jinja2 import Environment
from jinja2.exceptions import TemplateSyntaxError

from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFileSlice

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")


class JinjaTrace(NamedTuple):
    """Returned by JinjaTracer.trace()."""

    # Template output
    templated_str: str
    # Raw (i.e. before rendering) Jinja template sliced into tokens
    raw_sliced: List[RawFileSlice]
    # Rendered Jinja template (i.e. output) mapped back to rwa_str source
    sliced_file: List[TemplatedFileSlice]


@dataclass
class RawSliceInfo:
    """JinjaTracer-specific info about each RawFileSlice."""

    unique_alternate_id: Optional[str]
    alternate_code: Optional[str]
    next_slice_indices: List[int] = field(default_factory=list)
    inside_block: bool = field(default=False)  # {% block %}


class JinjaTracer:
    """Records execution path of a Jinja template."""

    def __init__(
        self,
        raw_str: str,
        raw_sliced: List[RawFileSlice],
        raw_slice_info: Dict[RawFileSlice, RawSliceInfo],
        sliced_file: List[TemplatedFileSlice],
        render_func: Callable[[str], str],
    ):
        # Input
        self.raw_str = raw_str
        self.raw_sliced = raw_sliced
        self.raw_slice_info = raw_slice_info
        self.sliced_file = sliced_file
        self.render_func = render_func

        # Internal bookkeeping
        self.program_counter: int = 0
        self.source_idx: int = 0

    def trace(
        self,
        append_to_templated: str = "",
    ) -> JinjaTrace:
        """Executes raw_str. Returns template output and trace."""
        trace_template_str = "".join(
            (
                cast(str, self.raw_slice_info[rs].alternate_code)
                if self.raw_slice_info[rs].alternate_code is not None
                else rs.raw
            )
            for rs in self.raw_sliced
        )
        trace_template_output = self.render_func(trace_template_str)
        # Split output by section. Each section has two possible formats.
        trace_entries: List[regex.Match[str]] = list(
            regex.finditer(r"\0", trace_template_output)
        )
        # If the file has no templated entries, we should just iterate
        # through the raw slices to add all the placeholders.
        if not trace_entries:
            for raw_idx, _ in enumerate(self.raw_sliced):
                self.record_trace(0, raw_idx)

        for match_idx, match in enumerate(trace_entries):
            pos1 = match.span()[0]
            try:
                pos2 = trace_entries[match_idx + 1].span()[0]
            except IndexError:
                pos2 = len(trace_template_output)
            p = trace_template_output[pos1 + 1 : pos2]
            m_id = regex.match(r"^([0-9a-f]+)(_(\d+))?", p)
            if not m_id:
                raise ValueError(  # pragma: no cover
                    "Internal error. Trace template output does not match expected "
                    "format."
                )
            if m_id.group(3):
                # E.g. "00000000000000000000000000000001_83". The number after
                # "_" is the length (in characters) of a corresponding literal
                # in raw_str.
                alt_id, slice_length = m_id.group(1), int(m_id.group(3))
            else:
                # E.g. "00000000000000000000000000000002 a < 10". The characters
                # after the slice ID are executable code from raw_str.
                alt_id, slice_length = m_id.group(0), len(p[len(m_id.group(0)) + 1 :])

            target_slice_idx = self.find_slice_index(alt_id)
            target_inside_block = self.raw_slice_info[
                self.raw_sliced[target_slice_idx]
            ].inside_block
            if not target_inside_block:
                # Normal case: Walk through the template.
                self.move_to_slice(target_slice_idx, slice_length)
            else:
                # {% block %} executes code elsewhere in the template but does
                # not move there. It's a bit like macro invocation.
                self.record_trace(slice_length, target_slice_idx)

        # TRICKY: The 'append_to_templated' parameter is only used by the dbt
        # templater, passing "\n" for this parameter if we need to add one back.
        # (The Jinja templater does not pass this parameter, so
        # 'append_to_templated' gets the default value of "", empty string.)
        # For more detail, see the comments near the call to slice_file() in
        # plugins/sqlfluff-templater-dbt/sqlfluff_templater_dbt/templater.py.
        templated_str = self.render_func(self.raw_str) + append_to_templated
        return JinjaTrace(templated_str, self.raw_sliced, self.sliced_file)

    def find_slice_index(self, slice_identifier: Union[int, str]) -> int:
        """Given a slice identifier, return its index.

        A slice identifier is a string like 00000000000000000000000000000002.
        """
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

    def move_to_slice(
        self,
        target_slice_idx: int,
        target_slice_length: int,
    ) -> Dict[int, List[int]]:
        """Given a template location, walk execution to that point.

        This updates the internal `program_counter` to the appropriate
        location.

        Returns:
            :obj:`dict`: For each step in the template, a :obj:`list` of
                which steps are accessible. In many cases each step will
                only have one accessible next step (the following one),
                however for branches in the program there may be more than
                one.
        """
        step_candidates = {}
        while self.program_counter < len(self.raw_sliced):
            self.record_trace(
                target_slice_length if self.program_counter == target_slice_idx else 0
            )
            current_raw_slice = self.raw_sliced[self.program_counter]
            if self.program_counter == target_slice_idx:
                # Reached the target slice. Go to next location and stop.
                self.program_counter += 1
                break

            # Choose the next step.
            # We could simply go to the next slice (sequential execution).
            candidates = [self.program_counter + 1]
            # If we have other options, consider those.
            candidates.extend(
                filter(
                    # They're a valid possibility if
                    # they don't take us past the target.
                    lambda idx: idx <= target_slice_idx,
                    self.raw_slice_info[current_raw_slice].next_slice_indices,
                )
            )
            # Choose the candidate that takes us closest to the target.
            candidates.sort(key=lambda c: abs(target_slice_idx - c))
            # Save all the candidates for each step so we can return them later.
            step_candidates[self.program_counter] = candidates
            # Step forward to the best step found.
            self.program_counter = candidates[0]

        # Return the candidates at each step.
        return step_candidates

    def record_trace(
        self,
        target_slice_length: int,
        slice_idx: Optional[int] = None,
        slice_type: Optional[str] = None,
    ) -> None:
        """Add the specified (default: current) location to the trace.

        Args:
            target_slice_length (int): The length of the target slice.
            slice_idx (Optional[int], optional): The index of the slice.
            Defaults to None.
            slice_type (Optional[str], optional): The type of the slice.
            Defaults to None.
        """
        if slice_idx is None:
            slice_idx = self.program_counter
        if slice_type is None:
            slice_type = self.raw_sliced[slice_idx].slice_type
        self.sliced_file.append(
            TemplatedFileSlice(
                slice_type,
                slice(
                    self.raw_sliced[slice_idx].source_idx,
                    (
                        self.raw_sliced[slice_idx + 1].source_idx
                        if slice_idx + 1 < len(self.raw_sliced)
                        else len(self.raw_str)
                    ),
                ),
                slice(self.source_idx, self.source_idx + target_slice_length),
            )
        )
        if target_slice_length:
            self.source_idx += target_slice_length


@dataclass(frozen=True)
class JinjaTagConfiguration:
    """Provides information about a Jinja tag and how it affects JinjaAnalyzer behavior.

    Attributes:
        block_type (str): The block type that the Jinja tag maps to; eventually stored
            in TemplatedFileSlice.slice_type and RawFileSlice.slice_type.
        block_tracking (bool): Whether the Jinja tag should be traced by JinjaTracer.
            If True, the Jinja tag will be treated as a conditional block similar to a
            "for/endfor" or "if/else/endif" block, and JinjaTracer will track potential
            execution path through the block.
        block_may_loop (bool): Whether the Jinja tag begins a block that might loop,
            similar to a "for" tag.  If True, JinjaTracer will track the execution path
            through the block and record a potential backward jump to the loop
            beginning.
    """

    block_type: str
    block_tracking: bool = False
    block_may_loop: bool = False


class JinjaAnalyzer:
    """Analyzes a Jinja template to prepare for tracing."""

    re_open_tag = regex.compile(r"^\s*({[{%])[\+\-]?\s*")
    re_close_tag = regex.compile(r"\s*[\+\-]?([}%]})\s*$")

    def __init__(self, raw_str: str, env: Environment) -> None:
        # Input
        self.raw_str: str = raw_str
        self.env = env

        # Output
        self.raw_sliced: List[RawFileSlice] = []
        self.raw_slice_info: Dict[RawFileSlice, RawSliceInfo] = {}
        self.sliced_file: List[TemplatedFileSlice] = []

        # Internal bookkeeping
        self.slice_id: int = 0
        # {% set %} or {% macro %} or {% call %}
        self.inside_set_macro_or_call: bool = False
        self.inside_block = False  # {% block %}
        self.stack: List[int] = []
        self.idx_raw: int = 0

    __known_tag_configurations = {
        # Conditional blocks: "if/elif/else/endif" blocks
        "if": JinjaTagConfiguration(
            block_type="block_start",
            block_tracking=True,
        ),
        "elif": JinjaTagConfiguration(
            block_type="block_mid",
            block_tracking=True,
        ),
        # NOTE: "else" is also used in for loops if there are no iterations
        "else": JinjaTagConfiguration(
            block_type="block_mid",
            block_tracking=True,
        ),
        "endif": JinjaTagConfiguration(
            block_type="block_end",
            block_tracking=True,
        ),
        # Conditional blocks: "for" loops
        "for": JinjaTagConfiguration(
            block_type="block_start",
            block_tracking=True,
            block_may_loop=True,
        ),
        "endfor": JinjaTagConfiguration(
            block_type="block_end",
            block_tracking=True,
        ),
        # Inclusions and imports
        # :TRICKY: Syntactically, the Jinja {% include %} directive looks like
        # a block, but its behavior is basically syntactic sugar for
        # {{ open("somefile).read() }}. Thus, treat it as templated code.
        # It's a similar situation with {% import %} and {% from ... import %}.
        "include": JinjaTagConfiguration(
            block_type="templated",
        ),
        "import": JinjaTagConfiguration(
            block_type="templated",
        ),
        "from": JinjaTagConfiguration(
            block_type="templated",
        ),
        "extends": JinjaTagConfiguration(
            block_type="block_start",
        ),
        # Macros and macro-like tags
        "macro": JinjaTagConfiguration(
            block_type="block_start",
        ),
        "endmacro": JinjaTagConfiguration(
            block_type="block_end",
        ),
        "call": JinjaTagConfiguration(
            block_type="block_start",
        ),
        "endcall": JinjaTagConfiguration(
            block_type="block_end",
        ),
        "set": JinjaTagConfiguration(
            block_type="block_start",
        ),
        "endset": JinjaTagConfiguration(
            block_type="block_end",
        ),
        "block": JinjaTagConfiguration(
            block_type="block_start",
        ),
        "endblock": JinjaTagConfiguration(
            block_type="block_end",
        ),
        "filter": JinjaTagConfiguration(
            block_type="block_start",
        ),
        "endfilter": JinjaTagConfiguration(
            block_type="block_end",
        ),
        # Common extensions
        # Expression statement (like {{ ... }} but doesn't actually print anything)
        "do": JinjaTagConfiguration(
            block_type="templated",
        ),
    }

    @classmethod
    def _get_tag_configuration(cls, tag: str) -> JinjaTagConfiguration:
        """Return information about the behaviors of a tag."""
        # Ideally, we should have a known configuration for this Jinja tag.  Derived
        # classes can override this method to provide additional information about the
        # tags they know about.
        known_cfg = cls.__known_tag_configurations.get(tag, None)
        if known_cfg:
            return known_cfg

        # If we don't have a firm configuration for this tag that is most likely
        # provided by a Jinja extension, we'll try to make some guesses about it based
        # on some heuristics.  But there's a decent chance we'll get this wrong, and
        # the user should instead consider overriding this method in a derived class to
        # handle their tag types.
        if tag.startswith("end"):
            return JinjaTagConfiguration(
                block_type="block_end",
            )
        elif tag.startswith("el"):
            # else, elif
            return JinjaTagConfiguration(
                block_type="block_mid",
            )
        return JinjaTagConfiguration(
            block_type="block_start",
        )

    def next_slice_id(self) -> str:
        """Returns a new, unique slice ID."""
        result = "{0:#0{1}x}".format(self.slice_id, 34)[2:]
        self.slice_id += 1
        return result

    def slice_info_for_literal(self, length: int, prefix: str = "") -> RawSliceInfo:
        """Returns a RawSliceInfo for a literal.

        In the alternate template, literals are replaced with a uniquely
        numbered, easy-to-parse literal. JinjaTracer uses this output as
        a "breadcrumb trail" to deduce the execution path through the template.

        This is important even if the original literal (i.e. in the raw SQL
        file) was empty, as is the case when Jinja whitespace control is used
        (e.g. "{%- endif -%}"), because fewer breadcrumbs means JinjaTracer has
        to *guess* the path, in which case it assumes simple, straight-line
        execution, which can easily be wrong with loops and conditionals.
        """
        unique_alternate_id = self.next_slice_id()
        alternate_code = f"\0{prefix}{unique_alternate_id}_{length}"
        return self.make_raw_slice_info(
            unique_alternate_id, alternate_code, inside_block=self.inside_block
        )

    def update_inside_set_call_macro_or_block(
        self,
        block_type: str,
        trimmed_parts: List[str],
        m_open: Optional[regex.Match[str]],
        m_close: Optional[regex.Match[str]],
        tag_contents: List[str],
    ) -> Tuple[Optional[RawSliceInfo], str]:
        """Based on block tag, update whether in a set/call/macro/block section."""
        if block_type == "block_start" and trimmed_parts[0] in (
            "block",
            "call",
            "macro",
            "set",
        ):
            # Jinja supports two forms of {% set %}:
            # - {% set variable = value %}
            # - {% set variable %}value{% endset %}
            # https://jinja.palletsprojects.com/en/2.10.x/templates/#block-assignments
            # When the second format is used, set one of the fields
            # 'inside_set_or_macro' or 'inside_block' to True. This info is
            # used elsewhere, as other code inside these regions require
            # special handling. (Generally speaking, JinjaAnalyzer ignores
            # the contents of these blocks, treating them like opaque templated
            # regions.)
            try:
                # Entering a set/macro block. Build a source string consisting
                # of just this one Jinja command and see if it parses. If so,
                # it's a standalone command. OTOH, if it fails with "Unexpected
                # end of template", it was the opening command for a block.
                self.env.from_string(
                    f"{self.env.block_start_string} {' '.join(trimmed_parts)} "
                    f"{self.env.block_end_string}"
                )
                # Here we should mutate the block type to just templated
                # so we don't treat it as a block.
                # https://github.com/sqlfluff/sqlfluff/issues/3750
                block_type = "templated"
            except TemplateSyntaxError as e:
                if (
                    isinstance(e.message, str)
                    and "Unexpected end of template" in e.message
                ):
                    # It was opening a block, thus we're inside a set, macro, or
                    # block.
                    if trimmed_parts[0] == "block":
                        self.inside_block = True
                    else:
                        result = None
                        if trimmed_parts[0] == "call":
                            assert m_open and m_close
                            result = self.track_call(m_open, m_close, tag_contents)
                        self.inside_set_macro_or_call = True
                        return result, block_type
                else:
                    raise  # pragma: no cover
        elif block_type == "block_end":
            if trimmed_parts[0] in ("endcall", "endmacro", "endset"):
                # Exiting a set or macro or block.
                self.inside_set_macro_or_call = False
            elif trimmed_parts[0] == "endblock":
                # Exiting a {% block %} block.
                self.inside_block = False
        return None, block_type

    def make_raw_slice_info(
        self,
        unique_alternate_id: Optional[str],
        alternate_code: Optional[str],
        inside_block: bool = False,
    ) -> RawSliceInfo:
        """Create RawSliceInfo as given, or "empty" if in set/macro block."""
        if not self.inside_set_macro_or_call:
            return RawSliceInfo(unique_alternate_id, alternate_code, [], inside_block)
        else:
            return RawSliceInfo(None, None, [], False)

    # We decide the "kind" of element we're dealing with using its _closing_
    # tag rather than its opening tag. The types here map back to similar types
    # of sections in the python slicer.
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

    def analyze(self, render_func: Callable[[str], str]) -> JinjaTracer:
        """Slice template in jinja."""
        # str_buff and str_parts are two ways we keep track of tokens received
        # from Jinja. str_buff concatenates them together, while str_parts
        # accumulates the individual strings. We generally prefer using
        # str_parts. That's because Jinja doesn't just split on whitespace, so
        # by keeping tokens as Jinja returns them, the code is more robust.
        # Consider the following:
        #   {% set col= "col1" %}
        # Note there's no space after col. Jinja splits this up for us. If we
        # simply concatenated the parts together and later split on whitespace,
        # we'd need some ugly, fragile logic to handle various whitespace
        # possibilities:
        #   {% set col= "col1" %}
        #   {% set col = "col1" %}
        #   {% set col ="col1" %}
        # By using str_parts and letting Jinja handle this, it just works.

        str_buff = ""
        str_parts = []

        # https://jinja.palletsprojects.com/en/2.11.x/api/#jinja2.Environment.lex
        block_idx = 0
        for _, elem_type, raw in self.env.lex(self.raw_str):
            if elem_type == "data":
                self.track_literal(raw, block_idx)
                continue
            str_buff += raw
            str_parts.append(raw)

            if elem_type.endswith("_begin"):
                self.handle_left_whitespace_stripping(raw, block_idx)

            raw_slice_info: RawSliceInfo = self.make_raw_slice_info(None, None)
            tag_contents = []
            # raw_end and raw_begin behave a little differently in
            # that the whole tag shows up in one go rather than getting
            # parts of the tag at a time.
            m_open = None
            m_close = None
            if elem_type.endswith("_end") or elem_type == "raw_begin":
                block_type = self.block_types[elem_type]
                block_tag = None
                # Handle starts and ends of blocks
                if block_type in ("block", "templated"):
                    m_open = self.re_open_tag.search(str_parts[0])
                    m_close = self.re_close_tag.search(str_parts[-1])
                    if m_open and m_close:
                        tag_contents = self.extract_tag_contents(
                            str_parts, m_close, m_open, str_buff
                        )

                    if block_type == "block" and tag_contents:
                        block_type = self._get_tag_configuration(
                            tag_contents[0]
                        ).block_type
                        block_tag = tag_contents[0]
                    if block_type == "templated" and tag_contents:
                        assert m_open and m_close
                        raw_slice_info = self.track_templated(
                            m_open, m_close, tag_contents
                        )
                (
                    raw_slice_info_temp,
                    block_type,
                ) = self.update_inside_set_call_macro_or_block(
                    block_type, tag_contents, m_open, m_close, tag_contents
                )
                if raw_slice_info_temp:
                    raw_slice_info = raw_slice_info_temp
                m_strip_right = regex.search(
                    r"\s+$", raw, regex.MULTILINE | regex.DOTALL
                )
                if block_type == "block_start":
                    block_idx += 1
                if elem_type.endswith("_end") and raw.startswith("-") and m_strip_right:
                    # Right whitespace was stripped after closing block. Split
                    # off the trailing whitespace into a separate slice. The
                    # desired behavior is to behave similarly as the left
                    # stripping case. Note that the stakes are a bit lower here,
                    # because lex() hasn't *omitted* any characters from the
                    # strings it returns, it has simply grouped them differently
                    # than we want.
                    trailing_chars = len(m_strip_right.group(0))
                    self.raw_sliced.append(
                        RawFileSlice(
                            str_buff[:-trailing_chars],
                            block_type,
                            self.idx_raw,
                            block_idx,
                            block_tag,
                        )
                    )
                    self.raw_slice_info[self.raw_sliced[-1]] = raw_slice_info
                    slice_idx = len(self.raw_sliced) - 1
                    self.idx_raw += len(str_buff) - trailing_chars
                    if block_type == "block_end":
                        block_idx += 1
                    self.raw_sliced.append(
                        RawFileSlice(
                            str_buff[-trailing_chars:],
                            "literal",
                            self.idx_raw,
                            block_idx,
                        )
                    )
                    self.raw_slice_info[self.raw_sliced[-1]] = (
                        self.slice_info_for_literal(0)
                    )
                    self.idx_raw += trailing_chars
                else:
                    self.raw_sliced.append(
                        RawFileSlice(
                            str_buff,
                            block_type,
                            self.idx_raw,
                            block_idx,
                            block_tag,
                        )
                    )
                    self.raw_slice_info[self.raw_sliced[-1]] = raw_slice_info
                    slice_idx = len(self.raw_sliced) - 1
                    self.idx_raw += len(str_buff)
                    if block_type == "block_end":
                        block_idx += 1
                if block_type.startswith("block"):
                    self.track_block_end(block_type, tag_contents[0])
                    self.update_next_slice_indices(
                        slice_idx, block_type, tag_contents[0]
                    )
                str_buff = ""
                str_parts = []
        return JinjaTracer(
            self.raw_str,
            self.raw_sliced,
            self.raw_slice_info,
            self.sliced_file,
            render_func,
        )

    def track_templated(
        self,
        m_open: regex.Match[str],
        m_close: regex.Match[str],
        tag_contents: List[str],
    ) -> RawSliceInfo:
        """Compute tracking info for Jinja templated region, e.g. {{ foo }}.

        Args:
            m_open (regex.Match): A regex match object representing the opening tag.
            m_close (regex.Match): A regex match object representing the closing tag.
            tag_contents (List[str]): A list of strings representing the contents of the
                tag.

        Returns:
            RawSliceInfo: A RawSliceInfo object containing the computed
            tracking info.
        """
        unique_alternate_id = self.next_slice_id()
        open_ = m_open.group(1)
        close_ = m_close.group(1)
        # Here, we still need to evaluate the original tag contents, e.g. in
        # case it has intentional side effects, but also return a slice ID
        # for tracking.
        alternate_code = (
            f"\0{unique_alternate_id} {open_} " f"{''.join(tag_contents)} {close_}"
        )
        return self.make_raw_slice_info(unique_alternate_id, alternate_code)

    def track_call(
        self,
        m_open: regex.Match[str],
        m_close: regex.Match[str],
        tag_contents: List[str],
    ) -> RawSliceInfo:
        """Set up tracking for "{% call ... %}".

        Args:
            m_open (regex.Match): A regex match object representing the opening tag.
            m_close (regex.Match): A regex match object representing the closing tag.
            tag_contents (List[str]): A list of strings representing the contents of the
                tag.

        Returns:
            RawSliceInfo: A RawSliceInfo object containing the computed
            tracking info.
        """
        unique_alternate_id = self.next_slice_id()
        open_ = m_open.group(1)
        close_ = m_close.group(1)
        # Here, we still need to evaluate the original tag contents, e.g. in
        # case it has intentional side effects, but also return a slice ID
        # for tracking.
        alternate_code = (
            f"\0{unique_alternate_id} {open_} " f"{''.join(tag_contents)} {close_}"
        )
        return self.make_raw_slice_info(unique_alternate_id, alternate_code)

    def track_literal(self, raw: str, block_idx: int) -> None:
        """Set up tracking for a Jinja literal."""
        self.raw_sliced.append(
            RawFileSlice(
                raw,
                "literal",
                self.idx_raw,
                block_idx,
            )
        )
        # Replace literal text with a unique ID.
        self.raw_slice_info[self.raw_sliced[-1]] = self.slice_info_for_literal(
            len(raw), ""
        )
        self.idx_raw += len(raw)

    @staticmethod
    def extract_tag_contents(
        str_parts: List[str],
        m_close: regex.Match[str],
        m_open: regex.Match[str],
        str_buff: str,
    ) -> List[str]:
        """Given Jinja tag info, return the stuff inside the braces.

        I.e. Trim off the brackets and the whitespace.

        Args:
            str_parts (List[str]): A list of string parts.
            m_close (regex.Match[str]): The regex match for the closing tag.
            m_open (regex.Match[str]): The regex match for the opening tag.
            str_buff (str): The string buffer.

        Returns:
            List[str]: The trimmed parts inside the Jinja tag.
        """
        if len(str_parts) >= 3:
            # Handle a tag received as individual parts.
            trimmed_parts = str_parts[1:-1]
            if trimmed_parts[0].isspace():
                del trimmed_parts[0]
            if trimmed_parts[-1].isspace():
                del trimmed_parts[-1]
        else:
            # Handle a tag received in one go.
            trimmed_content = str_buff[len(m_open.group(0)) : -len(m_close.group(0))]
            trimmed_parts = trimmed_content.split()
        return trimmed_parts

    def track_block_end(self, block_type: str, tag_name: str) -> None:
        """On ending a 'for' or 'if' block, set up tracking.

        Args:
            block_type (str): The type of block ('block_start', 'block_mid',
                'block_end').
            tag_name (str): The name of the tag ('for', 'if', or other configured tag).
        """
        if (
            block_type == "block_end"
            and self._get_tag_configuration(tag_name).block_tracking
        ):
            # Replace RawSliceInfo for this slice with one that has alternate ID
            # and code for tracking. This ensures, for instance, that if a file
            # ends with "{% endif %} (with no newline following), that we still
            # generate a TemplateSliceInfo for it.
            unique_alternate_id = self.next_slice_id()
            alternate_code = f"{self.raw_sliced[-1].raw}\0{unique_alternate_id}_0"
            self.raw_slice_info[self.raw_sliced[-1]] = self.make_raw_slice_info(
                unique_alternate_id, alternate_code
            )

    def update_next_slice_indices(
        self, slice_idx: int, block_type: str, tag_name: str
    ) -> None:
        """Based on block, update conditional jump info."""
        if (
            block_type == "block_start"
            and self._get_tag_configuration(tag_name).block_tracking
        ):
            self.stack.append(slice_idx)
            return None
        elif not self.stack:
            return None

        _idx = self.stack[-1]
        _raw_slice = self.raw_sliced[_idx]
        _slice_info = self.raw_slice_info[_raw_slice]
        if (
            block_type == "block_mid"
            and self._get_tag_configuration(tag_name).block_tracking
        ):
            # Record potential forward jump over this block.
            _slice_info.next_slice_indices.append(slice_idx)
            self.stack.pop()
            self.stack.append(slice_idx)
        elif (
            block_type == "block_end"
            and self._get_tag_configuration(tag_name).block_tracking
        ):
            if not self.inside_set_macro_or_call:
                # Record potential forward jump over this block.
                _slice_info.next_slice_indices.append(slice_idx)
                self.stack.pop()
                if _raw_slice.slice_type == "block_start":
                    assert _raw_slice.tag
                    if self._get_tag_configuration(_raw_slice.tag).block_may_loop:
                        # Record potential backward jump to the loop beginning.
                        self.raw_slice_info[
                            self.raw_sliced[slice_idx]
                        ].next_slice_indices.append(_idx + 1)

    def handle_left_whitespace_stripping(self, token: str, block_idx: int) -> None:
        """If block open uses whitespace stripping, record it.

        When a "begin" tag (whether block, comment, or data) uses whitespace
        stripping
        (https://jinja.palletsprojects.com/en/3.0.x/templates/#whitespace-control)
        the Jinja lex() function handles this by discarding adjacent whitespace
        from 'raw_str'. For more insight, see the tokeniter() function in this file:
        https://github.com/pallets/jinja/blob/main/src/jinja2/lexer.py

        We want to detect and correct for this in order to:
        - Correctly update "idx" (if this is wrong, that's a potential
          DISASTER because lint fixes use this info to update the source file,
          and incorrect values often result in CORRUPTING the user's file so
          it's no longer valid SQL. :-O
        - Guarantee that the slices we return fully "cover" the contents of
          'in_str'.

        We detect skipped characters by looking ahead in in_str for the token
        just returned from lex(). The token text will either be at the current
        'idx_raw' position (if whitespace stripping did not occur) OR it'll be
        farther along in 'raw_str', but we're GUARANTEED that lex() only skips
        over WHITESPACE; nothing else.
        """
        # Find the token returned. Did lex() skip over any characters?
        num_chars_skipped = self.raw_str.index(token, self.idx_raw) - self.idx_raw
        if not num_chars_skipped:
            return

        # Yes. It skipped over some characters. Compute a string
        # containing the skipped characters.
        skipped_str = self.raw_str[self.idx_raw : self.idx_raw + num_chars_skipped]

        # Sanity check: Verify that Jinja only skips over
        # WHITESPACE, never anything else.
        if not skipped_str.isspace():  # pragma: no cover
            templater_logger.warning(
                "Jinja lex() skipped non-whitespace: %s", skipped_str
            )
        # Treat the skipped whitespace as a literal.
        self.raw_sliced.append(
            RawFileSlice(skipped_str, "literal", self.idx_raw, block_idx)
        )
        self.raw_slice_info[self.raw_sliced[-1]] = self.slice_info_for_literal(0)
        self.idx_raw += num_chars_skipped
