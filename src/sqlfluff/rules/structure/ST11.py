"""Implementation of Rule ST11."""

from collections.abc import Iterator
from typing import cast

from sqlfluff.core.parser.segments import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.dialects.dialect_ansi import ObjectReferenceSegment
from sqlfluff.utils.analysis.query import Query


class UnqualifiedReferenceError(ValueError):
    """Custom exception for signalling when a reference is unqualified."""


class Rule_ST11(BaseRule):
    """Joined table not referenced in query.

    This rule will check if there are any tables that are referenced in the
    ``FROM`` or ``JOIN`` clause of a ``SELECT`` statement, but where no
    columns from that table are referenced in the any of the other clauses.
    Because some types of join are often used as filters, or to otherwise
    control granularity without being referenced (e.g. ``INNER`` and ``CROSS``),
    this rule only applies to explicit ``OUTER`` joins (i.e. ``LEFT``, ``RIGHT``
    and ``FULL`` joins).

    This rule relies on all of the column references in the ``SELECT``
    statement being qualified with at least the table name, and so is
    designed to work alongside :sqlfluff:ref:`references.qualification`
    (:sqlfluff:ref:`RF02`). This is because without the knowledge of what
    columns exist in each upstream table, the rule is unable to resolve
    which table an unqualified column reference is pulled from.

    This rule does not propose a fix, because it assumes that it an unused
    table is a mistake, but doesn't know whether the mistake was the join,
    or the mistake was not using it.

    **Anti-pattern**

    In this example, the table ``bar`` is included in the ``JOIN`` clause
    but not columns from it are referenced in

    .. code-block:: sql

        SELECT
            foo.a,
            foo.b
        FROM foo
        LEFT JOIN bar ON foo.a = bar.a

    **Best practice**

    Remove the join, or use the table.

    .. code-block:: sql

        SELECT foo.a, vee.b
        FROM foo;

        SELECT
            foo.a,
            foo.b,
            bar.c
        FROM foo
        LEFT JOIN bar ON foo.a = bar.a

    In the (*very rare*) situations that it is logically necessary to include
    a table in a join clause, but not otherwise refer to it (likely for
    granularity reasons, or as a stepping stone to another table), we recommend
    ignoring this rule for that specific line by using ``-- noqa: ST11`` at
    the end of the line.

    .. note:

       To avoid sticky situations with casing and quoting in different dialects
       this rule uses case-insensitive comparison. That means if you have two
       tables with the same name, but different cases (and you're really sure
       that's a good idea!), then this rule may not detect if one of them is
       unused.
    """

    name = "structure.unused_join"
    aliases = ()
    groups: tuple[str, ...] = ("all", "structure")
    crawl_behaviour = SegmentSeekerCrawler({"select_statement"})
    is_fix_compatible = False

    def _extract_references_from_expression(self, segment: BaseSegment) -> str:
        assert segment.is_type("from_expression_element")
        # If there's an alias, we care more about that.
        alias_expression = segment.get_child("alias_expression")
        if alias_expression:
            alias_identifier = alias_expression.get_child("identifier")
            if alias_identifier:
                # Append the raw representation and the from expression.
                return alias_identifier.raw_normalized(casefold=False).upper()
        # Otherwise if no alias, we need the name of the object we're
        # referencing.
        for table_reference in segment.recursive_crawl(
            "table_reference", no_recursive_seg_type="select_statement"
        ):
            return table_reference.segments[-1].raw_normalized(casefold=False).upper()
        # If we can't find a reference, just return an empty string
        # to signal that there isn't one. This could be a case of a
        # VALUES clause, or anything else selectable which hasn't
        # been given an alias.
        return ""

    def _extract_referenced_tables(
        self, segment: BaseSegment, allow_unqualified: bool = False
    ) -> Iterator[str]:
        # NOTE: Here we _may_ recurse into subqueries to find references.
        for ref in segment.recursive_crawl("column_reference"):
            obj_ref = cast(ObjectReferenceSegment, ref)
            parts = list(obj_ref.iter_raw_references())
            if len(parts) < 2:
                if allow_unqualified:
                    continue
                else:
                    raise UnqualifiedReferenceError(ref.raw)
            # Remove any quoting characters when returning.
            yield parts[-2].part.upper().strip("\"'`[]")

    def _extract_references_from_select(
        self, segment: BaseSegment
    ) -> list[tuple[str, BaseSegment]]:
        assert segment.is_type("select_statement")
        # Tables which exist in the query
        joined_tables = []
        # Tables which are referred to elsewhere.
        # NOTE: We populate this here if a table is referred to in the
        # join clause for a *different* table.
        referenced_tables = []
        # Extract the information from any FROM clauses.
        from_clause = segment.get_child("from_clause")
        if not from_clause:  # No from, no joins, no worries
            return []
        for from_expression in from_clause.get_children("from_expression"):
            # Handle the main FROM expression.
            for from_expression_elem in from_expression.get_children(
                "from_expression_element"
            ):
                ref = self._extract_references_from_expression(from_expression_elem)
                if ref:
                    joined_tables.append((ref, from_expression_elem))
                if len(joined_tables) > 1:
                    # We had an implicit cross join, don't add any FROM tables to check.
                    joined_tables.clear()
                    break

            # Then handle any JOIN clauses.
            for join_clause in from_expression.get_children("join_clause"):
                # Extract the join keywords used so we can exclude any which are
                # configured. For example, INNER joins are often used as filters
                # without being referenced.
                join_keywords = {
                    keyword.raw_upper for keyword in join_clause.get_children("keyword")
                }
                _this_clause_refs = []
                for from_expression_elem in join_clause.get_children(
                    "from_expression_element"
                ):
                    ref = self._extract_references_from_expression(from_expression_elem)
                    # Only mark it as a possible issue if it's an explicit LEFT, RIGHT
                    # or FULL join.
                    if ref and join_keywords.intersection({"FULL", "LEFT", "RIGHT"}):
                        joined_tables.append((ref, from_expression_elem))
                        _this_clause_refs.append(ref)
                    # If we have functions in the table_expression, we referenced them,
                    # add them to the list.
                    for tbl_ref in self._extract_referenced_tables(
                        from_expression_elem, allow_unqualified=True
                    ):
                        if tbl_ref not in _this_clause_refs:
                            referenced_tables.append(tbl_ref)

                # Look for any references in the ON clause to other tables.
                for join_on_condition in join_clause.get_children("join_on_condition"):
                    # We can tolerate some unqualified references here, so no need
                    # to raise exceptions.
                    for tbl_ref in self._extract_referenced_tables(
                        join_on_condition, allow_unqualified=True
                    ):
                        if tbl_ref not in _this_clause_refs:
                            referenced_tables.append(tbl_ref)

        # NOTE: For the following debug message, it's important to note that if tables
        # are brought in with join type which isn't covered - (e.g. an INNER JOIN), then
        # they won't be shown as "in scope".
        self.logger.debug(
            f"Processed SELECT statement.\nJoined tables in scope: {joined_tables}\n"
            f"...of which referenced in non-self join clauses: {referenced_tables}"
        )
        # If there's only a single table in this SELECT, we don't return
        # *ANY*. That's to shortcut this rule to not consider single table
        # selects.
        if len(joined_tables) <= 1:
            return []
        # If a table is referenced elsewhere in the join, we shouldn't consider
        # it as a potential issue later. So purge them from the list now.
        return [
            (ref, seg) for (ref, seg) in joined_tables if ref not in referenced_tables
        ]

    def _eval(self, context: RuleContext) -> list[LintResult]:
        """Implement the logic to detect unused tables in joins.

        First we fetch all the tables brought *into* the query via
        either FROM or JOIN clauses. We then search for all the
        tables referenced in all the other clauses and look for
        mismatches.

        NOTE: If *any* references aren't appropriately qualified,
        this rule will abort (because it won't know how to resolve
        the ambiguous references). That means it relies on RF02
        having been already applied.
        """
        reference_clause_types = [
            "select_clause",
            "where_clause",
            "groupby_clause",
            "orderby_clause",
            "having_clause",
            "qualify_clause",
        ]

        joined_tables = self._extract_references_from_select(context.segment)
        if not joined_tables:  # No from, no joins, no worries
            self.logger.debug("No tables found in scope.")
            return []
        # We should now have a list of joined tables (or aliases) which
        # aren't otherwise referred to in the FROM clause. Now we work
        # through all the other clauses.
        table_references = set()
        for other_clause in context.segment.get_children(*reference_clause_types):
            try:
                for tbl_ref in self._extract_referenced_tables(
                    other_clause, allow_unqualified=False
                ):
                    self.logger.debug(f"    {tbl_ref!r} referenced in {other_clause}")
                    table_references.add(tbl_ref)
            except UnqualifiedReferenceError as err:
                self.logger.debug(
                    f"Found an unqualified ref '{err}'. Aborting for this SELECT."
                )
                return []

        query: Query = Query.from_segment(context.segment, context.dialect)
        for selectable in query.selectables:
            for wcinfo in selectable.get_wildcard_info():
                table_references |= {t.upper() for t in wcinfo.tables}

        results: list[LintResult] = []
        self.logger.debug(
            f"Select statement {context.segment} references "
            f"tables: {table_references}.\n"
            f"Joined tables to asses: {joined_tables}"
        )
        for tbl_ref, segment in joined_tables:
            if tbl_ref not in table_references:
                results.append(
                    LintResult(
                        anchor=segment,
                        description=(
                            f"Joined table '{segment.raw}' not referenced "
                            "elsewhere in query"
                        ),
                    )
                )
        return results
