"""Implementation of Rule L004."""
from sqlfluff.core.parser import WhitespaceSegment
from sqlfluff.core.rules.base import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_fix_compatible,
    document_configuration,
)


@document_fix_compatible
@document_configuration
class Rule_L004(BaseRule):
    """Incorrect indentation type.

    Note 1: spaces are only fixed to tabs if the number of spaces in the
    indent is an integer multiple of the tab_space_size config.
    Note 2: fixes are only applied to indents at the start of a line. Indents
    after other text on the same line are not fixed.

    | **Anti-pattern**
    | Using tabs instead of spaces when indent_unit config set to spaces (default).

    .. code-block:: sql
       :force:

        select
        ••••a,
        →   b
        from foo

    | **Best practice**
    | Change the line to use spaces only.

    .. code-block:: sql
       :force:

        select
        ••••a,
        ••••b
        from foo
    """

    config_keywords = ["indent_unit", "tab_space_size"]

    # TODO fix indents after text: https://github.com/sqlfluff/sqlfluff/pull/590#issuecomment-739484190
    def _eval(self, context: RuleContext) -> LintResult:
        """Incorrect indentation found in file."""
        # Config type hints
        self.tab_space_size: int
        self.indent_unit: str

        tab = "\t"
        space = " "
        correct_indent = (
            space * self.tab_space_size if self.indent_unit == "space" else tab
        )
        wrong_indent = (
            tab if self.indent_unit == "space" else space * self.tab_space_size
        )
        if (
            context.segment.is_type("whitespace")
            and wrong_indent in context.segment.raw
        ):
            fixes = []
            description = "Incorrect indentation type found in file."
            edit_indent = context.segment.raw.replace(wrong_indent, correct_indent)
            # Ensure that the number of space indents is a multiple of tab_space_size
            # before attempting to convert spaces to tabs to avoid mixed indents
            # unless we are converted tabs to spaces (indent_unit = space)
            if (
                (
                    self.indent_unit == "space"
                    or context.segment.raw.count(space) % self.tab_space_size == 0
                )
                # Only attempt a fix at the start of a newline for now
                and (
                    len(context.raw_stack) == 0
                    or context.raw_stack[-1].is_type("newline")
                )
            ):
                fixes = [
                    LintFix.replace(
                        context.segment,
                        [
                            WhitespaceSegment(raw=edit_indent),
                        ],
                    )
                ]
            elif not (
                len(context.raw_stack) == 0 or context.raw_stack[-1].is_type("newline")
            ):
                # give a helpful message if the wrong indent has been found and is not at the start of a newline
                description += (
                    " The indent occurs after other text, so a manual fix is needed."
                )
            else:
                # If we get here, the indent_unit is tabs, and the number of spaces is not a multiple of tab_space_size
                description += " The number of spaces is not a multiple of tab_space_size, so a manual fix is needed."
            return LintResult(
                anchor=context.segment, fixes=fixes, description=description
            )
        return LintResult()
