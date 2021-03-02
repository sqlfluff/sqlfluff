"""Implementation of Rule L014."""

from typing import Tuple, List

from sqlfluff.core.rules.base import LintResult
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.core.rules.std.L010 import Rule_L010


@document_configuration
@document_fix_compatible
class Rule_L014(Rule_L010):
    """Inconsistent capitalisation of unquoted identifiers.

    The functionality for this rule is inherited from :obj:`Rule_L010`.
    """
    
    _target_elems: List[Tuple[str, str]] = [("name", "naked_identifier")]
    config_keywords = ["extended_capitalisation_policy", "only_aliases"]

    def _eval(self, segment, memory, parent_stack, **kwargs):
        # If self.only_aliases is true, we're a bit pickier here
        if (
                self.only_aliases and (
                    not parent_stack
                    or not parent_stack[-1].is_type(
                        # Skip aliases, column definition, and with statements
                        "alias_expression",
                        "column_definition",
                        "with_compound_statement",
                    )
                )
            ):
            return LintResult(memory=memory)
        else:
            return super()._eval(segment, memory, parent_stack, **kwargs)
