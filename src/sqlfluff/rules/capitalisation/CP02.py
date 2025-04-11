"""Implementation of Rule CP02."""

from typing import Optional

from sqlfluff.core.rules import LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.rules.capitalisation.CP01 import Rule_CP01
from sqlfluff.utils.identifers import identifiers_policy_applicable


class Rule_CP02(Rule_CP01):
    """Inconsistent capitalisation of unquoted identifiers.

    This rule applies to all unquoted identifiers, whether references
    or aliases, and whether they refer to columns or other objects (such
    as tables or schemas).

    .. note::

       In **most** dialects, unquoted identifiers are treated as case-insensitive
       and so the fixes proposed by this rule do not change the interpretation
       of the query. **HOWEVER**, some databases (notably :ref:`bigquery_dialect_ref`,
       :ref:`trino_dialect_ref` and :ref:`clickhouse_dialect_ref`) do take the casing
       of *unquoted* identifiers into account when determining the casing of the column
       heading in the *result*.

       As this feature is only present in a few dialects, and not widely understood
       by users, we regard it as *an antipattern*. It is more widely understood that
       if the case of an identifier *matters*, then it should be quoted. If you, or
       your organisation, do wish to rely on this feature, we recommend that you
       disabled this rule (see :ref:`ruleselection`).

    **Anti-pattern**

    In this example, unquoted identifier ``a`` is in lower-case but
    ``B`` is in upper-case.

    .. code-block:: sql

        select
            a,
            B
        from foo

    In this more complicated example, there are a mix of capitalisations
    in both reference and aliases of columns and tables. That inconsistency
    is acceptable when those identifiers are quoted, but not when unquoted.

    .. code-block:: sql

        select
            col_1 + Col_2 as COL_3,
            "COL_4" as Col_5
        from Foo as BAR

    **Best practice**

    Ensure all unquoted identifiers are either in upper-case or in lower-case.

    .. code-block:: sql

        select
            a,
            b
        from foo;

        -- ...also good...

        select
            A,
            B
        from foo;

        --- ...or for comparison with our more complex example, this too:

        select
            col_1 + col_2 as col_3,
            "COL_4" as col_5
        from foo as bar

    """

    name = "capitalisation.identifiers"
    aliases = ("L014",)
    is_fix_compatible = True

    crawl_behaviour = SegmentSeekerCrawler(
        {"naked_identifier", "properties_naked_identifier"}
    )
    config_keywords = [
        "extended_capitalisation_policy",
        "unquoted_identifiers_policy",
        "ignore_words",
        "ignore_words_regex",
    ]
    _description_elem = "Unquoted identifiers"

    def _eval(self, context: RuleContext) -> Optional[list[LintResult]]:
        # Return None if identifier is case-sensitive property to enable Change
        # Data Feed
        # https://docs.delta.io/2.0.0/delta-change-data-feed.html#enable-change-data-feed
        if (
            context.dialect.name in ["databricks", "sparksql"]
            and context.parent_stack
            and context.parent_stack[-1].type == "property_name_identifier"
            and context.segment.raw == "enableChangeDataFeed"
        ):
            return None

        if identifiers_policy_applicable(
            self.unquoted_identifiers_policy,  # type: ignore
            context.parent_stack,
        ):
            return super()._eval(context=context)
        else:
            return [LintResult(memory=context.memory)]
