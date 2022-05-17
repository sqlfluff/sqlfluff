"""Implementation of Rule L063."""

from typing import Tuple, List

from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.rules.L010 import Rule_L010


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L063(Rule_L010):
    """Inconsistent capitalisation of datatypes.

    **Anti-pattern**

    In this example, ``int`` and ``unsigned`` are in lower-case whereas
    ``VARCHAR`` is in upper-case.

    .. code-block:: sql

        CREATE TABLE t (
            a int unsigned,
            b VARCHAR(15)
        );

    **Best practice**

    Ensure all datatypes are consistently upper or lower case

    .. code-block:: sql

        CREATE TABLE t (
            a INT UNSIGNED,
            b VARCHAR(15)
        );

    """

    groups = ("all",)
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
