"""Standard SQL Linting Rules."""

import itertools
from typing import Tuple, List, Dict, Any

from .base import BaseCrawler, LintFix, LintResult, RuleSet
from .config_info import STANDARD_CONFIG_INFO_DICT

std_rule_set = RuleSet(name="standard", config_info=STANDARD_CONFIG_INFO_DICT)


@std_rule_set.document_fix_compatible
@std_rule_set.register
class Rule_L001(BaseCrawler):
    """Unnecessary trailing whitespace.

    | **Anti-pattern**
    | The • character represents a space.

    .. code-block::

        SELECT
            a
        FROM foo••

    | **Best practice**
    | Remove trailing spaces.

    .. code-block::

        SELECT
            a
        FROM foo
    """

    def _eval(self, segment, raw_stack, **kwargs):
        """Unneccessary trailing whitespace.

        Look for newline segments, and then evaluate what
        it was preceeded by.
        """
        # We only trigger on newlines
        if (
            segment.is_type("newline")
            and len(raw_stack) > 0
            and raw_stack[-1].is_type("whitespace")
        ):
            # If we find a newline, which is preceeded by whitespace, then bad
            deletions = []
            idx = -1
            while raw_stack[idx].is_type("whitespace"):
                deletions.append(raw_stack[idx])
                idx -= 1
            return LintResult(
                anchor=deletions[-1], fixes=[LintFix("delete", d) for d in deletions]
            )
        return LintResult()


@std_rule_set.document_configuration
@std_rule_set.register
class Rule_L002(BaseCrawler):
    """Mixed Tabs and Spaces in single whitespace.

    This rule will fail if a single section of whitespace
    contains both tabs and spaces.

    | **Anti-pattern**
    | The • character represents a space and the → character represents a tab.
    | In this example, the second line contains two spaces and one tab.

    .. code-block::

        SELECT
        ••→a
        FROM foo

    | **Best practice**
    | Change the line to use spaces only.

    .. code-block::

        SELECT
        ••••a
        FROM foo

    """

    config_keywords = ["tab_space_size"]

    def _eval(self, segment, raw_stack, **kwargs):
        """Mixed Tabs and Spaces in single whitespace.

        Only trigger from whitespace segments if they contain
        multiple kinds of whitespace.
        """
        if segment.is_type("whitespace"):
            if " " in segment.raw and "\t" in segment.raw:
                if len(raw_stack) == 0 or raw_stack[-1].is_type("newline"):
                    # We've got a single whitespace at the beginning of a line.
                    # It's got a mix of spaces and tabs. Replace each tab with
                    # a multiple of spaces
                    return LintResult(
                        anchor=segment,
                        fixes=[
                            LintFix(
                                "edit",
                                segment,
                                segment.edit(
                                    segment.raw.replace("\t", " " * self.tab_space_size)
                                ),
                            )
                        ],
                    )


@std_rule_set.document_fix_compatible
@std_rule_set.document_configuration
@std_rule_set.register
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
                "whitespace",
                "comment",
                "indent",  # dedent is a subtype of indent
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
                            "Unexpected case, please report bug, inluding the query you are linting!"
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


@std_rule_set.register
class Rule_L004(BaseCrawler):
    """Mixed Tab and Space indentation found in file.

    | **Anti-pattern**
    | The • character represents a space and the → character represents a tab.
    | In this example, the second line is indented with spaces and the third one with tab.

    .. code-block::

        SELECT
        ••••a,
        →   b
        FROM foo

    | **Best practice**
    | Change the line to use spaces only.

    .. code-block::

        SELECT
        ••••a,
        ••••b
        FROM foo
    """

    def _eval(self, segment, raw_stack, memory, **kwargs):
        """Mixed Tab and Space indentation found in file.

        We use the `memory` feature here to keep track of
        what we've seen in the past.

        """
        indents_seen = memory.get("indents_seen", set())
        if segment.is_type("whitespace"):
            if len(raw_stack) == 0 or raw_stack[-1].is_type("newline"):
                indents_here = set(segment.raw)
                indents_union = indents_here | indents_seen
                memory["indents_seen"] = indents_union
                if len(indents_union) > 1:
                    # We are seeing an indent we haven't seen before and we've seen others before
                    return LintResult(anchor=segment, memory=memory)
                else:
                    return LintResult(memory=memory)
        return LintResult(memory=memory)


@std_rule_set.document_fix_compatible
@std_rule_set.register
class Rule_L005(BaseCrawler):
    """Commas should not have whitespace directly before them.

    Unless it's an indent. Trailing/leading commas are dealt with
    in a different rule.

    | **Anti-pattern**
    | The • character represents a space.
    | There is an extra space in line two before the comma.

    .. code-block::

        SELECT
            a•,
            b
        FROM foo

    | **Best practice**
    | Remove the space before the comma.

    .. code-block::

        SELECT
            a,
            b
        FROM foo
    """

    def _eval(self, segment, raw_stack, **kwargs):
        """Commas should not have whitespace directly before them.

        We need at least one segment behind us for this to work.

        """
        if len(raw_stack) >= 1:
            cm1 = raw_stack[-1]
            if (
                segment.is_type("comma")
                and cm1.is_type("whitespace")
                and cm1.pos_marker.line_pos > 1
            ):
                anchor = cm1
                return LintResult(anchor=anchor, fixes=[LintFix("delete", cm1)])
        # Otherwise fine
        return None


@std_rule_set.document_fix_compatible
@std_rule_set.register
class Rule_L006(BaseCrawler):
    """Operators should be surrounded by a single whitespace.

    | **Anti-pattern**
    | The • character represents a space.
    | In this example, there is a space missing space between the operator and 'b'.

    .. code-block:: sql

        SELECT
            a +b
        FROM foo


    | **Best practice**
    | Keep a single space.

    .. code-block:: sql

        SELECT
            a + b
        FROM foo
    """

    def _eval(self, segment, memory, parent_stack, **kwargs):
        """Operators should be surrounded by a single whitespace.

        We use the memory to keep track of whitespace up to now, and
        whether the last code segment was an operator or not.

        """

        def _handle_previous_segments(segments_since_code, anchor, this_segment, fixes):
            """Handle the list of previous segments and return the new anchor and fixes.

            NB: This function mutates `fixes`.
            """
            if len(segments_since_code) == 0:
                # No whitespace, anchor is the segment AFTER where the whitespace
                # should be.
                anchor = this_segment
                fixes.append(
                    LintFix(
                        "create",
                        this_segment,
                        self.make_whitespace(
                            raw=" ", pos_marker=this_segment.pos_marker
                        ),
                    )
                )
            elif len(segments_since_code) > 1 or any(
                elem.is_type("newline") for elem in segments_since_code
            ):
                # TODO: This is a case we should deal with, but there are probably
                # some cases that SHOULDNT apply here (like comments and newlines)
                # so let's deal with them later
                anchor = None
            else:
                # We know it's just one thing.
                gap_seg = segments_since_code[-1]
                if gap_seg.raw != " ":
                    # It's not just a single space
                    anchor = gap_seg
                    fixes.append(
                        LintFix(
                            "edit",
                            gap_seg,
                            self.make_whitespace(
                                raw=" ", pos_marker=gap_seg.pos_marker
                            ),
                        )
                    )
                else:
                    # We have just the right amount of whitespace!
                    # Unset our signal.
                    anchor = None
            return anchor, fixes

        # anchor is our signal as to whether there's a problem
        anchor = None
        fixes = []
        description = None

        # The parent stack tells us whether we're in an expression or not.
        if parent_stack and parent_stack[-1].is_type("expression"):
            if segment.is_code:
                # This is code, what kind?
                if segment.is_type("binary_operator", "comparison_operator"):
                    # It's an operator, we can evaluate whitespace before it.
                    anchor, fixes = _handle_previous_segments(
                        memory["since_code"],
                        anchor=segment,
                        this_segment=segment,
                        fixes=fixes,
                    )
                    if anchor:
                        description = "Operators should be preceded by a space."
                else:
                    # It's not an operator, we can evaluate what happened after an
                    # operator if that's the last code we saw.
                    if memory["last_code"] and memory["last_code"].is_type(
                        "binary_operator",
                        "comparison_operator",
                    ):
                        # Evaluate whitespace AFTER the operator
                        anchor, fixes = _handle_previous_segments(
                            memory["since_code"],
                            anchor=memory["last_code"],
                            this_segment=segment,
                            fixes=fixes,
                        )
                        if anchor:
                            description = "Operators should be followed by a space."
                    else:
                        # This isn't an operator, and the thing before it wasn't
                        # either. I don't think that's an issue for now.
                        pass
                # Prepare memory for later
                memory["last_code"] = segment
                memory["since_code"] = []
            else:
                # This isn't a code segment...
                # Prepare memory for later
                memory["since_code"].append(segment)
        else:
            # Reset the memory if we're not in an expression
            memory = {"last_code": None, "since_code": []}

        # Anchor is our signal as to whether there's a problem
        if anchor:
            return LintResult(
                anchor=anchor, memory=memory, fixes=fixes, description=description
            )
        else:
            return LintResult(memory=memory)


