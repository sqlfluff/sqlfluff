"""Implementation of Rule L019."""

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.utils.reflow import ReflowSequence


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L019(BaseRule):
    """Leading/Trailing comma enforcement.

    **Anti-pattern**

    There is a mixture of leading and trailing commas.

    .. code-block:: sql

        SELECT
            a
            , b,
            c
        FROM foo

    **Best practice**

    By default, `SQLFluff` prefers trailing commas. However it
    is configurable for leading commas. The chosen style must be used
    consistently throughout your SQL.

    .. code-block:: sql

        SELECT
            a,
            b,
            c
        FROM foo

        -- Alternatively, set the configuration file to 'leading'
        -- and then the following would be acceptable:

        SELECT
            a
            , b
            , c
        FROM foo
    """

    groups = ("all",)
    crawl_behaviour = SegmentSeekerCrawler({"comma"})
    _adjust_anchors = True

    def _eval(self, context: RuleContext) -> LintResult:
        """Enforce comma placement.

        For leading commas we're looking for trailing commas, so
        we look for newline segments. For trailing commas we're
        looking for leading commas, so we look for the comma itself.

        We also want to handle proper whitespace removal/addition. We remove
        any trailing whitespace after the leading comma, when converting a
        leading comma to a trailing comma. We add whitespace after the leading
        comma when converting a trailing comma to a leading comma.
        """
        fixes = (
            ReflowSequence.from_around_target(
                context.segment,
                root_segment=context.parent_stack[0],
                config=context.config,
            )
            .rebreak()
            .get_fixes()
        )

        if not fixes:
            return LintResult()

        desired_position = context.config.get(
            "line_position", ("layout", "type", "comma")
        )

        return LintResult(
            context.segment,
            fixes,
            description=(
                "Found trailing comma. Expected only leading."
                if desired_position == "leading"
                else "Found leading comma. Expected only trailing."
            ),
        )
