"""Implementation of Rule L038."""

from ..base import BaseCrawler, LintFix, LintResult
from ..doc_decorators import document_fix_compatible, document_configuration


@document_configuration
@document_fix_compatible
class Rule_L038(BaseCrawler):
    """Trailing commas within select clause.

    For some database backends this is allowed. For some users
    this may be something they wish to enforce (in line with
    python best practice). Many database backends regard this
    as a syntax error, and as such the sqlfluff default is to
    forbid trailing commas in the select clause.

    | **Anti-pattern**

    .. code-block::

        SELECT
            a, b,
        FROM foo

    | **Best practice**

    .. code-block::

        SELECT
            a, b
        FROM foo
    """

    config_keywords = ["select_clause_trailing_comma"]

    def _eval(self, segment, parent_stack, **kwargs):
        """Trailing commas within select clause."""
        if segment.is_type("select_clause"):
            # Iterate content to find last element
            last_content = None
            for seg in segment.segments:
                if seg.is_code:
                    last_content = seg

            # What mode are we in?
            if self.select_clause_trailing_comma == "forbid":
                # Is it a comma?
                if last_content.is_type("comma"):
                    return LintResult(
                        anchor=last_content,
                        fixes=[LintFix("delete", last_content)],
                        description="Trailing comma in select statement forbidden",
                    )
            elif self.select_clause_trailing_comma == "require":
                if not last_content.is_type("comma"):
                    new_comma = self.make_symbol(
                        ",", last_content.get_end_pos_marker(), seg_type="comma"
                    )
                    return LintResult(
                        anchor=last_content,
                        fixes=[
                            LintFix("edit", last_content, [last_content, new_comma])
                        ],
                        description="Trailing comma in select statement required",
                    )
        return None
