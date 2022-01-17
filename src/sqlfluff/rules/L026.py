"""Implementation of Rule L026."""

from dataclasses import dataclass, field
from typing import cast, List, Optional

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.rules.analysis.select_crawler import (
    Query as SelectCrawlerQuery,
    SelectCrawler,
)
from sqlfluff.core.dialects.common import AliasInfo
from sqlfluff.core.rules.base import (
    BaseRule,
    LintResult,
    RuleContext,
    EvalResultType,
)
from sqlfluff.core.rules.functional import sp
from sqlfluff.core.rules.doc_decorators import document_configuration


@dataclass
class L026Query(SelectCrawlerQuery):
    """SelectCrawler Query with custom L026 info."""

    aliases: List[AliasInfo] = field(default_factory=list)


@document_configuration
class Rule_L026(BaseRule):
    """References cannot reference objects not present in ``FROM`` clause.

    NB: This rule is disabled by default for BigQuery due to its use of
    structs which trigger false positives. It can be enabled with the
    ``force_enable = True`` flag.

    | **Anti-pattern**
    | In this example, the reference ``vee`` has not been declared.

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

    def _eval(self, context: RuleContext) -> EvalResultType:
        # Config type hints
        self.force_enable: bool

        if (
            context.dialect.name in ["bigquery", "hive", "redshift"]
            and not self.force_enable
        ):
            return LintResult()

        violations: List[LintResult] = []
        start_types = ["select_statement", "delete_statement", "update_statement"]
        if context.segment.is_type(
            *start_types
        ) and not context.functional.parent_stack.any(sp.is_type(*start_types)):
            dml_target_table: Optional[str] = None
            if not context.segment.is_type("select_statement"):
                # Extract first table reference.
                table_reference = next(
                    context.segment.recursive_crawl("table_reference"), None
                )
                if table_reference:
                    dml_target_table = table_reference.raw

            # Verify table references in any SELECT statements found in or
            # below context.segment.
            crawler = SelectCrawler(
                context.segment, context.dialect, query_class=L026Query
            )
            query: L026Query = cast(L026Query, crawler.query_tree)
            self._analyze_table_references(
                query, dml_target_table, context.dialect, violations
            )
        return violations or None

    def _analyze_table_references(
        self,
        query: L026Query,
        dml_target_table: Optional[str],
        dialect: Dialect,
        violations: List[LintResult],
    ):
        # For each query...
        for selectable in query.selectables:
            select_info = selectable.select_info
            if select_info:
                # Record the table references.
                query.aliases += select_info.table_aliases

                # Try and resolve each table reference.
                for r in select_info.reference_buffer:
                    tbl_refs = r.extract_possible_references(
                        level=r.ObjectReferenceLevel.TABLE
                    )
                    # This function walks up the query's parent stack if necessary.
                    violation = self._resolve_reference(
                        r, tbl_refs, dml_target_table, query
                    )
                    if violation:
                        violations.append(violation)

        # Visit children.
        for child in query.children:
            self._analyze_table_references(
                cast(L026Query, child), dml_target_table, dialect, violations
            )

    def _resolve_reference(
        self, r, tbl_refs, dml_target_table: Optional[str], query: L026Query
    ):
        # Does this query define the referenced table?
        if tbl_refs and all(
            tbl_ref[0] not in [a.ref_str for a in query.aliases] for tbl_ref in tbl_refs
        ):
            # No. Check the parent query, if there is one.
            if query.parent:
                return self._resolve_reference(
                    r, tbl_refs, dml_target_table, cast(L026Query, query.parent)
                )
            # No parent query. If there's a DML statement at the root, check its
            # target table.
            elif not dml_target_table or all(
                tbl_ref[0] != dml_target_table for tbl_ref in tbl_refs
            ):
                return LintResult(
                    # Return the first segment rather than the string
                    anchor=tbl_refs[0].segments[0],
                    description=f"Reference {r.raw!r} refers to table/view "
                    "not found in the FROM clause or found in ancestor "
                    "statement.",
                )
