""" Standard SQL Linting Rules """

from .crawler import BaseCrawler
from ..parser_2.segments_base import RawSegment


def L001_eval(segment, raw_stack, **kwargs):
    """ We only care about the segment the preceeding segments """
    # We only trigger on newlines
    if segment.raw == '\n' and raw_stack[-1].name == 'whitespace':
        # If we find a newline, which is preceeded by whitespace, then bad
        return raw_stack[-1]
    else:
        return True


def L001_fix(segment, raw_stack, **kwargs):
    """ We only care about the segment the preceeding segments """
    # We only trigger on newlines
    if segment.raw == '\n' and raw_stack[-1].name == 'whitespace':
        # If we find a newline, which is preceeded by whitespace, then bad
        deletions = []
        idx = -1
        while True:
            if raw_stack[idx].name == 'whitespace':
                deletions.append(raw_stack[idx])
                idx -= 1
            else:
                break
        return {'delete': deletions}
    else:
        return {}


L001 = BaseCrawler(
    'L001',
    'Uneccessary trailing whitespace',
    evaluate_function=L001_eval,
    fix_function=L001_fix
)


# L002 - Mixed Tabs and Spaces


def L002_eval(segment, raw_stack, **kwargs):
    # We can only trigger on whitespace which is either
    # preceeded by nothing, a newline, or whitespace then either of the above.
    if segment.name == 'whitespace':
        if ' ' in segment.raw and '\t' in segment.raw:
            if len(raw_stack) == 0 or raw_stack[-1].raw == '\n':
                return False
            elif raw_stack[-1].name == 'whitespace':
                # It's preceeded by more whitespace!
                buff = list(raw_stack)
                while True:
                    # pop something off the end
                    if len(buff) == 0:
                        # Found start of file
                        return False

                    seg = buff.pop()
                    if seg.name == 'whitespace':
                        continue
                    elif seg.raw == '\n':
                        # we're at the start of a line
                        return False
                    else:
                        # We're not at the start of a line
                        break
    return True


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
        if segment.raw.count(' ') % 4 != 0:
            if len(raw_stack) == 0 or raw_stack[-1].raw == '\n':
                return False
    return True


L003 = BaseCrawler(
    'L003',
    'Spaced indent is not a multiple of four',
    evaluate_function=L003_eval
)


# L004 - Indentation is not a multiple of four


def L004_eval(segment, raw_stack, memory, **kwargs):
    # We can only trigger on whitespace which is either
    # preceeded by nothing or a newline.
    indents_seen = memory.get('indents_seen', set())
    if segment.name == 'whitespace':
        if len(raw_stack) == 0 or raw_stack[-1].raw == '\n':
            indents_here = set(segment.raw)
            indents_union = indents_here | indents_seen
            memory['indents_seen'] = indents_union
            if len(indents_union) > 1:
                # We are seeing an indent we haven't seen before and we've seen others before
                return False, memory
            else:
                return True, memory
    return True, memory


L004 = BaseCrawler(
    'L004',
    'Mixed tab/space indentation found in file',
    evaluate_function=L004_eval
)


# L008 - Commas should be followed by a single whitespace unless followed by a comment


def L008_eval(segment, raw_stack, **kwargs):
    """ This is a slightly odd one, because we'll almost always evaluate from a point a few places
    after the problem site """
    # We need at least two segments behind us for this to work
    if len(raw_stack) < 2:
        return True
    else:
        cm1 = raw_stack[-1]
        cm2 = raw_stack[-2]
        if cm2.name == 'comma':
            if cm1.name not in ['whitespace', 'newline']:
                # comma followed by something that isn't whitespace!
                return False
            elif cm1.raw not in ['\n', ' '] and not segment.is_comment:
                return False
    return True


def L008_fix(segment, raw_stack, **kwargs):
    # We need at least two segments behind us for this to work
    if len(raw_stack) < 2:
        return True
    else:
        cm1 = raw_stack[-1]
        cm2 = raw_stack[-2]
        if cm2.name == 'comma':
            if cm1.name not in ['whitespace', 'newline']:
                # comma followed by something that isn't whitespace!
                ws = RawSegment.make(' ', name='whitespace')
                ins = ws(raw=' ', pos_marker=cm1.pos_marker)
                return {'create': [(cm1, ins)]}
            elif cm1.raw not in ['\n', ' '] and not segment.is_comment:
                repl = cm1.__class__(
                    raw=' ',
                    pos_marker=cm1.pos_marker
                )
                return {'edit': [(cm1, repl)]}
    return True


L008 = BaseCrawler(
    'L008',
    'Commas should be followed by a single whitespace, unless followed by a comment',
    evaluate_function=L008_eval,
    fix_function=L008_fix
)

# L009 - Trailing Whitespace


def L009_eval(segment, siblings_post, parent_stack, **kwargs):
    """ We only care about the segment and the siblings which come after it
    for this rule, we discard the others into the kwargs argument """
    if len(siblings_post) > 0:
        # This can only fail on the last segment
        return True
    elif len(segment.segments) > 0:
        # This can only fail on the last base segment
        return True
    elif segment.raw == '\n':
        # If this is the last segment, and it's a newline then we're good
        return True
    else:
        # so this looks like the end of the file, but we
        # need to check that each parent segment is also the last
        file_len = len(parent_stack[0].raw)
        pos = segment.pos_marker.char_pos
        # Does the length of the file, equal the length of the segment plus it's position
        if file_len != pos + len(segment.raw):
            return True

    # No return value here is interpreted as a fail.


L009 = BaseCrawler(
    'L009',
    'Files must end with a trailing newline',
    evaluate_function=L009_eval
)


standard_rule_set = [L001, L002, L003, L004, L008, L009]
