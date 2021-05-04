"""Implementation of Rule L030."""

from typing import List, Tuple

from sqlfluff.core.rules.base import LintFix
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.rules.L010 import Rule_L010


@document_configuration
@document_fix_compatible
class Rule_L030(Rule_L010):
    """Inconsistent capitalisation of function names.

    The functionality for this rule is inherited from :obj:`Rule_L010`.

    | **Anti-pattern**
    | In this example, the two SUM functions don't have the same capitalisation.

    .. code-block:: sql

        SELECT
            sum(a) AS aa,
            SUM(b) AS bb
        FROM foo

    | **Best practice**
    |  Make the case consistent.

    .. code-block:: sql

        SELECT
            sum(a) AS aa,
            sum(b) AS bb
        FROM foo

    """

    _target_elems: List[Tuple[str, str]] = [("type", "function_name")]

    def _get_fix(self, segment, fixed_raw):
        """Overrides the base class.

        We need to do this because function_name nodes have a child
        function_name_identifier that holds the actual name.
        """
        child_segment = segment.segments[0]
        return LintFix(
            "edit",
            child_segment,
            child_segment.__class__(raw=fixed_raw, pos_marker=child_segment.pos_marker),
        )