@std_rule_set.register
class Rule_L007(BaseCrawler):
    """Operators near newlines should be after, not before the newline.

    | **Anti-pattern**
    | The • character represents a space.
    | In this example, the operator '+' should not be at the end of the second line.

    .. code-block:: sql

        SELECT
            a +
            b
        FROM foo


    | **Best practice**
    | Place the operator after the newline.

    .. code-block:: sql

        SELECT
            a
            + b
        FROM foo
    """

    def _eval(self, segment, memory, parent_stack, **kwargs):
        """Operators near newlines should be after, not before the newline.

        We use the memory to keep track of whitespace up to now, and
        whether the last code segment was an operator or not.
        Anchor is our signal as to whether there's a problem.

        We only trigger if we have an operator FOLLOWED BY a newline
        before the next meaningful code segment.

        """
        anchor = None

        # The parent stack tells us whether we're in an expression or not.
        if parent_stack and parent_stack[-1].is_type("expression"):
            if segment.is_code:
                # This is code, what kind?
                if segment.is_type("binary_operator", "comparison_operator"):
                    # We only trigger if the last was an operator, not if this is.
                    pass
                elif memory["last_code"] and memory["last_code"].is_type(
                    "binary_operator",
                    "comparison_operator",
                ):
                    # It's not an operator, but the last code was. Now check to see
                    # there is a newline between us and the last operator.
                    for s in memory["since_code"]:
                        if s.name == "newline":
                            anchor = memory["last_code"]
                            # TODO: Work out a nice fix for this.
                # Prepare memory for later
                memory["last_code"] = segment
                memory["since_code"] = []
            else:
                # This isn't a code segment...
                # Prepare memory for later
                memory["since_code"].append(segment)
        else:
            # Reset the memory if we're not in an expression
            memory = {"last_code": None, "since_code": []}

        # Anchor is our signal as to whether there's a problem
        if anchor:
            return LintResult(anchor=anchor, memory=memory)
        else:
            return LintResult(memory=memory)


@std_rule_set.document_fix_compatible
@std_rule_set.register
class Rule_L008(BaseCrawler):
    """Commas should be followed by a single whitespace unless followed by a comment.

    | **Anti-pattern**
    | The • character represents a space.
    | In this example, there is no space between the comma and 'zoo'.

    .. code-block::

        SELECT
            *
        FROM foo
        WHERE a IN ('plop','zoo')

    | **Best practice**
    | Keep a single space after the comma.

    .. code-block::

        SELECT
            *
        FROM foo
        WHERE a IN ('plop',•'zoo')
    """

    def _eval(self, segment, raw_stack, **kwargs):
        """Commas should be followed by a single whitespace unless followed by a comment.

        This is a slightly odd one, because we'll almost always evaluate from a point a few places
        after the problem site. NB: We need at least two segments behind us for this to work.
        """
        if len(raw_stack) < 2:
            return None

        cm1 = raw_stack[-1]
        cm2 = raw_stack[-2]
        if cm2.name == "comma":
            # comma followed by something that isn't whitespace?
            if cm1.name not in ["whitespace", "newline"]:
                ins = self.make_whitespace(raw=" ", pos_marker=cm1.pos_marker)
                return LintResult(anchor=cm1, fixes=[LintFix("create", cm1, ins)])
            # comma followed by too much whitespace?
            if (cm1.raw != " " and cm1.name != "newline") and not segment.is_comment:
                repl = cm1.__class__(raw=" ", pos_marker=cm1.pos_marker)
                return LintResult(anchor=cm1, fixes=[LintFix("edit", cm1, repl)])
        # Otherwise we're fine
        return None


@std_rule_set.document_fix_compatible
@std_rule_set.register
class Rule_L009(BaseCrawler):
    """Files must end with a trailing newline."""

    def _eval(self, segment, siblings_post, parent_stack, **kwargs):
        """Files must end with a trailing newline.

        We only care about the segment and the siblings which come after it
        for this rule, we discard the others into the kwargs argument.

        """
        if len(self.filter_meta(siblings_post)) > 0:
            # This can only fail on the last segment
            return None
        elif len(segment.segments) > 0:
            # This can only fail on the last base segment
            return None
        elif segment.name == "newline":
            # If this is the last segment, and it's a newline then we're good
            return None
        elif segment.is_meta:
            # We can't fail on a meta segment
            return None
        else:
            # so this looks like the end of the file, but we
            # need to check that each parent segment is also the last
            file_len = len(parent_stack[0].raw)
            pos = segment.pos_marker.char_pos
            # Does the length of the file, equal the length of the segment plus it's position
            if file_len != pos + len(segment.raw):
                return None

        ins = self.make_newline(pos_marker=segment.pos_marker.advance_by(segment.raw))
        # We're going to make an edit because otherwise we would never get a match!
        return LintResult(
            anchor=segment, fixes=[LintFix("edit", segment, [segment, ins])]
        )


@std_rule_set.document_fix_compatible
@std_rule_set.document_configuration
@std_rule_set.register
class Rule_L010(BaseCrawler):
    """Inconsistent capitalisation of keywords.

    | **Anti-pattern**
    | In this example, 'select 'is in lower-case whereas 'FROM' is in upper-case.

    .. code-block:: sql

        select
            a
        FROM foo

    | **Best practice**
    | Make all keywords either in upper-case or in lower-case

    .. code-block:: sql

        SELECT
            a
        FROM foo

        -- Also good

        select
            a
        from foo
    """

    # Binary operators behave like keywords too.
    _target_elems: List[Tuple[str, str]] = [
        ("type", "keyword"),
        ("type", "binary_operator"),
    ]
    config_keywords = ["capitalisation_policy"]

    def _eval(self, segment, memory, **kwargs):
        """Inconsistent capitalisation of keywords.

        We use the `memory` feature here to keep track of
        what we've seen in the past.

        """
        cases_seen = memory.get("cases_seen", set())

        if ("type", segment.type) in self._target_elems or (
            "name",
            segment.name,
        ) in self._target_elems:
            raw = segment.raw
            uc = raw.upper()
            lc = raw.lower()
            cap = raw.capitalize()
            seen_case = None
            if uc == lc:
                # Caseless
                pass
            elif raw == uc:
                seen_case = "upper"
            elif raw == lc:
                seen_case = "lower"
            elif raw == cap:
                seen_case = "capitalise"
            else:
                seen_case = "inconsistent"

            # NOTE: We'll only add to cases_seen if we DONT
            # also raise an error, so that we can focus in.

            def make_replacement(seg, policy):
                """Make a replacement segment, based on seen capitalisation."""
                if policy == "lower":
                    new_raw = seg.raw.lower()
                elif policy == "upper":
                    new_raw = seg.raw.upper()
                elif policy == "capitalise":
                    new_raw = seg.raw.capitalize()
                elif policy == "consistent":
                    # The only case we DONT allow here is "inconsistent",
                    # because it doesn't actually help us.
                    filtered_cases_seen = [c for c in cases_seen if c != "inconsistent"]
                    if filtered_cases_seen:
                        # Get an element from what we've already seen.
                        return make_replacement(seg, list(filtered_cases_seen)[0])
                    else:
                        # If we haven't seen anything yet, then let's default
                        # to upper
                        return make_replacement(seg, "upper")
                # Make a new class and return it.
                return seg.__class__(raw=new_raw, pos_marker=seg.pos_marker)

            if not seen_case:
                # Skip this if we haven't seen anything good.
                # No need to update memory
                return LintResult(memory=memory)
            elif (
                # Are we required to be consistent? (and this is inconsistent?)
                (
                    self.capitalisation_policy == "consistent"
                    and (
                        # Either because we've seen multiple
                        (cases_seen and seen_case not in cases_seen)
                        # Or just because this one is inconsistent internally
                        or seen_case == "inconsistent"
                    )
                )
                # Are we just required to be specfic?
                # Policy is either upper, lower or capitalize
                or (
                    self.capitalisation_policy != "consistent"
                    and seen_case != self.capitalisation_policy
                )
            ):
                return LintResult(
                    anchor=segment,
                    fixes=[
                        LintFix(
                            "edit",
                            segment,
                            make_replacement(segment, self.capitalisation_policy),
                        )
                    ],
                    memory=memory,
                )
            else:
                # Update memory and carry on
                cases_seen.add(seen_case)
                memory["cases_seen"] = cases_seen
                return LintResult(memory=memory)

        # If it's not a keyword just carry on
        return LintResult(memory=memory)


@std_rule_set.document_fix_compatible
@std_rule_set.register
class Rule_L011(BaseCrawler):
    """Implicit aliasing of table not allowed. Use explicit `AS` clause.

    | **Anti-pattern**
    | In this example, the alias 'voo' is implicit.

    .. code-block:: sql

        SELECT
            voo.a
        FROM foo voo

    | **Best practice**
    | Add `AS` to make it explicit.

    .. code-block:: sql

        SELECT
            voo.a
        FROM foo AS voo

    """

    _target_elems = ("table_expression",)

    def _eval(self, segment, parent_stack, raw_stack, **kwargs):
        """Implicit aliasing of table/column not allowed. Use explicit `AS` clause.

        We look for the alias segment, and then evaluate its parent and whether
        it contains an AS keyword. This is the _eval function for both L011 and L012.

        The use of `raw_stack` is just for working out how much whitespace to add.

        """
        if segment.is_type("alias_expression"):
            if parent_stack[-1].is_type(*self._target_elems):
                if not any(e.name.lower() == "as" for e in segment.segments):
                    insert_buff = []
                    insert_str = ""
                    init_pos = segment.segments[0].pos_marker

                    # Add intial whitespace if we need to...
                    if raw_stack[-1].name not in ["whitespace", "newline"]:
                        insert_buff.append(
                            self.make_whitespace(raw=" ", pos_marker=init_pos)
                        )
                        insert_str += " "

                    # Add an AS (Uppercase for now, but could be corrected later)
                    insert_buff.append(
                        self.make_keyword(
                            raw="AS", pos_marker=init_pos.advance_by(insert_str)
                        )
                    )
                    insert_str += "AS"

                    # Add a trailing whitespace if we need to
                    if segment.segments[0].name not in ["whitespace", "newline"]:
                        insert_buff.append(
                            self.make_whitespace(
                                raw=" ", pos_marker=init_pos.advance_by(insert_str)
                            )
                        )
                        insert_str += " "

                    return LintResult(
                        anchor=segment,
                        fixes=[LintFix("create", segment.segments[0], insert_buff)],
                    )
        return None


