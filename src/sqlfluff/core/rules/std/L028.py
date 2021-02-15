"""Implementation of Rule L028."""

from sqlfluff.core.rules.base import LintResult
from sqlfluff.core.rules.doc_decorators import document_configuration
from sqlfluff.core.rules.std.L025 import Rule_L025


@document_configuration
class Rule_L028(Rule_L025):
    """References should be consistent in statements with a single table.

    | **Anti-pattern**
    | In this example, only the field `b` is referenced.

    .. code-block:: sql

        SELECT
            a,
            foo.b
        FROM foo

    | **Best practice**
    |  Remove all the reference or reference all the fields.

    .. code-block:: sql

        SELECT
            a,
            b
        FROM foo

        -- Also good

        SELECT
            foo.a,
            foo.b
        FROM foo

    """

    config_keywords = ["single_table_references"]

    def _lint_references_and_aliases(
        self,
        table_aliases,
        value_table_function_aliases,
        references,
        col_aliases,
        using_cols,
        parent_select,
    ):
        """Iterate through references and check consistency."""
        # How many aliases are there? If more than one then abort.
        if len(table_aliases) > 1:
            return None
        standalone_aliases = [t[0] for t in value_table_function_aliases]
        # A buffer to keep any violations.
        violation_buff = []
        # Check all the references that we have.
        seen_ref_types = set()
        for ref in references:
            # We skip any unqualified wildcard references (i.e. *). They shouldn't count.
            if not ref.is_qualified() and ref.is_type("wildcard_identifier"):
                continue
            # Oddball case: Column aliases provided via function calls in by
            # FROM or JOIN. References to these don't need to be qualified.
            # Note there could be a table with a column by the same name as
            # this alias, so avoid bogus warnings by just skipping them
            # entirely rather than trying to enforce anything.
            if ref.raw in standalone_aliases:
                continue
            this_ref_type = ref.qualification()
            if self.single_table_references == "consistent":
                if seen_ref_types and this_ref_type not in seen_ref_types:
                    violation_buff.append(
                        LintResult(
                            anchor=ref,
                            description="{0} reference {1!r} found in single table select which is inconsistent with previous references.".format(
                                this_ref_type.capitalize(), ref.raw
                            ),
                        )
                    )
            elif self.single_table_references != this_ref_type:
                violation_buff.append(
                    LintResult(
                        anchor=ref,
                        description="{0} reference {1!r} found in single table select.".format(
                            this_ref_type.capitalize(), ref.raw
                        ),
                    )
                )
            seen_ref_types.add(this_ref_type)

        return violation_buff or None
