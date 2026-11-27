"""Definitions of crawlers."""

import threading
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import Any, cast

from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.segments.raw import RawSegment
from sqlfluff.core.rules.context import RuleContext


class _WalkIndex:
    """One pre-order walk of a tree, shared by every seeker crawler.

    Records, per segment, what a crawler needs to yield a RuleContext, plus
    the positions of each segment type, so each rule looks up its matches
    instead of walking the tree again.
    """

    __slots__ = ("root", "segs", "stacks", "idxs", "ends", "unparsable", "by_type")

    def __init__(self, root: BaseSegment) -> None:
        self.root = root
        self.segs: list[BaseSegment] = []
        self.stacks: list[tuple[BaseSegment, ...]] = []
        self.idxs: list[int] = []
        # ends[i] is the position just past segment i's last descendant.
        self.ends: list[int] = []
        # True if the segment is, or is inside, an unparsable section.
        self.unparsable: list[bool] = []
        self.by_type: dict[str, list[int]] = {}
        self._visit(root, (), 0, False)

    def _visit(
        self, seg: BaseSegment, stack: tuple[BaseSegment, ...], idx: int, unp: bool
    ) -> None:
        i = len(self.segs)
        types = seg.class_types
        unp = unp or "unparsable" in types
        self.segs.append(seg)
        self.stacks.append(stack)
        self.idxs.append(idx)
        self.unparsable.append(unp)
        self.ends.append(0)
        for t in types:
            self.by_type.setdefault(t, []).append(i)
        if seg.segments:
            child_stack = stack + (seg,)
            for j, child in enumerate(seg.segments):
                self._visit(child, child_stack, j, unp)
        self.ends[i] = len(self.segs)

    def positions(self, types: set[str]) -> list[int]:
        """Positions of every segment of any of the given types, in order."""
        lists = [self.by_type[t] for t in types if t in self.by_type]
        if len(lists) == 1:
            return lists[0]
        return sorted(set().union(*lists))


# The index of the tree each thread is crawling. Segments are immutable, so
# it stays valid for as long as that root is the one being crawled.
_last_index = threading.local()


def _walk_index(root: BaseSegment) -> _WalkIndex:
    index: _WalkIndex | None = getattr(_last_index, "index", None)
    if index is None or index.root is not root:
        index = _last_index.index = _WalkIndex(root)
    return index


def forget_walk_index() -> None:
    """Drop this thread's walk index, once a file's crawls are done.

    The index holds every segment of its tree, so keeping it after linting
    keeps the tree alive and slows garbage collection for the next file.
    """
    _last_index.index = None


class BaseCrawler(ABC):
    """The base interface for crawler classes."""

    def __init__(self, works_on_unparsable: bool = False, **kwargs: Any) -> None:
        self.works_on_unparsable = works_on_unparsable

    def passes_filter(self, segment: BaseSegment) -> bool:
        """Returns true if this segment considered at all.

        This method is called during crawling but also
        in evaluating the anchors for linting violations
        and their fixes to make sure we don't get issues
        with linting sections of queries that we can't
        parse.

        See `BaseRule._process_lint_result()`.
        """
        return self.works_on_unparsable or not segment.is_type("unparsable")

    @abstractmethod
    def crawl(self, context: RuleContext) -> Iterator[RuleContext]:
        """Yields a RuleContext for each segment the rule should process."""


class RootOnlyCrawler(BaseCrawler):
    """A crawler that doesn't crawl.

    This just yields one context on the root-level (topmost) segment of the file.
    """

    def crawl(self, context: RuleContext) -> Iterator[RuleContext]:
        """Yields a RuleContext for each segment the rule should process."""
        if self.passes_filter(context.segment):
            yield context


