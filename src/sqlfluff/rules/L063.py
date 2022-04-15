"""Implementation of Rule L063."""

from typing import Tuple, List

from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.rules.L010 import Rule_L010


@document_configuration
@document_fix_compatible
class Rule_L063(Rule_L010):
    """Inconsistent capitalisation of datatypes.

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

    lint_phase = "post"
    _target_elems: List[Tuple[str, str]] = [
        ("parenttype", "data_type"),
        ("parenttype", "datetime_type_identifier"),
        ("parenttype", "primitive_type"),
        ("type", "data_type_identifier"),
    ]
    _exclude_elements: List[Tuple[str, str]] = []
    config_keywords = [
        "extended_capitalisation_policy",
        "ignore_words",
        "ignore_words_regex",
    ]
    _description_elem = "Datatypes"
