"""Implementation of Rule TQ02."""

from typing import List, Optional

from sqlfluff.core.parser import BaseSegment, KeywordSegment, NewlineSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_TQ02(BaseRule):
    """Procedure bodies with multiple statements should be wrapped in BEGIN/END.

    **Anti-pattern**

    Procedure bodies with multiple statements should be wrapped in BEGIN/END
    for clarity and consistency.

    .. code-block:: sql
       :force:

        CREATE PROCEDURE Reporting.MultipleStatements
        AS
        SELECT
            [ID],
            [DataDate],
            [CaseOutput]
        FROM Table1;

        SELECT
            [ID],
            [DataDate],
            [CaseOutput]
        FROM Table2;

    **Best practice**

    Wrap procedure bodies with multiple statements in BEGIN/END blocks.

    .. code-block:: sql
       :force:

        CREATE PROCEDURE Reporting.MultipleStatements
        AS
        BEGIN
            SELECT
                [ID],
                [DataDate],
                [CaseOutput]
            FROM Table1;

            SELECT
                [ID],
                [DataDate],
                [CaseOutput]
            FROM Table2;
        END
    """

    name = "tsql.procedure_begin_end"
    aliases = ()
    groups = ("all", "tsql")
    crawl_behaviour = SegmentSeekerCrawler({"create_procedure_statement"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Procedure bodies with multiple statements should be wrapped in BEGIN/END."""
        # Rule only applies to T-SQL syntax.
        if context.dialect.name != "tsql":
            return None  # pragma: no cover

        # We are only interested in CREATE/ALTER PROCEDURE statements.
        assert context.segment.is_type("create_procedure_statement")

        # Find the procedure_statement (the body after AS)
        procedure_statement = None
        for seg in context.segment.segments:
            if seg.is_type("procedure_statement"):
                procedure_statement = seg
                break

        if not procedure_statement:
            return None  # pragma: no cover

        # Get direct statement children (excluding whitespace, newlines, meta, etc.)
        statements = [
            seg for seg in procedure_statement.segments if seg.is_type("statement")
        ]

        # If there are fewer than 2 statements, no need for BEGIN/END
        if len(statements) < 2:
            return None

        # Check if the first statement is already a begin_end_block
        if statements[0].segments:
            first_child = statements[0].segments[0]
            if first_child.is_type("begin_end_block"):
                # Already wrapped in BEGIN/END
                return None  # pragma: no cover
        else:
            # Defensive: statement with no segments shouldn't happen in valid parsed SQL
            return None  # pragma: no cover

        # We have multiple statements without BEGIN/END - create a fix
        fixes = self._create_begin_end_fixes(procedure_statement, statements)

        return LintResult(
            anchor=procedure_statement,
            description="Procedure body with multiple statements should be wrapped "
            "in BEGIN/END block.",
            fixes=fixes,
        )

    def _create_begin_end_fixes(
        self, procedure_statement: BaseSegment, statements: List[BaseSegment]
    ) -> List[LintFix]:
        """Create fixes to wrap the procedure body in BEGIN/END."""
        # The strategy: insert BEGIN at the start and END at the end
        # We need to find anchor points in the actual segment list

        # Find first statement segment in procedure_statement.segments
        first_statement_idx = None
        for idx, seg in enumerate(procedure_statement.segments):
            if seg in statements:
                first_statement_idx = idx
                break

        if first_statement_idx is None:
            return []  # pragma: no cover

        # Find last statement segment
        last_statement_idx = None
        for idx in range(len(procedure_statement.segments) - 1, -1, -1):
            seg = procedure_statement.segments[idx]
            if seg in statements:
                last_statement_idx = idx
                break

        if last_statement_idx is None:
            return []  # pragma: no cover

        fixes = []

        # Insert BEGIN before first statement
        begin_keyword = KeywordSegment("BEGIN")
        newline = NewlineSegment()

        fixes.append(
            LintFix.create_before(
                procedure_statement.segments[first_statement_idx],
                [begin_keyword, newline],
            )
        )

        # Insert END after last statement and its terminator (if present)
        # In the current branch, statement_terminator is a peer of statement,
        # so we need to check if there's a terminator after the last statement
        insert_after_seg = procedure_statement.segments[last_statement_idx]

        # Check if there's a statement_terminator after the last statement
        for idx in range(last_statement_idx + 1, len(procedure_statement.segments)):
            seg = procedure_statement.segments[idx]
            if seg.is_type("statement_terminator"):
                insert_after_seg = seg
                break
            elif seg.is_code:
                # Hit another code segment, no terminator after last statement
                break

        end_keyword = KeywordSegment("END")

        # Add newline before END
        fixes.append(
            LintFix.create_after(
                insert_after_seg,
                [newline, end_keyword],
            )
        )

        return fixes