@std_rule_set.register
class Rule_L012(Rule_L011):
    """Implicit aliasing of column not allowed. Use explicit `AS` clause.

    NB: This rule inherits its functionality from obj:`Rule_L011` but is
    seperate so that they can be enabled and disabled seperately.

    """

    _target_elems = ("select_target_element",)


@std_rule_set.document_configuration
@std_rule_set.register
class Rule_L013(BaseCrawler):
    """Column expression without alias. Use explicit `AS` clause.

    | **Anti-pattern**
    | In this example, there is no alias for both sums.

    .. code-block:: sql

        SELECT
            sum(a),
            sum(b)
        FROM foo

    | **Best practice**
    | Add aliases.

    .. code-block:: sql

        SELECT
            sum(a) AS a_sum,
            sum(b) AS b_sum
        FROM foo

    """

    config_keywords = ["allow_scalar"]

    def _eval(self, segment, parent_stack, **kwargs):
        """Column expression without alias. Use explicit `AS` clause.

        We look for the select_target_element segment, and then evaluate
        whether it has an alias segment or not and whether the expression
        is complicated enough. `parent_stack` is to assess how many other
        elements there are.

        """
        if segment.is_type("select_target_element"):
            if not any(e.is_type("alias_expression") for e in segment.segments):
                types = {e.type for e in segment.segments if e.name != "star"}
                unallowed_types = types - {
                    "whitespace",
                    "newline",
                    "column_reference",
                    "wildcard_expression",
                }
                if len(unallowed_types) > 0:
                    # No fixes, because we don't know what the alias should be,
                    # the user should document it themselves.
                    if self.allow_scalar:
                        # Check *how many* elements there are in the select
                        # statement. If this is the only one, then we won't
                        # report an error.
                        num_elements = sum(
                            e.is_type("select_target_element")
                            for e in parent_stack[-1].segments
                        )
                        if num_elements > 1:
                            return LintResult(anchor=segment)
                        else:
                            return None
                    else:
                        # Just error if we don't care.
                        return LintResult(anchor=segment)
        return None


@std_rule_set.document_configuration
@std_rule_set.register
class Rule_L014(Rule_L010):
    """Inconsistent capitalisation of unquoted identifiers.

    The functionality for this rule is inherited from :obj:`Rule_L010`.
    """

    _target_elems: List[Tuple[str, str]] = [("name", "naked_identifier")]


@std_rule_set.register
class Rule_L015(BaseCrawler):
    """DISTINCT used with parentheses.

    | **Anti-pattern**
    | In this example, parenthesis are not needed and confuse
    | DISTINCT with a function. The parethesis can also be misleading
    | in which columns they apply to.

    .. code-block:: sql

        SELECT DISTINCT(a), b FROM foo

    | **Best practice**
    | Remove parenthesis to be clear that the DISTINCT applies to
    | both columns.

    .. code-block:: sql

        SELECT DISTINCT a, b FROM foo

    """

    def _eval(self, segment, raw_stack, **kwargs):
        """Looking for DISTINCT before a bracket.

        Look for DISTINCT keyword immediately followed by open parenthesis.
        """
        # We only trigger on start_bracket (open parenthesis)
        if segment.name == "start_bracket":
            filt_raw_stack = self.filter_meta(raw_stack)
            if len(filt_raw_stack) > 0 and filt_raw_stack[-1].name == "DISTINCT":
                # If we find DISTINCT followed by open_bracket, then bad.
                return LintResult(anchor=segment)
        return LintResult()


