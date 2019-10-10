""" Standard SQL Linting Rules """

from .crawler import BaseCrawler


def L001_eval(segment, raw_stack, **kwargs):
    """ We only care about the segment the preceeding segments """
    # We only trigger on newlines
    if segment.raw == '\n' and raw_stack[-1].name == 'whitespace':
        # If we find a newline, which is preceeded by whitespace, then bad
        return False
    else:
        return True


L001 = BaseCrawler(
    'L001',
    'Uneccessary trailing whitespace',
    evaluate_function=L001_eval
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


standard_rule_set = [L001, L009]
