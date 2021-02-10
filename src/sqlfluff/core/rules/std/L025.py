"""Implementation of Rule L025."""

from ..base import LintResult
from sqlfluff.core.rules.std.L020 import Rule_L020
from sqlfluff.core.dialects.dialect_ansi import AliasInfo

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

        alias: AliasInfo
        for alias in table_aliases:
            if alias.aliased and alias.ref_str not in tbl_refs:
                violation_buff.append(
                    LintResult(
                        anchor=alias.segment,
                        description="Alias {0!r} is never used in SELECT statement.".format(
                            alias.ref_str
                        ),
                    )
                )
        return violation_buff or None
