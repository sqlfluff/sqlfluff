"""Helper classes & methods for applying fixes to segments."""

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from itertools import chain
from typing import (
    TYPE_CHECKING,
    Dict,
    Iterable,
    Iterator,
    List,
    Optional,
    Set,
    Sized,
    Tuple,
    cast,
)

from sqlfluff.core.parser import (
    BaseSegment,
    PositionMarker,
    RawSegment,
    SourceFix,
)
from sqlfluff.core.templaters import RawFileSlice, TemplatedFile

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.dialects import Dialect


linter_logger = logging.getLogger("sqlfluff.linter")
rules_logger = logging.getLogger("sqlfluff.rules")


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
            # Copy all the elements of edit to stop contamination.
            # We're about to start stripping the position markers
            # off some of the elements and we don't want to end up
            # stripping the positions of the original elements of
            # the parsed structure.
            self.edit = [s.copy() for s in edit]
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

        # On creation of the fix we'll also validate the edits are non-trivial.
        if self.edit_type in ("create_before", "create_after"):
            assert self.edit, "A create fix must have an edit."
            # They should all have a non-zero raw.
            assert all(
                seg.raw for seg in self.edit
            ), f"Invalid edit found: {self.edit}."
        elif self.edit_type == "replace":
            assert (
                self.edit != self.anchor
            ), "Fix created which replaces segment with itself."

    def is_just_source_edit(self) -> bool:
        """Return whether this a valid source only edit."""
        return (
            self.edit_type == "replace"
            and self.edit is not None
            and len(self.edit) == 1
            and self.edit[0].raw == self.anchor.raw
        )

    def __repr__(self) -> str:
        if self.edit_type == "delete":
            detail = f"delete:{self.anchor.raw!r}"
        elif self.edit_type in ("replace", "create_before", "create_after"):
            seg_list = cast(List[BaseSegment], self.edit)
            new_detail = "".join(s.raw for s in seg_list)

            if self.edit_type == "replace":
                if self.is_just_source_edit():
                    seg_list = cast(List[BaseSegment], self.edit)
                    detail = f"src-edt:{seg_list[0].source_fixes!r}"
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

    def __eq__(self, other: object) -> bool:
        """Compare equality with another fix.

        A fix is equal to another if is in the same place (position), with the
        same type and (if appropriate) the same edit values.

        """
        # We have to assert this here rather in the type annotation so we don't
        # violate the Liskov substitution principle.
        # More context here: https://stackoverflow.com/a/37557540/11381493
        if not isinstance(other, LintFix):  # pragma: no cover
            return NotImplemented

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
            # We have to get weird here to appease mypy --strict
            # mypy seems to have a bug where even though we check above to make sure
            # self.edit is not None it still thinks it could be None when doing the
            # type check below. But if we use cast(List[BaseSegment], self.edit) then
            # it throws a redundant-cast error, because magically now it _does_ know
            # that self.edit is not None. So we have to cast to Sized for the len()
            # check and to Iterable[BaseSegment] for the looped check to make mypy
            # happy.

            # 1. Check lengths
            edit_list = cast(Sized, self.edit)
            other_list = cast(Sized, other.edit)
            if len(edit_list) != len(other_list):
                return False  # pragma: no cover
            # 2. Zip and compare
            edit_list2 = cast(Iterable[BaseSegment], self.edit)
            other_list2 = cast(Iterable[BaseSegment], other.edit)
            for a, b in zip(edit_list2, other_list2):
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


def compute_anchor_edit_info(fixes: List["LintFix"]) -> Dict[int, AnchorEditInfo]:
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
    fixes: Dict[int, AnchorEditInfo],
) -> Tuple["BaseSegment", List["BaseSegment"], List["BaseSegment"], bool]:
    """Apply a dictionary of fixes to this segment.

    Used in applying fixes if we're fixing linting errors.
    If anything changes, this should return a new version of the segment
    rather than mutating the original.

    Note: We need to have fixes to apply AND this must have children. In the case
    of raw segments, they will be replaced or removed by their parent and
    so this function should just return self.
    """
    if not fixes or segment.is_raw():
        return segment, [], [], True

    seg_buffer = []
    before = []
    after = []
    fixes_applied: List[LintFix] = []
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
        seg_buffer.extend(pre)
        seg_buffer.append(s)
        seg_buffer.extend(post)
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

    # Only validate if there's a match_grammar. Otherwise we may get
    # strange results (for example with the BracketedSegment).
    if requires_validate and hasattr(new_seg, "match_grammar"):
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


def _iter_source_fix_patches(
    segment: BaseSegment, templated_file: TemplatedFile
) -> Iterator[FixPatch]:
    """Yield any source patches as fixes now.

    NOTE: This yields source fixes for the segment and any of its
    children, so it's important to call it at the right point in
    the recursion to avoid yielding duplicates.
    """
    for source_fix in segment.source_fixes:
        yield FixPatch(
            source_fix.templated_slice,
            source_fix.edit,
            patch_category="source",
            source_slice=source_fix.source_slice,
            templated_str=templated_file.templated_str[source_fix.templated_slice],
            source_str=templated_file.source_str[source_fix.source_slice],
        )


