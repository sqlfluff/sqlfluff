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

    **Anti-pattern**

    Using special characters within identifiers when creating or aliasing objects.

    .. code-block:: sql

        CREATE TABLE DBO.ColumnNames
        (
            [Internal Space] INT,
            [Greater>Than] INT,
            [Less<Than] INT,
            Number# INT
        )

    **Best practice**

    Identifiers should include only alphanumerics and underscores.

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
        "additional_allowed_characters",
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        """Do not use special characters in object names."""
        # Config type hints
        self.quoted_identifiers_policy: str
        self.unquoted_identifiers_policy: str
        self.allow_space_in_identifier: bool
        self.additional_allowed_characters: str

        # Exit early if not a single identifier.
        if context.segment.name not in ("naked_identifier", "quoted_identifier"):
            return None

        # Assume unquoted (we'll update if quoted)
        policy = self.unquoted_identifiers_policy

        identifier = context.segment.raw

        # Do some extra processing for quoted identifiers.
        if context.segment.name == "quoted_identifier":

            # Update the default policy to quoted
            policy = self.quoted_identifiers_policy

            # Strip the quotes first
            identifier = context.segment.raw[1:-1]

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

            # Spark3 file references for direct file query
            # are quoted in back ticks to allow for identfiers common
            # in file paths and regex patterns for path globbing
            # https://spark.apache.org/docs/latest/sql-ref-syntax-qry-select-file.html
            #
            # Path Glob Filters (done inline for SQL direct file query)
            # https://spark.apache.org/docs/latest/sql-data-sources-generic-options.html#path-global-filter
            #

            if (
                context.dialect.name in ["spark3"]
                and context.parent_stack
                and context.parent_stack[-1].name == "FileReferenceSegment"
            ):
                return None

            # Strip spaces if allowed (note a separate config as only valid for quoted
            # identifiers)
            if self.allow_space_in_identifier:
                identifier = identifier.replace(" ", "")

        # We always allow underscores so strip them out
        identifier = identifier.replace("_", "")

        # Set the identified minus the allowed characters
        if self.additional_allowed_characters:
            identifier = identifier.translate(
                str.maketrans("", "", self.additional_allowed_characters)
            )

        # Finally test if the remaining identifier is only made up of alphanumerics
        if identifiers_policy_applicable(policy, context.parent_stack) and not (
            identifier.isalnum()
        ):
            return LintResult(anchor=context.segment)

        return None
