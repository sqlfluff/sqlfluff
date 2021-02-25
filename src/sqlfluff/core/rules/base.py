"""Implements the base crawler which all the rules are based on.

Crawlers, crawl through the trees returned by the parser and
evaluate particular rules.

The intent is that it should be possible for the rules to be expressed
as simply as possible, with as much of the complexity abstracted away.

The evaluation function should take enough arguments that it can evaluate
the position of the given segment in relation to its neighbors, and that
the segment which finally "triggers" the error, should be the one that would
be corrected OR if the rule relates to something that is missing, then it
should flag on the segment FOLLOWING, the place that the desired element is
missing.
"""

import copy
import logging
import re
from collections import namedtuple

from sqlfluff.core.parser import RawSegment, KeywordSegment, BaseSegment, SymbolSegment
from sqlfluff.core.errors import SQLLintError

# The ghost of a rule (mostly used for testing)
RuleGhost = namedtuple("RuleGhost", ["code", "description"])

# Instantiate the rules logger
rules_logger = logging.getLogger("sqlfluff.rules")


class RuleLoggingAdapter(logging.LoggerAdapter):
    """A LoggingAdapter for rules which adds the code of the rule to it."""

    def process(self, msg, kwargs):
        """Add the code element to the logging message before emit."""
        return "[%s] %s" % (self.extra["code"], msg), kwargs


class LintResult:
    """A class to hold the results of a crawl operation.

    Args:
        anchor (:obj:`BaseSegment`, optional): A segment which represents
            the *position* of the a problem. NB: Each fix will also hold
            its own reference to position, so this position is mostly for
            alerting the user to where the *problem* is.
        fixes (:obj:`list` of :obj:`LintFix`, optional): An array of any
            fixes which would correct this issue. If not present then it's
            assumed that this issue will have to manually fixed.
        memory (:obj:`dict`, optional): An object which stores any working
            memory for the crawler. The `memory` returned in any `LintResult`
            will be passed as an input to the next segment to be crawled.
        description (:obj:`str`, optional): A description of the problem
            identified as part of this result. This will override the
            description of the rule as what gets reported to the user
            with the problem if provided.

    """

    def __init__(self, anchor=None, fixes=None, memory=None, description=None):
        # An anchor of none, means no issue
        self.anchor = anchor
        # Fixes might be blank
        self.fixes = fixes or []
        # When instantiating the result, we filter any fixes which are "trivial".
        self.fixes = [f for f in self.fixes if not f.is_trivial()]
        # Memory is passed back in the linting result
        self.memory = memory
        # store a description_override for later
        self.description = description

    def to_linting_error(self, rule):
        """Convert a linting result to a :exc:`SQLLintError` if appropriate."""
        if self.anchor:
            # Allow description override from the LintResult
            description = self.description or rule.description
            return SQLLintError(
                rule=rule,
                segment=self.anchor,
                fixes=self.fixes,
                description=description,
            )
        else:
            return None


class LintFix:
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
        if edit_type not in ["create", "edit", "delete"]:
            raise ValueError("Unexpected edit_type: {0}".format(edit_type))
        self.edit_type = edit_type
        self.anchor = anchor
        # Coerce to list
        if isinstance(edit, BaseSegment):
            edit = [edit]
        # Copy all the elements of edit to stop contamination.
        # We're about to start stripping the position markers
        # of some of the elements and we don't want to end up
        # stripping the positions of the original elements of
        # the parsed structure.
        self.edit = copy.deepcopy(edit)
        if self.edit:
            # Strip position markers of anything enriched, otherwise things can get blurry
            for seg in self.edit:
                seg.pos_marker = seg.pos_marker.strip()
        # Once stripped, we shouldn't replace any markers because
        # later code may rely on them being accurate, which we
        # can't guarantee with edits.

    def is_trivial(self):
        """Return true if the fix is trivial.

        Trivial edits are:
        - Anything of zero length.
        - Any edits which result in themselves.

        Removing these makes the routines which process fixes much faster.
        """
        if self.edit_type == "create":
            if isinstance(self.edit, BaseSegment):
                if len(self.edit.raw) == 0:
                    return True
            elif all(len(elem.raw) == 0 for elem in self.edit):
                return True
        elif self.edit_type == "edit" and self.edit == self.anchor:
            return True
        return False

    def __repr__(self):
        if self.edit_type == "delete":
            detail = "delete:{0!r}".format(self.anchor.raw)
        elif self.edit_type in ("edit", "create"):
            if hasattr(self.edit, "raw"):
                new_detail = self.edit.raw
            else:
                new_detail = "".join(s.raw for s in self.edit)

            if self.edit_type == "edit":
                detail = "edt:{0!r}->{1!r}".format(self.anchor.raw, new_detail)
            else:
                detail = "create:{0!r}".format(new_detail)
        else:
            detail = ""
        return "<LintFix: {0} @{1} {2}>".format(
            self.edit_type, self.anchor.pos_marker, detail
        )

    def __eq__(self, other):
        """Compare equality with another fix.

        A fix is equal to another if is in the same place (position), with the
        same type and (if appropriate) the same edit values.

        """
        if not self.edit_type == other.edit_type:
            return False
        if not self.anchor == other.anchor:
            return False
        if not self.edit == other.edit:
            return False
        return True


