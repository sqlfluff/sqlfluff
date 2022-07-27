"""Definitions of crawlers."""

from typing import Iterator

from sqlfluff.core.rules.context import RuleContext


class BaseCrawler:
    """The base interface for crawler classes."""

    def __init__(self, works_on_unparsable: bool = False, **kwargs):
        self.works_on_unparsable = works_on_unparsable

    def passes_filter(self, context: RuleContext):
        """Returns true if this segment considered at all."""
        return self.works_on_unparsable or not context.segment.is_type("unparsable")

    def crawl(self, context: RuleContext) -> Iterator[RuleContext]:
        """Yields a RuleContext for each segment the rule should process."""
        raise NotImplementedError("Use a sepecific crawler, not the BaseCrawler")


class RootOnlyCrawler(BaseCrawler):
    """A crawler that doesn't crawl.

    This just yields one context on the parent segment of the file.
    """

    def crawl(self, context: RuleContext) -> Iterator[RuleContext]:
        """Yields a RuleContext for each segment the rule should process."""
        if not self.passes_filter(context):
            return
        yield context
