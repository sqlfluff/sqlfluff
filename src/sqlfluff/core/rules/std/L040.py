"""Implementation of Rule L040."""

from typing import Tuple, List

from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.core.rules.std.L010 import Rule_L010


@document_configuration
@document_fix_compatible
class Rule_L040(Rule_L010):
    """Inconsistent capitalisation of boolean/null literal.

    The functionality for this rule is inherited from :obj:`Rule_L010`.
    """

    _target_elems: List[Tuple[str, str]] = [
        ("name", "null_literal"),
        ("name", "boolean_literal"),
    ]
