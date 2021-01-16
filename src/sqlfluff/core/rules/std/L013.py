"""Implementation of Rule L013."""

from sqlfluff.core.rules.base import BaseCrawler, LintResult
from sqlfluff.core.rules.doc_decorators import document_configuration


@document_configuration
class Rule_L013(BaseCrawler):
    """Column expression without alias. Use explicit `AS` clause.

    | **Anti-pattern**
    | In this example, there is no alias for both sums.

    .. code-block:: sql

        SELECT
            sum(a),
            sum(b)
        FROM foo

    | **Best practice**
    | Add aliases.

    .. code-block:: sql

        SELECT
            sum(a) AS a_sum,
            sum(b) AS b_sum
        FROM foo

    """

    config_keywords = ["allow_scalar"]

    def _eval(self, segment, parent_stack, **kwargs):
        """Column expression without alias. Use explicit `AS` clause.

        We look for the select_target_element segment, and then evaluate
        whether it has an alias segment or not and whether the expression
        is complicated enough. `parent_stack` is to assess how many other
        elements there are.

        """
        if segment.is_type("select_target_element"):
            if not any(e.is_type("alias_expression") for e in segment.segments):
                types = {e.type for e in segment.segments if e.name != "star"}
                unallowed_types = types - {
                    "whitespace",
                    "newline",
                    "column_reference",
                    "wildcard_expression",
                }
                if len(unallowed_types) > 0:
                    # No fixes, because we don't know what the alias should be,
                    # the user should document it themselves.
                    if self.allow_scalar:
                        # Check *how many* elements there are in the select
                        # statement. If this is the only one, then we won't
                        # report an error.
                        num_elements = sum(
                            e.is_type("select_target_element")
                            for e in parent_stack[-1].segments
                        )
                        if num_elements > 1:
                            return LintResult(anchor=segment)
                        else:
                            return None
                    else:
                        # Just error if we don't care.
                        return LintResult(anchor=segment)
        return None