@std_rule_set.document_fix_compatible
@std_rule_set.document_configuration
@std_rule_set.register
class Rule_L016(Rule_L003):
    """Line is too long."""

    config_keywords = ["max_line_length", "tab_space_size", "indent_unit"]

    def _eval_line_for_breaks(self, segments):
        """Evaluate the line for break points.

        We split the line into a few particular sections:
        - The indent (all the whitespace up to this point)
        - Content (which doesn't have whitespace at the start or end)
        - Breakpoint (which contains Indent/Dedent and potential
          whitespace). NB: If multiple indent/dedent sections share
          a breakpoint, then they will occupy the SAME one, so that
          dealing with whitespace post-split is easier.
        - Pausepoint (which is a comma, potentially surrounded by
          whitespace). This is for potential list splitting.

        Once split, we'll use a seperate method to work out what
        combinations make most sense for reflow.
        """
        chunk_buff = []
        indent_section = None

        class Section:
            def __init__(self, segments, role, indent_balance, indent_impulse=0):
                self.segments = segments
                self.role = role
                self.indent_balance = indent_balance
                self.indent_impulse = indent_impulse

            def __repr__(self):
                return "<Section @ {pos}: {role} [{indent_balance}:{indent_impulse}]. {segments!r}>".format(
                    role=self.role,
                    indent_balance=self.indent_balance,
                    indent_impulse=self.indent_impulse,
                    segments="".join(elem.raw for elem in self.segments),
                    pos=self.segments[0].get_start_pos_marker(),
                )

            @property
            def raw(self):
                return "".join(seg.raw for seg in self.segments)

            @staticmethod
            def find_segment_at(segments, pos):
                highest_pos = None
                for seg in segments:
                    if highest_pos is None or seg.pos_marker > highest_pos:
                        highest_pos = seg.pos_marker
                    if not seg.is_meta and seg.pos_marker == pos:
                        return seg

            def generate_fixes_to_coerce(
                self, segments, indent_section, crawler, indent
            ):
                """Generate a list of fixes to create a break at this point.

                The `segments` argument is necessary to extract anchors
                from the existing segments.
                """
                fixes = []

                # Generate some sample indents:
                unit_indent = crawler._make_indent()
                indent_p1 = indent_section.raw + unit_indent
                if unit_indent in indent_section.raw:
                    indent_m1 = indent_section.raw.replace(unit_indent, "", 1)
                else:
                    indent_m1 = indent_section.raw

                if indent > 0:
                    new_indent = indent_p1
                elif indent < 0:
                    new_indent = indent_m1
                else:
                    new_indent = indent_section.raw

                create_anchor = self.find_segment_at(
                    segments, self.segments[-1].get_end_pos_marker()
                )

                if self.role == "pausepoint":
                    # Assume that this means there isn't a breakpoint
                    # and that we'll break with the same indent as the
                    # existing line.

                    # NOTE: Deal with commas and binary operators differently here.
                    # Maybe only deal with commas to start with?
                    if any(seg.is_type("binary_operator") for seg in self.segments):
                        raise NotImplementedError(
                            "Don't know how to deal with binary operators here yet!!"
                        )

                    # Remove any existing whitespace
                    for elem in self.segments:
                        if not elem.is_meta and elem.is_type("whitespace"):
                            fixes.append(LintFix("delete", elem))

                    # Create a newline and a similar indent
                    fixes.append(
                        LintFix(
                            "create",
                            create_anchor,
                            [
                                crawler.make_newline(create_anchor.pos_marker),
                                crawler.make_whitespace(
                                    new_indent, create_anchor.pos_marker
                                ),
                            ],
                        )
                    )
                    return fixes

                if self.role == "breakpoint":
                    # Can we determine the required indent just from
                    # the info in this segment only?

                    # Remove anything which is already here
                    for elem in self.segments:
                        if not elem.is_meta:
                            fixes.append(LintFix("delete", elem))
                    # Create a newline, create an indent of the relevant size
                    fixes.append(
                        LintFix(
                            "create",
                            create_anchor,
                            [
                                crawler.make_newline(create_anchor.pos_marker),
                                crawler.make_whitespace(
                                    new_indent, create_anchor.pos_marker
                                ),
                            ],
                        )
                    )
                    return fixes
                raise ValueError("Unexpected break generated at {0}".format(self))

        segment_buff = ()
        whitespace_buff = ()
        indent_impulse = 0
        indent_balance = 0
        is_pause = False

        for seg in segments:
            if indent_section is None:
                if seg.is_type("whitespace") or seg.is_meta:
                    whitespace_buff += (seg,)
                else:
                    indent_section = Section(
                        segments=whitespace_buff,
                        role="indent",
                        indent_balance=indent_balance,
                    )
                    whitespace_buff = ()
                    segment_buff = (seg,)
            else:
                if seg.is_type("whitespace") or seg.is_meta:
                    whitespace_buff += (seg,)
                    if seg.is_meta:
                        indent_impulse += seg.indent_val
                else:
                    # We got something other than whitespace or a meta.
                    # Have we passed an indent?
                    if indent_impulse != 0:
                        # Yes. Bank the section, perhaps also with a content
                        # section.
                        if segment_buff:
                            chunk_buff.append(
                                Section(
                                    segments=segment_buff,
                                    role="content",
                                    indent_balance=indent_balance,
                                )
                            )
                            segment_buff = ()
                        # Deal with the whitespace
                        chunk_buff.append(
                            Section(
                                segments=whitespace_buff,
                                role="breakpoint",
                                indent_balance=indent_balance,
                                indent_impulse=indent_impulse,
                            )
                        )
                        whitespace_buff = ()
                        indent_balance += indent_impulse
                        indent_impulse = 0

                    # Did we think we were in a pause?
                    # TODO: Renable binary operator breaks some time in future.
                    if is_pause:
                        # We need to end the comma/operator
                        # (taking any whitespace with it).
                        chunk_buff.append(
                            Section(
                                segments=segment_buff + whitespace_buff,
                                role="pausepoint",
                                indent_balance=indent_balance,
                            )
                        )
                        # Start the segment buffer off with this section.
                        whitespace_buff = ()
                        segment_buff = (seg,)
                        is_pause = False
                    else:
                        # We're not in a pause (or not in a pause yet)
                        if seg.name == "comma":  # or seg.is_type('binary_operator')
                            if segment_buff:
                                # End the previous section, start a comma/operator.
                                # Any whitespace is added to the segment
                                # buff to go with the comma.
                                chunk_buff.append(
                                    Section(
                                        segments=segment_buff,
                                        role="content",
                                        indent_balance=indent_balance,
                                    )
                                )
                                segment_buff = ()

                            # Having a double comma should be impossible
                            # but let's deal with that case regardless.
                            segment_buff += whitespace_buff + (seg,)
                            whitespace_buff = ()
                            is_pause = True
                        else:
                            # Not in a pause, it's not a comma, were in
                            # some content.
                            segment_buff += whitespace_buff + (seg,)
                            whitespace_buff = ()

        # We're at the end, do we have anything left?
        if is_pause:
            role = "pausepoint"
        elif segment_buff:
            role = "content"
        elif indent_impulse:
            role = "breakpoint"
        else:
            raise ValueError("Is this possible?")

        chunk_buff.append(
            Section(
                segments=segment_buff + whitespace_buff,
                role=role,
                indent_balance=indent_balance,
            )
        )

        self.logger.info("Sections:")
        for idx, sec in enumerate(chunk_buff):
            self.logger.info("    {0}: {1!r}".format(idx, sec))

        # How do we prioritise where to work?
        # First, do we ever go through a negative breakpoint?
        lowest_bal = min(sec.indent_balance for sec in chunk_buff)
        split_at = []  # split_at is probably going to be a list.
        fixes = []
        if lowest_bal < 0:
            for sec in chunk_buff:
                if sec.indent_balance == 0 and sec.indent_impulse < 0:
                    split_at = [(sec, -1)]
                    break
        # Assuming we never go negative, we'll either use a pause
        # point in the base indent balance, or we'll split out
        # a section or two using the lowest breakpoints.
        else:
            # Look for low level pauses. Additionally, ignore
            # them if they're a comma at the end of the line,
            # they're useless for splitting
            pauses = [
                sec
                for sec in chunk_buff
                if sec.role == "pausepoint" and sec.indent_balance == 0
                # Not the last chunk
                and sec is not chunk_buff[-1]
            ]
            if any(pauses):
                split_at = [(pause, 0) for pause in pauses]
            else:
                # No pauses and no negatives. We should extract
                # a subsection using the breakpoints.

                # We'll definitely have an up. It's possible that the *down*
                # might not be on this line, so we have to allow for that case.
                upbreaks = [
                    sec
                    for sec in chunk_buff
                    if sec.role == "breakpoint"
                    and sec.indent_balance == 0
                    and sec.indent_impulse > 0
                ]
                if not upbreaks:
                    # No upbreaks?!
                    # abort
                    return []
                # First up break
                split_at = [(upbreaks[0], 1)]
                downbreaks = [
                    sec
                    for sec in chunk_buff
                    if sec.role == "breakpoint"
                    and sec.indent_balance + sec.indent_impulse == 0
                    and sec.indent_impulse < 0
                ]
                # First down break where we reach the base
                if downbreaks:
                    split_at.append((downbreaks[0], 0))
                # If no downbreaks then the corresponding downbreak isn't on this line.

        self.logger.info("Split at: %s", split_at)

        fixes = []
        for split, indent in split_at:
            fixes += split.generate_fixes_to_coerce(
                segments, indent_section, self, indent
            )

        self.logger.info("Fixes: %s", fixes)

        return fixes

    @staticmethod
    def _gen_line_so_far(raw_stack, initial_buff=None):
        """Work out from the raw stack what the elements on this line are.

        Returns:
            :obj:`list` of segments

        """
        working_buff = initial_buff or []
        idx = -1
        while True:
            if len(raw_stack) >= abs(idx):
                s = raw_stack[idx]
                if s.name == "newline":
                    break
                else:
                    working_buff.insert(0, s)
                    idx -= 1
            else:
                break
        return working_buff

    def _eval(self, segment, raw_stack, **kwargs):
        """Line is too long.

        This only triggers on newline segments, evaluating the whole line.
        The detection is simple, the fixing is much trickier.

        """
        if segment.name == "newline":
            # iterate to buffer the whole line up to this point
            this_line = self._gen_line_so_far(raw_stack, [])
        else:
            # Otherwise we're all good
            return None

        # Now we can work out the line length and deal with the content
        line_len = sum(len(s.raw) for s in this_line)
        if line_len > self.max_line_length:
            # Problem, we'll be reporting a violation. The
            # question is, can we fix it?

            # We'll need the indent, so let's get it for fixing.
            line_indent = []
            idx = 0
            for s in this_line:
                if s.name == "whitespace":
                    line_indent.append(s)
                else:
                    break

            # Does the line end in an inline comment that we can move back?
            if this_line[-1].name == "inline_comment":
                # Is this line JUST COMMENT (with optional predeeding whitespace) if
                # so, user will have to fix themselves.
                if len(this_line) == 1 or all(
                    elem.name == "whitespace" or elem.is_meta for elem in this_line[:-1]
                ):
                    self.logger.info(
                        "Unfixable inline comment, alone on line: %s", this_line[-1]
                    )
                    return LintResult(anchor=segment)

                self.logger.info(
                    "Attempting move of inline comment at end of line: %s",
                    this_line[-1],
                )
                # Set up to delete the original comment and the preceeding whitespace
                delete_buffer = [LintFix("delete", this_line[-1])]
                idx = -2
                while True:
                    if (
                        len(this_line) >= abs(idx)
                        and this_line[idx].name == "whitespace"
                    ):
                        delete_buffer.append(LintFix("delete", this_line[idx]))
                        idx -= 1
                    else:
                        break
                # Create a newline before this one with the existing comment, an
                # identical indent AND a terminating newline, copied from the current
                # target segment.
                create_buffer = [
                    LintFix(
                        "create", this_line[0], line_indent + [this_line[-1], segment]
                    )
                ]
                return LintResult(anchor=segment, fixes=delete_buffer + create_buffer)

            fixes = self._eval_line_for_breaks(this_line)
            if fixes:
                return LintResult(anchor=segment, fixes=fixes)
            return LintResult(anchor=segment)


@std_rule_set.document_fix_compatible
@std_rule_set.register
class Rule_L017(BaseCrawler):
    """Function name not immediately followed by bracket.

    | **Anti-pattern**
    | In this example, there is a space between the function and the parenthesis.

    .. code-block:: sql

        SELECT
            sum (a)
        FROM foo

    | **Best practice**
    | Remove the space between the function and the parenthesis.

    .. code-block:: sql

        SELECT
            sum(a)
        FROM foo

    """

    def _eval(self, segment, **kwargs):
        """Function name not immediately followed by bracket.

        Look for Function Segment with anything other than the
        function name before brackets
        """
        # We only trigger on start_bracket (open parenthesis)
        if segment.is_type("function"):
            # Look for the function name
            for fname_idx, seg in enumerate(segment.segments):
                if seg.is_type("function_name"):
                    break

            # Look for the start bracket
            for bracket_idx, seg in enumerate(segment.segments):
                if seg.name == "start_bracket":
                    break

            if bracket_idx != fname_idx + 1:
                return LintResult(
                    anchor=segment.segments[fname_idx + 1],
                    fixes=[
                        LintFix("delete", segment.segments[idx])
                        for idx in range(fname_idx + 1, bracket_idx)
                    ],
                )
        return LintResult()


