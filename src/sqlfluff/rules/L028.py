"""Implementation of Rule L028."""

from sqlfluff.core.rules.base import LintResult, EvalResultType, RuleContext
from sqlfluff.core.rules.doc_decorators import document_configuration
from sqlfluff.rules.L020 import Rule_L020


@document_configuration
class Rule_L028(Rule_L020):
    """References should be consistent in statements with a single table.

    .. note::
       This rule is disabled by default for BigQuery due to its use of
       structs which trigger false positives. It can be enabled with the
       ``force_enable = True`` flag.

    **Anti-pattern**

    In this example, only the field ``b`` is referenced.

    .. code-block:: sql

        SELECT
            a,
            foo.b
        FROM foo

    **Best practice**

    Add or remove references to all fields.

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

    config_keywords = ["single_table_references", "force_enable"]
    _allow_select_alias = False

    def _lint_references_and_aliases(
        self,
        table_aliases,
        standalone_aliases,
        references,
        col_aliases,
        using_cols,
        parent_select,
    ):
        """Iterate through references and check consistency."""
        # How many aliases are there? If more than one then abort.
        if len(table_aliases) > 1:
            return None
        # A buffer to keep any violations.
        violation_buff = []
        # Check all the references that we have.
        seen_ref_types = set()
        for ref in references:
            # We skip any unqualified wildcard references (i.e. *). They shouldn't
            # count.
            if not ref.is_qualified() and ref.is_type("wildcard_identifier"):
                continue
            # Oddball case: Column aliases provided via function calls in by
            # FROM or JOIN. References to these don't need to be qualified.
            # Note there could be a table with a column by the same name as
            # this alias, so avoid bogus warnings by just skipping them
            # entirely rather than trying to enforce anything.
            if ref.raw in standalone_aliases:
                continue

            # Certain dialects allow use of SELECT alias in WHERE clauses
            col_alias_names = [c.alias_identifier_name for c in col_aliases]
            if self._allow_select_alias and ref.raw in col_alias_names:
                continue
            this_ref_type = ref.qualification()
            if self.single_table_references == "consistent":
                if seen_ref_types and this_ref_type not in seen_ref_types:
                    violation_buff.append(
                        LintResult(
                            anchor=ref,
                            description=f"{this_ref_type.capitalize()} reference "
                            f"{ref.raw!r} found in single table select which is "
                            "inconsistent with previous references.",
                        )
                    )
            elif self.single_table_references != this_ref_type:
                violation_buff.append(
                    LintResult(
                        anchor=ref,
                        description="{} reference {!r} found in single table "
                        "select.".format(this_ref_type.capitalize(), ref.raw),
                    )
                )
            seen_ref_types.add(this_ref_type)

        return violation_buff or None

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Override base class for dialects that use structs, or SELECT aliases."""
        # Config type hints
        self.force_enable: bool

        # Some dialects use structs (e.g. column.field) which look like
        # table references and so incorrectly trigger this rule.
        if (
            context.dialect.name in ["bigquery", "hive", "redshift"]
            and not self.force_enable
        ):
            return LintResult()

        # Certain dialects allow use of SELECT alias in WHERE clauses
        if context.dialect.name in ["snowflake", "redshift"]:
            self._allow_select_alias = True

        return super()._eval(context=context)
