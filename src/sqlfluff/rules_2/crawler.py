""" implements the base crawler which all the rules are based on """

# Crawlers, crawl through the trees returned by the parser and
# evaluate particular rules.
# The intent is that it should be possible for the rules to be epxressed
# as simply as possible, with as much of the complexity abstracted away.

# The evaluation function should take enough arguments that it can evaluate
# the position of the given segment in relation to it's neighbors, and that
# the segment which finally "triggers" the error, should be the one that would
# be corrected OR if the rule relates to something that is missing, then it
# should flag on the segment FOLLOWING, the place that the desired element is
# missing.

from ..errors import SQLBaseError, SQLLintError


class BaseCrawler(object):
    def __init__(self, code, description, evaluate_function):
        # NB not sure how crawlers should be instantiated yet.
        self.description = description
        self.code = code
        # evaluation functions should return a boolean and optionally a fixed version of the given segment.
        # True means that we PASS. False means that we have a problem
        self.evaluate_function = evaluate_function

    def crawl(self, segment, parent_stack=None, siblings_pre=None, siblings_post=None, fix=False):
        # parent stack should be a tuple if it exists

        # crawlers, should evalutate on segments FIRST, before evaulating on their
        # children. They should also return a list of violations.

        # If FIX is true, then we should start again at the start of the file.
        # TODO: Work out how to do this!

        parent_stack = parent_stack or tuple([])
        siblings_post = siblings_post or tuple([])
        siblings_pre = siblings_pre or tuple([])

        res = self.evaluate_function(
            segment=segment, parent_stack=parent_stack,
            siblings_pre=siblings_pre, siblings_post=siblings_post)

        vs = []
        if isinstance(res, bool) or res is None:
            if not res:  # NB: This triggers on False, but also None
                # We're appending strings for now. We can do better
                # vs.append("Found Violation of {0} at {1}".format(self.code, segment))
                vs.append(SQLLintError(rule=self, segment=segment))
        elif res:
            # If we've got anything else, then there was a problem
            if isinstance(res, SQLBaseError):
                # Maybe the crawler implements it's own erro handling
                vs.append(res)
            else:
                raise ValueError("Unexpected response from a crawler: {0}".format(res))

        parent_stack = parent_stack + tuple([segment])
        for idx, child in enumerate(segment.segments):
            vs += self.crawl(child, parent_stack=parent_stack,
                             siblings_pre=segment.segments[:idx], siblings_post=segment.segments[idx + 1:],
                             fix=fix)

        return vs


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
