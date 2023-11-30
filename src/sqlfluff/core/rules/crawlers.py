"""Definitions of crawlers."""

from abc import ABC, abstractmethod
from typing import Any, Iterator, Set, cast

from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.segments.raw import RawSegment
from sqlfluff.core.rules.context import RuleContext


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
        types: Set[str],
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

    def crawl(self, context: RuleContext) -> Iterator[RuleContext]:
        """Yields a RuleContext for each segment the rule should process.

        We assume that segments are yielded by their parent.
        """
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

        # Check whether one of the targets is present (set intersection)
        if not self.types & context.segment.descendant_type_set:
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
