"""Implementation of Rule L059."""

from typing import List, Tuple

from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.rules.L010 import Rule_L010


@document_configuration
@document_fix_compatible
class Rule_L059(Rule_L010):
    """Inconsistent capitalisation of data types.

    The functionality for this rule is inherited from :obj:`Rule_L010`.

    | **Anti-pattern**
    | In this example, the two data types don't have the same capitalisation.

    .. code-block:: sql

        CREATE TABLE table1 (
            account_id bigint
            , account_compound_id VARCHAR(255)
        );

    | **Best practice**
    |  Make the case consistent.

    .. code-block:: sql

        CREATE TABLE table1 (
            account_id BIGINT
            , account_compound_id VARCHAR(255)
        );

    """

    _target_elems: List[Tuple[str, str]] = [
        ("type", "data_type_identifier"),
    ]
    _description_elem = "Data types"

    def _get_fix(self, segment, fixed_raw):
        return super()._get_fix(segment, fixed_raw)
