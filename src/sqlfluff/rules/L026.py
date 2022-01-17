"""Implementation of Rule L026."""

from dataclasses import dataclass, field
from typing import cast, List

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.rules.analysis.select import (
    get_select_statement_info,
)
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
        start_types = ["select_statement"]
        if context.segment.is_type(
            *start_types
        ) and not context.functional.parent_stack.any(sp.is_type(*start_types)):
            select_info = get_select_statement_info(context.segment, context.dialect)
            if not select_info:
                return LintResult()

            # Analyze the SELECT.
            crawler = SelectCrawler(
                context.segment, context.dialect, query_class=L026Query
            )
            query: L026Query = cast(L026Query, crawler.query_tree)
            self._analyze_table_references(query, context.dialect, violations)
        return violations or None

    def _analyze_table_references(
        self, query: L026Query, dialect: Dialect, violations: List[LintResult]
    ):
        # Get table aliases defined in query.
        for selectable in query.selectables:
            select_info = get_select_statement_info(selectable.selectable, dialect)
            if select_info:
                # Record the table references.
                query.aliases += select_info.table_aliases

                # Look at each table reference; if it's an alias reference,
                # resolve the alias: could be an alias defined in "query"
                # itself or an "ancestor" query.
                for r in select_info.reference_buffer:
                    tbl_refs = r.extract_possible_references(  # type: ignore
                        level=r.ObjectReferenceLevel.TABLE  # type: ignore
                    )
                    # This function walks up the query's parent stack if necessary.
                    violation = self._resolve_reference(query, r, tbl_refs)
                    if violation:
                        violations.append(violation)

        # Visit children.
        for child in query.children:
            self._analyze_table_references(cast(L026Query, child), dialect, violations)

    @staticmethod
    def _is_bad_tbl_ref(table_aliases, tbl_ref):
        """Given a table reference, try to find what it's referring to."""
        # Is it referring to one of the table aliases?
        return tbl_ref[0] not in [a.ref_str for a in table_aliases]

    def _resolve_reference(self, query: L026Query, r, tbl_refs):
        # Does this query define the referenced table?
        if tbl_refs and all(
            self._is_bad_tbl_ref(query.aliases, tbl_ref) for tbl_ref in tbl_refs
        ):
            if query.parent:
                return self._resolve_reference(
                    cast(L026Query, query.parent), r, tbl_refs
                )
            else:
                return LintResult(
                    # Return the first segment rather than the string
                    anchor=tbl_refs[0].segments[0],
                    description=f"Reference {r.raw!r} refers to table/view "
                    "not found in the FROM clause or found in ancestor "
                    "statement.",
                )
