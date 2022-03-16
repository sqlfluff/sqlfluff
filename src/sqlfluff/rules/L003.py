"""Implementation of Rule L003."""
import dataclasses
import itertools
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from sqlfluff.core.parser import WhitespaceSegment
from sqlfluff.core.parser.segments import BaseSegment
from sqlfluff.core.rules.functional import rsp, sp, Segments
from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)
from sqlfluff.core.templaters import TemplatedFile
from sqlfluff.core.templaters.base import RawFileSlice


class _DictLikeDataCls:
    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, key, item):
        return setattr(self, key, item)

    def items(self):
        for field_el in dataclasses.fields(self):
            key = field_el.name
            yield key, getattr(self, key)


@dataclasses.dataclass
class _LineSummary(_DictLikeDataCls):
    """A dataobject to represent a line.

    Doubles as a memory object (holding state)
    that can be converted to a fresh summary instance
    """

    line_no: int = 0
    templated_line: Optional[int] = None
    line_buffer: List[BaseSegment] = dataclasses.field(default_factory=list)
    indent_buffer: List[BaseSegment] = dataclasses.field(default_factory=list)
    indent_size: int = 1
    indent_balance: int = 0
    hanging_indent: Optional[int] = None
    clean_indent: bool = True
    template_content: str = ""
    templated_line_type: Optional[str] = None

    # These are only required for carrying state between lines
    indent_balance_marker: int = 0
    in_indent: bool = True
    line_indent_stack: List[int] = dataclasses.field(default_factory=list)
    hanger_pos: Optional[int] = None

    def strip_buffers(self) -> dict:
        """Strip a line dict of buffers for logging."""
        keys_to_strip = (
            "line_buffer",
            "indent_buffer",
        )
        print_dict: Dict = {
            key: value for key, value in self.items() if key not in keys_to_strip
        }
        print_dict["raw"] = "".join(el.raw for el in self.line_buffer)
        return print_dict

    def trigger_el(self):
        """Get the pivot element."""
        for el in self.line_buffer:
            if el.is_type("newline", "whitespace"):
                continue
            if el.segments:
                continue
            if el.is_meta and el.indent_val != 0:
                continue
            return el

        return None

    def memo_line_reset(self):
        """When acting like a MemoryLine this resets state."""
        self.templated_line = False
        self.indent_buffer = []
        line_buffer = self.line_buffer
        self.line_buffer = []
        self.line_indent_stack = []
        self.indent_size = 0
        self.in_indent = True
        self.hanger_pos = None
        self.clean_indent = False
        # Assume an unclean indent, but if the last line
        # ended with an indent then we might be ok.
        # Was there an indent after the last code element of the previous line?
        for search_elem in reversed(line_buffer):
            is_meta = search_elem.is_meta
            if not search_elem.is_code and not is_meta:
                continue
            elif is_meta and search_elem.indent_val > 0:
                self.clean_indent = True
            break

        return self

    def from_memo_line(self, line_no: int, templated_file: Optional[TemplatedFile]):
        """Create a final summary from a memo line."""
        memo_line = self
        copied_line_buffer = memo_line.line_buffer[:]
        template_info = _TemplateLineInterpreter(copied_line_buffer, templated_file)
        # Generate our line summaary based on the current state of the MemoLine
        output = self.__class__(
            **{  # type: ignore
                "line_no": line_no,
                "templated_line": self.templated_line,
                # Using slicing to copy line_buffer here to be py2 compliant
                "line_buffer": copied_line_buffer,
                "indent_buffer": self.indent_buffer,
                "indent_size": self.indent_size,
                # Indent balance is the indent at the start of the first content
                "indent_balance": self.indent_balance_marker,
                "indent_balance_marker": self.indent_balance,
                "hanging_indent": self.hanger_pos
                if memo_line.line_indent_stack
                else None,
                # Clean indent is true if the line *ends* with an indent
                # or has an indent in the initial whitespace.
                "clean_indent": self.clean_indent,
                "template_content": template_info.template_content,
                "templated_line_type": template_info.block_type(),
            }
        )
        self.memo_line_reset()
        return output


