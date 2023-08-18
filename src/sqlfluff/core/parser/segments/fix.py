"""Helper classes for applying fixes to segments."""

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, List, Optional, Tuple

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.rules import LintFix

# Instantiate the linter logger (only for use in methods involved with fixing.)
linter_logger = logging.getLogger("sqlfluff.linter")


@dataclass(frozen=True)
class SourceFix:
    """A stored reference to a fix in the non-templated file."""

    edit: str
    source_slice: slice
    # TODO: It might be possible to refactor this to not require
    # a templated_slice (because in theory it's unnecessary).
    # However much of the fix handling code assumes we need
    # a position in the templated file to interpret it.
    # More work required to achieve that if desired.
    templated_slice: slice

    def __hash__(self) -> int:
        # Only hash based on the source slice, not the
        # templated slice (which might change)
        return hash((self.edit, self.source_slice.start, self.source_slice.stop))


@dataclass
class FixPatch:
    """An edit patch for a source file."""

    templated_slice: slice
    fixed_raw: str
    # The patch category, functions mostly for debugging and explanation
    # than for function. It allows traceability of *why* this patch was
    # generated. It has no significance for processing.
    patch_category: str
    source_slice: slice
    templated_str: str
    source_str: str

    def dedupe_tuple(self) -> Tuple[slice, str]:
        """Generate a tuple of this fix for deduping."""
        return (self.source_slice, self.fixed_raw)


@dataclass
class AnchorEditInfo:
    """For a given fix anchor, count of the fix edit types and fixes for it."""

    delete: int = field(default=0)
    replace: int = field(default=0)
    create_before: int = field(default=0)
    create_after: int = field(default=0)
    fixes: List["LintFix"] = field(default_factory=list)
    source_fixes: List[SourceFix] = field(default_factory=list)
    # First fix of edit_type "replace" in "fixes"
    _first_replace: Optional["LintFix"] = field(default=None)

    def add(self, fix: "LintFix") -> None:
        """Adds the fix and updates stats.

        We also allow potentially multiple source fixes on the same
        anchor by condensing them together here.
        """
        if fix in self.fixes:
            # Deduplicate fixes in case it's already in there.
            return

        if fix.is_just_source_edit():
            assert fix.edit
            # is_just_source_edit confirms there will be a list
            # so we can hint that to mypy.
            self.source_fixes += fix.edit[0].source_fixes
            # is there already a replace?
            if self._first_replace:
                assert self._first_replace.edit
                # is_just_source_edit confirms there will be a list
                # and that's the only way to get into _first_replace
                # if it's populated so we can hint that to mypy.
                linter_logger.info(
                    "Multiple edits detected, condensing %s onto %s",
                    fix,
                    self._first_replace,
                )
                self._first_replace.edit[0] = self._first_replace.edit[0].edit(
                    source_fixes=self.source_fixes
                )
                linter_logger.info("Condensed fix: %s", self._first_replace)
                # Return without otherwise adding in this fix.
                return

        self.fixes.append(fix)
        if fix.edit_type == "replace" and not self._first_replace:
            self._first_replace = fix
        setattr(self, fix.edit_type, getattr(self, fix.edit_type) + 1)

    @property
    def total(self) -> int:
        """Returns total count of fixes."""
        return len(self.fixes)

    @property
    def is_valid(self) -> bool:
        """Returns True if valid combination of fixes for anchor.

        Cases:
        * 0-1 fixes of any type: Valid
        * 2 fixes: Valid if and only if types are create_before and create_after
        """
        if self.total <= 1:
            # Definitely valid (i.e. no conflict) if 0 or 1. In practice, this
            # function probably won't be called if there are 0 fixes, but 0 is
            # valid; it simply means "no fixes to apply".
            return True
        if self.total == 2:
            # This is only OK for this special case. We allow this because
            # the intent is clear (i.e. no conflict): Insert something *before*
            # the segment and something else *after* the segment.
            return self.create_before == 1 and self.create_after == 1
        # Definitely bad if > 2.
        return False  # pragma: no cover
