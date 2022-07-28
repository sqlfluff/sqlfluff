"""Definitions of crawlers."""

from typing import Iterator, Set, cast
from sqlfluff.core.parser.segments.base import BaseSegment

from sqlfluff.core.rules.context import RuleContext
from sqlfluff.core.rules.functional.segment_predicates import is_type


class BaseCrawler:
    """The base interface for crawler classes."""

    def __init__(self, works_on_unparsable: bool = False, **kwargs):
        self.works_on_unparsable = works_on_unparsable

    def passes_filter(self, segment: BaseSegment):
        """Returns true if this segment considered at all."""
        return self.works_on_unparsable or not segment.is_type("unparsable")

    def crawl(self, context: RuleContext) -> Iterator[RuleContext]:
        """Yields a RuleContext for each segment the rule should process."""
        raise NotImplementedError(  # pragma: no cover
            "Use a sepecific crawler, not the BaseCrawler. If you're seeing "
            "this error, a rule has likely not set it's crawl_behaviour attribute."
        )


class RootOnlyCrawler(BaseCrawler):
    """A crawler that doesn't crawl.

    This just yields one context on the parent segment of the file.
    """

    def crawl(self, context: RuleContext) -> Iterator[RuleContext]:
        """Yields a RuleContext for each segment the rule should process."""
        if not self.passes_filter(context.segment):
            return
        yield context


class SegmentSeekerCrawler(BaseCrawler):
    """A crawler that efficiently searches for specific segment types.

    The segment type(s) are specified on creation.
    """

    def __init__(self, types: Set[str], **kwargs):
        self.types = types
        super().__init__(**kwargs)

    def crawl(self, context: RuleContext) -> Iterator[RuleContext]:
        """Yields a RuleContext for each segment the rule should process.

        We assume that segments are yielded by their parent.
        """

        # First check the segment itself
        if context.segment.is_type(*self.types):
            yield context

        # Check whether any children?
        # Abort if not - we've already yielded self.
        if not context.segment.segments:
            return

        # Check whether one of the targets is present (set intersection)
        if not self.types & context.segment.child_type_set:
            # None present. Don't look further.
            # This aggressive pruning helps performance.
            return

        # NOTE: Do rule 21 first and don't populate all the context.

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
