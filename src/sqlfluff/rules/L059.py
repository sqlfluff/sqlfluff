"""Implementation of Rule L059."""

from typing import Optional

import regex

from sqlfluff.core.parser.segments.raw import CodeSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L059(BaseRule):
    """Unnecessary quoted identifier.

    | **Anti-pattern**
    | In this example, a valid unquoted identifier,
    | that is also not a reserved keyword, is needlessly quoted.

    .. code-block:: sql

        SELECT 123 as "foo"

    | **Best practice**
    | Use unquoted identifiers where possible.

    .. code-block:: sql

        SELECT 123 as foo

    """

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Unnecessary quoted identifier."""
        # We only care about quoted identifiers.
        if context.segment.name != "quoted_identifier":
            return None

        # Extract contents of outer quotes.
        quoted_identifier_contents = context.segment.raw[1:-1]

        # Retrieve NakedIdentifierSegment RegexParser for the dialect.
        naked_identifier_parser = context.dialect._library["NakedIdentifierSegment"]

        # Check if quoted_identifier_contents could be a valid naked identifier
        # and that it is not a reserved keyword.
        if (
            regex.fullmatch(
                naked_identifier_parser.template,
                quoted_identifier_contents,
                regex.IGNORECASE,
            )
            is not None
        ) and (
            regex.fullmatch(
                naked_identifier_parser.anti_template,
                quoted_identifier_contents,
                regex.IGNORECASE,
            )
            is None
        ):
            return LintResult(
                context.segment,
                fixes=[
                    LintFix.replace(
                        context.segment,
                        [
                            CodeSegment(
                                raw=quoted_identifier_contents,
                                name="naked_identifier",
                                type="identifier",
                            )
                        ],
                    )
                ],
                description=f"Unnecessary quoted identifier {context.segment.raw}.",
            )

        return None
