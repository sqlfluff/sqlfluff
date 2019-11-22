""" Standard SQL Linting Rules """

from ..parser import RawSegment
from .crawler import BaseCrawler, LintFix, LintResult

# TODO: Make this multiple configurable somewhere in
# the dialect.
TAB_SPACE_SIZE = 4


def L001_eval(segment, raw_stack, **kwargs):
    """ We only care about the segment the preceeding segments """
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


L001 = BaseCrawler(
    'L001',
    'Uneccessary trailing whitespace',
    evaluate_function=L001_eval
)


# L002 - Mixed Tabs and Spaces


def L002_eval(segment, raw_stack, **kwargs):
    # We can only trigger on whitespace which is either
    # preceeded by nothing, a newline, or whitespace then either of the above.

    def construct_response():
        """ Make this generic so we can call it from a few places """
        return LintResult(
            anchor=segment,
            fixes=[
                LintFix(
                    'edit', segment,
                    segment.edit(segment.raw.replace('\t', ' ' * TAB_SPACE_SIZE)))
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


L002 = BaseCrawler(
    'L002',
    'Mixture of tabs and spaces in indentation',
    evaluate_function=L002_eval
)


# L003 - Indentation is not a multiple of four


def L003_eval(segment, raw_stack, **kwargs):
    # We can only trigger on whitespace which is either
    # preceeded by nothing or a newline.
    if segment.name == 'whitespace':
        ws_len = segment.raw.count(' ')
        if ws_len % TAB_SPACE_SIZE != 0:
            if len(raw_stack) == 0 or raw_stack[-1].name == 'newline':
                best_len = int(round(ws_len * 1.0 / TAB_SPACE_SIZE)) * TAB_SPACE_SIZE
                return LintResult(
                    anchor=segment,
                    fixes=[LintFix('edit', segment, segment.edit(' ' * best_len))]
                )


L003 = BaseCrawler(
    'L003',
    'Spaced indent is not a multiple of {0}'.format(TAB_SPACE_SIZE),
    evaluate_function=L003_eval
)


# L004 - Mixed tab/space indentation found in file


def L004_eval(segment, raw_stack, memory, **kwargs):
    # We can only trigger on whitespace which is either
    # preceeded by nothing or a newline.
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


L004 = BaseCrawler(
    'L004',
    'Mixed tab/space indentation found in file',
    evaluate_function=L004_eval
)


# L005 - Commas should not have whitespace directly before them


def L005_fix(segment, raw_stack, **kwargs):
    # We need at least one segment behind us for this to work
    if len(raw_stack) >= 1:
        cm1 = raw_stack[-1]
        if segment.name == 'comma' and cm1.name in ['whitespace', 'newline']:
            return LintResult(anchor=cm1, fixes=[LintFix('delete', cm1)])


L005 = BaseCrawler(
    'L005',
    'Commas should not have whitespace directly before them',
    evaluate_function=L005_fix
)


# L006 - Operators should be surrounded by a single whitespace


def L006_fix(segment, memory, parent_stack, **kwargs):
    # We use the memory to keep track of whitespace up to now, and
    # whether the last code segment was an operator or not.

    # TODO: Check that the memory works in NESTED expressions

    # anchor is our signal as to whether there's a problem
    anchor = None
    fixes = []
    WhitespaceSegment = RawSegment.make(' ', name='whitespace')
    # The parent stack tells us whether we're in an expression or not.
    if parent_stack and parent_stack[-1].type == 'expression':
        if segment.is_code:
            # This is code, what kind?
            if segment.type in ['binary_operator', 'comparison_operator']:
                # It's an operator, we can evaluate whitespace before it.
                anchor = segment
                if len(memory['since_code']) == 0:
                    fixes.append(
                        LintFix(
                            'create', segment,
                            WhitespaceSegment(raw=' ', pos_marker=segment.pos_marker))
                    )
                elif len(memory['since_code']) > 1:
                    # TODO: This is a case we should deal with, but there are probably
                    # some cases that SHOULDNT apply here (like comments and newlines)
                    # so let's deal with them later
                    anchor = None
                    pass
                else:
                    # We know it's just one thing.
                    gap_seg = memory['since_code'][-1]
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
            else:
                # It's not an operator, we can evaluate what happened after an
                # operator if that's the last code we saw.
                if memory['last_code'] and memory['last_code'].type in ['binary_operator', 'comparison_operator']:
                    # Evaluate whitespace AFTER the operator
                    if len(memory['since_code']) == 0:
                        fixes.append(
                            LintFix(
                                'create', segment,
                                WhitespaceSegment(raw=' ', pos_marker=segment.pos_marker))
                        )
                    elif len(memory['since_code']) > 1:
                        # TODO: This is a case we should deal with, but there are probably
                        # some cases that SHOULDNT apply here (like comments and newlines)
                        # so let's deal with them later
                        anchor = None
                        pass
                    else:
                        # We know it's just one thing.
                        gap_seg = memory['since_code'][-1]
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


L006 = BaseCrawler(
    'L006',
    'Operators should be surrounded by a single whitespace',
    evaluate_function=L006_fix
)


# L008 - Commas should be followed by a single whitespace unless followed by a comment


def L008_fix(segment, raw_stack, **kwargs):
    """ This is a slightly odd one, because we'll almost always evaluate from a point a few places
    after the problem site """
    # We need at least two segments behind us for this to work
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


L008 = BaseCrawler(
    'L008',
    'Commas should be followed by a single whitespace, unless followed by a comment',
    evaluate_function=L008_fix
)

# L009 - Trailing Whitespace


def L009_eval(segment, siblings_post, parent_stack, **kwargs):
    """ We only care about the segment and the siblings which come after it
    for this rule, we discard the others into the kwargs argument """
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


L009 = BaseCrawler(
    'L009',
    'Files must end with a trailing newline',
    evaluate_function=L009_eval
)


standard_rule_set = [L001, L002, L003, L004, L005, L006, L008, L009]
