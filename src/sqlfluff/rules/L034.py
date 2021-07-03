"""Implementation of Rule L034."""

from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L034(BaseRule):
    """Use wildcards then simple targets before calculations and aggregates in select statements.

    | **Anti-pattern**

    .. code-block:: sql

        select
            a,
            *,
            row_number() over (partition by id order by date) as y,
            b
        from x


    | **Best practice**
    |  Order "select" targets in ascending complexity

    .. code-block:: sql

        select
            *,
            a,
            b,
            row_number() over (partition by id order by date) as y
        from x

    """

    def _validate(self, i, segment):
        # Check if we've seen a more complex select target element already
        if self.seen_band_elements[i + 1 : :] != [[]] * len(
            self.seen_band_elements[i + 1 : :]
        ):
            # Found a violation (i.e. a simpler element that *follows* a more
            # complex element.
            self.violation_exists = True
        self.current_element_band = i
        self.seen_band_elements[i].append(segment)

    def _eval(self, segment, parent_stack, **kwargs):
        self.violation_buff = []
        self.violation_exists = False
        # Bands of select targets in order to be enforced
        select_element_order_preference = (
            ("wildcard_expression",),
            (
                "object_reference",
                "literal",
                "cast_expression",
                ("function", "cast"),
                ("expression", "cast_expression"),
            ),
        )

        # Track which bands have been seen, with additional empty list for the non-matching elements
        # If we find a matching target element, we append the element to the corresponding index
        self.seen_band_elements = [[] for i in select_element_order_preference] + [[]]

        # Ignore select clauses which belong to a set expression, which are most commonly a union.
        if segment.is_type("select_clause") and not parent_stack[-2].is_type(
            "set_expression"
        ):
            select_clause_segment = segment
            select_target_elements = segment.get_children("select_clause_element")
            if not select_target_elements:
                return None

            # Iterate through all the select targets to find any order violations
            for segment in select_target_elements:
                # The band index of the current segment in select_element_order_preference
                self.current_element_band = None

                # Compare the segment to the bands in select_element_order_preference
                for i, band in enumerate(select_element_order_preference):
                    for e in band:
                        # Identify simple select target
                        if segment.get_child(e):
                            self._validate(i, segment)

                        # Identify function
                        elif type(e) == tuple and e[0] == "function":
                            try:
                                if (
                                    segment.get_child("function")
                                    .get_child("function_name")
                                    .raw
                                    == e[1]
                                ):
                                    self._validate(i, segment)
                            except AttributeError:
                                # If the segment doesn't match
                                pass

                        # Identify simple expression
                        elif type(e) == tuple and e[0] == "expression":
                            try:
                                if (
                                    segment.get_child("expression").get_child(e[1])
                                    and segment.get_child("expression").segments[0].type
                                    in (
                                        "column_reference",
                                        "object_reference",
                                        "literal",
                                    )
                                    # len == 2 to ensure the expression is 'simple'
                                    and len(segment.get_child("expression").segments)
                                    == 2
                                ):
                                    self._validate(i, segment)
                            except AttributeError:
                                # If the segment doesn't match
                                pass

                # If the target doesn't exist in select_element_order_preference then it is 'complex' and must go last
                if self.current_element_band is None:
                    self.seen_band_elements[-1].append(segment)

            if self.violation_exists:
                # Create a list of all the edit fixes
                # We have to do this at the end of iterating through all the select_target_elements to get the order correct
                # This means we can't add a lint fix to each individual LintResult as we go
                ordered_select_target_elements = [
                    segment for band in self.seen_band_elements for segment in band
                ]
                fixes = [
                    LintFix(
                        "edit",
                        initial_select_target_element,
                        replace_select_target_element,
                    )
                    for initial_select_target_element, replace_select_target_element in zip(
                        select_target_elements, ordered_select_target_elements
                    )
                ]
                # Anchoring on the select statement segment ensures that
                # select statements which include macro targets are ignored
                # when ignore_templated_areas is set
                lint_result = LintResult(anchor=select_clause_segment, fixes=fixes)
                self.violation_buff = [lint_result]

        return self.violation_buff or None
