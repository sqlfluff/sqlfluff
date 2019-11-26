"""Implements the base crawler which all the rules are based on.

Crawlers, crawl through the trees returned by the parser and
evaluate particular rules.

The intent is that it should be possible for the rules to be expressed
as simply as possible, with as much of the complexity abstracted away.

The evaluation function should take enough arguments that it can evaluate
the position of the given segment in relation to it's neighbors, and that
the segment which finally "triggers" the error, should be the one that would
be corrected OR if the rule relates to something that is missing, then it
should flag on the segment FOLLOWING, the place that the desired element is
missing.
"""

import logging
from collections import namedtuple

from ..errors import SQLLintError

# The ghost of a rule (mostly used for testing)
RuleGhost = namedtuple('RuleGhost', ['code', 'description'])


class LintResult(object):
    """A class to hold the results of a crawl operation.

    Args:
        anchor (:obj:`BaseSegment`, optional): A segment which represents
            the *position* of the a problem. NB: Each fix will also hold
            it's own reference to position, so this position is mostly for
            alterting the user to where the *problem* is.
        fixes (:obj:`list` of :obj:`LintFix`, optional): An array of any
            fixes which would correct this issue. If not present then it's
            assumed that this issue will have to manually fixed.
        memory (:obj:`dict`, optional): An object which stores any working
            memory for the crawler. The `memory` returned in any `LintResult`
            will be passed as an input to the next segment to be crawled.

    """

    def __init__(self, anchor=None, fixes=None, memory=None):
        # An anchor of none, means no issue
        self.anchor = anchor
        # Fixes might be blank
        self.fixes = fixes or []
        # Memory is passed back in the linting result
        self.memory = memory

    def to_linting_error(self, rule):
        """Convert a linting result to a :exc:`SQLLintError` if appropriate."""
        if self.anchor:
            return SQLLintError(rule=rule, segment=self.anchor, fixes=self.fixes)
        else:
            return None


class LintFix(object):
    """A class to hold a potential fix to a linting violation.

    Args:
        edit_type (:obj:`str`): One of `create`, `edit`, `delete` to indicate
            the kind of fix this represents.
        anchor (:obj:`BaseSegment`): A segment which represents
            the *position* that this fix should be applied at. For deletions
            it represents the segment to delete, for creations it implies the
            position to create at (with the existing element at this position
            to be moved *after* the edit), for an `edit` it implies the segment
            to be replaced.
        edit (:obj:`BaseSegment`, optional): For `edit` and `create` fixes, this
            hold the segment, or iterable of segments to create to replace at the
            given `anchor` point.

    """

    def __init__(self, edit_type, anchor, edit=None):
        if edit_type not in ['create', 'edit', 'delete']:
            raise ValueError("Unexpected edit_type: {0}".format(edit_type))
        self.edit_type = edit_type
        self.anchor = anchor
        self.edit = edit

    def __repr__(self):
        return "<LintFix: {0} @{1}>".format(self.edit_type, self.anchor.pos_marker)


