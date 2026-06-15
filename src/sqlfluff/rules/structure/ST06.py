"""Implementation of Rule ST06."""

from collections.abc import Iterator
from typing import Optional, Union

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

    def _is_view_with_explicit_columns(self, context: RuleContext) -> bool:
        """Check if SELECT is in a CREATE VIEW with explicit column list.

        Args:
            context: The rule context containing parent stack

        Returns:
            True if this SELECT is in a CREATE VIEW with explicit columns
        """
        # Traverse parent stack looking for create_view_statement
        for parent in context.parent_stack:
            if parent.is_type("create_view_statement"):
                # Check if the view has an explicit column list
                # Look for a bracketed segment containing column references
                for child in parent.segments:
                    if child.is_type("bracketed"):
                        # Check if this bracketed segment contains column references
                        # ANSI-based dialects (Snowflake, PostgreSQL, etc.)
                        # use column_reference
                        if any(
                            seg.is_type("column_reference")
                            for seg in child.recursive_crawl("column_reference")
                        ):
                            return True
                        # T-SQL dialect uses index_column_definition instead
                        if any(
                            seg.is_type("index_column_definition")
                            for seg in child.recursive_crawl("index_column_definition")
                        ):
                            return True
                # Found a CREATE VIEW but no explicit column list
                return False
        return False

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

    @classmethod
    def _is_simple_function(cls, segment: BaseSegment) -> bool:
        """Return whether a function segment is considered simple."""
        function_name = segment.get_child("function_name")
        return bool(function_name and function_name.raw_upper == "CAST")

    @classmethod
    def _is_simple_cast_expression(cls, segment: BaseSegment) -> bool:
        """Return whether a cast expression wraps a simple expression."""
        if not segment.is_type("cast_expression"):
            return False
        return cls._is_simple_expression_segment(segment.segments[0])

    @classmethod
    def _is_simple_expression_segment(cls, segment: BaseSegment) -> bool:
        """Return whether a segment should be treated as a simple expression."""
        if segment.is_type("column_reference", "object_reference", "literal"):
            return True
        if segment.is_type("function"):
            return cls._is_simple_function(segment)
        if segment.is_type("cast_expression"):
            return cls._is_simple_cast_expression(segment)
        return False

    @classmethod
    def _is_simple_expression(cls, segment: BaseSegment, child_type: str) -> bool:
        """Return whether an expression child should be treated as simple."""
        if not segment.is_type("expression") or not segment.get_child(child_type):
            return False
        if len(segment.segments) not in (1, 2):
            return False
        return cls._is_simple_expression_segment(segment.segments[0])

    def _eval(self, context: RuleContext) -> EvalResultType:
        self.violation_exists = False
        # Bands of select targets in order to be enforced
        select_element_order_preference: tuple[
            tuple[Union[str, tuple[str, ...]], ...], ...
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
        self.seen_band_elements: list[list[BaseSegment]] = [
            [] for _ in select_element_order_preference
        ] + [[]]  # type: ignore

        assert context.segment.is_type("select_clause")

        # insert, merge, create table, union are order-sensitive
        for seg in reversed(context.parent_stack):
            if seg.is_type(
                "insert_statement",
                "set_expression",
                "create_table_statement",
                "merge_statement",
            ):
                return None

        # CTE is order-sensitive only if CTE is referenced as SELECT * in set expression
        for seg in reversed(context.parent_stack):
            if seg.is_type("common_table_expression"):
                cte_identifier = seg.get_child("identifier")
                assert cte_identifier is not None
                maybe_with_compound_statement = seg.get_parent()
                if maybe_with_compound_statement is None:
                    break  # pragma: no cover
                with_compound_statement, _ = maybe_with_compound_statement
                for ref in with_compound_statement.recursive_crawl("table_reference"):
                    if ref.raw_upper == cte_identifier.raw_upper:
                        path = with_compound_statement.path_to(ref)
                        if any(
                            path_step.segment.is_type("set_expression")
                            for path_step in path
                        ):
                            select_statements = [
                                path_step.segment
                                for path_step in path
                                if path_step.segment.is_type(
                                    "select_statement",
                                    "unordered_select_statement_segment",
                                )
                            ]
                            if any(
                                "wildcard_expression"
                                in select_statement.descendant_type_set
                                for select_statement in select_statements
                            ):
                                return None

        # Skip reordering for CREATE VIEW with explicit column list
        if self._is_view_with_explicit_columns(context):
            return None

        select_clause_segment = context.segment
        select_target_elements = context.segment.get_children("select_clause_element")
        if not select_target_elements:  # pragma: no cover
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
                        child = segment.get_child(e)
                        assert child
                        if e != "cast_expression" or self._is_simple_cast_expression(
                            child
                        ):
                            self._validate(i, segment)

                    # Identify function
                    elif isinstance(e, tuple) and e[0] == "function":
                        try:
                            _function = segment.get_child("function")
                            assert _function
                            if self._is_simple_function(_function):
                                self._validate(i, segment)
                        except (AttributeError, AssertionError):
                            # If the segment doesn't match
                            pass

                    # Identify simple expression
                    elif isinstance(e, tuple) and e[0] == "expression":
                        try:
                            _expression = segment.get_child("expression")
                            assert _expression

                            if self._is_simple_expression(_expression, e[1]):
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
                for initial_select_target_element, replace_select_target_element in zip(
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
        _ignore_types: list[str] = ["withingroup_clause", "window_specification"]
        if not segment.is_type(*_ignore_types):  # Ignore Windowing clauses
            if segment.is_type("groupby_clause", "orderby_clause"):
                for seg in segment.segments:
                    if seg.is_type("numeric_literal"):
                        yield segment
            else:
                for seg in segment.segments:
                    yield from cls._implicit_column_references(seg)
