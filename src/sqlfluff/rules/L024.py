"""Implementation of Rule L024."""


from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.core.rules.doc_decorators import document_fix_compatible, document_groups
from sqlfluff.rules.L023 import Rule_L023


@document_groups
@document_fix_compatible
class Rule_L024(Rule_L023):
    """Single whitespace expected after ``USING`` in ``JOIN`` clause.

    **Anti-pattern**

    .. code-block:: sql

        SELECT b
        FROM foo
        LEFT JOIN zoo USING(a)

    **Best practice**

    Add a space after ``USING``, to avoid confusing it
    for a function.

    .. code-block:: sql
       :force:

        SELECT b
        FROM foo
        LEFT JOIN zoo USING (a)
    """

    groups = ("all", "core")
    crawl_behaviour = SegmentSeekerCrawler({"join_clause"})
    target_keyword = "USING"
    strip_newlines = False
