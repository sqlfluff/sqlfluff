"""Classes for lint rule results."""
import copy
import logging
from typing import Optional

from sqlfluff.core.errors import SQLLintError
from sqlfluff.core.parser import BaseSegment

# Instantiate the rules logger
rules_logger = logging.getLogger("sqlfluff.rules")


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

    def __init__(self, edit_type, anchor: BaseSegment, edit=None):
        if edit_type not in (
            "create_before",
            "create_after",
            "edit",
            "delete",
        ):  # pragma: no cover
            raise ValueError(f"Unexpected edit_type: {edit_type}")
        self.edit_type = edit_type
        if not anchor:  # pragma: no cover
            raise ValueError("Fixes must provide an anchor.")
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
                    seg.pos_marker = None
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
        elif self.edit_type == "edit" and self.edit == self.anchor:
            return True  # pragma: no cover TODO?
        return False

    def __repr__(self):
        if self.edit_type == "delete":
            detail = f"delete:{self.anchor.raw!r}"
        elif self.edit_type in ("edit", "create_before", "create_after"):
            if hasattr(self.edit, "raw"):
                new_detail = self.edit.raw  # pragma: no cover TODO?
            else:
                new_detail = "".join(s.raw for s in self.edit)

            if self.edit_type == "edit":
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
