"""Implementation of Rule L025."""

from sqlfluff.core.rules.base import LintFix, LintResult
from sqlfluff.core.rules.doc_decorators import document_fix_compatible
from sqlfluff.core.rules.functional import Segments
import sqlfluff.core.rules.functional.segment_predicates as sp
from sqlfluff.rules.L020 import Rule_L020
from sqlfluff.core.dialects.common import AliasInfo


@document_fix_compatible
class Rule_L025(Rule_L020):
    """Tables should not be aliased if that alias is not used.

    | **Anti-pattern**

    .. code-block:: sql

        SELECT
            a
        FROM foo AS zoo

    | **Best practice**
    | Use the alias or remove it. An unused alias makes code
    | harder to read without changing any functionality.

    .. code-block:: sql

        SELECT
            zoo.a
        FROM foo AS zoo

        -- Alternatively...

        SELECT
            a
        FROM foo

    """

    def _lint_references_and_aliases(
        self,
        table_aliases,
        standalone_aliases,
        references,
        col_aliases,
        using_cols,
        parent_select,
    ):
        """Check all aliased references against tables referenced in the query."""
        # A buffer to keep any violations.
        violation_buff = []
        # Check all the references that we have, keep track of which aliases we refer
        # to.
        tbl_refs = set()
        for r in references:
            tbl_refs.update(
                tr.part
                for tr in r.extract_possible_references(
                    level=r.ObjectReferenceLevel.TABLE
                )
            )

        alias: AliasInfo
        for alias in table_aliases:
            if alias.aliased and alias.ref_str not in tbl_refs:
                fixes = [LintFix.delete(alias.alias_expression)]
                # Walk back to remove indents/whitespaces
                to_delete = (
                    Segments(*alias.from_expression_element.segments)
                    .reversed()
                    .select(
                        start_seg=alias.alias_expression,
                        # Stop once we reach an other, "regular" segment.
                        loop_while=sp.or_(sp.is_whitespace(), sp.is_meta()),
                    )
                )
                fixes += [LintFix.delete(seg) for seg in to_delete]
                violation_buff.append(
                    LintResult(
                        anchor=alias.segment,
                        description="Alias {!r} is never used in SELECT "
                        "statement.".format(alias.ref_str),
                        fixes=fixes,
                    )
                )
        return violation_buff or None
