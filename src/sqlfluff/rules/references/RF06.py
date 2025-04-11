"""Implementation of Rule RF06."""

from functools import cached_property
from typing import TYPE_CHECKING, Optional, cast

import regex

from sqlfluff.core.parser import CodeSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.utils.functional import FunctionalContext, sp

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.parsers import RegexParser


class Rule_RF06(BaseRule):
    """Unnecessary quoted identifier.

    This rule will fail if the quotes used to quote an identifier are (un)necessary
    depending on the ``force_quote_identifier`` configuration. This rule applies to
    both column *references* and their *aliases*. The *default* (safe) behaviour is
    designed not to unexpectedly corrupt SQL. That means the circumstances in which
    quotes can be safely removed depends on the current dialect would resolve the
    unquoted variant of the identifier (see below for examples).

    Additionally this rule may be configured to a more aggressive setting by setting
    :code:`case_sensitive` to :code:`False`, in which case quotes will be removed
    regardless of the casing of the contained identifier. Any identifiers which contain
    special characters, spaces or keywords will still be left quoted. This setting is
    more appropriate for projects or teams where there is more control over the inputs
    and outputs of queries, and where it's more viable to institute rules such
    as enforcing that all identifiers are the default casing (and therefore meaning
    that using quotes to change the case of identifiers is unnecessary).

    .. list-table::
       :widths: 26 26 48
       :header-rows: 1

       * - Dialect group
         - ✅ Example where quotes are safe to remove.
         - ⚠️ Examples where quotes are not safe to remove.
       * - Natively :code:`UPPERCASE` dialects e.g. Snowflake, BigQuery,
           TSQL & Oracle.
         - Identifiers which, without quotes, would resolve to the default
           casing of :code:`FOO` i.e. :code:`"FOO"`.
         - Identifiers where the quotes are necessary to preserve case
           (e.g. :code:`"Foo"` or :code:`"foo"`), or where the identifier
           contains something invalid without the quotes such as keywords
           or special characters e.g. :code:`"SELECT"`, :code:`"With Space"`
           or :code:`"Special&Characters"`.
       * - Natively :code:`lowercase` dialects e.g. Athena,
           Hive & Postgres
         - Identifiers which, without quotes, would resolve to the default
           casing of :code:`foo` i.e. :code:`"foo"`.
         - Identifiers where the quotes are necessary to preserve case
           (e.g. :code:`"Foo"` or :code:`"foo"`), or where the identifier
           contains something invalid without the quotes such as keywords
           or special characters e.g. :code:`"SELECT"`, :code:`"With Space"`
           or :code:`"Special&Characters"`.
       * - Case insensitive dialects e.g. :ref:`duckdb_dialect_ref` or
           :ref:`sparksql_dialect_ref`
         - Any identifiers which are valid without quotes: e.g. :code:`"FOO"`,
           :code:`"foo"`, :code:`"Foo"`, :code:`"fOo"`, :code:`FOO` and
           :code:`foo` would all resolve to the same object.
         - Identifiers which contain something invalid without the quotes
           such as keywords or special characters e.g. :code:`"SELECT"`,
           :code:`"With Space"` or :code:`"Special&Characters"`.

    This rule is closely associated with (and constrained by the same above
    factors) as :sqlfluff:ref:`aliasing.self_alias.column` (:sqlfluff:ref:`AL09`).

    When ``prefer_quoted_identifiers = False`` (default behaviour), the quotes are
    unnecessary, except for reserved keywords and special characters in identifiers.

    **Anti-pattern**

    In this example, valid unquoted identifiers,
    that are not also reserved keywords, are needlessly quoted.

    .. code-block:: sql

        SELECT "foo" as "bar";  -- For lowercase dialects like Postgres
        SELECT "FOO" as "BAR";  -- For uppercase dialects like Snowflake

    **Best practice**

    Use unquoted identifiers where possible.

    .. code-block:: sql

        SELECT foo as bar;  -- For lowercase dialects like Postgres
        SELECT FOO as BAR;  -- For uppercase dialects like Snowflake

        -- Note that where the case of the quoted identifier requires
        -- the quotes to remain, or where the identifier cannot be
        -- unquoted because it would be invalid to do so, the quotes
        -- may remain. For example:
        SELECT
            "Case_Sensitive_Identifier" as is_allowed,
            "Identifier with spaces or speci@l characters" as this_too,
            "SELECT" as also_reserved_words
        FROM "My Table With Spaces"

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

    name = "references.quoting"
    aliases = ("L059",)
    groups = ("all", "references")
    config_keywords = [
        "prefer_quoted_identifiers",
        "prefer_quoted_keywords",
        "ignore_words",
        "ignore_words_regex",
        "case_sensitive",
    ]
    crawl_behaviour = SegmentSeekerCrawler({"quoted_identifier", "naked_identifier"})
    is_fix_compatible = True

    # Ignore "password_auth" type to allow quotes around passwords within
    # `CREATE USER` statements in Exasol dialect.
    # `EXECUTE AS` clauses in TSQL also require quotes.
    _ignore_types: list[str] = ["password_auth", "execute_as_clause"]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Unnecessary quoted identifier."""
        # Config type hints
        self.prefer_quoted_identifiers: bool
        self.prefer_quoted_keywords: bool
        self.ignore_words: str
        self.ignore_words_regex: str
        self.case_sensitive: bool

        # Ignore some segment types
        if FunctionalContext(context).parent_stack.any(sp.is_type(*self._ignore_types)):
            return None

        identifier_is_quoted = not regex.search(
            r'^[^"\'[].+[^"\'\]]$', context.segment.raw
        )

        identifier_contents = context.segment.raw
        if identifier_is_quoted:
            identifier_contents = identifier_contents[1:-1]

        identifier_is_keyword = identifier_contents.upper() in context.dialect.sets(
            "reserved_keywords"
        ) or identifier_contents.upper() in context.dialect.sets("unreserved_keywords")

        if self.prefer_quoted_identifiers:
            context_policy = "naked_identifier"
        else:
            context_policy = "quoted_identifier"

        # Get the ignore_words_list configuration.
        ignore_words_list = self.ignore_words_list

        # Skip if in ignore list
        if ignore_words_list and identifier_contents.lower() in ignore_words_list:
            return None

        # Skip if matches ignore regex
        if self.ignore_words_regex and regex.search(
            self.ignore_words_regex, identifier_contents
        ):
            return LintResult(memory=context.memory)

        if self.prefer_quoted_keywords and identifier_is_keyword:
            if not identifier_is_quoted:
                return LintResult(
                    context.segment,
                    description=(
                        f"Missing quoted keyword identifier {identifier_contents}."
                    ),
                )
            return None

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

        # Retrieve NakedIdentifierSegment RegexParser for the dialect.
        naked_identifier_parser = cast(
            "RegexParser", context.dialect._library["NakedIdentifierSegment"]
        )
        anti_template = cast(str, naked_identifier_parser.anti_template)
        NakedIdentifierSegment = cast(
            type[CodeSegment], context.dialect.get_segment("IdentifierSegment")
        )

        # For this to be a candidate for unquoting, it must:
        # - Casefold to it's current exact case. i.e. already be in the default
        #   casing of the dialect *unless case_sensitive mode is False*.
        # - be a valid naked identifier.
        # - not be a reserved keyword.
        # NOTE: If the identifier parser has no casefold defined, we assume that
        # there is no casefolding (i.e. that the dialect is case sensitive, and
        # even when unquoted, and therefore we should never unquote).
        # EXCEPT: if we're in a totally case insensitive dialect like DuckDB.
        is_case_insensitive_dialect = context.dialect.name in ("duckdb", "sparksql")
        if (
            not is_case_insensitive_dialect
            and self.case_sensitive
            and naked_identifier_parser.casefold
            and identifier_contents
            != naked_identifier_parser.casefold(identifier_contents)
        ):
            return None
        if not regex.fullmatch(
            naked_identifier_parser.template,
            identifier_contents,
            regex.IGNORECASE,
        ):
            return None
        if regex.fullmatch(
            anti_template,
            identifier_contents,
            regex.IGNORECASE,
        ):
            return None

        return LintResult(
            context.segment,
            fixes=[
                LintFix.replace(
                    context.segment,
                    [
                        NakedIdentifierSegment(
                            raw=identifier_contents,
                            **naked_identifier_parser.segment_kwargs(),
                        )
                    ],
                )
            ],
            description=f"Unnecessary quoted identifier {context.segment.raw}.",
        )

    @cached_property
    def ignore_words_list(self) -> list[str]:
        """Words that the rule should ignore.

        Cached so that it's only evaluated on the first pass.
        """
        ignore_words_config: str = str(getattr(self, "ignore_words"))
        if ignore_words_config and ignore_words_config != "None":
            return self.split_comma_separated_string(ignore_words_config.lower())
        return []
