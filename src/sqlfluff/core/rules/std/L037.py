"""Implementation of Rule L037."""

from typing import NamedTuple, Optional, List

from sqlfluff.core.rules.base import BaseCrawler, LintFix, LintResult
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


class OrderByColumnInfo(NamedTuple):
    """For L037, segment that ends an ORDER BY column and any order provided."""

    separator: BaseSegment
    order: Optional[str]  # One of 'ASC'/'DESC'/None


@document_fix_compatible
class Rule_L037(BaseCrawler):
    """Ambiguous ordering directions for columns in order by clause.

    | **Anti-pattern**

    .. code-block::

        SELECT
            a, b
        FROM foo
        ORDER BY a, b DESC

    | **Best practice**
    | If any columns in the ORDER BY clause specify ASC or DESC, they should all
      do so.

    .. code-block::

        SELECT
            a, b
        FROM foo
        ORDER BY a ASC, b DESC
    """

    @staticmethod
    def _get_orderby_info(segment: BaseSegment) -> List[OrderByColumnInfo]:
        assert segment.is_type("orderby_clause")

        result = []
        found_column_reference = False
        ordering_reference = None
        for child_segment in segment.segments:
            if child_segment.is_type("column_reference"):
                found_column_reference = True
            elif child_segment.is_type("keyword") and child_segment.name in (
                "ASC",
                "DESC",
            ):
                ordering_reference = child_segment.name
            elif found_column_reference and child_segment.type not in [
                "keyword",
                "whitespace",
                "indent",
                "dedent",
            ]:
                result.append(
                    OrderByColumnInfo(separator=child_segment, order=ordering_reference)
                )

                # Reset findings
                found_column_reference = False
                ordering_reference = None

        # Special handling for last column
        if found_column_reference:
            result.append(
                OrderByColumnInfo(
                    separator=segment.segments[-1], order=ordering_reference
                )
            )
        return result

    def _eval(self, segment, parent_stack, **kwargs):
        """Ambiguous ordering directions for columns in order by clause.

        This rule checks if some ORDER BY columns explicitly specify ASC or
        DESC and some don't.
        """
        # We only trigger on orderby_clause
        if segment.is_type("orderby_clause"):
            lint_fixes = []
            orderby_spec = self._get_orderby_info(segment)
            order_types = {o.order for o in orderby_spec}
            # If ALL columns or NO columns explicitly specify ASC/DESC, all is
            # well.
            if None not in order_types or order_types == {None}:
                return None

            # There's a mix of explicit and default sort order. Make everything
            # explicit.
            for col_info in orderby_spec:
                if not col_info.order:
                    # Since ASC is default in SQL, add in ASC for fix
                    new_whitespace = self.make_whitespace(
                        raw=" ", pos_marker=col_info.separator.pos_marker
                    )
                    new_keyword = self.make_keyword(
                        raw="ASC", pos_marker=col_info.separator.pos_marker
                    )
                    order_lint_fix = LintFix(
                        "create", col_info.separator, [new_whitespace, new_keyword]
                    )
                    lint_fixes.append(order_lint_fix)

            return [
                LintResult(
                    anchor=segment,
                    fixes=lint_fixes,
                    description=(
                        "Ambiguous order by clause. Order by "
                        "clauses should specify order direction for ALL columns or NO columns."
                    ),
                )
            ]
        return None
