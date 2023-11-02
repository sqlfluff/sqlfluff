"""Implementation of Rule AL04."""

import itertools
from typing import List, Optional, Tuple

from sqlfluff.core.dialects.common import AliasInfo, ColumnAliasInfo
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import BaseRule, EvalResultType, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.dialects.dialect_ansi import ObjectReferenceSegment
from sqlfluff.utils.analysis.select import get_select_statement_info


class Rule_AL04(BaseRule):
    """Table aliases should be unique within each clause.

    Reusing table aliases is very likely a coding error.

    **Anti-pattern**

    In this example, the alias ``t`` is reused for two different tables:

    .. code-block:: sql

        SELECT
            t.a,
            t.b
        FROM foo AS t, bar AS t

        -- This can also happen when using schemas where the
        -- implicit alias is the table name:

        SELECT
            a,
            b
        FROM
            2020.foo,
            2021.foo

    **Best practice**

    Make all tables have a unique alias.

    .. code-block:: sql

        SELECT
            f.a,
            b.b
        FROM foo AS f, bar AS b

        -- Also use explicit aliases when referencing two tables
        -- with the same name from two different schemas.

        SELECT
            f1.a,
            f2.b
        FROM
            2020.foo AS f1,
            2021.foo AS f2

    """

    name = "aliasing.unique.table"
    aliases = ("L020",)
    groups: Tuple[str, ...] = ("all", "core", "aliasing", "aliasing.unique")
    crawl_behaviour = SegmentSeekerCrawler({"select_statement"})

    def _lint_references_and_aliases(
        self,
        table_aliases: List[AliasInfo],
        standalone_aliases: List[str],
        references: List[ObjectReferenceSegment],
        col_aliases: List[ColumnAliasInfo],
        using_cols: List[str],
        parent_select: Optional[BaseSegment],
    ) -> Optional[List[LintResult]]:
        """Check whether any aliases are duplicates.

        NB: Subclasses of this error should override this function.

        """
        # Are any of the aliases the same?
        duplicate = set()
        for a1, a2 in itertools.combinations(table_aliases, 2):
            # Compare the strings
            if a1.ref_str == a2.ref_str and a1.ref_str:
                duplicate.add(a2)
        if duplicate:
            return [
                LintResult(
                    # Reference the element, not the string.
                    anchor=aliases.segment,
                    description=(
                        "Duplicate table alias {!r}. Table " "aliases should be unique."
                    ).format(aliases.ref_str),
                )
                for aliases in duplicate
            ]
        else:
            return None

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Get References and Aliases and allow linting.

        This rule covers a lot of potential cases of odd usages of
        references, see the code for each of the potential cases.

        Subclasses of this rule should override the
        `_lint_references_and_aliases` method.
        """
        assert context.segment.is_type("select_statement")
        select_info = get_select_statement_info(context.segment, context.dialect)
        if not select_info:
            return None

        # Work out if we have a parent select function
        parent_select = None
        for seg in reversed(context.parent_stack):
            if seg.is_type("select_statement"):
                parent_select = seg
                break

        # Pass them all to the function that does all the work.
        # NB: Subclasses of this rules should override the function below
        return self._lint_references_and_aliases(
            select_info.table_aliases,
            select_info.standalone_aliases,
            select_info.reference_buffer,
            select_info.col_aliases,
            select_info.using_cols,
            parent_select,
        )
