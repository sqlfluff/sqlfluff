"""Implementation of Rule L072."""
from typing import Optional, Tuple

from sqlfluff.core.parser import KeywordSegment
from sqlfluff.core.rules import BaseRule, LintResult, LintFix, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups


@document_groups
@document_fix_compatible
class Rule_L072(BaseRule):
    """Use ``CREATE/ALTER/DROP DATABASE`` instead of using ``CREATE/ALTER/DROP SCHEMA``.

    They are equivalent in MySQL, Hive and SparkSQL.
    **Anti-pattern**

    .. code-block:: sql

        CREATE SCHEMA database_name

    **Best practice**

    .. code-block:: sql

        CREATE DATABASE database_name
    """

    groups: Tuple[str, ...] = ("all",)
    crawl_behaviour = SegmentSeekerCrawler(
        {
            "create_database_statement",
            "alter_database_statement",
            "drop_schema_statement",
        }
    )

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Prefer using ``DATABASE`` instead of using ``SCHEMA``."""
        if context.dialect.name not in [
            "mysql",
            "hive",
            "sparksql",
        ]:
            return None

        if context.segment.get_children("keyword")[1].raw_upper != "SCHEMA":
            return None

        statement_type = context.segment.get_child("keyword").raw_upper
        return LintResult(
            anchor=context.segment,
            fixes=[
                LintFix.replace(
                    context.segment.get_children("keyword")[1],
                    [KeywordSegment(raw="DATABASE")],
                )
            ],
            description=f"Use '{statement_type} DATABASE' instead of "
            f"'{statement_type} SCHEMA'.",
        )
