"""Implementation of Rule CP04."""

from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.rules.capitalisation.CP01 import Rule_CP01


class Rule_CP04(Rule_CP01):
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

    name = "capitalisation.literals"
    aliases = ("L040",)
    is_fix_compatible = True

    crawl_behaviour = SegmentSeekerCrawler({"null_literal", "boolean_literal"})
    _exclude_types = ()
    _exclude_parent_types = ()
    _description_elem = "Boolean/null literals"