@std_rule_set.document_fix_compatible
@std_rule_set.register
class Rule_L018(BaseCrawler):
    """WITH clause closing bracket should be aligned with WITH keyword.

    | **Anti-pattern**
    | The • character represents a space.
    | In this example, the closing bracket is not aligned with WITH keyword.

    .. code-block::

        WITH zoo AS (
            SELECT a FROM foo
        ••••)

        SELECT * FROM zoo

    | **Best practice**
    | Remove the spaces to align the WITH keyword with the closing bracket.

    .. code-block::

        WITH zoo AS (
            SELECT a FROM foo
        )

        SELECT * FROM zoo

    """

    _works_on_unparsable = False
    config_keywords = ["tab_space_size"]

    def _eval(self, segment, raw_stack, **kwargs):
        """WITH clause closing bracket should be aligned with WITH keyword.

        Look for a with clause and evaluate the position of closing brackets.
        """
        # We only trigger on start_bracket (open parenthesis)
        if segment.is_type("with_compound_statement"):
            raw_stack_buff = list(raw_stack)
            # Look for the with keyword
            for seg in segment.segments:
                if seg.name.lower() == "with":
                    seg_line_no = seg.pos_marker.line_no
                    break
            else:
                # This *could* happen if the with statement is unparsable,
                # in which case then the user will have to fix that first.
                if any(s.is_type("unparsable") for s in segment.segments):
                    return LintResult()
                # If it's parsable but we still didn't find a with, then
                # we should raise that.
                raise RuntimeError("Didn't find WITH keyword!")

            def indent_size_up_to(segs):
                seg_buff = []
                # Get any segments running up to the WITH
                for elem in reversed(segs):
                    if elem.is_type("newline"):
                        break
                    elif elem.is_meta:
                        continue
                    else:
                        seg_buff.append(elem)
                # reverse the indent if we have one
                if seg_buff:
                    seg_buff = list(reversed(seg_buff))
                indent_str = "".join(seg.raw for seg in seg_buff).replace(
                    "\t", " " * self.tab_space_size
                )
                indent_size = len(indent_str)
                return indent_size, indent_str

            balance = 0
            with_indent, with_indent_str = indent_size_up_to(raw_stack_buff)
            for seg in segment.segments:
                if seg.name == "start_bracket":
                    balance += 1
                elif seg.name == "end_bracket":
                    balance -= 1
                    if balance == 0:
                        closing_bracket_indent, _ = indent_size_up_to(raw_stack_buff)
                        indent_diff = closing_bracket_indent - with_indent
                        # Is indent of closing bracket not the same as
                        # indent of WITH keyword.
                        if seg.pos_marker.line_no == seg_line_no:
                            # Skip if it's the one-line version. That's ok
                            pass
                        elif indent_diff < 0:
                            return LintResult(
                                anchor=seg,
                                fixes=[
                                    LintFix(
                                        "create",
                                        seg,
                                        self.make_whitespace(
                                            " " * (-indent_diff), seg.pos_marker
                                        ),
                                    )
                                ],
                            )
                        elif indent_diff > 0:
                            # Is it all whitespace before the bracket on this line?
                            prev_segs_on_line = [
                                elem
                                for elem in segment.segments
                                if elem.pos_marker.line_no == seg.pos_marker.line_no
                                and elem.pos_marker.line_pos < seg.pos_marker.line_pos
                            ]
                            if all(
                                elem.is_type("whitespace") for elem in prev_segs_on_line
                            ):
                                # We can move it back, it's all whitespace
                                fixes = [
                                    LintFix(
                                        "create",
                                        seg,
                                        [
                                            self.make_whitespace(
                                                with_indent_str,
                                                seg.pos_marker.advance_by("\n"),
                                            )
                                        ],
                                    )
                                ] + [
                                    LintFix("delete", elem)
                                    for elem in prev_segs_on_line
                                ]
                            else:
                                # We have to move it to a newline
                                fixes = [
                                    LintFix(
                                        "create",
                                        seg,
                                        [
                                            self.make_newline(
                                                pos_marker=seg.pos_marker
                                            ),
                                            self.make_whitespace(
                                                with_indent_str,
                                                seg.pos_marker.advance_by("\n"),
                                            ),
                                        ],
                                    )
                                ]
                            return LintResult(anchor=seg, fixes=fixes)
                else:
                    raw_stack_buff.append(seg)
        return LintResult()


@std_rule_set.document_fix_compatible
@std_rule_set.document_configuration
@std_rule_set.register
class Rule_L019(BaseCrawler):
    """Leading/Trailing comma enforcement.

    | **Anti-pattern**
    | There is a mixture of leading and trailing commas.

    .. code-block:: sql

        SELECT
            a
            , b,
            c
        FROM foo

    | **Best practice**
    | By default sqlfluff prefers trailing commas, however it
    | is configurable for leading commas. Whichever option you chose
    | it does expect you to be consistent.

    .. code-block:: sql

        SELECT
            a,
            b,
            c
        FROM foo

        -- Alternatively, set the configuration file to 'leading'
        -- and then the following would be acceptable:

        SELECT
            a
            , b
            , c
        FROM foo


    """

    config_keywords = ["comma_style"]

    @staticmethod
    def _last_code_seg(raw_stack, idx=-1):
        while True:
            if raw_stack[idx].is_code or raw_stack[idx].is_type("newline"):
                return raw_stack[idx]
            idx -= 1

    def _eval(self, segment, raw_stack, memory, **kwargs):
        """Enforce comma placement.

        For leading commas we're looking for trailing commas, so
        we look for newline segments. For trailing commas we're
        looking for leading commas, so we look for the comma itself.

        We also want to handle proper whitespace removal/addition. We remove
        any trailing whitespace after the leading comma, when converting a
        leading comma to a trailing comma. We add whitespace after the leading
        comma when converting a trailing comma to a leading comma.
        """
        if not memory:
            memory: Dict[str, Any] = {
                # Trailing comma keys
                #
                # Do we have a fix in place for removing a leading
                # comma violation, and inserting a new trailing comma?
                "insert_trailing_comma": False,
                # A list of whitespace segments that come after a
                # leading comma violation, to be removed during fixing.
                "whitespace_deletions": None,
                # The leading comma violation segment to be removed during fixing
                "last_leading_comma_seg": None,
                # The newline segment where we're going to insert our new trailing
                # comma during fixing
                "anchor_for_new_trailing_comma_seg": None,
                #
                # Leading comma keys
                #
                # Do we have a fix in place for removing a trailing
                # comma violation, and inserting a new leading comma?
                "insert_leading_comma": False,
                # The trailing comma violation segment to be removed during fixing
                "last_trailing_comma_segment": None,
            }

        if self.comma_style == "trailing":
            # A comma preceded by a new line == a leading comma
            if segment.is_type("comma"):
                last_seg = self._last_code_seg(raw_stack)
                if last_seg.is_type("newline"):
                    # Recorded where the fix should be applied
                    memory["last_leading_comma_seg"] = segment
                    memory["anchor_for_new_trailing_comma_seg"] = last_seg
                    # Trigger fix routine
                    memory["insert_trailing_comma"] = True
                    memory["whitespace_deletions"] = []
                    return LintResult(memory=memory)
            # Have we found a leading comma violation?
            if memory["insert_trailing_comma"]:
                # Search for trailing whitespace to delete after the leading
                # comma violation
                if segment.is_type("whitespace"):
                    memory["whitespace_deletions"] += [segment]
                    return LintResult(memory=memory)
                else:
                    # We've run out of whitespace to delete, time to fix
                    last_leading_comma_seg = memory["last_leading_comma_seg"]
                    return LintResult(
                        anchor=last_leading_comma_seg,
                        description="Found leading comma. Expected only trailing.",
                        fixes=[
                            LintFix("delete", last_leading_comma_seg),
                            *[
                                LintFix("delete", d)
                                for d in memory["whitespace_deletions"]
                            ],
                            LintFix(
                                "create",
                                anchor=memory["anchor_for_new_trailing_comma_seg"],
                                # Reuse the previous leading comma violation to
                                # create a new trailing comma
                                edit=last_leading_comma_seg,
                            ),
                        ],
                    )

        elif self.comma_style == "leading":
            # A new line preceded by a comma == a trailing comma
            if segment.is_type("newline"):
                last_seg = self._last_code_seg(raw_stack)
                if last_seg.is_type("comma"):
                    # Trigger fix routine
                    memory["insert_leading_comma"] = True
                    # Record where the fix should be applied
                    memory["last_trailing_comma_segment"] = last_seg
                    return LintResult(memory=memory)
            # Have we found a trailing comma violation?
            if memory["insert_leading_comma"]:
                # Only insert the comma here if this isn't a comment/whitespace segment
                if segment.is_code:
                    last_comma_seg = memory["last_trailing_comma_segment"]
                    # Create whitespace to insert after the new leading comma
                    new_whitespace_seg = self.make_whitespace(
                        raw=" ", pos_marker=segment.pos_marker.advance_by(" ")
                    )
                    return LintResult(
                        anchor=last_comma_seg,
                        description="Found trailing comma. Expected only leading.",
                        fixes=[
                            LintFix("delete", anchor=last_comma_seg),
                            LintFix(
                                "edit",
                                anchor=segment,
                                edit=[last_comma_seg, new_whitespace_seg, segment],
                            ),
                        ],
                    )
        # Otherwise, no issue
        return None


@std_rule_set.register
class Rule_L020(BaseCrawler):
    """Table aliases should be unique within each clause."""

    def _lint_references_and_aliases(
        self, aliases, references, col_aliases, using_cols, parent_select
    ):
        """Check whether any aliases are duplicates.

        NB: Subclasses of this error should override this function.

        """
        # Are any of the aliases the same?
        for a1, a2 in itertools.combinations(aliases, 2):
            # Compare the strings
            if a1[0] == a2[0] and a1[0]:
                # If there are any, then the rest of the code
                # won't make sense so just return here.
                return [
                    LintResult(
                        # Reference the element, not the string.
                        anchor=a2[1],
                        description=(
                            "Duplicate table alias {0!r}. Table "
                            "aliases should be unique."
                        ).format(a2[0]),
                    )
                ]
        return None

    @staticmethod
    def _get_aliases_from_select(segment):
        # Get the aliases referred to in the clause
        fc = segment.get_child("from_clause")
        if not fc:
            # If there's no from clause then just abort.
            return None
        return fc.get_eventual_aliases()

    def _eval(self, segment, parent_stack, **kwargs):
        """Get References and Aliases and allow linting.

        This rule covers a lot of potential cases of odd usages of
        references, see the code for each of the potential cases.

        Subclasses of this rule should override the
        `_lint_references_and_aliases` method.
        """
        if segment.is_type("select_statement"):
            aliases = self._get_aliases_from_select(segment)
            if not aliases:
                return None

            # Iterate through all the references, both in the select clause, but also
            # potential others.
            sc = segment.get_child("select_clause")
            reference_buffer = list(sc.recursive_crawl("object_reference"))
            # Add any wildcard references
            reference_buffer += list(sc.recursive_crawl("wildcard_identifier"))
            for potential_clause in (
                "where_clause",
                "groupby_clause",
                "having_clause",
                "orderby_clause",
            ):
                clause = segment.get_child(potential_clause)
                if clause:
                    reference_buffer += list(clause.recursive_crawl("object_reference"))
            # PURGE any references which are in nested select statements
            for ref in reference_buffer.copy():
                ref_path = segment.path_to(ref)
                # is it in a subselect? i.e. a select which isn't this one.
                if any(
                    seg.is_type("select_statement") and seg is not segment
                    for seg in ref_path
                ):
                    reference_buffer.remove(ref)

            # Get all column aliases
            col_aliases = []
            for col_seg in list(sc.recursive_crawl("alias_expression")):
                for seg in col_seg.segments:
                    if seg.is_type("identifier"):
                        col_aliases.append(seg.raw)

            # Get any columns referred to in a using clause, and extract anything
            # from ON clauses.
            using_cols = []
            fc = segment.get_child("from_clause")
            for join_clause in fc.recursive_crawl("join_clause"):
                in_using_brackets = False
                seen_using = False
                seen_on = False
                for seg in join_clause.segments:
                    if seg.is_type("keyword") and seg.name == "USING":
                        seen_using = True
                    elif seg.is_type("keyword") and seg.name == "ON":
                        seen_on = True
                    elif seen_using and seg.is_type("start_bracket"):
                        in_using_brackets = True
                    elif seen_using and seg.is_type("end_bracket"):
                        in_using_brackets = False
                        seen_using = False
                    elif in_using_brackets and seg.is_type("identifier"):
                        using_cols.append(seg.raw)
                    elif seen_on and seg.is_type("expression"):
                        # Deal with expressions
                        reference_buffer += list(
                            seg.recursive_crawl("object_reference")
                        )

            # Work out if we have a parent select function
            parent_select = None
            for seg in reversed(parent_stack):
                if seg.is_type("select_statement"):
                    parent_select = seg
                    break

            # Pass them all to the function that does all the work.
            # NB: Subclasses of this rules should override the function below
            return self._lint_references_and_aliases(
                aliases, reference_buffer, col_aliases, using_cols, parent_select
            )
        return None


