"""Implementation of Rule AM08."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_AM09(BaseRule):
    """Ensures all tables are referenced with schemas.

    **Anti-pattern**

    A table is referenced without a schema.

    .. code-block:: sql

        SELECT
            a,
            b
        FROM my_table

    **Best practice**

    Always fully qualify tables.

    .. code-block:: sql

        SELECT
            a,
            b
        FROM my_schema.my_table
    """

    groups: tuple[str, ...] = ("all", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"table_reference"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Tables must be schema-qualified."""
        # A table reference is schema-qualified if it contains a dot.
        if "." in context.segment.raw:
            return None

        # We should also skip CTEs, as they are not schema-qualified.
        if context.memory is None:
            return None

        ctes = context.memory.get("ctes", set())
        if context.segment.raw.lower() in ctes:
            return None


        # It's not a CTE , and it's not qualified.
        return LintResult(
            anchor=context.segment,
            description=(
                f"Table `{context.segment.raw}` is not schema-qualified. "
                "Please use Explicit Schema Name."
            ),
        )


