"""Implementation of Rule L002."""

from sqlfluff.core.rules.base import BaseCrawler, LintResult, LintFix
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)


@document_configuration
@document_fix_compatible
class Rule_L002(BaseCrawler):
    """Mixed Tabs and Spaces in single whitespace.

    This rule will fail if a single section of whitespace
    contains both tabs and spaces.

    | **Anti-pattern**
    | The • character represents a space and the → character represents a tab.
    | In this example, the second line contains two spaces and one tab.

    .. code-block::

        SELECT
        ••→a
        FROM foo

    | **Best practice**
    | Change the line to use spaces only.

    .. code-block::

        SELECT
        ••••a
        FROM foo

    """

    config_keywords = ["tab_space_size"]

    def _eval(self, segment, raw_stack, **kwargs):
        """Mixed Tabs and Spaces in single whitespace.

        Only trigger from whitespace segments if they contain
        multiple kinds of whitespace.
        """
        if segment.is_type("whitespace"):
            if " " in segment.raw and "\t" in segment.raw:
                if len(raw_stack) == 0 or raw_stack[-1].is_type("newline"):
                    # We've got a single whitespace at the beginning of a line.
                    # It's got a mix of spaces and tabs. Replace each tab with
                    # a multiple of spaces
                    return LintResult(
                        anchor=segment,
                        fixes=[
                            LintFix(
                                "edit",
                                segment,
                                segment.edit(
                                    segment.raw.replace("\t", " " * self.tab_space_size)
                                ),
                            )
                        ],
                    )
