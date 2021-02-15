"""Implementation of Rule L030."""

from typing import List, Tuple

from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.core.rules.std.L010 import Rule_L010


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

    _target_elems: List[Tuple[str, str]] = [("name", "function_name")]
