"""Implementation of Rule L027."""

from sqlfluff.core.rules.base import LintResult
from sqlfluff.rules.L020 import Rule_L020


class Rule_L027(Rule_L020):
    """References should be qualified if select has more than one referenced table/view.

    NB: Except if they're present in a USING clause.

    | **Anti-pattern**
    | In this example, the reference 'vee' has not been declared
    | and the variables 'a' and 'b' are potentially ambiguous.

    .. code-block:: sql

        SELECT a, b
        FROM foo
        LEFT JOIN vee ON vee.a = foo.a

    | **Best practice**
    |  Add the references.

    .. code-block:: sql

        SELECT foo.a, vee.b
        FROM foo
        LEFT JOIN vee ON vee.a = foo.a
    """

    def _lint_references_and_aliases(
        self,
        table_aliases,
        standalone_aliases,
        references,
        col_aliases,
        using_cols,
        parent_select,
    ):
        # Do we have more than one? If so, all references should be qualified.
        if len(table_aliases) <= 1:
            return None
        # A buffer to keep any violations.
        violation_buff = []
        # Check all the references that we have.
        for r in references:
            this_ref_type = r.qualification()
            if (
                this_ref_type == "unqualified"
                and r.raw not in col_aliases
                and r.raw not in using_cols
            ):
                violation_buff.append(
                    LintResult(
                        anchor=r,
                        description=f"Unqualified reference {r.raw!r} found in "
                        "select with more than one referenced table/view.",
                    )
                )

        return violation_buff or None
