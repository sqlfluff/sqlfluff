"""Implementation of Rule L028."""

from typing import List, Optional, Set

from sqlfluff.core.dialects.common import AliasInfo, ColumnAliasInfo
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.segments.raw import CodeSegment, SymbolSegment
from sqlfluff.core.rules.base import LintFix, LintResult, EvalResultType, RuleContext
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
            foo.a,
            foo.b
        FROM foo

        -- Also good

        SELECT
            a,
            b
        FROM foo

    """

    config_keywords = [
        "single_table_references",
        "force_enable",
        "fix_inconsistent_to",
    ]
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
        self.single_table_references: str
        self.fix_inconsistent_to: Optional[str]
        return _generate_fixes(
            table_aliases,
            standalone_aliases,
            references,
            col_aliases,
            self.single_table_references,
            self._allow_select_alias,
            self.dialect,
            self.fix_inconsistent_to,
        )

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Override base class for dialects that use structs, or SELECT aliases."""
        # Config type hints
        self.force_enable: bool
        self.dialect: str = context.dialect.name
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


def _generate_fixes(
    table_aliases: List[AliasInfo],
    standalone_aliases: List[str],
    references: List[BaseSegment],
    col_aliases: List[ColumnAliasInfo],
    single_table_references: str,
    allow_select_alias: bool,
    dialect: str,
    fix_inconsistent_to: Optional[str],
) -> Optional[List[LintResult]]:
    """Iterate through references and check consistency."""
    # How many aliases are there? If more than one then abort.
    if len(table_aliases) > 1:
        return None
    # A buffer to keep any violations.
    violation_buff: List[LintResult] = []
    col_alias_names: List[str] = [c.alias_identifier_name for c in col_aliases]
    table_ref_str: str = table_aliases[0].ref_str
    # Check all the references that we have.
    seen_ref_types: Set[str] = set()
    for ref in references:
        this_ref_type: str = ref.qualification()  # type: ignore
        if this_ref_type == "qualified" and dialect in ["bigquery", "hive", "redshift"]:
            # If this col appears "qualified" check if it is more logically a struct.
            if next(ref.iter_raw_references()).part != table_ref_str:  # type: ignore
                this_ref_type = "unqualified"

        lint_res = _validate_one_reference(
            single_table_references,
            allow_select_alias,
            ref,
            this_ref_type,
            standalone_aliases,
            table_ref_str,
            col_alias_names,
            seen_ref_types,
        )

        seen_ref_types.add(this_ref_type)
        if not lint_res:
            continue

        if fix_inconsistent_to and single_table_references == "consistent":
            # If we found a "consistent" error but we have a fix directive,
            # recurse with a different single_table_references value
            return _generate_fixes(
                table_aliases,
                standalone_aliases,
                references,
                col_aliases,
                single_table_references=fix_inconsistent_to,
                allow_select_alias=allow_select_alias,
                dialect=dialect,
                fix_inconsistent_to=None,
            )

        violation_buff.append(lint_res)

    return violation_buff or None


def _validate_one_reference(
    single_table_references: str,
    allow_select_alias: bool,
    ref: BaseSegment,
    this_ref_type: str,
    standalone_aliases: List[str],
    table_ref_str: str,
    col_alias_names: List[str],
    seen_ref_types: Set[str],
) -> Optional[LintResult]:
    # We skip any unqualified wildcard references (i.e. *). They shouldn't
    # count.
    if not ref.is_qualified() and ref.is_type("wildcard_identifier"):  # type: ignore
        return None
    # Oddball case: Column aliases provided via function calls in by
    # FROM or JOIN. References to these don't need to be qualified.
    # Note there could be a table with a column by the same name as
    # this alias, so avoid bogus warnings by just skipping them
    # entirely rather than trying to enforce anything.
    if ref.raw in standalone_aliases:
        return None

    # Certain dialects allow use of SELECT alias in WHERE clauses
    if allow_select_alias and ref.raw in col_alias_names:
        return None

    if single_table_references == "consistent":
        if seen_ref_types and this_ref_type not in seen_ref_types:
            return LintResult(
                anchor=ref,
                description=f"{this_ref_type.capitalize()} reference "
                f"{ref.raw!r} found in single table select which is "
                "inconsistent with previous references.",
            )

        return None

    if single_table_references != this_ref_type:
        if single_table_references == "unqualified":
            # If this is qualified we must have a "table", "."" at least
            fixes = [LintFix.delete(el) for el in ref.segments[:2]]
            return LintResult(
                anchor=ref,
                fixes=fixes,
                description="{} reference {!r} found in single table "
                "select.".format(this_ref_type.capitalize(), ref.raw),
            )

        fixes = [
            LintFix.create_before(
                ref.segments[0] if len(ref.segments) else ref,
                edit_segments=[
                    CodeSegment(
                        raw=table_ref_str,
                        name="naked_identifier",
                        type="identifier",
                    ),
                    SymbolSegment(raw=".", type="symbol", name="dot"),
                ],
            )
        ]
        return LintResult(
            anchor=ref,
            fixes=fixes,
            description="{} reference {!r} found in single table "
            "select.".format(this_ref_type.capitalize(), ref.raw),
        )

    return None
