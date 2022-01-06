"""Implementation of Rule L003."""
from typing import List, Optional, Sequence, Tuple

from sqlfluff.core.parser import WhitespaceSegment
from sqlfluff.core.parser.segments import BaseSegment, RawSegment
from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)
from sqlfluff.core.templaters import TemplatedFile


@document_fix_compatible
@document_configuration
class Rule_L003(BaseRule):
    """Indentation not consistent with previous lines.

    Note:
        This rule used to be _"Indentation length is not a multiple
        of `tab_space_size`"_, but was changed to be much smarter.

    | **Anti-pattern**
    | The • character represents a space.
    | In this example, the third line contains five spaces instead of four.

    .. code-block:: sql
       :force:

        SELECT
        ••••a,
        •••••b
        FROM foo


    | **Best practice**
    | Change the indentation to use a multiple of four spaces.

    .. code-block:: sql
       :force:

        SELECT
        ••••a,
        ••••b
        FROM foo

    """

    _works_on_unparsable = False
    _ignore_types: List[str] = ["script_content"]
    config_keywords = ["tab_space_size", "indent_unit"]

    @staticmethod
    def _make_indent(
        num: int = 1, tab_space_size: int = 4, indent_unit: str = "space"
    ) -> str:
        if indent_unit == "tab":
            base_unit = "\t"
        elif indent_unit == "space":
            base_unit = " " * tab_space_size
        else:
            raise ValueError(
                f"Parameter indent_unit has unexpected value: `{indent_unit}`. Expected `tab` or `space`."
            )
        return base_unit * num

    @staticmethod
    def _indent_size(segments: Sequence[BaseSegment], tab_space_size: int = 4) -> int:
        indent_size = 0
        for elem in segments:
            raw = elem.raw
            # convert to spaces for convenience (and hanging indents)
            raw = raw.replace("\t", " " * tab_space_size)
            indent_size += len(raw)
        return indent_size

    @classmethod
    def _process_raw_stack(
        cls,
        raw_stack: Tuple[BaseSegment, ...],
        memory: dict = None,
        tab_space_size: int = 4,
        templated_file: Optional[TemplatedFile] = None,
    ) -> dict:
        """Take the raw stack, split into lines and evaluate some stats."""
        indent_balance = 0
        line_no = 1
        in_indent = True
        indent_buffer: List[BaseSegment] = []
        line_buffer: List[BaseSegment] = []
        result_buffer = {}
        indent_size = 0
        line_indent_stack: List[int] = []
        this_indent_balance = 0
        clean_indent = False
        hanger_pos = None

        for elem in raw_stack:
            line_buffer.append(elem)
            # Pin indent_balance to above zero
            if indent_balance < 0:
                indent_balance = 0

            if elem.is_type("newline"):
                result_buffer[line_no] = {
                    "line_no": line_no,
                    # Using slicing to copy line_buffer here to be py2 compliant
                    "line_buffer": line_buffer[:],
                    "indent_buffer": indent_buffer,
                    "indent_size": indent_size,
                    # Indent balance is the indent at the start of the first content
                    "indent_balance": this_indent_balance,
                    "hanging_indent": hanger_pos if line_indent_stack else None,
                    # Clean indent is true if the line *ends* with an indent
                    # or has an indent in the initial whitespace.
                    "clean_indent": clean_indent,
                }
                line_no += 1
                indent_buffer = []
                line_buffer = []
                indent_size = 0
                in_indent = True
                line_indent_stack = []
                hanger_pos = None
                # Assume an unclean indent, but if the last line
                # ended with an indent then we might be ok.
                clean_indent = False
                # Was there an indent after the last code element of the previous line?
                for search_elem in reversed(result_buffer[line_no - 1]["line_buffer"]):  # type: ignore
                    if not search_elem.is_code and not search_elem.is_meta:
                        continue
                    elif search_elem.is_meta and search_elem.indent_val > 0:
                        clean_indent = True
                    break
            elif in_indent:
                if elem.is_type("whitespace"):
                    indent_buffer.append(elem)
                elif elem.is_meta and elem.indent_val != 0:  # type: ignore
                    indent_balance += elem.indent_val  # type: ignore
                    if elem.indent_val > 0:  # type: ignore
                        # a "clean" indent is one where it contains
                        # an increase in indentation? Can't quite
                        # remember the logic here. Let's go with that.
                        clean_indent = True
                else:
                    in_indent = False
                    this_indent_balance = indent_balance
                    indent_size = cls._indent_size(
                        indent_buffer, tab_space_size=tab_space_size
                    )
            elif elem.is_meta and elem.indent_val != 0:  # type: ignore
                indent_balance += elem.indent_val  # type: ignore
                if elem.indent_val > 0:  # type: ignore
                    # Keep track of the indent at the last ... indent
                    line_indent_stack.append(
                        cls._indent_size(line_buffer, tab_space_size=tab_space_size)
                    )
                    hanger_pos = None
                else:
                    # this is a dedent, we could still have a hanging indent,
                    # but only if there's enough on the stack
                    if line_indent_stack:
                        line_indent_stack.pop()
            elif elem.is_code:
                if hanger_pos is None:
                    hanger_pos = cls._indent_size(
                        line_buffer[:-1], tab_space_size=tab_space_size
                    )

            # If we hit the trigger element, stop processing.
            if memory and elem is memory["trigger"]:
                break

        # If we get to the end, and still have a buffer, add it on
        if line_buffer:
            result_buffer[line_no] = {
                "line_no": line_no,
                "line_buffer": line_buffer,
                "indent_buffer": indent_buffer,
                "indent_size": indent_size,
                "indent_balance": this_indent_balance,
                "hanging_indent": line_indent_stack.pop()
                if line_indent_stack
                else None,
                "clean_indent": clean_indent,
            }
        return result_buffer

    def _coerce_indent_to(
        self,
        desired_indent: str,
        current_indent_buffer: Tuple[RawSegment, ...],
        current_anchor: BaseSegment,
    ) -> List[LintFix]:
        """Generate fixes to make an indent a certain size."""
        # If there shouldn't be an indent at all, just delete.
        if len(desired_indent) == 0:
            fixes = [LintFix.delete(elem) for elem in current_indent_buffer]
        # If we don't have any indent and we should, then add a single
        elif len("".join(elem.raw for elem in current_indent_buffer)) == 0:
            fixes = [
                LintFix.create_before(
                    current_anchor,
                    [
                        WhitespaceSegment(
                            raw=desired_indent,
                        ),
                    ],
                ),
            ]
        # Otherwise edit the first element to be the right size
        else:
            # Edit the first element of this line's indent and remove any other
            # indents.
            fixes = [
                LintFix.replace(
                    current_indent_buffer[0],
                    [
                        WhitespaceSegment(
                            raw=desired_indent,
                        ),
                    ],
                ),
            ] + [LintFix.delete(elem) for elem in current_indent_buffer[1:]]
        return fixes

    @staticmethod
    def _strip_buffers(line_dict: dict) -> dict:
        """Strip a line dict of buffers for logging."""
        return {
            key: line_dict[key]
            for key in line_dict
            if key not in ("line_buffer", "indent_buffer")
        }

    @classmethod
    def _is_last_segment(
        cls,
        segment: BaseSegment,
        memory: dict,
        parent_stack: Tuple[BaseSegment, ...],
        siblings_post: Tuple[BaseSegment, ...],
    ) -> bool:
        """Returns True if 'segment' is the very last node in the parse tree."""
        if siblings_post:
            # We have subsequent siblings. Not finished.
            return False
        elif parent_stack:
            # No subsequent siblings. Our parent is finished.
            memory["finished"].add(parent_stack[-1])
        if segment.segments:
            # We have children. Not finished.
            return False

        # We have no subsequent siblings or children. If all our parents are
        # finished, the whole parse tree is finished.
        for parent in parent_stack:
            if parent not in memory["finished"]:
                return False
        return True

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

        raw_stack: Tuple[BaseSegment, ...] = context.raw_stack

        # We ignore certain types (e.g. non-SQL scripts in functions)
        # so check if on ignore list
        if context.segment.type in self._ignore_types:
            return LintResult()
        for parent in context.parent_stack:
            if parent.type in self._ignore_types:
                return LintResult()

        # Memory keeps track of what we've seen
        if not context.memory:
            memory: dict = {
                # in_indent keeps track of whether we're in an indent right now
                "in_indent": True,
                # problem_lines keeps track of lines with problems so that we
                # don't compare to them.
                "problem_lines": [],
                # hanging_lines keeps track of hanging lines so that we don't
                # compare to them when assessing indent.
                "hanging_lines": [],
                # comment_lines keeps track of lines which are all comment.
                "comment_lines": [],
                # segments we've seen the last child of
                "finished": set(),
                # First non-whitespace node on a line.
                "trigger": None,
            }
        else:
            memory = context.memory

        if context.segment.is_type("newline"):
            memory["in_indent"] = True
        elif memory["in_indent"]:
            if context.segment.is_type("whitespace"):
                # it's whitespace, carry on
                pass
            elif context.segment.segments or (context.segment.is_meta and context.segment.indent_val != 0):  # type: ignore
                # it's not a raw segment or placeholder. Carry on.
                pass
            else:
                memory["in_indent"] = False
                # we're found a non-whitespace element. This is our trigger,
                # which we'll handle after this if-statement
                memory["trigger"] = context.segment
        else:
            # Not in indent and not a newline, don't trigger here.
            pass

        # Is this the last segment? If so, need to "flush" any leftovers.
        is_last = self._is_last_segment(
            context.segment, memory, context.parent_stack, context.siblings_post
        )

        if not context.segment.is_type("newline") and not is_last:
            # We only process complete lines or on the very last segment
            # (since there may not be a newline on the very last line)..
            return LintResult(memory=memory)

        if raw_stack and raw_stack[-1] is not context.segment:
            raw_stack = raw_stack + (context.segment,)
        res = self._process_raw_stack(
            raw_stack,
            memory,
            tab_space_size=self.tab_space_size,
            templated_file=context.templated_file,
        )

        if res:
            # Saw a newline or end of parse tree. Is the current line empty?
            trigger_segment = memory["trigger"]
            if trigger_segment:
                # Not empty. Process it.
                result = self._process_current_line(res, memory, context)
                if context.segment.is_type("newline"):
                    memory["trigger"] = None
                return result
        return LintResult(memory=memory)

    def _process_current_line(
        self, res: dict, memory: dict, context: RuleContext
    ) -> LintResult:
        """Checks indentation of one line of code, returning a LintResult.

        The _eval() function calls it for the current line of code:
        - When passed a newline segment (thus ending a line)
        - When passed the *final* segment in the entire parse tree (which may
          not be a newline)
        """
        this_line_no = max(res.keys())
        this_line = res.pop(this_line_no)
        self.logger.debug(
            "Evaluating line #%s. %s",
            this_line_no,
            # Don't log the line or indent buffer, it's too noisy.
            self._strip_buffers(this_line),
        )
        trigger_segment = memory["trigger"]

        # Is this line just comments? (Disregard trailing newline if present.)
        check_comment_line = this_line["line_buffer"]
        if check_comment_line and all(
            seg.is_type(
                "whitespace", "comment", "indent"  # dedent is a subtype of indent
            )
            for seg in check_comment_line
        ):
            # Comment line, deal with it later.
            memory["comment_lines"].append(this_line_no)
            self.logger.debug("    Comment Line. #%s", this_line_no)
            return LintResult(memory=memory)

        # Is it a hanging indent?
        # Find last meaningful line indent.
        last_code_line = None
        for k in sorted(res.keys(), reverse=True):
            if any(seg.is_code for seg in res[k]["line_buffer"]):
                last_code_line = k
                break

        if len(res) > 0 and last_code_line:
            last_line_hanger_indent = res[last_code_line]["hanging_indent"]
            # Let's just deal with hanging indents here.
            if (
                # NB: Hangers are only allowed if there was content after the last
                # indent on the previous line. Otherwise it's just an indent.
                this_line["indent_size"] == last_line_hanger_indent
                # Or they're if the indent balance is the same and the indent is the
                # same AND the previous line was a hanger
                or (
                    this_line["indent_size"] == res[last_code_line]["indent_size"]
                    and this_line["indent_balance"]
                    == res[last_code_line]["indent_balance"]
                    and last_code_line in memory["hanging_lines"]
                )
            ) and (
                # There MUST also be a non-zero indent. Otherwise we're just on the baseline.
                this_line["indent_size"]
                > 0
            ):
                # This is a HANGER
                memory["hanging_lines"].append(this_line_no)
                self.logger.debug("    Hanger Line. #%s", this_line_no)
                self.logger.debug(
                    "    Last Line: %s", self._strip_buffers(res[last_code_line])
                )
                return LintResult(memory=memory)

        # Is this an indented first line?
        elif len(res) == 0:
            if this_line["indent_size"] > 0:
                self.logger.debug("    Indented First Line. #%s", this_line_no)
                return LintResult(
                    anchor=trigger_segment,
                    memory=memory,
                    description="First line has unexpected indent",
                    fixes=[LintFix.delete(elem) for elem in this_line["indent_buffer"]],
                )

        # Special handling for template end blocks on a line by themselves.
        if self._is_template_block_end_line(
            this_line["line_buffer"], context.templated_file
        ):
            block_lines = {
                k: (
                    "end"
                    if self._is_template_block_end_line(
                        res[k]["line_buffer"], context.templated_file
                    )
                    else "start",
                    res[k]["indent_balance"],
                    "".join(
                        seg.raw or getattr(seg, "source_str", "")
                        for seg in res[k]["line_buffer"]
                    ),
                )
                for k in res
                if self._is_template_block_end_line(
                    res[k]["line_buffer"], context.templated_file
                )
                or self._is_template_block_start_line(
                    res[k]["line_buffer"], context.templated_file
                )
            }

            # For a template block end on a line by itself, search for a
            # matching block start on a line by itself. If there is one, match
            # its indentation. Question: Could we avoid treating this as a
            # special case? It has some similarities to the non-templated test
            # case test/fixtures/linter/indentation_error_contained.sql, in tha
            # both have lines where indent_balance drops 2 levels from one line
            # to the next, making it a bit unclear how to indent that line.
            template_block_level = -1
            for k in sorted(block_lines.keys(), reverse=True):
                if block_lines[k][0] == "end":
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
                if this_line["indent_size"] == res[k]["indent_size"]:
                    # All good.
                    return LintResult(memory=memory)

                # Indents don't match even though balance is the same...
                memory["problem_lines"].append(this_line_no)

                # The previous indent.
                desired_indent = "".join(elem.raw for elem in res[k]["indent_buffer"])

                # Make fixes
                fixes = self._coerce_indent_to(
                    desired_indent=desired_indent,
                    current_indent_buffer=this_line["indent_buffer"],
                    current_anchor=this_line["line_buffer"][0],
                )
                self.logger.debug(
                    "    !! Indentation does not match #%s. Fixes: %s", k, fixes
                )
                return LintResult(
                    anchor=trigger_segment,
                    memory=memory,
                    description="Indentation not consistent with line #{}".format(k),
                    # See above for logic
                    fixes=fixes,
                )

        # Assuming it's not a hanger, let's compare it to the other previous
        # lines. We do it in reverse so that closer lines are more relevant.
        for k in sorted(res.keys(), reverse=True):

            # Is this a problem line?
            if k in memory["problem_lines"] + memory["hanging_lines"]:
                # Skip it if it is
                continue

            # Is this an empty line?
            if not any(
                elem.is_code or elem.is_type("placeholder")
                for elem in res[k]["line_buffer"]
            ):
                # Skip if it is
                continue

            # Work out the difference in indent
            indent_diff = this_line["indent_balance"] - res[k]["indent_balance"]
            # If we're comparing to a previous, more deeply indented line, then skip and keep looking.
            if indent_diff < 0:
                continue

            # Is the indent balance the same?
            if indent_diff == 0:
                self.logger.debug("    [same indent balance] Comparing to #%s", k)
                if this_line["indent_size"] != res[k]["indent_size"]:
                    # Indents don't match even though balance is the same...
                    memory["problem_lines"].append(this_line_no)

                    # Work out desired indent
                    if res[k]["indent_size"] == 0:
                        desired_indent = ""
                    elif this_line["indent_size"] == 0:
                        desired_indent = self._make_indent(
                            indent_unit=self.indent_unit,
                            tab_space_size=self.tab_space_size,
                        )
                    else:
                        # The previous indent.
                        desired_indent = "".join(
                            elem.raw for elem in res[k]["indent_buffer"]
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
                        description="Indentation not consistent with line #{}".format(
                            k
                        ),
                        # See above for logic
                        fixes=fixes,
                    )
            # Are we at a deeper indent?
            elif indent_diff > 0:
                self.logger.debug("    [deeper indent balance] Comparing to #%s", k)
                # NB: We shouldn't need to deal with correct hanging indents
                # here, they should already have been dealt with before. We
                # may still need to deal with *creating* hanging indents if
                # appropriate.
                self.logger.debug(
                    "    Comparison Line: %s", self._strip_buffers(res[k])
                )

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
                        elem.raw for elem in res[k]["indent_buffer"]
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
                    elif res[k]["hanging_indent"]:
                        self.logger.debug("        Use hanging indent.")
                        desired_indent = " " * res[k]["hanging_indent"]
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
                else:
                    # We'll need this value later.
                    this_indent_num = this_line["indent_size"] // self.tab_space_size

                # We know that the indent balance is higher, what actually is
                # the difference in indent counts? It should be a whole number
                # if we're still here.
                comp_indent_num = res[k]["indent_size"] // self.tab_space_size

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

                    # First work out if we have some closing brackets, and if so, how many.
                    b_idx = 0
                    b_num = 0
                    while True:
                        if len(this_line["line_buffer"][b_idx:]) == 0:
                            break

                        elem = this_line["line_buffer"][b_idx]
                        if not elem.is_code:
                            b_idx += 1
                            continue
                        else:
                            if elem.is_type("end_bracket", "end_square_bracket"):
                                b_idx += 1
                                b_num += 1
                                continue
                            break  # pragma: no cover

                    if b_num >= indent_diff:
                        # It does. This line is fine.
                        pass
                    else:
                        # It doesn't. That means we *should* have an indent when compared to
                        # this line and we DON'T.
                        memory["problem_lines"].append(this_line_no)
                        return LintResult(
                            anchor=trigger_segment,
                            memory=memory,
                            description="Indent expected and not found compared to line #{}".format(
                                k
                            ),
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
                        description="Line under-indented compared to line #{}".format(
                            k
                        ),
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
            fixes = []
            for n in range(this_line_no - 1, -1, -1):
                if n in memory["comment_lines"]:
                    # The previous line WAS a comment.
                    prev_line = res[n]
                    if this_line["indent_size"] != prev_line["indent_size"]:
                        # It's not aligned.
                        # Find the anchor first.
                        anchor: BaseSegment = None  # type: ignore
                        for seg in prev_line["line_buffer"]:
                            if seg.is_type("comment"):
                                anchor = seg
                                break
                        # Make fixes.
                        fixes += self._coerce_indent_to(
                            desired_indent="".join(
                                elem.raw for elem in this_line["indent_buffer"]
                            ),
                            current_indent_buffer=prev_line["indent_buffer"],
                            current_anchor=anchor,
                        )

                        memory["problem_lines"].append(n)
                else:
                    break

            if fixes:
                return LintResult(
                    anchor=anchor,
                    memory=memory,
                    description="Comment not aligned with following line.",
                    fixes=fixes,
                )

            # Otherwise all good.
            return LintResult(memory=memory)

            # NB: At shallower indents, we don't check, we just check the
            # previous lines with the same balance. Deeper indents can check
            # themselves.

        # If we get to here, then we're all good for now.
        return LintResult(memory=memory)

    @classmethod
    def _get_element_template_info(
        cls, elem: BaseSegment, templated_file: Optional[TemplatedFile]
    ) -> Optional[str]:
        if elem.is_type("placeholder"):
            if templated_file is None:
                raise ValueError("Parameter templated_file cannot be: None.")
            slices = templated_file.raw_slices_spanning_source_slice(
                elem.pos_marker.source_slice
            )
            if slices:
                return slices[0].slice_type
        return None

    @classmethod
    def _single_placeholder_line(cls, current_line):
        count_placeholder = 0
        for seg in current_line:
            if seg.is_code:
                return False
            elif seg.is_type("placeholder"):
                count_placeholder += 1
        return count_placeholder == 1

    @classmethod
    def _is_template_block_start_line(cls, current_line, templated_file):
        def segment_info(idx: int) -> Tuple[str, Optional[str]]:
            """Helper function."""
            seg = current_line[idx]
            return seg.type, cls._get_element_template_info(seg, templated_file)

        if not cls._single_placeholder_line(current_line):
            return False
        for idx in range(1, len(current_line)):
            if (
                segment_info(idx - 1)
                in (
                    ("placeholder", "block_start"),
                    ("placeholder", "compound"),
                    ("placeholder", "block_mid"),
                )
                and segment_info(idx) == ("indent", None)
            ):
                return True
        return False

    @classmethod
    def _is_template_block_end_line(cls, current_line, templated_file):
        def segment_info(idx: int) -> Tuple[str, Optional[str]]:
            """Helper function."""
            seg = current_line[idx]
            return seg.type, cls._get_element_template_info(seg, templated_file)

        if not cls._single_placeholder_line(current_line):
            return False
        for idx in range(1, len(current_line)):
            if segment_info(idx - 1) == ("dedent", None) and segment_info(idx) in (
                ("placeholder", "block_end"),
                ("placeholder", "compound"),
                ("placeholder", "block_mid"),
            ):
                return True
        return False
