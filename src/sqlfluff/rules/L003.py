"""Implementation of Rule L003."""
import dataclasses
import itertools
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from sqlfluff.core.parser import WhitespaceSegment
from sqlfluff.core.parser.segments import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.utils.functional import Segments, rsp, sp
from sqlfluff.core.templaters import TemplatedFile
from sqlfluff.core.templaters.base import RawFileSlice


@dataclasses.dataclass
class _LineSummary:
    """A dataobject to represent a line.

    A _LineSummary is created and then filled with elements,
    before calling self.finalise to generate a final
    representation.
    """

    line_no: int = 0
    line_buffer: List[BaseSegment] = dataclasses.field(default_factory=list)
    indent_buffer: List[BaseSegment] = dataclasses.field(default_factory=list)
    # As of end of line
    indent_balance: int = 0
    # As it was as of the "Anchor" / first code elem
    anchor_indent_balance: int = 0
    line_anchor: Optional[BaseSegment] = None

    # Fixed calculated values
    templated_line: Optional[int] = None
    hanging_indent: Optional[int] = None
    indent_size: int = 1
    clean_indent: bool = True
    templated_line_type: Optional[str] = None
    is_comment_line: bool = False
    is_empty_line: bool = False
    has_code_segment: bool = False

    line_indent_stack: List[int] = dataclasses.field(default_factory=list)
    hanger_pos: Optional[int] = None

    def __repr__(self) -> str:
        """Printable Summary without Segments."""
        keys_to_strip = (
            "line_buffer",
            "indent_buffer",
            "as_of_anchor",
        )
        print_dict: Dict = {
            key: value
            for key, value in self.__dict__.copy().items()
            if key not in keys_to_strip
        }
        print_dict["raw_line"] = self.template_content
        return print_dict.__repr__()

    @property
    def template_content(self):  # pragma: no cover
        return "".join(
            seg.raw or getattr(seg, "source_str", "") for seg in self.line_buffer
        )

    def finalise(self, line_no: int, templated_file: Optional[TemplatedFile]):
        """Create a final summary from a memo/marker line."""
        copied_line_buffer = self.line_buffer[:]
        # Generate our final line summary based on the current state
        is_comment_line = all(
            seg.is_type(
                "whitespace",
                "comment",
                "indent",  # dedent is a subtype of indent
                "end_of_file",
            )
            for seg in copied_line_buffer
        )
        has_code_segment = any(elem.is_code for elem in copied_line_buffer)
        has_placeholder = any(
            elem.is_type("placeholder") for elem in copied_line_buffer
        )
        is_empty_line = not has_code_segment and not has_placeholder

        line_summary = self.__class__(
            line_no=line_no,
            templated_line=self.templated_line,
            line_buffer=copied_line_buffer,
            indent_buffer=self.indent_buffer,
            indent_size=self.indent_size,
            indent_balance=self.indent_balance,
            anchor_indent_balance=self.anchor_indent_balance,
            hanging_indent=self.hanger_pos if self.line_indent_stack else None,
            # Clean indent is true if the line *ends* with an indent
            # or has an indent in the initial whitespace.
            clean_indent=self.clean_indent,
            # Solidify expensive immutable characteristics
            templated_line_type=_get_template_block_type(
                copied_line_buffer, templated_file
            ),
            is_comment_line=is_comment_line,
            is_empty_line=is_empty_line,
            has_code_segment=has_code_segment,
        )
        return line_summary


def _set_line_anchor(
    line: _LineSummary,
    anchor: Optional[BaseSegment],
    tab_space_size: int,
):
    """Create a Line state of this line upon reaching the anchor."""
    line.anchor_indent_balance = line.indent_balance
    line.indent_size = _indent_size(
        line.indent_buffer,
        tab_space_size=tab_space_size,
    )
    line.line_anchor = anchor

    return line


def _is_clean_indent(prev_line_buffer: List[BaseSegment]):
    """Check the previous line to see if the current state is a clean indent."""
    # Assume an unclean indent, but if the last line
    # ended with an indent then we might be ok.
    # Was there an indent after the last code element of the previous line?
    for search_elem in reversed(prev_line_buffer):
        is_meta = search_elem.is_meta
        if not search_elem.is_code and not is_meta:
            continue
        if is_meta and search_elem.indent_val > 0:  # type: ignore
            return True
        break

    return False


