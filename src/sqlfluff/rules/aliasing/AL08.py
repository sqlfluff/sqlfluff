"""Implementation of Rule AL08."""

from typing import Optional, Tuple, Dict
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext, EvalResultType
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_AL08(BaseRule):
    """Column aliases should be unique within each clause.

    Reusing column aliases is very likely a coding error.

    **Anti-pattern**

    In this example, the alias ``foo`` is reused for two different columns:

    .. code-block:: sql

        SELECT
            a as foo,
            b as foo
        FROM tbl;

        -- This can also happen when referencing the same column
        -- column twice, or aliasing an expression to the same
        -- name as a column:

        SELECT
            foo,
            foo,
            a as foo
        FROM tbl;

    **Best practice**

    Make all columns have a unique alias.

    .. code-block:: sql

        SELECT
            a as foo,
            b as bar
        FROM tbl;

        -- Avoid also using the same column twice unless aliased:

        SELECT
            foo as foo1,
            foo as foo2,
            a as foo3
        FROM tbl;

    """

    name = "aliasing.unique.column"
    aliases = ()
    groups: Tuple[str, ...] = ("all", "core", "aliasing", "aliasing.unique")
    crawl_behaviour = SegmentSeekerCrawler({"select_clause"})

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Get References and Aliases and allow linting.

        This rule covers a lot of potential cases of odd usages of
        references, see the code for each of the potential cases.

        Subclasses of this rule should override the
        `_lint_references_and_aliases` method.
        """
        assert context.segment.is_type("select_clause")

        used_aliases: Dict[str, BaseSegment] = {}
        violations = []

        # Work through each of the elements
        for clause_element in context.segment.get_children("select_clause_element"):
            # Is there an alias expression?
            alias_expression = clause_element.get_child("alias_expression")
            column_alias: Optional[BaseSegment] = None
            if alias_expression:
                # Get the alias (it will be the next code element after AS)
                seg: Optional[BaseSegment] = None
                for seg in alias_expression.segments:
                    if not seg or not seg.is_code or seg.raw_upper == "AS":
                        continue
                    break
                assert seg
                column_alias = seg
            # No alias, the only other thing we'll track are column references.
            else:
                column_reference = clause_element.get_child("column_reference")
                if column_reference:
                    column_alias = column_reference

            # If we don't have an alias to work with, just skip this element
            if not column_alias:
                continue

            # Otherwise check whether it's been used before
            if column_alias.raw in used_aliases:
                # It has.
                previous = used_aliases[column_alias.raw]
                assert previous.pos_marker
                violations.append(
                    LintResult(
                        anchor=column_alias,
                        description=(
                            "Reuse of column alias "
                            f"{column_alias.raw!r} from line "
                            f"{previous.pos_marker.line_no}."
                        ),
                    )
                )
            else:
                # It's not, save it to check against others.
                used_aliases[column_alias.raw] = clause_element

        return violations
