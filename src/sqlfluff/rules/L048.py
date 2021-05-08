"""Implementation of Rule L048."""

from typing import Tuple, List

from sqlfluff.core.rules.doc_decorators import document_fix_compatible

from sqlfluff.rules.L006 import Rule_L006


@document_fix_compatible
class Rule_L048(Rule_L006):
    """Quoted literals should be surrounded by a single whitespace.

    | **Anti-pattern**
    | In this example, there is a space missing space between the string 'foo'
    | and the keyword AS.

    .. code-block:: sql

        SELECT
            'foo'AS bar
        FROM foo


    | **Best practice**
    | Keep a single space.

    .. code-block:: sql

        SELECT
            'foo' AS bar
        FROM foo
    """

    _target_elems: List[Tuple[str, str]] = [
        ("name", "quoted_literal"),
    ]

    @staticmethod
    def _missing_whitespace(seg, before=True):
        """Check whether we're missing whitespace given an adjoining segment.

        This avoids flagging for commas after quoted strings.
        https://github.com/sqlfluff/sqlfluff/issues/943
        """
        simple_res = Rule_L006._missing_whitespace(seg, before=before)
        if not before and seg and seg.is_type("comma"):
            return False
        return simple_res
