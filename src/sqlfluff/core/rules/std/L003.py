"""Implementation of Rule L003."""

from sqlfluff.core.rules.base import BaseCrawler, LintResult, LintFix
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)


@document_fix_compatible
@document_configuration
class Rule_L003(BaseCrawler):
    """Indentation not consistent with previous lines.

    Note:
        This rule used to be _"Indentation length is not a multiple
        of `tab_space_size`"_, but was changed to be much smarter.

    | **Anti-pattern**
    | The • character represents a space.
    | In this example, the third line contains five spaces instead of four.

    .. code-block::

        SELECT
        ••••a,
        •••••b
        FROM foo


    | **Best practice**
    | Change the indentation to use a multiple of four spaces.

    .. code-block::

        SELECT
        ••••a,
        ••••b
        FROM foo

    """

    _works_on_unparsable = False
    config_keywords = ["tab_space_size", "indent_unit", "lint_templated_tokens"]

    def _make_indent(self, num=1, tab_space_size=None, indent_unit=None):
        if (indent_unit or self.indent_unit) == "tab":
            base_unit = "\t"
        elif (indent_unit or self.indent_unit) == "space":
            base_unit = " " * (tab_space_size or self.tab_space_size)
        return base_unit * num

    def _indent_size(self, segments):
        indent_size = 0
        for elem in segments:
            raw = elem.raw
            # convert to spaces for convenience (and hanging indents)
            raw = raw.replace("\t", " " * self.tab_space_size)
            indent_size += len(raw)
        return indent_size

    def _process_raw_stack(self, raw_stack):
        """Take the raw stack, split into lines and evaluate some stats."""
        indent_balance = 0
        line_no = 1
        in_indent = True
        indent_buffer = []
        line_buffer = []
        result_buffer = {}
        indent_size = 0
        line_indent_stack = []
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
                    # Clean indent is true if the line *ends* win an indent
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
                for search_elem in reversed(result_buffer[line_no - 1]["line_buffer"]):
                    if not search_elem.is_code and not search_elem.is_meta:
                        continue
                    elif search_elem.is_meta and search_elem.indent_val > 0:
                        clean_indent = True
                    break
            elif in_indent:
                if elem.is_type("whitespace"):
                    indent_buffer.append(elem)
                elif elem.is_meta and elem.indent_val != 0:
                    indent_balance += elem.indent_val
                    if elem.indent_val > 0:
                        # a "clean" indent is one where it contains
                        # an increase in indentation? Can't quite
                        # remember the logic here. Let's go with that.
                        clean_indent = True
                else:
                    in_indent = False
                    this_indent_balance = indent_balance
                    indent_size = self._indent_size(indent_buffer)
            elif elem.is_meta and elem.indent_val != 0:
                indent_balance += elem.indent_val
                if elem.indent_val > 0:
                    # Keep track of the indent at the last ... indent
                    line_indent_stack.append(self._indent_size(line_buffer))
                    hanger_pos = None
                else:
                    # this is a dedent, we could still have a hanging indent,
                    # but only if there's enough on the stack
                    if line_indent_stack:
                        line_indent_stack.pop()
            elif elem.is_code:
                if hanger_pos is None:
                    hanger_pos = self._indent_size(line_buffer[:-1])

        # If we get to the end, and still have a buffer, add it on
        if line_buffer:
            result_buffer[line_no] = {
                "line_no": line_no,
                "line_buffer": line_buffer,
                "indent_buffer": indent_buffer,
                "indent_size": indent_size,
                "indent_balance": indent_balance,
                "hanging_indent": line_indent_stack.pop()
                if line_indent_stack
                else None,
                "clean_indent": clean_indent,
            }
        return result_buffer

    def _coerce_indent_to(self, desired_indent, current_indent_buffer, current_anchor):
        """Generate fixes to make an indent a certain size."""
        # If there shouldn't be an indent at all, just delete.
        if len(desired_indent) == 0:
            fixes = [LintFix("delete", elem) for elem in current_indent_buffer]
        # If we don't have any indent and we should, then add a single
        elif len("".join(elem.raw for elem in current_indent_buffer)) == 0:
            fixes = [
                LintFix(
                    "create",
                    current_anchor,
                    self.make_whitespace(
                        raw=desired_indent, pos_marker=current_anchor.pos_marker
                    ),
                )
            ]
        # Otherwise edit the first element to be the right size
        else:
            # Edit the first element of this line's indent.
            fixes = [
                LintFix(
                    "edit",
                    current_indent_buffer[0],
                    self.make_whitespace(
                        raw=desired_indent,
                        pos_marker=current_indent_buffer[0].pos_marker,
                    ),
                )
            ]
        return fixes

    def _eval(self, segment, raw_stack, memory, **kwargs):
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
        # Memory keeps track of what we just saw
        if not memory:
            memory = {
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
            }

        if segment.is_type("newline"):
            memory["in_indent"] = True
            # We're not going to flag on empty lines so we can safely proceed
            return LintResult(memory=memory)
        elif memory["in_indent"]:
            if segment.is_type("whitespace"):
                # it's whitespace, carry on
                return LintResult(memory=memory)
            elif segment.segments or (segment.is_meta and segment.indent_val != 0):
                # it's not a raw segment or placeholder. Carry on.
                return LintResult(memory=memory)
            else:
                memory["in_indent"] = False
                # we're found a non-whitespace element. This is our trigger,
                # which we'll handle after this if-statement
        else:
            # Not in indent and not a newline, don't trigger here.
            return LintResult(memory=memory)

        res = self._process_raw_stack(raw_stack + (segment,))
        this_line_no = max(res.keys())
        this_line = res.pop(this_line_no)
        self.logger.debug(
            "Evaluating line #%s. %s",
            this_line_no,
            # Don't log the line or indent buffer, it's too noisy.
            {
                key: this_line[key]
                for key in this_line
                if key not in ("line_buffer", "indent_buffer")
            },
        )

        # Is this line just comments?
        if all(
            seg.is_type(
                "whitespace", "comment", "indent"  # dedent is a subtype of indent
            )
            for seg in this_line["line_buffer"]
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
                return LintResult(memory=memory)

        # Is this an indented first line?
        elif len(res) == 0:
            if this_line["indent_size"] > 0:
                self.logger.debug("    Indented First Line. #%s", this_line_no)
                return LintResult(
                    anchor=segment,
                    memory=memory,
                    description="First line has unexpected indent",
                    fixes=[
                        LintFix("delete", elem) for elem in this_line["indent_buffer"]
                    ],
                )

        # Are we linting a placeholder, and if so are we allowed to?
        if (not self.lint_templated_tokens) and this_line["line_buffer"][
            len(this_line["indent_buffer"]) :
        ][0].is_type("placeholder"):
            # If not, make this a problem line and carry on.
            memory["problem_lines"].append(this_line_no)
            self.logger.debug(
                "    Avoiding template placeholder Line. #%s", this_line_no
            )
            return LintResult(memory=memory)

        # Assuming it's not a hanger, let's compare it to the other previous
        # lines. We do it in reverse so that closer lines are more relevant.
        for k in sorted(res.keys(), reverse=True):

            # Is this a problem line?
            if k in memory["problem_lines"] + memory["hanging_lines"]:
                # Skip it if it is
                continue

            # Is this an empty line?
            if not any(elem.is_code for elem in res[k]["line_buffer"]):
                # Skip if it is
                continue

            # Work out the difference in indent
            indent_diff = this_line["indent_balance"] - res[k]["indent_balance"]
            # If we're comparing to a previous, more deeply indented line, then skip and keep looking.
            if indent_diff < 0:
                continue
            # Is the indent balance the same?
            elif indent_diff == 0:
                self.logger.debug("    [same indent balance] Comparing to #%s", k)
                if this_line["indent_size"] != res[k]["indent_size"]:
                    # Indents don't match even though balance is the same...
                    memory["problem_lines"].append(this_line_no)

                    # Work out desired indent
                    if res[k]["indent_size"] == 0:
                        desired_indent = ""
                    elif this_line["indent_size"] == 0:
                        desired_indent = self._make_indent()
                    else:
                        # The previous indent.
                        desired_indent = "".join(
                            elem.raw for elem in res[k]["indent_buffer"]
                        )

                    # Make fixes
                    fixes = self._coerce_indent_to(
                        desired_indent=desired_indent,
                        current_indent_buffer=this_line["indent_buffer"],
                        current_anchor=segment,
                    )
                    self.logger.debug(
                        "    !! Indentation does not match #%s. Fixes: %s", k, fixes
                    )
                    return LintResult(
                        anchor=segment,
                        memory=memory,
                        description="Indentation not consistent with line #{0}".format(
                            k
                        ),
                        # See above for logic
                        fixes=fixes,
                    )
            # Are we at a deeper indent?
            elif indent_diff > 0:
                self.logger.debug("    [deeper indent balance] Comparing to #%s", k)
                # NB: We shouldn't need to deal with hanging indents
                # here, they should already have been dealt with before.

                # Check to see if we've got a whole number of multiples. If
                # we do then record the number for later, otherwise raise
                # an error. We do the comparison here so we have a reference
                # point to do the repairs. We need a sensible previous line
                # to base the repairs off.
                if this_line["indent_size"] % self.tab_space_size != 0:
                    memory["problem_lines"].append(this_line_no)

                    # If we have a clean indent, we can just add steps in line
                    # with the difference in the indent buffers. simples.
                    # We can also do this if we've skipped a line. I think?
                    if this_line["clean_indent"] or this_line_no - k > 1:
                        desired_indent = "".join(
                            elem.raw for elem in res[k]["indent_buffer"]
                        ) + (self._make_indent() * indent_diff)
                    # If we have the option of a hanging indent then use it.
                    elif res[k]["hanging_indent"]:
                        desired_indent = " " * res[k]["hanging_indent"]
                    else:
                        raise RuntimeError(
                            "Unexpected case, please report bug, including the query you are linting!"
                        )

                    # Make fixes
                    fixes = self._coerce_indent_to(
                        desired_indent=desired_indent,
                        current_indent_buffer=this_line["indent_buffer"],
                        current_anchor=segment,
                    )

                    return LintResult(
                        anchor=segment,
                        memory=memory,
                        description=(
                            "Indentation not hanging or " "a multiple of {0} spaces"
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
                            break

                    if b_num >= indent_diff:
                        # It does. This line is fine.
                        pass
                    else:
                        # It doesn't. That means we *should* have an indent when compared to
                        # this line and we DON'T.
                        memory["problem_lines"].append(this_line_no)
                        return LintResult(
                            anchor=segment,
                            memory=memory,
                            description="Indent expected and not found compared to line #{0}".format(
                                k
                            ),
                            # Add in an extra bit of whitespace for the indent
                            fixes=[
                                LintFix(
                                    "create",
                                    segment,
                                    self.make_whitespace(
                                        raw=self._make_indent(),
                                        pos_marker=segment.pos_marker,
                                    ),
                                )
                            ],
                        )
                elif this_indent_num < comp_indent_num:
                    memory["problem_lines"].append(this_line_no)
                    return LintResult(
                        anchor=segment,
                        memory=memory,
                        description="Line under-indented compared to line #{0}".format(
                            k
                        ),
                        fixes=[
                            LintFix(
                                "create",
                                segment,
                                self.make_whitespace(
                                    # Make the minimum indent for it to be ok.
                                    raw=self._make_indent(
                                        num=comp_indent_num - this_indent_num
                                    ),
                                    pos_marker=segment.pos_marker,
                                ),
                            )
                        ],
                    )
                elif this_indent_num > comp_indent_num + indent_diff:
                    # Calculate the lowest ok indent:
                    desired_indent = self._make_indent(
                        num=comp_indent_num - this_indent_num
                    )

                    # Make fixes
                    fixes = self._coerce_indent_to(
                        desired_indent=desired_indent,
                        current_indent_buffer=this_line["indent_buffer"],
                        current_anchor=segment,
                    )

                    memory["problem_lines"].append(this_line_no)
                    return LintResult(
                        anchor=segment,
                        memory=memory,
                        description="Line over-indented compared to line #{0}".format(
                            k
                        ),
                        fixes=fixes,
                    )

            # This was a valid comparison, so if it doesn't flag then
            # we can assume that we're ok.
            self.logger.debug("    Indent deemed ok comparing to #%s", k)

            # Given that this line is ok, consider if the previous line is a comment.
            # If it is, lint the indentation of that comment.
            if this_line_no - 1 in memory["comment_lines"]:
                # The previous line WAS as comment.
                prev_line = res[this_line_no - 1]
                if this_line["indent_size"] != prev_line["indent_size"]:
                    # It's not aligned.
                    # Find the anchor first.
                    anchor = None
                    for seg in prev_line["line_buffer"]:
                        if seg.is_type("comment"):
                            anchor = seg
                            break
                    # Make fixes.
                    fixes = self._coerce_indent_to(
                        desired_indent="".join(
                            elem.raw for elem in this_line["indent_buffer"]
                        ),
                        current_indent_buffer=prev_line["indent_buffer"],
                        current_anchor=anchor,
                    )

                    memory["problem_lines"].append(this_line_no - 1)
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
