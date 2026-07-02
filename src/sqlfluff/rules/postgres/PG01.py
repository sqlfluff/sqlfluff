"""Implementation of Rule PG01."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


def _has_keyword(segments, keyword: str) -> bool:
    """Check if a keyword exists among direct child segments."""
    return any(seg.is_type("keyword") and seg.raw_upper == keyword for seg in segments)


class Rule_PG01(BaseRule):
    """Avoid excessive locks in PostgreSQL DDL statements.

    Several PostgreSQL DDL operations acquire locks that block reads or writes
    for the duration of the operation. On large tables this can cause significant
    downtime. This rule flags statements that should use safer alternatives:

    * ``CREATE INDEX`` → use ``CONCURRENTLY`` (``CREATE UNIQUE INDEX`` excluded)
    * ``DROP INDEX`` → use ``CONCURRENTLY``
    * ``REINDEX`` → use ``CONCURRENTLY``
    * ``REFRESH MATERIALIZED VIEW`` → use ``CONCURRENTLY``

    This rule only applies to the ``postgres`` dialect and is disabled by
    default. Enable it with the ``force_enable = True`` flag.

    **Anti-pattern**

    DDL that acquires excessive locks.

    .. code-block:: sql

        CREATE INDEX idx_foo ON bar (tenant_id);

        DROP INDEX idx_foo;

        REINDEX INDEX idx_foo;

        REFRESH MATERIALIZED VIEW my_view;

    **Best practice**

    Use non-blocking alternatives.

    .. code-block:: sql

        CREATE INDEX CONCURRENTLY idx_foo ON bar (tenant_id);

        DROP INDEX CONCURRENTLY idx_foo;

        REINDEX INDEX CONCURRENTLY idx_foo;

        REFRESH MATERIALIZED VIEW CONCURRENTLY my_view;

    """

    name = "postgres.excessive_locks"
    aliases = ()
    groups = ("all", "postgres")
    config_keywords = ["force_enable"]
    crawl_behaviour = SegmentSeekerCrawler(
        {
            "create_index_statement",
            "drop_index_statement",
            "reindex_statement_segment",
            "refresh_materialized_view_statement",
        }
    )

    _target_dialects = ("postgres",)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        self.force_enable: bool

        if not self.force_enable:
            return None

        if context.dialect.name not in self._target_dialects:
            return None

        segment = context.segment
        seg_type = segment.get_type()

        if seg_type == "create_index_statement":
            return self._check_create_index(segment)
        if seg_type in (
            "drop_index_statement",
            "reindex_statement_segment",
            "refresh_materialized_view_statement",
        ):
            return self._check_concurrently(segment)
        return None  # pragma: no cover

    def _check_create_index(self, segment) -> Optional[LintResult]:
        if _has_keyword(segment.segments, "CONCURRENTLY"):
            return None
        if _has_keyword(segment.segments, "UNIQUE"):
            return None
        return LintResult(
            anchor=segment,
            description=(
                "CREATE INDEX should use CONCURRENTLY "
                "to avoid locking the table during the build."
            ),
        )

    def _check_concurrently(self, segment) -> Optional[LintResult]:
        if _has_keyword(segment.segments, "CONCURRENTLY"):
            return None
        stmt = segment.segments[0].raw_upper if segment.segments else "DDL"
        return LintResult(
            anchor=segment,
            description=(
                f"{stmt} statement should use CONCURRENTLY to avoid locking the table."
            ),
        )
