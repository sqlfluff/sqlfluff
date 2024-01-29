"""Implementation of Rule CV10."""

from typing import Optional

import regex

from sqlfluff.core.parser import LiteralSegment
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, rsp


class Rule_CV10(BaseRule):
    r"""Consistent usage of preferred quotes for quoted literals.

    Some databases allow quoted literals to use either single or double quotes.
    Prefer one type of quotes as specified in rule setting, falling back to
    alternate quotes to reduce the need for escapes.

    Dollar-quoted raw strings are excluded from this rule, as they are mostly used for
    literal UDF Body definitions.

    .. note::
       This rule only checks quoted literals and not quoted identifiers as they often
       cannot interchange single and double quotes

       This rule is only enabled for dialects that allow single *and* double quotes for
       quoted literals
       (currently ``bigquery``, ``databricks``, ``hive``, ``mysql``, ``sparksql``).
       It can be enabled for other dialects with the ``force_enable = True`` flag.

    **Anti-pattern**

    .. code-block:: sql
       :force:

        select
            "abc",
            'abc',
            "\"",
            "abc" = 'abc'
        from foo

    **Best practice**

    Ensure all quoted literals use preferred quotes, unless escaping can be reduced by
    using alternate quotes.

    .. code-block:: sql
       :force:

        select
            "abc",
            "abc",
            '"',
            "abc" = "abc"
        from foo

    """

    name = "convention.quoted_literals"
    aliases = ("L064",)
    groups = ("all", "convention")
    config_keywords = ["preferred_quoted_literal_style", "force_enable"]
    crawl_behaviour = SegmentSeekerCrawler({"literal"})
    targets_templated = True
    is_fix_compatible = True
    _dialects_with_double_quoted_strings = [
        "bigquery",
        "databricks",
        "hive",
        "mysql",
        "sparksql",
    ]

    _quotes_mapping = {
        "single_quotes": {
            "common_name": "single quotes",
            "preferred_quote_char": "'",
            "alternate_quote_char": '"',
        },
        "double_quotes": {
            "common_name": "double quotes",
            "preferred_quote_char": '"',
            "alternate_quote_char": "'",
        },
    }
    # BigQuery string prefix characters.
    _string_prefix_chars = "rbRB"

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        # Config type hints
        self.preferred_quoted_literal_style: str
        self.force_enable: bool

        # Only care about quoted literal segments.
        if not context.segment.is_type("quoted_literal"):
            return None

        if not (
            self.force_enable
            or context.dialect.name in self._dialects_with_double_quoted_strings
        ):
            return LintResult(memory=context.memory)

        # This rule can also cover quoted literals that are partially templated.
        # I.e. when the quotes characters are _not_ part of the template we can
        # meaningfully apply this rule.
        templated_raw_slices = FunctionalContext(context).segment.raw_slices.select(
            rsp.is_slice_type("templated")
        )
        for raw_slice in templated_raw_slices:
            pos_marker = context.segment.pos_marker
            # This is to make mypy happy.
            assert isinstance(pos_marker, PositionMarker)

            # Check whether the quote characters are inside the template.
            # For the leading quote we need to account for string prefix characters.
            leading_quote_inside_template = pos_marker.source_str()[:2].lstrip(
                self._string_prefix_chars
            )[0] not in ['"', "'"]
            trailing_quote_inside_template = pos_marker.source_str()[-1] not in [
                '"',
                "'",
            ]

            # quotes are not entirely outside of a template, nothing we can do
            if leading_quote_inside_template or trailing_quote_inside_template:
                return LintResult(memory=context.memory)

        # If quoting style is set to consistent we use the quoting style of the first
        # quoted_literal that we encounter.
        if self.preferred_quoted_literal_style == "consistent":
            memory = context.memory
            preferred_quoted_literal_style = memory.get(
                "preferred_quoted_literal_style"
            )

            if not preferred_quoted_literal_style:
                # Getting the quote from LAST character to be able to handle STRING
                # prefixes
                preferred_quoted_literal_style = (
                    "double_quotes"
                    if context.segment.raw[-1] == '"'
                    else "single_quotes"
                )
                memory["preferred_quoted_literal_style"] = (
                    preferred_quoted_literal_style
                )
                self.logger.debug(
                    "Preferred string quotes is set to `consistent`. Derived quoting "
                    "style %s from first quoted literal.",
                    preferred_quoted_literal_style,
                )
        else:
            preferred_quoted_literal_style = self.preferred_quoted_literal_style

        fixed_string = self._normalize_preferred_quoted_literal_style(
            context.segment.raw,
            preferred_quote_char=self._quotes_mapping[preferred_quoted_literal_style][
                "preferred_quote_char"
            ],
            alternate_quote_char=self._quotes_mapping[preferred_quoted_literal_style][
                "alternate_quote_char"
            ],
        )

        if fixed_string != context.segment.raw:
            # We can't just set the primary type, but we have to ensure that the
            # subtypes are properly set too so that the re-parse checks pass.
            if fixed_string[0] == "'":
                _instance_types = ("quoted_literal", "single_quote")
            else:
                _instance_types = ("quoted_literal", "double_quote")
            return LintResult(
                anchor=context.segment,
                memory=context.memory,
                fixes=[
                    LintFix.replace(
                        context.segment,
                        [
                            LiteralSegment(
                                raw=fixed_string,
                                instance_types=_instance_types,
                            )
                        ],
                    )
                ],
                description=(
                    "Inconsistent use of preferred quote style '"
                    f"{self._quotes_mapping[preferred_quoted_literal_style]['common_name']}"  # noqa: E501
                    f"'. Use {fixed_string} instead of {context.segment.raw}."
                ),
            )

        return None

    # Code for preferred quoted_literal style was copied from Black string normalization
    # and adapted to our use-case.
    def _regex_sub_with_overlap(
        self, regex: regex.Pattern, replacement: str, original: str
    ) -> str:
        """Replace `regex` with `replacement` twice on `original`.

        This is used by string normalization to perform replaces on overlapping matches.

        Source:
        https://github.com/psf/black/blob/7f7673d941a947a8d392c8c0866d3d588affc174/src/black/strings.py#L23-L29
        """
        return regex.sub(replacement, regex.sub(replacement, original))

    def _normalize_preferred_quoted_literal_style(
        self, s: str, preferred_quote_char: str, alternate_quote_char: str
    ) -> str:
        """Prefer `preferred_quote_char` but only if it doesn't cause more escaping.

        Adds or removes backslashes as appropriate.

        Source:
        https://github.com/psf/black/blob/7f7673d941a947a8d392c8c0866d3d588affc174/src/black/strings.py#L167
        """
        value = s.lstrip(self._string_prefix_chars)

        if value[:3] == preferred_quote_char * 3:
            # In triple-quoted strings we are not replacing escaped quotes.
            # So nothing left to do and we can exit.
            return s
        elif value[0] == preferred_quote_char:
            # Quotes are alright already. But maybe we can remove some unnecessary
            # escapes or reduce the number of escapes using alternate_quote_char ?
            orig_quote = preferred_quote_char
            new_quote = alternate_quote_char
        elif value[:3] == alternate_quote_char * 3:
            orig_quote = alternate_quote_char * 3
            new_quote = preferred_quote_char * 3
        elif value[0] == alternate_quote_char:
            orig_quote = alternate_quote_char
            new_quote = preferred_quote_char
        else:
            self.logger.debug(
                "Found quoted string %s using neither preferred quote char %s "
                "nor alternate_quote_char %s. Skipping...",
                s,
                preferred_quote_char,
                alternate_quote_char,
            )
            return s

        first_quote_pos = s.find(orig_quote)
        prefix = s[:first_quote_pos]
        unescaped_new_quote = regex.compile(rf"(([^\\]|^)(\\\\)*){new_quote}")
        escaped_new_quote = regex.compile(rf"([^\\]|^)\\((?:\\\\)*){new_quote}")
        escaped_orig_quote = regex.compile(rf"([^\\]|^)\\((?:\\\\)*){orig_quote}")
        body = s[first_quote_pos + len(orig_quote) : -len(orig_quote)]

        if "r" in prefix.lower():
            if unescaped_new_quote.search(body):
                self.logger.debug(
                    "There's at least one unescaped new_quote in this raw string "
                    "so converting is impossible."
                )
                return s

            # Do not modify the body of raw strings by introducing or removing
            # backslashes as this changes the value of the raw string.
            new_body = body
        else:
            # remove unnecessary escapes
            new_body = self._regex_sub_with_overlap(
                escaped_new_quote, rf"\1\2{new_quote}", body
            )
            if body != new_body:
                # Consider the string without unnecessary escapes as the original
                self.logger.debug("Removing unnecessary escapes in %s.", body)
                body = new_body
                s = f"{prefix}{orig_quote}{body}{orig_quote}"
            new_body = self._regex_sub_with_overlap(
                escaped_orig_quote, rf"\1\2{orig_quote}", new_body
            )
            new_body = self._regex_sub_with_overlap(
                unescaped_new_quote, rf"\1\\{new_quote}", new_body
            )

        if (
            new_quote == 3 * preferred_quote_char
            and new_body[-1:] == preferred_quote_char
        ):
            # edge case: for example when converting quotes from '''a"'''
            # to """a\"""" the last " of the string body needs to be escaped.
            new_body = new_body[:-1] + f"\\{preferred_quote_char}"

        orig_escape_count = body.count("\\")
        new_escape_count = new_body.count("\\")
        if new_escape_count > orig_escape_count:
            self.logger.debug(
                "Changing quote style would introduce more escapes in the body. "
                "Before: %s After: %s . Skipping.",
                body,
                new_body,
            )
            return s  # Do not introduce more escaping

        if new_escape_count == orig_escape_count and orig_quote == preferred_quote_char:
            # Already using preferred_quote_char, and no escape benefit to changing
            return s

        return f"{prefix}{new_quote}{new_body}{new_quote}"
