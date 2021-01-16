"""Implementation of Rule L029."""


from sqlfluff.core.rules.base import BaseCrawler, LintResult
from sqlfluff.core.rules.doc_decorators import document_configuration


@document_configuration
class Rule_L029(BaseCrawler):
    """Keywords should not be used as identifiers.

    | **Anti-pattern**
    | In this example, SUM function is used as an alias.

    .. code-block:: sql

        SELECT
            sum.a
        FROM foo AS sum

    | **Best practice**
    |  Avoid keywords as the name of an alias.

    .. code-block:: sql

        SELECT
            vee.a
        FROM foo AS vee

    """

    config_keywords = ["only_aliases"]

    def _eval(self, segment, dialect, parent_stack, **kwargs):
        """Keywords should not be used as identifiers."""
        if segment.name == "naked_identifier":
            # If self.only_aliases is true, we're a bit pickier here
            if self.only_aliases:
                # Aliases are ok (either directly, or in column definitions or in with statements)
                if parent_stack[-1].is_type(
                    "alias_expression", "column_definition", "with_compound_statement"
                ):
                    pass
                # All other references may not be at the discretion of the developer, so leave them out
                else:
                    return None
            # Actually lint
            if segment.raw.upper() in dialect.sets("unreserved_keywords"):
                return LintResult(anchor=segment)
