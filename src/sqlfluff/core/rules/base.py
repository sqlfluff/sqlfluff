"""Implements the base rule class.

Rules crawl through the trees returned by the parser and evaluate particular
rules.

The intent is that it should be possible for the rules to be expressed
as simply as possible, with as much of the complexity abstracted away.

The evaluation function should take enough arguments that it can evaluate
the position of the given segment in relation to its neighbors, and that
the segment which finally "triggers" the error, should be the one that would
be corrected OR if the rule relates to something that is missing, then it
should flag on the segment FOLLOWING, the place that the desired element is
missing.
"""

import bdb
import copy
import fnmatch
import logging
import pathlib
import regex
from typing import Iterable, Optional, List, Set, Tuple, Union, Any
from collections import namedtuple
from dataclasses import dataclass

from sqlfluff.core.linter import LintedFile
from sqlfluff.core.parser import BaseSegment, RawSegment
from sqlfluff.core.dialects import Dialect
from sqlfluff.core.errors import SQLLintError
from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFile

# The ghost of a rule (mostly used for testing)
RuleGhost = namedtuple("RuleGhost", ["code", "description"])

# Instantiate the rules logger
rules_logger = logging.getLogger("sqlfluff.rules")

linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")


class RuleLoggingAdapter(logging.LoggerAdapter):
    """A LoggingAdapter for rules which adds the code of the rule to it."""

    def process(self, msg, kwargs):
        """Add the code element to the logging message before emit."""
        return "[{}] {}".format(self.extra["code"], msg), kwargs


