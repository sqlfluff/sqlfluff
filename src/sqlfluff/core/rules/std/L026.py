"""Implementation of Rule L026."""

from sqlfluff.core.rules.base import LintResult
from sqlfluff.core.rules.std.L025 import Rule_L025


class Rule_L026(Rule_L025):
    """References cannot reference objects not present in FROM clause.

    | **Anti-pattern**
    | In this example, the reference 'vee' has not been declared.

    .. code-block:: sql

        SELECT
            vee.a
        FROM foo

    | **Best practice**
    |  Remove the reference.

    .. code-block:: sql

        SELECT
            a
        FROM foo

    """

    def _lint_references_and_aliases(
        self,
        table_aliases,
        value_table_function_aliases,
        references,
        col_aliases,
        using_cols,
        parent_select,
    ):
        # A buffer to keep any violations.
        violation_buff = []

        # Check all the references that we have, do they reference present aliases?
        for r in references:
            tbl_ref = r.extract_reference(level=2)
            # Check whether the string in the list of strings
            if tbl_ref and tbl_ref[0] not in [a.ref_str for a in table_aliases]:
                # Last check, this *might* be a correlated subquery reference.
                if parent_select:
                    parent_aliases, _ = self._get_aliases_from_select(parent_select)
                    if parent_aliases and tbl_ref[0] in [a[0] for a in parent_aliases]:
                        continue

                violation_buff.append(
                    LintResult(
                        # Return the segment rather than the string
                        anchor=tbl_ref[1],
                        description="Reference {0!r} refers to table/view {1!r} not found in the FROM clause or found in parent subquery.".format(
                            r.raw, tbl_ref[0]
                        ),
                    )
                )
        return violation_buff or None
