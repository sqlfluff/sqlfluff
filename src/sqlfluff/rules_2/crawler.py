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

from collections import namedtuple

from ..errors import SQLBaseError, SQLLintError


# The ghost of a rule (mostly used for testing)
RuleGhost = namedtuple('RuleGhost', ['code', 'description'])


class BaseCrawler(object):
    def __init__(self, code, description, evaluate_function, fix_function=None):
        # NB not sure how crawlers should be instantiated yet.
        self.description = description
        self.code = code
        # evaluation functions should return a boolean and optionally a fixed version of the given segment.
        # True means that we PASS. False means that we have a problem
        self.evaluate_function = evaluate_function
        # Fix functions should return results as a dict
        # of the form {'create':[],'edit':[],'delete':[]}
        self.fix_function = fix_function

    def crawl(self, segment, parent_stack=None, siblings_pre=None, siblings_post=None, raw_stack=None, fix=False):
        # parent stack should be a tuple if it exists

        # crawlers, should evalutate on segments FIRST, before evaulating on their
        # children. They should also return a list of violations.

        # If FIX is true, then we should start again at the start of the file.
        # TODO: Work out how to do this!

        parent_stack = parent_stack or tuple([])
        raw_stack = raw_stack or tuple([])
        siblings_post = siblings_post or tuple([])
        siblings_pre = siblings_pre or tuple([])

        res = self.evaluate_function(
            segment=segment, parent_stack=parent_stack,
            siblings_pre=siblings_pre, siblings_post=siblings_post,
            raw_stack=raw_stack)

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

        fix_edits = None
        if fix and vs and self.fix_function:
            # There must be a violation to invoke a fix
            fix_edits = self.fix_function(
                segment=segment, parent_stack=parent_stack,
                siblings_pre=siblings_pre, siblings_post=siblings_post,
                raw_stack=raw_stack)
            if fix_edits:
                # If we made any fixes, we should return immediately
                return vs, raw_stack, fix_edits
            else:
                # TODO: May log nicely and warn here...
                pass

        # The raw stack only keeps track of the previous raw segments
        if len(segment.segments) == 0:
            raw_stack += tuple([segment])
        # Parent stack keeps track of all the parent segments
        parent_stack += tuple([segment])

        for idx, child in enumerate(segment.segments):
            dvs, raw_stack, fix_edits = self.crawl(
                child, parent_stack=parent_stack,
                siblings_pre=segment.segments[:idx],
                siblings_post=segment.segments[idx + 1:],
                raw_stack=raw_stack, fix=fix)
            vs += dvs

            if fix_edits:
                # If we have a fix then return immediately so it can be applied
                return vs, raw_stack, fix_edits

        # NB If we're returning at this stage, the assumption is that
        # there aren't any fixes to apply
        return vs, raw_stack, fix_edits
