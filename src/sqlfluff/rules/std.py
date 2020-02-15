"""Standard SQL Linting Rules."""

import logging

from .base import BaseCrawler, LintFix, LintResult, RuleSet


std_rule_set = RuleSet(name='standard')


@std_rule_set.register
class Rule_L001(BaseCrawler):
    """Uneccessary trailing whitespace."""

    def _eval(self, segment, raw_stack, **kwargs):
        """Uneccessary trailing whitespace.

        Look for newline segments, and then evaluate what
        it was preceeded by.
        """
        # We only trigger on newlines
        if segment.type == 'newline' and len(raw_stack) > 0 and raw_stack[-1].type == 'whitespace':
            # If we find a newline, which is preceeded by whitespace, then bad
            deletions = []
            idx = -1
            while True:
                if raw_stack[idx].type == 'whitespace':
                    deletions.append(raw_stack[idx])
                    idx -= 1
                else:
                    break
            return LintResult(
                anchor=deletions[-1],
                fixes=[LintFix('delete', d) for d in deletions]
            )
        return LintResult()


@std_rule_set.register
class Rule_L002(BaseCrawler):
    """Mixed Tabs and Spaces in single whitespace.

    This rule will fail if a single section of whitespace
    contains both tabs and spaces.

    Args:
        tab_space_size (:obj:`int`): The number of spaces to consider
            equal to one tab. Used in the fixing step of this rule.
            Defaults to 4.

    """

    def __init__(self, tab_space_size=4, **kwargs):
        """Initialise, extracting the tab size from the config.

        We need to know the tab size for reconstruction.
        """
        self.tab_space_size = tab_space_size
        super(Rule_L002, self).__init__(**kwargs)

    def _eval(self, segment, raw_stack, **kwargs):
        """Mixed Tabs and Spaces in single whitespace.

        Only trigger from whitespace segments if they contain
        multiple kinds of whitespace.
        """
        def construct_response():
            """Make this generic so we can call it from a few places."""
            return LintResult(
                anchor=segment,
                fixes=[
                    LintFix(
                        'edit', segment,
                        segment.edit(segment.raw.replace('\t', ' ' * self.tab_space_size)))
                ]
            )

        if segment.type == 'whitespace':
            if ' ' in segment.raw and '\t' in segment.raw:
                if len(raw_stack) == 0 or raw_stack[-1].type == 'newline':
                    # We've got a single whitespace at the beginning of a line.
                    # It's got a mix of spaces and tabs. Replace each tab with
                    # a multiple of spaces
                    return construct_response()
                elif raw_stack[-1].type == 'whitespace':
                    # It's preceeded by more whitespace!
                    # We shouldn't worry about correcting those
                    # segments, because those will be caught themselves, but we
                    # do want to collect them together.
                    buff = list(raw_stack)
                    while True:
                        # pop something off the end
                        seg = buff.pop()
                        if seg.type == 'whitespace':
                            if len(buff) == 0:
                                # Found start of file
                                return construct_response()
                            else:
                                continue
                        elif seg.type == 'newline':
                            # we're at the start of a line
                            return construct_response()
                        else:
                            # We're not at the start of a line
                            break


