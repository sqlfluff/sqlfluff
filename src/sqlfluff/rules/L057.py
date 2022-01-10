"""Implementation of Rule L057."""

from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
)
from sqlfluff.rules.L014 import identifiers_policy_applicable


@document_configuration
class Rule_L057(BaseRule):
    """Do not use special characters in identifiers.

    | **Anti-pattern**
    | Using special characters within identifiers when creating or aliasing objects.

    .. code-block:: sql

        CREATE TABLE DBO.ColumnNames
        (
            [Internal Space] INT,
            [Greater>Than] INT,
            [Less<Than] INT,
            Number# INT
        )

    | **Best practice**
    | Identifiers should include only alphanumerics and underscores.

    .. code-block:: sql

        CREATE TABLE DBO.ColumnNames
        (
            [Internal_Space] INT,
            [GreaterThan] INT,
            [LessThan] INT,
            NumberVal INT
        )

    """

    config_keywords = [
        "quoted_identifiers_policy",
        "unquoted_identifiers_policy",
        "allow_space_in_identifier",
        "additional_allowed_identifiers",
    ]

    @staticmethod
    def _standard_cleanups(
        identifier: str,
        allow_space_in_identifier: bool,
        additional_allowed_identifiers: str,
    ) -> str:

        # We always allow underscores so strip them out
        identifier = identifier.replace("_", "")

        # Set the identified minus the allowed characters
        if additional_allowed_identifiers:
            identifier = identifier.translate(
                str.maketrans("", "", additional_allowed_identifiers)
            )

        # Strip spaces if allowed (note a separate config as only valid for quoted identifiers)
        if allow_space_in_identifier:
            identifier = identifier.replace(" ", "")

        return identifier

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Do not use special characters in object names."""
        # Config type hints
        self.quoted_identifiers_policy: str
        self.unquoted_identifiers_policy: str
        self.allow_space_in_identifier: bool
        self.additional_allowed_identifiers: str

        # Exit early if not a single identifier.
        if context.segment.name not in ("naked_identifier", "quoted_identifier"):
            return None

        identifier = context.segment.raw

        if context.segment.name == "naked_identifier":

            identifier = self._standard_cleanups(
                identifier, False, self.additional_allowed_identifiers
            )

            # Evaluate unquoted identifiers.
            if identifiers_policy_applicable(
                self.unquoted_identifiers_policy, context.parent_stack
            ) and not (identifier.isalnum()):
                return LintResult(anchor=context.segment)
        else:
            # Evaluate quoted identifiers.

            # Strip the quotes first
            identifier = context.segment.raw[1:-1]

            # Then strip the standard stuff
            identifier = self._standard_cleanups(
                identifier,
                self.allow_space_in_identifier,
                self.additional_allowed_identifiers,
            )

            # BigQuery table references are quoted in back ticks so allow dots
            #
            # It also allows a star at the end of table_references for wildcards
            # (https://cloud.google.com/bigquery/docs/querying-wildcard-tables)
            #
            # Strip both out before testing the identifier
            if (
                context.dialect.name in ["bigquery"]
                and context.parent_stack
                and context.parent_stack[-1].name == "TableReferenceSegment"
            ):
                if identifier[-1] == "*":
                    identifier = identifier[:-1]
                identifier = identifier.replace(".", "")

            if identifiers_policy_applicable(
                self.quoted_identifiers_policy, context.parent_stack
            ) and not (identifier.isalnum()):
                return LintResult(anchor=context.segment)

        return None
