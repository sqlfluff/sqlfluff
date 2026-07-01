"""Implementation of Rule CV13."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler


class Rule_CV13(BaseRule):
    """The final ``SELECT`` of a CTE model should be ``SELECT * FROM ...``.

    This is a convention popularised by the dbt
    `style guide
    <https://docs.getdbt.com/best-practices/how-we-style/0-how-we-style-our-dbt-projects>`_,
    where the final statement of a model is a "passthrough" select from the last
    CTE. Keeping the final select as ``SELECT * FROM final`` makes a model easier
    to debug, because the source of the final result set can be swapped by
    changing a single line (for example replacing ``final`` with an earlier CTE).

    To avoid flagging ad-hoc queries, this rule only applies when the *last*
    top-level statement of a file is a ``WITH ... SELECT`` (i.e. it uses CTEs).
    Plain ``SELECT`` statements, and files ending in DML or DDL, are not in
    scope. The final select must also be a pure passthrough: a lone
    ``SELECT * FROM <cte>`` with no further transformation (``WHERE``,
    ``GROUP BY``, ``DISTINCT``, ``ORDER BY``, ``LIMIT``, etc.).

    This convention is opinionated and not universally agreed upon, so this
    rule is **disabled by default**. It can be enabled with the
    ``force_enable = True`` flag:

    .. code-block:: cfg

        [sqlfluff:rules:convention.last_select_star]
        force_enable = True

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
    config_keywords = ["force_enable"]
    crawl_behaviour = RootOnlyCrawler()

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """The final select of a CTE model should be ``SELECT * FROM ...``."""
        # Config type hints
        self.force_enable: bool

        # This convention is opinionated, so the rule is disabled by default
        # and only runs when explicitly enabled via `force_enable = True`.
        if not self.force_enable:
            return None

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

    # Clauses that are permitted in a pure passthrough select. Anything else
    # (`where_clause`, `groupby_clause`, `having_clause`, `orderby_clause`,
    # `limit_clause`, `qualify_clause`, ...) is a transformation and means the
    # final select is doing more than passing the last CTE through.
    _passthrough_clauses = frozenset({"select_clause", "from_clause"})

    @classmethod
    def _is_select_star_from(cls, select_statement: BaseSegment) -> bool:
        """Return whether a select is exactly ``SELECT * FROM <source>``.

        This must be a *pure* passthrough: a lone wildcard selected from a
        single source, with no further transformation clauses (e.g. ``WHERE``,
        ``GROUP BY``, ``DISTINCT``, ``ORDER BY``, ``LIMIT``).
        """
        # The convention is `select * from`, so a source must be present.
        if not select_statement.get_child("from_clause"):
            return False

        # Reject any transformation clause beyond `select`/`from`. A passthrough
        # must not filter, aggregate, sort or limit the final result set.
        for clause in select_statement.segments:
            if clause.is_type("keyword") or clause.is_meta:
                continue  # pragma: no cover
            if (
                clause.type.endswith("_clause")
                and clause.type not in cls._passthrough_clauses
            ):
                return False

        select_clause = select_statement.get_child("select_clause")
        if not select_clause:
            return False  # pragma: no cover

        # A select modifier such as `DISTINCT` reshapes the result set, so it is
        # not a passthrough (`ALL` is the default and is harmless, but treating
        # any explicit modifier as non-passthrough keeps the rule conservative).
        if select_clause.get_child("select_clause_modifier"):
            return False

        elements = select_clause.get_children("select_clause_element")
        # There must be exactly one selected element, and it must be a wildcard.
        if len(elements) != 1:
            return False

        first = next((seg for seg in elements[0].segments if not seg.is_meta), None)
        return bool(first and first.is_type("wildcard_expression"))
