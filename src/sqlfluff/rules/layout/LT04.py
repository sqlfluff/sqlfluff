"""Implementation of Rule LT04."""

from sqlfluff.core.parser import Lexer
from sqlfluff.core.rules import LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.rules.layout.LT03 import Rule_LT03
from sqlfluff.utils.reflow import ReflowSequence


class Rule_LT04(Rule_LT03):
    """Leading/Trailing comma enforcement.

    The configuration for whether operators should be ``trailing`` or
    ``leading`` is part of :ref:`layoutconfig`. The default configuration is:

    .. code-block:: cfg

        [sqlfluff:layout:type:comma]
        line_position = trailing

    In Redshift this rule also checks separator commas inside dollar-quoted
    stored procedure bodies. The body remains a quoted literal for other rules.

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

    name = "layout.commas"
    aliases = ("L019",)
    groups = ("all", "layout")
    crawl_behaviour = SegmentSeekerCrawler({"comma", "function_definition"})
    _adjust_anchors = True
    is_fix_compatible = True

    def _redshift_procedure_commas(self, context: RuleContext) -> list[LintResult]:
        """Reflow separators in a dollar-quoted procedure using Redshift tokens."""
        if context.dialect.name != "redshift" or not context.parent_stack[-1].is_type(
            "create_procedure_statement"
        ):
            return []

        # SET options can also contain dollar-quoted literals. Only the literal
        # immediately following AS is procedure code.
        code = [seg for seg in context.segment.segments if seg.is_code]
        body = next(
            (
                value
                for keyword, value in zip(code, code[1:])
                if keyword.raw_upper == "AS" and value.is_type("dollar_quote")
            ),
            None,
        )
        if body is None or "," not in body.raw:
            return []

        # The outer lexer has already matched the closing delimiter, including
        # its optional tag. Lex the contents so comments and nested strings
        # retain their boundaries without parsing PL/pgSQL statements.
        delimiter = body.raw[: body.raw.index("$", 1) + 1]
        segments, errors = Lexer(config=context.config).lex(
            body.raw[len(delimiter) : -len(delimiter)]
        )
        if errors:
            self.logger.debug("Skipping procedure body with lexer errors: %s", errors)
            return []
        body_tokens = context.dialect.get_segment("FileSegment")(segments)
        sequence = ReflowSequence.from_root(body_tokens, context.config)
        fixed = sequence.rebreak(target_type="comma")
        if not fixed.get_results():
            return []
        return [
            LintResult(
                anchor=body,
                fixes=[
                    LintFix.replace(
                        body, [body.edit(raw=delimiter + fixed.get_raw() + delimiter)]
                    )
                ],
                description="Incorrect comma placement in Redshift procedure body.",
            )
        ]

    def _eval(self, context: RuleContext) -> list[LintResult]:
        """Enforce comma placement.

        For the fixing routines we delegate to the reflow utils. However
        for performance reasons we have some initial shortcuts to quickly
        identify situations which are _ok_ to avoid the overhead of the
        full reflow path.
        """
        if context.segment.is_type("function_definition"):
            return self._redshift_procedure_commas(context)

        comma_positioning = context.config.get(
            "line_position", ["layout", "type", "comma"]
        )
        # NOTE: These shortcuts assume that any newlines will be direct
        # siblings of the comma in question. This isn't _always_ the case
        # but is true often enough to have meaningful upside from early
        # detection.
        if self._check_trail_lead_shortcut(
            context.segment_idx, context.parent_stack[-1], comma_positioning
        ):
            return [LintResult()]

        return (
            ReflowSequence.from_around_target(
                context.segment,
                root_segment=context.parent_stack[0],
                config=context.config,
            )
            .rebreak()
            .get_results()
        )