class BaseCrawler:
    """The base class for a crawler, of which all rules are derived from.

    Args:
        code (:obj:`str`): The identifier for this rule, used in inclusion
            or exclusion.
        description (:obj:`str`): A human readable description of what this
            rule does. It will be displayed when any violations are found.

    """

    _works_on_unparsable = True

    def __init__(self, code, description, **kwargs):
        self.description = description
        self.code = code
        # kwargs represents the config passed to the crawler. Add all kwargs as class attributes
        # so they can be accessed in rules which inherit from this class
        for key, value in kwargs.items():
            self.__dict__[key] = value

        # We also define a custom logger here, which also includes the code
        # of the rule in the logging.
        self.logger = RuleLoggingAdapter(rules_logger, {"code": code})
        # Validate that declared configuration options exist
        try:
            for keyword in self.config_keywords:
                if keyword not in kwargs.keys():
                    raise ValueError(
                        (
                            "Unrecognized config '{0}' for Rule {1}. If this "
                            "is a new option, please add it to "
                            "`default_config.cfg`"
                        ).format(keyword, code)
                    )
        except AttributeError:
            self.logger.info("No config_keywords defined for {0}".format(code))

    def _eval(self, **kwargs):
        """Evaluate this rule against the current context.

        This should indicate whether a linting violation has occurred and/or
        whether there is something to remember from this evaluation.

        Note that an evaluate function should always accept `**kwargs`, but
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
                "{0} has not had its `eval` function defined. This is a problem "
                "with the rule setup."
            ).format(self.__class__.__name__)
        )

    def crawl(
        self,
        segment,
        dialect,
        parent_stack=None,
        siblings_pre=None,
        siblings_post=None,
        raw_stack=None,
        memory=None,
    ):
        """Recursively perform the crawl operation on a given segment.

        Returns:
            A tuple of (vs, raw_stack, fixes, memory)

        """
        # parent stack should be a tuple if it exists

        # crawlers, should evaluate on segments FIRST, before evaluating on their
        # children. They should also return a list of violations.

        parent_stack = parent_stack or ()
        raw_stack = raw_stack or ()
        siblings_post = siblings_post or ()
        siblings_pre = siblings_pre or ()
        memory = memory or {}
        vs = []
        fixes = []

        # First, check whether we're looking at an unparsable and whether
        # this rule will still operate on that.
        if not self._works_on_unparsable and segment.is_type("unparsable"):
            # Abort here if it doesn't. Otherwise we'll get odd results.
            return vs, raw_stack, [], memory

        # TODO: Document what options are available to the evaluation function.
        try:
            res = self._eval(
                segment=segment,
                parent_stack=parent_stack,
                siblings_pre=siblings_pre,
                siblings_post=siblings_post,
                raw_stack=raw_stack,
                memory=memory,
                dialect=dialect,
            )
        # Any exception at this point would halt the linter and
        # cause the user to get no results
        except Exception as e:
            self.logger.critical(
                f"Applying rule {self.code} threw an Exception: {e}", exc_info=True
            )
            vs.append(
                SQLLintError(
                    rule=self,
                    segment=segment,
                    fixes=[],
                    description=(
                        f"""Unexpected exception: {str(e)};
                        Could you open an issue at https://github.com/sqlfluff/sqlfluff/issues ?
                        You can ignore this exception for now, by adding '--noqa: {self.code}' at the end
                        of line {segment.pos_marker.line_no}
                        """
                    ),
                )
            )
            return vs, raw_stack, fixes, memory

        if res is None:
            # Assume this means no problems (also means no memory)
            pass
        elif isinstance(res, LintResult):
            # Extract any memory
            memory = res.memory
            lerr = res.to_linting_error(rule=self)
            if lerr:
                vs.append(lerr)
            fixes += res.fixes
        elif isinstance(res, list) and all(
            isinstance(elem, LintResult) for elem in res
        ):
            # Extract any memory from the *last* one, assuming
            # it was the last to be added
            memory = res[-1].memory
            for elem in res:
                lerr = elem.to_linting_error(rule=self)
                if lerr:
                    vs.append(lerr)
                fixes += elem.fixes
        else:
            raise TypeError(
                "Got unexpected result [{0!r}] back from linting rule: {1!r}".format(
                    res, self.code
                )
            )

        # The raw stack only keeps track of the previous raw segments
        if len(segment.segments) == 0:
            raw_stack += (segment,)
        # Parent stack keeps track of all the parent segments
        parent_stack += (segment,)

        for idx, child in enumerate(segment.segments):
            dvs, raw_stack, child_fixes, memory = self.crawl(
                segment=child,
                parent_stack=parent_stack,
                siblings_pre=segment.segments[:idx],
                siblings_post=segment.segments[idx + 1 :],
                raw_stack=raw_stack,
                memory=memory,
                dialect=dialect,
            )
            vs += dvs
            fixes += child_fixes
        return vs, raw_stack, fixes, memory

    # HELPER METHODS --------

    @staticmethod
    def filter_meta(segments, keep_meta=False):
        """Filter the segments to non-meta.

        Or optionally the opposite if keep_meta is True.
        """
        buff = []
        for elem in segments:
            if elem.is_meta is keep_meta:
                buff.append(elem)
        return tuple(buff)

    @classmethod
    def get_parent_of(cls, segment, root_segment):
        """Return the segment immediately containing segment.

        NB: This is recursive.

        Args:
            segment: The segment to look for.
            root_segment: Some known parent of the segment
                we're looking for (although likely not the
                direct parent in question).

        """
        if segment in root_segment.segments:
            return root_segment
        elif root_segment.segments:
            # try each of the subsegments
            for sub in root_segment.segments:
                p = cls.get_parent_of(segment, sub)
                if p:
                    return p
        # Not directly in the segment and
        # no subsegments to check. Return None.
        return None

    @classmethod
    def make_whitespace(cls, raw, pos_marker):
        """Make a whitespace segment."""
        WhitespaceSegment = RawSegment.make(" ", name="whitespace", type="whitespace")
        return WhitespaceSegment(raw=raw, pos_marker=pos_marker)

    @classmethod
    def make_newline(cls, pos_marker, raw=None):
        """Make a newline segment."""
        # Default the newline to \n
        raw = raw or "\n"
        nls = RawSegment.make("\n", name="newline", type="newline")
        return nls(raw=raw, pos_marker=pos_marker)

    @classmethod
    def make_keyword(cls, raw, pos_marker):
        """Make a keyword segment."""
        # For the name of the segment, we force the string to lowercase.
        kws = KeywordSegment.make(raw.lower())
        # At the moment we let the rule dictate *case* here.
        return kws(raw=raw, pos_marker=pos_marker)

    @classmethod
    def make_symbol(cls, raw, pos_marker, seg_type, name=None):
        """Make a symbol segment."""
        # For the name of the segment, we force the string to lowercase.
        symbol_seg = SymbolSegment.make(
            raw.lower(), name=name or seg_type, type=seg_type
        )
        # At the moment we let the rule dictate *case* here.
        return symbol_seg(raw=raw, pos_marker=pos_marker)


class RuleSet:
    """Class to define a ruleset.

    A rule set is instantiated on module load, but the references
    to each of its classes are instantiated at runtime. This means
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

    def __init__(self, name, config_info):
        self.name = name
        self.config_info = config_info
        self._register = {}

    def _validate_config_options(self, config, rule=None):
        """Ensure that all config options are valid.

        Config options can also be checked for a specific rule e.g L010.
        """
        rule_config = config.get_section("rules")
        for config_name, info_dict in self.config_info.items():
            config_option = (
                rule_config.get(config_name)
                if not rule
                else rule_config.get(rule).get(config_name)
            )
            valid_options = info_dict.get("validation")
            if (
                valid_options
                and config_option not in valid_options
                and config_option is not None
            ):
                raise ValueError(
                    (
                        "Invalid option '{0}' for {1} configuration. Must be one of {2}"
                    ).format(
                        config_option,
                        config_name,
                        valid_options,
                    )
                )

    @property
    def valid_rule_name_regex(self):
        """Defines the accepted pattern for rule names.

        The first group captures the plugin name (optional), which
        must be capitalized.
        The second group captures the rule code.

        Examples of valid rule names:
        * Rule_PluginName_L001
        * Rule_L001
        """
        return re.compile(r"Rule_?([A-Z]{1}[a-zA-Z]+)?_([A-Z][0-9]{3})")

    def register(self, cls, plugin=None):
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
        rule_name_match = self.valid_rule_name_regex.match(cls.__name__)
        # Validate the name
        if not rule_name_match:
            raise ValueError(
                (
                    "Tried to register rule on set {0!r} with unexpected "
                    "format: {1}, format should be: Rule_PluginName_L123 (for plugins) "
                    "or Rule_L123 (for core rules)."
                ).format(self.name, cls.__name__)
            )

        plugin_name, code = rule_name_match.groups()
        # If the docstring is multiline, then we extract just summary.
        description = cls.__doc__.split("\n")[0]

        if plugin_name:
            code = f"{plugin_name}_{code}"

        # Keep track of the *class* in the register. Don't instantiate yet.
        if code in self._register:
            raise ValueError(
                "Rule {0!r} has already been registered on RuleSet {1!r}!".format(
                    code, self.name
                )
            )
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
        # Validate all generic rule configs
        self._validate_config_options(config)
        # default the whitelist to all the rules if not set
        whitelist = config.get("rule_whitelist") or list(self._register.keys())
        blacklist = config.get("rule_blacklist") or []

        whitelisted_unknown_rule_codes = [
            r for r in whitelist if r not in self._register
        ]
        if any(whitelisted_unknown_rule_codes):
            rules_logger.warning(
                "Tried to whitelist unknown rules: {0!r}".format(
                    whitelisted_unknown_rule_codes
                )
            )

        blacklisted_unknown_rule_codes = [
            r for r in blacklist if r not in self._register
        ]
        if any(blacklisted_unknown_rule_codes):
            rules_logger.warning(
                "Tried to blacklist unknown rules: {0!r}".format(
                    blacklisted_unknown_rule_codes
                )
            )

        keylist = sorted(self._register.keys())
        # First we filter the rules
        keylist = [r for r in keylist if r in whitelist and r not in blacklist]

        # Construct the kwargs for instantiation before we actually do it.
        rule_kwargs = {}
        for k in keylist:
            kwargs = {}
            generic_rule_config = config.get_section("rules")
            specific_rule_config = config.get_section(
                ("rules", self._register[k]["code"])
            )
            if generic_rule_config:
                kwargs.update(generic_rule_config)
            if specific_rule_config:
                # Validate specific rule config before adding
                self._validate_config_options(config, self._register[k]["code"])
                kwargs.update(specific_rule_config)
            kwargs["code"] = self._register[k]["code"]
            # Allow variable substitution in making the description
            kwargs["description"] = self._register[k]["description"].format(**kwargs)
            rule_kwargs[k] = kwargs

        # Instantiate in the final step
        return [self._register[k]["cls"](**rule_kwargs[k]) for k in keylist]

    def copy(self):
        """Return a copy of self with a separate register."""
        new_ruleset = copy.copy(self)
        new_ruleset._register = self._register.copy()
        return new_ruleset
