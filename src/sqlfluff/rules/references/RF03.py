"""Implementation of Rule RF03."""

from collections.abc import Iterator
from typing import Optional

from sqlfluff.core.dialects.common import (
    AliasInfo,
    ColumnAliasInfo,
    ObjectReferenceLevel,
    extract_possible_references,
    is_qualified,
    iter_raw_references,
    qualification,
)
from sqlfluff.core.parser import IdentifierSegment
from sqlfluff.core.parser.segments import BaseSegment, SymbolSegment
from sqlfluff.core.rules import (
    BaseRule,
    EvalResultType,
    LintFix,
    LintResult,
    RuleContext,
)
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.dialects.dialect_ansi import ObjectReferenceSegment
from sqlfluff.utils.analysis.query import Query
from sqlfluff.utils.analysis.select import SelectStatementColumnsAndTables

_START_TYPES = [
    "delete_statement",
    "merge_statement",
    "select_statement",
    "set_expression",
    "update_statement",
    "with_compound_statement",
]


class Rule_RF03(BaseRule):
    """Column references should be qualified consistently in single table statements.

    .. note::
        For Athena, BigQuery, Hive and Redshift this rule is disabled by default.
        This is due to historical false positives associated with STRUCT data types.
        This default behaviour may be changed in the future.
        The rule can be enabled with the ``force_enable = True`` flag.

    "consistent" will be fixed to "qualified" if inconsistency is found.

    **Anti-pattern**

    In this example, only the reference to ``b`` is qualified.

    .. code-block:: sql

        SELECT
            a,
            foo.b
        FROM foo

    **Best practice**

    Either all column references should be qualified, or all unqualified.

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

    name = "references.consistent"
    aliases = ("L028",)
    groups = ("all", "references")
    config_keywords = [
        "single_table_references",
        "force_enable",
    ]
    # If any of the parents would have also triggered the rule, don't fire
    # because they will more accurately process any internal references.
    crawl_behaviour = SegmentSeekerCrawler(set(_START_TYPES), allow_recurse=False)
    _is_struct_dialect = False
    # Dialects with STRUCT-like data types accessed via dot syntax (e.g.
    # `col.field.subfield`), which can be misread as table-qualified column
    # references (`table.column`) in single table SELECTs.
    # https://docs.aws.amazon.com/athena/latest/ug/filtering-with-dot.html
    _dialects_with_structs = ["athena", "bigquery", "hive", "redshift"]
    # This could be turned into an option
    _fix_inconsistent_to = "qualified"
    is_fix_compatible = True
    single_table_references: str

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Override base class for dialects that use structs, or SELECT aliases."""
        # Config type hints
        self.force_enable: bool
        # Some dialects use structs (e.g. column.field) which look like
        # table references and so incorrectly trigger this rule.
        if (
            context.dialect.name in self._dialects_with_structs
            and not self.force_enable
        ):
            return LintResult()

        if context.dialect.name in self._dialects_with_structs:
            self._is_struct_dialect = True

        query: Query = Query.from_segment(context.segment, dialect=context.dialect)
        visited: set = set()
        templater_name = context.config.get("templater")
        # Recursively visit and check each query in the tree.
        return list(self._visit_queries(query, visited, templater_name))

    def _iter_available_targets(
        self, query: Query, subquery: Optional[Query] = None
    ) -> Iterator[AliasInfo]:
        """Iterate along a list of valid alias targets."""
        for selectable in query.selectables:
            select_info = selectable.select_info
            if select_info:
                for alias in select_info.table_aliases:
                    if (
                        subquery
                        and alias.from_expression_element.is_type(
                            "from_expression_element"
                        )
                        and alias.from_expression_element.path_to(
                            subquery.selectables[0].selectable
                        )
                    ):
                        # Skip the subquery alias itself
                        continue
                    # Tables without an alias name (e.g. unaliased T-SQL table
                    # variables) can't be targets for added qualifiers, but a
                    # subquery can still see their columns, and reference them
                    # by their bracketed name (e.g. `[@orders].id`).
                    if alias.ref_str or subquery:
                        yield alias

    @property
    def _may_add_qualifiers(self) -> bool:
        """Whether fixes may add qualifiers to references.

        Only adding qualifiers needs to know about the tables of enclosing
        queries. Removing them is safe, as unqualified names resolve to the
        inner table first.
        """
        return self.single_table_references != "unqualified"

    def _outer_visible_aliases(self, query: Query) -> list[AliasInfo]:
        """Get the aliases visible from all queries enclosing this subquery.

        A correlated subquery may reference any enclosing query, not just its
        direct parent, so walk up the whole chain of ancestors. A CTE never
        sees the FROM clause of the query that uses it, so skip that query,
        but it can see the queries enclosing its WITH statement.
        """
        outer_aliases: list[AliasInfo] = []
        child = query
        while child.parent:
            if child.cte_definition_segment is None:
                outer_aliases += self._iter_available_targets(child.parent, child)
            child = child.parent
        return outer_aliases

    def _visit_queries(
        self, query: Query, visited: set, templater_name: str
    ) -> Iterator[LintResult]:
        select_info: Optional[SelectStatementColumnsAndTables] = None
        if query.selectables:
            select_info = query.selectables[0].select_info
            # How many table names are visible from here? If more than one then do
            # nothing.
            if select_info and len(select_info.table_aliases) == 1:
                fixable = True
                # :TRICKY: Subqueries in the column list of a SELECT can see tables
                # in the FROM list of the containing query. Thus, count tables at
                # the *parent* query level. Only check if it is a subquery of the
                # parent. Nested subqueries can see the tables of all enclosing
                # queries, which matters if the parent has no tables of its own.
                possible_ref_tables = list(self._iter_available_targets(query))
                # Top level queries have no outer aliases.
                outer_aliases = self._outer_visible_aliases(query)
                references_outer_table = bool(outer_aliases) and (
                    _references_outer_table(
                        select_info.reference_buffer,
                        select_info.table_aliases,
                        outer_aliases,
                        query.dialect.name,
                    )
                )
                if query.parent and query.is_subquery:
                    if self._may_add_qualifiers or references_outer_table:
                        possible_ref_tables += outer_aliases
                    else:
                        # Outer tables without an alias name only matter when
                        # adding qualifiers, or when a reference names them.
                        possible_ref_tables += [a for a in outer_aliases if a.ref_str]
                # Subqueries in the FROM clause and CTEs normally can't see the
                # tables of the enclosing queries. Correlated ones can (e.g.
                # T-SQL CROSS/OUTER APPLY or LATERAL joins), so count the outer
                # tables if any reference uses one of them. In valid SQL only
                # correlated subqueries do that. An unqualified column may also
                # belong to an outer table, so adding a qualifier is unsafe even
                # without references to the outer tables.
                elif references_outer_table or (
                    outer_aliases
                    and self._may_add_qualifiers
                    and _sees_outer_columns(query.selectables[0].selectable)
                ):
                    possible_ref_tables += outer_aliases
                if len(possible_ref_tables) > 1:
                    # If more than one table name is visible, check for and report
                    # potential lint warnings, but don't generate fixes, because
                    # fixes are unsafe if there's more than one table visible.
                    fixable = False

                yield from _check_references(
                    select_info.table_aliases,
                    select_info.standalone_aliases,
                    select_info.reference_buffer,
                    select_info.col_aliases,
                    self.single_table_references,
                    self._is_struct_dialect,
                    self._fix_inconsistent_to,
                    fixable,
                    query.dialect.name,
                    templater_name,
                )
        children = list(query.children)
        # 'query.children' includes CTEs and "main" queries, but not queries in
        # the "FROM" list. We want to visit those as well.
        if select_info:
            for a in select_info.table_aliases:
                for q in query.crawl_sources(a.from_expression_element, True):
                    if not isinstance(q, Query):
                        continue
                    # Check for previously visited selectables to avoid possible
                    # infinite recursion, e.g.:
                    #   WITH test1 AS (SELECT i + 1, j + 1 FROM test1)
                    #   SELECT * FROM test1;
                    if any(s.selectable in visited for s in q.selectables):
                        continue
                    visited.update(s.selectable for s in q.selectables)
                    children.append(q)
        for child in children:
            yield from self._visit_queries(child, visited, templater_name)


