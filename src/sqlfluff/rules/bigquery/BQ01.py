"""Implementation of Rule BQ01."""

from typing import Optional

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_BQ01(BaseRule):
    """Forbid BigQuery ``WITH`` expressions.

    BigQuery's ``WITH`` expression assigns variables inside an expression and
    then evaluates a final expression:

    .. code-block:: sql

        SELECT WITH(a AS 1, b AS a + 1, b * 2) AS total;

    Some teams prefer to keep statements to CTEs, subqueries or plain
    expressions, and to avoid this construct entirely. This rule flags every
    ``WITH`` expression in the ``bigquery`` dialect.

    This rule only applies to the ``bigquery`` dialect and is disabled by
    default. Enable it with the ``forbid_with_expressions = True`` flag.

    **Anti-pattern**

    Using a ``WITH`` expression.

    .. code-block:: sql

        SELECT WITH(a AS 1, a) AS x;

    **Best practice**

    Rewrite the expression without ``WITH``.

    .. code-block:: sql

        SELECT 1 AS x;

    """

    name = "bigquery.forbid_with_expressions"
    aliases = ()
    groups = ("all", "bigquery")
    config_keywords = ["forbid_with_expressions"]
    crawl_behaviour = SegmentSeekerCrawler({"with_expression"})

    _target_dialects = ("bigquery",)

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        self.forbid_with_expressions: bool

        if not self.forbid_with_expressions:
            return None

        if context.dialect.name not in self._target_dialects:
            # The crawler only finds ``with_expression`` in the bigquery
            # dialect, so this branch is defensive only.
            return None  # pragma: no cover

        return LintResult(anchor=context.segment)
