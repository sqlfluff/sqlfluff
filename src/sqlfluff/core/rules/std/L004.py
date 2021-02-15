"""Implementation of Rule L004."""

from sqlfluff.core.rules.base import BaseCrawler, LintResult, LintFix
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)


@document_fix_compatible
@document_configuration
class Rule_L004(BaseCrawler):
    """Incorrect indentation type.

    Note 1: spaces are only fixed to tabs if the number of spaces in the
    indent is an integer multiple of the tab_space_size config.
    Note 2: fixes are only applied to indents at the start of a line. Indents
    after other text on the same line are not fixed.

    | **Anti-pattern**
    | Using tabs instead of spaces when indent_unit config set to spaces (default).

    .. code-block::

        select
        ••••a,
        →   b
        from foo

    | **Best practice**
    | Change the line to use spaces only.

    .. code-block::

        select
        ••••a,
        ••••b
        from foo
    """

    config_keywords = ["indent_unit", "tab_space_size"]

    # TODO fix indents after text: https://github.com/sqlfluff/sqlfluff/pull/590#issuecomment-739484190
    def _eval(self, segment, raw_stack, **kwargs):
        """Incorrect indentation found in file."""
        tab = "\t"
        space = " "
        correct_indent = (
            space * self.tab_space_size if self.indent_unit == "space" else tab
        )
        wrong_indent = (
            tab if self.indent_unit == "space" else space * self.tab_space_size
        )
        if segment.is_type("whitespace") and wrong_indent in segment.raw:
            fixes = []
            description = "Incorrect indentation type found in file."
            edit_indent = segment.raw.replace(wrong_indent, correct_indent)
            # Ensure that the number of space indents is a multiple of tab_space_size
            # before attempting to convert spaces to tabs to avoid mixed indents
            # unless we are converted tabs to spaces (indent_unit = space)
            if (
                (
                    self.indent_unit == "space"
                    or segment.raw.count(space) % self.tab_space_size == 0
                )
                # Only attempt a fix at the start of a newline for now
                and (len(raw_stack) == 0 or raw_stack[-1].is_type("newline"))
            ):
                fixes = [
                    LintFix(
                        "edit",
                        segment,
                        self.make_whitespace(
                            raw=edit_indent, pos_marker=segment.pos_marker
                        ),
                    )
                ]
            elif not (len(raw_stack) == 0 or raw_stack[-1].is_type("newline")):
                # give a helpful message if the wrong indent has been found and is not at the start of a newline
                description += (
                    " The indent occurs after other text, so a manual fix is needed."
                )
            else:
                # If we get here, the indent_unit is tabs, and the number of spaces is not a multiple of tab_space_size
                description += " The number of spaces is not a multiple of tab_space_size, so a manual fix is needed."
            return LintResult(anchor=segment, fixes=fixes, description=description)
