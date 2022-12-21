"""Implementation of Rule L030."""

from typing import List, Tuple
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler

from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.rules.L010 import Rule_L010


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L030(Rule_L010):
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

    groups = ("all", "core")
    lint_phase = "post"
    crawl_behaviour = SegmentSeekerCrawler(
        {"function_name_identifier", "bare_function"}
    )
    _exclude_elements: List[Tuple[str, str]] = []
    config_keywords = [
        "extended_capitalisation_policy",
        "ignore_words",
        "ignore_words_regex",
    ]
    _description_elem = "Function names"

    def _get_fix(self, segment, fixed_raw):
        return super()._get_fix(segment, fixed_raw)
