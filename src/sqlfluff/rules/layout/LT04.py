"""Implementation of Rule LT04."""

from sqlfluff.core.parser import (
    BaseSegment,
    CodeSegment,
    CommentSegment,
    PositionMarker,
    PyLexer,
    RegexLexer,
    SourceFix,
    SymbolSegment,
)
from sqlfluff.core.rules import LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.rules.layout.LT03 import Rule_LT03
from sqlfluff.utils.reflow import ReflowSequence

# PL/pgSQL comments in Redshift end at the first */. Standard identifiers
# may contain multibyte UTF-8 characters, including in unquoted names.
_PROCEDURE_LEXERS = {
    "block_comment": RegexLexer("block_comment", r"/\*.*?\*/", CommentSegment),
    "word": RegexLexer(
        "word",
        r"#?(?:[0-9a-zA-Z_]|[^\x00-\x7f])(?:[0-9a-zA-Z_$]|[^\x00-\x7f])*",
        CodeSegment,
    ),
}


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
        if body is None or body.source_fixes or "," not in body.raw:
            return []

        # The outer lexer has already matched the closing delimiter, including
        # its optional tag. Lex the contents so comments and nested strings
        # retain their boundaries without parsing PL/pgSQL statements.
        delimiter = body.raw[: body.raw.index("$", 1) + 1]
        lexer = PyLexer(config=context.config)
        lexer.lexer_matchers = [
            _PROCEDURE_LEXERS.get(matcher.name, matcher)
            for matcher in lexer.lexer_matchers
        ]
        segments, errors = lexer.lex(body.raw[len(delimiter) : -len(delimiter)])
        if errors:
            self.logger.debug("Skipping procedure body with lexer errors: %s", errors)
            return []
        body_tokens = context.dialect.get_segment("FileSegment")(segments)
        assert body.pos_marker
        if body.pos_marker.is_literal():
            fixed = ReflowSequence.from_root(body_tokens, context.config).rebreak(
                target_type="comma"
            )
            if not fixed.get_results():
                return []
            return [
                LintResult(
                    anchor=body,
                    description="Incorrect comma placement in Redshift procedure body.",
                    fixes=[
                        LintFix.replace(
                            body,
                            [body.edit(raw=delimiter + fixed.get_raw() + delimiter)],
                        )
                    ],
                )
            ]

        # Template tags can sit inside this one outer token. Apply each
        # independent comma fix to its literal source range.
        results = []
        for comma in body_tokens.get_children("comma"):
            result = self._procedure_comma_fix(
                context, body, body_tokens, comma, len(delimiter)
            )
            if result:
                results.append(result)
        return results

    @staticmethod
    def _procedure_comma_fix(
        context: RuleContext,
        body: BaseSegment,
        body_tokens: BaseSegment,
        comma: BaseSegment,
        delimiter_length: int,
    ) -> LintResult | None:
        """Map a comma's reflow back to the literal source between adjacent tokens."""
        around = ReflowSequence.from_around_target(comma, body_tokens, context.config)
        fixed = around.rebreak(target_type="comma")
        if not fixed.get_results():
            return None

        first = around.elements[0].segments[0]
        last = around.elements[-1].segments[-1]
        assert (
            body.pos_marker
            and first.pos_marker
            and last.pos_marker
            and comma.pos_marker
        )
        offset = body.pos_marker.templated_slice.start + delimiter_length
        window = slice(
            offset + first.pos_marker.templated_slice.stop,
            offset + last.pos_marker.templated_slice.start,
        )
        template = body.pos_marker.templated_file
        source = template.templated_slice_to_source_slice(window)
        # A separator can move within literal SQL, even when an adjacent
        # argument is templated. Never move it across a template boundary.
        if not template.is_source_slice_literal(source) or (
            template.source_str[source] != template.templated_str[window]
        ):
            return None

        text = fixed.get_raw()
        replacement = text[len(first.raw) : len(text) - len(last.raw)]
        patch = SourceFix(replacement, source, window)
        position = offset + comma.pos_marker.templated_slice.start
        location = slice(position, position + 1)
        anchor = SymbolSegment(
            raw=",",
            type="comma",
            pos_marker=PositionMarker(
                template.templated_slice_to_source_slice(location), location, template
            ),
        )
        return LintResult(
            anchor=anchor,
            description=fixed.get_results()[0].description,
            fixes=[LintFix.replace(body, [body.edit(source_fixes=[patch])])],
        )

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