def _sees_outer_columns(selectable: BaseSegment) -> bool:
    """Check whether a selectable can see the columns of the enclosing query.

    A subquery in the FROM clause can see the columns of its own query only
    if it is a LATERAL or APPLY subquery. Other subqueries (e.g. in the WHERE
    clause, SET clause, or MERGE match actions) always can. A CTE takes the
    position of the WITH statement which defines it. Any subquery can also see
    the columns which its enclosing query can see, e.g. a derived table nested
    in a LATERAL subquery.
    """
    parent = _parent_segment(selectable)
    while parent:
        if parent.is_type(
            "select_statement",
            "update_statement",
            "delete_statement",
            "merge_statement",
        ):
            return True
        if parent.is_type("from_expression_element"):
            if _is_lateral_element(parent):
                return True
            # A plain derived table can't see the columns of the query whose
            # FROM clause holds it, so skip that query.
            parent = _enclosing_select(parent)
            if not parent:  # pragma: no cover
                return False
        parent = _parent_segment(parent)
    return False


def _parent_segment(segment: BaseSegment) -> Optional[BaseSegment]:
    """Get the parent of a segment, if it has one."""
    parent = segment.get_parent()
    return parent[0] if parent else None


def _enclosing_select(segment: BaseSegment) -> Optional[BaseSegment]:
    """Get the nearest select statement which contains a segment."""
    parent = _parent_segment(segment)
    while parent and not parent.is_type(
        "select_statement",
        "update_statement",
        "delete_statement",
        "merge_statement",
    ):
        parent = _parent_segment(parent)
    return parent