@std_rule_set.register
class Rule_L003(BaseCrawler):
    """Indentation not consistent with previous lines.

    Args:
        tab_space_size (:obj:`int`): The number of spaces to consider
            equal to one tab. Used in the fixing step of this rule.
            Defaults to 4.
        indent_unit (:obj:`str`): Whether to use tabs or spaces to
            add new indents. Defaults to `space`.

    Note:
        This rule used to be _"Indentation length is not a multiple
        of {tab_space_size}"_, but was changed to be much smarter.

    """

    def __init__(self, tab_space_size=4, indent_unit='space', **kwargs):
        """Initialise, extracting the tab size from the config."""
        self.tab_space_size = tab_space_size
        self.indent_unit = indent_unit
        super(Rule_L003, self).__init__(**kwargs)

    def _make_indent(self, num=1, tab_space_size=None, indent_unit=None):
        if (indent_unit or self.indent_unit) == 'tab':
            base_unit = '\t'
        elif (indent_unit or self.indent_unit) == 'space':
            base_unit = ' ' * (tab_space_size or self.tab_space_size)
        else:
            raise ValueError("Unexpected value for `indent_unit`: {0!r}".format(
                indent_unit or self.indent_unit))
        return base_unit * num

    def _indent_size(self, segments):
        indent_size = 0
        for elem in segments:
            raw = elem.raw
            # convert to spaces for convenience (and hanging indents)
            raw = raw.replace('\t', ' ' * self.tab_space_size)
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
            if elem.type == 'newline':
                result_buffer[line_no] = {
                    'line_no': line_no,
                    # Using slicing to copy line_buffer here to be py2 compliant
                    'line_buffer': line_buffer[:],
                    'indent_buffer': indent_buffer,
                    'indent_size': indent_size,
                    'indent_balance': this_indent_balance,
                    'hanging_indent': hanger_pos if line_indent_stack else None,
                    'clean_indent': clean_indent
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
                # did the last line end with an indent?
                for search_elem in reversed(result_buffer[line_no - 1]['line_buffer']):
                    if search_elem.type in ('newline', 'whitespace'):
                        continue
                    elif search_elem.is_meta and search_elem.indent_val > 0:
                        clean_indent = True
                    break
            elif in_indent:
                if elem.type == 'whitespace':
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
                    line_indent_stack.append(
                        self._indent_size(line_buffer)
                    )
                    hanger_pos = None
                else:
                    # this is a dedent, we could still have a hanging indent,
                    # but only if there's enough on the stack
                    if line_indent_stack:
                        line_indent_stack.pop()
            elif elem.is_code and hanger_pos is None:
                hanger_pos = self._indent_size(line_buffer[:-1])

        # If we get to the end, and still have a buffer, add it on
        if line_buffer:
            result_buffer[line_no] = {
                'line_no': line_no,
                'line_buffer': line_buffer,
                'indent_buffer': indent_buffer,
                'indent_size': indent_size,
                'indent_balance': indent_balance,
                'hanging_indent': line_indent_stack.pop() if line_indent_stack else None,
                'clean_indent': clean_indent
            }
        return result_buffer

    def _coerce_indent_to(self, desired_indent, current_indent_buffer, current_anchor):
        """Generate fixes to make an indent a certain size."""
        # If there shouldn't be an indent at all, just delete.
        if len(desired_indent) == 0:
            fixes = [
                LintFix('delete', elem) for elem in current_indent_buffer
            ]
        # If we don't have any indent and we should, then add a single
        elif len(''.join(elem.raw for elem in current_indent_buffer)) == 0:
            fixes = [LintFix(
                'create', current_anchor,
                self.make_whitespace(
                    raw=desired_indent,
                    pos_marker=current_anchor.pos_marker)
            )]
        # Otherwise edit the first element to be the right size and delete the rest
        else:
            # Edit the first element of this line's indent.
            fixes = [LintFix(
                'edit', current_indent_buffer[0],
                self.make_whitespace(
                    raw=desired_indent,
                    pos_marker=current_indent_buffer[0].pos_marker)
            )]
            # Remove the others.
            for seg in current_indent_buffer[1:]:
                fixes.append(LintFix('delete', seg))
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
          the same indent balance at it's start.
        - Apart from "whole" indents, a "hanging" indent is possible
          if the line starts in line with either the indent of the
          previous line or if it starts at the same indent as the *last*
          indent meta segment in the previous line.

        """
        # Memory keeps track of what we just saw
        if not memory:
            memory = {
                # in_indent keeps track of whether we're in an indent right now
                'in_indent': True,
                # problem_lines keeps track of lines with problems so that we
                # don't compare to them.
                'problem_lines': [],
                # hanging_lines keeps track of hanging lines so that we don't
                # compare to them when assessing indent.
                'hanging_lines': []
            }

        if segment.type == 'newline':
            memory['in_indent'] = True
            # We're not going to flag on empty lines so we can safely proceed
            return LintResult(memory=memory)
        elif memory['in_indent']:
            if segment.type == 'whitespace':
                # it's whitespace, carry on
                return LintResult(memory=memory)
            elif segment.segments or segment.is_meta:
                # it's not a raw segment. Carry on.
                return LintResult(memory=memory)
            else:
                memory['in_indent'] = False
                # we're found a non-whitespace element. This is our trigger,
                # which we'll handle after this if-statement
        else:
            # Not in indent and not a newline, don't trigger here.
            return LintResult(memory=memory)

        res = self._process_raw_stack(raw_stack + (segment,))
        this_line_no = max(res.keys())
        this_line = res.pop(this_line_no)

        # Is it a hanging indent?
        if len(res) > 0:
            last_line_hanger_indent = res[this_line_no - 1]['hanging_indent']
            # Let's just deal with hanging indents here.
            if (
                # NB: Hangers are only allowed if there was content after the last
                # indent on the previous line. Otherwise it's just an indent.
                this_line['indent_size'] == last_line_hanger_indent
                # Or they're if the indent balance is the same and the indent is the
                # same
                or (
                    this_line['indent_size'] == res[this_line_no - 1]['indent_size']
                    and this_line['indent_balance'] == res[this_line_no - 1]['indent_balance']
                )
            ):
                # This is a HANGER
                memory['hanging_lines'].append(this_line_no)
                return LintResult(memory=memory)
        # Is this an indented first line?
        else:
            if this_line['indent_size'] > 0:
                return LintResult(
                    anchor=segment,
                    memory=memory,
                    description="First line has unexpected indent",
                    fixes=[LintFix('delete', elem) for elem in this_line['indent_buffer']]
                )

        # Assuming it's not a hanger, let's compare it to the other previous
        # lines. We do it in reverse so that closer lines are more relevant.
        for k in sorted(res.keys(), reverse=True):

            # Is this a problem line?
            if k in memory['problem_lines'] + memory['hanging_lines']:
                # Skip it if it is
                continue

            # Is this an empty line?
            if not any(elem.is_code for elem in res[k]['line_buffer']):
                # Skip if it is
                continue

            # Is the indent balance the same?
            indent_diff = this_line['indent_balance'] - res[k]['indent_balance']
            if indent_diff == 0:
                if this_line['indent_size'] != res[k]['indent_size']:
                    # Indents don't match even though balance is the same...
                    memory['problem_lines'].append(this_line_no)

                    # Work out desired indent
                    if res[k]['indent_size'] == 0:
                        desired_indent = ''
                    elif this_line['indent_size'] == 0:
                        desired_indent = self._make_indent()
                    else:
                        # The previous indent.
                        desired_indent = ''.join(elem.raw for elem in res[k]['indent_buffer'])

                    # Make fixes
                    fixes = self._coerce_indent_to(
                        desired_indent=desired_indent,
                        current_indent_buffer=this_line['indent_buffer'],
                        current_anchor=segment)

                    return LintResult(
                        anchor=segment,
                        memory=memory,
                        description="Indentation not consistent with line #{0}".format(k),
                        # See above for logic
                        fixes=fixes
                    )
                else:
                    # Indents match. And this is a line that it's ok to
                    # compare with, we're fine.
                    return LintResult(memory=memory)

            # Are we at a deeper indent?
            elif indent_diff > 0:
                # NB: We shouldn't need to deal with hanging indents
                # here, they should already have been dealt with before.

                # Check to see if we've got a whole number of multiples. If
                # we do then record the number for later, otherwise raise
                # an error. We do the comparison here so we have a reference
                # point to do the repairs. We need a sensible previous line
                # to base the repairs off.
                if this_line['indent_size'] % self.tab_space_size != 0:
                    memory['problem_lines'].append(this_line_no)

                    # If we have a clean indent, we can just add steps in line
                    # with the difference in the indent buffers. simples.
                    # We can also do this if we've skipped a line. I think?
                    if this_line['clean_indent'] or this_line_no - k > 1:
                        desired_indent = (
                            ''.join(elem.raw for elem in res[k]['indent_buffer'])
                            + (self._make_indent() * indent_diff))
                    # If we have the option of a hanging indent then use it.
                    elif res[k]['hanging_indent']:
                        desired_indent = ' ' * res[k]['hanging_indent']
                    else:
                        raise RuntimeError("Unexpected case, please report bug, inluding the query you are linting!")

                    # Make fixes
                    fixes = self._coerce_indent_to(
                        desired_indent=desired_indent,
                        current_indent_buffer=this_line['indent_buffer'],
                        current_anchor=segment)

                    return LintResult(
                        anchor=segment,
                        memory=memory,
                        description=(
                            "Indentation not hanging or "
                            "a multiple of {0} spaces").format(self.tab_space_size),
                        fixes=fixes
                    )
                else:
                    # We'll need this value later.
                    this_indent_num = this_line['indent_size'] // self.tab_space_size

                # We know that the indent balance is higher, what actually is
                # the difference in indent counts? It should be a whole number
                # if we're still here.
                comp_indent_num = res[k]['indent_size'] // self.tab_space_size

                # The indent number should be at least 1, and can be UP TO
                # and including the difference in the indent balance.
                if comp_indent_num == this_indent_num:
                    memory['problem_lines'].append(this_line_no)
                    return LintResult(
                        anchor=segment,
                        memory=memory,
                        description="Indent expected and not found compared to line #{0}".format(k),
                        # Add in an extra bit of whitespace for the indent
                        fixes=[LintFix(
                            'create', segment,
                            self.make_whitespace(
                                raw=self._make_indent(),
                                pos_marker=segment.pos_marker)
                        )]
                    )
                elif this_indent_num < comp_indent_num:
                    memory['problem_lines'].append(this_line_no)
                    return LintResult(
                        anchor=segment,
                        memory=memory,
                        description="Line under-indented compared to line #{0}".format(k),
                        fixes=[LintFix(
                            'create', segment,
                            self.make_whitespace(
                                # Make the minimum indent for it to be ok.
                                raw=self._make_indent(num=comp_indent_num - this_indent_num),
                                pos_marker=segment.pos_marker)
                        )]
                    )
                elif this_indent_num > comp_indent_num + indent_diff:
                    # Calculate the lowest ok indent:
                    desired_indent = self._make_indent(num=comp_indent_num - this_indent_num)

                    # Make fixes
                    fixes = self._coerce_indent_to(
                        desired_indent=desired_indent,
                        current_indent_buffer=this_line['indent_buffer'],
                        current_anchor=segment)

                    memory['problem_lines'].append(this_line_no)
                    return LintResult(
                        anchor=segment,
                        memory=memory,
                        description="Line over-indented compared to line #{0}".format(k),
                        fixes=fixes
                    )

                # This was a valid comparison, so if it doesn't flag then
                # we can assume that we're ok.
                return LintResult(memory=memory)

            # NB: At shallower indents, we don't check, we just check the
            # previous lines with the same balance. Deeper indents can check
            # themselves.

        # If we get to here, then we're all good for now.
        return LintResult(memory=memory)


@std_rule_set.register
class Rule_L004(BaseCrawler):
    """Mixed Tab and Space indentation found in file."""

    def _eval(self, segment, raw_stack, memory, **kwargs):
        """Mixed Tab and Space indentation found in file.

        We use the `memory` feature here to keep track of
        what we've seen in the past.

        """
        indents_seen = memory.get('indents_seen', set())
        if segment.type == 'whitespace':
            if len(raw_stack) == 0 or raw_stack[-1].type == 'newline':
                indents_here = set(segment.raw)
                indents_union = indents_here | indents_seen
                memory['indents_seen'] = indents_union
                if len(indents_union) > 1:
                    # We are seeing an indent we haven't seen before and we've seen others before
                    return LintResult(anchor=segment, memory=memory)
                else:
                    return LintResult(memory=memory)
        return LintResult(memory=memory)


@std_rule_set.register
class Rule_L005(BaseCrawler):
    """Commas should not have whitespace directly before them."""

    def _eval(self, segment, raw_stack, **kwargs):
        """Commas should not have whitespace directly before them.

        We need at least one segment behind us for this to work.

        """
        if len(raw_stack) >= 1:
            cm1 = raw_stack[-1]
            if segment.type == 'comma' and cm1.type in ['whitespace', 'newline']:
                # NB: if its a *newline*, then it's confusing to the user
                # to report on the newline, so in that case we point at the comma
                if cm1.type == 'newline':
                    anchor = segment
                else:
                    anchor = cm1
                return LintResult(anchor=anchor, fixes=[LintFix('delete', cm1)])
        # Otherwise fine
        return None


@std_rule_set.register
class Rule_L006(BaseCrawler):
    """Operators should be surrounded by a single whitespace."""

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
                        'create', this_segment,
                        self.make_whitespace(raw=' ', pos_marker=this_segment.pos_marker))
                )
            elif len(segments_since_code) > 1:
                # TODO: This is a case we should deal with, but there are probably
                # some cases that SHOULDNT apply here (like comments and newlines)
                # so let's deal with them later
                anchor = None
            else:
                # We know it's just one thing.
                gap_seg = segments_since_code[-1]
                if gap_seg.raw != ' ':
                    # It's not just a single space
                    anchor = gap_seg
                    fixes.append(
                        LintFix(
                            'edit', gap_seg,
                            self.make_whitespace(raw=' ', pos_marker=gap_seg.pos_marker))
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
        if parent_stack and parent_stack[-1].type == 'expression':
            if segment.is_code:
                # This is code, what kind?
                if segment.type in ['binary_operator', 'comparison_operator']:
                    # It's an operator, we can evaluate whitespace before it.
                    anchor, fixes = _handle_previous_segments(
                        memory['since_code'], anchor=segment, this_segment=segment,
                        fixes=fixes)
                    if anchor:
                        description = "Operators should be preceded by a space."
                else:
                    # It's not an operator, we can evaluate what happened after an
                    # operator if that's the last code we saw.
                    if memory['last_code'] and memory['last_code'].type in ['binary_operator', 'comparison_operator']:
                        # Evaluate whitespace AFTER the operator
                        anchor, fixes = _handle_previous_segments(
                            memory['since_code'], anchor=memory['last_code'],
                            this_segment=segment, fixes=fixes)
                        if anchor:
                            description = "Operators should be followed by a space."
                    else:
                        # This isn't an operator, and the thing before it wasn't
                        # either. I don't think that's an issue for now.
                        pass
                # Prepare memory for later
                memory['last_code'] = segment
                memory['since_code'] = []
            else:
                # This isn't a code segment...
                # Prepare memory for later
                memory['since_code'].append(segment)
        else:
            # Reset the memory if we're not in an expression
            memory = {'last_code': None, 'since_code': []}

        # Anchor is our signal as to whether there's a problem
        if anchor:
            return LintResult(anchor=anchor, memory=memory, fixes=fixes, description=description)
        else:
            return LintResult(memory=memory)


@std_rule_set.register
class Rule_L007(BaseCrawler):
    """Operators near newlines should be after, not before the newline."""

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
        if parent_stack and parent_stack[-1].type == 'expression':
            if segment.is_code:
                # This is code, what kind?
                if segment.type in ['binary_operator', 'comparison_operator']:
                    # We only trigger if the last was an operator, not if this is.
                    pass
                elif memory['last_code'] and memory['last_code'].type in ['binary_operator', 'comparison_operator']:
                    # It's not an operator, but the last code was. Now check to see
                    # there is a newline between us and the last operator.
                    for s in memory['since_code']:
                        if s.name == 'newline':
                            anchor = memory['last_code']
                            # TODO: Work out a nice fix for this.
                # Prepare memory for later
                memory['last_code'] = segment
                memory['since_code'] = []
            else:
                # This isn't a code segment...
                # Prepare memory for later
                memory['since_code'].append(segment)
        else:
            # Reset the memory if we're not in an expression
            memory = {'last_code': None, 'since_code': []}

        # Anchor is our signal as to whether there's a problem
        if anchor:
            return LintResult(anchor=anchor, memory=memory)
        else:
            return LintResult(memory=memory)


@std_rule_set.register
class Rule_L008(BaseCrawler):
    """Commas should be followed by a single whitespace unless followed by a comment."""

    def _eval(self, segment, raw_stack, **kwargs):
        """Commas should be followed by a single whitespace unless followed by a comment.

        This is a slightly odd one, because we'll almost always evaluate from a point a few places
        after the problem site. NB: We need at least two segments behind us for this to work.
        """
        if len(raw_stack) < 2:
            return None

        cm1 = raw_stack[-1]
        cm2 = raw_stack[-2]
        if cm2.name == 'comma':
            # comma followed by something that isn't whitespace?
            if cm1.name not in ['whitespace', 'newline']:
                ins = self.make_whitespace(raw=' ', pos_marker=cm1.pos_marker)
                return LintResult(anchor=cm1, fixes=[LintFix('create', cm1, ins)])
            # comma followed by too much whitespace?
            if (cm1.raw != ' ' and cm1.name != 'newline') and not segment.is_comment:
                repl = cm1.__class__(
                    raw=' ',
                    pos_marker=cm1.pos_marker
                )
                return LintResult(anchor=cm1, fixes=[LintFix('edit', cm1, repl)])
        # Otherwise we're fine
        return None


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
        elif segment.name == 'newline':
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
        return LintResult(anchor=segment, fixes=[LintFix('edit', segment, [segment, ins])])


@std_rule_set.register
class Rule_L010(BaseCrawler):
    """Inconsistent capitalisation of keywords.

    Args:
        capitalisation_policy (:obj:`str`): The capitalisation policy to
            enforce. One of `consistent`, `upper`, `lower`, `capitalise`.

    """

    # Binary operators behave like keywords too.
    _target_elems = ('keyword', 'binary_operator')

    def __init__(self, capitalisation_policy='consistent', **kwargs):
        """Initialise, extracting the capitalisation mode from the config."""
        capitalisation_options = ('consistent', 'upper', 'lower', 'capitalise')
        if capitalisation_policy not in capitalisation_options:
            raise ValueError(
                ("Unexpected capitalisation_policy for rule {1}: {0!r}\nShould "
                 "be one of: {2!r}").format(capitalisation_policy, self.__class__.__name__,
                                            capitalisation_options))
        self.capitalisation_policy = capitalisation_policy
        super(Rule_L010, self).__init__(**kwargs)

    def _eval(self, segment, memory, **kwargs):
        """Inconsistent capitalisation of keywords.

        We use the `memory` feature here to keep track of
        what we've seen in the past.

        """
        cases_seen = memory.get('cases_seen', set())

        if segment.type in self._target_elems:
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
                # NB: American spelling :(
                seen_case = "capitalize"
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
                elif policy == "capitalize":
                    new_raw = seg.raw.capitalize()
                elif policy == "consistent":
                    # The only case we DONT allow here is "inconsistent",
                    # because it doesn't actually help us.
                    filtered_cases_seen = [c for c in cases_seen if c != "inconsistent"]
                    if filtered_cases_seen:
                        # Get an element from what we've already seen.
                        return make_replacement(
                            seg,
                            list(filtered_cases_seen)[0]
                        )
                    else:
                        # If we haven't seen anything yet, then let's default
                        # to upper
                        return make_replacement(seg, "upper")
                else:
                    raise ValueError("Unexpected capitalisation policy: {0!r}".format(policy))
                # Make a new class and return it.
                return seg.__class__(
                    raw=new_raw, pos_marker=seg.pos_marker
                )

            if not seen_case:
                # Skip this if we haven't seen anything good.
                # No need to update memory
                return LintResult(memory=memory)
            elif (
                # Are we required to be consistent? (and this is inconsistent?)
                (
                    self.capitalisation_policy == "consistent" and (
                        # Either because we've seen multiple
                        (cases_seen and seen_case not in cases_seen)
                        # Or just because this one is inconsistent internally
                        or seen_case == "inconsistent")
                )
                # Are we just required to be specfic?
                # Policy is either upper, lower or capitalize
                or (self.capitalisation_policy != "consistent" and seen_case != self.capitalisation_policy)
            ):
                return LintResult(
                    anchor=segment,
                    fixes=[
                        LintFix('edit', segment, make_replacement(
                            segment, self.capitalisation_policy))
                    ],
                    memory=memory)
            else:
                # Update memory and carry on
                cases_seen.add(seen_case)
                memory['cases_seen'] = cases_seen
                return LintResult(memory=memory)

        # If it's not a keyword just carry on
        return LintResult(memory=memory)


@std_rule_set.register
class Rule_L011(BaseCrawler):
    """Implicit aliasing of table not allowed. Use explicit `AS` clause."""

    _target_elems = ('table_expression',)

    def _eval(self, segment, parent_stack, raw_stack, **kwargs):
        """Implicit aliasing of table/column not allowed. Use explicit `AS` clause.

        We look for the alias segment, and then evaluate it's parent and whether
        it contains an AS keyword. This is the _eval function for both L011 and L012.

        The use of `raw_stack` is just for working out how much whitespace to add.

        """
        if segment.type == 'alias_expression':
            if parent_stack[-1].type in self._target_elems:
                if not any(e.name.lower() == 'as' for e in segment.segments):
                    insert_buff = []
                    insert_str = ''
                    init_pos = segment.segments[0].pos_marker

                    # Add intial whitespace if we need to...
                    if raw_stack[-1].name not in ['whitespace', 'newline']:
                        insert_buff.append(self.make_whitespace(raw=' ', pos_marker=init_pos))
                        insert_str += ' '

                    # Add an AS (Uppercase for now, but could be corrected later)
                    insert_buff.append(self.make_keyword(raw='AS', pos_marker=init_pos.advance_by(insert_str)))
                    insert_str += 'AS'

                    # Add a trailing whitespace if we need to
                    if segment.segments[0].name not in ['whitespace', 'newline']:
                        insert_buff.append(self.make_whitespace(raw=' ', pos_marker=init_pos.advance_by(insert_str)))
                        insert_str += ' '

                    return LintResult(
                        anchor=segment,
                        fixes=[
                            LintFix(
                                'create', segment.segments[0],
                                insert_buff
                            )
                        ]
                    )
        return None


@std_rule_set.register
class Rule_L012(Rule_L011):
    """Implicit aliasing of column not allowed. Use explicit `AS` clause.

    NB: This rule inherits it's functionality from obj:`Rule_L011` but is
    seperate so that they can be enabled and disabled seperately.

    """

    _target_elems = ('select_target_element',)


@std_rule_set.register
class Rule_L013(BaseCrawler):
    """Column expression without alias. Use explicit `AS` clause.

    Args:
        allow_scalar (:obj:`bool`): If `True` then this rule will
            not fail if there is only one element in the select
            clause e.g. `SELECT 1 + 2 FROM blah`. It will still
            fail if there are multiple columns. (Default `True`)

    """

    def __init__(self, allow_scalar=True, **kwargs):
        """Initialise, extracting the allow_scalar mode from the config."""
        self.allow_scalar = allow_scalar
        super(Rule_L013, self).__init__(**kwargs)

    def _eval(self, segment, parent_stack, **kwargs):
        """Column expression without alias. Use explicit `AS` clause.

        We look for the select_target_element segment, and then evaluate
        whether it has an alias segment or not and whether the expression
        is complicated enough. `parent_stack` is to assess how many other
        elements there are.

        """
        if segment.type == 'select_target_element':
            if not any(e.type == 'alias_expression' for e in segment.segments):
                types = {e.type for e in segment.segments}
                unallowed_types = types - {'whitespace', 'newline', 'object_reference'}
                if len(unallowed_types) > 0:
                    # No fixes, because we don't know what the alias should be,
                    # the user should document it themselves.
                    if self.allow_scalar:
                        # Check *how many* elements there are in the select
                        # statement. If this is the only one, then we won't
                        # report an error.
                        num_elements = sum(e.type == 'select_target_element' for e in parent_stack[-1].segments)
                        if num_elements > 1:
                            return LintResult(anchor=segment)
                        else:
                            return None
                    else:
                        # Just erro if we don't care.
                        return LintResult(anchor=segment)
        return None


@std_rule_set.register
class Rule_L014(Rule_L010):
    """Inconsistent capitalisation of unquoted identifiers.

    The functionality for this rule is inherited from :obj:`Rule_L010`.

    Args:
        capitalisation_policy (:obj:`str`): The capitalisation policy to
            enforce. One of 'consistent', 'upper', 'lower', 'capitalise'.

    """

    _target_elems = ('naked_identifier',)


@std_rule_set.register
class Rule_L015(BaseCrawler):
    """DISTINCT used with parentheses."""

    def _eval(self, segment, raw_stack, **kwargs):
        """Uneccessary trailing whitespace.

        Look for DISTINCT keyword immediately followed by open parenthesis.
        """
        # We only trigger on start_bracket (open parenthesis)
        if segment.name == 'start_bracket':
            filt_raw_stack = self.filter_meta(raw_stack)
            if len(filt_raw_stack) > 0 and filt_raw_stack[-1].name == 'DISTINCT':
                # If we find DISTINCT followed by open_bracket, then bad.
                return LintResult(anchor=segment)
        return LintResult()


@std_rule_set.register
class Rule_L016(Rule_L003):
    """Line is too long.

    Args:
        max_line_length (:obj:`int`): The maximum length of a line
            to allow without raising a violation.
        tab_space_size (:obj:`int`): The number of spaces to consider
            equal to one tab. Used in the fixing step of this rule.
            Defaults to 4.
        indent_unit (:obj:`str`): Whether to use tabs or spaces to
            add new indents. Defaults to `space`.

    """

    def __init__(self, max_line_length=80, tab_space_size=4, indent_unit='space', **kwargs):
        """Initialise, getting the max line length."""
        self.max_line_length = max_line_length
        # Call out tab_space_size and indent_unit to make it clear they're still options.
        super(Rule_L016, self).__init__(
            tab_space_size=tab_space_size, indent_unit=indent_unit,
            **kwargs)

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
                    role=self.role, indent_balance=self.indent_balance,
                    indent_impulse=self.indent_impulse,
                    segments=''.join(elem.raw for elem in self.segments),
                    pos=self.segments[0].get_start_pos_marker())

            @property
            def raw(self):
                return ''.join(seg.raw for seg in self.segments)

            def first(self):
                # Return the first non meta segment
                return next(seg for seg in self.segments if not seg.is_meta)

            def others(self):
                gen = (seg for seg in self.segments if not seg.is_meta)
                next(gen)
                return tuple(gen)

            @staticmethod
            def find_segment_at(segments, pos):
                highest_pos = None
                for seg in segments:
                    if highest_pos is None or seg.pos_marker > highest_pos:
                        highest_pos = seg.pos_marker
                    if not seg.is_meta and seg.pos_marker == pos:
                        return seg
                # are we at the end of the file?
                if pos > highest_pos:
                    return None
                raise ValueError("Segment not found at position {0}".format(pos))

            def generate_fixes_to_coerce(self, segments, indent_section, crawler, indent):
                """Generate a list of fixes to create a break at this point.

                The `segments` argument is necessary to extract anchors
                from the existing segments.
                """
                fixes = []

                # Generate some sample indents:
                unit_indent = crawler._make_indent()
                indent_p1 = indent_section.raw + unit_indent
                if unit_indent in indent_section.raw:
                    indent_m1 = indent_section.raw.replace(unit_indent, '', 1)
                else:
                    indent_m1 = indent_section.raw

                if indent > 0:
                    new_indent = indent_p1
                elif indent < 0:
                    new_indent = indent_m1
                else:
                    new_indent = indent_section.raw

                create_anchor = self.find_segment_at(
                    segments, self.segments[-1].get_end_pos_marker())
                if create_anchor is None:
                    # If we're at the end of the file, there's no point
                    # creating anything.
                    return []

                if self.role == 'pausepoint':
                    # Assume that this means there isn't a breakpoint
                    # and that we'll break with the same indent as the
                    # existing line.

                    # NOTE: Deal with commas and binary operators differently here.
                    # Maybe only deal with commas to start with?
                    if any(seg.type == 'binary_operator' for seg in self.segments):
                        raise NotImplementedError("Don't know how to deal with binary operators here yet!!")

                    # Remove any existing whitespace
                    for elem in self.segments:
                        if not elem.is_meta and elem.type == 'whitespace':
                            fixes.append(
                                LintFix(
                                    'delete', elem
                                )
                            )

                    # Create a newline and a similar indent
                    fixes.append(
                        LintFix(
                            'create', create_anchor,
                            [
                                crawler.make_newline(create_anchor.pos_marker),
                                crawler.make_whitespace(new_indent, create_anchor.pos_marker)
                            ]
                        )
                    )
                    return fixes

                if self.role == 'breakpoint':
                    # Can we determine the required indent just from
                    # the info in this segment only?

                    # Remove anything which is already here
                    for elem in self.segments:
                        if not elem.is_meta:
                            fixes.append(
                                LintFix(
                                    'delete', elem
                                )
                            )
                    # Create a newline, create an indent of the relevant size
                    fixes.append(
                        LintFix(
                            'create', create_anchor,
                            [
                                crawler.make_newline(create_anchor.pos_marker),
                                crawler.make_whitespace(new_indent, create_anchor.pos_marker)
                            ]
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
                if seg.type == 'whitespace' or seg.is_meta:
                    whitespace_buff += (seg,)
                else:
                    indent_section = Section(
                        segments=whitespace_buff,
                        role='indent',
                        indent_balance=indent_balance
                    )
                    whitespace_buff = ()
                    segment_buff = (seg,)
            else:
                if seg.type == 'whitespace' or seg.is_meta:
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
                                    role='content',
                                    indent_balance=indent_balance
                                )
                            )
                            segment_buff = ()
                        # Deal with the whitespace
                        chunk_buff.append(
                            Section(
                                segments=whitespace_buff,
                                role='breakpoint',
                                indent_balance=indent_balance,
                                indent_impulse=indent_impulse
                            )
                        )
                        whitespace_buff = ()
                        indent_balance += indent_impulse
                        indent_impulse = 0

                    # Did we think we were in a pause?
                    # TODO: Renable binary operator breaks some time in future.
                    if is_pause:
                        if seg.name == 'comma':  # or seg.type == 'binary_operator'
                            # Having a double comma/operator should be impossible
                            # but let's deal with that case regardless.
                            segment_buff += whitespace_buff + (seg,)
                            whitespace_buff = ()
                        else:
                            # We need to end the comma/operator
                            # (taking any whitespace with it).
                            chunk_buff.append(
                                Section(
                                    segments=segment_buff + whitespace_buff,
                                    role='pausepoint',
                                    indent_balance=indent_balance
                                )
                            )
                            # Start the segment buffer off with this section.
                            whitespace_buff = ()
                            segment_buff = (seg,)
                            is_pause = False
                    else:
                        # We're not in a pause (or not in a pause yet)
                        if seg.name == 'comma':  # or seg.type == 'binary_operator'
                            if segment_buff:
                                # End the previous section, start a comma/operator.
                                # Any whitespace is added to the segment
                                # buff to go with the comma.
                                chunk_buff.append(
                                    Section(
                                        segments=segment_buff,
                                        role='content',
                                        indent_balance=indent_balance
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
            role = 'pausepoint'
        elif segment_buff:
            role = 'content'
        elif indent_impulse:
            role = 'breakpoint'
        else:
            raise ValueError("Is this possible?")

        chunk_buff.append(
            Section(
                segments=segment_buff + whitespace_buff,
                role=role,
                indent_balance=indent_balance
            )
        )

        logging.info("Rule L016: Sections")
        for sec in chunk_buff:
            logging.info(sec)

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
                sec for sec in chunk_buff
                if sec.role == 'pausepoint'
                and sec.indent_balance == 0
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
                    sec for sec in chunk_buff if sec.role == 'breakpoint'
                    and sec.indent_balance == 0 and sec.indent_impulse > 0
                ]
                if not upbreaks:
                    # No upbreaks?!
                    # abort
                    return []
                # First up break
                split_at = [(upbreaks[0], 1)]
                downbreaks = [
                    sec for sec in chunk_buff if sec.role == 'breakpoint'
                    and sec.indent_balance + sec.indent_impulse == 0 and sec.indent_impulse < 0
                ]
                # First down break where we reach the base
                if downbreaks:
                    split_at.append((downbreaks[0], 0))
                # If no downbreaks then the corresponding downbreak isn't on this line.

        logging.info("Split at: {0}".format(split_at))

        fixes = []
        for split, indent in split_at:
            fixes += split.generate_fixes_to_coerce(segments, indent_section, self, indent)

        logging.info("Fixes: {0}".format(fixes))

        return fixes

    def _eval(self, segment, raw_stack, **kwargs):
        """Line is too long.

        This only triggers on newline segments, evaluating the whole line.
        The detection is simple, the fixing is much trickier.

        """
        if segment.name == 'newline':
            # iterate to buffer the whole line up to this point
            this_line = []
            idx = -1
            while True:
                if len(raw_stack) >= abs(idx):
                    s = raw_stack[idx]
                    if s.name == 'newline':
                        break
                    else:
                        this_line.insert(0, s)
                        idx -= 1
                else:
                    break

            # Now we can work out the line length and deal with the content
            line_len = sum(len(s.raw) for s in this_line)
            if line_len > self.max_line_length:
                # Problem, we'll be reporting a violation. The
                # question is, can we fix it?

                # We'll need the indent, so let's get it for fixing.
                line_indent = []
                idx = 0
                for s in this_line:
                    if s.name == 'whitespace':
                        line_indent.append(s)
                    else:
                        break

                # Does the line end in an inline comment that we can move back?
                if this_line[-1].name == 'inline_comment':
                    # Is this line JUST COMMENT, if so, user will have to fix themselves
                    if len(this_line) == 1:
                        return LintResult(anchor=segment)
                    # Set up to delete the original comment and the preceeding whitespace
                    delete_buffer = [LintFix('delete', this_line[-1])]
                    idx = -2
                    while True:
                        if len(this_line) >= abs(idx) and this_line[idx].name == 'whitespace':
                            delete_buffer.append(LintFix('delete', this_line[idx]))
                            idx -= 1
                        else:
                            break
                    # Create a newline before this one with the existing comment, an
                    # identical indent AND a terminating newline, copied from the current
                    # target segment.
                    create_buffer = [
                        LintFix(
                            'create', this_line[0],
                            line_indent + [this_line[-1], segment]
                        )
                    ]
                    return LintResult(anchor=segment, fixes=delete_buffer + create_buffer)

                fixes = self._eval_line_for_breaks(this_line)
                if fixes:
                    return LintResult(anchor=segment, fixes=fixes)
                return LintResult(anchor=segment)
        # Otherwise we're all good
        return None


@std_rule_set.register
class Rule_L017(BaseCrawler):
    """Function name not immediately followed by bracket."""

    def _eval(self, segment, raw_stack, **kwargs):
        """Function name not immediately followed by bracket.

        Look for Function Segment with anything other than the
        function name before brackets
        """
        # We only trigger on start_bracket (open parenthesis)
        if segment.type == 'function':
            # Look for the function name
            for fname_idx, seg in enumerate(segment.segments):
                if seg.type == 'function_name':
                    break
            else:
                # This shouldn't happen, but let's not worry
                # about it if it does.
                return LintResult()

            # Look for the start bracket
            for bracket_idx, seg in enumerate(segment.segments):
                if seg.name == 'start_bracket':
                    break
            else:
                # This shouldn't happen, but let's not worry
                # about it if it does.
                return LintResult()

            if bracket_idx < fname_idx:
                # This is a result which shouldn't happen. Ignore it.
                return LintResult()

            if bracket_idx != fname_idx + 1:
                return LintResult(
                    anchor=segment.segments[fname_idx + 1],
                    fixes=[
                        LintFix('delete', segment.segments[idx])
                        for idx in range(fname_idx + 1, bracket_idx)
                    ])
        return LintResult()


@std_rule_set.register
class Rule_L018(BaseCrawler):
    """WITH clause closing bracket should be aligned with WITH keyword."""

    def __init__(self, tab_space_size=4, **kwargs):
        """Initialise, extracting the tab size from the config.

        We need to know the tab size for reconstruction.
        """
        self.tab_space_size = tab_space_size
        super(Rule_L018, self).__init__(**kwargs)

    def _eval(self, segment, raw_stack, **kwargs):
        """WITH clause closing bracket should be aligned with WITH keyword.

        Look for a with clause and evaluate the position of closing brackets.
        """
        # We only trigger on start_bracket (open parenthesis)
        if segment.type == 'with_compound_statement':
            raw_stack_buff = list(raw_stack)
            # Look for the with keyword
            for seg in segment.segments:
                if seg.name.lower() == 'with':
                    seg_line_no = seg.pos_marker.line_no
                    break
                else:
                    raw_stack_buff.append(seg)
            else:
                raise RuntimeError("Didn't find WITH keyword!")

            def indent_size_up_to(segs):
                seg_buff = []
                # Get any segments running up to the WITH
                for elem in reversed(segs):
                    if elem.type == 'newline':
                        break
                    elif elem.is_meta:
                        continue
                    else:
                        seg_buff.append(elem)
                # reverse the indent if we have one
                if seg_buff:
                    seg_buff = list(reversed(seg_buff))
                indent_str = ''.join(
                    seg.raw for seg in seg_buff
                ).replace('\t', ' ' * self.tab_space_size)
                indent_size = len(indent_str)
                return indent_size, indent_str

            balance = 0
            with_indent, with_indent_str = indent_size_up_to(raw_stack_buff)
            for seg in segment.segments:
                if seg.name == 'start_bracket':
                    balance += 1
                elif seg.name == 'end_bracket':
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
                                anchor=seg, fixes=[
                                    LintFix(
                                        'create', seg,
                                        self.make_whitespace(' ' * (-indent_diff), seg.pos_marker)
                                    )
                                ]
                            )
                        elif indent_diff > 0:
                            # Is it all whitespace before the bracket on this line?
                            prev_segs_on_line = [
                                elem for elem in segment.segments
                                if elem.pos_marker.line_no == seg.pos_marker.line_no
                                and elem.pos_marker.line_pos < seg.pos_marker.line_pos
                            ]
                            if all(elem.type == 'whitespace' for elem in prev_segs_on_line):
                                # We can move it back, it's all whitespace
                                fixes = (
                                    [LintFix('create', seg, [self.make_whitespace(
                                        with_indent_str, seg.pos_marker.advance_by('\n'))])]
                                    + [LintFix('delete', elem) for elem in prev_segs_on_line]
                                )
                            else:
                                # We have to move it to a newline
                                fixes = [
                                    LintFix(
                                        'create', seg,
                                        [
                                            self.make_newline(pos_marker=seg.pos_marker),
                                            self.make_whitespace(
                                                with_indent_str, seg.pos_marker.advance_by('\n')
                                            )
                                        ]
                                    )
                                ]
                            return LintResult(anchor=seg, fixes=fixes)
                else:
                    raw_stack_buff.append(seg)
        return LintResult()
