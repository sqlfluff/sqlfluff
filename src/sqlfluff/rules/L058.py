"""Implementation of Rule L030."""

from typing import List, Tuple

from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.rules.L010 import Rule_L010


@document_configuration
@document_fix_compatible
class Rule_L058(Rule_L010):
    """Inconsistent capitalisation of data types.

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

    _target_elems: List[Tuple[str, str]] = [
        ("type", "data_type_identifier"),
    ]
    _description_elem = "Data types"

    def _get_fix(self, segment, fixed_raw):
        return super()._get_fix(segment, fixed_raw)
