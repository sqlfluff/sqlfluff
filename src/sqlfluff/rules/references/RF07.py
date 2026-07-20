"""Implementation of Rule RF07."""

from sqlfluff.core.dialects.common import qualification
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.analysis.select import get_select_statement_info


def _identifier_key(identifier: BaseSegment) -> tuple[bool, str]:
    """Return a comparison key of quoting style and normalized name.

    Unquoted identifiers fold case according to the dialect, so they compare
    case-insensitively with each other. A quoted identifier keeps its exact
    spelling and only compares equal to another quoted identifier with the
    same spelling, mirroring ANSI quoted identifier semantics.
    """
    if identifier.is_type("quoted_identifier"):
        return (True, identifier.raw_normalized())
    return (False, identifier.raw_normalized())


class Rule_RF07(BaseRule):
    """Do not reference a column alias inside its own ``OVER`` clause.

    Window functions are evaluated before the ``SELECT`` list aliases are
    applied, so an unqualified reference in a ``PARTITION BY`` or ``ORDER BY``
    which happens to match an alias does not resolve to that alias. When more
    than one table is in scope it silently resolves to a real column on one of
    them instead, changing the result without any error.

    .. note::
       This rule is disabled by default. Enable it with the
       ``force_enable = True`` flag.

    **Anti-pattern**

    ``id`` is an alias for ``t1.col1``, but inside the window it resolves to
    ``t2.id`` from the joined table.

    .. code-block:: sql

        SELECT
            t1.col1 AS id,
            ROW_NUMBER() OVER (PARTITION BY id ORDER BY t1.ts) AS rn
        FROM t1
        LEFT JOIN t2 ON t1.col1 = t2.id

    **Best practice**

    Qualify the reference with its table so the intended column is used.

    .. code-block:: sql

        SELECT
            t1.col1 AS id,
            ROW_NUMBER() OVER (PARTITION BY t1.col1 ORDER BY t1.ts) AS rn
        FROM t1
        LEFT JOIN t2 ON t1.col1 = t2.id
    """

    name = "references.window_alias"
    groups = ("all", "references")
    config_keywords = ["force_enable"]
    # A window_specification holds the PARTITION BY/ORDER BY of both an inline
    # OVER (...) and a named WINDOW ... AS (...) definition.
    crawl_behaviour = SegmentSeekerCrawler({"window_specification"})

    def _eval(self, context: RuleContext) -> EvalResultType:
        self.force_enable: bool
        if not self.force_enable:
            return None

        select_statement = None
        for parent in reversed(context.parent_stack):
            if parent.is_type("select_statement"):
                select_statement = parent
                break
        if select_statement is None:  # pragma: no cover
            return None

        select_info = get_select_statement_info(select_statement, context.dialect)
        # Only relevant when the alias could collide with a column on another
        # table, i.e. when more than one table is referenced.
        if not select_info or len(select_info.table_aliases) <= 1:
            return None

        # Comparison keys of the aliases declared in this SELECT: case variants
        # of unquoted identifiers match, quoted identifiers match exactly.
        alias_names = {
            _identifier_key(identifier)
            for element in select_statement.recursive_crawl(
                "select_clause_element", no_recursive_seg_type="select_statement"
            )
            for alias_expression in element.recursive_crawl(
                "alias_expression", no_recursive_seg_type="select_statement"
            )
            for identifier in alias_expression.recursive_crawl("identifier")
        }
        if not alias_names:
            return None

        results: list[LintResult] = []
        for clause in context.segment.recursive_crawl(
            "partitionby_clause", "orderby_clause"
        ):
            for reference in clause.recursive_crawl(
                "column_reference", no_recursive_seg_type="select_statement"
            ):
                if qualification(reference, context.dialect.name) != "unqualified":
                    continue
                # An unqualified reference contains a single identifier.
                identifier = next(reference.recursive_crawl("identifier"), None)
                if identifier is None:  # pragma: no cover
                    continue
                if _identifier_key(identifier) in alias_names:
                    results.append(
                        LintResult(
                            anchor=reference,
                            description=(
                                f"Reference {reference.raw!r} in window clause "
                                "matches a select alias but resolves to a table "
                                "column. Qualify it with its table."
                            ),
                        )
                    )
        return results or None
