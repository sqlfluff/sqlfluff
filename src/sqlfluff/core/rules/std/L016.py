"""Implementation of Rule L016."""


from sqlfluff.core.rules.base import LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)
from sqlfluff.core.rules.std.L003 import Rule_L003


@document_fix_compatible
@document_configuration
class Rule_L016(Rule_L003):
    """Line is too long."""

    config_keywords = [
        "max_line_length",
        "tab_space_size",
        "indent_unit",
        "ignore_comment_lines",
    ]

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

        Once split, we'll use a separate method to work out what
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
                # Is this line JUST COMMENT (with optional preceding whitespace) if
                # so, user will have to fix themselves.
                if len(this_line) == 1 or all(
                    elem.name == "whitespace" or elem.is_meta for elem in this_line[:-1]
                ):
                    self.logger.info(
                        "Unfixable inline comment, alone on line: %s", this_line[-1]
                    )
                    if self.ignore_comment_lines:
                        return LintResult()
                    else:
                        return LintResult(anchor=segment)

                self.logger.info(
                    "Attempting move of inline comment at end of line: %s",
                    this_line[-1],
                )
                # Set up to delete the original comment and the preceding whitespace
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