def iter_patches(
    segment: BaseSegment, templated_file: TemplatedFile
) -> Iterator[FixPatch]:
    """Iterate through the segments generating fix patches.

    The patches are generated in TEMPLATED space. This is important
    so that we defer dealing with any loops until later. At this stage
    everything *should* happen in templated order.

    Occasionally we have an insertion around a placeholder, so we also
    return a hint to deal with that.
    """
    # Does it match? If so we can ignore it.
    assert segment.pos_marker
    templated_raw = templated_file.templated_str[segment.pos_marker.templated_slice]
    matches = segment.raw == templated_raw
    if matches:
        # First yield any source fixes
        yield from _iter_source_fix_patches(segment, templated_file)
        # Then return.
        return

    # If we're here, the segment doesn't match the original.
    linter_logger.debug(
        "# Changed Segment Found: %s at %s: Original: [%r] Fixed: [%r]",
        type(segment).__name__,
        segment.pos_marker.templated_slice,
        templated_raw,
        segment.raw,
    )

    # If it's all literal, then we don't need to recurse.
    if segment.pos_marker.is_literal():
        # First yield any source fixes
        yield from _iter_source_fix_patches(segment, templated_file)
        # Then yield the position in the source file and the patch
        yield FixPatch(
            source_slice=segment.pos_marker.source_slice,
            templated_slice=segment.pos_marker.templated_slice,
            patch_category="literal",
            fixed_raw=segment.raw,
            templated_str=templated_file.templated_str[
                segment.pos_marker.templated_slice
            ],
            source_str=templated_file.source_str[segment.pos_marker.source_slice],
        )
    # Can we go deeper?
    elif not segment.segments:
        # It's not literal, but it's also a raw segment. If we're going
        # to yield a change, we would have done it from the parent, so
        # we just abort from here.
        return  # pragma: no cover TODO?
    else:
        # This segment isn't a literal, but has changed, we need to go deeper.

        # If there's an end of file segment or indent, ignore them just for the
        # purposes of patch iteration.
        # NOTE: This doesn't mutate the underlying `self.segments`.
        segments = segment.segments
        while segments and segments[-1].is_type("end_of_file", "indent"):
            segments = segments[:-1]

        # Iterate through the child segments
        source_idx = segment.pos_marker.source_slice.start
        templated_idx = segment.pos_marker.templated_slice.start
        insert_buff = ""
        for seg in segments:
            # First check for insertions.
            # At this stage, everything should have a position.
            assert seg.pos_marker
            # We know it's an insertion if it has length but not in the templated
            # file.
            if seg.raw and seg.pos_marker.is_point():
                # Add it to the insertion buffer if it has length:
                if seg.raw:
                    insert_buff += seg.raw
                    linter_logger.debug(
                        "Appending insertion buffer. %r @idx: %s",
                        insert_buff,
                        templated_idx,
                    )
                continue

            # If we get here, then we know it's an original. Check for deletions at
            # the point before this segment (vs the TEMPLATED).
            # Deletions in this sense could also mean source consumption.
            start_diff = seg.pos_marker.templated_slice.start - templated_idx

            # Check to see whether there's a discontinuity before the current
            # segment
            if start_diff > 0 or insert_buff:
                # If we have an insert buffer, then it's an edit, otherwise a
                # deletion.

                # For the start of the next segment, we need the position of the
                # first raw, not the pos marker of the whole thing. That accounts
                # better for loops.
                first_segment_pos = seg.raw_segments[0].pos_marker
                yield FixPatch(
                    # Whether the source slice is zero depends on the start_diff.
                    # A non-zero start diff implies a deletion, or more likely
                    # a consumed element of the source. We can use the tracking
                    # markers from the last segment to recreate where this element
                    # should be inserted in both source and template.
                    source_slice=slice(
                        source_idx,
                        first_segment_pos.source_slice.start,
                    ),
                    templated_slice=slice(
                        templated_idx,
                        first_segment_pos.templated_slice.start,
                    ),
                    patch_category="mid_point",
                    fixed_raw=insert_buff,
                    templated_str="",
                    source_str="",
                )

                insert_buff = ""

            # Now we deal with any changes *within* the segment itself.
            yield from iter_patches(seg, templated_file=templated_file)

            # Once we've dealt with any patches from the segment, update
            # our position markers.
            source_idx = seg.pos_marker.source_slice.stop
            templated_idx = seg.pos_marker.templated_slice.stop

        # After the loop, we check whether there's a trailing deletion
        # or insert. Also valid if we still have an insertion buffer here.
        end_diff = segment.pos_marker.templated_slice.stop - templated_idx
        if end_diff or insert_buff:
            source_slice = slice(
                source_idx,
                segment.pos_marker.source_slice.stop,
            )
            templated_slice = slice(
                templated_idx,
                segment.pos_marker.templated_slice.stop,
            )
            # We determine the source_slice directly rather than
            # inferring it so that we can be very specific that
            # we ensure that fixes adjacent to source-only slices
            # (e.g. {% endif %}) are placed appropriately relative
            # to source-only slices.
            yield FixPatch(
                source_slice=source_slice,
                templated_slice=templated_slice,
                patch_category="end_point",
                fixed_raw=insert_buff,
                templated_str=templated_file.templated_str[templated_slice],
                source_str=templated_file.source_str[source_slice],
            )
