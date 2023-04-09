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
from dataclasses import dataclass
import fnmatch
from itertools import chain
import logging
import pathlib
import regex
import re
from typing import (
    cast,
    Iterable,
    Optional,
    List,
    Set,
    Tuple,
    Union,
    Any,
    Dict,
    Type,
    DefaultDict,
    Iterator,
)
from collections import namedtuple, defaultdict

from sqlfluff.core.config import FluffConfig, split_comma_separated_string

from sqlfluff.core.linter import LintedFile, NoQaDirective
from sqlfluff.core.parser import BaseSegment, PositionMarker, RawSegment
from sqlfluff.core.dialects import Dialect
from sqlfluff.core.errors import SQLLintError, SQLFluffUserError
from sqlfluff.core.parser.segments.base import SourceFix
from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.crawlers import BaseCrawler
from sqlfluff.core.rules.config_info import get_config_info
from sqlfluff.core.templaters.base import RawFileSlice, TemplatedFile

# The ghost of a rule (mostly used for testing)
RuleGhost = namedtuple("RuleGhost", ["code", "name", "description"])

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
            the *position* of the problem. NB: Each fix will also hold
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
        source (:obj:`str`, optional): A string identifier for what
            generated the result. Within larger libraries like reflow this
            can be useful for tracking where a result came from.

    """

    def __init__(
        self,
        anchor: Optional[BaseSegment] = None,
        fixes: Optional[List["LintFix"]] = None,
        memory=None,
        description: Optional[str] = None,
        source: Optional[str] = None,
    ):
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
        # Optional code for where the result came from
        self.source: str = source or ""

    def __repr__(self):
        if not self.anchor:
            return "LintResult(<empty>)"
        # The "F" at the end is short for "fixes", to indicate how many there are.
        fix_coda = f"+{len(self.fixes)}F" if self.fixes else ""
        if self.description:
            if self.source:
                return (
                    f"LintResult({self.description} [{self.source}]"
                    f": {self.anchor}{fix_coda})"
                )
            return f"LintResult({self.description}: {self.anchor}{fix_coda})"
        return f"LintResult({self.anchor}{fix_coda})"

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
        edit_type (:obj:`str`): One of `create_before`, `create_after`,
            `replace`, `delete` to indicate the kind of fix this represents.
        anchor (:obj:`BaseSegment`): A segment which represents
            the *position* that this fix should be applied at. For deletions
            it represents the segment to delete, for creations it implies the
            position to create at (with the existing element at this position
            to be moved *after* the edit), for a `replace` it implies the
            segment to be replaced.
        edit (iterable of :obj:`BaseSegment`, optional): For `replace` and
            `create` fixes, this holds the iterable of segments to create
            or replace at the given `anchor` point.
        source (iterable of :obj:`BaseSegment`, optional): For `replace` and
            `create` fixes, this holds iterable of segments that provided
            code. IMPORTANT: The linter uses this to prevent copying material
            from templated areas.
    """

    def __init__(
        self,
        edit_type: str,
        anchor: BaseSegment,
        edit: Optional[Iterable[BaseSegment]] = None,
        source: Optional[Iterable[BaseSegment]] = None,
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
            # Strip position markers of anything enriched, otherwise things can get
            # blurry
            for seg in self.edit:
                if seg.pos_marker:
                    # Developer warning.
                    rules_logger.debug(
                        "Developer Note: Edit segment found with preset position "
                        "marker. These should be unset and calculated later."
                    )
                    seg.pos_marker = None
            # Once stripped, we shouldn't replace any markers because
            # later code may rely on them being accurate, which we
            # can't guarantee with edits.
        self.source = [seg for seg in source if seg.pos_marker] if source else []

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

    def is_just_source_edit(self) -> bool:
        """Return whether this a valid source only edit."""
        return (
            self.edit_type == "replace"
            and self.edit is not None
            and len(self.edit) == 1
            and self.edit[0].raw == self.anchor.raw
        )

    def __repr__(self):
        if self.edit_type == "delete":
            detail = f"delete:{self.anchor.raw!r}"
        elif self.edit_type in ("replace", "create_before", "create_after"):
            if hasattr(self.edit, "raw"):
                new_detail = self.edit.raw  # pragma: no cover TODO?
            else:
                new_detail = "".join(s.raw for s in self.edit)

            if self.edit_type == "replace":
                if self.is_just_source_edit():
                    detail = f"src-edt:{self.edit[0].source_fixes!r}"
                else:
                    detail = f"edt:{self.anchor.raw!r}->{new_detail!r}"
            else:
                detail = f"create:{new_detail!r}"
        else:
            detail = ""  # pragma: no cover TODO?
        return (
            f"<LintFix: {self.edit_type} {self.anchor.get_type()}"
            f"@{self.anchor.pos_marker} {detail}>"
        )

    def __eq__(self, other):
        """Compare equality with another fix.

        A fix is equal to another if is in the same place (position), with the
        same type and (if appropriate) the same edit values.

        """
        if not self.edit_type == other.edit_type:
            return False
        # For checking anchor equality, first check types.
        if not self.anchor.class_types == other.anchor.class_types:
            return False
        # If types match, check uuids to see if they're the same original segment.
        if self.anchor.uuid != other.anchor.uuid:
            return False
        # Then compare edits, here we only need to check the raw and source
        # fixes (positions are meaningless).
        # Only do this if we have edits.
        if self.edit:
            # 1. Check lengths
            if len(self.edit) != len(other.edit):
                return False  # pragma: no cover
            # 2. Zip and compare
            for a, b in zip(self.edit, other.edit):
                # Check raws
                if a.raw != b.raw:
                    return False
                # Check source fixes
                if a.source_fixes != b.source_fixes:
                    return False
        return True

    @classmethod
    def delete(cls, anchor_segment: BaseSegment) -> "LintFix":
        """Delete supplied anchor segment."""
        return cls("delete", anchor_segment)

    @classmethod
    def replace(
        cls,
        anchor_segment: BaseSegment,
        edit_segments: Iterable[BaseSegment],
        source: Optional[Iterable[BaseSegment]] = None,
    ) -> "LintFix":
        """Replace supplied anchor segment with the edit segments."""
        return cls("replace", anchor_segment, edit_segments, source)

    @classmethod
    def create_before(
        cls,
        anchor_segment: BaseSegment,
        edit_segments: Iterable[BaseSegment],
        source: Optional[Iterable[BaseSegment]] = None,
    ) -> "LintFix":
        """Create edit segments before the supplied anchor segment."""
        return cls(
            "create_before",
            anchor_segment,
            edit_segments,
            source,
        )

    @classmethod
    def create_after(
        cls,
        anchor_segment: BaseSegment,
        edit_segments: Iterable[BaseSegment],
        source: Optional[Iterable[BaseSegment]] = None,
    ) -> "LintFix":
        """Create edit segments after the supplied anchor segment."""
        return cls(
            "create_after",
            anchor_segment,
            edit_segments,
            source,
        )

    def get_fix_slices(
        self, templated_file: TemplatedFile, within_only: bool
    ) -> Set[RawFileSlice]:
        """Returns slices touched by the fix."""
        # Goal: Find the raw slices touched by the fix. Two cases, based on
        # edit type:
        # 1. "delete", "replace": Raw slices touching the anchor segment.
        # 2. "create_before", "create_after": Raw slices encompassing the two
        #    character positions surrounding the insertion point (**NOT** the
        #    whole anchor segment, because we're not *touching* the anchor
        #    segment, we're inserting **RELATIVE** to it.
        assert self.anchor.pos_marker, f"Anchor missing position marker: {self.anchor}"
        anchor_slice = self.anchor.pos_marker.templated_slice
        templated_slices = [anchor_slice]

        # If "within_only" is set for a "create_*" fix, the slice should only
        # include the area of code "within" the area of insertion, not the other
        # side.
        adjust_boundary = 1 if not within_only else 0
        if self.edit_type == "create_before":
            # Consider the first position of the anchor segment and the
            # position just before it.
            templated_slices = [
                slice(anchor_slice.start - 1, anchor_slice.start + adjust_boundary),
            ]
        elif self.edit_type == "create_after":
            # Consider the last position of the anchor segment and the
            # character just after it.
            templated_slices = [
                slice(anchor_slice.stop - adjust_boundary, anchor_slice.stop + 1),
            ]
        elif (
            self.edit_type == "replace"
            and self.anchor.pos_marker.source_slice.stop
            == self.anchor.pos_marker.source_slice.start
        ):
            # We're editing something with zero size in the source. This means
            # it likely _didn't exist_ in the source and so can be edited safely.
            # We return an empty set because this edit doesn't touch anything
            # in the source.
            return set()
        elif (
            self.edit_type == "replace"
            and all(edit.is_type("raw") for edit in cast(List[RawSegment], self.edit))
            and all(edit._source_fixes for edit in cast(List[RawSegment], self.edit))
        ):
            # As an exception to the general rule about "replace" fixes (where
            # they're only safe if they don't touch a templated section at all),
            # source-only fixes are different. This clause handles that exception.

            # So long as the fix is *purely* source-only we can assume that the
            # rule has done the relevant due diligence on what it's editing in
            # the source and just yield the source slices directly.

            # More complicated fixes that are a blend or source and templated
            # fixes are currently not supported but this (mostly because they've
            # not arisen yet!), so further work would be required to support them
            # elegantly.
            rules_logger.debug("Source only fix.")
            source_edit_slices = [
                fix.source_slice
                # We can assume they're all raw and all have source fixes, because we
                # check that above.
                for fix in chain.from_iterable(
                    cast(List[SourceFix], edit._source_fixes)
                    for edit in cast(List[RawSegment], self.edit)
                )
            ]

            if len(source_edit_slices) > 1:  # pragma: no cover
                raise NotImplementedError(
                    "Unable to handle multiple source only slices."
                )
            return set(
                templated_file.raw_slices_spanning_source_slice(source_edit_slices[0])
            )

        # TRICKY: For creations at the end of the file, there won't be an
        # existing slice. In this case, the function adds file_end_slice to the
        # result, as a sort of placeholder or sentinel value. We pass a literal
        # slice for "file_end_slice" so that later in this function, the LintFix
        # is interpreted as literal code. Otherwise, it could be interpreted as
        # a fix to *templated* code and incorrectly discarded.
        return self._raw_slices_from_templated_slices(
            templated_file,
            templated_slices,
            file_end_slice=RawFileSlice("", "literal", -1),
        )

    def has_template_conflicts(self, templated_file: TemplatedFile) -> bool:
        """Based on the fix slices, should we discard the fix?"""
        # Check for explicit source fixes.
        # TODO: This doesn't account for potentially more complicated source fixes.
        # If we're replacing a single segment with many *and* doing source fixes
        # then they will be discarded here as unsafe.
        if self.edit_type == "replace" and self.edit and len(self.edit) == 1:
            edit: BaseSegment = self.edit[0]
            if edit.raw == self.anchor.raw and edit.source_fixes:
                return False
        # Given fix slices, check for conflicts.
        check_fn = all if self.edit_type in ("create_before", "create_after") else any
        fix_slices = self.get_fix_slices(templated_file, within_only=False)
        result = check_fn(fs.slice_type == "templated" for fs in fix_slices)
        if result or not self.source:
            return result

        # Fix slices were okay. Now check template safety of the "source" field.
        templated_slices = [
            cast(PositionMarker, source.pos_marker).templated_slice
            for source in self.source
        ]
        raw_slices = self._raw_slices_from_templated_slices(
            templated_file, templated_slices
        )
        return any(fs.slice_type == "templated" for fs in raw_slices)

    @staticmethod
    def _raw_slices_from_templated_slices(
        templated_file: TemplatedFile,
        templated_slices: List[slice],
        file_end_slice: Optional[RawFileSlice] = None,
    ) -> Set[RawFileSlice]:
        raw_slices: Set[RawFileSlice] = set()
        for templated_slice in templated_slices:
            try:
                raw_slices.update(
                    templated_file.raw_slices_spanning_source_slice(
                        templated_file.templated_slice_to_source_slice(templated_slice)
                    )
                )
            except (IndexError, ValueError):
                # These errors will happen with "create_before" at the beginning
                # of the file or "create_after" at the end of the file. By
                # default, we ignore this situation. If the caller passed
                # "file_end_slice", add that to the result. In effect,
                # file_end_slice serves as a placeholder or sentinel value.
                if file_end_slice is not None:
                    raw_slices.add(file_end_slice)
        return raw_slices


EvalResultType = Union[LintResult, List[LintResult], None]


class RuleMetaclass(type):
    """The metaclass for rules.

    This metaclass provides provides auto-enrichment of the
    rule docstring so that examples, groups, aliases and
    names are added.

    The reason we enrich the docstring is so that it can be
    picked up by autodoc and all be displayed in the sqlfluff
    docs.
    """

    # Precompile the regular expressions
    _doc_search_regex = re.compile(
        "(\\s{4}\\*\\*Anti-pattern\\*\\*|\\s{4}\\.\\. note::|"
        "\\s\\s{4}\\*\\*Configuration\\*\\*)",
        flags=re.MULTILINE,
    )
    _valid_classname_regex = regex.compile(r"Rule_?([A-Z]{1}[a-zA-Z]+)?_([A-Z0-9]{4})")
    _valid_rule_name_regex = regex.compile(r"[a-z][a-z\.\_]+")

    def _populate_code_and_description(mcs, name, class_dict):
        """Extract and validate the rule code & description.

        We expect that rules are defined as classes with the name `Rule_XXXX`
        where `XXXX` is of the form `LLNN`, where L is a letter and N is a
        two digit number. For backward compatibility we also still support
        the legacy format of LNNN i.e. a single letter and three digit number.

        The two letters should be indicative of the grouping and focus of
        the rule. e.g. capitalisation rules have the code CP for CaPitalisation.

        If this receives classes by any other name, then it will raise a
        :exc:`ValueError`.
        """
        rule_name_match = mcs._valid_classname_regex.match(name)
        # Validate the name
        if not rule_name_match:  # pragma: no cover
            raise SQLFluffUserError(
                f"Tried to define rule class with "
                f"unexpected format: {name}. Format should be: "
                "'Rule_PluginName_LL23' (for plugins) or "
                "`Rule_LL23` (for core rules)."
            )

        plugin_name, code = rule_name_match.groups()
        # If the docstring is multiline, then we extract just summary.
        description = class_dict["__doc__"].replace("``", "'").split("\n")[0]
        if plugin_name:
            code = f"{plugin_name}_{code}"

        class_dict["code"] = code
        class_dict["description"] = description

        return class_dict

    def _populate_docstring(mcs, name, class_dict):
        """Enrich the docstring in the class_dict.

        This takes the various defined values in the BaseRule class
        and uses them to populate documentation in the final class
        docstring so that it can be displayed in the sphinx docs.
        """
        # Ensure that there _is_ a docstring.
        assert (
            "__doc__" in class_dict
        ), f"Tried to define rule {name!r} without docstring."

        # Build up a buffer of entries to add to the docstring.
        fix_docs = (
            "    This rule is ``sqlfluff fix`` compatible.\n\n"
            if class_dict.get("is_fix_compatible", False)
            else ""
        )
        name_docs = (
            f"    **Name**: ``{class_dict['name']}``\n\n"
            if class_dict.get("name", "")
            else ""
        )
        alias_docs = (
            ("    **Aliases**: ``" + "``, ``".join(class_dict["aliases"]) + "``\n\n")
            if class_dict.get("aliases", [])
            else ""
        )
        groups_docs = (
            ("    **Groups**: ``" + "``, ``".join(class_dict["groups"]) + "``\n\n")
            if class_dict.get("groups", [])
            else ""
        )

        config_docs = ""
        if class_dict.get("config_keywords", []):
            config_docs = "\n    **Configuration**\n"
            config_info = get_config_info()
            for keyword in sorted(class_dict["config_keywords"]):
                try:
                    info_dict = config_info[keyword]
                except KeyError:  # pragma: no cover
                    raise KeyError(
                        "Config value {!r} for rule {} is not configured in "
                        "`config_info`.".format(keyword, name)
                    )
                config_docs += "\n    * ``{}``: {}".format(
                    keyword, info_dict["definition"]
                )
                if (
                    config_docs[-1] != "."
                    and config_docs[-1] != "?"
                    and config_docs[-1] != "\n"
                ):
                    config_docs += "."
                if "validation" in info_dict:
                    config_docs += " Must be one of ``{}``.".format(
                        info_dict["validation"]
                    )
            config_docs += "\n"

        all_docs = fix_docs + name_docs + alias_docs + groups_docs + config_docs
        # Modify the docstring using the search regex.
        class_dict["__doc__"] = mcs._doc_search_regex.sub(
            f"\n\n{all_docs}\n\n\\1", class_dict["__doc__"], count=1
        )
        # If the inserted string is not now in the docstring - append it on
        # the end. This just means the regex didn't find a better place to
        # put it.
        if all_docs not in class_dict["__doc__"]:
            class_dict["__doc__"] += f"\n\n{all_docs}"

        # Return the modified class_dict
        return class_dict

    def __new__(mcs, name, bases, class_dict):
        """Generate a new class."""
        # Optionally, groups may be inherited. At this stage of initialisation
        # they won't have been. Check parent classes if they exist.
        # names, aliases and description are less appropriate to inherit.
        # NOTE: This applies in particular to CP02, which inherits all groups
        # from CP01. If we don't do this, those groups don't show in the docs.
        for base in reversed(bases):
            if "groups" in class_dict:
                break
            elif base.groups:
                class_dict["groups"] = base.groups
                break

        class_dict = mcs._populate_docstring(mcs, name, class_dict)
        # Don't try and infer code and description for the base class
        if bases:
            class_dict = mcs._populate_code_and_description(mcs, name, class_dict)
        # Validate rule names
        rule_name = class_dict.get("name", "")
        if rule_name:
            if not mcs._valid_rule_name_regex.match(rule_name):
                raise SQLFluffUserError(
                    f"Tried to define rule with unexpected "
                    f"name format: {rule_name}. Rule names should be lowercase "
                    "and snake_case with optional `.` characters to indicate "
                    "a namespace or grouping. e.g. `layout.spacing`."
                )

        # Use the stock __new__ method now we've adjusted the docstring.
        return super().__new__(mcs, name, bases, class_dict)


class BaseRule(metaclass=RuleMetaclass):
    """The base class for a rule.

    Args:
        code (:obj:`str`): The identifier for this rule, used in inclusion
            or exclusion.
        description (:obj:`str`): A human readable description of what this
            rule does. It will be displayed when any violations are found.

    """

    _check_docstring = True
    _works_on_unparsable = True
    _adjust_anchors = False
    targets_templated = False
    # Some fix routines do their own checking for whether their fixes
    # are safe around templated elements. For those - the default
    # safety checks might be inappropriate. In those cases, set
    # template_safe_fixes to True.
    template_safe_fixes = False

    # Config settings supported for this rule.
    # See config_info.py for supported values.
    config_keywords: List[str] = []
    # Lint loop / crawl behavior. When appropriate, rules can (and should)
    # override these values to make linting faster.
    crawl_behaviour: BaseCrawler
    # Rules can override this to specify "post". "Post" rules are those that are
    # not expected to trigger any downstream rules, e.g. capitalization fixes.
    # They run on two occasions:
    # - On the first pass of the main phase
    # - In a second linter pass after the main phase
    lint_phase = "main"
    # Groups attribute to be overwritten.
    groups: Tuple[str, ...] = ()
    # Name attribute to be overwritten.
    # NOTE: for backward compatibility we should handle the case
    # where no name is set gracefully.
    name: str = ""
    # Optional set of aliases for the rule. Most often used for old codes which
    # referred to this rule.
    aliases: Tuple[str, ...] = ()

    # NOTE: code and description are provided here as hints, but should not
    # be set directly. They are set automatically by the metaclass based on
    # the class _name_ when defined.
    code: str
    description: str

    # Should we document this rule as fixable? Used by the metaclass to add
    # a line to the docstring.
    is_fix_compatible = False

    # Add comma separated string to Base Rule to ensure that it uses the same
    # Configuration that is defined in the Config.py file
    split_comma_separated_string = staticmethod(split_comma_separated_string)

    def __init__(self, code, description, **kwargs):
        self.description = description
        self.code = code
        # kwargs represents the config passed to the rule. Add all kwargs as class
        # attributes so they can be accessed in rules which inherit from this class
        for key, value in kwargs.items():
            self.__dict__[key] = value

        # We also define a custom logger here, which also includes the code
        # of the rule in the logging.
        self.logger = RuleLoggingAdapter(rules_logger, {"code": code})
        # Validate that declared configuration options exist
        for keyword in self.config_keywords:
            if keyword not in kwargs.keys():
                raise ValueError(
                    (
                        "Unrecognized config '{}' for Rule {}. If this "
                        "is a new option, please add it to "
                        "`default_config.cfg`"
                    ).format(keyword, code)
                )

    @classmethod
    def get_config_ref(cls):
        """Return the config lookup ref for this rule.

        If a `name` is defined, it's the name - otherwise the code.

        The name is a much more understandable reference and so makes config
        files more readable. For backward compatibility however we also support
        the rule code for those without names.
        """
        return cls.name if cls.name else cls.code

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
        tree: BaseSegment,
        dialect: Dialect,
        fix: bool,
        templated_file: Optional["TemplatedFile"],
        ignore_mask: List[NoQaDirective],
        fname: Optional[str],
        config: FluffConfig,
    ) -> Tuple[List[SQLLintError], Tuple[RawSegment, ...], List[LintFix], Any]:
        """Run the rule on a given tree.

        Returns:
            A tuple of (vs, raw_stack, fixes, memory)

        """
        root_context = RuleContext(
            dialect=dialect,
            fix=fix,
            templated_file=templated_file,
            path=pathlib.Path(fname) if fname else None,
            segment=tree,
            config=config,
        )
        vs: List[SQLLintError] = []
        fixes: List[LintFix] = []

        # Propagates memory from one rule _eval() to the next.
        memory: Any = root_context.memory
        context = root_context
        for context in self.crawl_behaviour.crawl(root_context):
            try:
                context.memory = memory
                res = self._eval(context=context)
            except (bdb.BdbQuit, KeyboardInterrupt):  # pragma: no cover
                raise
            # Any exception at this point would halt the linter and
            # cause the user to get no results
            except Exception as e:
                # If a filename is present, include it in the critical exception.
                self.logger.critical(
                    f"Applying rule {self.code} to {fname!r} threw an Exception: {e}"
                    if fname
                    else f"Applying rule {self.code} threw an Exception: {e}",
                    exc_info=True,
                )
                assert context.segment.pos_marker
                exception_line, _ = context.segment.pos_marker.source_position()
                self._log_critical_errors(e)
                vs.append(
                    SQLLintError(
                        rule=self,
                        segment=context.segment,
                        fixes=[],
                        description=(
                            f"Unexpected exception: {str(e)};\n"
                            "Could you open an issue at "
                            "https://github.com/sqlfluff/sqlfluff/issues ?\n"
                            "You can ignore this exception for now, by adding "
                            f"'-- noqa: {self.code}' at the end\n"
                            f"of line {exception_line}\n"
                        ),
                    )
                )
                return vs, context.raw_stack, fixes, context.memory

            new_lerrs: List[SQLLintError] = []
            new_fixes: List[LintFix] = []

            if res is None or res == []:
                # Assume this means no problems (also means no memory)
                pass
            elif isinstance(res, LintResult):
                # Extract any memory
                memory = res.memory
                self._adjust_anchors_for_fixes(context, res)
                self._process_lint_result(
                    res, templated_file, ignore_mask, new_lerrs, new_fixes, tree
                )
            elif isinstance(res, list) and all(
                isinstance(elem, LintResult) for elem in res
            ):
                # Extract any memory from the *last* one, assuming
                # it was the last to be added
                memory = res[-1].memory
                for elem in res:
                    self._adjust_anchors_for_fixes(context, elem)
                    self._process_lint_result(
                        elem, templated_file, ignore_mask, new_lerrs, new_fixes, tree
                    )
            else:  # pragma: no cover
                raise TypeError(
                    "Got unexpected result [{!r}] back from linting rule: {!r}".format(
                        res, self.code
                    )
                )

            for lerr in new_lerrs:
                self.logger.info("!! Violation Found: %r", lerr.description)
            if new_fixes:
                if not self.is_fix_compatible:  # pragma: no cover
                    rules_logger.error(
                        f"Rule {self.code} returned a fix but is not documented as "
                        "`is_fix_compatible`, you may encounter unusual fixing "
                        "behaviour. Report this a bug to the developer of this rule."
                    )
                for lfix in new_fixes:
                    self.logger.info("!! Fix Proposed: %r", lfix)

            # Consume the new results
            vs += new_lerrs
            fixes += new_fixes
        return vs, context.raw_stack if context else tuple(), fixes, context.memory

    # HELPER METHODS --------
    @staticmethod
    def _log_critical_errors(error: Exception):  # pragma: no cover
        """This method is monkey patched into a "raise" for certain tests."""
        pass

    def _process_lint_result(
        self, res, templated_file, ignore_mask, new_lerrs, new_fixes, root
    ):
        # Unless the rule declares that it's already template safe. Do safety
        # checks.
        if not self.template_safe_fixes:
            self.discard_unsafe_fixes(res, templated_file)
        lerr = res.to_linting_error(rule=self)
        ignored = False
        if lerr:
            # Check whether this should be filtered out for being unparsable.
            # To do that we check the parents of the anchors (of the violation
            # and fixes) against the filter in the crawler.
            # NOTE: We use `.passes_filter` here to do the test for unparsable
            # to avoid duplicating code because that test is already implemented
            # there.
            anchors = [lerr.segment] + [fix.anchor for fix in lerr.fixes]
            for anchor in anchors:
                if not self.crawl_behaviour.passes_filter(anchor):  # pragma: no cover
                    # NOTE: This clause is untested, because it's a hard to produce
                    # edge case. The latter clause is much more likely.
                    linter_logger.info(
                        "Fix skipped due to anchor not passing filter: %s", anchor
                    )
                    lerr = None
                    ignored = True
                    break
                parent_stack = root.path_to(anchor)
                if not all(
                    self.crawl_behaviour.passes_filter(ps.segment)
                    for ps in parent_stack
                ):
                    linter_logger.info(
                        "Fix skipped due to parent of anchor not passing filter: %s",
                        [ps.segment for ps in parent_stack],
                    )
                    lerr = None
                    ignored = True
                    break

            if lerr and ignore_mask:
                filtered = LintedFile.ignore_masked_violations([lerr], ignore_mask)
                if not filtered:
                    lerr = None
                    ignored = True
        if lerr:
            new_lerrs.append(lerr)
        if not ignored:
            new_fixes.extend(res.fixes)

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
    def discard_unsafe_fixes(
        lint_result: LintResult, templated_file: Optional[TemplatedFile]
    ):
        """Remove (discard) LintResult fixes if they are "unsafe".

        By removing its fixes, a LintResult will still be reported, but it
        will be treated as _unfixable_.
        """
        if not lint_result.fixes or not templated_file:
            return

        # Check for fixes that touch templated code.
        for fix in lint_result.fixes:
            if fix.has_template_conflicts(templated_file):
                linter_logger.info(
                    "      * Discarding fixes that touch templated code: %s",
                    lint_result.fixes,
                )
                lint_result.fixes = []
                return

        # Issue 3079: Fixes that span multiple template blocks are bad. Don't
        # permit them.
        block_indices: Set[int] = set()
        for fix in lint_result.fixes:
            fix_slices = fix.get_fix_slices(templated_file, within_only=True)
            for fix_slice in fix_slices:
                # Ignore fix slices that exist only in the source. For purposes
                # of this check, it's not meaningful to say that a fix "touched"
                # one of these.
                if not fix_slice.is_source_only_slice():
                    block_indices.add(fix_slice.block_idx)
        if len(block_indices) > 1:
            linter_logger.info(
                "      * Discarding fixes that span multiple template blocks: %s",
                lint_result.fixes,
            )
            lint_result.fixes = []
            return

    @classmethod
    def _adjust_anchors_for_fixes(cls, context, lint_result) -> None:
        """Makes simple fixes to the anchor position for fixes.

        Some rules return fixes where the anchor is too low in the tree. These
        are most often rules like LT02 and LT05 that make whitespace changes
        without a "deep" understanding of the parse structure. This function
        attempts to correct those issues automatically. It may not be perfect,
        but it should be an improvement over the old behaviour, where rules like
        LT02 often corrupted the parse tree, placing spaces in weird places that
        caused issues with other rules. For more context, see issue #1304.
        """
        if not cls._adjust_anchors:
            return

        fix: LintFix
        for fix in lint_result.fixes:
            if fix.anchor:
                fix.anchor = cls._choose_anchor_segment(
                    # If no parent stack, that means the segment itself is the root
                    context.parent_stack[0]
                    if context.parent_stack
                    else context.segment,
                    fix.edit_type,
                    fix.anchor,
                )

    @staticmethod
    def _choose_anchor_segment(
        root_segment: BaseSegment,
        edit_type: str,
        segment: BaseSegment,
        filter_meta: bool = False,
    ):
        """Choose the anchor point for a lint fix, i.e. where to apply the fix.

        From a grammar perspective, segments near the leaf of the tree are
        generally less likely to allow general edits such as whitespace
        insertion.

        This function avoids such issues by taking a proposed anchor point
        (assumed to be near the leaf of the tree) and walking "up" the parse
        tree as long as the ancestor segments have the same start or end point
        (depending on the edit type) as "segment". This newly chosen anchor
        is more likely to be a valid anchor point for the fix.
        """
        if edit_type not in ("create_before", "create_after"):
            return segment

        anchor: BaseSegment = segment
        child: BaseSegment = segment
        path: Optional[List[BaseSegment]] = (
            [ps.segment for ps in root_segment.path_to(segment)]
            if root_segment
            else None
        )
        assert path
        for seg in path[::-1]:
            # If the segment allows non code ends, then no problem.
            # We're done. This is usually the outer file segment.
            if seg.can_start_end_non_code:
                linter_logger.debug(
                    "Stopping hoist at %s, as allows non code ends.", seg
                )
                break
            # Which lists of children to check against.
            children_lists: List[List[BaseSegment]] = []
            if filter_meta:
                # Optionally check against filtered (non-meta only) children.
                children_lists.append(
                    [child for child in seg.segments if not child.is_meta]
                )
            # Always check against the full set of children.
            children_lists.append(seg.segments)
            children: List[BaseSegment]
            for children in children_lists:
                if edit_type == "create_before" and children[0] is child:
                    linter_logger.debug(
                        "Hoisting anchor from before %s to %s", anchor, seg
                    )
                    anchor = seg
                    assert anchor.raw.startswith(segment.raw)
                    child = seg
                    break
                elif edit_type == "create_after" and children[-1] is child:
                    linter_logger.debug(
                        "Hoisting anchor from after %s to %s", anchor, seg
                    )
                    anchor = seg
                    assert anchor.raw.endswith(segment.raw)
                    child = seg
                    break
        return anchor


