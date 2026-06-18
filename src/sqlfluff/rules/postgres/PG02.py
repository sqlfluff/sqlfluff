"""Implementation of Rule PG02."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


def _has_keyword(segments, keyword: str) -> bool:
    """Check if a keyword exists among direct child segments."""
    return any(seg.is_type("keyword") and seg.raw_upper == keyword for seg in segments)


class Rule_PG02(BaseRule):
    """Avoid blocking table scans when adding foreign key constraints.

    ``ALTER TABLE ... ADD CONSTRAINT ... FOREIGN KEY`` acquires an
    ``ACCESS EXCLUSIVE`` lock and validates existing rows by scanning the
    entire table, which can cause extended downtime on large tables.

    The recommended approach is a two-step process:

    1. Add the constraint with ``NOT VALID`` to skip the initial scan
       while still enforcing the constraint for new writes.
    2. Run ``VALIDATE CONSTRAINT`` later (e.g. during a maintenance
       window) to validate any pre-existing rows.

    .. code-block:: sql

        ALTER TABLE foo ADD CONSTRAINT fk_bar
            FOREIGN KEY (bar_id) REFERENCES bar (id) NOT VALID;
        -- later, after verifying existing data:
        ALTER TABLE foo VALIDATE CONSTRAINT fk_bar;

    This rule was split from ``PG01`` in version 4.2.3. PG01 continues
    to check for ``CONCURRENTLY`` on index-related DDL statements.

    This rule only applies to the ``postgres`` dialect.

    **Anti-pattern**

    .. code-block:: sql

        ALTER TABLE foo ADD CONSTRAINT fk_bar
            FOREIGN KEY (bar_id) REFERENCES bar (id);

    **Best practice**

    .. code-block:: sql

        ALTER TABLE foo ADD CONSTRAINT fk_bar
            FOREIGN KEY (bar_id) REFERENCES bar (id) NOT VALID;

    """

    name = "postgres.foreign_key_not_valid"
    aliases = ()
    groups = ("all", "postgres")
    crawl_behaviour = SegmentSeekerCrawler(
        {
            "alter_table_statement",
        }
    )

    _target_dialects = ("postgres",)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        if context.dialect.name not in self._target_dialects:
            return None

        segment = context.segment

        action = segment.get_child("alter_table_action_segment")
        if not action:  # pragma: no cover
            return None
        constraint = action.get_child("table_constraint")
        if not constraint:
            return None
        if not _has_keyword(constraint.segments, "FOREIGN"):
            return None
        if _has_keyword(constraint.segments, "VALID"):
            return None
        return LintResult(
            anchor=segment,
            description=(
                "ADD CONSTRAINT ... FOREIGN KEY should use NOT VALID "
                "to avoid blocking scans while validating existing rows. "
                "Follow with VALIDATE CONSTRAINT afterwards."
            ),
        )
