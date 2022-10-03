"""Implementation of Rule L059."""

from typing import List, Optional, cast, Type

import regex

from sqlfluff.core.parser.segments.raw import CodeSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.utils.functional import sp, FunctionalContext


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L059(BaseRule):
    """Unnecessary quoted identifier.

    This rule will fail if the quotes used to quote an identifier are (un)necessary
    depending on the ``force_quote_identifier`` configuration.

    When ``prefer_quoted_identifiers = False`` (default behaviour), the quotes are
    unnecessary, except for reserved keywords and special characters in identifiers.

    .. note::
       This rule is disabled by default for Postgres and Snowflake because they allow
       quotes as part of the column name. In other words, ``date`` and ``"date"`` are
       two different columns.

       It can be enabled with the ``force_enable = True`` flag.

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

    groups = ("all",)
    config_keywords = [
        "prefer_quoted_identifiers",
        "ignore_words",
        "ignore_words_regex",
        "force_enable",
    ]
    crawl_behaviour = SegmentSeekerCrawler({"quoted_identifier", "naked_identifier"})
    _dialects_allowing_quotes_in_column_names = ["postgres", "snowflake"]

    # Ignore "password_auth" type to allow quotes around passwords within
    # `CREATE USER` statements in Exasol dialect.
    _ignore_types: List[str] = ["password_auth"]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Unnecessary quoted identifier."""
        # Config type hints
        self.prefer_quoted_identifiers: bool
        self.ignore_words: str
        self.ignore_words_regex: str
        self.force_enable: bool
        # Some dialects allow quotes as PART OF the column name. In other words,
        # these are two different columns:
        # - date
        # - "date"
        # For safety, disable this rule by default in those dialects.
        if (
            context.dialect.name in self._dialects_allowing_quotes_in_column_names
            and not self.force_enable
        ):
            return LintResult()

        # Ignore some segment types
        if FunctionalContext(context).parent_stack.any(sp.is_type(*self._ignore_types)):
            return None

        if self.prefer_quoted_identifiers:
            context_policy = "naked_identifier"
            identifier_contents = context.segment.raw
        else:
            context_policy = "quoted_identifier"
            identifier_contents = context.segment.raw[1:-1]

        # Get the ignore_words_list configuration.
        try:
            ignore_words_list = self.ignore_words_list
        except AttributeError:
            # First-time only, read the settings from configuration. This is
            # very slow.
            ignore_words_list = self._init_ignore_words_list()

        # Skip if in ignore list
        if ignore_words_list and identifier_contents.lower() in ignore_words_list:
            return None

        # Skip if matches ignore regex
        if self.ignore_words_regex and regex.search(
            self.ignore_words_regex, identifier_contents
        ):
            return LintResult(memory=context.memory)

        # Ignore the segments that are not of the same type as the defined policy above.
        # Also TSQL has a keyword called QUOTED_IDENTIFIER which maps to the name so
        # need to explicitly check for that.
        if not context.segment.is_type(
            context_policy
        ) or context.segment.raw.lower() in (
            "quoted_identifier",
            "naked_identifier",
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
        IdentifierSegment = cast(
            Type[CodeSegment], context.dialect.get_segment("IdentifierSegment")
        )

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
                            IdentifierSegment(
                                raw=quoted_identifier_contents,
                                type="naked_identifier",
                            )
                        ],
                    )
                ],
                description=f"Unnecessary quoted identifier {context.segment.raw}.",
            )

        return None

    def _init_ignore_words_list(self):
        """Called first time rule is evaluated to fetch & cache the policy."""
        ignore_words_config: str = str(getattr(self, "ignore_words"))
        if ignore_words_config and ignore_words_config != "None":
            self.ignore_words_list = self.split_comma_separated_string(
                ignore_words_config.lower()
            )
        else:
            self.ignore_words_list = []

        return self.ignore_words_list
