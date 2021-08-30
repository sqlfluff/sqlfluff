"""Implementation of Rule L040."""

from typing import Tuple, List

from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.rules.L010 import Rule_L010


@document_configuration
@document_fix_compatible
class Rule_L040(Rule_L010):
    """Inconsistent capitalisation of boolean/null literal.

    The functionality for this rule is inherited from :obj:`Rule_L010`.

    | **Anti-pattern**
    | In this example, 'null' and 'false' is in lower-case whereas 'TURE' is in upper-case.

    .. code-block:: sql

        select
            a,
            null,
            TURE,
            false
        from foo

    | **Best practice**
    | Make all literal null/true/false either in upper-case or in lower-case

    .. code-block:: sql

        select
            a,
            null,
            true,
            false
        from foo

        -- Also good

        select
            a,
            NULL,
            TRUE,
            FALSE
        from foo

    """

    _target_elems: List[Tuple[str, str]] = [
        ("name", "null_literal"),
        ("name", "boolean_literal"),
    ]
