"""Implementation of Rule PG02."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


def _has_keyword(segments, keyword: str) -> bool:
    """Check if a keyword exists among direct child segments."""
    return any(seg.is_type("keyword") and seg.raw_upper == keyword for seg in segments)


class Rule_PG02(BaseRule):
    """Create PostgreSQL foreign keys as ``NOT VALID`` before validating.

    Adding a foreign key constraint normally validates existing rows as part of
    the ``ALTER TABLE`` statement. On large tables, this can hold locks for
    longer than necessary. Creating the constraint as ``NOT VALID`` defers that
    scan so it can be run later with ``VALIDATE CONSTRAINT``.

    This rule only applies to the ``postgres`` dialect.

    **Anti-pattern**

    A foreign key constraint that validates existing rows during creation.

    .. code-block:: sql

        ALTER TABLE foo ADD CONSTRAINT fk_bar
            FOREIGN KEY (bar_id) REFERENCES bar (id);

    **Best practice**

    Create the foreign key as ``NOT VALID``, then validate it in a separate
    statement.

    .. code-block:: sql

        ALTER TABLE foo ADD CONSTRAINT fk_bar
            FOREIGN KEY (bar_id) REFERENCES bar (id) NOT VALID;

        ALTER TABLE foo VALIDATE CONSTRAINT fk_bar;

    """

    name = "postgres.not_valid_foreign_key"
    aliases = ()
    groups = ("all", "postgres")
    crawl_behaviour = SegmentSeekerCrawler({"alter_table_statement"})

    _target_dialects = ("postgres",)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        if context.dialect.name not in self._target_dialects:
            return None

        assert context.segment.is_type("alter_table_statement")

        action = context.segment.get_child("alter_table_action_segment")
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
            anchor=context.segment,
            description=(
                "ADD CONSTRAINT ... FOREIGN KEY should use NOT VALID, then "
                "VALIDATE CONSTRAINT separately, to avoid locking the table "
                "while validating existing rows."
            ),
        )
