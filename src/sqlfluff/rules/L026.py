"""Implementation of Rule L026."""

from sqlfluff.core.rules.analysis.select import get_aliases_from_select
from sqlfluff.core.rules.base import LintResult
from sqlfluff.rules.L025 import Rule_L020


class Rule_L026(Rule_L020):
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

    @staticmethod
    def _is_bad_tbl_ref(table_aliases, parent_select, tbl_ref):
        if tbl_ref and tbl_ref[0] not in [a.ref_str for a in table_aliases]:
            # Last check, this *might* be a correlated subquery reference.
            if parent_select:
                parent_aliases, _ = get_aliases_from_select(parent_select)
                if parent_aliases and tbl_ref[0] in [a[0] for a in
                                                     parent_aliases]:
                    return False
            return True
        return False

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
            tbl_refs = r.extract_possible_references(level=2)
            if tbl_refs and all(
                self._is_bad_tbl_ref(table_aliases, parent_select, tbl_ref)
                for tbl_ref in tbl_refs
            ):
                violation_buff.append(
                    LintResult(
                        # Return the first segment rather than the string
                        anchor=tbl_refs[0].segments[0],
                        description="Reference {0!r} refers to table/view "
                        "not found in the FROM clause or found in parent"
                        "subquery.".format(r.raw),
                    )
                )
        return violation_buff or None
