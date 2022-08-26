"""Implementation of Rule L060."""

from typing import Optional

from sqlfluff.core.parser.segments.raw import CodeSegment
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups


@document_groups
@document_fix_compatible
class Rule_L060(BaseRule):
    """Use ``COALESCE`` instead of ``IFNULL`` or ``NVL``.

    **Anti-pattern**

    ``IFNULL`` or ``NVL`` are used to fill ``NULL`` values.

    .. code-block:: sql

        SELECT ifnull(foo, 0) AS bar,
        FROM baz;

        SELECT nvl(foo, 0) AS bar,
        FROM baz;

    **Best practice**

    Use ``COALESCE`` instead.
    ``COALESCE`` is universally supported,
    whereas Redshift doesn't support ``IFNULL``
    and BigQuery doesn't support ``NVL``.
    Additionally, ``COALESCE`` is more flexible
    and accepts an arbitrary number of arguments.

    .. code-block:: sql

        SELECT coalesce(foo, 0) AS bar,
        FROM baz;

    """

    groups = ("all",)
    crawl_behaviour = SegmentSeekerCrawler({"function_name_identifier"})

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Use ``COALESCE`` instead of ``IFNULL`` or ``NVL``."""
        # We only care about function names, and they should be the
        # only things we get
        assert context.segment.is_type("function_name_identifier")

        # Only care if the function is ``IFNULL`` or ``NVL``.
        if context.segment.raw_upper not in {"IFNULL", "NVL"}:
            return None

        # Create fix to replace ``IFNULL`` or ``NVL`` with ``COALESCE``.
        fix = LintFix.replace(
            context.segment,
            [
                CodeSegment(
                    raw="COALESCE",
                    type="function_name_identifier",
                )
            ],
        )

        return LintResult(
            anchor=context.segment,
            fixes=[fix],
            description=f"Use 'COALESCE' instead of '{context.segment.raw_upper}'.",
        )
