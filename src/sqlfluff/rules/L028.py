"""Implementation of Rule L028."""

from typing import Iterator, List, Optional, Set

from sqlfluff.core.dialects.common import AliasInfo, ColumnAliasInfo
from sqlfluff.core.parser.segments.base import BaseSegment, IdentitySet
from sqlfluff.core.parser.segments.raw import SymbolSegment
from sqlfluff.utils.analysis.select import SelectStatementColumnsAndTables
from sqlfluff.utils.analysis.select_crawler import Query, SelectCrawler
from sqlfluff.core.rules import (
    BaseRule,
    LintFix,
    LintResult,
    EvalResultType,
    RuleContext,
)
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import sp, FunctionalContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.dialects.dialect_ansi import IdentifierSegment


_START_TYPES = ["select_statement", "set_expression", "with_compound_statement"]


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L028(BaseRule):
    """References should be consistent in statements with a single table.

    .. note::
        For BigQuery, Hive and Redshift this rule is disabled by default.
        This is due to historical false positives associated with STRUCT data types.
        This default behaviour may be changed in the future.
        The rule can be enabled with the ``force_enable = True`` flag.

    "consistent" will be fixed to "qualified" if inconsistency is found.

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

    groups = ("all",)
    config_keywords = [
        "single_table_references",
        "force_enable",
    ]
    crawl_behaviour = SegmentSeekerCrawler(set(_START_TYPES))
    _is_struct_dialect = False
    _dialects_with_structs = ["bigquery", "hive", "redshift"]
    # This could be turned into an option
    _fix_inconsistent_to = "qualified"

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

        if not FunctionalContext(context).parent_stack.any(sp.is_type(*_START_TYPES)):
            crawler = SelectCrawler(context.segment, context.dialect)
            visited: IdentitySet = IdentitySet()
            if crawler.query_tree:
                # Recursively visit and check each query in the tree.
                return list(self._visit_queries(crawler.query_tree, visited))
        return None

    def _visit_queries(
        self, query: Query, visited: IdentitySet
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
                # the *parent* query level.
                table_search_root = query.parent if query.parent else query
                query_list = (
                    SelectCrawler.get(
                        table_search_root, table_search_root.selectables[0].selectable
                    )
                    if table_search_root.selectables
                    else []
                )
                filtered_query_list = [q for q in query_list if isinstance(q, str)]
                if len(filtered_query_list) != 1:
                    # If more than one table name is visible, check for and report
                    # potential lint warnings, but don't generate fixes, because
                    # fixes are unsafe if there's more than one table visible.
                    fixable = False
                yield from _check_references(
                    select_info.table_aliases,
                    select_info.standalone_aliases,
                    select_info.reference_buffer,
                    select_info.col_aliases,
                    self.single_table_references,  # type: ignore
                    self._is_struct_dialect,
                    self._fix_inconsistent_to,
                    fixable,
                )
        children = list(query.children)
        # 'query.children' includes CTEs and "main" queries, but not queries in
        # the "FROM" list. We want to visit those as well.
        if select_info:
            for a in select_info.table_aliases:
                for q in SelectCrawler.get(query, a.from_expression_element):
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
            yield from self._visit_queries(child, visited)


def _check_references(
    table_aliases: List[AliasInfo],
    standalone_aliases: List[str],
    references: List[BaseSegment],
    col_aliases: List[ColumnAliasInfo],
    single_table_references: str,
    is_struct_dialect: bool,
    fix_inconsistent_to: Optional[str],
    fixable: bool,
) -> Iterator[LintResult]:
    """Iterate through references and check consistency."""
    # A buffer to keep any violations.
    col_alias_names: List[str] = [c.alias_identifier_name for c in col_aliases]
    table_ref_str: str = table_aliases[0].ref_str
    table_ref_str_source = table_aliases[0].segment
    # Check all the references that we have.
    seen_ref_types: Set[str] = set()
    for ref in references:
        this_ref_type: str = ref.qualification()  # type: ignore
        if this_ref_type == "qualified" and is_struct_dialect:
            # If this col appears "qualified" check if it is more logically a struct.
            if next(ref.iter_raw_references()).part != table_ref_str:  # type: ignore
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
        )

        seen_ref_types.add(this_ref_type)
        if not lint_res:
            continue

        if fix_inconsistent_to and single_table_references == "consistent":
            # If we found a "consistent" error but we have a fix directive,
            # recurse with a different single_table_references value
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
            )

        yield lint_res


def _validate_one_reference(
    single_table_references: str,
    ref: BaseSegment,
    this_ref_type: str,
    standalone_aliases: List[str],
    table_ref_str: str,
    table_ref_str_source: Optional[BaseSegment],
    col_alias_names: List[str],
    seen_ref_types: Set[str],
    fixable: bool,
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

    # Oddball case: tsql table variables can't be used to qualify references.
    # This appears here as an empty string for table_ref_str.
    if not table_ref_str:
        return None

    # Certain dialects allow use of SELECT alias in WHERE clauses
    if ref.raw in col_alias_names:
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
            fixes = [LintFix.delete(el) for el in ref.segments[:2]] if fixable else None
            return LintResult(
                anchor=ref,
                fixes=fixes,
                description="{} reference {!r} found in single table "
                "select.".format(this_ref_type.capitalize(), ref.raw),
            )

        fixes = None
        if fixable:
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
            description="{} reference {!r} found in single table "
            "select.".format(this_ref_type.capitalize(), ref.raw),
        )

    return None