@std_rule_set.register
class Rule_L021(BaseCrawler):
    """Ambiguous use of DISTINCT in select statement with GROUP BY.

    | **Anti-pattern**
    | DISTINCT and GROUP BY are conflicting.

    .. code-block:: sql

        SELECT DISTINCT
            a
        FROM foo
        GROUP BY a

    | **Best practice**
    | Remove DISTINCT or GROUP BY. In our case, removing GROUP BY is better.

    .. code-block:: sql

        SELECT DISTINCT
            a
        FROM foo
    """

    def _eval(self, segment, **kwargs):
        """Ambiguous use of DISTINCT in select statement with GROUP BY."""
        if segment.is_type("select_statement"):
            # Do we have a group by clause
            group_clause = segment.get_child("groupby_clause")
            if not group_clause:
                return None

            # Do we have the "DISTINCT" keyword in the select clause
            select_clause = segment.get_child("select_clause")
            select_modifier = select_clause.get_child("select_clause_modifier")
            if not select_modifier:
                return None
            select_keywords = select_modifier.get_children("keyword")
            for kw in select_keywords:
                if kw.name == "DISTINCT":
                    return LintResult(anchor=kw)
        return None


@std_rule_set.document_fix_compatible
@std_rule_set.register
class Rule_L022(BaseCrawler):
    """Blank line expected but not found after CTE definition.

    | **Anti-pattern**
    | There is no blank line after the CTE. In queries with many
    | CTEs this hinders readability.

    .. code-block:: sql

        WITH plop AS (
            SELECT * FROM foo
        )
        SELECT a FROM plop

    | **Best practice**
    | Add a blank line.

    .. code-block:: sql

        WITH plop AS (
            SELECT * FROM foo
        )

        SELECT a FROM plop

    """

    config_keywords = ["comma_style"]

    def _eval(self, segment, **kwargs):
        """Blank line expected but not found after CTE definition."""
        error_buffer = []
        if segment.is_type("with_compound_statement"):
            # First we need to find all the commas, the end brackets, the
            # things that come after that and the blank lines in between.

            # Find all the closing brackets. They are our anchor points.
            bracket_indices = []
            for idx, seg in enumerate(segment.segments):
                if seg.is_type("end_bracket"):
                    bracket_indices.append(idx)

            # Work through each point and deal with it individually
            for bracket_idx in bracket_indices:
                forward_slice = segment.segments[bracket_idx:]
                seg_idx = 1
                line_idx = 0
                comma_seg_idx = None
                blank_lines = 0
                comma_line_idx = None
                line_blank = False
                comma_style = None
                line_starts = {}
                comment_lines = []

                self.logger.info(
                    "## CTE closing bracket found at %s, idx: %s. Forward slice: %.20r",
                    forward_slice[0].pos_marker,
                    bracket_idx,
                    "".join(elem.raw for elem in forward_slice),
                )

                # Work forward to map out the following segments.
                while (
                    forward_slice[seg_idx].is_type("comma")
                    or not forward_slice[seg_idx].is_code
                ):
                    if forward_slice[seg_idx].is_type("newline"):
                        if line_blank:
                            # It's a blank line!
                            blank_lines += 1
                        line_blank = True
                        line_idx += 1
                        line_starts[line_idx] = seg_idx + 1
                    elif forward_slice[seg_idx].is_type("comment"):
                        # Lines with comments aren't blank
                        line_blank = False
                        comment_lines.append(line_idx)
                    elif forward_slice[seg_idx].is_type("comma"):
                        # Keep track of where the comma is.
                        # We'll evaluate it later.
                        comma_line_idx = line_idx
                        comma_seg_idx = seg_idx
                    seg_idx += 1

                # Infer the comma style (NB this could be different for each case!)
                if comma_line_idx is None:
                    comma_style = "final"
                elif line_idx == 0:
                    comma_style = "oneline"
                elif comma_line_idx == 0:
                    comma_style = "trailing"
                elif comma_line_idx == line_idx:
                    comma_style = "leading"
                else:
                    comma_style = "floating"

                # Readout of findings
                self.logger.info(
                    "blank_lines: %s, comma_line_idx: %s. final_line_idx: %s, final_seg_idx: %s",
                    blank_lines,
                    comma_line_idx,
                    line_idx,
                    seg_idx,
                )
                self.logger.info(
                    "comma_style: %r, line_starts: %r, comment_lines: %r",
                    comma_style,
                    line_starts,
                    comment_lines,
                )

                if blank_lines < 1:
                    # We've got an issue
                    self.logger.info(
                        "!! Found CTE without enough blank lines.",
                    )

                    # Based on the current location of the comma we insert newlines
                    # to correct the issue.
                    fix_type = "create"  # In most cases we just insert newlines.
                    if comma_style == "oneline":
                        # Here we respect the target comma style to insert at the relevant point.
                        if self.comma_style == "trailing":
                            # Add a blank line after the comma
                            fix_point = forward_slice[comma_seg_idx + 1]
                            # Optionally here, if the segment we've landed on is
                            # whitespace then we REPLACE it rather than inserting.
                            if forward_slice[comma_seg_idx + 1].is_type("whitespace"):
                                fix_type = "edit"
                        elif self.comma_style == "leading":
                            # Add a blank line before the comma
                            fix_point = forward_slice[comma_seg_idx]
                        # In both cases it's a double newline.
                        num_newlines = 2
                    else:
                        # In the following cases we only care which one we're in
                        # when comments don't get in the way. If they *do*, then
                        # we just work around them.
                        if not comment_lines or line_idx - 1 not in comment_lines:
                            self.logger.info("Comment routines not applicable")
                            if comma_style in ("trailing", "final", "floating"):
                                # Detected an existing trailing comma or it's a final CTE,
                                # OR the comma isn't leading or trailing.
                                # If the preceeding segment is whitespace, replace it
                                if forward_slice[seg_idx - 1].is_type("whitespace"):
                                    fix_point = forward_slice[seg_idx - 1]
                                    fix_type = "edit"
                                else:
                                    # Otherwise add a single newline before the end content.
                                    fix_point = forward_slice[seg_idx]
                            elif comma_style == "leading":
                                # Detected an existing leading comma.
                                fix_point = forward_slice[comma_seg_idx]
                        else:
                            self.logger.info("Handling preceeding comments")
                            offset = 1
                            while line_idx - offset in comment_lines:
                                offset += 1
                            fix_point = forward_slice[
                                line_starts[line_idx - (offset - 1)]
                            ]
                        # Note: There is an edge case where this isn't enough, if
                        # comments are in strange places, but we'll catch them on
                        # the next iteration.
                        num_newlines = 1

                    fixes = [
                        LintFix(
                            fix_type,
                            fix_point,
                            [self.make_newline(pos_marker=fix_point.pos_marker)]
                            * num_newlines,
                        )
                    ]
                    # Create a result, anchored on the start of the next content.
                    error_buffer.append(
                        LintResult(anchor=forward_slice[seg_idx], fixes=fixes)
                    )
        # Return the buffer if we have one.
        return error_buffer or None


