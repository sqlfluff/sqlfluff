"""Implementation of Rule L025."""

from dataclasses import dataclass, field
from typing import cast, List, Set

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.rules.analysis.select import get_select_statement_info
from sqlfluff.core.rules.analysis.select_crawler import (
    Query as SelectCrawlerQuery,
    SelectCrawler,
)
from sqlfluff.core.rules.base import (
    BaseRule,
    LintFix,
    LintResult,
    RuleContext,
    EvalResultType,
)
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
from sqlfluff.core.rules.functional import Segments, sp
from sqlfluff.core.dialects.common import AliasInfo


@dataclass
class L025Query(SelectCrawlerQuery):
    """SelectCrawler Query with custom L025 info."""

    aliases: List[AliasInfo] = field(default_factory=list)
    tbl_refs: Set[str] = field(default_factory=set)


@document_fix_compatible
class Rule_L025(BaseRule):
    """Tables should not be aliased if that alias is not used.

    **Anti-pattern**

    .. code-block:: sql

        SELECT
            a
        FROM foo AS zoo

    **Best practice**

    Use the alias or remove it. An unused alias makes code
    harder to read without changing any functionality.

    .. code-block:: sql

        SELECT
            zoo.a
        FROM foo AS zoo

        -- Alternatively...

        SELECT
            a
        FROM foo

    """

    def _eval(self, context: RuleContext) -> EvalResultType:
        violations: List[LintResult] = []
        if context.segment.is_type("select_statement"):
            # Exit early if the SELECT does not define any aliases.
            select_info = get_select_statement_info(context.segment, context.dialect)
            if not select_info or not select_info.table_aliases:
                return None

            # Analyze the SELECT.
            crawler = SelectCrawler(
                context.segment, context.dialect, query_class=L025Query
            )
            query: L025Query = cast(L025Query, crawler.query_tree)
            self._analyze_table_aliases(query, context.dialect)

            alias: AliasInfo
            for alias in query.aliases:
                if alias.aliased and alias.ref_str not in query.tbl_refs:
                    # Unused alias. Report and fix.
                    violations.append(self._report_unused_alias(alias))
        return violations or None

    @classmethod
    def _analyze_table_aliases(cls, query: L025Query, dialect: Dialect):
        # Get table aliases defined in query.
        for selectable in query.selectables:
            select_info = selectable.select_info
            if select_info:
                # Record the aliases.
                query.aliases += select_info.table_aliases

                # Look at each table reference; if it's an alias reference,
                # resolve the alias: could be an alias defined in "query"
                # itself or an "ancestor" query.
                for r in select_info.reference_buffer:
                    for tr in r.extract_possible_references(
                        level=r.ObjectReferenceLevel.TABLE
                    ):
                        # This function walks up the query's parent stack if necessary.
                        cls._resolve_and_mark_reference(query, tr.part)

        # Visit children.
        for child in query.children:
            cls._analyze_table_aliases(cast(L025Query, child), dialect)

    @classmethod
    def _resolve_and_mark_reference(cls, query: L025Query, ref: str):
        # Does this query define the referenced alias?
        if any(ref == a.ref_str for a in query.aliases):
            # Yes. Record the reference.
            query.tbl_refs.add(ref)
        elif query.parent:
            # No. Recursively check the query's parent hierarchy.
            cls._resolve_and_mark_reference(cast(L025Query, query.parent), ref)

    @classmethod
    def _report_unused_alias(cls, alias: AliasInfo) -> LintResult:
        fixes = [LintFix.delete(alias.alias_expression)]  # type: ignore
        # Walk back to remove indents/whitespaces
        to_delete = (
            Segments(*alias.from_expression_element.segments)
            .reversed()
            .select(
                start_seg=alias.alias_expression,
                # Stop once we reach an other, "regular" segment.
                loop_while=sp.or_(sp.is_whitespace(), sp.is_meta()),
            )
        )
        fixes += [LintFix.delete(seg) for seg in to_delete]
        return LintResult(
            anchor=alias.segment,
            description="Alias {!r} is never used in SELECT statement.".format(
                alias.ref_str
            ),
            fixes=fixes,
        )
