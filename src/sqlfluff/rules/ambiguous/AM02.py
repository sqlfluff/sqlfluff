"""Implementation of Rule AM02."""

from sqlfluff.core.parser import KeywordSegment, WhitespaceSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_AM02(BaseRule):
    """``UNION [DISTINCT|ALL]`` is preferred over just ``UNION``.

    .. note::
       This rule is only enabled for dialects that support ``UNION`` and
       ``UNION DISTINCT`` (``ansi``, ``bigquery``, ``clickhouse``,
       ``databricks``, ``db2``, ``hive``, ``mysql``, ``redshift``,
       ``snowflake``, and ``trino``).

    **Anti-pattern**

    In this example, ``UNION DISTINCT`` should be preferred over ``UNION``, because
    explicit is better than implicit.

    .. code-block:: sql

        SELECT a, b FROM table_1
        UNION
        SELECT a, b FROM table_2

    **Best practice**

    Specify ``DISTINCT`` or ``ALL`` after ``UNION`` (note that ``DISTINCT`` is the
    default behavior).

    .. code-block:: sql

        SELECT a, b FROM table_1
        UNION DISTINCT
        SELECT a, b FROM table_2

    """

    name = "ambiguous.union"
    aliases = ("L033",)
    groups: tuple[str, ...] = ("all", "core", "ambiguous")
    crawl_behaviour = SegmentSeekerCrawler({"set_operator"})
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> LintResult:
        """Look for UNION keyword not immediately followed by DISTINCT or ALL.

        Note that UNION DISTINCT is valid, rule only applies to bare UNION.
        The function does this by looking for a segment of type set_operator
        which has a UNION but no DISTINCT or ALL.

        Note only some dialects have concept of UNION DISTINCT, so rule is only
        applied to dialects that are known to support this syntax.
        """
        if context.dialect.name not in [
            "ansi",
            "bigquery",
            "clickhouse",
            "databricks",
            "db2",
            "hive",
            "mysql",
            "redshift",
            "snowflake",
            "trino",
        ]:
            return LintResult()

        assert context.segment.is_type("set_operator")
        raw_upper = context.segment.raw.upper()
        if "UNION" not in raw_upper or "ALL" in raw_upper or "DISTINCT" in raw_upper:
            return LintResult()

        # Insert DISTINCT after the existing UNION keyword rather than
        # replacing it. Replacing it with a hardcoded "UNION"/"union" forced
        # any other casing (e.g. "Union") to one of those two, silently
        # fighting a project's chosen capitalisation style - that's CP01's
        # job, not this rule's. Match the case of the new keyword to the
        # existing one so an all-caps UNION still gets an all-caps DISTINCT.
        union_keyword = context.segment.segments[0]
        distinct_kw = "DISTINCT" if union_keyword.raw.isupper() else "distinct"
        return LintResult(
            anchor=context.segment,
            fixes=[
                LintFix.create_after(
                    union_keyword,
                    [WhitespaceSegment(), KeywordSegment(distinct_kw)],
                )
            ],
        )
