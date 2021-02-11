"""Implementation of Rule L025."""

from src.sqlfluff.core.rules.base import LintResult
from sqlfluff.core.rules.std.L020 import Rule_L020


class Rule_L025(Rule_L020):
    """Tables should not be aliased if that alias is not used.

    | **Anti-pattern**

    .. code-block:: sql

        SELECT
            a
        FROM foo AS zoo

    | **Best practice**
    | Use the alias or remove it. An unused alias makes code
    | harder to read without changing any functionality.

    .. code-block:: sql

        SELECT
            zoo.a
        FROM foo AS zoo

        -- Alternatively...

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
        """Check all aliased references against tables referenced in the query."""
        # A buffer to keep any violations.
        violation_buff = []
        # Check all the references that we have, keep track of which aliases we refer to.
        tbl_refs = set()
        for r in references:
            tbl_ref = r.extract_reference(level=2)
            if tbl_ref:
                tbl_refs.add(tbl_ref[0])

        for ref_str, seg, aliased in table_aliases:
            if aliased and ref_str not in tbl_refs:
                violation_buff.append(
                    LintResult(
                        anchor=seg,
                        description="Alias {0!r} is never used in SELECT statement.".format(
                            ref_str
                        ),
                    )
                )
        return violation_buff or None
