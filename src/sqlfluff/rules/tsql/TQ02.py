"""Implementation of Rule TQ02."""

from typing import Optional

from sqlfluff.core.parser import (
    BaseSegment,
    Dedent,
    Indent,
    KeywordSegment,
    NewlineSegment,
)
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

        return LintResult(
            anchor=procedure_statement.raw_segments[0],
            description="Procedure body with multiple statements should be wrapped "
            "in BEGIN/END block.",
            fixes=[
                LintFix.replace(
                    procedure_statement,
                    [self._wrap_body(procedure_statement, context)],
                )
            ],
        )

    @staticmethod
    def _wrap_body(
        procedure_statement: BaseSegment, context: RuleContext
    ) -> BaseSegment:
        """Wrap the body's statements in a parse-shaped ``begin_end_block``.

        The fix loop doesn't reparse between passes, so the wrapper mirrors
        how ``BEGIN ... END`` parses. The body is then a single statement,
        so the rule doesn't re-fire on its own output.
        """
        children = procedure_statement.segments
        code_idx = [i for i, seg in enumerate(children) if seg.is_code]
        start, end = code_idx[0], code_idx[-1] + 1
        block = context.dialect.get_segment("BeginEndSegment")(
            segments=(
                KeywordSegment("BEGIN"),
                Indent(),
                NewlineSegment(),
                *children[start:end],
                NewlineSegment(),
                Dedent(),
                KeywordSegment("END"),
            )
        )
        statement = context.dialect.get_segment("StatementSegment")(segments=(block,))
        return procedure_statement.copy(
            segments=(*children[:start], statement, *children[end:])
        )