@std_rule_set.document_fix_compatible
@std_rule_set.register
class Rule_L023(BaseCrawler):
    """Single whitespace expected after AS in WITH clause.

    | **Anti-pattern**

    .. code-block::

        WITH plop AS(
            SELECT * FROM foo
        )

        SELECT a FROM plop


    | **Best practice**
    | The • character represents a space.
    | Add a space after AS, to avoid confusing
    | it for a function.

    .. code-block::

        WITH plop AS•(
            SELECT * FROM foo
        )

        SELECT a FROM plop
    """

    expected_mother_segment_type = "with_compound_statement"
    pre_segment_identifier = ("name", "AS")
    post_segment_identifier = ("type", "start_bracket")
    allow_newline = False

    def _eval(self, segment, **kwargs):
        """Single whitespace expected in mother segment between pre and post segments."""
        error_buffer = []
        if segment.is_type(self.expected_mother_segment_type):
            last_code = None
            mid_segs = []
            for seg in segment.segments:
                if seg.is_code:
                    if (
                        last_code
                        and getattr(last_code, self.pre_segment_identifier[0])
                        == self.pre_segment_identifier[1]
                        and getattr(seg, self.post_segment_identifier[0])
                        == self.post_segment_identifier[1]
                    ):
                        # Do we actually have the right amount of whitespace?
                        raw_inner = "".join(s.raw for s in mid_segs)
                        if raw_inner != " " and not (
                            self.allow_newline
                            and any(s.name == "newline" for s in mid_segs)
                        ):
                            if not raw_inner:
                                # There's nothing between. Just add a whitespace
                                fixes = [
                                    LintFix(
                                        "create",
                                        seg,
                                        [
                                            self.make_whitespace(
                                                raw=" ", pos_marker=seg.pos_marker
                                            )
                                        ],
                                    )
                                ]
                            else:
                                # Don't otherwise suggest a fix for now.
                                # TODO: Enable more complex fixing here.
                                fixes = None
                            error_buffer.append(
                                LintResult(anchor=last_code, fixes=fixes)
                            )
                    mid_segs = []
                    if not seg.is_meta:
                        last_code = seg
                else:
                    mid_segs.append(seg)
        return error_buffer or None


@std_rule_set.register
class Rule_L024(Rule_L023):
    """Single whitespace expected after USING in JOIN clause.

    | **Anti-pattern**

    .. code-block::

        SELECT b
        FROM foo
        LEFT JOIN zoo USING(a)

    | **Best practice**
    | The • character represents a space.
    | Add a space after USING, to avoid confusing it
    | for a function.

    .. code-block::

        SELECT b
        FROM foo
        LEFT JOIN zoo USING•(a)

    """

    expected_mother_segment_type = "join_clause"
    pre_segment_identifier = ("name", "USING")
    post_segment_identifier = ("type", "start_bracket")
    allow_newline = True


@std_rule_set.register
class Rule_L025(Rule_L020):
    """Tables should not be aliased if that alias is not used.

    | **Anti-pattern**

    .. code-block:: sql

        SELECT
            a
        FROM foo AS zoo

    | **Best practice**
    | Use the alias or remove it. An usused alias makes code
    | harder to read without changing any functionality.

    .. code-block:: sql

        SELECT
            zoo.a
        FROM foo AS zoo

        -- Alternatively...

        SELECT
            a
        FROM foo

    """

    def _lint_references_and_aliases(
        self, aliases, references, col_aliases, using_cols, parent_select
    ):
        """Check all aliased references against tables referenced in the query."""
        # A buffer to keep any violations.
        violation_buff = []
        # Check all the references that we have, keep track of which aliases we refer to.
        tbl_refs = set()
        for r in references:
            tbl_ref = r.extract_reference(level=2)
            if tbl_ref:
                tbl_refs.add(tbl_ref[0])

        for ref_str, seg, aliased in aliases:
            if aliased and ref_str not in tbl_refs:
                violation_buff.append(
                    LintResult(
                        anchor=seg,
                        description="Alias {0!r} is never used in SELECT statement.".format(
                            ref_str
                        ),
                    )
                )
        return violation_buff or None


@std_rule_set.register
class Rule_L026(Rule_L025):
    """References cannot reference objects not present in FROM clause.

    | **Anti-pattern**
    | In this example, the reference 'vee' has not been declared.

    .. code-block:: sql

        SELECT
            vee.a
        FROM foo

    | **Best practice**
    |  Remove the reference.

    .. code-block:: sql

        SELECT
            a
        FROM foo

    """

    def _lint_references_and_aliases(
        self, aliases, references, col_aliases, using_cols, parent_select
    ):
        # A buffer to keep any violations.
        violation_buff = []

        # Check all the references that we have, do they reference present aliases?
        for r in references:
            tbl_ref = r.extract_reference(level=2)
            # Check whether the string in the list of strings
            if tbl_ref and tbl_ref[0] not in [a[0] for a in aliases]:
                # Last check, this *might* be a correlated subquery reference.
                if parent_select:
                    parent_aliases = self._get_aliases_from_select(parent_select)
                    if parent_aliases and tbl_ref[0] in [a[0] for a in parent_aliases]:
                        continue

                violation_buff.append(
                    LintResult(
                        # Return the segment rather than the string
                        anchor=tbl_ref[1],
                        description="Reference {0!r} refers to table/view {1!r} not found in the FROM clause or found in parent subquery.".format(
                            r.raw, tbl_ref[0]
                        ),
                    )
                )
        return violation_buff or None


@std_rule_set.register
class Rule_L027(Rule_L025):
    """References should be qualified if select has more than one referenced table/view.

    NB: Except if they're present in a USING clause.

    | **Anti-pattern**
    | In this example, the reference 'vee' has not been declared
    | and the variables 'a' and 'b' are potentially ambiguous.

    .. code-block:: sql

        SELECT a, b
        FROM foo
        LEFT JOIN vee ON vee.a = foo.a

    | **Best practice**
    |  Add the references.

    .. code-block:: sql

        SELECT foo.a, vee.b
        FROM foo
        LEFT JOIN vee ON vee.a = foo.a
    """

    def _lint_references_and_aliases(
        self, aliases, references, col_aliases, using_cols, parent_select
    ):
        # Do we have more than one? If so, all references should be qualified.
        if len(aliases) <= 1:
            return None
        # A buffer to keep any violations.
        violation_buff = []
        # Check all the references that we have.
        for r in references:
            this_ref_type = r.qualification()
            if (
                this_ref_type == "unqualified"
                and r.raw not in col_aliases
                and r.raw not in using_cols
            ):
                violation_buff.append(
                    LintResult(
                        anchor=r,
                        description="Unqualified reference {0!r} found in select with more than one referenced table/view.".format(
                            r.raw
                        ),
                    )
                )

        return violation_buff or None


@std_rule_set.document_configuration
@std_rule_set.register
class Rule_L028(Rule_L025):
    """References should be consistent in statements with a single table.

    | **Anti-pattern**
    | In this example, only the field `b` is referenced.

    .. code-block:: sql

        SELECT
            a,
            foo.b
        FROM foo

    | **Best practice**
    |  Remove all the reference or reference all the fields.

    .. code-block:: sql

        SELECT
            a,
            b
        FROM foo

        -- Also good

        SELECT
            foo.a,
            foo.b
        FROM foo

    """

    config_keywords = ["single_table_references"]

    def _lint_references_and_aliases(
        self, aliases, references, col_aliases, using_cols, parent_select
    ):
        """Iterate through references and check consistency."""
        # How many aliases are there? If more than one then abort.
        if len(aliases) > 1:
            return None
        # A buffer to keep any violations.
        violation_buff = []
        # Check all the references that we have.
        seen_ref_types = set()
        for ref in references:
            # We skip any unqualified wildcard references (i.e. *). They shouldn't count.
            if not ref.is_qualified() and ref.is_type("wildcard_identifier"):
                continue
            this_ref_type = ref.qualification()
            if self.single_table_references == "consistent":
                if seen_ref_types and this_ref_type not in seen_ref_types:
                    violation_buff.append(
                        LintResult(
                            anchor=ref,
                            description="{0} reference {1!r} found in single table select which is inconsistent with previous references.".format(
                                this_ref_type.capitalize(), ref.raw
                            ),
                        )
                    )
            elif self.single_table_references != this_ref_type:
                violation_buff.append(
                    LintResult(
                        anchor=ref,
                        description="{0} reference {1!r} found in single table select.".format(
                            this_ref_type.capitalize(), ref.raw
                        ),
                    )
                )
            seen_ref_types.add(this_ref_type)

        return violation_buff or None


@std_rule_set.document_configuration
@std_rule_set.register
class Rule_L029(BaseCrawler):
    """Keywords should not be used as identifiers.

    | **Anti-pattern**
    | In this example, SUM function is used as an alias.

    .. code-block:: sql

        SELECT
            sum.a
        FROM foo AS sum

    | **Best practice**
    |  Avoid keywords as the name of an alias.

    .. code-block:: sql

        SELECT
            vee.a
        FROM foo AS vee

    """

    config_keywords = ["only_aliases"]

    def _eval(self, segment, dialect, parent_stack, **kwargs):
        """Keywords should not be used as identifiers."""
        if segment.name == "naked_identifier":
            # If self.only_aliases is true, we're a bit pickier here
            if self.only_aliases:
                # Aliases are ok (either directly, or in column definitions or in with statements)
                if parent_stack[-1].is_type(
                    "alias_expression",
                    "column_definition",
                    "with_compound_statement",
                ):
                    pass
                # All other references may not be at the discretion of the developer, so leave them out
                else:
                    return None
            # Actually lint
            if segment.raw.upper() in dialect.sets("unreserved_keywords"):
                return LintResult(anchor=segment)


@std_rule_set.document_configuration
@std_rule_set.register
class Rule_L030(Rule_L010):
    """Inconsistent capitalisation of function names.

    The functionality for this rule is inherited from :obj:`Rule_L010`.

    | **Anti-pattern**
    | In this example, the two SUM functions don't have the same capitalisation.

    .. code-block:: sql

        SELECT
            sum(a) AS aa,
            SUM(b) AS bb
        FROM foo

    | **Best practice**
    |  Make the case consistent.

    .. code-block:: sql

        SELECT
            sum(a) AS aa,
            sum(b) AS bb
        FROM foo

    """

    _target_elems: List[Tuple[str, str]] = [("name", "function_name")]


