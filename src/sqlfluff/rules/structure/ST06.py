"""Implementation of Rule ST06."""

from typing import Iterator, List, Optional, Tuple, Union

from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import (
    BaseRule,
    EvalResultType,
    LintFix,
    LintResult,
    RuleContext,
)
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_ST06(BaseRule):
    """Select wildcards then simple targets before calculations and aggregates.

    **Anti-pattern**

    .. code-block:: sql

        select
            a,
            *,
            row_number() over (partition by id order by date) as y,
            b
        from x


    **Best practice**

    Order ``select`` targets in ascending complexity

    .. code-block:: sql

        select
            *,
            a,
            b,
            row_number() over (partition by id order by date) as y
        from x

    """

    name = "structure.column_order"
    aliases = ("L034",)
    groups = ("all", "structure")
    crawl_behaviour = SegmentSeekerCrawler({"select_clause"})
    is_fix_compatible = True

    def _validate(self, i: int, segment: BaseSegment) -> None:
        # Check if we've seen a more complex select target element already
        if self.seen_band_elements[i + 1 : :] != [[]] * len(
            self.seen_band_elements[i + 1 : :]
        ):
            # Found a violation (i.e. a simpler element that *follows* a more
            # complex element.
            self.violation_exists = True
        self.current_element_band: Optional[int] = i
        self.seen_band_elements[i].append(segment)

    def _eval(self, context: RuleContext) -> EvalResultType:
        self.violation_exists = False
        # Bands of select targets in order to be enforced
        select_element_order_preference: Tuple[
            Tuple[Union[str, Tuple[str, ...]], ...], ...
        ] = (
            ("wildcard_expression",),
            (
                "object_reference",
                "literal",
                "cast_expression",
                ("function", "cast"),
                ("expression", "cast_expression"),
            ),
        )

        # Track which bands have been seen, with additional empty list for the
        # non-matching elements. If we find a matching target element, we append the
        # element to the corresponding index.
        self.seen_band_elements: List[List[BaseSegment]] = [
            [] for _ in select_element_order_preference
        ] + [
            []
        ]  # type: ignore

        assert context.segment.is_type("select_clause")
        # Ignore select clauses which belong to:
        # - set expression, which is most commonly a union
        # - insert_statement
        # - create table statement
        #
        # In each of these contexts, the order of columns in a select should
        # be preserved.
        if len(context.parent_stack) >= 2 and context.parent_stack[-2].is_type(
            "insert_statement", "set_expression"
        ):
            return None
        if (
            len(context.parent_stack) >= 3
            and context.parent_stack[-3].is_type("insert_statement", "set_expression")
            and context.parent_stack[-2].is_type("with_compound_statement")
        ):
            return None
        if len(context.parent_stack) >= 3 and context.parent_stack[-3].is_type(
            "create_table_statement", "merge_statement"
        ):
            return None
        if (
            len(context.parent_stack) >= 4
            and context.parent_stack[-4].is_type(
                "create_table_statement", "merge_statement"
            )
            and context.parent_stack[-2].is_type("with_compound_statement")
        ):
            return None

        select_clause_segment = context.segment
        select_target_elements = context.segment.get_children("select_clause_element")
        if not select_target_elements:
            return None

        # Iterate through all the select targets to find any order violations
        for segment in select_target_elements:
            # The band index of the current segment in
            # select_element_order_preference
            self.current_element_band = None

            # Compare the segment to the bands in select_element_order_preference
            for i, band in enumerate(select_element_order_preference):
                for e in band:
                    # Identify simple select target
                    if isinstance(e, str) and segment.get_child(e):
                        self._validate(i, segment)

                    # Identify function
                    elif isinstance(e, tuple) and e[0] == "function":
                        try:
                            _function = segment.get_child("function")
                            assert _function
                            _function_name = _function.get_child("function_name")
                            assert _function_name
                            if _function_name.raw == e[1]:
                                self._validate(i, segment)
                        except (AttributeError, AssertionError):
                            # If the segment doesn't match
                            pass

                    # Identify simple expression
                    elif isinstance(e, tuple) and e[0] == "expression":
                        try:
                            _expression = segment.get_child("expression")
                            assert _expression

                            if (
                                _expression.get_child(e[1])
                                and _expression.segments[0].type
                                in (
                                    "column_reference",
                                    "object_reference",
                                    "literal",
                                    "cast_expression",
                                )
                                # len == 2 to ensure the expression is 'simple'
                                and (
                                    len(_expression.segments) == 2
                                    # cast_expression is one length
                                    or len(_expression.segments) == 1
                                )
                            ):
                                self._validate(i, segment)
                        except (AttributeError, AssertionError):
                            # If the segment doesn't match
                            pass

            # If the target doesn't exist in select_element_order_preference then it
            # is 'complex' and must go last
            if self.current_element_band is None:
                self.seen_band_elements[-1].append(segment)

        if self.violation_exists:
            if len(context.parent_stack) and any(
                self._implicit_column_references(context.parent_stack[-1])
            ):
                # If there are implicit column references (i.e. column
                # numbers), warn but don't fix, because it's much more
                # complicated to autofix.
                return LintResult(anchor=select_clause_segment)
            # Create a list of all the edit fixes
            # We have to do this at the end of iterating through all the
            # select_target_elements to get the order correct. This means we can't
            # add a lint fix to each individual LintResult as we go
            ordered_select_target_elements = [
                segment for band in self.seen_band_elements for segment in band
            ]
            # TODO: The "if" in the loop below compares corresponding items
            # to avoid creating "do-nothing" edits. A potentially better
            # approach would leverage difflib.SequenceMatcher.get_opcodes(),
            # which generates a list of edit actions (similar to the
            # command-line "diff" tool in Linux). This is more complex to
            # implement, but minimizing the number of LintFixes makes the
            # final application of patches (in "sqlfluff fix") more robust.
            fixes = [
                LintFix.replace(
                    initial_select_target_element,
                    [replace_select_target_element],
                )
                for initial_select_target_element, replace_select_target_element in zip(  # noqa: E501
                    select_target_elements, ordered_select_target_elements
                )
                if initial_select_target_element is not replace_select_target_element
            ]
            # Anchoring on the select statement segment ensures that
            # select statements which include macro targets are ignored
            # when ignore_templated_areas is set
            return LintResult(anchor=select_clause_segment, fixes=fixes)

        return None

    @classmethod
    def _implicit_column_references(cls, segment: BaseSegment) -> Iterator[BaseSegment]:
        """Yield any implicit ORDER BY or GROUP BY column references.

        This function was adapted from similar code in AM06.
        """
        _ignore_types: List[str] = ["withingroup_clause", "window_specification"]
        if not segment.is_type(*_ignore_types):  # Ignore Windowing clauses
            if segment.is_type("groupby_clause", "orderby_clause"):
                for seg in segment.segments:
                    if seg.is_type("numeric_literal"):
                        yield segment
            else:
                for seg in segment.segments:
                    yield from cls._implicit_column_references(seg)
