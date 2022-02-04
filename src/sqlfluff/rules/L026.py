"""Implementation of Rule L026."""
from dataclasses import dataclass, field
from typing import cast, List, Optional, Tuple

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
from sqlfluff.core.rules.reference import object_ref_matches_table


@dataclass
class L026Query(SelectCrawlerQuery):
    """SelectCrawler Query with custom L026 info."""

    aliases: List[AliasInfo] = field(default_factory=list)


@document_configuration
class Rule_L026(BaseRule):
    """References cannot reference objects not present in ``FROM`` clause.

    .. note::
       This rule is disabled by default for BigQuery due to its use of
       structs which trigger false positives. It can be enabled with the
       ``force_enable = True`` flag.

    **Anti-pattern**

    In this example, the reference ``vee`` has not been declared.

    .. code-block:: sql

        SELECT
            vee.a
        FROM foo

    **Best practice**

    Remove the reference.

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
            dml_target_table: Optional[Tuple[str, ...]] = None
            if not context.segment.is_type("select_statement"):
                # Extract first table reference. This will be the target
                # table in a DELETE or UPDATE statement.
                table_reference = next(
                    context.segment.recursive_crawl("table_reference"), None
                )
                if table_reference:
                    dml_target_table = self._table_ref_as_tuple(table_reference)

            # Verify table references in any SELECT statements found in or
            # below context.segment in the parser tree.
            crawler = SelectCrawler(
                context.segment, context.dialect, query_class=L026Query
            )
            query: L026Query = cast(L026Query, crawler.query_tree)
            if query:
                self._analyze_table_references(
                    query, dml_target_table, context.dialect, violations
                )
        return violations or None

    @classmethod
    def _alias_info_as_tuples(cls, alias_info: AliasInfo) -> List[Tuple[str, ...]]:
        result: List[Tuple[str, ...]] = []
        if alias_info.aliased:
            result.append((alias_info.ref_str,))
        if alias_info.object_reference:
            result.append(cls._table_ref_as_tuple(alias_info.object_reference))
        return result

    @staticmethod
    def _table_ref_as_tuple(table_reference) -> Tuple[str, ...]:
        return tuple(ref.part for ref in table_reference.iter_raw_references())

    def _analyze_table_references(
        self,
        query: L026Query,
        dml_target_table: Optional[Tuple[str, ...]],
        dialect: Dialect,
        violations: List[LintResult],
    ):
        # For each query...
        for selectable in query.selectables:
            select_info = selectable.select_info
            if select_info:
                # Record the available tables.
                query.aliases += select_info.table_aliases

                # Try and resolve each reference to a value in query.aliases (or
                # in an ancestor query).
                for r in select_info.reference_buffer:
                    if not self._should_ignore_reference(r, selectable):
                        # This function walks up the query's parent stack if necessary.
                        violation = self._resolve_reference(
                            r, self._get_table_refs(r, dialect), dml_target_table, query
                        )
                        if violation:
                            violations.append(violation)

        # Visit children.
        for child in query.children:
            self._analyze_table_references(
                cast(L026Query, child), dml_target_table, dialect, violations
            )

    @staticmethod
    def _should_ignore_reference(reference, selectable):
        ref_path = selectable.selectable.path_to(reference)
        # Ignore references occurring in an "INTO" clause:
        # - They are table references, not column references.
        # - They are the target table, similar to an INSERT or UPDATE
        #   statement, thus not expected to match a table in the FROM
        #   clause.
        return any(seg.is_type("into_table_clause") for seg in ref_path)

    @staticmethod
    def _get_table_refs(ref, dialect):
        """Given ObjectReferenceSegment, determine possible table references."""
        tbl_refs = []
        # First, handle any schema.table references.
        for sr, tr in ref.extract_possible_multipart_references(
            levels=[
                ref.ObjectReferenceLevel.SCHEMA,
                ref.ObjectReferenceLevel.TABLE,
            ]
        ):
            tbl_refs.append((tr, (sr.part, tr.part)))
        # Maybe check for simple table references. Two cases:
        # - For most dialects, skip this if it's a schema+table reference -- the
        #   reference was specific, so we shouldn't ignore that by looking
        #   elsewhere.)
        # - Always do this in BigQuery. BigQuery table references are frequently
        #   ambiguous because BigQuery SQL supports structures, making some
        #   multi-level "." references impossible to interpret with certainty.
        #   We may need to genericize this code someday to support other
        #   dialects. If so, this check should probably align somehow with
        #   whether the dialect overrides
        #   ObjectReferenceSegment.extract_possible_references().
        if not tbl_refs or dialect.name in ["bigquery"]:
            for tr in ref.extract_possible_references(
                level=ref.ObjectReferenceLevel.TABLE
            ):
                tbl_refs.append((tr, (tr.part,)))
        return tbl_refs

    def _resolve_reference(
        self, r, tbl_refs, dml_target_table: Optional[Tuple[str, ...]], query: L026Query
    ):
        # Does this query define the referenced table?
        possible_references = [tbl_ref[1] for tbl_ref in tbl_refs]
        targets = []
        for alias in query.aliases:
            targets += self._alias_info_as_tuples(alias)
        if not object_ref_matches_table(possible_references, targets):
            # No. Check the parent query, if there is one.
            if query.parent:
                return self._resolve_reference(
                    r, tbl_refs, dml_target_table, cast(L026Query, query.parent)
                )
            # No parent query. If there's a DML statement at the root, check its
            # target table.
            elif not dml_target_table or not object_ref_matches_table(
                possible_references, [dml_target_table]
            ):
                return LintResult(
                    # Return the first segment rather than the string
                    anchor=tbl_refs[0][0].segments[0],
                    description=f"Reference {r.raw!r} refers to table/view "
                    "not found in the FROM clause or found in ancestor "
                    "statement.",
                )
