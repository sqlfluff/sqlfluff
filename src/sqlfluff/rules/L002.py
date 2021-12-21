"""Implementation of Rule L002."""
from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)


@document_configuration
@document_fix_compatible
class Rule_L002(BaseRule):
    """Mixed Tabs and Spaces in single whitespace.

    This rule will fail if a single section of whitespace
    contains both tabs and spaces.

    | **Anti-pattern**
    | The • character represents a space and the → character represents a tab.
    | In this example, the second line contains two spaces and one tab.

    .. code-block:: sql
       :force:

        SELECT
        ••→a
        FROM foo

    | **Best practice**
    | Change the line to use spaces only.

    .. code-block:: sql
       :force:

        SELECT
        ••••a
        FROM foo

    """

    config_keywords = ["tab_space_size"]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Mixed Tabs and Spaces in single whitespace.

        Only trigger from whitespace segments if they contain
        multiple kinds of whitespace.
        """
        # Config type hints
        self.tab_space_size: int

        if context.segment.is_type("whitespace"):
            if " " in context.segment.raw and "\t" in context.segment.raw:
                if len(context.raw_stack) == 0 or context.raw_stack[-1].is_type(
                    "newline"
                ):
                    # We've got a single whitespace at the beginning of a line.
                    # It's got a mix of spaces and tabs. Replace each tab with
                    # a multiple of spaces
                    return LintResult(
                        anchor=context.segment,
                        fixes=[
                            LintFix.replace(
                                context.segment,
                                [
                                    context.segment.edit(
                                        context.segment.raw.replace(
                                            "\t", " " * self.tab_space_size
                                        )
                                    ),
                                ],
                            ),
                        ],
                    )
        return None
