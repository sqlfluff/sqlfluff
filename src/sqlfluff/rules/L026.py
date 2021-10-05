"""Implementation of Rule L026."""

from sqlfluff.core.rules.analysis.select import get_aliases_from_select
from sqlfluff.core.rules.base import LintResult
from sqlfluff.core.rules.doc_decorators import document_configuration
from sqlfluff.rules.L025 import Rule_L020


@document_configuration
class Rule_L026(Rule_L020):
    """References cannot reference objects not present in FROM clause.

    NB: This rule is disabled by default for BigQuery due to its use of
    structs which trigger false positives. It can be enabled with the
    `force_enable = True` flag.

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

    config_keywords = ["force_enable"]

    @staticmethod
    def _is_bad_tbl_ref(table_aliases, parent_select, tbl_ref):
        """Given a table reference, try to find what it's referring to."""
        # Is it referring to one of the table aliases?
        if tbl_ref[0] in [a.ref_str for a in table_aliases]:
            # Yes. Therefore okay.
            return False

        # Not a table alias. It it referring to a correlated subquery?
        if parent_select:
            parent_aliases, _ = get_aliases_from_select(parent_select)
            if parent_aliases and tbl_ref[0] in [a[0] for a in parent_aliases]:
                # Yes. Therefore okay.
                return False

        # It's not referring to an alias or a correlated subquery. Looks like a
        # bad reference (i.e. referring to something unknown.)
        return True

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
            tbl_refs = r.extract_possible_references(level=r.ObjectReferenceLevel.TABLE)
            if tbl_refs and all(
                self._is_bad_tbl_ref(table_aliases, parent_select, tbl_ref)
                for tbl_ref in tbl_refs
            ):
                violation_buff.append(
                    LintResult(
                        # Return the first segment rather than the string
                        anchor=tbl_refs[0].segments[0],
                        description=f"Reference {r.raw!r} refers to table/view "
                        "not found in the FROM clause or found in parent "
                        "subquery.",
                    )
                )
        return violation_buff or None

    def _eval(self, segment, parent_stack, dialect, **kwargs):
        """Override Rule L020 for dialects that use structs.

        Some dialects use structs (e.g. column.field) which look like
        table references and so incorrectly trigger this rule.
        """
        if dialect.name in ["bigquery"] and not self.force_enable:
            return LintResult()

        return super()._eval(segment, parent_stack, dialect, **kwargs)
