"""Implementation of Rule AL08."""

from typing import Dict, Optional, Tuple

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_AL08(BaseRule):
    """Column aliases should be unique within each clause.

    Reusing column aliases is very likely a coding error. Note that while
    in many dialects, quoting an identifier makes it case-sensitive
    this rule always compares in a case-insensitive way. This is because
    columns with the same name, but different case, are still confusing
    and potentially ambiguous to other readers.

    In situations where it is *necessary* to have columns with the same
    name (whether they differ in case or not) we recommend disabling this
    rule for either just the line, or the whole file.

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
        """Walk through select clauses, looking for matching identifiers."""
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
                    # We don't want the whole reference, just the last section.
                    # If it is qualified, take the last bit. Otherwise, we still
                    # take the last bit but it shouldn't make a difference.
                    column_alias = column_reference.segments[-1]

            # If we don't have an alias to work with, just skip this element
            if not column_alias:
                continue

            # NOTE: Always case insensitive, see docstring for why.
            _key = column_alias.raw_upper
            # Strip any quote tokens
            _key = _key.strip("\"'`")
            # Otherwise check whether it's been used before
            if _key in used_aliases:
                # It has.
                previous = used_aliases[_key]
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
                used_aliases[_key] = clause_element

        return violations
