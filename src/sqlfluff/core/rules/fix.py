"""Defines the LintFix class, returned by rules when recommending a fix."""

import logging
from itertools import chain
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Set,
    Sized,
    cast,
)

from sqlfluff.core.parser import (
    BaseSegment,
    PositionMarker,
    RawSegment,
    SourceFix,
)
from sqlfluff.core.templaters import RawFileSlice, TemplatedFile

rules_logger = logging.getLogger("sqlfluff.rules")


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

    def to_dict(self) -> Dict[str, Any]:
        """Serialise this LintFix as a dict."""
        assert self.anchor
        _position = self.anchor.pos_marker
        assert _position
        _src_loc = _position.to_source_dict()
        if self.edit_type == "delete":
            return {
                "type": self.edit_type,
                "edit": "",
                **_src_loc,
            }
        elif self.edit_type == "replace" and self.is_just_source_edit():
            assert self.edit is not None
            assert len(self.edit) == 1
            assert len(self.edit[0].source_fixes) == 1
            _source_fix = self.edit[0].source_fixes[0]
            return {
                "type": self.edit_type,
                "edit": _source_fix.edit,
                **_position.templated_file.source_position_dict_from_slice(
                    _source_fix.source_slice
                ),
            }

        # Otherwise it's a standard creation or a replace.
        seg_list = cast(List[BaseSegment], self.edit)
        _edit = "".join(s.raw for s in seg_list)

        if self.edit_type == "create_before":
            # If we're creating _before_, the end point isn't relevant.
            # Make it the same as the start.
            _src_loc["end_line_no"] = _src_loc["start_line_no"]
            _src_loc["end_line_pos"] = _src_loc["start_line_pos"]
            _src_loc["end_file_pos"] = _src_loc["start_file_pos"]
        elif self.edit_type == "create_after":
            # If we're creating _after_, the start point isn't relevant.
            # Make it the same as the end.
            _src_loc["start_line_no"] = _src_loc["end_line_no"]
            _src_loc["start_line_pos"] = _src_loc["end_line_pos"]
            _src_loc["start_file_pos"] = _src_loc["end_file_pos"]

        return {
            "type": self.edit_type,
            "edit": _edit,
            **_src_loc,
        }

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