@std_rule_set.document_fix_compatible
@std_rule_set.register
class Rule_L031(BaseCrawler):
    """Avoid table aliases in from clauses and join conditions.

    | **Anti-pattern**
    | In this example, alias 'o' is used for the orders table, and 'c' is used for 'customers' table.

    .. code-block:: sql

        SELECT
            COUNT(o.customer_id) as order_amount,
            c.name
        FROM orders as o
        JOIN customers as c on o.id = c.user_id


    | **Best practice**
    |  Avoid aliases.

    .. code-block:: sql

        SELECT
            COUNT(orders.customer_id) as order_amount,
            customers.name
        FROM orders
        JOIN customers on orders.id = customers.user_id

        -- Self-join will not raise issue

        SELECT
            table.a,
            table_alias.b,
        FROM
            table
            LEFT JOIN table AS table_alias ON table.foreign_key = table_alias.foreign_key

    """

    def _eval(self, segment, **kwargs):
        """Identify aliases in from clause and join conditions.

        Find base table, table expressions in join, and other expressions in select clause
        and decide if it's needed to report them.
        """
        if segment.is_type("select_statement"):
            # A buffer for all table expressions in join conditions
            table_expression_segments = []
            column_reference_segments = []

            from_clause_segment = segment.get_child("from_clause")

            if not from_clause_segment:
                return None

            table_expression = from_clause_segment.get_child("table_expression")

            # Find base table
            base_table = None
            if table_expression:
                base_table = table_expression.get_child("object_reference")

            from_clause_index = segment.segments.index(from_clause_segment)
            from_clause_and_after = segment.segments[from_clause_index:]

            for clause in from_clause_and_after:
                for table_expression in clause.recursive_crawl("table_expression"):
                    table_expression_segments.append(table_expression)
                for column_reference in clause.recursive_crawl("column_reference"):
                    column_reference_segments.append(column_reference)

            return (
                self._lint_aliases_in_join(
                    base_table,
                    table_expression_segments,
                    column_reference_segments,
                    segment,
                )
                or None
            )
        return None

    def _lint_aliases_in_join(
        self, base_table, table_expression_segments, column_reference_segments, segment
    ):
        """Lint and fix all aliases in joins - except for self-joins."""
        # A buffer to keep any violations.
        violation_buff = []

        for table_exp in table_expression_segments:
            table_ref = table_exp.get_child("object_reference")

            # If this is self-join - skip it
            if (
                base_table
                and base_table.raw == table_ref.raw
                and base_table != table_ref
            ):
                continue

            whitespace_ref = table_exp.get_child("whitespace")

            # If there's no alias expression - skip it
            alias_exp_ref = table_exp.get_child("alias_expression")
            if alias_exp_ref is None:
                continue

            alias_identifier_ref = alias_exp_ref.get_child("identifier")
            select_clause = segment.get_child("select_clause")

            ids_refs = []

            # Find all references to alias in select clause
            for alias_with_column in select_clause.recursive_crawl("object_reference"):
                used_alias_ref = alias_with_column.get_child("identifier")
                if used_alias_ref and used_alias_ref.raw == alias_identifier_ref.raw:
                    ids_refs.append(used_alias_ref)

            # Find all references to alias in column references
            for exp_ref in column_reference_segments:
                used_alias_ref = exp_ref.get_child("identifier")
                # exp_ref.get_child('dot') ensures that the column reference includes a table reference
                if (
                    used_alias_ref.raw == alias_identifier_ref.raw
                    and exp_ref.get_child("dot")
                ):
                    ids_refs.append(used_alias_ref)

            # Fixes for deleting ` as sth` and for editing references to aliased tables
            fixes = [
                *[LintFix("delete", d) for d in [alias_exp_ref, whitespace_ref]],
                *[
                    LintFix("edit", alias, alias.edit(table_ref.raw))
                    for alias in [alias_identifier_ref, *ids_refs]
                ],
            ]

            violation_buff.append(
                LintResult(
                    anchor=alias_identifier_ref,
                    description="Avoid using aliases in join condition",
                    fixes=fixes,
                )
            )

        return violation_buff or None


@std_rule_set.register
class Rule_L032(BaseCrawler):
    """Prefer specifying join keys instead of using "USING".

    | **Anti-pattern**

    .. code-block:: sql

        SELECT
            table_a.field_1,
            table_b.field_2
        FROM
            table_a
        INNER JOIN table_b USING (id)

    | **Best practice**
    |  Specify the keys directly

    .. code-block:: sql

        SELECT
            table_a.field_1,
            table_b.field_2
        FROM
            table_a
        INNER JOIN table_b
            ON table_a.id = table_b.id

    """

    def _eval(self, segment, **kwargs):
        """Look for USING in a join clause."""
        if segment.is_type("join_clause"):
            for seg in segment.segments:
                if seg.is_type("keyword") and seg.name == "USING":
                    return [
                        LintResult(
                            # Reference the element, not the string.
                            anchor=seg,
                            description=(
                                "Found USING statement. Expected only ON statements."
                            ),
                        )
                    ]
        return None


@std_rule_set.register
class Rule_L033(BaseCrawler):
    """UNION ALL is preferred over UNION.

    | **Anti-pattern**
    | In this example, UNION ALL should be preferred over UNION

    .. code-block:: sql

        SELECT a, b FROM table_1 UNION SELECT a, b FROM table_2

    | **Best practice**
    | Replace UNION with UNION ALL

    .. code-block:: sql

        SELECT a, b FROM table_1 UNION ALL SELECT a, b FROM table_2

    """

    def _eval(self, segment, raw_stack, **kwargs):
        """Look for UNION keyword not immediately followed by ALL keyword. Note that UNION DISTINCT is valid, rule only applies to bare UNION.

        The function does this by looking for a segment of type set_operator
        which has a UNION but no DISTINCT or ALL.
        """
        if segment.type == "set_operator":
            if "UNION" in segment.raw.upper() and not (
                "ALL" in segment.raw.upper() or "DISTINCT" in segment.raw.upper()
            ):
                return LintResult(anchor=segment)
        return LintResult()


@std_rule_set.document_fix_compatible
@std_rule_set.register
class Rule_L034(BaseCrawler):
    """Use wildcards then simple select targets before calculations and aggregates.

    | **Anti-pattern**

    .. code-block:: sql

        select
            a,
            *,
            row_number() over (partition by id order by date) as y,
            b
        from x


    | **Best practice**
    |  Order "select" targets in ascending complexity

    .. code-block:: sql

        select
            *,
            a,
            b,
            row_number() over (partition by id order by date) as y
        from x

    """

    def _validate(self, i, segment):
        # Check if we've seen a more complex select target element already
        if self.seen_band_elements[i + 1 : :] != [[]] * len(
            self.seen_band_elements[i + 1 : :]
        ):
            self.violation_buff.append(LintResult(anchor=segment))
        self.current_element_band = i
        self.seen_band_elements[i].append(segment)

    def _eval(self, segment, **kwargs):
        self.violation_buff = []
        # Bands of select targets in order to be enforced
        select_element_order_preference = (
            ("wildcard_expression",),
            (
                "object_reference",
                "literal",
                "cast_expression",
                ("function", "cast"),
                ("expression", "cast_expression"),
            ),
        )

        # Track which bands have been seen, with additional empty list for the non-matching elements
        # If we find a matching target element, we append the element to the corresponding index
        self.seen_band_elements = [[] for i in select_element_order_preference] + [[]]

        if segment.type == "select_clause":
            select_target_elements = segment.get_children("select_target_element")
            if not select_target_elements:
                return None

            # Iterate through all the select targets to find any order violations
            for segment in select_target_elements:
                # The band index of the current segment in select_element_order_preference
                self.current_element_band = None

                # Compare the segment to the bands in select_element_order_preference
                for i, band in enumerate(select_element_order_preference):
                    for e in band:
                        # Identify simple select target
                        if segment.get_child(e):
                            self._validate(i, segment)

                        # Identify function
                        elif type(e) == tuple and e[0] == "function":
                            try:
                                if (
                                    segment.get_child("function")
                                    .get_child("function_name")
                                    .raw
                                    == e[1]
                                ):
                                    self._validate(i, segment)
                            except AttributeError:
                                # If the segment doesn't match
                                pass

                        # Identify simple expression
                        elif type(e) == tuple and e[0] == "expression":
                            try:
                                if (
                                    segment.get_child("expression").get_child(e[1])
                                    and segment.get_child("expression").segments[0].type
                                    in (
                                        "column_reference",
                                        "object_reference",
                                        "literal",
                                    )
                                    # len == 2 to ensure the expression is 'simple'
                                    and len(segment.get_child("expression").segments)
                                    == 2
                                ):
                                    self._validate(i, segment)
                            except AttributeError:
                                # If the segment doesn't match
                                pass

                # If the target doesn't exist in select_element_order_preference then it is 'complex' and must go last
                if self.current_element_band is None:
                    self.seen_band_elements[-1].append(segment)

            if self.violation_buff:
                # Create a list of all the edit fixes
                # We have to do this at the end of iterating through all the select_target_elements to get the order correct
                # This means we can't add a lint fix to each individual LintResult as we go
                ordered_select_target_elements = [
                    segment for band in self.seen_band_elements for segment in band
                ]
                fixes = [
                    LintFix(
                        "edit",
                        initial_select_target_element,
                        replace_select_target_element,
                    )
                    for initial_select_target_element, replace_select_target_element in zip(
                        select_target_elements, ordered_select_target_elements
                    )
                ]

                # Add the set of fixes to the last lint result in the violation buffer
                self.violation_buff[-1].fixes = fixes

        return self.violation_buff or None