def _is_lateral_element(element: BaseSegment) -> bool:
    """Check whether a FROM expression element is a LATERAL or APPLY join."""
    if any(seg.raw_upper == "LATERAL" for seg in element.get_children("keyword")):
        return True
    parent = _parent_segment(element)
    return bool(
        parent
        and parent.is_type("join_clause")
        and any(seg.raw_upper == "APPLY" for seg in parent.get_children("keyword"))
    )


def _normalized_parts(reference: BaseSegment, dialect_name: str) -> tuple[str, ...]:
    """Get the parts of a reference, normalized to the dialect's casing."""
    return tuple(
        "".join(seg.raw_normalized() for seg in part.segments)
        for part in iter_raw_references(reference, dialect_name)
    )


def _table_names(alias: AliasInfo, dialect_name: str) -> tuple[str, ...]:
    """Get the name which qualifies references to a table.

    Aliased tables are only known by their alias. Other tables may also be
    known by their schema qualified name, e.g. ``public.orders``.
    """
    if not alias.aliased and alias.object_reference:
        parts = _normalized_parts(alias.object_reference, dialect_name)
        if parts:
            return parts
        # Table variables (e.g. T-SQL `@orders`) aren't identifiers, but
        # references can still name them, e.g. `[@orders].id`. T-SQL
        # normalizes identifiers to upper case.
        return (alias.object_reference.raw_normalized().upper(),)
    # Aliases without a segment have no name (e.g. an unaliased subquery).
    return (alias.segment.raw_normalized(),) if alias.segment else ()


def _is_suffix(short: tuple[str, ...], long: tuple[str, ...]) -> bool:
    return 0 < len(short) <= len(long) and long[len(long) - len(short) :] == short


def _references_outer_table(
    references: list[ObjectReferenceSegment],
    inner_aliases: list[AliasInfo],
    outer_aliases: list[AliasInfo],
    dialect_name: str,
) -> bool:
    """Check whether any reference is qualified with a table of an outer query.

    A reference qualified with ``orders`` or ``public.orders`` names the
    ``public.orders`` table. An inner table shadows an outer table with the
    same name, so references which name an inner table point at that one.
    The longest qualifier which names a table wins, e.g. ``public.orders.id``
    names the outer ``orders`` or ``public.orders`` even if an inner table is
    called ``public``. When it isn't clear which table a reference names, assume
    the outer one, as that keeps the fixes safe.
    """
    inner_names = [_table_names(t, dialect_name) for t in inner_aliases]
    outer_names = [_table_names(t, dialect_name) for t in outer_aliases]
    for ref in references:
        parts = _normalized_parts(ref, dialect_name)
        # The leading parts of a column reference name the table, but it
        # isn't clear how many (e.g. `schema.table.column` or
        # `table.column.struct_field`), so try all of them, longest first.
        # Unqualified references have no table name: they resolve to the
        # inner table first.
        qualifiers = [parts[:i] for i in range(1, len(parts))]
        for qualifier in reversed(qualifiers):
            if any(_is_suffix(qualifier, name) for name in inner_names):
                break
            # The reference may also add a schema to an outer table name,
            # e.g. `public.orders` for `orders`. Inner names don't get this
            # check: an inner alias `orders` can't be written as
            # `public.orders`, so it mustn't hide an outer `public.orders`.
            if any(
                _is_suffix(qualifier, name) or _is_suffix(name, qualifier)
                for name in outer_names
            ):
                return True
    return False


