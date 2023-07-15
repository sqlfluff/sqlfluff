"""Implementation of Rule ST09."""
from typing import Optional, Tuple, Any
from sqlfluff.core.parser.segments.raw import BaseSegment, SymbolSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import Segments, sp, FunctionalContext


class Rule_ST09(BaseRule):
    """Joins should list the left/right table first.

    This rule will break down conditions from join clauses into subconditions
    using the "and" and "or" binary operators.
    Subconditions that are made up of a column reference, a comparison operator
    and another column reference are then evaluated to check whether they list
    the left - or right, depending on the ``preferred_first_table_in_join_clause``
    configuration - table first (default is left).
    Subconditions that do not follow that pattern are ignored by this rule.

    **Anti-pattern**

    In this example, the right tables are listed first
    and ``preferred_first_table_in_join_clause = 'left'``.

    .. code-block:: sql

        select
            foo.a,
            foo.b,
            bar.c
        from foo
        left join bar
            on bar.a = foo.a -- This subcondition does not list the left table first.
            and bar.b = foo.b -- Neither does this subcondition.

    **Best practice**

    List the left tables first.

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

    name = "structure.first_table"
    groups: Tuple[str, ...] = ("all", "structure")
    config_keywords = ["preferred_first_table_in_join_clause"]
    crawl_behaviour = SegmentSeekerCrawler({"from_expression"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Find rule violations and provide fixes.

        0. Grab all table aliases into a table_aliases list.
        1. Grab all conditions from the different join_on_condition segments.
        2. Break down conditions into subconditions using the "and" and "or"
        binary operators.
        3. Keep subconditions that are made up of a column_reference,
        a comparison_operator and another column_reference segments.
        4. Check whether the table associated with the first column_reference segment
        has a greater index in table_aliases than the second column_reference segment.
        If so, populate the fixes list (lower index instead of greater index
        if preferred_first_table_in_join_clause == "right").
        5.a. If fixes is empty the rule passes.
        5.b. If fixes isn't empty we return a LintResult object with fixable violations.
        """
        self.preferred_first_table_in_join_clause: str

        assert context.segment.is_type("from_expression")

        # PART 0.
        table_aliases: list[str] = []

        children = FunctionalContext(context).segment.children()

        join_clauses = children.select(sp.is_type("join_clause"))

        join_on_conditions = join_clauses.children().select(
            sp.is_type("join_on_condition")
        )

        # we only care about join_on_condition segments
        if len(join_on_conditions) == 0:
            return None

        from_expression__from_expression_element: Any = children.first(
            sp.is_type("from_expression_element")
        )[0]

        # the first alias comes from the from clause
        table_aliases.append(
            from_expression__from_expression_element.get_eventual_alias().ref_str
        )

        # the rest of the aliases come from the different join clauses
        join_clause_list: list[Any] = [clause for clause in join_clauses]

        join_clause_aliases: list[str] = [
            join_clause_list[i].get_eventual_aliases()[0][1].ref_str
            for i in range(len(join_clause_list))
        ]

        table_aliases = table_aliases + join_clause_aliases

        table_aliases = [alias.upper() for alias in table_aliases]

        # PART 1.
        conditions: list[list[BaseSegment]] = []

        join_on_condition__expressions = join_on_conditions.children().select(
            sp.is_type("expression")
        )

        # we exclude segments of type whitespace or newline
        for expression in join_on_condition__expressions:
            expression_group = []
            for element in Segments(expression).children():
                if element.type not in ("whitespace", "newline"):
                    expression_group.append(element)
            conditions.append(expression_group)

        # PART 2.
        subconditions: list[list[list[BaseSegment]]] = []

        for expression_group in conditions:
            subconditions.append(
                self._split_list_by_segment_type(
                    segment_list=expression_group,
                    delimiter_type="binary_operator",
                    delimiters=["and", "or"],
                )
            )

        subconditions_flattened: list[list[BaseSegment]] = [
            item for sublist in subconditions for item in sublist
        ]

        # PART 3.
        column_operator_column_subconditions: list[list[BaseSegment]] = [
            subcondition
            for subcondition in subconditions_flattened
            if self._is_column_operator_column_sequence(subcondition)
        ]

        # PART 4.
        fixes: list[LintFix] = []

        for subcondition in column_operator_column_subconditions:
            comparison_operator = Segments(subcondition[1])
            first_column_reference = Segments(subcondition[0])
            second_column_reference = Segments(subcondition[2])
            raw_comparison_operators = comparison_operator.children().select(
                sp.is_type("raw_comparison_operator")
            )
            first_table = (
                first_column_reference.children()
                .first(sp.is_type("naked_identifier"))[0]
                .raw_upper
            )
            second_table = (
                second_column_reference.children()
                .first(sp.is_type("naked_identifier"))[0]
                .raw_upper
            )

            # if we swap the two column references around the comparison operator
            # we might have to replace the comparison operator with a different one
            raw_comparison_operator_opposites = {"<": ">", ">": "<"}

            if (
                table_aliases.index(first_table) > table_aliases.index(second_table)
                and self.preferred_first_table_in_join_clause == "left"
            ) or (
                table_aliases.index(first_table) < table_aliases.index(second_table)
                and self.preferred_first_table_in_join_clause == "right"
            ):
                fixes = (
                    fixes
                    + [
                        LintFix.replace(
                            first_column_reference[0],
                            [second_column_reference[0]],
                        )
                    ]
                    + [
                        LintFix.replace(
                            second_column_reference[0],
                            [first_column_reference[0]],
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

        # PART 5.a.
        if fixes == []:
            return None

        # PART 5.b.
        else:
            return LintResult(anchor=context.segment, fixes=fixes)

    @staticmethod
    def _split_list_by_segment_type(
        segment_list: list[BaseSegment], delimiter_type: str, delimiters: list[str]
    ) -> list:
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
    def _is_column_operator_column_sequence(segment_list: list[BaseSegment]) -> bool:
        # Check if list is made up of a column_reference segment,
        # a comparison_operator segment and another column_reference segment
        if len(segment_list) != 3:
            return False
        if (
            segment_list[0].type == "column_reference"
            and segment_list[1].type == "comparison_operator"
            and segment_list[2].type == "column_reference"
        ):
            return True
        return False
