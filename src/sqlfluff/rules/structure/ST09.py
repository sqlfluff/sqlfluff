"""Implementation of Rule ST09."""

from typing import List, Optional, Tuple, cast

from sqlfluff.core.parser import BaseSegment, SymbolSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.dialects.dialect_ansi import (
    FromExpressionElementSegment,
    JoinClauseSegment,
)
from sqlfluff.utils.functional import FunctionalContext, Segments


class Rule_ST09(BaseRule):
    """Joins should list the table referenced earlier/later first.

    This rule will break conditions from join clauses down into subconditions
    using the "and" and "or" binary operators.

    Subconditions that are made up of a qualified column reference,
    a comparison operator and another qualified column reference
    are then evaluated to check whether they list the table that was referenced
    earlier - or later, depending on the ``preferred_first_table_in_join_clause``
    configuration.

    Subconditions that do not follow that pattern are ignored by this rule.

    .. note::
       Joins in ``WHERE`` clauses are currently not supported by this rule.

    **Anti-pattern**

    In this example, the tables that were referenced later are listed first
    and the ``preferred_first_table_in_join_clause`` configuration
    is set to ``earlier``.

    .. code-block:: sql

        select
            foo.a,
            foo.b,
            bar.c
        from foo
        left join bar
            -- This subcondition does not list
            -- the table referenced earlier first:
            on bar.a = foo.a
            -- Neither does this subcondition:
            and bar.b = foo.b

    **Best practice**

    List the tables that were referenced earlier first.

    .. code-block:: sql

        select
            foo.a,
            foo.b,
            bar.c
        from foo
        left join bar
            on foo.a = bar.a
            and foo.b = bar.b
    """

    name = "structure.join_condition_order"
    aliases = ()
    groups: Tuple[str, ...] = ("all", "structure")
    config_keywords = ["preferred_first_table_in_join_clause"]
    crawl_behaviour = SegmentSeekerCrawler({"from_expression"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Find rule violations and provide fixes.

        0. Grab all table aliases into a table_aliases list.
        1. Grab all conditions from the different join_on_condition segments.
        2. Break conditions down into subconditions using the "and" and "or"
        binary operators.
        3. Keep subconditions that are made up of a qualified column_reference,
        a comparison_operator and another qualified column_reference segments.
        4. Check whether the table associated with the first column_reference segment
        has a greater index in table_aliases than the second column_reference segment.
        If so, populate the fixes list (lower index instead of greater index
        if preferred_first_table_in_join_clause == "later").
        5.a. If fixes is empty the rule passes.
        5.b. If fixes isn't empty we return a LintResult object with fixable violations.
        """
        self.preferred_first_table_in_join_clause: str

        assert context.segment.is_type("from_expression")

        # STEP 0.
        table_aliases: List[str] = []

        children = FunctionalContext(context).segment.children()

        # we use recursive_crawl to deal with brackets
        join_clauses = children.recursive_crawl("join_clause")

        join_on_conditions = join_clauses.children().recursive_crawl(
            "join_on_condition"
        )

        # we only care about join_on_condition segments
        if len(join_on_conditions) == 0:
            return None

        # the first alias comes from the from clause
        from_expression_alias: str = (
            cast(
                FromExpressionElementSegment,
                children.recursive_crawl("from_expression_element")[0],
            )
            .get_eventual_alias()
            .ref_str
        )

        table_aliases.append(from_expression_alias)

        # the rest of the aliases come from the different join clauses
        join_clause_aliases: List[str] = [
            cast(JoinClauseSegment, join_clause).get_eventual_aliases()[0][1].ref_str
            for join_clause in [clause for clause in join_clauses]
        ]

        table_aliases = table_aliases + join_clause_aliases

        table_aliases = [alias.upper() for alias in table_aliases]

        # STEP 1.
        conditions: List[List[BaseSegment]] = []

        join_on_condition__expressions = join_on_conditions.children().recursive_crawl(
            "expression"
        )

        for expression in join_on_condition__expressions:
            expression_group = []
            for element in Segments(expression).children():
                if element.type not in ("whitespace", "newline"):
                    expression_group.append(element)
            conditions.append(expression_group)

        # STEP 2.
        subconditions: List[List[List[BaseSegment]]] = []

        for expression_group in conditions:
            subconditions.append(
                self._split_list_by_segment_type(
                    segment_list=expression_group,
                    delimiter_type="binary_operator",
                    delimiters=["and", "or"],
                )
            )

        subconditions_flattened: List[List[BaseSegment]] = [
            item for sublist in subconditions for item in sublist
        ]

        # STEP 3.
        column_operator_column_subconditions: List[List[BaseSegment]] = [
            subcondition
            for subcondition in subconditions_flattened
            if self._is_qualified_column_operator_qualified_column_sequence(
                subcondition
            )
        ]

        # STEP 4.
        fixes: List[LintFix] = []

        for subcondition in column_operator_column_subconditions:
            comparison_operator = subcondition[1]
            first_column_reference = subcondition[0]
            second_column_reference = subcondition[2]
            raw_comparison_operators = comparison_operator.get_children(
                "raw_comparison_operator"
            )

            first_table_seg = first_column_reference.get_child(
                "naked_identifier", "quoted_identifier"
            )
            second_table_seg = second_column_reference.get_child(
                "naked_identifier", "quoted_identifier"
            )
            assert first_table_seg and second_table_seg
            first_table = first_table_seg.raw_upper
            second_table = second_table_seg.raw_upper

            # if we swap the two column references around the comparison operator
            # we might have to replace the comparison operator with a different one
            raw_comparison_operator_opposites = {"<": ">", ">": "<"}

            # there seem to be edge cases where either the first table or the second
            # table is not in table_aliases, in which case we cannot provide any fix
            if first_table not in table_aliases or second_table not in table_aliases:
                continue

            if (
                table_aliases.index(first_table) > table_aliases.index(second_table)
                and self.preferred_first_table_in_join_clause == "earlier"
            ) or (
                table_aliases.index(first_table) < table_aliases.index(second_table)
                and self.preferred_first_table_in_join_clause == "later"
            ):
                fixes = (
                    fixes
                    + [
                        LintFix.replace(
                            first_column_reference,
                            [second_column_reference],
                        )
                    ]
                    + [
                        LintFix.replace(
                            second_column_reference,
                            [first_column_reference],
                        )
                    ]
                    + (
                        [
                            LintFix.replace(
                                raw_comparison_operators[0],
                                [
                                    SymbolSegment(
                                        raw=raw_comparison_operator_opposites[
                                            raw_comparison_operators[0].raw
                                        ],
                                        type="raw_comparison_operator",
                                    )
                                ],
                            )
                        ]
                        if raw_comparison_operators[0].raw
                        in raw_comparison_operator_opposites
                        and [r.raw for r in raw_comparison_operators] != ["<", ">"]
                        else []
                    )
                )

        # STEP 5.a.
        if fixes == []:
            return None

        # STEP 5.b.
        else:
            return LintResult(
                anchor=context.segment,
                fixes=fixes,
                description=(
                    "Joins should list the table referenced "
                    f"{self.preferred_first_table_in_join_clause} first."
                ),
            )

    @staticmethod
    def _split_list_by_segment_type(
        segment_list: List[BaseSegment], delimiter_type: str, delimiters: List[str]
    ) -> List:
        # Break down a list into multiple sub-lists using a set of delimiters
        delimiters = [delimiter.upper() for delimiter in delimiters]
        new_list = []
        sub_list = []
        for i in range(len(segment_list)):
            if i == len(segment_list) - 1:
                sub_list.append(segment_list[i])
                new_list.append(sub_list)
            elif (
                segment_list[i].type == delimiter_type
                and segment_list[i].raw_upper in delimiters
            ):
                new_list.append(sub_list)
                sub_list = []
            else:
                sub_list.append(segment_list[i])

        return new_list

    @staticmethod
    def _is_qualified_column_operator_qualified_column_sequence(
        segment_list: List[BaseSegment],
    ) -> bool:
        # Check if list is made up of a qualified column_reference segment,
        # a comparison_operator segment and another qualified column_reference segment
        if len(segment_list) != 3:
            return False
        if (
            segment_list[0].type == "column_reference"
            and "dot" in segment_list[0].direct_descendant_type_set
            and segment_list[1].type == "comparison_operator"
            and segment_list[2].type == "column_reference"
            and "dot" in segment_list[2].direct_descendant_type_set
        ):
            return True
        return False