def _check_references(
    table_aliases: list[AliasInfo],
    standalone_aliases: list[BaseSegment],
    references: list[ObjectReferenceSegment],
    col_aliases: list[ColumnAliasInfo],
    single_table_references: str,
    is_struct_dialect: bool,
    fix_inconsistent_to: Optional[str],
    fixable: bool,
    dialect_name: str,
    templater_name: str,
) -> Iterator[LintResult]:
    """Iterate through references and check consistency."""
    # A buffer to keep any violations.
    col_alias_names: list[str] = [c.alias_identifier_name for c in col_aliases]
    table_ref_str: str = table_aliases[0].ref_str
    table_ref_str_source = table_aliases[0].segment
    # Check all the references that we have.
    seen_ref_types: set[str] = set()
    for ref in references:
        this_ref_type: str = qualification(ref, dialect_name)
        # Skip unqualified references rendered by the `placeholder` templater
        # (e.g. bind parameters like `:colname` that get rendered as bare
        # identifiers). These are not real column references and should not
        # be qualified or flagged. This must NOT be widened to templated
        # references in general: a Jinja/dbt `{{ my_col }}` renders to a
        # genuine column identifier that the user intends to reference, and
        # skipping it here would silently hide real qualification
        # inconsistencies.
        if (
            this_ref_type == "unqualified"
            and ref.is_templated
            and templater_name == "placeholder"
        ):
            continue
        # Skip whole-row references: a bare reference matching the single table's
        # own alias/name (e.g. ``tbl ->> 'k'`` in postgres, or ``SELECT tbl FROM
        # tbl``) refers to the whole row, not a column. It neither needs
        # qualification nor counts towards single-table consistency, so qualifying
        # it as ``tbl.tbl`` would be invalid.
        if (
            this_ref_type == "unqualified"
            and ref.raw_normalized(casefold=False) == table_ref_str
        ):
            continue
        if this_ref_type == "qualified" and is_struct_dialect:
            # If this col appears "qualified" check if it is more logically a struct.
            if next(iter_raw_references(ref, dialect_name)).part != table_ref_str:
                this_ref_type = "unqualified"

        lint_res = _validate_one_reference(
            single_table_references,
            ref,
            this_ref_type,
            standalone_aliases,
            table_ref_str,
            table_ref_str_source,
            col_alias_names,
            seen_ref_types,
            fixable,
            dialect_name,
        )

        seen_ref_types.add(this_ref_type)
        if not lint_res:
            continue

        if fix_inconsistent_to and single_table_references == "consistent":
            # If we found a "consistent" error but we have a fix directive,
            # recurse with a different single_table_references value.
            # This re-check iterates the same references list, so the
            # placeholder-templater skip above still applies and intentionally
            # keeps those bind parameters out of every consistency pass.
            yield from _check_references(
                table_aliases,
                standalone_aliases,
                references,
                col_aliases,
                # NB vars are passed in a different order here
                single_table_references=fix_inconsistent_to,
                is_struct_dialect=is_struct_dialect,
                fix_inconsistent_to=None,
                fixable=fixable,
                dialect_name=dialect_name,
                templater_name=templater_name,
            )

        yield lint_res


