"""Implementation of Rule TQ01."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_TQ01(BaseRule):
    r"""``SP_`` prefix should not be used for user-defined stored procedures in T-SQL.

    **Anti-pattern**

    The ``SP_`` prefix is used to identify system procedures and can adversely
    affect performance of the user-defined stored procedure. It can also break
    system procedures if there is a naming conflict.

    .. code-block:: sql
       :force:

        CREATE PROCEDURE dbo.sp_pull_data
        AS
        SELECT
            ID,
            DataDate,
            CaseOutput
        FROM table1

    **Best practice**

    Use a different name for the stored procedure.

    .. code-block:: sql
       :force:

        CREATE PROCEDURE dbo.pull_data
        AS
        SELECT
            ID,
            DataDate,
            CaseOutput
        FROM table1

        -- Alternatively prefix with USP_ to
        -- indicate a user-defined stored procedure.

        CREATE PROCEDURE dbo.usp_pull_data
        AS
        SELECT
            ID,
            DataDate,
            CaseOutput
        FROM table1
    """

    name = "tsql.sp_prefix"
    aliases = ("L056",)
    groups = ("all", "tsql")
    crawl_behaviour = SegmentSeekerCrawler({"create_procedure_statement"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        r"""``SP_`` prefix should not be used for user-defined stored procedures."""
        # Rule only applies to T-SQL syntax.
        if context.dialect.name != "tsql":
            return None  # pragma: no cover

        # We are only interested in CREATE PROCEDURE statements.
        assert context.segment.is_type("create_procedure_statement")

        # Find the object reference for the stored procedure.
        object_reference_segment = next(
            (s for s in context.segment.segments if s.type == "object_reference")
        )

        # We only want to check the stored procedure name.
        procedure_segment = object_reference_segment.segments[-1]

        # If stored procedure name starts with 'SP\_' then raise lint error.
        if procedure_segment.raw_upper.lstrip('["').startswith("SP_"):
            "s".lstrip
            return LintResult(
                procedure_segment,
                description="'SP_' prefix should not be used for user-defined stored "
                "procedures.",
            )

        return None
