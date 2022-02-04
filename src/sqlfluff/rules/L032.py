"""Implementation of Rule L032."""
from typing import List, Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext


class Rule_L032(BaseRule):
    """Prefer specifying join keys instead of using ``USING``.

    .. note::
       This rule was taken from the `dbt Style Guide
       <https://github.com/dbt-labs/corp/blob/master/dbt_style_guide.md>`_
       which notes that:

        Certain warehouses have inconsistencies in ``USING``
        results (specifically Snowflake).

       Other users may prefer to disable this rule.

    **Anti-pattern**

    .. code-block:: sql

        SELECT
            table_a.field_1,
            table_b.field_2
        FROM
            table_a
        INNER JOIN table_b USING (id)

    **Best practice**

    Specify the keys directly

    .. code-block:: sql

        SELECT
            table_a.field_1,
            table_b.field_2
        FROM
            table_a
        INNER JOIN table_b
            ON table_a.id = table_b.id

    """

    def _eval(self, context: RuleContext) -> Optional[List[LintResult]]:
        """Look for USING in a join clause."""
        if context.segment.is_type("join_clause"):
            for seg in context.segment.segments:
                if seg.is_type("keyword") and seg.name == "using":
                    return [
                        LintResult(
                            # Reference the element, not the string.
                            anchor=seg,
                            description=(
                                "Found USING statement. Expected only ON statements."
                            ),
                        )
                    ]
        return None
