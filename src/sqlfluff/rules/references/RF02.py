"""Implementation of Rule RF02."""

from typing import List, Optional

import regex

from sqlfluff.core.dialects.common import AliasInfo, ColumnAliasInfo
from sqlfluff.core.parser import BaseSegment
from sqlfluff.core.rules import LintResult
from sqlfluff.rules.aliasing.AL04 import Rule_AL04


class Rule_RF02(Rule_AL04):
    """References should be qualified if select has more than one referenced table/view.

    .. note::
       Except if they're present in a ``USING`` clause.

    **Anti-pattern**

    In this example, the reference ``vee`` has not been declared,
    and the variables ``a`` and ``b`` are potentially ambiguous.

    .. code-block:: sql

        SELECT a, b
        FROM foo
        LEFT JOIN vee ON vee.a = foo.a

    **Best practice**

    Add the references.

    .. code-block:: sql

        SELECT foo.a, vee.b
        FROM foo
        LEFT JOIN vee ON vee.a = foo.a
    """

    name = "references.qualification"
    aliases = ("L027",)
    groups = ("all", "references")
    # Crawl behaviour is defined in AL04

    def _lint_references_and_aliases(
        self,
        table_aliases: List[AliasInfo],
        standalone_aliases: List[str],
        references,
        col_aliases: List[ColumnAliasInfo],
        using_cols: List[str],
        parent_select: Optional[BaseSegment],
    ) -> Optional[List[LintResult]]:
        # Config type hints
        self.ignore_words_regex: str

        # Do we have more than one? If so, all references should be qualified.
        if len(table_aliases) <= 1:
            return None

        # Get the ignore_words_list configuration.
        try:
            ignore_words_list = self.ignore_words_list
        except AttributeError:
            # First-time only, read the settings from configuration. This is
            # very slow.
            ignore_words_list = self._init_ignore_words_list()

        # A buffer to keep any violations.
        violation_buff = []
        # Check all the references that we have.
        for r in references:
            # Skip if in ignore list
            if ignore_words_list and r.raw.lower() in ignore_words_list:
                continue

            # Skip if matches ignore regex
            if self.ignore_words_regex and regex.search(self.ignore_words_regex, r.raw):
                continue

            this_ref_type = r.qualification()
            # Discard column aliases that
            # refer to the current column reference.
            col_alias_names = [
                c.alias_identifier_name
                for c in col_aliases
                if r not in c.column_reference_segments
            ]
            if (
                this_ref_type == "unqualified"
                # Allow unqualified columns that
                # are actually aliases defined
                # in a different select clause element.
                and r.raw not in col_alias_names
                # Allow columns defined in a USING expression.
                and r.raw not in using_cols
                # Allow columns defined as standalone aliases
                # (e.g. value table functions from bigquery)
                and r.raw not in standalone_aliases
            ):
                violation_buff.append(
                    LintResult(
                        anchor=r,
                        description=f"Unqualified reference {r.raw!r} found in "
                        "select with more than one referenced table/view.",
                    )
                )

        return violation_buff or None

    def _init_ignore_words_list(self) -> List[str]:
        """Called first time rule is evaluated to fetch & cache the policy."""
        ignore_words_config: str = str(getattr(self, "ignore_words"))
        if ignore_words_config and ignore_words_config != "None":
            self.ignore_words_list = self.split_comma_separated_string(
                ignore_words_config.lower()
            )
        else:
            self.ignore_words_list = []

        return self.ignore_words_list
