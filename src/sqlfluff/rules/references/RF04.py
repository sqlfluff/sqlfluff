"""Implementation of Rule RF04."""

from typing import Optional

import regex

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.identifers import identifiers_policy_applicable


class Rule_RF04(BaseRule):
    """Keywords should not be used as identifiers.

    This rule flags `reserved` keywords and `future reserved` keywords
    when used as quoted identifiers, as these words are reserved for
    SQL syntax use. Unreserved (non-reserved) keywords are explicitly
    allowed as identifiers by the SQL standard and are therefore not
    flagged by this rule.

    .. note::
       Note that `reserved` keywords cannot be used as unquoted identifiers
       and will cause parsing errors and so are not covered by this rule.

    **Anti-pattern**

    In this example, ``CASE`` (a reserved keyword) is used as an alias.

    .. code-block:: sql

        SELECT
            "case".a
        FROM foo AS "case"

    **Best practice**

    Avoid reserved keywords as the name of an alias.

    .. code-block:: sql

        SELECT
            vee.a
        FROM foo AS vee

    """

    name = "references.keywords"
    aliases = ("L029",)
    groups = ("all", "references")
    crawl_behaviour = SegmentSeekerCrawler({"naked_identifier", "quoted_identifier"})
    config_keywords = [
        "unquoted_identifiers_policy",
        "quoted_identifiers_policy",
        "ignore_words",
        "ignore_words_regex",
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Keywords should not be used as identifiers."""
        # Config type hints
        self.ignore_words_regex: str

        # Skip 1 letter identifiers. These can be datepart keywords
        # (e.g. "d" for Snowflake) but most people expect to be able to use them.
        if len(context.segment.raw) == 1:
            return LintResult(memory=context.memory)

        # Get the identifier text, stripping quotes for quoted identifiers
        is_quoted = context.segment.is_type("quoted_identifier")
        if is_quoted:
            identifier_text = context.segment.raw[1:-1]
        else:
            identifier_text = context.segment.raw

        # Get the ignore list configuration and cache it
        try:
            ignore_words_list = self.ignore_words_list
        except AttributeError:
            # First-time only, read the settings from configuration.
            # So we can cache them for next time for speed.
            ignore_words_list = self._init_ignore_string()

        # Skip if in ignore list
        if ignore_words_list and identifier_text.upper() in ignore_words_list:
            return LintResult(memory=context.memory)

        # Skip if matches ignore regex
        if self.ignore_words_regex and regex.search(
            self.ignore_words_regex, identifier_text
        ):
            return LintResult(memory=context.memory)

        if (
            is_quoted
            and identifiers_policy_applicable(
                self.quoted_identifiers_policy,  # type: ignore
                context.parent_stack,
            )
            and (
                identifier_text.upper()
                in context.dialect.sets("reserved_keywords")
                or identifier_text.upper()
                in context.dialect.sets("future_reserved_keywords")
            )
        ):
            return LintResult(anchor=context.segment)
        else:
            return None

    def _init_ignore_string(self) -> list[str]:
        """Called first time rule is evaluated to fetch & cache the ignore_words."""
        # Use str() in case bools are passed which might otherwise be read as bool
        ignore_words_config = str(getattr(self, "ignore_words"))
        if ignore_words_config and ignore_words_config != "None":
            self.ignore_words_list = self.split_comma_separated_string(
                ignore_words_config.upper()
            )
        else:
            self.ignore_words_list = []

        ignore_words_list = self.ignore_words_list
        return ignore_words_list
