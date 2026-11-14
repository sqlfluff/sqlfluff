"""Implementation of Rule AL10."""

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_AL10(BaseRule):
    """Derived tables must have an alias.

    A derived table (subquery in a ``FROM`` clause) without an alias will
    cause a syntax error in most SQL dialects including MySQL, PostgreSQL,
    and T-SQL.

    .. note::
       BigQuery, DuckDB, Snowflake and SQLite accept a derived table without
       an alias, so this rule does not apply to them. ClickHouse accepts one
       as the single source of a ``FROM`` clause and in a ``PASTE JOIN``, but
       requires an alias in other joins and in a comma list. For ClickHouse
       this rule flags derived tables in a ``FROM`` clause with more than one
       source, so it still flags a ``PASTE JOIN``.

    **Anti-pattern**

    A subquery in a ``FROM`` clause without an alias.

    .. code-block:: sql

        SELECT *
        FROM (
            SELECT 1 AS a
        )

    **Best practice**

    Add an alias to the derived table.

    .. code-block:: sql

        SELECT *
        FROM (
            SELECT 1 AS a
        ) AS derived

    """

    name = "aliasing.required"
    aliases = ()
    groups = ("all", "core", "aliasing")
    crawl_behaviour = SegmentSeekerCrawler({"from_expression_element"})
    is_fix_compatible = False
    # Dialects whose grammar makes the derived table alias optional:
    # https://docs.cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax
    # https://duckdb.org/docs/2.0/sql/query_syntax/from.html
    # https://docs.snowflake.com/en/sql-reference/constructs/from
    # https://www.sqlite.org/lang_select.html
    _dialects_without_required_alias = [
        "bigquery",
        "duckdb",
        "snowflake",
        "sqlite",
    ]

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Check that derived tables have an alias."""
        assert context.segment.is_type("from_expression_element")

        if context.dialect.name in self._dialects_without_required_alias:
            return None

        # Check if this FROM expression contains a derived table.
        if not self._contains_derived_table(context.segment):
            return None

        # It's a derived table. Check if it has an alias.
        if context.segment.get_child("alias_expression"):
            return None

        # ClickHouse only requires an alias on a subquery in a FROM clause with
        # more than one table source (a join or a comma list), while the
        # `joined_subquery_requires_alias` setting is on (the default).
        # https://clickhouse.com/docs/reference/settings/session-settings/joined
        if context.dialect.name == "clickhouse" and not self._in_multi_source_from(
            context
        ):
            return None

        # Derived table without an alias.
        return LintResult(
            anchor=context.segment,
            description="Derived table must have an alias.",
        )

    @staticmethod
    def _in_multi_source_from(context: RuleContext) -> bool:
        """Check whether the FROM clause holding the segment has several sources."""
        # Without an enclosing FROM clause, the segment is its only source.
        from_clause = next(
            (p for p in reversed(context.parent_stack) if p.is_type("from_clause")),
            context.segment,
        )
        sources = from_clause.recursive_crawl(
            "from_expression_element", no_recursive_seg_type="select_statement"
        )
        return len(list(sources)) > 1

    @staticmethod
    def _contains_derived_table(from_expression_element: BaseSegment) -> bool:
        """Check whether a FROM expression element contains a derived table.

        A derived table is a subquery (SELECT, set expression, or WITH-compound
        statement) nested inside a FROM clause, potentially wrapped in brackets.
        """
        for segment in from_expression_element.iter_segments(expanding=("bracketed",)):
            if segment.is_type("table_expression"):
                # Check for nested SELECT, UNION/INTERSECT/EXCEPT, or
                # WITH-compound statement.
                for seg in segment.iter_segments(expanding=("bracketed",)):
                    if seg.is_type(
                        "select_statement",
                        "set_expression",
                        "with_compound_statement",
                    ):
                        return True
        return False
