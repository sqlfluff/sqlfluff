"""Implementation of Rule L032."""

from sqlfluff.core.rules.base import BaseCrawler, LintResult


class Rule_L032(BaseCrawler):
    """Prefer specifying join keys instead of using "USING".

    | **Anti-pattern**

    .. code-block:: sql

        SELECT
            table_a.field_1,
            table_b.field_2
        FROM
            table_a
        INNER JOIN table_b USING (id)

    | **Best practice**
    |  Specify the keys directly

    .. code-block:: sql

        SELECT
            table_a.field_1,
            table_b.field_2
        FROM
            table_a
        INNER JOIN table_b
            ON table_a.id = table_b.id

    """

    def _eval(self, segment, **kwargs):
        """Look for USING in a join clause."""
        if segment.is_type("join_clause"):
            for seg in segment.segments:
                if seg.is_type("keyword") and seg.name == "USING":
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
