"""Dataclasses for reflow work."""

import logging
from itertools import chain
from typing import Iterator, List, Optional, Sequence, Tuple, Type, cast

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.parser import BaseSegment, RawSegment
from sqlfluff.core.rules import LintFix, LintResult
from sqlfluff.utils.reflow.config import ReflowConfig
from sqlfluff.utils.reflow.depthmap import DepthMap
from sqlfluff.utils.reflow.elements import (
    ReflowBlock,
    ReflowPoint,
    ReflowSequenceType,
    get_consumed_whitespace,
)
from sqlfluff.utils.reflow.helpers import fixes_from_results
from sqlfluff.utils.reflow.rebreak import rebreak_sequence
from sqlfluff.utils.reflow.reindent import (
    construct_single_indent,
    lint_indent_points,
    lint_line_length,
)

# We're in the utils module, but users will expect reflow
# logs to appear in the context of rules. Hence it's a subset
# of the rules logger.
reflow_logger = logging.getLogger("sqlfluff.rules.reflow")


class ReflowSequence:
    """Class for keeping track of elements in a reflow operation.

    This acts as the primary route into using the reflow routines.
    It acts in a way that plays nicely within a rule context in that
    it accepts segments and configuration, while allowing access to
    modified segments and a series of :obj:`LintFix` objects, which
    can be returned by the calling rule.

    Sequences are made up of alternating :obj:`ReflowBlock` and
    :obj:`ReflowPoint` objects (even if some points have no segments).
    This is validated on construction.

    Most operations also return :obj:`ReflowSequence` objects such
    that operations can be chained, and then the resultant fixes
    accessed at the last stage, for example:

    .. code-block:: py3

        fixes = (
            ReflowSequence.from_around_target(
                context.segment,
                root_segment=context.parent_stack[0],
                config=context.config,
            )
            .rebreak()
            .get_fixes()
        )
    """

    def __init__(
        self,
        elements: ReflowSequenceType,
        root_segment: BaseSegment,
        reflow_config: ReflowConfig,
        depth_map: DepthMap,
        lint_results: Optional[List[LintResult]] = None,
    ):
        # First validate integrity
        self._validate_reflow_sequence(elements)
        # Then save
        self.elements = elements
        self.root_segment = root_segment
        self.reflow_config = reflow_config
        self.depth_map = depth_map
        # This keeps track of fixes generated in the chaining process.
        # Alternatively pictured: This is the list of fixes required
        # to generate this sequence. We can build on this as we edit
        # the sequence.
        # Rather than saving *fixes* directly, we package them into
        # LintResult objects to make it a little easier to expose them
        # in the CLI.
        self.lint_results: List[LintResult] = lint_results or []

    def get_fixes(self) -> List[LintFix]:
        """Get the current fix buffer.

        We're hydrating them here directly from the LintResult
        objects, so for more accurate results, consider using
        .get_results(). This method is particularly useful
        when consolidating multiple results into one.
        """
        return fixes_from_results(self.lint_results)

    def get_results(self) -> List[LintResult]:
        """Return the current result buffer."""
        return self.lint_results

    def get_raw(self) -> str:
        """Get the current raw representation."""
        return "".join(elem.raw for elem in self.elements)

    @staticmethod
    def _validate_reflow_sequence(elements: ReflowSequenceType) -> None:
        # An empty set of elements _is_ allowed as an edge case.
        if not elements:
            # Return early if so
            return None
        # Check odds and evens
        OddType = elements[0].__class__
        EvenType = ReflowPoint if OddType is ReflowBlock else ReflowBlock
        try:
            # Check odds are all points
            assert all(
                isinstance(elem, OddType) for elem in elements[::2]
            ), f"Not all odd elements are {OddType.__name__}"
            # Check evens are all blocks
            assert all(
                isinstance(elem, EvenType) for elem in elements[1::2]
            ), f"Not all even elements are {EvenType.__name__}"
            return None
        except AssertionError as err:  # pragma: no cover
            for elem in elements:
                reflow_logger.error("   - %s", elem)
            reflow_logger.exception("Assertion check on ReflowSequence failed.")
            raise err

    @staticmethod
    def _elements_from_raw_segments(
        segments: Sequence[RawSegment], reflow_config: ReflowConfig, depth_map: DepthMap
    ) -> ReflowSequenceType:
        """Construct reflow elements from raw segments.

        NOTE: ReflowBlock elements should only ever have one segment
        which simplifies iteration here.
        """
        elem_buff: ReflowSequenceType = []
        seg_buff: List[RawSegment] = []
        for seg in segments:
            # NOTE: end_of_file is block-like rather than point-like.
            # This is to facilitate better evaluation of the ends of files.
            # NOTE: This also allows us to include literal placeholders for
            # whitespace only strings.
            if (
                seg.is_type("whitespace", "newline", "indent")
                or (get_consumed_whitespace(seg) or "").isspace()
            ):
                # Add to the buffer and move on.
                seg_buff.append(seg)
                continue
            elif elem_buff or seg_buff:
                # There are elements. The last will have been a block.
                # Add a point before we add the block. NOTE: It may be empty.
                elem_buff.append(ReflowPoint(segments=tuple(seg_buff)))
            # Add the block, with config info.
            elem_buff.append(
                ReflowBlock.from_config(
                    segments=[seg],
                    config=reflow_config,
                    depth_info=depth_map.get_depth_info(seg),
                )
            )
            # Empty the buffer
            seg_buff = []

        # If we ended with a buffer, apply it.
        # TODO: Consider removing this clause?
        if seg_buff:  # pragma: no cover
            elem_buff.append(ReflowPoint(segments=tuple(seg_buff)))
        return elem_buff

    @classmethod
    def from_raw_segments(
        cls: Type["ReflowSequence"],
        segments: Sequence[RawSegment],
        root_segment: BaseSegment,
        config: FluffConfig,
        depth_map: Optional[DepthMap] = None,
    ) -> "ReflowSequence":
        """Construct a ReflowSequence from a sequence of raw segments.

        This is intended as a base constructor, which others can use.
        In particular, if no `depth_map` argument is provided, this
        method will generate one in a potentially inefficient way.
        If the calling method has access to a better way of inferring
        a depth map (for example because it has access to a common root
        segment for all the content), it should do that instead and pass
        it in.
        """
        reflow_config = ReflowConfig.from_fluff_config(config)
        if depth_map is None:
            depth_map = DepthMap.from_raws_and_root(segments, root_segment)
        return cls(
            elements=cls._elements_from_raw_segments(
                segments,
                reflow_config=reflow_config,
                # NOTE: This pathway is inefficient. Ideally the depth
                # map should be constructed elsewhere and then passed in.
                depth_map=depth_map,
            ),
            root_segment=root_segment,
            reflow_config=reflow_config,
            depth_map=depth_map,
        )

    @classmethod
    def from_root(
        cls: Type["ReflowSequence"], root_segment: BaseSegment, config: FluffConfig
    ) -> "ReflowSequence":
        """Generate a sequence from a root segment.

        Args:
            root_segment (:obj:`BaseSegment`): The relevant root
                segment (usually the base :obj:`FileSegment`).
            config (:obj:`FluffConfig`): A config object from which
                to load the spacing behaviours of different segments.
        """
        return cls.from_raw_segments(
            root_segment.raw_segments,
            root_segment,
            config=config,
            # This is the efficient route. We use it here because we can.
            depth_map=DepthMap.from_parent(root_segment),
        )

    @classmethod
    def from_around_target(
        cls: Type["ReflowSequence"],
        target_segment: BaseSegment,
        root_segment: BaseSegment,
        config: FluffConfig,
        sides: str = "both",
    ) -> "ReflowSequence":
        """Generate a sequence around a target.

        Args:
            target_segment (:obj:`RawSegment`): The segment to center
                around when considering the sequence to construct.
            root_segment (:obj:`BaseSegment`): The relevant root
                segment (usually the base :obj:`FileSegment`).
            config (:obj:`FluffConfig`): A config object from which
                to load the spacing behaviours of different segments.
            sides (:obj:`str`): Limit the reflow sequence to just one
                side of the target. Default is two sided ("both"), but
                set to "before" or "after" to limit to either side.


        **NOTE**: We don't just expand to the first block around the
        target but to the first *code* element, which means we
        may swallow several `comment` blocks in the process.

        To evaluate reflow around a specific target, we need
        need to generate a sequence which goes for the preceding
        raw to the following raw.
        i.e. at least: block - point - block - point - block
        (where the central block is the target).
        """
        # There's probably a more efficient way than immediately
        # materialising the raw_segments for the whole root, but
        # it works. Optimise later.
        all_raws = root_segment.raw_segments

        target_raws = target_segment.raw_segments
        assert target_raws
        pre_idx = all_raws.index(target_raws[0])
        post_idx = all_raws.index(target_raws[-1]) + 1
        initial_idx = (pre_idx, post_idx)
        if sides in ("both", "before"):
            # Catch at least the previous segment
            pre_idx -= 1
            for pre_idx in range(pre_idx, -1, -1):
                if all_raws[pre_idx].is_code:
                    break
        if sides in ("both", "after"):
            for post_idx in range(post_idx, len(all_raws)):
                if all_raws[post_idx].is_code:
                    break
            # Capture one more after the whitespace.
            post_idx += 1
        segments = all_raws[pre_idx:post_idx]
        reflow_logger.debug(
            "Generating ReflowSequence.from_around_target(). idx: %s. "
            "slice: %s:%s. raw: %r",
            initial_idx,
            pre_idx,
            post_idx,
            "".join(seg.raw for seg in segments),
        )
        return cls.from_raw_segments(segments, root_segment, config=config)

    def _find_element_idx_with(self, target: RawSegment) -> int:
        for idx, elem in enumerate(self.elements):
            if target in elem.segments:
                return idx
        raise ValueError(  # pragma: no cover
            f"Target [{target}] not found in ReflowSequence."
        )

    def without(self, target: RawSegment) -> "ReflowSequence":
        """Returns a new :obj:`ReflowSequence` without the specified segment.

        This generates appropriate deletion :obj:`LintFix` objects
        to direct the linter to remove those elements.
        """
        removal_idx = self._find_element_idx_with(target)
        if removal_idx == 0 or removal_idx == len(self.elements) - 1:
            raise NotImplementedError(  # pragma: no cover
                "Unexpected removal at one end of a ReflowSequence."
            )
        if isinstance(self.elements[removal_idx], ReflowPoint):
            raise NotImplementedError(  # pragma: no cover
                "Not expected removal of whitespace in ReflowSequence."
            )
        merged_point = ReflowPoint(
            segments=self.elements[removal_idx - 1].segments
            + self.elements[removal_idx + 1].segments,
        )
        return ReflowSequence(
            elements=self.elements[: removal_idx - 1]
            + [merged_point]
            + self.elements[removal_idx + 2 :],
            root_segment=self.root_segment,
            reflow_config=self.reflow_config,
            depth_map=self.depth_map,
            # Generate the fix to do the removal.
            lint_results=[LintResult(target, [LintFix.delete(target)])],
        )

    def insert(
        self, insertion: RawSegment, target: RawSegment, pos: str = "before"
    ) -> "ReflowSequence":
        """Returns a new :obj:`ReflowSequence` with the new element inserted.

        Insertion is always relative to an existing element. Either before
        or after it as specified by `pos`. This generates appropriate creation
        :obj:`LintFix` objects to direct the linter to insert those elements.
        """
        assert pos in ("before", "after")
        target_idx = self._find_element_idx_with(target)
        # Are we trying to insert something whitespace-like?
        if insertion.is_type("whitespace", "indent", "newline"):  # pragma: no cover
            raise ValueError(
                "ReflowSequence.insert() does not support direct insertion of "
                "spacing elements such as whitespace or newlines"
            )

        # We're inserting something blocky. That means a new block AND a new point.
        # It's possible we try to _split_ a point by targeting a whitespace element
        # inside a larger point. For now this isn't supported.
        # NOTE: We use the depth info of the reference anchor, with the assumption
        # (I think reliable) that the insertion will be applied as a sibling of
        # the target.
        self.depth_map.copy_depth_info(target, insertion)
        new_block = ReflowBlock.from_config(
            segments=[insertion],
            config=self.reflow_config,
            depth_info=self.depth_map.get_depth_info(target),
        )
        if isinstance(self.elements[target_idx], ReflowPoint):
            raise NotImplementedError(  # pragma: no cover
                "Can't insert relative to whitespace for now."
            )
        elif pos == "before":
            return ReflowSequence(
                elements=self.elements[:target_idx]
                + [new_block, ReflowPoint(())]
                + self.elements[target_idx:],
                root_segment=self.root_segment,
                reflow_config=self.reflow_config,
                depth_map=self.depth_map,
                # Generate the fix to do the removal.
                lint_results=[
                    LintResult(target, [LintFix.create_before(target, [insertion])])
                ],
            )
        elif pos == "after":  # pragma: no cover
            # TODO: This doesn't get coverage - should it even exist?
            # Re-evaluate whether this code path is ever taken once more rules use
            # this.
            return ReflowSequence(
                elements=self.elements[: target_idx + 1]
                + [ReflowPoint(()), new_block]
                + self.elements[target_idx + 1 :],
                root_segment=self.root_segment,
                reflow_config=self.reflow_config,
                depth_map=self.depth_map,
                # Generate the fix to do the removal.
                lint_results=[
                    LintResult(target, [LintFix.create_after(target, [insertion])])
                ],
            )
        raise ValueError(
            f"Unexpected value for ReflowSequence.insert(pos): {pos}"
        )  # pragma: no cover

    def replace(
        self, target: BaseSegment, edit: Sequence[BaseSegment]
    ) -> "ReflowSequence":
        """Returns a new :obj:`ReflowSequence` with `edit` elements replaced.

        This generates appropriate replacement :obj:`LintFix` objects to direct
        the linter to modify those elements.
        """
        target_raws = target.raw_segments
        assert target_raws

        edit_raws = list(chain.from_iterable(seg.raw_segments for seg in edit))

        # Add the new segments to the depth map at the same level as the target.
        # First work out how much to trim by.
        trim_amount = len(target.path_to(target_raws[0]))
        reflow_logger.debug(
            "Replacement trim amount: %s.",
            trim_amount,
        )
        for edit_raw in edit_raws:
            # NOTE: if target raws has more than one segment we take the depth info
            # of the first one. We trim to avoid including the implications of removed
            # "container" segments.
            self.depth_map.copy_depth_info(target_raws[0], edit_raw, trim=trim_amount)

        # It's much easier to just totally reconstruct the sequence rather
        # than do surgery on the elements.

        # TODO: The surgery is actually a good idea for long sequences now that
        # we have the depth map.

        current_raws = list(
            chain.from_iterable(elem.segments for elem in self.elements)
        )
        start_idx = current_raws.index(target_raws[0])
        last_idx = current_raws.index(target_raws[-1])

        return ReflowSequence(
            self._elements_from_raw_segments(
                current_raws[:start_idx] + edit_raws + current_raws[last_idx + 1 :],
                reflow_config=self.reflow_config,
                # NOTE: the depth map has been mutated to include the new segments.
                depth_map=self.depth_map,
            ),
            root_segment=self.root_segment,
            reflow_config=self.reflow_config,
            depth_map=self.depth_map,
            lint_results=[LintResult(target, [LintFix.replace(target, edit)])],
        )

    def _iter_points_with_constraints(
        self,
    ) -> Iterator[Tuple[ReflowPoint, Optional[ReflowBlock], Optional[ReflowBlock]]]:
        for idx, elem in enumerate(self.elements):
            # Only evaluate points.
            if isinstance(elem, ReflowPoint):
                pre = None
                post = None
                if idx > 0:
                    pre = cast(ReflowBlock, self.elements[idx - 1])
                if idx < len(self.elements) - 1:
                    post = cast(ReflowBlock, self.elements[idx + 1])
                yield elem, pre, post

    def respace(
        self, strip_newlines: bool = False, filter: str = "all"
    ) -> "ReflowSequence":
        """Returns a new :obj:`ReflowSequence` with points respaced.

        Args:
            strip_newlines (:obj:`bool`): Optionally strip newlines
                before respacing. This is primarily used on focused
                sequences to coerce objects onto a single line. This
                does not apply any prioritisation to which line breaks
                to remove and so is not a substitute for the full
                `reindent` or `reflow` methods.
            filter (:obj:`str`): Optionally filter which reflow points
                to respace. Default configuration is `all`. Other options
                are `line_break` which only respaces points containing
                a `newline` or followed by an `end_of_file` marker, or
                `inline` which is the inverse of `line_break`. This is
                most useful for filtering between trailing whitespace
                and fixes between content on a line.

        **NOTE** this method relies on the embodied results being correct
        so that we can build on them.
        """
        assert filter in (
            "all",
            "newline",
            "inline",
        ), f"Unexpected value for filter: {filter}"
        # Use the embodied fixes as a starting point.
        lint_results = self.get_results()
        new_elements: ReflowSequenceType = []
        for point, pre, post in self._iter_points_with_constraints():
            # We filter on the elements POST RESPACE. This is to allow
            # strict respacing to reclaim newlines.
            new_lint_results, new_point = point.respace_point(
                prev_block=pre,
                next_block=post,
                root_segment=self.root_segment,
                lint_results=lint_results,
                strip_newlines=strip_newlines,
            )
            # If filter has been set, optionally unset the returned values.
            if (
                filter == "inline"
                if (
                    # NOTE: We test on the NEW point.
                    any(seg.is_type("newline") for seg in new_point.segments)
                    # Or if it's followed by the end of file
                    or (post and "end_of_file" in post.class_types)
                )
                else filter == "newline"
            ):
                # Reset the values
                reflow_logger.debug(
                    "    Filter %r applied. Resetting %s", filter, point
                )
                new_point = point
            # Otherwise apply the new fixes
            else:
                lint_results = new_lint_results

            if pre and (not new_elements or new_elements[-1] != pre):
                new_elements.append(pre)
            new_elements.append(new_point)
            if post:
                new_elements.append(post)
        return ReflowSequence(
            elements=new_elements,
            root_segment=self.root_segment,
            reflow_config=self.reflow_config,
            depth_map=self.depth_map,
            lint_results=lint_results,
        )

    def rebreak(self) -> "ReflowSequence":
        """Returns a new :obj:`ReflowSequence` corrected line breaks.

        This intentionally **does not handle indentation**,
        as the existing indents are assumed to be correct.

        .. note::

            Currently this only *moves* existing segments
            around line breaks (e.g. for operators and commas),
            but eventually this method will also handle line
            length considerations too.
        """
        if self.lint_results:
            raise NotImplementedError(  # pragma: no cover
                "rebreak cannot currently handle pre-existing embodied fixes."
            )

        # Delegate to the rebreak algorithm
        elem_buff, lint_results = rebreak_sequence(self.elements, self.root_segment)

        return ReflowSequence(
            elements=elem_buff,
            root_segment=self.root_segment,
            reflow_config=self.reflow_config,
            depth_map=self.depth_map,
            lint_results=lint_results,
        )

    def reindent(self) -> "ReflowSequence":
        """Reindent lines within a sequence."""
        if self.lint_results:
            raise NotImplementedError(  # pragma: no cover
                "rebreak cannot currently handle pre-existing embodied fixes."
            )

        single_indent = construct_single_indent(
            indent_unit=self.reflow_config.indent_unit,
            tab_space_size=self.reflow_config.tab_space_size,
        )

        reflow_logger.info("# Evaluating indents.")
        elements, indent_results = lint_indent_points(
            self.elements,
            single_indent=single_indent,
            skip_indentation_in=self.reflow_config.skip_indentation_in,
            allow_implicit_indents=self.reflow_config.allow_implicit_indents,
            ignore_comment_lines=self.reflow_config.ignore_comment_lines,
        )

        return ReflowSequence(
            elements=elements,
            root_segment=self.root_segment,
            reflow_config=self.reflow_config,
            depth_map=self.depth_map,
            lint_results=indent_results,
        )

    def break_long_lines(self):
        """Rebreak any remaining long lines in a sequence.

        This assumes that reindent() has already been applied.
        """
        if self.lint_results:
            raise NotImplementedError(  # pragma: no cover
                "break_long_lines cannot currently handle pre-existing "
                "embodied fixes."
            )

        single_indent = construct_single_indent(
            indent_unit=self.reflow_config.indent_unit,
            tab_space_size=self.reflow_config.tab_space_size,
        )

        reflow_logger.info("# Evaluating line lengths.")
        elements, length_results = lint_line_length(
            self.elements,
            self.root_segment,
            single_indent=single_indent,
            line_length_limit=self.reflow_config.max_line_length,
            allow_implicit_indents=self.reflow_config.allow_implicit_indents,
            trailing_comments=self.reflow_config.trailing_comments,
        )

        return ReflowSequence(
            elements=elements,
            root_segment=self.root_segment,
            reflow_config=self.reflow_config,
            depth_map=self.depth_map,
            lint_results=length_results,
        )
