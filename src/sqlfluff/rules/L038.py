"""Implementation of Rule L038."""
from typing import Optional

from sqlfluff.core.parser import BaseSegment, SymbolSegment

from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import sp, FunctionalContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L038(BaseRule):
    """Trailing commas within select clause.

    .. note::
       For many database backends this is allowed. For some users
       this may be something they wish to enforce (in line with
       Python best practice). Many database backends regard this
       as a syntax error, and as such the `SQLFluff` default is to
       forbid trailing commas in the select clause.

    **Anti-pattern**

    .. code-block:: sql

        SELECT
            a,
            b,
        FROM foo

    **Best practice**

    .. code-block:: sql

        SELECT
            a,
            b
        FROM foo
    """

    groups = ("all", "core")
    config_keywords = ["select_clause_trailing_comma"]
    crawl_behaviour = SegmentSeekerCrawler({"select_clause"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Trailing commas within select clause."""
        # Config type hints
        self.select_clause_trailing_comma: str

        segment = FunctionalContext(context).segment
        children = segment.children()
        # Iterate content to find last element
        last_content: BaseSegment = children.last(sp.is_code())[0]

        # What mode are we in?
        if self.select_clause_trailing_comma == "forbid":
            # Is it a comma?
            if last_content.is_type("comma"):
                return LintResult(
                    anchor=last_content,
                    fixes=[LintFix.delete(last_content)],
                    description="Trailing comma in select statement forbidden",
                )
        elif self.select_clause_trailing_comma == "require":
            if not last_content.is_type("comma"):
                new_comma = SymbolSegment(",", type="comma")
                return LintResult(
                    anchor=last_content,
                    fixes=[LintFix.replace(last_content, [last_content, new_comma])],
                    description="Trailing comma in select statement required",
                )
        return None
