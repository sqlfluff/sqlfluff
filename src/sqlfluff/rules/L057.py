"""Implementation of Rule L057."""

from typing import Tuple, List, Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
)
from sqlfluff.rules.L014 import identifiers_policy_applicable


@document_configuration
@document_fix_compatible
class Rule_L057(BaseRule):
    """Do not use special characters in object names.

    The functionality for this rule is inherited from :obj:`Rule_L010`.

    | **Anti-pattern**
    | Using special characters within names when creating or aliasing objects.

    .. code-block:: sql

        CREATE TABLE DBO.ColumnNames
        (
            [TrailingSpace ] INT,
            [Greater>Than] INT,
            [Less<Than] INT,
            Number# INT
        )

    | **Best practice**
    | Remove special characters from object and alias names.

    .. code-block:: sql

        CREATE TABLE DBO.ColumnNames
        (
            [TrailingSpace] INT,
            [GreaterThan] INT,
            [LessThan] INT,
            NumberVal INT
        )

    """

    config_keywords = [
        "quoted_identifiers_policy",
        "unquoted_identifiers_policy",
        "allow_space_in_identifier",
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Do not use special characters in object names."""
        if (
            (
                context.segment.name == "naked_identifier"
                and identifiers_policy_applicable(
                    self.unquoted_identifiers_policy, context.parent_stack  # type: ignore
                )
                and not (
                    context.segment.raw.isalnum()
                    or (
                        self.allow_space_in_identifier
                        and context.segment.raw.replace(" ", "").isalnum()
                    )
                )
            )
        ) or (
            (
                context.segment.name == "quoted_identifier"
                and identifiers_policy_applicable(
                    self.quoted_identifiers_policy, context.parent_stack  # type: ignore
                )
                and not (
                    context.segment.raw[1:-1].isalnum()
                    or (
                        self.allow_space_in_identifier
                        and context.segment.raw[1:-1].replace(" ", "").isalnum()
                    )
                )
            )
        ):
            return LintResult(anchor=context.segment)
        else:
            return None
