"""Helper classes & methods for applying fixes to segments."""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from sqlfluff.core.parser import BaseSegment, SourceFix
from sqlfluff.core.rules.fix import LintFix

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.dialects import Dialect


linter_logger = logging.getLogger("sqlfluff.linter")


@dataclass
class AnchorEditInfo:
    """For a given fix anchor, count of the fix edit types and fixes for it."""

    delete: int = field(default=0)
    replace: int = field(default=0)
    create_before: int = field(default=0)
    create_after: int = field(default=0)
    fixes: list["LintFix"] = field(default_factory=list)
    source_fixes: list[SourceFix] = field(default_factory=list)
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


def compute_anchor_edit_info(fixes: list["LintFix"]) -> dict[int, AnchorEditInfo]:
    """Group and count fixes by anchor, return dictionary."""
    anchor_info = defaultdict(AnchorEditInfo)  # type: ignore
    for fix in fixes:
        # :TRICKY: Use segment uuid as the dictionary key since
        # different segments may compare as equal.
        anchor_id = fix.anchor.uuid
        anchor_info[anchor_id].add(fix)
    return dict(anchor_info)


def apply_fixes(
    segment: BaseSegment,
    dialect: "Dialect",
    rule_code: str,
    fixes: dict[int, AnchorEditInfo],
    fix_even_unparsable: bool = False,
) -> tuple["BaseSegment", list["BaseSegment"], list["BaseSegment"], bool]:
    """Apply a dictionary of fixes to this segment.

    Used in to apply fixes found in linting. If a segment remains unchanged
    then the original is returned, but if any changes are made to it, or any
    of it's child segments, then it returns a copy rather than mutating the
    original.

    Most fixes are usually applied when this method is called on their parent
    segment, this is because that's where we can insert or move segments relative
    to the anchor specified in the fix. This has the implication that if the
    method is called on a `RawSegment`, then no changes will be applied, because
    a `RawSegment` never has child segments.

    After fixing, it calls `validate_segment_with_reparse` on the segment to
    check that the segment still parses after any changes are made. The result
    of this is returned as a boolean in the last element of the return tuple.
    As the function recurses, if an inner element doesn't parse after fixing,
    then the outer segment will also be checked, and if found to parse successfully
    then the method returns `True` as valid. This is because sometimes the fixes
    change the structure enough that a wider reparse is necessary.

    Because of this validity checking, any unparsable sections are assumed
    unfixable (because we won't know if we're corrupting the SQL). The method
    will therefore return early without applying any fixes if the segment it's
    called on is unparsable (because we already know that validation check will
    fail already).

    If `fix_even_unparsable` is True, then we will still apply fixes to unparsable
    sections, but will do so *without validation*. That means that the final
    element of the return value will always return `True`, so that we don't interrupt
    the validity checking of any outer (parsable) sections.
    """
    if not fixes or segment.is_raw():
        return segment, [], [], True

    seg_buffer = []
    before = []
    after = []
    fixes_applied: list[LintFix] = []
    requires_validate = False

    for seg in segment.segments:
        # Look for uuid match.
        # This handles potential positioning ambiguity.
        anchor_info: Optional[AnchorEditInfo] = fixes.pop(seg.uuid, None)

        if anchor_info is None:
            # No fix matches here, just add the segment and move on.
            seg_buffer.append(seg)
            continue

        # Otherwise there is a fix match.
        seg_fixes = anchor_info.fixes
        if (
            len(seg_fixes) == 2 and seg_fixes[0].edit_type == "create_after"
        ):  # pragma: no cover
            # Must be create_before & create_after. Swap so the
            # "before" comes first.
            seg_fixes.reverse()

        for f in anchor_info.fixes:
            assert f.anchor.uuid == seg.uuid
            fixes_applied.append(f)
            linter_logger.debug(
                "Matched fix for %s against segment: %s -> %s",
                rule_code,
                f,
                seg,
            )

            # Deletes are easy.
            if f.edit_type == "delete":
                # We're just getting rid of this segment.
                requires_validate = True
                # NOTE: We don't add the segment in this case.
                continue

            # Otherwise it must be a replace or a create.
            assert f.edit_type in (
                "replace",
                "create_before",
                "create_after",
            ), f"Unexpected edit_type: {f.edit_type!r} in {f!r}"

            if f.edit_type == "create_after" and len(anchor_info.fixes) == 1:
                # in the case of a creation after that is not part
                # of a create_before/create_after pair, also add
                # this segment before the edit.
                seg_buffer.append(seg)

            # We're doing a replacement (it could be a single
            # segment or an iterable)
            assert f.edit, f"Edit {f.edit_type!r} requires `edit`."
            consumed_pos = False
            for s in f.edit:
                seg_buffer.append(s)
                # If one of them has the same raw representation
                # then the first that matches gets to take the
                # original position marker.
                if f.edit_type == "replace" and s.raw == seg.raw and not consumed_pos:
                    seg_buffer[-1].pos_marker = seg.pos_marker
                    consumed_pos = True

            # If we're just editing a segment AND keeping the type the
            # same then no need to validate. Otherwise we should
            # trigger a validation (e.g. for creations or
            # multi-replace).
            if not (
                f.edit_type == "replace"
                and len(f.edit) == 1
                and f.edit[0].class_types == seg.class_types
            ):
                requires_validate = True

            if f.edit_type == "create_before":
                # in the case of a creation before, also add this
                # segment on the end
                seg_buffer.append(seg)

    # Invalidate any caches
    segment.invalidate_caches()

    # If any fixes applied, do an intermediate reposition. When applying
    # fixes to children and then trying to reposition them, that recursion
    # may rely on the parent having already populated positions for any
    # of the fixes applied there first. This ensures those segments have
    # working positions to work with.
    if fixes_applied:
        assert segment.pos_marker
        seg_buffer = list(
            segment._position_segments(tuple(seg_buffer), parent_pos=segment.pos_marker)
        )

    # Then recurse (i.e. deal with the children) (Requeueing)
    seg_queue = seg_buffer
    seg_buffer = []
    for seg in seg_queue:
        s, pre, post, validated = apply_fixes(seg, dialect, rule_code, fixes)
        # 'before' and 'after' will usually be empty. Only used when
        # lower-level fixes left 'seg' with non-code (usually
        # whitespace) segments as the first or last children. This is
        # generally not allowed (see the can_start_end_non_code field),
        # and these segments need to be "bubbled up" the tree.
        seg_buffer += pre + [s] + post
        # If we fail to validate a child segment, make sure to validate this
        # segment.
        if not validated:
            requires_validate = True

    # Most correct whitespace positioning will have already been handled
    # _however_, the exception is `replace` edits which match start or
    # end with whitespace. We also need to handle any leading or trailing
    # whitespace ejected from the any fixes applied to child segments.
    # Here we handle those by checking the start and end of the resulting
    # segment sequence for whitespace.
    # If we're left with any non-code at the end, trim them off and pass them
    # up to the parent segment for handling.
    if not segment.can_start_end_non_code:
        _idx = 0
        for _idx in range(0, len(seg_buffer)):
            if segment._is_code_or_meta(seg_buffer[_idx]):
                break
        before = seg_buffer[:_idx]
        seg_buffer = seg_buffer[_idx:]

        _idx = len(seg_buffer)
        for _idx in range(len(seg_buffer), 0, -1):
            if segment._is_code_or_meta(seg_buffer[_idx - 1]):
                break
        after = seg_buffer[_idx:]
        seg_buffer = seg_buffer[:_idx]

    # Reform into a new segment
    assert segment.pos_marker
    try:
        new_seg = segment.__class__(
            # Realign the segments within
            segments=segment._position_segments(
                tuple(seg_buffer), parent_pos=segment.pos_marker
            ),
            pos_marker=segment.pos_marker,
            # Pass through any additional kwargs
            **{k: getattr(segment, k) for k in segment.additional_kwargs},
        )
    except AssertionError as err:  # pragma: no cover
        # An AssertionError on creating a new segment is likely a whitespace
        # check fail. If possible add information about the fixes we tried to
        # apply, before re-raising.
        # NOTE: only available in python 3.11+.
        if hasattr(err, "add_note"):
            err.add_note(f" After applying fixes: {fixes_applied}.")
        raise err

    # Handle any necessary validation.
    if requires_validate:
        # Was it already unparsable?
        if "unparsable" in segment.descendant_type_set | segment.class_types:
            if fix_even_unparsable:
                # If we're fixing even unparsable sections, there's no point trying
                # to validate, it will always fail. We may still want to validate
                # other sections of the file though, so we should just declare *this*
                # part of the file to be all good.
                validated = True
            else:
                # It was already unparsable, but we're being asked to validate.
                # Don't any apply fixes from within this region and just return the
                # original segment.
                return segment, [], [], True
        # Otherwise only validate if there's a match_grammar. Otherwise we may get
        # strange results (for example with the BracketedSegment).
        elif hasattr(new_seg, "match_grammar"):
            validated = new_seg.validate_segment_with_reparse(dialect)
    else:
        validated = not requires_validate
    # Return the new segment and any non-code that needs to bubble up
    # the tree.
    # NOTE: We pass on whether this segment has been validated. It's
    # very possible that our parsing here may fail depending on the
    # type of segment that has been replaced, but if not we rely on
    # a parent segment still being valid. If we get all the way up
    # to the root and it's still not valid - that's a problem.
    return new_seg, before, after, validated
