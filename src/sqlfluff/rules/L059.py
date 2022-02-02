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

    When ``force_quote_identifier = False`` (default behavior), the quotes are 
    unnecessary, except for reserved keywords and special charcters in identifiers.

    | **Anti-pattern**
    | In this example, a valid unquoted identifier,
    | that is also not a reserved keyword, is needlessly quoted.

    .. code-block:: sql

        SELECT 123 as "foo"

    | **Best practice**

    .. code-block:: sql

        SELECT 123 as foo

    When ``force_quote_identifier = True``, the quotes are always necessary, no
    matter if the identifier is valid, a reserved keyword, or contains special
    characters.

    | **Anti-pattern**
    | In this example, a valid unquoted identifier,
    | that is also not a reserved keyword, is required to be quoted.

    .. code-block:: sql

        SELECT 123 as foo

    | **Best practice**

    .. code-block:: sql

        SELECT 123 as "foo" -- For ANSI, ...
        -- or
        SELECT 123 as `foo` -- For BigQuery, MySql, ...

    """

    config_keywords = [
        "force_quote_identifier"
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Unnecessary quoted identifier."""
        # Config type hints
        self.force_quote_identifier: bool

        if self.force_quote_identifier:
            context_policy = ("naked_identifier")
            identifier_contents = context.segment.raw
        else:
            context_policy = ("quoted_identifier")
            identifier_contents = context.segment.raw[1:-1]

        # Ignore the segments that are not of the same type as the defined policy above.
        if context.segment.name not in context_policy:
            return None

        # Manage cases of quoted identifiers must be forced first. 
        # Naked identifiers are _de facto_ making this rule fail as configuration forces
        # them to be quoted.
        # In this case, it cannot be fixed as quote to use is dialect and DBMS
        # configuration dependent.
        if self.force_quote_identifier:
            return LintResult(
                context.segment,
                description=f"Missing quoted identifier {identifier_contents}.",
            )

        # Now we only deal with NOT forced quoted identifiers configuration 
        # (meaning force_quote_identifier=False).

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
