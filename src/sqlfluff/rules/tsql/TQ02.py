"""Implementation of Rule TQ02."""

from typing import Optional

from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_TQ02(BaseRule):
    r"""Use ``SET` rather than ``SELECT`` to assign variables in T-SQL.

    **Anti-pattern**

    .. code-block:: sql

        SELECT @VARIABLE = X.ID FROM X WHERE X.EMAIL = 'foo@bar.com';

    **Best practice**

    Variable value is ambiguous after the above query if it returns >1 row.
    Avoid this by re-writing as SET statement; this will error if >1 row is returned.
    TODO: automate ability to fix; the following re-writing only applies in the simplest cases with no other projections or joins

    .. code-block:: sql

        SET @VARIABLE = ( SELECT X.ID FROM X WHERE X.EMAIL = 'foo@bar.com' );

    """

    name = "tsql.select_into_variable"
    aliases = ()
    groups = ("all", "tsql")
    # NB T-SQL dialect code uses the term 'parameter' whenever lexing '@identifier'
    # This case is 'local variable' in MS docs so we use 'variable' in user-facing docs here
    crawl_behaviour = SegmentSeekerCrawler({"parameter_assignment"})
    is_fix_compatible = False

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Enforce SET over SELECT for assigning local variables."""

        # Rule only applies to T-SQL syntax.
        if context.dialect.name != "tsql":
            return None  # pragma: no cover

        # We are only interested in CREATE PROCEDURE statements.
        assert context.segment.is_type("parameter_assignment")

        # Warning depends on parent element
        _parent: BaseSegment = context.parent_stack[-1]
        if _parent.is_type("set_segment"):
            return None
        elif _parent.is_type("select_clause_element"):
            return LintResult(
                _parent,
                description="Prefer 'SET' for variable assignment over 'SELECT'.",
            )
        else:  # pragma: no cover
            raise NotImplementedError(
                "T-SQL parameter assignment not within SET or SELECT clause?  Raise this as a bug on GitHub."
            )
