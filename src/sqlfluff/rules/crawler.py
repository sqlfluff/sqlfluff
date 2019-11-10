""" implements the base crawler which all the rules are based on """

# Crawlers, crawl through the trees returned by the parser and
# evaluate particular rules.
# The intent is that it should be possible for the rules to be expressed
# as simply as possible, with as much of the complexity abstracted away.

# The evaluation function should take enough arguments that it can evaluate
# the position of the given segment in relation to it's neighbors, and that
# the segment which finally "triggers" the error, should be the one that would
# be corrected OR if the rule relates to something that is missing, then it
# should flag on the segment FOLLOWING, the place that the desired element is
# missing.

from collections import namedtuple

from ..errors import SQLLintError

# The ghost of a rule (mostly used for testing)
RuleGhost = namedtuple('RuleGhost', ['code', 'description'])


class LintResult(object):
    def __init__(self, anchor=None, fixes=None, memory=None):
        # An anchor of none, means no issue
        self.anchor = anchor
        # Fixes might be blank
        self.fixes = fixes or []
        # Memory is passed back in the linting result
        self.memory = memory

    def to_linting_error(self, rule):
        if self.anchor:
            return SQLLintError(rule=rule, segment=self.anchor, fixes=self.fixes)
        else:
            return None


class LintFix(object):
    def __init__(self, edit_type, anchor, edit=None):
        if edit_type not in ['create', 'edit', 'delete']:
            raise ValueError("Unexpected edit_type: {0}".format(edit_type))
        self.edit_type = edit_type
        self.anchor = anchor
        self.edit = edit

    def __repr__(self):
        return "<LintFix: {0} @{1}>".format(self.edit_type, self.anchor.pos_marker)


class BaseCrawler(object):
    def __init__(self, code, description, evaluate_function=None, fix_function=None):
        # NB not sure how crawlers should be instantiated yet.
        self.description = description
        self.code = code
        # evaluation functions should return a boolean and optionally a fixed version of the given segment.
        # True means that we PASS. False means that we have a problem
        # Evaluate functions can be simple, but best they should return a LintResult
        # which also records any fixes to be made.
        self.evaluate_function = evaluate_function

    def crawl(self, segment, parent_stack=None, siblings_pre=None, siblings_post=None, raw_stack=None, fix=False, memory=None):
        # parent stack should be a tuple if it exists

        # crawlers, should evalutate on segments FIRST, before evaulating on their
        # children. They should also return a list of violations.

        # If FIX is true, then we should start again at the start of the file.
        # TODO: Work out how to do this!

        parent_stack = parent_stack or tuple([])
        raw_stack = raw_stack or tuple([])
        siblings_post = siblings_post or tuple([])
        siblings_pre = siblings_pre or tuple([])
        memory = memory or {}
        vs = []

        res = self.evaluate_function(
            segment=segment, parent_stack=parent_stack,
            siblings_pre=siblings_pre, siblings_post=siblings_post,
            raw_stack=raw_stack, memory=memory)

        if res is None:
            # Assume this means no problems (also means no memory)
            pass
        elif isinstance(res, LintResult):
            # Extract any memory
            memory = res.memory
            lerr = res.to_linting_error(rule=self)
            if lerr:
                vs.append(lerr)
            # We need fixes and to be in fix mode to invoke this...
            if res.fixes and fix:
                # Return straight away so the fixes can be applied.
                return vs, raw_stack, res.fixes, memory
        else:
            raise TypeError(
                "Got unexpected result [{0!r}] back from linting rule: {1!r}".format(res, self.code))

        # The raw stack only keeps track of the previous raw segments
        if len(segment.segments) == 0:
            raw_stack += tuple([segment])
        # Parent stack keeps track of all the parent segments
        parent_stack += tuple([segment])

        for idx, child in enumerate(segment.segments):
            dvs, raw_stack, fixes, memory = self.crawl(
                child, parent_stack=parent_stack,
                siblings_pre=segment.segments[:idx],
                siblings_post=segment.segments[idx + 1:],
                raw_stack=raw_stack, fix=fix, memory=memory)
            vs += dvs

            if fixes and fix:
                # If we have a fix then return immediately so it can be applied
                return vs, raw_stack, fixes, memory

        # If we get here, then we're not returning any fixes (even if they've been
        # generated). So blank that out here.
        return vs, raw_stack, [], memory
