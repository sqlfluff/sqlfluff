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

    _target_elems: List[Tuple[str, str]] = [
        ("name", "null_literal"),
        ("name", "boolean_literal"),
    ]
    _description_elem = "Boolean/null literals"
