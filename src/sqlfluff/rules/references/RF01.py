"""Implementation of Rule RF01."""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, cast

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.dialects.common import AliasInfo
from sqlfluff.core.rules import (
    BaseRule,
    LintResult,
    RuleContext,
)
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.reference import object_ref_matches_table
from sqlfluff.utils.analysis.query import Query

_START_TYPES = [
    "delete_statement",
    "merge_statement",
    "select_statement",
    "update_statement",
]


@dataclass
class RF01Query(Query):
    """Query with custom RF01 info."""

    aliases: List[AliasInfo] = field(default_factory=list)
    standalone_aliases: List[str] = field(default_factory=list)


class Rule_RF01(BaseRule):
    """References cannot reference objects not present in ``FROM`` clause.

    .. note::

       This rule is disabled by default for BigQuery, Databricks, Hive,
       Redshift, SOQL and SparkSQL due to the support of things like
       structs and lateral views which trigger false positives. It can be
       enabled with the ``force_enable = True`` flag.

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

    name = "references.from"
    aliases = ("L026",)
    groups = ("all", "core", "references")
    config_keywords = ["force_enable"]
    # If any of the parents would have also triggered the rule, don't fire
    # because they will more accurately process any internal references.
    crawl_behaviour = SegmentSeekerCrawler(set(_START_TYPES), allow_recurse=False)
    _dialects_disabled_by_default = [
        "bigquery",
        "databricks",
        "hive",
        "redshift",
        "soql",
        "sparksql",
    ]

    def _eval(self, context: RuleContext) -> List[LintResult]:
        # Config type hints
        self.force_enable: bool

        if (
            context.dialect.name in self._dialects_disabled_by_default
            and not self.force_enable
        ):
            return []

        violations: List[LintResult] = []
        dml_target_table: Optional[Tuple[str, ...]] = None
        self.logger.debug("Trigger on: %s", context.segment)
        if not context.segment.is_type("select_statement"):
            # Extract first table reference. This will be the target
            # table in a DML statement.
            table_reference = next(
                context.segment.recursive_crawl("table_reference"), None
            )
            if table_reference:
                dml_target_table = self._table_ref_as_tuple(table_reference)

        self.logger.debug("DML Reference Table: %s", dml_target_table)
        # Verify table references in any SELECT statements found in or
        # below context.segment in the parser tree.
        query = RF01Query.from_segment(context.segment, context.dialect)
        self._analyze_table_references(
            query, dml_target_table, context.dialect, violations
        )
        return violations

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
        query: RF01Query,
        dml_target_table: Optional[Tuple[str, ...]],
        dialect: Dialect,
        violations: List[LintResult],
    ) -> None:
        # For each query...
        for selectable in query.selectables:
            select_info = selectable.select_info
            self.logger.debug(
                "Selectable: %s",
                selectable,
            )
            if select_info:
                # Record the available tables.
                query.aliases += select_info.table_aliases
                query.standalone_aliases += select_info.standalone_aliases
                self.logger.debug(
                    "Aliases: %s %s",
                    [alias.ref_str for alias in select_info.table_aliases],
                    select_info.standalone_aliases,
                )

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
                cast(RF01Query, child), dml_target_table, dialect, violations
            )

    @staticmethod
    def _should_ignore_reference(reference, selectable) -> bool:
        ref_path = selectable.selectable.path_to(reference)
        # Ignore references occurring in an "INTO" clause:
        # - They are table references, not column references.
        # - They are the target table, similar to an INSERT or UPDATE
        #   statement, thus not expected to match a table in the FROM
        #   clause.
        if ref_path:
            return any(ps.segment.is_type("into_table_clause") for ps in ref_path)
        else:
            return False  # pragma: no cover

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
        self, r, tbl_refs, dml_target_table: Optional[Tuple[str, ...]], query: RF01Query
    ):
        # Does this query define the referenced table?
        possible_references = [tbl_ref[1] for tbl_ref in tbl_refs]
        targets = []
        for alias in query.aliases:
            targets += self._alias_info_as_tuples(alias)
        for standalone_alias in query.standalone_aliases:
            targets.append((standalone_alias,))
        if not object_ref_matches_table(possible_references, targets):
            # No. Check the parent query, if there is one.
            if query.parent:
                return self._resolve_reference(
                    r, tbl_refs, dml_target_table, cast(RF01Query, query.parent)
                )
            # No parent query. If there's a DML statement at the root, check its
            # target table or alias.
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
