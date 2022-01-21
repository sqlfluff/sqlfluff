"""Implementation of Rule L056."""
from typing import Optional
from sqlfluff.core.parser.segments.base import BaseSegment

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext


class Rule_L056(BaseRule):
    r"""Avoid Hungarian notation prefixes ``SP_`` and ``TBL_``.

    | **Anti-pattern**
    | Hungarian prefixes `SP_`` and ``TBL_`` encode redundant information in SQL.

    .. code-block:: sql
        :force:

        -- It's already evident that foo is a table without ``TBL`` prefix.

        CREATE TABLE tbl_foo (
            col INT
        );

        -- Additionally in T-SQL, the ``SP_`` prefix is used to
        -- identify system procedures and can adversely affect
        -- performance of the user-defined stored procedure.
        -- It can also break system procedures if there is a naming conflict.

        CREATE PROCEDURE dbo.sp_pull_data
        AS
        SELECT
            ID,
            DataDate,
            CaseOutput
        FROM table1

    | **Best practice**
    | Name tables without the ``TBL_`` prefix.

    .. code-block:: sql
        :force:

        CREATE TABLE foo (
            col INT
        );

        -- Use a non-prefixed name for the stored procedure.

        CREATE PROCEDURE dbo.pull_data
        AS
        SELECT
            ID,
            DataDate,
            CaseOutput
        FROM table1
    """

    @staticmethod
    def _is_hungarian_notation(seg: BaseSegment):
        """Check if an identifier segment is hungarian notation."""
        if seg.is_name("naked_identifier") and (
            seg.raw_upper.startswith("SP_") or seg.raw_upper.startswith("TBL_")
        ):
            return True
        elif seg.is_name("quoted_identifier") and (
            seg.raw_upper[1:].startswith("SP_") or seg.raw_upper[1:].startswith("TBL_")
        ):
            return True
        else:
            return False

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        r"""Avoid Hungarian notation prefixes ``SP_`` and ``TBL_``."""
        # We only care about hungarian object references.
        if not self._is_hungarian_notation(context.segment):
            return None

        return LintResult(context.segment)