def _validate_one_reference(
    single_table_references: str,
    ref: ObjectReferenceSegment,
    this_ref_type: str,
    standalone_aliases: list[BaseSegment],
    table_ref_str: str,
    table_ref_str_source: Optional[BaseSegment],
    col_alias_names: list[str],
    seen_ref_types: set[str],
    fixable: bool,
    dialect_name: str,
) -> Optional[LintResult]:
    # We skip any unqualified wildcard references (i.e. *). They shouldn't
    # count.
    if not is_qualified(ref, dialect_name) and ref.is_type("wildcard_identifier"):
        return None
    # Oddball case: Column aliases provided via function calls in by
    # FROM or JOIN. References to these don't need to be qualified.
    # Note there could be a table with a column by the same name as
    # this alias, so avoid bogus warnings by just skipping them
    # entirely rather than trying to enforce anything.
    if ref.raw in [a.raw for a in standalone_aliases]:
        return None

    # If the reference is qualified, see that the table is not in the standalone_aliases
    # namely for lambda expressions.
    if is_qualified(ref, dialect_name):
        standalone_alias_raws = [a.raw for a in standalone_aliases]
        for part in extract_possible_references(
            ref, level=ObjectReferenceLevel.TABLE, dialect_name=dialect_name
        ):
            if part.part in standalone_alias_raws:
                return None
        # Also check the leading (first) part of the reference. For multi-part
        # references like `item.taskId.oid` (e.g. in Databricks higher-order
        # functions), the lambda parameter `item` is at the SCHEMA level, not
        # TABLE level. We need to check it against standalone aliases too.
        first_raw_ref = next(iter_raw_references(ref, dialect_name), None)
        if first_raw_ref and first_raw_ref.part in standalone_alias_raws:
            return None

    # Oddball case: tsql table variables can't be used to qualify references.
    # This appears here as an empty string for table_ref_str.
    if not table_ref_str:
        return None

    # Certain dialects allow use of SELECT alias in WHERE clauses
    if ref.raw in col_alias_names:
        return None

    # Check first for consistency
    if single_table_references == "consistent":
        if seen_ref_types and this_ref_type not in seen_ref_types:
            return LintResult(
                anchor=ref,
                description=f"{this_ref_type.capitalize()} reference "
                f"{ref.raw!r} found in single table select which is "
                "inconsistent with previous references.",
            )
        # Config is consistent, and this reference matches types so far.
        return None

    # Otherwise check for a specified type of referencing.
    # If it's the right kind already, just return.
    if single_table_references == this_ref_type:
        return None

    # A single templated expression can render to more than one column. For
    # example a Jinja/dbt `{{ cols }}` (or `dbt_utils.star()`) rendering to
    # `customer_id, region` is lexed as several column references that all map
    # back to the *same* template slice. We can still flag such references for
    # consistency, but we must not attach a fix: inserting or deleting a
    # qualifier around that shared slice would only touch the first rendered
    # column (producing e.g. `orders.{{ cols }}` -> `orders.customer_id,
    # region`, which leaves `region` unqualified) and silently corrupt the SQL.
    # Leave the rewrite to the user when the reference is templated.
    ref_is_templated = ref.is_templated

    # If not, it's the wrong type and we should handle it.
    if single_table_references == "unqualified":
        # If unqualified and not fixable, there is no error.
        if not fixable:
            return None
        # If this is qualified we must have a "table", "."" at least
        return LintResult(
            anchor=ref,
            fixes=(
                []
                if ref_is_templated
                else [LintFix.delete(el) for el in ref.segments[:2]]
            ),
            description="{} reference {!r} found in single table select.".format(
                this_ref_type.capitalize(), ref.raw
            ),
        )

    fixes = None
    if fixable and not ref_is_templated:
        fixes = [
            LintFix.create_before(
                ref.segments[0] if len(ref.segments) else ref,
                source=[table_ref_str_source] if table_ref_str_source else None,
                edit_segments=[
                    IdentifierSegment(
                        raw=table_ref_str,
                        type="naked_identifier",
                    ),
                    SymbolSegment(raw=".", type="symbol"),
                ],
            )
        ]
    return LintResult(
        anchor=ref,
        fixes=fixes,
        description="{} reference {!r} found in single table select.".format(
            this_ref_type.capitalize(), ref.raw
        ),
    )