@dataclasses.dataclass
class _MemoryDict(_DictLikeDataCls):
    # problem_lines keeps track of lines with problems so that we
    # don't compare to them.
    problem_lines: List[int] = dataclasses.field(default_factory=list)
    # hanging_lines keeps track of hanging lines so that we don't
    # compare to them when assessing indent.
    hanging_lines: List[int] = dataclasses.field(default_factory=list)
    # comment_lines keeps track of lines which are all comment.
    comment_lines: List[int] = dataclasses.field(default_factory=list)
    # Dict of processed lines
    line_summaries: Dict[int, _LineSummary] = dataclasses.field(default_factory=dict)
    # Raw elements seen
    raw_stack: List[Tuple[BaseSegment, bool]] = dataclasses.field(default_factory=list)


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

    targets_templated = True
    _works_on_unparsable = False
    _adjust_anchors = True
    _ignore_types: List[str] = ["script_content"]
    config_keywords = ["tab_space_size", "indent_unit"]
    tab_space_size: int
    indent_unit: str

    @staticmethod
    def _make_indent(
        num: int = 1, tab_space_size: int = 4, indent_unit: str = "space"
    ) -> str:
        if num == 0:
            return ""

        if indent_unit == "tab":
            base_unit = "\t"
        elif indent_unit == "space":
            base_unit = " " * tab_space_size
        else:
            raise ValueError(
                f"Parameter indent_unit has unexpected value: `{indent_unit}`. Expected"
                " `tab` or `space`."
            )

        return base_unit * num

    @staticmethod
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

    @staticmethod
    def _indent_size(segments: Sequence[BaseSegment], tab_space_size: int = 4) -> int:
        indent_size = 0
        for elem in segments:
            raw = Rule_L003._segment_length(elem, tab_space_size)
            indent_size += len(raw)
        return indent_size

    @classmethod
    def _process_raw_stack(
        cls,
        raw_stack: List[Tuple[BaseSegment, bool]],
        memory: _MemoryDict,
        tab_space_size: int = 4,
        templated_file: Optional[TemplatedFile] = None,
    ) -> Dict[int, _LineSummary]:
        """Take the raw stack, split into lines and evaluate some stats."""
        line_no = 1
        result_buffer: Dict[int, _LineSummary] = memory["line_summaries"]
        # Create a memo line which will hold state during this loop
        # Use the last processed line if possible
        memo_line = dataclasses.replace(
            next(reversed(result_buffer.values())) if result_buffer else _LineSummary()
        )
        memo_line.memo_line_reset()
        # True lines invert the balance and the balance marker.
        # When reading from a cache take the opposite values for our start positions
        tranfer_indent_balance_marker = memo_line.indent_balance_marker
        memo_line.indent_balance_marker = memo_line.indent_balance
        memo_line.indent_balance = tranfer_indent_balance_marker

        trigger_el = _find_final_trigger(raw_stack)
        # Set up helpers to act as cache when asked to reparse lines
        memo_size = len(result_buffer)
        started = line_no == (memo_size + 1)
        for elem, _ in raw_stack:
            if not started:
                # Skip everything we have processed already
                if elem.is_type("newline"):
                    line_no += 1
                started = line_no == (memo_size + 1)
                continue

            memo_line.line_buffer.append(elem)
            # Pin indent_balance to above zero
            if memo_line.indent_balance < 0:
                memo_line.indent_balance = 0

            if elem.is_type("newline"):
                # convert our memo line into a true summary
                # then rest the memo aspects that need reseting
                result_buffer[line_no] = memo_line.from_memo_line(
                    line_no, templated_file
                )
                line_no += 1
                # Set the "templated_line" flag for the *next* line if the
                # newline that ended the *current* line was in templated space.
                # Reason: We want to ignore indentation of lines that are not
                # present in the raw (pre-templated) code.
                memo_line.templated_line = elem.is_templated

            elif memo_line.in_indent:
                if elem.is_type("whitespace"):
                    memo_line.indent_buffer.append(elem)
                elif elem.is_meta and elem.indent_val != 0:  # type: ignore
                    memo_line.indent_balance += elem.indent_val  # type: ignore
                    if elem.indent_val > 0:  # type: ignore
                        # a "clean" indent is one where it contains
                        # an increase in indentation? Can't quite
                        # remember the logic here. Let's go with that.
                        memo_line.clean_indent = True
                else:
                    memo_line.in_indent = False
                    memo_line.indent_balance_marker = memo_line.indent_balance
                    memo_line.indent_size = cls._indent_size(
                        memo_line.indent_buffer,
                        tab_space_size=tab_space_size,
                    )
            elif elem.is_meta and elem.indent_val != 0:  # type: ignore
                memo_line.indent_balance += elem.indent_val  # type: ignore
                if elem.indent_val > 0:  # type: ignore
                    # Keep track of the indent at the last ... indent
                    memo_line.line_indent_stack.append(
                        cls._indent_size(
                            memo_line.line_buffer,
                            tab_space_size=tab_space_size,
                        )
                    )
                    memo_line.hanger_pos = None
                else:
                    # this is a dedent, we could still have a hanging indent,
                    # but only if there's enough on the stack
                    if memo_line.line_indent_stack:
                        memo_line.line_indent_stack.pop()
            elif elem.is_code:
                if memo_line.hanger_pos is None:
                    memo_line.hanger_pos = cls._indent_size(
                        memo_line.line_buffer[:-1],
                        tab_space_size=tab_space_size,
                    )

            # If we hit the trigger element, stop processing.
            if elem is trigger_el:
                break

        # If we get to the end, and still have a buffer, add it on
        if memo_line.line_buffer:
            result_buffer[line_no] = memo_line.from_memo_line(
                line_no,
                templated_file,
            )

        return result_buffer

    def _coerce_indent_to(
        self,
        desired_indent: str,
        current_indent_buffer: List[BaseSegment],
        current_anchor: BaseSegment,
    ) -> List[LintFix]:
        """Generate fixes to make an indent a certain size."""
        # In all cases we empty the existing buffer
        # except for our indent markers
        fixes = [
            LintFix.delete(elem)
            for elem in current_indent_buffer
            if not elem.is_type("indent")
        ]
        if len(desired_indent) == 0:
            # If there shouldn't be an indent at all, just delete.
            return fixes

        # Anything other than 0 create a fresh buffer
        return [
            LintFix.create_before(
                current_anchor,
                [
                    WhitespaceSegment(
                        raw=desired_indent,
                    ),
                ],
            ),
            *fixes,
        ]

    def _eval_new(self, context: RuleContext) -> Optional[List[LintResult]]:
        is_last = self.is_final_segment(context)
        memory: _MemoryDict = context.memory or _MemoryDict()
        is_ignorable = any(
            element.is_type(*self._ignore_types)
            for element in context.parent_stack + (context.segment,)
        )
        if not context.segment.segments:
            memory.raw_stack.append(
                (
                    context.segment,
                    is_ignorable,
                )
            )

        if not is_last:
            return [LintResult(memory=memory)]

        # Calculate all Line Summaries
        line_summaries = self._process_raw_stack(
            memory.raw_stack,
            memory,
            tab_space_size=self.tab_space_size,
            templated_file=context.templated_file,
        )

        results: List[LintResult] = []
        for line_number, summary in line_summaries.items():
            if summary["templated_line"]:
                continue
            # Return fixes
            fix = self._process_current_line(
                line_summaries,
                memory,
                line_number,
            )
            if not fix.fixes:
                continue
            results.append(fix)

        # Poor Man's correction of duplicate changes
        seen = set()
        for res in results:
            if not res.fixes:
                continue
            fixes: List[LintFix] = []
            for fix_el in res.fixes:
                this_set = (fix_el.anchor, fix_el.edit_type)
                if this_set in seen:
                    continue
                fixes.append(fix_el)
                seen.add(this_set)
            res.fixes = fixes

        return results

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
        memory: _MemoryDict = context.memory or _MemoryDict()
        # We ignore certain types (e.g. non-SQL scripts in functions)
        # so check if on ignore list
        ignorable = any(
            element.is_type(*self._ignore_types)
            for element in context.parent_stack + (context.segment,)
        )

        if not context.segment.segments:
            memory.raw_stack.append(
                (
                    context.segment,
                    ignorable,
                )
            )

        if ignorable:
            return LintResult(memory=memory)

        # Is this the last segment? If so, need to "flush" any leftovers.
        is_last = self.is_final_segment(context)

        if not context.segment.is_type("newline") and not is_last:
            # We only process complete lines or on the very last segment
            # (since there may not be a newline on the very last line)..
            return LintResult(memory=memory)

        line_summaries = self._process_raw_stack(
            memory.raw_stack,
            memory,
            tab_space_size=self.tab_space_size,
            templated_file=context.templated_file,
        )
        memory["line_summaries"] = line_summaries
        this_line_no = max(line_summaries.keys())
        this_line = line_summaries[this_line_no]
        if this_line.templated_line:
            # If it's a templated line, ignore the result (i.e. any lint
            # errors it found) because these lines don't exist in the raw
            # (pre-templated) code.
            return LintResult(memory=memory)
        lint_result = self._process_current_line(line_summaries, memory, this_line_no)
        # ensure we recalc the final line once we reach teh next line
        line_summaries.pop(this_line_no)
        return lint_result

    def _process_current_line(
        self,
        res: Dict[int, _LineSummary],
        memory: _MemoryDict,
        this_line_no: int,
    ) -> LintResult:
        """Checks indentation of one line of code, returning a LintResult.

        The _eval() function calls it for the current line of code:
        - When passed a newline segment (thus ending a line)
        - When passed the *final* segment in the entire parse tree (which may
          not be a newline)
        """
        res = res.copy()
        this_line = res.pop(this_line_no)
        this_line_segments = Segments(*this_line["line_buffer"])
        trigger_segment = this_line.trigger_el()
        # certain lines should not be processed or
        # contribute to the memory. eg scripts
        if not trigger_segment:
            return LintResult(memory=memory)

        lines_before = sorted(
            line_no for line_no in res.keys() if line_no <= this_line_no
        )
        self.logger.debug(
            "Evaluating line #%s. %s",
            this_line_no,
            # Don't log the line or indent buffer, it's too noisy.
            this_line.strip_buffers(),
        )
        # Is this line just comments? (Disregard trailing newline if present.)
        if this_line_segments.all(
            sp.is_type(
                "whitespace",
                "comment",
                "indent",
                "newline",
            )
        ):
            # Comment line, deal with it later.
            memory["comment_lines"].append(this_line_no)
            self.logger.debug("    Comment Line. #%s", this_line_no)
            return LintResult(memory=memory)

        # Is it a hanging indent?
        # Find last meaningful line indent.
        last_code_line: Optional[int] = None
        for k in reversed(lines_before):
            if any(seg.is_code for seg in res[k]["line_buffer"]):
                last_code_line = k
                break

        last_line = res[last_code_line] if last_code_line else None
        if len(res) > 0 and last_line:
            last_line_hanger_indent = last_line["hanging_indent"]
            # Let's just deal with hanging indents here.
            if (
                # NB: Hangers are only allowed if there was content after the last
                # indent on the previous line. Otherwise it's just an indent.
                this_line["indent_size"] == last_line_hanger_indent
                # Or they're if the indent balance is the same and the indent is the
                # same AND the previous line was a hanger
                or (
                    this_line["indent_size"] == last_line["indent_size"]
                    and this_line["indent_balance"] == last_line["indent_balance"]
                    and last_code_line in memory["hanging_lines"]
                )
            ) and (
                # There MUST also be a non-zero indent. Otherwise we're just on the
                # baseline.
                this_line["indent_size"]
                > 0
            ):
                # This is a HANGER
                memory["hanging_lines"].append(this_line_no)
                self.logger.debug("    Hanger Line. #%s", this_line_no)
                self.logger.debug("    Last Line: %s", last_line.strip_buffers())
                return LintResult(memory=memory)

        # Is this an indented first line?
        if this_line_no == 1 and this_line["indent_size"] > 0:
            self.logger.debug("    Indented First Line. #%s", this_line_no)
            return LintResult(
                anchor=trigger_segment,
                memory=memory,
                description="First line has unexpected indent",
                fixes=[
                    LintFix.delete(elem)
                    for elem in this_line["indent_buffer"]
                    if not elem.is_type("indent")
                ],
            )

        # Special handling for template end blocks on a line by themselves.
        # the start of a start block (up to the trigger)
        # cannot be id'd as a template_line
        if this_line.templated_line_type == "end":
            # For a template block end on a line by itself, search for a
            # matching block start on a line by itself. If there is one, match
            # its indentation. Question: Could we avoid treating this as a
            # special case? It has some similarities to the non-templated test
            # case test/fixtures/linter/indentation_error_contained.sql, in tha
            # both have lines where indent_balance drops 2 levels from one line
            # to the next, making it a bit unclear how to indent that line.
            template_block_level = -1
            for k in sorted(lines_before, reverse=True):
                prev_block_line = res[k]
                if prev_block_line.templated_line_type is None:
                    # This is not a template only line -> skip
                    continue
                if prev_block_line.templated_line_type == "end":
                    template_block_level -= 1
                else:
                    template_block_level += 1

                if template_block_level != 0:
                    continue

                # Found prior template block line with the same indent balance.
                # Is this a problem line?
                if k in memory["problem_lines"] + memory["hanging_lines"]:
                    # Skip it if it is
                    return LintResult(memory=memory)

                self.logger.debug("    [template block end] Comparing to #%s", k)
                if this_line["indent_size"] == prev_block_line["indent_size"]:
                    return LintResult(memory=memory)

                # Indents don't match even though balance is the same...
                memory["problem_lines"].append(this_line_no)

                # The previous indent.
                desired_indent = "".join(
                    elem.raw for elem in prev_block_line["indent_buffer"]
                )

                first_non_indent_i = len(this_line["indent_buffer"])
                current_anchor = this_line.line_buffer[first_non_indent_i]
                fixes = self._coerce_indent_to(
                    desired_indent=desired_indent,
                    current_indent_buffer=this_line["indent_buffer"],
                    current_anchor=current_anchor,
                )
                self.logger.debug(
                    "    !! Indentation does not match #%s. Fixes: %s", k, fixes
                )
                return LintResult(
                    anchor=trigger_segment,
                    memory=memory,
                    description="Indentation not consistent with line #{}".format(k),
                    fixes=fixes,
                )

        # Assuming it's not a hanger, let's compare it to the other previous
        # lines. We do it in reverse so that closer lines are more relevant.
        prev_line = _find_comparison_line(
            map(lambda num: res[num], reversed(lines_before)),
            this_line,
            ignoreable_lines=memory["problem_lines"] + memory["hanging_lines"],
        )
        if not prev_line:
            return LintResult(memory=memory)

        k = prev_line.line_no
        indent_diff = this_line["indent_balance"] - prev_line["indent_balance"]
        # Is the indent balance the same?
        if indent_diff == 0:
            self.logger.debug("    [same indent balance] Comparing to #%s", k)
            if this_line["indent_size"] != prev_line["indent_size"]:
                # Indents don't match even though balance is the same...
                memory["problem_lines"].append(this_line_no)

                # Work out desired indent
                if prev_line["indent_size"] == 0:
                    desired_indent = ""
                elif this_line["indent_size"] == 0:
                    desired_indent = self._make_indent(
                        indent_unit=self.indent_unit,
                        tab_space_size=self.tab_space_size,
                    )
                else:
                    # The previous indent.
                    desired_indent = "".join(
                        elem.raw for elem in prev_line["indent_buffer"]
                    )

                # Make fixes
                fixes = self._coerce_indent_to(
                    desired_indent=desired_indent,
                    current_indent_buffer=this_line["indent_buffer"],
                    current_anchor=trigger_segment,
                )
                self.logger.debug(
                    "    !! Indentation does not match #%s. Fixes: %s", k, fixes
                )
                return LintResult(
                    anchor=trigger_segment,
                    memory=memory,
                    description=f"Indentation not consistent with line #{k}",
                    fixes=fixes,
                )
        # Are we at a deeper indent?
        elif indent_diff > 0:
            self.logger.debug("    [deeper indent balance] Comparing to #%s", k)
            # NB: We shouldn't need to deal with correct hanging indents
            # here, they should already have been dealt with before. We
            # may still need to deal with *creating* hanging indents if
            # appropriate.
            self.logger.debug("    Comparison Line: %s", prev_line.strip_buffers())

            # Check to see if we've got a whole number of multiples. If
            # we do then record the number for later, otherwise raise
            # an error. We do the comparison here so we have a reference
            # point to do the repairs. We need a sensible previous line
            # to base the repairs off. If there's no indent at all, then
            # we should also take this route because there SHOULD be one.
            if this_line["indent_size"] % self.tab_space_size != 0:
                memory["problem_lines"].append(this_line_no)

                # The default indent is the one just reconstructs it from
                # the indent size.
                default_indent = "".join(
                    elem.raw for elem in prev_line["indent_buffer"]
                ) + self._make_indent(
                    indent_unit=self.indent_unit,
                    tab_space_size=self.tab_space_size,
                    num=indent_diff,
                )
                # If we have a clean indent, we can just add steps in line
                # with the difference in the indent buffers. simples.
                if this_line["clean_indent"]:
                    self.logger.debug("        Use clean indent.")
                    desired_indent = default_indent
                # If we have the option of a hanging indent then use it.
                elif prev_line["hanging_indent"]:
                    self.logger.debug("        Use hanging indent.")
                    desired_indent = " " * prev_line["hanging_indent"]
                else:  # pragma: no cover
                    self.logger.debug("        Use default indent.")
                    desired_indent = default_indent

                # Make fixes
                fixes = self._coerce_indent_to(
                    desired_indent=desired_indent,
                    current_indent_buffer=this_line["indent_buffer"],
                    current_anchor=trigger_segment,
                )

                return LintResult(
                    anchor=trigger_segment,
                    memory=memory,
                    description=(
                        "Indentation not hanging or a multiple of {} spaces"
                    ).format(self.tab_space_size),
                    fixes=fixes,
                )

            # We'll need this value later.
            this_indent_num = this_line["indent_size"] // self.tab_space_size

            # We know that the indent balance is higher, what actually is
            # the difference in indent counts? It should be a whole number
            # if we're still here.
            comp_indent_num = prev_line["indent_size"] // self.tab_space_size

            indents = this_line_segments.select(sp.is_type("indent"))
            positive_indents = indents.select(select_if=sp.not_(sp.is_type("dedent")))
            start_line_indents = this_line_segments.select(
                select_if=sp.and_(sp.is_type("indent"), sp.not_(sp.is_type("dedent"))),
                stop_seg=this_line_segments.first(sp.is_code()).get(0),
            )
            dedents = indents.select(select_if=sp.is_type("dedent"))
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
                # Due to strange inheritence all dedents are also indents

                self.logger.debug((positive_indents, dedents, start_line_indents))
                # Calc the balance of this line.
                # Double the contribution for any indents at the start of the line.
                b_num = len(dedents) - len(positive_indents)
                # - len(start_line_indents)
                if len(dedents):
                    b_num = b_num - len(indents.select(stop_seg=dedents.get(0)))

                self.logger.debug((b_num, this_line["line_buffer"]))

                if b_num < indent_diff:
                    # It doesn't. That means we *should* have an indent when
                    # compared to this line and we DON'T.
                    memory["problem_lines"].append(this_line_no)
                    return LintResult(
                        anchor=trigger_segment,
                        memory=memory,
                        description="Indent expected and not found compared to line"
                        " #{}".format(k),
                        # Add in an extra bit of whitespace for the indent
                        fixes=[
                            LintFix.create_before(
                                trigger_segment,
                                [
                                    WhitespaceSegment(
                                        raw=self._make_indent(
                                            indent_unit=self.indent_unit,
                                            tab_space_size=self.tab_space_size,
                                        ),
                                    ),
                                ],
                            ),
                        ],
                    )
            elif this_indent_num < comp_indent_num:
                memory["problem_lines"].append(this_line_no)
                return LintResult(
                    anchor=trigger_segment,
                    memory=memory,
                    description="Line under-indented compared to line #{}".format(k),
                    fixes=[
                        LintFix.create_before(
                            trigger_segment,
                            [
                                WhitespaceSegment(
                                    # Make the minimum indent for it to be ok.
                                    raw=self._make_indent(
                                        num=comp_indent_num - this_indent_num,
                                        indent_unit=self.indent_unit,
                                        tab_space_size=self.tab_space_size,
                                    ),
                                ),
                            ],
                        ),
                    ],
                )
            elif this_indent_num > comp_indent_num + indent_diff:
                self.logger.debug(
                    (
                        start_line_indents,
                        this_line_segments,
                        this_indent_num,
                        comp_indent_num,
                        indent_diff,
                    )
                )
                # Calculate the lowest ok indent:
                desired_indent = self._make_indent(
                    num=comp_indent_num - this_indent_num,
                    indent_unit=self.indent_unit,
                    tab_space_size=self.tab_space_size,
                )

                # Make fixes
                fixes = self._coerce_indent_to(
                    desired_indent=desired_indent,
                    current_indent_buffer=this_line["indent_buffer"],
                    current_anchor=trigger_segment,
                )

                memory["problem_lines"].append(this_line_no)
                return LintResult(
                    anchor=trigger_segment,
                    memory=memory,
                    description="Line over-indented compared to line #{}".format(k),
                    fixes=fixes,
                )

        # This was a valid comparison, so if it doesn't flag then
        # we can assume that we're ok.
        self.logger.debug("    Indent deemed ok comparing to #%s", k)

        # Given that this line is ok, consider if the preceding lines are
        # comments. If they are, lint the indentation of the comment(s).
        fixes_list: List[LintFix] = []
        anchor: Optional[BaseSegment] = None
        for n in range(this_line_no - 1, -1, -1):
            if n not in memory["comment_lines"]:
                break
            # The previous line WAS a comment.
            prev_line = res[n]
            if this_line["indent_size"] == prev_line["indent_size"]:
                continue
            # It's not aligned.
            # Find the anchor first.
            for seg in prev_line["line_buffer"]:
                if seg.is_type("comment"):
                    anchor = seg
                    break

            if not anchor:
                # Without an anchor we cant fix anything
                continue
            fixes_list += self._coerce_indent_to(
                desired_indent="".join(elem.raw for elem in this_line["indent_buffer"]),
                current_indent_buffer=prev_line["indent_buffer"],
                current_anchor=anchor,
            )

            memory["problem_lines"].append(n)

        if fixes_list:
            return LintResult(
                anchor=anchor,
                memory=memory,
                description="Comment not aligned with following line.",
                fixes=fixes_list,
            )

        # NB: At shallower indents, we don't check, we just check the
        # previous lines with the same balance. Deeper indents can check
        # themselves.
        return LintResult(memory=memory)


