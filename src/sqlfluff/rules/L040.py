"""Implementation of Rule L040."""

from typing import Tuple, List
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
class Rule_L040(Rule_L010):
    """Inconsistent capitalisation of boolean/null literal.

    **Anti-pattern**

    In this example, ``null`` and ``false`` are in lower-case whereas ``TRUE`` is in
    upper-case.

    .. code-block:: sql

        select
            a,
            null,
            TRUE,
            false
        from foo

    **Best practice**

    Ensure all literal ``null``/``true``/``false`` literals are consistently
    upper or lower case

    .. code-block:: sql

        select
            a,
            NULL,
            TRUE,
            FALSE
        from foo

        -- Also good

        select
            a,
            null,
            true,
            false
        from foo

    """

    groups = ("all", "core")
    lint_phase = "post"
    crawl_behaviour = SegmentSeekerCrawler({"null_literal", "boolean_literal"})
    _exclude_elements: List[Tuple[str, str]] = []
    _description_elem = "Boolean/null literals"