class BaseCrawler(object):
    """The base class for a crawler, of which all rules are derived from.

    Args:
        code (:obj:`str`): The identifier for this rule, used in inclusion
            or exclusion.
        description (:obj:`str`): A human readable description of what this
            rule does. It will be displayed when any violations are found.

    """
    def __init__(self, code, description, **kwargs):
        self.description = description
        self.code = code
        # Any unused kwargs will just be ignored from here.

    def _eval(self, **kwargs):
        """Evaluate this rule against the current context.

        This should indicate whether a linting violation has occured and/or
        whether there is something to remember from this evaluation.

        Note that an evaluate function shoul always accept `**kwargs`, but
        if it relies on any available kwargs, it should explicitly call
        them out at definition.

        Returns:
            :obj:`LintResult` or :obj:`None`.

        The reason that this method is called :meth:`_eval` and not `eval` is
        a bit of a hack with sphinx autodoc, to make it so that the rule
        documentation auto-generates nicely.

        """
        raise NotImplementedError(
            (
                "{0} has not had it's `eval` function defined. This is a problem "
                "with the rule setup."
            ).format(self.__class__.__name__)
        )

    def crawl(self, segment, parent_stack=None, siblings_pre=None, siblings_post=None, raw_stack=None, fix=False, memory=None):
        """Recursively perform the crawl operation on a given segment.

        Returns:
            A tuple of (vs, raw_stack, fixes, memory)

        """
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

        # TODO: Document what options are available to the evaluation function.
        res = self._eval(
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


class RuleSet(object):
    """Class to define a ruleset.

    A rule set is instantiated on module load, but the references
    to each of it's classes are instantiated at runtime. This means
    that configuration values can be passed to those rules live
    and be responsive to any changes in configuration from the
    path that the file is in.

    Rules should be fetched using the :meth:`get_rulelist` command which
    also handles any filtering (i.e. whitelisting and blacklisting).

    New rules should be added to the instance of this class using the
    :meth:`register` decorator. That decorator registers the class, but also
    performs basic type and name-convention checks.

    The code for the rule will be parsed from the name, the description
    from the docstring. The eval function is assumed that it will be
    overriden by the subclass, and the parent class raises an error on
    this function if not overriden.

    """

    def __init__(self, name):
        self.name = name
        self._register = {}

    def register(self, cls):
        """Decorate a class with this to add it to the ruleset.

        .. code-block:: python

           @myruleset.register
           class Rule_L001(BaseCrawler):
               "Description of rule."

               def eval(self, **kwargs):
                   return LintResult()

        We expect that rules are defined as classes with the name `Rule_XXXX`
        where `XXXX` is of the form `LNNN`, where L is a letter (literally L for
        *linting* by default) and N is a three digit number.

        If this receives classes by any other name, then it will raise a
        :exc:`ValueError`.

        """
        elems = cls.__name__.split('_')
        # Validate the name
        if len(elems) != 2 or elems[0] != 'Rule' or len(elems[1]) != 4:
            raise ValueError(
                (
                    "Tried to register rule on set {0!r} with unexpected "
                    "format: {1}"
                ).format(
                    self.name,
                    cls.__name__
                )
            )

        code = elems[1]
        # If the docstring is multiline, then we extract just summary.
        description = cls.__doc__.split('\n')[0]

        # Keep track of the *class* in the register. Don't instantiate yet.
        if code in self._register:
            raise ValueError(
                "Rule {0!r} has already been registered on RuleSet {1!r}!".format(
                    code, self.name))
        self._register[code] = dict(code=code, description=description, cls=cls)

        # Make sure we actually return the original class
        return cls

    def get_rulelist(self, config):
        """Use the config to return the appropriate rules.

        We use the config both for whitelisting and blacklisting, but also
        for configuring the rules given the given config.

        Returns:
            :obj:`list` of instantiated :obj:`BaseCrawler`.

        """
        # default the whitelist to all the rules if not set
        whitelist = config.get('rule_whitelist') or list(self._register.keys())
        blacklist = config.get('rule_blacklist') or []

        whitelisted_unknown_rule_codes = [r for r in whitelist if r not in self._register]
        if any(whitelisted_unknown_rule_codes):
            logging.warning(
                "Tried to whitelist unknown rules: {0!r}".format(
                    whitelisted_unknown_rule_codes))

        blacklisted_unknown_rule_codes = [r for r in blacklist if r not in self._register]
        if any(blacklisted_unknown_rule_codes):
            logging.warning(
                "Tried to blacklist unknown rules: {0!r}".format(
                    blacklisted_unknown_rule_codes))

        keylist = sorted(self._register.keys())
        # First we filter the rules
        keylist = [r for r in keylist if r in whitelist and r not in blacklist]

        # Construct the kwargs for instatiation before we actually do it.
        rule_kwargs = {}
        for k in keylist:
            kwargs = {}
            generic_rule_config = config.get_section('rules')
            specific_rule_config = config.get_section(('rules', self._register[k]['code']))
            if generic_rule_config:
                kwargs.update(generic_rule_config)
            if specific_rule_config:
                kwargs.update(specific_rule_config)
            kwargs['code'] = self._register[k]['code']
            # Allow variable substitution in making the description
            kwargs['description'] = self._register[k]['description'].format(**kwargs)
            rule_kwargs[k] = kwargs

        # Instantiate in the final step
        return [self._register[k]['cls'](**rule_kwargs[k]) for k in keylist]