class _TemplateLineInterpreter:
    def __init__(
        self,
        current_line: List[BaseSegment],
        templated_file: Optional[TemplatedFile],
    ) -> None:
        self.current_line = [el for el in current_line if not el.is_whitespace]
        self.templated_file = templated_file

    @property
    def template_content(self):
        return "".join(
            seg.raw or getattr(seg, "source_str", "") for seg in self.current_line
        )

    def is_single_placeholder_line(self):
        count_placeholder = 0
        for seg in self.current_line:
            if seg.is_code:
                return False
            elif seg.is_type("placeholder"):
                count_placeholder += 1
        return count_placeholder == 1

    def list_segement_and_raw_segement_types(self):
        """Yields the tuple of seg type and underlying type were applicable."""
        for seg in self.current_line:
            raw_seg = self.get_raw_slices(seg)
            yield (seg.type, raw_seg[0].slice_type if raw_seg else None)

    def iterate_type_pairs(self):
        """Produce a list of pairs of each sequenctial combo of two."""
        iterable = self.list_segement_and_raw_segement_types()
        a, b = itertools.tee(iterable)
        # consume the first item in b
        next(b, None)
        return zip(a, b)

    def is_block_start(self):
        # Check for this sequence
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
        valid_combos = list(
            itertools.product(
                start_blocks,
                indent_types,
            )
        )
        return any(pair in valid_combos for pair in self.iterate_type_pairs())

    def is_block_end(self):
        # Check for this sequence
        dedent_types = (("dedent", None),)
        end_block = (
            ("placeholder", "block_end"),
            ("placeholder", "compound"),
            ("placeholder", "block_mid"),
        )
        valid_combos = list(
            itertools.product(
                dedent_types,
                end_block,
            )
        )
        return any(pair in valid_combos for pair in self.iterate_type_pairs())

    def block_type(self) -> Optional[str]:
        """Return a block_type enum."""
        if not self.templated_file:
            return None

        if not self.is_single_placeholder_line():
            return None

        if self.is_block_end():
            return "end"

        if self.is_block_start():
            return "start"

        return None

    def get_raw_slices(self, elem: BaseSegment) -> Optional[List[RawFileSlice]]:
        if not self.templated_file:
            return None

        if not elem.is_type("placeholder"):
            return None

        assert elem.pos_marker, "TypeGuard"
        slices = self.templated_file.raw_slices_spanning_source_slice(
            elem.pos_marker.source_slice
        )
        return slices or None