class SegmentSeekerCrawler(BaseCrawler):
    """A crawler that efficiently searches for specific segment types.

    The segment type(s) are specified on creation.
    """

    def __init__(
        self,
        types: set[str],
        provide_raw_stack: bool = False,
        allow_recurse: bool = True,
        **kwargs: Any,
    ) -> None:
        self.types = types
        # Tracking a raw stack involves a lot of tuple manipulation, so we
        # only do it when required - otherwise we skip it. Rules can explicitly
        # request it when defining their crawler.
        self.provide_raw_stack = provide_raw_stack
        # If allow_recurse is false, then once a segment matches, none of it's
        # children will be returned. This is useful in cases where we might have
        # many start points, but one root segment will check any matching sub-
        # segments in the same evaluation.
        self.allow_recurse = allow_recurse
        super().__init__(**kwargs)

    def is_self_match(self, segment: BaseSegment) -> bool:
        """Does this segment match the relevant criteria."""
        return segment.is_type(*self.types)

    def _crawl_indexed(self, context: RuleContext) -> Iterator[RuleContext]:
        """As crawl(), from the shared walk index instead of a fresh walk."""
        index = _walk_index(context.segment)
        skip_unparsable = not self.works_on_unparsable
        skip_until = 0
        for i in index.positions(self.types):
            if i < skip_until or (skip_unparsable and index.unparsable[i]):
                continue
            if not self.allow_recurse:
                skip_until = index.ends[i]
            context.segment = index.segs[i]
            context.parent_stack = index.stacks[i]
            context.segment_idx = index.idxs[i]
            yield context

    def crawl(self, context: RuleContext) -> Iterator[RuleContext]:
        """Yields a RuleContext for each segment the rule should process.

        We assume that segments are yielded by their parent.
        """
        # A plain seeker starting at the root reads the shared walk index.
        # Subclasses and raw-stack tracking keep the recursive walk below.
        if (
            type(self) is SegmentSeekerCrawler
            and not self.provide_raw_stack
            and not context.parent_stack
        ):
            yield from self._crawl_indexed(context)
            return

        # Check whether we should consider this segment _or it's children_
        # at all.
        self_match = False
        if not self.passes_filter(context.segment):
            if self.provide_raw_stack:  # pragma: no cover
                context.raw_stack += tuple(context.segment.raw_segments)
            return

        # Then check the segment itself, yield if it's a match.
        if self.is_self_match(context.segment):
            self_match = True
            yield context

        # Check whether any children?
        # Abort if not - we've already yielded self.
        # NOTE: This same clause also works if we did match but aren't
        # allowed to recurse.
        if not context.segment.segments or (self_match and not self.allow_recurse):
            # Add self to raw stack first if so.
            if self.provide_raw_stack:
                context.raw_stack += (cast(RawSegment, context.segment),)
            return

        # Check whether one of the targets is present.
        if self.types.isdisjoint(context.segment.descendant_type_set):
            # None present. Don't look further.
            # This aggressive pruning helps performance.
            # Track raw stack if required.
            if self.provide_raw_stack:
                context.raw_stack += tuple(context.segment.raw_segments)
            return

        # NOTE: Full context is not implemented yet. More dev work required
        # before everything will be available here.

        # Given we know that one is present in here somewhere, search for it.
        new_parent_stack = context.parent_stack + (context.segment,)
        for idx, child in enumerate(context.segment.segments):
            # Handle children with no children of their own here, and skip
            # children which neither match nor contain a match, rather than
            # starting a crawl of each. The result is the same as this method
            # gives for that child, as long as is_self_match() and
            # passes_filter() have no side effects. A subclass's override of
            # crawl() is not called for these children.
            if not child.segments:
                if self.is_self_match(child) and self.passes_filter(child):
                    context.segment = child
                    context.parent_stack = new_parent_stack
                    context.segment_idx = idx
                    yield context
                    if self.provide_raw_stack:
                        context.raw_stack += (cast(RawSegment, child),)
                elif self.provide_raw_stack:
                    context.raw_stack += (
                        (cast(RawSegment, child),)
                        if self.passes_filter(child)
                        else tuple(child.raw_segments)
                    )
                continue
            if self.types.isdisjoint(
                child.descendant_type_set
            ) and not self.is_self_match(child):
                if self.provide_raw_stack:
                    context.raw_stack += tuple(child.raw_segments)
                continue
            # For performance reasons, don't create a new RuleContext for
            # each segment; just modify the existing one in place. This
            # requires some careful bookkeeping, but it avoids creating a
            # HUGE number of short-lived RuleContext objects
            # (#linter loops x #rules x #segments).
            # Importantly, we're resetting values here, because they
            # may have been modified deeper in the recursion.
            context.segment = child
            context.parent_stack = new_parent_stack
            context.segment_idx = idx
            yield from self.crawl(context)


class ParentOfSegmentCrawler(SegmentSeekerCrawler):
    """A crawler that efficiently searches for parents of specific segment types.

    The segment type(s) are specified on creation.
    """

    def is_self_match(self, segment: BaseSegment) -> bool:
        """Does this segment match the relevant criteria.

        We use the _direct_ child set here so that if any of the
        direct child segments match any of the types we're looking
        for, then we know that this segment is a parent of that
        kind of segment.
        """
        return bool(self.types & segment.direct_descendant_type_set)