@dataclass(frozen=True)
class RuleManifest:
    """Element in the rule register."""

    code: str
    name: str
    description: str
    groups: Tuple[str]
    aliases: Tuple[str]
    rule_class: Type[BaseRule]


@dataclass
class RulePack:
    """A bundle of rules to be applied.

    This contains a set of rules, post filtering but also contains the mapping
    required to interpret any noqa messages found in files.

    The reason for this object is that rules are filtered and instantiated
    into this pack in the main process when running in multi-processing mode so
    that user defined rules can be used without reference issues.

    Attributes:
        rules (:obj:`list` of :obj:`BaseRule`): A filtered list of instantiated
            rules to be applied to a given file.
        reference_map (:obj:`dict`): A mapping of rule references to the codes
            they refer to, e.g. `{"my_ref": {"LT01", "LT02"}}`. The references
            (i.e. the keys) may be codes, groups, aliases or names. The values
            of the mapping are sets of rule codes *only*. This object acts as
            a lookup to be able to translate selectors (which may contain
            diverse references) into a consolidated list of rule codes. This
            mapping contains the full set of rules, rather than just the filtered
            set present in the `rules` attribute.
    """

    rules: List[BaseRule]
    reference_map: Dict[str, Set[str]]

    def codes(self) -> Iterator[str]:
        """Returns an iterator through the codes contained in the pack."""
        return (r.code for r in self.rules)


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
    overridden by the subclass, and the parent class raises an error on
    this function if not overridden.

    """

    def __init__(self, name, config_info) -> None:
        self.name = name
        self.config_info = config_info
        self._register: Dict[str, RuleManifest] = {}

    def _validate_config_options(self, config, rule_ref: Optional[str] = None):
        """Ensure that all config options are valid.

        Config options can also be checked for a specific rule e.g CP01.
        """
        rule_config = config.get_section("rules")
        for config_name, info_dict in self.config_info.items():
            config_option = (
                rule_config.get(config_name)
                if not rule_ref
                else rule_config.get(rule_ref).get(config_name)
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

    def register(self, cls, plugin=None):
        """Decorate a class with this to add it to the ruleset.

        .. code-block:: python

           @myruleset.register
           class Rule_LT01(BaseRule):
               "Description of rule."

               def eval(self, **kwargs):
                   return LintResult()

        We expect that rules are defined as classes with the name `Rule_XXXX`
        where `XXXX` is of the form `LNNN`, where L is a letter (literally L for
        *linting* by default) and N is a three digit number.

        If this receives classes by any other name, then it will raise a
        :exc:`ValueError`.

        """
        code = cls.code

        # Check for code collisions.
        if code in self._register:  # pragma: no cover
            raise ValueError(
                "Rule {!r} has already been registered on RuleSet {!r}!".format(
                    code, self.name
                )
            )

        assert "all" in cls.groups, "Rule {!r} must belong to the 'all' group".format(
            code
        )

        self._register[code] = RuleManifest(
            code=code,
            name=cls.name,
            description=cls.description,
            groups=cls.groups,
            aliases=cls.aliases,
            rule_class=cls,
        )

        # Make sure we actually return the original class
        return cls

    def _expand_rule_refs(
        self, glob_list: List[str], reference_map: Dict[str, Set[str]]
    ) -> Set[str]:
        """Expand a list of rule references into a list of rule codes.

        Returns:
            :obj:`set` of :obj:`str` rule codes.

        """
        expanded_rule_set: Set[str] = set()
        for r in glob_list:
            # Is it a direct reference?
            if r in reference_map:
                expanded_rule_set.update(reference_map[r])
            # Otherwise treat as a glob expression on all references.
            # NOTE: We expand _all_ references (i.e. groups, aliases, names
            # AND codes) so that we preserve the most backward compatibility
            # with existing references to legacy codes in config files.
            else:
                matched_refs = fnmatch.filter(reference_map.keys(), r)
                for matched in matched_refs:
                    expanded_rule_set.update(reference_map[matched])
        return expanded_rule_set

    def rule_reference_map(self) -> Dict[str, Set[str]]:
        """Generate a rule reference map for looking up rules.

        Generate the master reference map. The priority order is:
        codes > names > groups > aliases
        (i.e. if there's a collision between a name and an alias - we assume
        the alias is wrong)
        """
        valid_codes: Set[str] = set(self._register.keys())
        reference_map: Dict[str, Set[str]] = {code: {code} for code in valid_codes}

        # Generate name map.
        name_map: Dict[str, Set[str]] = {
            manifest.name: {manifest.code}
            for manifest in self._register.values()
            if manifest.name
        }
        # Check collisions.
        name_collisions = set(name_map.keys()) & valid_codes
        if name_collisions:  # pragma: no cover
            # NOTE: This clause is untested, because it's quite hard to actually
            # have a valid name which replicates a valid code. The name validation
            # will probably catch it first.
            rules_logger.warning(
                "The following defined rule names were found which collide "
                "with codes. Those names will not be available for selection: %s",
                name_collisions,
            )
        # Incorporate (with existing references taking precedence).
        reference_map = {**name_map, **reference_map}

        # Generate the group map.
        group_map: DefaultDict[str, Set[str]] = defaultdict(set)
        for manifest in self._register.values():
            for group in manifest.groups:
                if group in reference_map:
                    rules_logger.warning(
                        "Rule %s defines group %r which is already defined as a "
                        "name or code of %s. This group will not be available "
                        "for use as a result of this collision.",
                        manifest.code,
                        group,
                        reference_map[group],
                    )
                else:
                    group_map[group].add(manifest.code)
        # Incorporate after all checks are done.
        reference_map = {**group_map, **reference_map}

        # Generate the alias map.
        alias_map: DefaultDict[str, Set[str]] = defaultdict(set)
        for manifest in self._register.values():
            for alias in manifest.aliases:
                if alias in reference_map:
                    rules_logger.warning(
                        "Rule %s defines alias %r which is already defined as a "
                        "name, code or group of %s. This alias will "
                        "not be available for use as a result of this collision.",
                        manifest.code,
                        alias,
                        reference_map[alias],
                    )
                else:
                    alias_map[alias].add(manifest.code)
        # Incorporate after all checks are done.
        return {**alias_map, **reference_map}

    def get_rulepack(self, config) -> RulePack:
        """Use the config to return the appropriate rules.

        We use the config both for allowlisting and denylisting, but also
        for configuring the rules given the given config.
        """
        # Validate all generic rule configs
        self._validate_config_options(config)

        # Fetch config section:
        rules_config = config.get_section("rules")

        # Generate the master reference map. The priority order is:
        # codes > names > groups > aliases
        # (i.e. if there's a collision between a name and an
        # alias - we assume the alias is wrong.)
        valid_codes: Set[str] = set(self._register.keys())
        reference_map = self.rule_reference_map()
        valid_config_lookups = set(
            manifest.rule_class.get_config_ref() for manifest in self._register.values()
        )

        # Validate config doesn't try to specify values for unknown rules.
        # NOTE: We _warn_ here rather than error.
        for unexpected_ref in [
            # Filtering to dicts gives us the sections.
            k
            for k, v in rules_config.items()
            if isinstance(v, dict)
            # Only keeping ones we don't expect
            if k not in valid_config_lookups
        ]:
            rules_logger.warning(
                "Rule configuration contain a section for unexpected "
                f"rule {unexpected_ref!r}. These values will be ignored."
            )
            # For convenience (and migration), if we do find a potential match
            # for the reference - add that as a warning.
            # NOTE: We don't actually accept config in these cases, even though
            # we could potentially match - because how to resolve _multiple_
            # matching config sections is ambiguous.
            if unexpected_ref in reference_map:
                referenced_codes = reference_map[unexpected_ref]
                if len(referenced_codes) == 1:
                    referenced_code = list(referenced_codes)[0]
                    referenced_name = self._register[referenced_code].name
                    config_ref = self._register[
                        referenced_code
                    ].rule_class.get_config_ref()
                    rules_logger.warning(
                        "The reference was however found as a match for rule "
                        f"{referenced_code} with name {referenced_name!r}. "
                        "SQLFluff assumes configuration for this rule will "
                        f"be specified in 'sqlfluff:rules:{config_ref}'."
                    )
                elif referenced_codes:
                    rules_logger.warning(
                        "The reference was found as a match for multiple rules: "
                        f"{referenced_codes}. Config should be specified by the "
                        "name of the relevant rule e.g. "
                        "'sqlfluff:rules:capitalisation.keywords'."
                    )

        # The lists here are lists of references, which might be codes,
        # names, aliases or groups.
        # We default the allowlist to all the rules if not set (i.e. not specifying
        # any rules, just means "all the rules").
        allowlist = config.get("rule_allowlist") or list(valid_codes)
        denylist = config.get("rule_denylist") or []

        allowlisted_unknown_rule_codes = [
            r
            for r in allowlist
            # Add valid groups to the register when searching for invalid rules _only_
            if not fnmatch.filter(reference_map.keys(), r)
        ]
        if any(allowlisted_unknown_rule_codes):
            rules_logger.warning(
                "Tried to allowlist unknown rule references: {!r}".format(
                    allowlisted_unknown_rule_codes
                )
            )

        denylisted_unknown_rule_codes = [
            r for r in denylist if not fnmatch.filter(reference_map.keys(), r)
        ]
        if any(denylisted_unknown_rule_codes):  # pragma: no cover
            rules_logger.warning(
                "Tried to denylist unknown rules references: {!r}".format(
                    denylisted_unknown_rule_codes
                )
            )

        keylist = sorted(self._register.keys())

        # First we expand the allowlist and denylist globs
        expanded_allowlist = self._expand_rule_refs(allowlist, reference_map)
        expanded_denylist = self._expand_rule_refs(denylist, reference_map)

        # Then we filter the rules
        keylist = [
            r for r in keylist if r in expanded_allowlist and r not in expanded_denylist
        ]

        # Construct the kwargs for each rule and instantiate in turn.
        instantiated_rules = []
        # Keep only config which isn't a section (for specific rule) (i.e. isn't a dict)
        # We'll handle those directly in the specific rule config section below.
        generic_rule_config = {
            k: v for k, v in rules_config.items() if not isinstance(v, dict)
        }
        for code in keylist:
            kwargs = {}
            rule_class = cast(Type[BaseRule], self._register[code].rule_class)
            # Fetch the lookup code for the rule.
            rule_config_ref = rule_class.get_config_ref()
            specific_rule_config = config.get_section(("rules", rule_config_ref))
            if generic_rule_config:
                kwargs.update(generic_rule_config)
            if specific_rule_config:
                # Validate specific rule config before adding
                self._validate_config_options(config, rule_config_ref)
                kwargs.update(specific_rule_config)
            kwargs["code"] = code
            # Allow variable substitution in making the description
            kwargs["description"] = self._register[code].description.format(**kwargs)
            # Instantiate when ready
            instantiated_rules.append(rule_class(**kwargs))

        return RulePack(instantiated_rules, reference_map)

    def copy(self):
        """Return a copy of self with a separate register."""
        new_ruleset = copy.copy(self)
        new_ruleset._register = self._register.copy()
        return new_ruleset
