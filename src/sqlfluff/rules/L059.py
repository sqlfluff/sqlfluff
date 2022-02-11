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

    This rule will fail if the quotes used to quote an identifier are (un)necessary
    depending on the ``force_quote_identifier`` configuration.

    When ``prefer_quoted_identifiers = False`` (default behaviour), the quotes are
    unnecessary, except for reserved keywords and special characters in identifiers.

    **Anti-pattern**

    In this example, a valid unquoted identifier,
    that is also not a reserved keyword, is needlessly quoted.

    .. code-block:: sql

        SELECT 123 as "foo"

    **Best practice**

    Use unquoted identifiers where possible.

    .. code-block:: sql

        SELECT 123 as foo

    When ``prefer_quoted_identifiers = True``, the quotes are always necessary, no
    matter if the identifier is valid, a reserved keyword, or contains special
    characters.

    .. note::
       Note due to different quotes being used by different dialects supported by
       `SQLFluff`, and those quotes meaning different things in different contexts,
       this mode is not ``sqlfluff fix`` compatible.

    **Anti-pattern**

    In this example, a valid unquoted identifier, that is also not a reserved keyword,
    is required to be quoted.

    .. code-block:: sql

        SELECT 123 as foo

    **Best practice**
    Use quoted identifiers.

    .. code-block:: sql

        SELECT 123 as "foo" -- For ANSI, ...
        -- or
        SELECT 123 as `foo` -- For BigQuery, MySql, ...

    """

    config_keywords = ["prefer_quoted_identifiers"]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Unnecessary quoted identifier."""
        # Config type hints
        self.prefer_quoted_identifiers: bool

        if self.prefer_quoted_identifiers:
            context_policy = "naked_identifier"
            identifier_contents = context.segment.raw
        else:
            context_policy = "quoted_identifier"
            identifier_contents = context.segment.raw[1:-1]

        # Ignore the segments that are not of the same type as the defined policy above.
        # Also TSQL has a keyword called QUOTED_IDENTIFIER which maps to the name so
        # need to explicity check for that.
        if (
            context.segment.name not in context_policy
            or context.segment.raw.lower() in ("quoted_identifier", "naked_identifier")
        ):
            return None

        # Manage cases of identifiers must be quoted first.
        # Naked identifiers are _de facto_ making this rule fail as configuration forces
        # them to be quoted.
        # In this case, it cannot be fixed as which quote to use is dialect dependent
        if self.prefer_quoted_identifiers:
            return LintResult(
                context.segment,
                description=f"Missing quoted identifier {identifier_contents}.",
            )

        # Now we only deal with NOT forced quoted identifiers configuration
        # (meaning prefer_quoted_identifiers=False).

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
