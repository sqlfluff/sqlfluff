"""Implementation of Rule L024."""


from sqlfluff.core.rules.doc_decorators import document_fix_compatible
from sqlfluff.rules.L023 import Rule_L023


@document_fix_compatible
class Rule_L024(Rule_L023):
    """Single whitespace expected after USING in JOIN clause.

    | **Anti-pattern**

    .. code-block:: sql

        SELECT b
        FROM foo
        LEFT JOIN zoo USING(a)

    | **Best practice**
    | The • character represents a space.
    | Add a space after USING, to avoid confusing it
    | for a function.

    .. code-block:: sql

        SELECT b
        FROM foo
        LEFT JOIN zoo USING•(a)

    """

    expected_mother_segment_type = "join_clause"
    pre_segment_identifier = ("name", "using")
    post_segment_identifier = ("type", "bracketed")
    expand_children = None
    allow_newline = True