class LintResult:
    """A class to hold the results of a rule evaluation.

    Args:
        anchor (:obj:`BaseSegment`, optional): A segment which represents
            the *position* of the a problem. NB: Each fix will also hold
            its own reference to position, so this position is mostly for
            alerting the user to where the *problem* is.
        fixes (:obj:`list` of :obj:`LintFix`, optional): An array of any
            fixes which would correct this issue. If not present then it's
            assumed that this issue will have to manually fixed.
        memory (:obj:`dict`, optional): An object which stores any working
            memory for the rule. The `memory` returned in any `LintResult`
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

    def to_linting_error(self, rule) -> Optional[SQLLintError]:
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
            hold the segment, or iterable of segments to create or replace at the
            given `anchor` point.

    """

    def __init__(
        self,
        edit_type: str,
        anchor: BaseSegment,
        edit: Optional[Iterable[BaseSegment]] = None,
    ) -> None:
        if edit_type not in (
            "create_before",
            "create_after",
            "replace",
            "delete",
        ):  # pragma: no cover
            raise ValueError(f"Unexpected edit_type: {edit_type}")
        self.edit_type = edit_type
        if not anchor:  # pragma: no cover
            raise ValueError("Fixes must provide an anchor.")
        self.anchor = anchor
        self.edit: Optional[List[BaseSegment]] = None
        if edit is not None:
            # Coerce edit iterable to list
            edit = list(edit)
            # Copy all the elements of edit to stop contamination.
            # We're about to start stripping the position markers
            # off some of the elements and we don't want to end up
            # stripping the positions of the original elements of
            # the parsed structure.
            self.edit = copy.deepcopy(edit)
            # Check that any edits don't have a position marker set.
            # We should rely on realignment to make position markers.
            # Strip position markers of anything enriched, otherwise things can get blurry
            for seg in self.edit:
                if seg.pos_marker:
                    # Developer warning.
                    rules_logger.debug(
                        "Developer Note: Edit segment found with preset position marker. "
                        "These should be unset and calculated later."
                    )
                    seg.pos_marker = None  # type: ignore
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
        if self.edit_type in ("create_before", "create_after"):
            if isinstance(self.edit, BaseSegment):
                if len(self.edit.raw) == 0:  # pragma: no cover TODO?
                    return True
            elif all(len(elem.raw) == 0 for elem in self.edit):
                return True
        elif self.edit_type == "replace" and self.edit == self.anchor:
            return True  # pragma: no cover TODO?
        return False

    def __repr__(self):
        if self.edit_type == "delete":
            detail = f"delete:{self.anchor.raw!r}"
        elif self.edit_type in ("replace", "create_before", "create_after"):
            if hasattr(self.edit, "raw"):
                new_detail = self.edit.raw  # pragma: no cover TODO?
            else:
                new_detail = "".join(s.raw for s in self.edit)

            if self.edit_type == "replace":
                detail = f"edt:{self.anchor.raw!r}->{new_detail!r}"
            else:
                detail = f"create:{new_detail!r}"
        else:
            detail = ""  # pragma: no cover TODO?
        return "<LintFix: {} @{} {}>".format(
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
        return True  # pragma: no cover TODO?

    @classmethod
    def delete(cls, anchor_segment: BaseSegment) -> "LintFix":
        """Delete supplied anchor segment."""
        return cls("delete", anchor_segment)

    @classmethod
    def replace(
        cls, anchor_segment: BaseSegment, edit_segments: Iterable[BaseSegment]
    ) -> "LintFix":
        """Replace supplied anchor segment with the edit segments."""
        return cls("replace", anchor_segment, edit_segments)

    @classmethod
    def create_before(
        cls, anchor_segment: BaseSegment, edit_segments: Iterable[BaseSegment]
    ) -> "LintFix":
        """Create edit segments before the supplied anchor segment."""
        return cls("create_before", anchor_segment, edit_segments)

    @classmethod
    def create_after(
        cls, anchor_segment: BaseSegment, edit_segments: Iterable[BaseSegment]
    ) -> "LintFix":
        """Create edit segments after the supplied anchor segment."""
        return cls("create_after", anchor_segment, edit_segments)


EvalResultType = Union[LintResult, List[LintResult], None]


@dataclass
class RuleContext:
    """Class for holding the context passed to rule eval functions."""

    segment: BaseSegment
    parent_stack: Tuple[BaseSegment, ...]
    siblings_pre: Tuple[BaseSegment, ...]
    siblings_post: Tuple[BaseSegment, ...]
    raw_stack: Tuple[RawSegment, ...]
    memory: Any
    dialect: Dialect
    path: Optional[pathlib.Path]
    templated_file: Optional[TemplatedFile]


class BaseRule:
    """The base class for a rule.

    Args:
        code (:obj:`str`): The identifier for this rule, used in inclusion
            or exclusion.
        description (:obj:`str`): A human readable description of what this
            rule does. It will be displayed when any violations are found.

    """

    _check_docstring = True
    _works_on_unparsable = True
    targets_templated = False

    def __init__(self, code, description, **kwargs):
        self.description = description
        self.code = code
        # kwargs represents the config passed to the rule. Add all kwargs as class attributes
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
                            "Unrecognized config '{}' for Rule {}. If this "
                            "is a new option, please add it to "
                            "`default_config.cfg`"
                        ).format(keyword, code)
                    )
        except AttributeError:
            self.logger.info(f"No config_keywords defined for {code}")

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Evaluate this rule against the current context.

        This should indicate whether a linting violation has occurred and/or
        whether there is something to remember from this evaluation.

        Note that an evaluate function should always accept `**kwargs`, but
        if it relies on any available kwargs, it should explicitly call
        them out at definition.

        Returns:
            :obj:`LintResult`, list of :obj:`LintResult` or :obj:`None`.

        The reason that this method is called :meth:`_eval` and not `eval` is
        a bit of a hack with sphinx autodoc, to make it so that the rule
        documentation auto-generates nicely.

        """
        raise NotImplementedError(
            (
                "{} has not had its `eval` function defined. This is a problem "
                "with the rule setup."
            ).format(self.__class__.__name__)
        )  # pragma: no cover

    def crawl(
        self,
        segment,
        ignore_mask,
        dialect,
        parent_stack=None,
        siblings_pre=None,
        siblings_post=None,
        raw_stack=None,
        memory=None,
        fname=None,
        templated_file: Optional["TemplatedFile"] = None,
    ):
        """Recursively perform the crawl operation on a given segment.

        Returns:
            A tuple of (vs, raw_stack, fixes, memory)

        """
        # parent stack should be a tuple if it exists

        # Rules should evaluate on segments FIRST, before evaluating on their
        # children. They should also return a list of violations.

        parent_stack = parent_stack or ()
        raw_stack = raw_stack or ()
        siblings_post = siblings_post or ()
        siblings_pre = siblings_pre or ()
        memory = memory or {}
        vs: List[SQLLintError] = []
        fixes: List[LintFix] = []

        # First, check whether we're looking at an unparsable and whether
        # this rule will still operate on that.
        if not self._works_on_unparsable and segment.is_type("unparsable"):
            # Abort here if it doesn't. Otherwise we'll get odd results.
            return vs, raw_stack, [], memory

        # TODO: Document what options are available to the evaluation function.
        try:
            res = self._eval(
                context=RuleContext(
                    segment=segment,
                    parent_stack=parent_stack,
                    siblings_pre=siblings_pre,
                    siblings_post=siblings_post,
                    raw_stack=raw_stack,
                    memory=memory,
                    dialect=dialect,
                    path=pathlib.Path(fname) if fname else None,
                    templated_file=templated_file,
                )
            )
        except (bdb.BdbQuit, KeyboardInterrupt):  # pragma: no cover
            raise
        # Any exception at this point would halt the linter and
        # cause the user to get no results
        except Exception as e:
            self.logger.critical(
                f"Applying rule {self.code} threw an Exception: {e}", exc_info=True
            )
            exception_line, _ = segment.pos_marker.source_position()
            vs.append(
                SQLLintError(
                    rule=self,
                    segment=segment,
                    fixes=[],
                    description=(
                        f"""Unexpected exception: {str(e)};
                        Could you open an issue at https://github.com/sqlfluff/sqlfluff/issues ?
                        You can ignore this exception for now, by adding '--noqa: {self.code}' at the end
                        of line {exception_line}
                        """
                    ),
                )
            )
            return vs, raw_stack, fixes, memory

        new_lerrs = []
        new_fixes = []

        def _process_lint_result(res):
            self.discard_unsafe_fixes(res, templated_file)
            lerr = res.to_linting_error(rule=self)
            ignored = False
            if lerr:
                if ignore_mask:
                    filtered = LintedFile.ignore_masked_violations([lerr], ignore_mask)
                    if not filtered:
                        lerr = None
                        ignored = True
            if lerr:
                new_lerrs.append(lerr)
            if not ignored:
                new_fixes.extend(res.fixes)

        if res is None:
            # Assume this means no problems (also means no memory)
            pass
        elif isinstance(res, LintResult):
            # Extract any memory
            memory = res.memory
            _process_lint_result(res)
        elif isinstance(res, list) and all(
            isinstance(elem, LintResult) for elem in res
        ):
            # Extract any memory from the *last* one, assuming
            # it was the last to be added
            memory = res[-1].memory
            for elem in res:
                _process_lint_result(elem)
        else:  # pragma: no cover
            raise TypeError(
                "Got unexpected result [{!r}] back from linting rule: {!r}".format(
                    res, self.code
                )
            )

        for lerr in new_lerrs:
            self.logger.debug("!! Violation Found: %r", lerr.description)
        for fix in new_fixes:
            self.logger.debug("!! Fix Proposed: %r", fix)

        # Consume the new results
        vs += new_lerrs
        fixes += new_fixes

        # The raw stack only keeps track of the previous raw segments
        if len(segment.segments) == 0:
            raw_stack += (segment,)
        # Parent stack keeps track of all the parent segments
        parent_stack += (segment,)

        for idx, child in enumerate(segment.segments):
            dvs, raw_stack, child_fixes, memory = self.crawl(
                segment=child,
                ignore_mask=ignore_mask,
                parent_stack=parent_stack,
                siblings_pre=segment.segments[:idx],
                siblings_post=segment.segments[idx + 1 :],
                raw_stack=raw_stack,
                memory=memory,
                dialect=dialect,
                fname=fname,
                templated_file=templated_file,
            )
            vs += dvs
            fixes += child_fixes
        return vs, raw_stack, fixes, memory

    # HELPER METHODS --------

    def is_final_segment(self, context: RuleContext) -> bool:
        """Is the current segment the final segment in the parse tree."""
        if len(self.filter_meta(context.siblings_post)) > 0:
            # This can only fail on the last segment
            return False
        elif len(context.segment.segments) > 0:
            # This can only fail on the last base segment
            return False
        elif context.segment.is_meta:
            # We can't fail on a meta segment
            return False
        else:
            # We know we are at a leaf of the tree but not necessarily at the end of the tree.
            # Therefore we look backwards up the parent stack and ask if any of the parent segments
            # have another non-meta child segment after the current one.
            child_segment = context.segment
            for parent_segment in context.parent_stack[::-1]:
                possible_children = [
                    s for s in parent_segment.segments if not s.is_meta
                ]
                if len(possible_children) > possible_children.index(child_segment) + 1:
                    return False
                child_segment = parent_segment

        return True

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
    def get_parent_of(cls, segment, root_segment):  # pragma: no cover TODO?
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

    @staticmethod
    def matches_target_tuples(seg: BaseSegment, target_tuples: List[Tuple[str, str]]):
        """Does the given segment match any of the given type tuples."""
        if seg.name in [elem[1] for elem in target_tuples if elem[0] == "name"]:
            return True
        elif seg.is_type(*[elem[1] for elem in target_tuples if elem[0] == "type"]):
            return True
        return False

    @staticmethod
    def discard_unsafe_fixes(
        lint_result: LintResult, templated_file: Optional[TemplatedFile]
    ):
        """Remove (discard) LintResult fixes if they are "unsafe".

        By removing its fixes, a LintResult will still be reported, but it
        will be treated as _unfixable_.
        """
        if not lint_result.fixes or not templated_file:
            return

        # Get the set of slices touched by any of the fixes.
        fix_slices: Set[RawFileSlice] = set()
        for fix in lint_result.fixes:
            if fix.anchor:
                fix_slices.update(
                    templated_file.raw_slices_spanning_source_slice(
                        fix.anchor.pos_marker.source_slice
                    )
                )

        # Compute the set of block IDs affected by the fixes. If it's more than
        # one, discard the fixes. Rationale: Fixes that span block boundaries
        # may corrupt the file, e.g. by moving code in or out of a template
        # loop.
        block_info = templated_file.raw_slice_block_info
        fix_block_ids = set(block_info.block_ids[slice_] for slice_ in fix_slices)
        if len(fix_block_ids) > 1:
            linter_logger.info(
                "      * Discarding fixes that span blocks: %s",
                lint_result.fixes,
            )
            lint_result.fixes = []
            return

        # If the fixes touch a literal-only loop, discard the fixes.
        # Rationale: Fixes to a template loop that contains only literals are:
        # - Difficult to correctly back to source code, so there's a risk of
        #   accidentally "expanding" the loop body if we apply them.
        # - Highly unusual (In practice, templated loops in SQL are usually for
        #   expanding the same code using different column names, types, etc.,
        #   in which case the loop body contains template variables.
        for block_id in fix_block_ids:
            if block_id in block_info.literal_only_loops:
                linter_logger.info(
                    "      * Discarding fixes to literal-only loop: %s",
                    lint_result.fixes,
                )
                lint_result.fixes = []
                return


class RuleSet:
    """Class to define a ruleset.

    A rule set is instantiated on module load, but the references
    to each of its classes are instantiated at runtime. This means
    that configuration values can be passed to those rules live
    and be responsive to any changes in configuration from the
    path that the file is in.

    Rules should be fetched using the :meth:`get_rulelist` command which
    also handles any filtering (i.e. allowlisting and denylisting).

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
                        "Invalid option '{}' for {} configuration. Must be one of {}"
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
        return regex.compile(r"Rule_?([A-Z]{1}[a-zA-Z]+)?_([A-Z][0-9]{3})")

    def register(self, cls, plugin=None):
        """Decorate a class with this to add it to the ruleset.

        .. code-block:: python

           @myruleset.register
           class Rule_L001(BaseRule):
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
        if not rule_name_match:  # pragma: no cover
            raise ValueError(
                (
                    "Tried to register rule on set {!r} with unexpected "
                    "format: {}, format should be: Rule_PluginName_L123 (for plugins) "
                    "or Rule_L123 (for core rules)."
                ).format(self.name, cls.__name__)
            )

        plugin_name, code = rule_name_match.groups()
        # If the docstring is multiline, then we extract just summary.
        description = cls.__doc__.split("\n")[0]

        if plugin_name:
            code = f"{plugin_name}_{code}"

        # Keep track of the *class* in the register. Don't instantiate yet.
        if code in self._register:  # pragma: no cover
            raise ValueError(
                "Rule {!r} has already been registered on RuleSet {!r}!".format(
                    code, self.name
                )
            )
        self._register[code] = dict(code=code, description=description, cls=cls)

        # Make sure we actually return the original class
        return cls

    def _expand_config_rule_glob_list(self, glob_list: List[str]) -> List[str]:
        """Expand a list of rule globs into a list of rule codes.

        Returns:
            :obj:`list` of :obj:`str` rule codes.

        """
        expanded_glob_list = []
        for r in glob_list:
            expanded_glob_list.extend(
                [
                    x
                    for x in fnmatch.filter(self._register, r)
                    if x not in expanded_glob_list
                ]
            )

        return expanded_glob_list

    def get_rulelist(self, config) -> List[BaseRule]:
        """Use the config to return the appropriate rules.

        We use the config both for allowlisting and denylisting, but also
        for configuring the rules given the given config.

        Returns:
            :obj:`list` of instantiated :obj:`BaseRule`.

        """
        # Validate all generic rule configs
        self._validate_config_options(config)
        # default the allowlist to all the rules if not set
        allowlist = config.get("rule_allowlist") or list(self._register.keys())
        denylist = config.get("rule_denylist") or []

        allowlisted_unknown_rule_codes = [
            r for r in allowlist if not fnmatch.filter(self._register, r)
        ]
        if any(allowlisted_unknown_rule_codes):
            rules_logger.warning(
                "Tried to allowlist unknown rules: {!r}".format(
                    allowlisted_unknown_rule_codes
                )
            )

        denylisted_unknown_rule_codes = [
            r for r in denylist if not fnmatch.filter(self._register, r)
        ]
        if any(denylisted_unknown_rule_codes):  # pragma: no cover
            rules_logger.warning(
                "Tried to denylist unknown rules: {!r}".format(
                    denylisted_unknown_rule_codes
                )
            )

        keylist = sorted(self._register.keys())

        # First we expand the allowlist and denylist globs
        expanded_allowlist = self._expand_config_rule_glob_list(allowlist)
        expanded_denylist = self._expand_config_rule_glob_list(denylist)

        # Then we filter the rules
        keylist = [
            r for r in keylist if r in expanded_allowlist and r not in expanded_denylist
        ]

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
