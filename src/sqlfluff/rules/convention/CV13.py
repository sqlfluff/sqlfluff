"""Implementation of Rule CV13."""

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CV13(BaseRule):
    """``CREATE INDEX`` should use ``CONCURRENTLY`` to avoid locking the table.

    ``CREATE INDEX`` without ``CONCURRENTLY`` acquires a lock that blocks
    writes for the duration of the index build. On large tables this can
    cause significant downtime.

    This rule is disabled by default and must be explicitly enabled.
    It only applies to the ``postgres`` dialect.

    .. note::
        ``CREATE UNIQUE INDEX`` statements are excluded because unique
        constraints often need transactional guarantees.

    **Anti-pattern**

    Creating an index without ``CONCURRENTLY``.

    .. code-block:: sql

        CREATE INDEX idx_foo ON bar (tenant_id);

    **Best practice**

    Use ``CONCURRENTLY`` to build the index without blocking writes.

    .. code-block:: sql

        CREATE INDEX CONCURRENTLY idx_foo ON bar (tenant_id);

    """

    name = "convention.create_index_concurrently"
    aliases = ()
    groups = ("all", "convention")
    crawl_behaviour = SegmentSeekerCrawler({"create_index_statement"})

    _target_dialects = ("postgres",)

    def _eval(self, context: RuleContext) -> LintResult | None:
        if context.dialect.name not in self._target_dialects:
            return None

        segment = context.segment

        for seg in segment.segments:
            if seg.is_type("keyword") and seg.raw_upper == "CONCURRENTLY":
                return None

        for seg in segment.segments:
            if seg.is_type("keyword") and seg.raw_upper == "UNIQUE":
                return None

        return LintResult(
            anchor=segment.segments[0],
            description=(
                "CREATE INDEX should use CONCURRENTLY "
                "to avoid locking the table during the build."
            ),
        )
