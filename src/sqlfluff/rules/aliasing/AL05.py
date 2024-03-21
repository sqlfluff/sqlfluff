"""Implementation of Rule AL05."""

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Set, cast

from sqlfluff.core.dialects.base import Dialect
from sqlfluff.core.dialects.common import AliasInfo
from sqlfluff.core.parser.segments import BaseSegment, RawSegment
from sqlfluff.core.rules import (
    BaseRule,
    EvalResultType,
    LintFix,
    LintResult,
    RuleContext,
)
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.analysis.query import Query
from sqlfluff.utils.analysis.select import get_select_statement_info
from sqlfluff.utils.functional import Segments, sp


@dataclass
class AL05Query(Query):
    """Query subclass with custom AL05 info."""

    aliases: List[AliasInfo] = field(default_factory=list)
    tbl_refs: Set[str] = field(default_factory=set)


class Rule_AL05(BaseRule):
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

    name = "aliasing.unused"
    aliases = ("L025",)
    groups = ("all", "core", "aliasing")
    crawl_behaviour = SegmentSeekerCrawler({"select_statement"})
    _dialects_requiring_alias_for_values_clause = [
        "snowflake",
        "tsql",
        "postgres",
    ]
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> EvalResultType:
        violations: List[LintResult] = []
        assert context.segment.is_type("select_statement")
        # Exit early if the SELECT does not define any aliases.
        select_info = get_select_statement_info(context.segment, context.dialect)
        if not select_info or not select_info.table_aliases:
            return None

        # Analyze the SELECT.
        alias: AliasInfo
        query = AL05Query.from_segment(context.segment, dialect=context.dialect)
        self._analyze_table_aliases(query, context.dialect)

        if context.dialect.name in ("redshift", "bigquery"):
            # Redshift supports un-nesting using aliases.
            # Detect that situation and ignore.
            # https://docs.aws.amazon.com/redshift/latest/dg/query-super.html#unnest

            # Do any references refer to aliases in the same list?
            references = set()
            aliases = set()

            for alias in query.aliases:
                aliases.add(alias.ref_str)
                if not alias.object_reference:
                    continue  # pragma: no cover
                for seg in alias.object_reference.segments:
                    if seg.is_type("identifier"):
                        references.add(cast(RawSegment, seg).raw_normalized())

            # If there's any overlap between aliases and reference
            if aliases.intersection(references):
                self.logger.debug(
                    "Overlapping references found. Assuming redshift semi-structured."
                )
                return None

        # Get the number of times an object (table/view) is referenced. While some
        # dialects can handle the same table name reference with different schemas,
        # we don't want to allow a conflict with AL04's uniqueness rule so we grab
        # the base table name instead of the fully qualified one to determine naming
        # collisions.
        ref_counter = Counter(
            a.object_reference.segments[-1].raw_normalized()
            for a in query.aliases
            if a.object_reference and a.object_reference.segments
        )
        print(query)
        for alias in query.aliases:
            # Skip alias if it's required (some dialects require aliases for
            # VALUES clauses).
            if alias.from_expression_element and self._is_alias_required(
                alias.from_expression_element, context.dialect.name
            ):
                continue
            # Skip alias if the table is referenced more than once, some dialects
            # require the referenced table names to be unique even if not returned
            # by the statement.
            if (
                alias.object_reference
                and alias.object_reference.segments
                and ref_counter.get(
                    cast(
                        RawSegment, alias.object_reference.segments[-1]
                    ).raw_normalized(),
                    0,
                )
                > 1
            ):
                continue
            # Redshift requires an alias when a `QUALIFY` statement immediately follows
            # the `FROM` clause.
            # https://docs.aws.amazon.com/redshift/latest/dg/r_QUALIFY_clause.html
            if (
                context.dialect.name == "redshift"
                and alias.alias_expression
                and self._followed_by_qualify(context, alias)
            ):
                continue

            print(alias.ref_str, query.tbl_refs)
            if alias.aliased and alias.ref_str not in query.tbl_refs:
                # Unused alias. Report and fix.
                violations.append(self._report_unused_alias(alias))
        return violations or None

    @classmethod
    def _followed_by_qualify(cls, context: RuleContext, alias: AliasInfo) -> bool:
        curr_from_seen = False
        assert alias.alias_expression
        for seg in context.segment.segments:
            if alias.alias_expression.get_end_loc() == seg.get_end_loc():
                curr_from_seen = True
            elif curr_from_seen and not seg.is_code:
                continue
            elif curr_from_seen and seg.is_type("qualify_clause"):
                return True
            elif curr_from_seen:
                return False
        return False

    @classmethod
    def _is_alias_required(
        cls, from_expression_element: BaseSegment, dialect_name: str
    ) -> bool:
        """Given an alias, is it REQUIRED to be present?

        Aliases are required in SOME, but not all dialects when there's a VALUES
        clause.
        """
        # Look for a table_expression (i.e. VALUES clause) as a descendant of
        # the FROM expression, potentially nested inside brackets. The reason we
        # allow nesting in brackets is that in some dialects (e.g. TSQL), this
        # is actually *required* in order for SQL Server to parse it.
        for segment in from_expression_element.iter_segments(expanding=("bracketed",)):
            if segment.is_type("table_expression"):
                # Found a table expression. Does it have a VALUES clause?
                if segment.get_child("values_clause"):
                    # Found a VALUES clause. Is this a dialect that requires
                    # VALUE clauses to be aliased?
                    return (
                        dialect_name in cls._dialects_requiring_alias_for_values_clause
                    )
                elif any(
                    seg.is_type(
                        "select_statement", "set_expression", "with_compound_statement"
                    )
                    for seg in segment.iter_segments(expanding=("bracketed",))
                ):
                    # The FROM expression is a derived table, i.e. a nested
                    # SELECT. In this case, the alias is required in every
                    # dialect we checked (MySQL, Postgres, T-SQL).
                    # https://pganalyze.com/docs/log-insights/app-errors/U115
                    return True
                else:
                    # None of the special cases above applies, so the alias is
                    # not required.
                    return False

        # This should never happen. Return False just to be safe.
        return False  # pragma: no cover

    @classmethod
    def _analyze_table_aliases(cls, query: AL05Query, dialect: Dialect) -> None:
        # Get table aliases defined in query.
        for selectable in query.selectables:
            select_info = selectable.select_info
            if select_info:
                # Record the aliases.
                query.aliases += select_info.table_aliases

                # Look at each table reference; if it's an alias reference,
                # resolve the alias: could be an alias defined in "query"
                # itself or an "ancestor" query.
                for r in (
                    select_info.reference_buffer + select_info.table_reference_buffer
                ):
                    for tr in r.extract_possible_references(
                        level=r.ObjectReferenceLevel.TABLE
                    ):
                        # This function walks up the query's parent stack if necessary.
                        cls._resolve_and_mark_reference(query, tr.part)

        # Visit children.
        for child in query.children:
            cls._analyze_table_aliases(cast(AL05Query, child), dialect)

    @classmethod
    def _resolve_and_mark_reference(cls, query: AL05Query, ref: str) -> None:
        # Does this query define the referenced alias?
        print("mark:", ref, [a.ref_str for a in query.aliases])
        if any(ref == a.ref_str for a in query.aliases):
            # Yes. Record the reference.
            query.tbl_refs.add(ref)
        elif query.parent:
            # No. Recursively check the query's parent hierarchy.
            cls._resolve_and_mark_reference(cast(AL05Query, query.parent), ref)

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