def _find_comparison_line(
    lines_before: Iterable[_LineSummary],
    this_line: _LineSummary,
    ignoreable_lines: List[int],
) -> Optional[_LineSummary]:
    for prev_line in lines_before:
        # Skip lines with problems
        if prev_line.line_no in ignoreable_lines:
            continue

        # Skip empty lines
        if not any(
            elem.is_code or elem.is_type("placeholder")
            for elem in prev_line.line_buffer
        ):
            continue

        # Work out the difference in indent
        indent_diff = this_line["indent_balance"] - prev_line["indent_balance"]
        # If we're comparing to a previous, more deeply indented line, then skip and
        # keep looking.
        if indent_diff < 0:
            continue
        return prev_line

    return None


def _find_final_trigger(
    raw_stack: List[Tuple[BaseSegment, bool]]
) -> Optional[BaseSegment]:
    """Pull out the last line worth of items and find first code el."""
    last_line: List[Tuple[BaseSegment, bool]] = []
    for i, raw_info in enumerate(reversed(raw_stack)):
        elem = raw_info[0]
        if elem.is_type("newline") and i != 0:
            break
        last_line.append(raw_info)

    for el, is_ignoreable in reversed(last_line):
        if el.is_type("newline", "whitespace"):
            continue

        if is_ignoreable:
            continue

        if el.segments:
            continue

        if el.is_meta and el.indent_val != 0:  # type: ignore
            continue

        return el

    return None
