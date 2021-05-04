"""Implementation of Rule L020."""

import itertools

from sqlfluff.core.rules.base import BaseRule, LintResult
from sqlfluff.core.rules.analysis.select import get_select_statement_info


class Rule_L020(BaseRule):
    """Table aliases should be unique within each clause."""

    def _lint_references_and_aliases(
        self,
        table_aliases,
        value_table_function_aliases,
        references,
        col_aliases,
        using_cols,
        parent_select,
    ):
        """Check whether any aliases are duplicates.

        NB: Subclasses of this error should override this function.

        """
        # Are any of the aliases the same?
        for a1, a2 in itertools.combinations(table_aliases, 2):
            # Compare the strings
            if a1.ref_str == a2.ref_str and a1.ref_str:
                # If there are any, then the rest of the code
                # won't make sense so just return here.
                return [
                    LintResult(
                        # Reference the element, not the string.
                        anchor=a2.segment,
                        description=(
                            "Duplicate table alias {0!r}. Table "
                            "aliases should be unique."
                        ).format(a2.ref_str),
                    )
                ]
        return None

    def _eval(self, segment, parent_stack, dialect, **kwargs):
        """Get References and Aliases and allow linting.

        This rule covers a lot of potential cases of odd usages of
        references, see the code for each of the potential cases.

        Subclasses of this rule should override the
        `_lint_references_and_aliases` method.
        """
        if segment.is_type("select_statement"):
            select_info = get_select_statement_info(segment, dialect)
            if not select_info:
                return None

            # Work out if we have a parent select function
            parent_select = None
            for seg in reversed(parent_stack):
                if seg.is_type("select_statement"):
                    parent_select = seg
                    break

            # Pass them all to the function that does all the work.
            # NB: Subclasses of this rules should override the function below
            return self._lint_references_and_aliases(
                select_info.table_aliases,
                select_info.value_table_function_aliases,
                select_info.reference_buffer,
                select_info.col_aliases,
                select_info.using_cols,
                parent_select,
            )
        return None
