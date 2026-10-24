"""Implementation of Rule TQ05."""

from typing import Optional

from sqlfluff.core.parser import BaseSegment, SymbolSegment
from sqlfluff.core.rules import BaseRule, LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_TQ05(BaseRule):
    """Combine consecutive scalar T-SQL DECLARE statements.

    This optional style rule only joins directly adjacent scalar declarations
    with explicit semicolons. Comments, templated content, table variables,
    cursors, and nonliteral initializers are left untouched because combining
    them could change the meaning or ownership of source text.

    Enable the rule using force_enable = True.

    **Anti-pattern**

    .. code-block:: sql
       :force:

        DECLARE @first INT;
        DECLARE @second NVARCHAR(10);

    **Best practice**

    .. code-block:: sql
       :force:

        DECLARE @first INT,
            @second NVARCHAR(10);
    """

    name = "tsql.combine_declarations"
    aliases = ()
    groups = ("all", "tsql")
    config_keywords = ["force_enable"]
    is_fix_compatible = True
    crawl_behaviour = SegmentSeekerCrawler(
        {"batch", "begin_end_block", "procedure_statement"}
    )

    @staticmethod
    def _scalar_declare(statement: BaseSegment) -> Optional[BaseSegment]:
        """Find a safely mergeable declaration directly within a statement."""
        if not statement.is_type("statement"):
            return None
        declaration = statement.get_child("declare_segment")
        if (
            declaration is None
            or not declaration.pos_marker
            or not declaration.pos_marker.is_literal()
            or any(
                segment.is_type("comment")
                or not segment.pos_marker
                or not segment.pos_marker.is_literal()
                for segment in statement.raw_segments
            )
        ):
            return None

        children = declaration.segments
        if not children or not children[0].is_type("keyword"):
            return None
        if children[0].raw_upper != "DECLARE":
            return None
        # TABLE variables must be declared alone. CURSOR declarations have a
        # separate grammar, but share the type "declare_segment".
        if any(
            segment.is_type("keyword") and segment.raw_upper not in {"DECLARE", "AS"}
            for segment in children
        ):
            return None
        variables = [s for s in children if s.is_type("parameter")]
        datatypes = [s for s in children if s.is_type("data_type")]
        if not variables or len(variables) != len(datatypes):
            return None
        # Named data types can be user-defined TABLE types, which must be
        # declared alone. Without schema information, only join declarations
        # whose types use the dialect's built-in (keyword) grammar.
        if any(
            not s.raw_segments
            or not s.raw_segments[0].is_type("keyword")
            or s.raw_segments[0].raw_upper in {"CURSOR", "TABLE"}
            or any(
                part.is_type("data_type_identifier", "dot") for part in s.raw_segments
            )
            for s in datatypes
        ):
            return None
        if any(not s.raw.startswith("@") or s.raw.startswith("@@") for s in variables):
            return None
        if len({s.raw.upper() for s in variables}) != len(variables):
            return None

        # Only expressions made from a single literal can be independent of
        # preceding declarations or other database state.
        expressions = [s for s in children if s.is_type("expression")]
        for expression in expressions:
            code = [s for s in expression.segments if s.is_code]
            if len(code) != 1 or not code[0].is_type(
                "integer_literal", "numeric_literal", "quoted_literal", "null_literal"
            ):
                return None
        return declaration

    def _eval(self, context: RuleContext) -> Optional[list[LintResult]]:
        """Combine maximal safe runs without crossing a statement boundary."""
        self.force_enable: bool
        if not self.force_enable or context.dialect.name != "tsql":
            return None

        segments = context.segment.segments
        results = []
        idx = 0
        while idx < len(segments):
            first_declare = self._scalar_declare(segments[idx])
            if first_declare is None:
                idx += 1
                continue

            current_idx = idx
            variables = {
                s.raw.upper() for s in first_declare.segments if s.is_type("parameter")
            }
            fixes: list[LintFix] = []
            while current_idx + 2 < len(segments):
                terminator = segments[current_idx + 1]
                if (
                    not terminator.is_type("statement_terminator")
                    or terminator.raw != ";"
                    or not terminator.pos_marker
                    or not terminator.pos_marker.is_literal()
                ):
                    break

                next_idx = current_idx + 2
                while next_idx < len(segments) and segments[next_idx].is_type(
                    "whitespace", "newline", "indent", "dedent"
                ):
                    next_idx += 1
                between = segments[current_idx + 2 : next_idx]
                if next_idx == len(segments) or not all(
                    segment.pos_marker and segment.pos_marker.is_literal()
                    for segment in between
                ):
                    break
                next_declare = self._scalar_declare(segments[next_idx])
                if next_declare is None:
                    break
                next_variables = {
                    s.raw.upper()
                    for s in next_declare.segments
                    if s.is_type("parameter")
                }
                if variables.intersection(next_variables):
                    break

                # Replace the statement separator with the list delimiter,
                # preserving the next variable's original data type and text.
                fixes.append(
                    LintFix.replace(terminator, [SymbolSegment(raw=",", type="comma")])
                )
                fixes.append(LintFix.delete(next_declare.segments[0]))
                # The whitespace after DECLARE supplies the inline separator;
                # remove preceding same-line spaces to avoid doubling them.
                if not any(s.is_type("newline") for s in between):
                    fixes.extend(
                        LintFix.delete(s) for s in between if s.is_type("whitespace")
                    )
                variables.update(next_variables)
                current_idx = next_idx

            if fixes:
                results.append(
                    LintResult(
                        anchor=first_declare,
                        fixes=fixes,
                        description="Combine consecutive scalar DECLARE statements.",
                    )
                )
                idx = current_idx + 1
            else:
                idx += 1
        return results or None
