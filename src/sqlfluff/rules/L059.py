"""Implementation of Rule L059."""

from typing import Optional

import regex

from sqlfluff.core.parser.segments.raw import CodeSegment
from sqlfluff.core.rules.base import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)

@document_configuration
@document_fix_compatible
class Rule_L059(BaseRule):
    """Unnecessary quoted identifier.
    
    This rule will fail if the quotes used to quote an identifier are unnecessary, 
    or wrong considering the configuration.
    
    By default, the quotes are optional, but required to double-quotes when identifier 
    is named as a keyword, or contains special characters.

    | **Anti-pattern**
    | In this example, a valid unquoted identifier,
    | that is also not a reserved keyword, is needlessly quoted.

    .. code-block:: sql

        SELECT 123 as "foo"

    | **Best practice**
    | If ``force_quote_identifier = False`` and ``preferred_quote_identifier = '"'`` (or unspecified, as these are the default)
    | Use unquoted identifiers where possible.

    .. code-block:: sql

        SELECT 123 as foo

    | If ``force_quote_identifier = True`` and ``preferred_quote_identifier = "`"``
    | Use preferred quote identifiers any time.
    
    .. code-block:: sql

        SELECT 123 as `foo`

    """

    config_keywords = [
        "force_quote_identifier",
        "preferred_quote_identifier"
    ]
    
    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Unnecessary quoted identifier."""
        # Config type hints
        self.force_quote_identifier: bool
        self.preferred_quote_identifier: str
        
        # TODO: take care of default values for config
        
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
