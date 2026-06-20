"""Implementation of Rule CV13."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler


class Rule_CV13(BaseRule):
    """The final ``SELECT`` of a CTE model should be ``SELECT * FROM ...``.

    This is a convention popularised by the dbt
    `coding conventions <https://github.com/dbt-labs/corp/blob/main/dbt_style_guide.md>`_,
    where the final statement of a model is a "passthrough" select from the last
    CTE. Keeping the final select as ``SELECT * FROM final`` makes a model easier
    to debug, because the source of the final result set can be swapped by
    changing a single line (for example replacing ``final`` with an earlier CTE).

    To avoid flagging ad-hoc queries, this rule only applies when the *last*
    top-level statement of a file is a ``WITH ... SELECT`` (i.e. it uses CTEs).
    Plain ``SELECT`` statements, and files ending in DML or DDL, are not in
    scope.

    **Anti-pattern**

    The final select of a CTE model lists explicit columns rather than selecting
    everything from the final CTE.

    .. code-block:: sql

        WITH final AS (
            SELECT
                a,
                b
            FROM foo
        )

        SELECT
            a,
            b
        FROM final

    **Best practice**

    Select everything from the final CTE.

    .. code-block:: sql

        WITH final AS (
            SELECT
                a,
                b
            FROM foo
        )

        SELECT * FROM final

    """

    name = "convention.last_select_star"
    aliases = ()
    groups: tuple[str, ...] = ("all", "convention")
    crawl_behaviour = RootOnlyCrawler()

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """The final select of a CTE model should be ``SELECT * FROM ...``."""
        # We only operate on the file root.
        assert context.segment.is_type("file")

        # Find the last top-level statement in the file.
        statements = context.segment.get_children("statement")
        if not statements:
            # Nothing to check (e.g. a file of only comments).
            return None

        # A statement wraps a single inner segment (the actual query/DDL/DML).
        inner = statements[-1].segments[0]

        # The dbt convention applies to CTE-based models. To avoid false
        # positives on ad-hoc queries, only flag when the final statement is a
        # `WITH ... SELECT`.
        if not inner.is_type("with_compound_statement"):
            return None

        # The "passthrough" is the trailing query element of the WITH statement.
        final_select = self._final_select(inner)
        if final_select is None:
            # The WITH ends in a set expression (e.g. a UNION), which is not a
            # single `SELECT * FROM ...`. Anchor on the whole statement.
            return LintResult(anchor=inner)

        if self._is_select_star_from(final_select):
            return None

        # Anchor the violation on the select clause so the offending columns are
        # highlighted.
        select_clause = final_select.get_child("select_clause")
        return LintResult(anchor=select_clause or final_select)

    @staticmethod
    def _final_select(with_statement: BaseSegment) -> Optional[BaseSegment]:
        """Return the trailing ``select_statement`` of a WITH statement.

        If the trailing query element is a set expression (e.g. a ``UNION``)
        rather than a single select, ``None`` is returned.
        """
        queries = with_statement.get_children("select_statement", "set_expression")
        if queries and queries[-1].is_type("select_statement"):
            return queries[-1]
        return None

    @staticmethod
    def _is_select_star_from(select_statement: BaseSegment) -> bool:
        """Return whether a select is exactly ``SELECT * FROM ...``."""
        # The convention is `select * from`, so a source must be present.
        if not select_statement.get_child("from_clause"):
            return False

        select_clause = select_statement.get_child("select_clause")
        if not select_clause:
            return False  # pragma: no cover

        elements = select_clause.get_children("select_clause_element")
        # There must be exactly one selected element, and it must be a wildcard.
        if len(elements) != 1:
            return False

        first = next((seg for seg in elements[0].segments if not seg.is_meta), None)
        return bool(first and first.is_type("wildcard_expression"))
