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

        SELECT 123 as foo, 'sum'

    | **Best practice**
    | If ``force_quote_identifier = False`` and ``preferred_quote_identifier = '"'``
    | (or unspecified, as these are the default), use unquoted identifiers 
    | where possible, and use '"' whenever necessary.

    .. code-block:: sql

        SELECT 123 as foo, "sum"

    | If ``force_quote_identifier = True`` and ``preferred_quote_identifier = "`"``,
    | use preferred quote identifiers any time.

    .. code-block:: sql

        SELECT 123 as `foo`, `sum`

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

        quote = self.preferred_quote_identifier

        # If the configuration says to not force the identifier quoting, then
        # simply care about the quoted identifiers.
        if self.force_quote_identifier:
            context_policy = ("naked_identifier", "quoted_identifier")
        else:
            context_policy = ("quoted_identifier")

        # We only care about quoted identifiers and possibly naked identifiers if
        # the configuration setting is forcing identifiers to be quoted.
        if context.segment.name not in context_policy:
            return None

        # Manage cases of quoted identifiers must be forced first.
        if self.force_quote_identifier:
            if context.segment.name == "naked_identifier":
                identifier_contents = context.segment.raw
            else:
                identifier_contents = context.segment.raw[1:-1]

            # If the identifier_contents contains any occurrence of the preferred quote,
            # ignore this rule for now.
            if quote in identifier_contents:
                # TODO: if different levels of criticity can be set, this case should
                #       trigger an `info` level.
                return None

            expected = f"{quote}{identifier_contents}{quote}"

            # For naked identifiers, make the rule fails directly.
            if context.segment.name == "naked_identifier":
                return LintResult(
                    context.segment,
                    fixes=[
                        LintFix.replace(
                            context.segment,
                            [
                                CodeSegment(
                                    raw=expected, 
                                    name="quoted_identifier", 
                                    type="identifier"
                                )
                            ],
                        )
                    ],
                    description=f"Missing quoted identifier {expected}.",
                )

            # For quoted identifiers, ensure the quote is the expected one.
            if expected != context.segment.raw:
                desc=f"Wrong quoted identifier. Expected {expected}, got {context.segment.raw}."
                return LintResult(
                    context.segment,
                    fixes=[
                        LintFix.replace(
                            context.segment,
                            [
                                CodeSegment(
                                    raw=expected, 
                                    name="quoted_identifier", 
                                    type="identifier"
                                )
                            ],
                        )
                    ],
                    description=desc,
                )

            # If configuration is set to forced quoted identifiers, 
            # we managed all failure cases.
            return None

        # Now we only deal with NOT forced quoted identifiers configuration 
        # (meaning force_quote_identifier=False).

        # Extract contents of outer quotes.
        quoted_identifier_contents = context.segment.raw[1:-1]

        # If the identifier contents contains any occurrence of the preferred quote,
        # ignore this rule for now.
        if quote in quoted_identifier_contents:
            # TODO: if different levels of criticity can be set, this case should
            #       trigger an `info` level.
            return None

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

        # If this is a reserved keyword, or it is not a valid naked identifier,
        # ensure the quote used is the preferred one.
        expected = f"{quote}{quoted_identifier_contents}{quote}"
        if expected != context.segment.raw:
            return LintResult(
                context.segment,
                fixes=[
                    LintFix.replace(
                        context.segment,
                        [
                            CodeSegment(
                                raw=expected, 
                                name="quoted_identifier", 
                                type="identifier"
                            )
                        ],
                    )
                ],
                description=f"Wrong necessary quoted identifier. Expected {expected}, got {context.segment.raw}.",
            )

        return None