@dataclasses.dataclass
class _Memory:
    problem_lines: Set[int] = dataclasses.field(default_factory=set)
    # hanging_lines keeps track of hanging lines so that we don't
    # compare to them when assessing indent.
    hanging_lines: Set[int] = dataclasses.field(default_factory=set)
    comment_lines: Set[int] = dataclasses.field(default_factory=set)
    line_summaries: Dict[int, _LineSummary] = dataclasses.field(default_factory=dict)

    in_indent: bool = True
    trigger: Optional[BaseSegment] = None

    line_no: int = dataclasses.field(default=1)
    start_process_raw_idx: int = dataclasses.field(default=0)

    @property
    def noncomparable_lines(self):
        return self.hanging_lines.union(self.problem_lines)


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L003(BaseRule):
    """Indentation not consistent with previous lines.

    **Anti-pattern**

    The ``•`` character represents a space.
    In this example, the third line contains five spaces instead of four.

    .. code-block:: sql
       :force:

        SELECT
        ••••a,
        •••••b
        FROM foo


    **Best practice**

    Change the indentation to use a multiple of four spaces.

    .. code-block:: sql
       :force:

        SELECT
        ••••a,
        ••••b
        FROM foo

    """

    groups = ("all", "core")
    # This rule is mostly a raw crawler, so not much performance gain to be
    # had from being more specific.
    crawl_behaviour = SegmentSeekerCrawler({"raw"}, provide_raw_stack=True)
    targets_templated = True
    _adjust_anchors = True
    _ignore_types: List[str] = ["script_content"]
    config_keywords = ["tab_space_size", "indent_unit", "hanging_indents"]

    @staticmethod
    def _make_indent(
        num: int = 1, tab_space_size: int = 4, indent_unit: str = "space"
    ) -> str:
        if indent_unit == "tab":
            return "\t" * num
        if indent_unit == "space":
            return " " * tab_space_size * num

        raise ValueError(
            f"Parameter indent_unit has unexpected value: `{indent_unit}`. Expected"
            " `tab` or `space`."
        )

    @staticmethod
    def _indent_size(segments: Sequence[BaseSegment], tab_space_size: int = 4) -> int:
        return _indent_size(segments, tab_space_size)

    @classmethod
    def _process_raw_stack(
        cls,
        raw_stack: Tuple[BaseSegment, ...],
        memory: _Memory,
        tab_space_size: int = 4,
        templated_file: Optional[TemplatedFile] = None,
    ) -> Dict[int, _LineSummary]:
        """Take the raw stack, split into lines and evaluate some stats."""
        result_buffer: Dict[int, _LineSummary] = memory.line_summaries
        cached_line_count = len(result_buffer)
        starting_indent_balance = 0
        if cached_line_count:
            starting_indent_balance = result_buffer[cached_line_count].indent_balance

        working_state = _LineSummary(indent_balance=starting_indent_balance)

        line_no = memory.line_no
        target_line_no = cached_line_count + 1
        for idx, elem in enumerate(raw_stack[memory.start_process_raw_idx :]):
            is_newline = elem.is_type("newline")
            if line_no < target_line_no:
                if is_newline:
                    line_no += 1
                    if line_no == target_line_no:
                        memory.start_process_raw_idx += idx + 1
                        memory.line_no = line_no
                        working_state.templated_line = elem.is_templated
                continue

            working_state.line_buffer.append(elem)
            # Pin indent_balance to above zero
            if working_state.indent_balance < 0:
                working_state.indent_balance = 0

            if is_newline:
                result_buffer[line_no] = working_state.finalise(line_no, templated_file)
                # Set the "templated_line" if the newline that ended the *current* line
                # was in templated space. Reason: We want to ignore indentation of lines
                # not present in the raw (pre-templated) code.
                working_state = _LineSummary(
                    indent_balance=working_state.indent_balance,
                    clean_indent=_is_clean_indent(working_state.line_buffer),
                    templated_line=elem.is_templated,
                )
                line_no += 1
                continue

            if working_state.line_anchor is None:
                working_state = cls._process_pre_anchor(
                    elem, working_state, tab_space_size
                )
                # If we hit the trigger element, stop processing.
                if elem is memory.trigger:
                    break
                continue

            if elem.is_meta and elem.indent_val != 0:  # type: ignore
                working_state = cls._process_line_indents(
                    elem, working_state, tab_space_size
                )
                continue

            elif elem.is_code and working_state.hanger_pos is None:
                working_state.hanger_pos = cls._indent_size(
                    working_state.line_buffer[:-1], tab_space_size=tab_space_size
                )

        # If we get to the end, and still have a buffer, add it on
        if working_state.line_buffer:
            result_buffer[line_no] = working_state.finalise(
                line_no,
                templated_file,
            )
        return result_buffer

    @classmethod
    def _process_line_indents(
        cls,
        elem: BaseSegment,
        working_state: _LineSummary,
        tab_space_size: int,
    ) -> _LineSummary:
        working_state.indent_balance += elem.indent_val  # type: ignore
        if elem.indent_val > 0:  # type: ignore
            # Keep track of the indent at the last ... indent
            working_state.line_indent_stack.append(
                cls._indent_size(
                    working_state.line_buffer, tab_space_size=tab_space_size
                )
            )
            working_state.hanger_pos = None
            return working_state
        # this is a dedent, we could still have a hanging indent,
        # but only if there's enough on the stack
        if working_state.line_indent_stack:
            working_state.line_indent_stack.pop()
        return working_state

    @classmethod
    def _process_pre_anchor(
        cls,
        elem: BaseSegment,
        working_state: _LineSummary,
        tab_space_size: int,
    ) -> _LineSummary:
        if elem.is_whitespace:
            working_state.indent_buffer.append(elem)
            return working_state
        if elem.is_meta and elem.indent_val != 0:  # type: ignore
            working_state.indent_balance += elem.indent_val  # type: ignore
            if elem.indent_val > 0:  # type: ignore
                # a "clean" indent is one where it contains
                # an increase in indentation? Can't quite
                # remember the logic here. Let's go with that.
                working_state.clean_indent = True
            return working_state

        return _set_line_anchor(working_state, elem, tab_space_size)

    def _coerce_indent_to(
        self,
        desired_indent: str,
        current_indent_buffer: List[BaseSegment],
        current_anchor: BaseSegment,
    ) -> List[LintFix]:
        """Generate fixes to make an indent a certain size.

        Rather than blindly creating indent, we should _edit_
        if at all possible, this stops other rules trying to
        remove floating double indents.
        """
        existing_whitespace = [
            seg for seg in current_indent_buffer if seg.is_type("whitespace")
        ]
        # Should we have an indent?
        if len(desired_indent) == 0:
            # No? Just delete everything
            return [LintFix.delete(seg) for seg in existing_whitespace]
        else:
            # Is there already an indent?
            if existing_whitespace:
                # Edit the first, delete the rest.
                edit_fix = LintFix.replace(
                    existing_whitespace[0],
                    [existing_whitespace[0].edit(desired_indent)],
                )
                delete_fixes = [LintFix.delete(seg) for seg in existing_whitespace[1:]]
                return [edit_fix] + delete_fixes
            else:
                # Just create an indent.
                return [
                    LintFix.create_before(
                        current_anchor,
                        [
                            WhitespaceSegment(
                                raw=desired_indent,
                            ),
                        ],
                    )
                ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Indentation not consistent with previous lines.

        To set the default tab size, set the `tab_space_size` value
        in the appropriate configuration.

        We compare each line (first non-whitespace element of the
        line), with the indentation of previous lines. The presence
        (or lack) of indent or dedent meta-characters indicate whether
        the indent is appropriate.

        - Any line is assessed by the indent level at the first non
          whitespace element.
        - Any increase in indentation may be _up to_ the number of
          indent characters.
        - Any line must be in line with the previous line which had
          the same indent balance at its start.
        - Apart from "whole" indents, a "hanging" indent is possible
          if the line starts in line with either the indent of the
          previous line or if it starts at the same indent as the *last*
          indent meta segment in the previous line.

        """
        # Config type hints
        self.tab_space_size: int
        self.indent_unit: str
        self.hanging_indents: bool
        segment = context.segment
        memory: _Memory = context.memory or _Memory()
        raw_stack: Tuple[BaseSegment, ...] = context.raw_stack
        if raw_stack and raw_stack[-1] is not context.segment:
            raw_stack = raw_stack + (segment,)

        is_ignorable = any(
            el.is_type(*self._ignore_types) for el in context.parent_stack + (segment,)
        )
        if is_ignorable:
            return LintResult(memory=memory)

        if segment.is_type("newline"):
            memory.in_indent = True
        elif memory.in_indent:
            has_children = bool(segment.segments)
            if not (segment.is_whitespace or has_children or segment.is_type("indent")):
                memory.in_indent = False
                # First non-whitespace element is our trigger
                memory.trigger = segment

        if not segment.is_type("newline", "end_of_file"):
            # Process on line ends or file end
            return LintResult(memory=memory)

        line_summaries = self._process_raw_stack(
            raw_stack=raw_stack,
            memory=memory,
            tab_space_size=self.tab_space_size,
            templated_file=context.templated_file,
        )
        memory.line_summaries = line_summaries
        trigger_segment = memory.trigger
        memory.trigger = None
        if line_summaries and trigger_segment:
            last_line_no = max(line_summaries.keys())
            this_line = line_summaries[last_line_no]
            result = self._process_working_state(memory, trigger_segment)
            # Template lines don't need fixes
            # However we do need the mutations from the processing.
            if not this_line.templated_line:
                return result

        return LintResult(memory=memory)

    def _process_working_state(
        self,
        memory: _Memory,
        trigger_segment: BaseSegment,
    ) -> LintResult:
        """Checks indentation of one line of code, returning a LintResult.

        The _eval() function calls it for the current line of code:
        - When passed a newline segment (thus ending a line)
        - When passed the *final* segment in the entire parse tree (which may
          not be a newline)
        """
        line_summaries = memory.line_summaries
        this_line_no = max(line_summaries.keys())
        this_line: _LineSummary = line_summaries.pop(this_line_no)
        self.logger.debug(
            "Evaluating line #%s. %s",
            this_line_no,
            this_line,
        )

        if this_line.is_comment_line:
            # Comment line, deal with it later.
            memory.comment_lines.add(this_line_no)
            self.logger.debug("    Comment Line. #%s", this_line_no)
            return LintResult(memory=memory)

        if this_line.line_buffer and this_line.line_buffer[0].is_type(
            "end_of_file"
        ):  # pragma: no cover
            # This is just the end of the file.
            self.logger.debug("    Just end of file. #%s", this_line_no)
            return LintResult(memory=memory)

        previous_line_numbers = sorted(line_summaries.keys(), reverse=True)
        # we will iterate this more than once
        previous_lines = list(map(lambda k: line_summaries[k], previous_line_numbers))

        # handle hanging indents if allowed
        hanger_res = self.hanging_indents and self._handle_hanging_indents(
            this_line, previous_lines, memory
        )
        if hanger_res:
            return hanger_res

        # Is this an indented first line?
        if this_line.line_no == 1 and this_line.indent_size > 0:
            self.logger.debug("    Indented First Line. #%s", this_line_no)
            return LintResult(
                anchor=trigger_segment,
                memory=memory,
                description="First line has unexpected indent",
                fixes=[LintFix.delete(elem) for elem in this_line.indent_buffer],
            )

        # Special handling for template end/mid blocks on a line by themselves.
        # NOTE: Mid blocks (i.e. TemplateLoop segmets) behave like ends here, but
        # don't otherwise have the same indent balance implications.
        if this_line.templated_line_type in ("end", "mid"):
            return self._handle_template_blocks(
                this_line=this_line,
                trigger_segment=trigger_segment,
                previous_lines=previous_lines,
                memory=memory,
            )
        # Assuming it's not a hanger, let's compare it to the other previous
        # lines. We do it in reverse so that closer lines are more relevant.

        prev_line = _find_previous_line(
            this_line,
            previous_lines,
            memory.noncomparable_lines,
        )

        if not prev_line:
            return LintResult(memory=memory)
        prev_line_no = prev_line.line_no
        indent_diff = this_line.anchor_indent_balance - prev_line.anchor_indent_balance
        this_indent_num, this_indent_rem = divmod(
            this_line.indent_size, self.tab_space_size
        )
        has_partial_indent = bool(this_indent_rem)
        comp_indent_num = prev_line.indent_size // self.tab_space_size
        # Is the indent balance the same?
        if indent_diff == 0:
            self.logger.debug(
                "    [same indent balance] Comparing to #%s",
                prev_line_no,
            )
            if this_line.indent_size != prev_line.indent_size:
                # Indents don't match even though balance is the same...
                memory.problem_lines.add(this_line_no)

                # Work out desired indent
                desired_indent = self._make_indent(
                    indent_unit=self.indent_unit,
                    tab_space_size=self.tab_space_size,
                    num=comp_indent_num,
                )

                fixes = self._coerce_indent_to(
                    desired_indent=desired_indent,
                    current_indent_buffer=this_line.indent_buffer,
                    current_anchor=trigger_segment,
                )
                self.logger.debug(
                    "    !! Indentation does not match #%s. Fixes: %s",
                    prev_line_no,
                    fixes,
                )
                return LintResult(
                    anchor=trigger_segment,
                    memory=memory,
                    description=_Desc(
                        expected=comp_indent_num,
                        found=this_indent_num,
                        has_partial_indent=has_partial_indent,
                        compared_to=prev_line.line_no,
                    ),
                    fixes=fixes,
                )
        # Are we at a deeper indent?
        elif indent_diff > 0:
            self.logger.debug(
                "    [deeper indent balance] Comparing to #%s",
                prev_line_no,
            )
            # NB: We shouldn't need to deal with correct hanging indents
            # here, they should already have been dealt with before. We
            # may still need to deal with *creating* hanging indents if
            # appropriate.
            self.logger.debug("    Comparison Line: %s", prev_line)

            # Check to see if we've got a whole number of multiples. If
            # we do then record the number for later, otherwise raise
            # an error. We do the comparison here so we have a reference
            # point to do the repairs. We need a sensible previous line
            # to base the repairs off. If there's no indent at all, then
            # we should also take this route because there SHOULD be one.
            if this_line.indent_size % self.tab_space_size != 0:
                memory.problem_lines.add(this_line_no)

                # The default indent is the one just reconstructs it from
                # the indent size.
                desired_indent = self._make_indent(
                    indent_unit=self.indent_unit,
                    tab_space_size=self.tab_space_size,
                    num=indent_diff + this_indent_num,
                )
                # If we have the option of a hanging indent then use it.
                if self.hanging_indents and prev_line.hanging_indent:
                    self.logger.debug("        Use hanging indent.")
                    desired_indent = " " * prev_line.hanging_indent

                fixes = self._coerce_indent_to(
                    desired_indent=desired_indent,
                    current_indent_buffer=this_line.indent_buffer,
                    current_anchor=trigger_segment,
                )
                return LintResult(
                    anchor=trigger_segment,
                    memory=memory,
                    description=_Desc(
                        expected=len(desired_indent) // self.tab_space_size,
                        found=this_indent_num,
                        has_partial_indent=has_partial_indent,
                        compared_to=prev_line.line_no,
                    ),
                    fixes=fixes,
                )

            # The indent number should be at least 1, and can be UP TO
            # and including the difference in the indent balance.
            if comp_indent_num == this_indent_num:
                # We have two lines indented the same, but with a different starting
                # indent balance. This is either a problem OR a sign that one of the
                # opening indents wasn't used. We account for the latter and then
                # have a violation if that wasn't the case.

                # Does the comparison line have enough unused indent to get us back
                # to where we need to be? NB: This should only be applied if this is
                # a CLOSING bracket.

                # First work out if we have some closing brackets, and if so, how
                # many.
                b_num = 0
                for elem in this_line.line_buffer:
                    if not elem.is_code:
                        continue
                    if elem.is_type("end_bracket", "end_square_bracket"):
                        b_num += 1
                        continue
                    break  # pragma: no cover

                if b_num < indent_diff:
                    # It doesn't. That means we *should* have an indent when
                    # compared to this line and we DON'T.
                    memory.problem_lines.add(this_line_no)
                    return LintResult(
                        anchor=trigger_segment,
                        memory=memory,
                        description=_Desc(
                            expected=this_indent_num + 1,
                            found=this_indent_num,
                            has_partial_indent=has_partial_indent,
                            compared_to=prev_line.line_no,
                        ),
                        # Coerce the indent to what we think it should be.
                        fixes=self._coerce_indent_to(
                            desired_indent=self._make_indent(
                                num=this_indent_num + 1,
                                tab_space_size=self.tab_space_size,
                                indent_unit=self.indent_unit,
                            ),
                            current_indent_buffer=this_line.indent_buffer,
                            current_anchor=trigger_segment,
                        ),
                    )
            elif (
                this_indent_num < comp_indent_num
                or this_indent_num > comp_indent_num + indent_diff
            ):
                memory.problem_lines.add(this_line_no)
                desired_indent = self._make_indent(
                    num=comp_indent_num,
                    indent_unit=self.indent_unit,
                    tab_space_size=self.tab_space_size,
                )
                fixes = self._coerce_indent_to(
                    desired_indent=desired_indent,
                    current_indent_buffer=this_line.indent_buffer,
                    current_anchor=trigger_segment,
                )
                return LintResult(
                    anchor=trigger_segment,
                    memory=memory,
                    description=_Desc(
                        expected=comp_indent_num,
                        found=this_indent_num,
                        has_partial_indent=has_partial_indent,
                        compared_to=prev_line.line_no,
                    ),
                    fixes=fixes,
                )

        # This was a valid comparison, so if it doesn't flag then
        # we can assume that we're ok.
        self.logger.debug("    Indent deemed ok comparing to #%s", prev_line_no)
        comment_fix = self._calculate_comment_fixes(
            memory, previous_line_numbers, this_line
        )
        return comment_fix or LintResult(memory=memory)

    def _calculate_comment_fixes(
        self, memory: _Memory, previous_line_numbers: List[int], this_line: _LineSummary
    ) -> Optional[LintResult]:
        # Given that this line is ok, consider if the preceding lines are
        # comments. If they are, lint the indentation of the comment(s).
        fixes: List[LintFix] = []
        anchor: Optional[BaseSegment] = None
        for n in previous_line_numbers:
            if n not in memory.comment_lines:
                break
            # The previous line WAS a comment.
            prev_line = memory.line_summaries[n]
            if this_line.indent_size != prev_line.indent_size:
                # It's not aligned.
                # Find the anchor first.
                for seg in prev_line.line_buffer:
                    if seg.is_type("comment"):
                        anchor = seg
                        break

                if not anchor:  # pragma: no cover
                    continue

                fixes += self._coerce_indent_to(
                    desired_indent="".join(
                        elem.raw for elem in this_line.indent_buffer
                    ),
                    current_indent_buffer=prev_line.indent_buffer,
                    current_anchor=anchor,
                )

                memory.problem_lines.add(n)

        if not fixes:
            return None

        return LintResult(
            anchor=anchor,
            memory=memory,
            description="Comment not aligned with following line.",
            fixes=fixes,
        )

    def _handle_hanging_indents(
        self,
        this_line: _LineSummary,
        previous_lines: List[_LineSummary],
        memory: _Memory,
    ) -> Optional[LintResult]:
        if len(previous_lines) == 0:
            return None

        last_line = _find_last_meaningful_line(previous_lines)
        if not last_line:
            return None
        # Handle Hanging Indents
        is_anchor_indent_match = (
            this_line.anchor_indent_balance == last_line.anchor_indent_balance
        )
        is_end_indent_match = this_line.indent_size == last_line.indent_size
        is_known_hanging_line = last_line.line_no in memory.hanging_lines
        # There MUST also be a non-zero indent. Otherwise we're just on the
        # baseline.
        if this_line.indent_size <= 0:
            return None

        # NB: Hangers are only allowed if there was content after the last
        # indent on the previous line. Otherwise it's just an indent.
        is_hanging_match = this_line.indent_size == last_line.hanging_indent
        # Or they're if the indent balance is the same and the indent is the
        # same AND the previous line was a hanger
        is_matching_previous = (
            is_anchor_indent_match and is_end_indent_match and is_known_hanging_line
        )
        if not is_matching_previous and not is_hanging_match:
            return None
        memory.hanging_lines.add(this_line.line_no)
        self.logger.debug("    Hanger Line. #%s", this_line.line_no)
        self.logger.debug("    Last Line: %s", last_line)
        return LintResult(memory=memory)

    def _handle_template_blocks(
        self,
        this_line: _LineSummary,
        trigger_segment: BaseSegment,
        previous_lines: List[_LineSummary],
        memory: _Memory,
    ):
        # For a template block end on a line by itself, search for a
        # matching block start on a line by itself. If there is one, match
        # its indentation. Question: Could we avoid treating this as a
        # special case? It has some similarities to the non-templated test
        # case test/fixtures/linter/indentation_error_contained.sql, in that
        # both have lines where anchor_indent_balance drops 2 levels from one line
        # to the next, making it a bit unclear how to indent that line.
        template_line = _find_matching_start_line(previous_lines)
        # In rare circumstances there may be disbalanced pairs
        if not template_line:
            return LintResult(memory=memory)

        if template_line.line_no in memory.noncomparable_lines:
            return LintResult(memory=memory)

        self.logger.debug(
            "    [template block end] Comparing to #%s", template_line.line_no
        )
        if this_line.indent_size == template_line.indent_size:
            return LintResult(memory=memory)

        memory.problem_lines.add(this_line.line_no)

        # The previous indent.
        desired_indent = "".join(elem.raw for elem in template_line.indent_buffer)
        first_non_indent_i = len(this_line.indent_buffer)
        current_anchor = this_line.line_buffer[first_non_indent_i]
        fixes = self._coerce_indent_to(
            desired_indent=desired_indent,
            current_indent_buffer=this_line.indent_buffer,
            current_anchor=current_anchor,
        )
        self.logger.debug(
            "    !! Indentation does not match #%s. Fixes: %s",
            template_line.line_no,
            fixes,
        )
        return LintResult(
            anchor=trigger_segment,
            memory=memory,
            description=_Desc(
                len(desired_indent) // self.tab_space_size,
                this_line.indent_size,
                template_line.line_no,
            ),
            fixes=fixes,
        )


class _TemplateLineInterpreter:
    start_blocks = (
        ("placeholder", "block_start"),
        ("placeholder", "compound"),
        ("placeholder", "literal"),
        ("placeholder", "block_mid"),
    )
    indent_types = (
        ("indent", None),
        ("newline", None),
    )
    valid_start_combos = list(
        itertools.product(
            start_blocks,
            indent_types,
        )
    )
    dedent_types = (("dedent", None),)
    end_block = (
        ("placeholder", "block_end"),
        ("placeholder", "compound"),
        ("placeholder", "block_mid"),
    )
    valid_end_combos = list(
        itertools.product(
            dedent_types,
            end_block,
        )
    )

    def __init__(
        self,
        working_state: List[BaseSegment],
        templated_file: Optional[TemplatedFile],
    ) -> None:
        self.working_state = [el for el in working_state if not el.is_whitespace]
        self.templated_file = templated_file
        self._adjacent_pairs: Optional[
            List[Tuple[Tuple[str, Optional[str]], Tuple[str, Optional[str]]]]
        ] = None

    def is_single_placeholder_line(self):
        count_placeholder = 0
        for seg in self.working_state:
            if seg.is_code:
                return False
            elif seg.is_type("placeholder"):
                count_placeholder += 1

        return count_placeholder == 1

    def is_template_loop_line(self):
        for seg in self.working_state:
            if seg.is_code:
                return False
            if seg.is_type("template_loop"):
                return True
        return False

    def list_segment_and_raw_segment_types(self) -> Iterable[Tuple[str, Optional[str]]]:
        """Yields the tuple of seg type and underlying type were applicable."""
        for seg in self.working_state:
            raw_seg = self.get_raw_slices(seg)
            raw_str = raw_seg[0].slice_type if raw_seg else None
            yield (seg.type, raw_str)

    def get_adjacent_type_pairs(self):
        """Produce a list of pairs of each sequenctial combo of two."""
        if self._adjacent_pairs:
            return self._adjacent_pairs
        iterable = self.list_segment_and_raw_segment_types()
        a, b = itertools.tee(iterable)
        # consume the first item in b
        next(b, None)
        self._adjacent_pairs = list(zip(a, b))
        return self._adjacent_pairs

    def is_block_start(self):
        return any(
            pair in self.valid_start_combos for pair in self.get_adjacent_type_pairs()
        )

    def is_block_end(self):
        return any(
            pair in self.valid_end_combos for pair in self.get_adjacent_type_pairs()
        )

    def block_type(self) -> Optional[str]:
        """Return a block_type enum."""
        if not self.templated_file:
            return None

        if self.is_template_loop_line():
            return "mid"

        if not self.is_single_placeholder_line():
            return None

        if self.is_block_end():
            return "end"

        if self.is_block_start():
            return "start"

        return None

    def get_raw_slices(self, elem: BaseSegment) -> Optional[List[RawFileSlice]]:
        if not self.templated_file:  # pragma: no cover
            return None

        if not elem.is_type("placeholder"):
            return None

        assert elem.pos_marker, "TypeGuard"
        slices = self.templated_file.raw_slices_spanning_source_slice(
            elem.pos_marker.source_slice
        )
        return slices or None


def _get_template_block_type(
    line_buffer: List[BaseSegment],
    templated_file: Optional[TemplatedFile] = None,
):
    """Convenience fn for getting 'start', 'end' etc of a placeholder line."""
    template_info = _TemplateLineInterpreter(line_buffer, templated_file)
    return template_info.block_type()


def _segment_length(elem: BaseSegment, tab_space_size: int):
    # Start by assuming the typical case, where we need not consider slices
    # or templating.
    raw = elem.raw

    # If it's whitespace, it might be a mixture of literal and templated
    # whitespace. Check for this.
    if elem.is_type("whitespace") and elem.is_templated:
        # Templated case: Find the leading *literal* whitespace.
        assert elem.pos_marker
        templated_file = elem.pos_marker.templated_file
        # Extract the leading literal whitespace, slice by slice.
        raw = ""
        for raw_slice in Segments(
            elem, templated_file=templated_file
        ).raw_slices.select(loop_while=rsp.is_slice_type("literal")):
            # Compute and append raw_slice's contribution.
            raw += sp.raw_slice(elem, raw_slice)

    # convert to spaces for convenience (and hanging indents)
    return raw.replace("\t", " " * tab_space_size)


def _indent_size(segments: Sequence[BaseSegment], tab_space_size: int = 4) -> int:
    indent_size = 0
    for elem in segments:
        raw = _segment_length(elem, tab_space_size)
        indent_size += len(raw)
    return indent_size


def _find_last_meaningful_line(
    previous_lines: List[_LineSummary],
) -> Optional[_LineSummary]:
    # Find last meaningful line indent.
    for line in previous_lines:
        if line.has_code_segment:
            return line

    return None


def _find_previous_line(
    this_line: _LineSummary,
    previous_lines: List[_LineSummary],
    ignoreable_lines: Set[int],
) -> Optional[_LineSummary]:
    for prev_line in previous_lines:
        should_ignore = prev_line.line_no in ignoreable_lines
        if should_ignore or prev_line.is_empty_line:
            continue

        # Work out the difference in indent
        indent_diff = this_line.anchor_indent_balance - prev_line.anchor_indent_balance
        # If we're comparing to a previous, more deeply indented line,
        # then skip and keep looking.
        if indent_diff < 0:
            continue
        return prev_line
    return None


def _find_matching_start_line(
    previous_lines: List[_LineSummary],
) -> Optional[_LineSummary]:
    template_block_level = -1
    for template_line in previous_lines:
        if not template_line.templated_line_type:
            continue
        if template_line.templated_line_type == "end":
            template_block_level -= 1
        else:
            template_block_level += 1

        if template_block_level != 0:
            continue

        return template_line
    return None  # pragma: no cover


def _Desc(
    expected: int, found: int, compared_to: int, has_partial_indent: bool = False
) -> str:
    indentations = "indentation" if expected == 1 else "indentations"
    if found >= expected and has_partial_indent:
        found_explanation = f"more than {found}"
    elif found < expected and has_partial_indent:
        found_explanation = f"less than {found + 1}"
    else:
        found_explanation = str(found)
    return (
        f"Expected {expected} {indentations},"
        f" found {found_explanation} [compared to line {compared_to:02}]"
    )
