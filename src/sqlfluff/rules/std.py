"""Standard SQL Linting Rules."""

from ..parser import RawSegment
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
        if segment.name == 'newline' and len(raw_stack) > 0 and raw_stack[-1].name == 'whitespace':
            # If we find a newline, which is preceeded by whitespace, then bad
            deletions = []
            idx = -1
            while True:
                if raw_stack[idx].name == 'whitespace':
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

        if segment.name == 'whitespace':
            if ' ' in segment.raw and '\t' in segment.raw:
                if len(raw_stack) == 0 or raw_stack[-1].name == 'newline':
                    # We've got a single whitespace at the beginning of a line.
                    # It's got a mix of spaces and tabs. Replace each tab with
                    # a multiple of spaces
                    return construct_response()
                elif raw_stack[-1].name == 'whitespace':
                    # It's preceeded by more whitespace!
                    # We shouldn't worry about correcting those
                    # segments, because those will be caught themselves, but we
                    # do want to collect them together.
                    buff = list(raw_stack)
                    while True:
                        # pop something off the end
                        seg = buff.pop()
                        if seg.name == 'whitespace':
                            if len(buff) == 0:
                                # Found start of file
                                return construct_response()
                            else:
                                continue
                        elif seg.name == 'newline':
                            # we're at the start of a line
                            return construct_response()
                        else:
                            # We're not at the start of a line
                            break


@std_rule_set.register
class Rule_L003(BaseCrawler):
    """Indentation length is not a multiple of {tab_space_size}."""

    def __init__(self, tab_space_size=4, **kwargs):
        """Initialise, extracting the tab size from the config."""
        self.tab_space_size = tab_space_size
        super(Rule_L003, self).__init__(**kwargs)

    def _eval(self, segment, raw_stack, **kwargs):
        """Indentation is not a multiple of a configured value.

        To set the default tab size, set the `tab_space_size` value
        in the appropriate configuration.

        We can only trigger on whitespace which is either
        preceeded by nothing or a newline.
        """
        if segment.name == 'whitespace':
            ws_len = segment.raw.count(' ')
            if ws_len % self.tab_space_size != 0:
                if len(raw_stack) == 0 or raw_stack[-1].name == 'newline':
                    best_len = int(round(ws_len * 1.0 / self.tab_space_size)) * self.tab_space_size
                    return LintResult(
                        anchor=segment,
                        fixes=[LintFix('edit', segment, segment.edit(' ' * best_len))]
                    )


@std_rule_set.register
class Rule_L004(BaseCrawler):
    """Mixed Tab and Space indentation found in file."""

    def _eval(self, segment, raw_stack, memory, **kwargs):
        """Mixed Tab and Space indentation found in file.

        We use the `memory` feature here to keep track of
        what we've seen in the past.

        """
        indents_seen = memory.get('indents_seen', set())
        if segment.name == 'whitespace':
            if len(raw_stack) == 0 or raw_stack[-1].name == 'newline':
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
            if segment.name == 'comma' and cm1.name in ['whitespace', 'newline']:
                return LintResult(anchor=cm1, fixes=[LintFix('delete', cm1)])


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
            WhitespaceSegment = RawSegment.make(' ', name='whitespace')

            if len(segments_since_code) == 0:
                # No whitespace, anchor is the segment AFTER where the whitespace
                # should be.
                anchor = this_segment
                fixes.append(
                    LintFix(
                        'create', this_segment,
                        WhitespaceSegment(raw=' ', pos_marker=this_segment.pos_marker))
                )
            elif len(segments_since_code) > 1:
                # TODO: This is a case we should deal with, but there are probably
                # some cases that SHOULDNT apply here (like comments and newlines)
                # so let's deal with them later
                anchor = None
                pass
            else:
                # We know it's just one thing.
                gap_seg = segments_since_code[-1]
                if gap_seg.raw != ' ':
                    # It's not just a single space
                    anchor = gap_seg
                    fixes.append(
                        LintFix(
                            'edit', gap_seg,
                            WhitespaceSegment(raw=' ', pos_marker=gap_seg.pos_marker))
                    )
                else:
                    # We have just the right amount of whitespace!
                    # Unset our signal.
                    anchor = None
                    pass
            return anchor, fixes

        # anchor is our signal as to whether there's a problem
        anchor = None
        fixes = []

        # The parent stack tells us whether we're in an expression or not.
        if parent_stack and parent_stack[-1].type == 'expression':
            if segment.is_code:
                # This is code, what kind?
                if segment.type in ['binary_operator', 'comparison_operator']:
                    # It's an operator, we can evaluate whitespace before it.
                    anchor, fixes = _handle_previous_segments(
                        memory['since_code'], anchor=segment, this_segment=segment,
                        fixes=fixes)
                else:
                    # It's not an operator, we can evaluate what happened after an
                    # operator if that's the last code we saw.
                    if memory['last_code'] and memory['last_code'].type in ['binary_operator', 'comparison_operator']:
                        # Evaluate whitespace AFTER the operator
                        anchor, fixes = _handle_previous_segments(
                            memory['since_code'], anchor=memory['last_code'],
                            this_segment=segment, fixes=fixes)
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
            return LintResult(anchor=anchor, memory=memory, fixes=fixes)
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
        else:
            cm1 = raw_stack[-1]
            cm2 = raw_stack[-2]
            if cm2.name == 'comma':
                if cm1.name not in ['whitespace', 'newline']:
                    # comma followed by something that isn't whitespace!
                    ws = RawSegment.make(' ', name='whitespace')
                    ins = ws(raw=' ', pos_marker=cm1.pos_marker)
                    return LintResult(anchor=cm1, fixes=[LintFix('create', cm1, ins)])
                elif (cm1.raw != ' ' and cm1.name != 'newline') and not segment.is_comment:
                    repl = cm1.__class__(
                        raw=' ',
                        pos_marker=cm1.pos_marker
                    )
                    return LintResult(anchor=cm1, fixes=[LintFix('edit', cm1, repl)])


@std_rule_set.register
class Rule_L009(BaseCrawler):
    """Files must end with a trailing newline."""

    def _eval(self, segment, siblings_post, parent_stack, **kwargs):
        """Files must end with a trailing newline.

        We only care about the segment and the siblings which come after it
        for this rule, we discard the others into the kwargs argument.

        """
        if len(siblings_post) > 0:
            # This can only fail on the last segment
            return None
        elif len(segment.segments) > 0:
            # This can only fail on the last base segment
            return None
        elif segment.name == 'newline':
            # If this is the last segment, and it's a newline then we're good
            return None
        else:
            # so this looks like the end of the file, but we
            # need to check that each parent segment is also the last
            file_len = len(parent_stack[0].raw)
            pos = segment.pos_marker.char_pos
            # Does the length of the file, equal the length of the segment plus it's position
            if file_len != pos + len(segment.raw):
                return None

        nls = RawSegment.make('\n', name='newline')
        ins = nls(raw='\n', pos_marker=segment.pos_marker.advance_by(segment.raw))
        # We're going to make an edit because otherwise we would never get a match!
        return LintResult(anchor=segment, fixes=[LintFix('edit', segment, [segment, ins])])
