"""Implementation of Rule CP03."""

from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.rules import LintFix
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.rules.capitalisation.CP01 import Rule_CP01


class Rule_CP03(Rule_CP01):
    """Inconsistent capitalisation of function names.

    **Anti-pattern**

    In this example, the two ``SUM`` functions don't have the same capitalisation.

    .. code-block:: sql

        SELECT
            sum(a) AS aa,
            SUM(b) AS bb
        FROM foo

    **Best practice**

    Make the case consistent.

    .. code-block:: sql

        SELECT
            sum(a) AS aa,
            sum(b) AS bb
        FROM foo

    """

    name = "capitalisation.functions"
    aliases = ("L030",)
    is_fix_compatible = True

    crawl_behaviour = SegmentSeekerCrawler(
        {"function_name_identifier", "bare_function"}
    )
    _exclude_types = ()
    _exclude_parent_types = ()

    config_keywords = [
        "extended_capitalisation_policy",
        "ignore_words",
        "ignore_words_regex",
    ]
    _description_elem = "Function names"

    def _get_fix(self, segment: BaseSegment, fixed_raw: str) -> LintFix:
        return super()._get_fix(segment, fixed_raw)
