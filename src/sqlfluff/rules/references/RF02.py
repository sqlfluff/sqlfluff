"""Implementation of Rule RF02."""

from typing import Optional

import regex

from sqlfluff.core.dialects.common import AliasInfo, ColumnAliasInfo
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import LintResult, RuleContext
from sqlfluff.rules.aliasing.AL04 import Rule_AL04
from sqlfluff.utils.analysis.select import get_select_statement_info


class Rule_RF02(Rule_AL04):
    """References should be qualified if select has more than one referenced table/view.

    .. note::
       Except if they're present in a ``USING`` clause.

    **Anti-pattern**

    In this example, the reference ``vee`` has not been declared,
    and the variables ``a`` and ``b`` are potentially ambiguous.

    .. code-block:: sql

        SELECT a, b
        FROM foo
        LEFT JOIN vee ON vee.a = foo.a

    **Best practice**

    Add the references.

    .. code-block:: sql

        SELECT foo.a, vee.b
        FROM foo
        LEFT JOIN vee ON vee.a = foo.a
    """

    name = "references.qualification"
    aliases = ("L027",)
    groups = ("all", "references")
    # Crawl behaviour is defined in AL04
    config_keywords = [
        "subqueries_ignore_external_references",
    ]

    # Config type hints
    ignore_words_regex: str
    ignore_words_list: list[str]
    subqueries_ignore_external_references: bool

    def _lint_references_and_aliases(
        self,
        table_aliases: list[AliasInfo],
        standalone_aliases: list[BaseSegment],
        references,
        col_aliases: list[ColumnAliasInfo],
        using_cols: list[BaseSegment],
        parent_select: Optional[BaseSegment],
        rule_context: RuleContext,
    ) -> Optional[list[LintResult]]:
        if parent_select:
            parent_select_info = get_select_statement_info(
                parent_select, rule_context.dialect
            )
            if parent_select_info:
                # If we are looking at a subquery, include any table references
                for table_alias in parent_select_info.table_aliases:
                    is_from = self._is_root_from_clause(rule_context)
                    if (
                        table_alias.from_expression_element.path_to(
                            rule_context.segment
                        )
                        or is_from
                        or self.subqueries_ignore_external_references
                    ):
                        # Skip the subquery alias itself or if the subquery is inside
                        # of a `from` or `join`` clause that isn't a nested where clause
                        continue
                    table_aliases.append(table_alias)

        # Do we have more than one? If so, all references should be qualified.
        if len(table_aliases) <= 1:
            return None

        # Get the ignore_words_list configuration.
        try:
            ignore_words_list = self.ignore_words_list
        except AttributeError:
            # First-time only, read the settings from configuration. This is
            # very slow.
            ignore_words_list = self._init_ignore_words_list()

        sql_variables = self._find_sql_variables(rule_context)

        # A buffer to keep any violations.
        violation_buff = []
        # Check all the references that we have.
        for r in references:
            # Skip if in ignore list
            if ignore_words_list and r.raw.lower() in ignore_words_list:
                continue

            # Skip if a sql variable name inside the file
            if r.raw.lower() in sql_variables:
                continue

            # Skip if matches ignore regex
            if self.ignore_words_regex and regex.search(self.ignore_words_regex, r.raw):
                continue

            this_ref_type = r.qualification()
            # Discard column aliases that
            # refer to the current column reference.
            col_alias_names = [
                c.alias_identifier_name
                for c in col_aliases
                if r not in c.column_reference_segments
            ]
            if (
                this_ref_type == "unqualified"
                # Allow unqualified columns that
                # are actually aliases defined
                # in a different select clause element.
                and r.raw not in col_alias_names
                # Allow columns defined in a USING expression.
                and r.raw not in [using_col.raw for using_col in using_cols]
                # Allow columns defined as standalone aliases
                # (e.g. value table functions from bigquery)
                and r.raw not in [a.raw for a in standalone_aliases]
            ):
                violation_buff.append(
                    LintResult(
                        anchor=r,
                        description=f"Unqualified reference {r.raw!r} found in "
                        "select with more than one referenced table/view.",
                    )
                )

        return violation_buff or None

    def _is_root_from_clause(self, rule_context: RuleContext) -> bool:
        """This is to determine if a subquery is part of the from clause.

        Any subqueries in the `from_clause` should be ignore, unless they are a nested
        correlated query.
        """
        is_from = False
        for x in reversed(rule_context.parent_stack):
            if x.is_type("from_clause"):
                is_from = True
                break
            elif x.is_type("where_clause"):
                break
        return is_from

    def _init_ignore_words_list(self) -> list[str]:
        """Called first time rule is evaluated to fetch & cache the policy."""
        ignore_words_config: str = str(getattr(self, "ignore_words"))
        if ignore_words_config and ignore_words_config != "None":
            self.ignore_words_list = self.split_comma_separated_string(
                ignore_words_config.lower()
            )
        else:
            self.ignore_words_list = []

        return self.ignore_words_list

    def _find_sql_variables(self, rule_context: RuleContext) -> set[str]:
        """Get any `DECLARE`d variables in the whole of the linted file.

        This assumes that the declare statement is going to be used before any reference
        """
        sql_variables: set[str] = set()

        # Check for bigquery declared variables. These may only exists at the top of
        # the file or at the beginning of a `BEGIN` block. The risk of collision
        # _should_ be low and no `IF` chain searching should be required.
        if rule_context.dialect.name == "bigquery":
            sql_variables |= {
                identifier.raw.lower()
                for declare in rule_context.parent_stack[0].recursive_crawl(
                    "declare_segment"
                )
                for identifier in declare.get_children("identifier")
            }

        # TODO: Add any additional dialect specific variable names

        return sql_variables
