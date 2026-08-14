"""Implementation of Rule CV13."""


from sqlfluff.core.parser import KeywordSegment, WhitespaceSegment
from sqlfluff.core.rules import (
    BaseRule,
    EvalResultType,
    LintFix,
    LintResult,
    RuleContext,
)
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CV13(BaseRule):
    """Redundant boolean comparison in expressions.

    Boolean comparisons with ``TRUE`` or ``FALSE`` (e.g. ``x = TRUE``, ``x = FALSE``,
    ``x IS TRUE``, ``x IS NOT FALSE``) are redundant and should be simplified to
    ``x`` or ``NOT x``.

    **Anti-pattern**

    Comparing a boolean expression or column against boolean literals.

    .. code-block:: sql

        SELECT a
        FROM foo
        WHERE is_active = TRUE AND is_deleted = FALSE;

    **Best practice**

    Use the boolean expression directly or with ``NOT``.

    .. code-block:: sql

        SELECT a
        FROM foo
        WHERE is_active AND NOT is_deleted;

    """

    name = "convention.boolean_comparison"
    aliases = ()
    groups = ("all", "convention")
    crawl_behaviour = SegmentSeekerCrawler({"expression"})
    config_keywords = ["preferred_boolean_comparison_style"]
    is_fix_compatible = True

    def _eval(self, context: RuleContext) -> EvalResultType:
        """Find redundant boolean comparisons in expressions and simplify them."""
        self.preferred_boolean_comparison_style: str
        preferred_style = (
            getattr(self, "preferred_boolean_comparison_style", "implicit")
            or "implicit"
        )
        if preferred_style != "implicit":
            return None

        # Allow assignments in SET clauses or assignment operators
        if any(
            parent.is_type(
                "set_clause_list",
                "execute_script_statement",
                "options_segment",
                "assignment_operator",
            )
            for parent in context.parent_stack
        ):
            return None

        expr = context.segment
        children = list(expr.segments)

        # Split into subconditions by top-level binary operators (AND / OR / XOR)
        subconditions = []
        current = []
        for child in children:
            if child.is_type("binary_operator") and child.raw.upper() in (
                "AND",
                "OR",
                "XOR",
            ):
                if current:
                    subconditions.append(current)
                    current = []
                subconditions.append([child])
            else:
                current.append(child)
        if current:
            subconditions.append(current)

        results: list[LintResult] = []
        for chunk in subconditions:
            code_segs = [s for s in chunk if s.is_code]
            if not code_segs:
                continue

            is_match = False
            is_positive = True
            target_segs = []
            anchor = None
            boolean_lit_seg = None

            # Pattern 1: comparison_operator (=, !=, <>) with a boolean literal
            comp_ops = [s for s in code_segs if s.is_type("comparison_operator")]
            if len(comp_ops) == 1:
                comp_op = comp_ops[0]
                raw_comp = (
                    "".join(
                        s.raw for s in comp_op.get_children("raw_comparison_operator")
                    )
                    or comp_op.raw.strip()
                )
                if raw_comp in ("=", "!=", "<>"):
                    comp_idx = chunk.index(comp_op)
                    before_chunk = chunk[:comp_idx]
                    after_chunk = chunk[comp_idx + 1 :]
                    before_code = [s for s in before_chunk if s.is_code]
                    after_code = [s for s in after_chunk if s.is_code]

                    # Subcase 1A: RHS is boolean literal
                    if (
                        len(after_code) == 1
                        and after_code[0].raw.upper() in ("TRUE", "FALSE")
                        and not (
                            len(before_code) == 1
                            and before_code[0].raw.upper() in ("TRUE", "FALSE")
                        )
                    ):
                        boolean_lit_seg = after_code[0]
                        lit = boolean_lit_seg.raw.upper()
                        is_match = True
                        anchor = comp_op
                        target_segs = before_chunk
                        if raw_comp == "=":
                            is_positive = lit == "TRUE"
                        else:
                            is_positive = lit == "FALSE"

                    # Subcase 1B: LHS is boolean literal
                    elif (
                        len(before_code) == 1
                        and before_code[0].raw.upper() in ("TRUE", "FALSE")
                        and not (
                            len(after_code) == 1
                            and after_code[0].raw.upper() in ("TRUE", "FALSE")
                        )
                    ):
                        boolean_lit_seg = before_code[0]
                        lit = boolean_lit_seg.raw.upper()
                        is_match = True
                        anchor = comp_op
                        target_segs = after_chunk
                        if raw_comp == "=":
                            is_positive = lit == "TRUE"
                        else:
                            is_positive = lit == "FALSE"

            # Pattern 2: IS [NOT] TRUE / FALSE
            if not is_match and len(code_segs) >= 2:
                last_code = code_segs[-1]
                if last_code.raw.upper() in ("TRUE", "FALSE"):
                    boolean_lit_seg = last_code
                    lit = boolean_lit_seg.raw.upper()
                    if (
                        len(code_segs) >= 3
                        and code_segs[-2].raw.upper() == "NOT"
                        and code_segs[-3].raw.upper() == "IS"
                    ):
                        is_match = True
                        anchor = code_segs[-3]
                        is_idx = chunk.index(code_segs[-3])
                        target_segs = chunk[:is_idx]
                        is_positive = lit == "FALSE"
                    elif code_segs[-2].raw.upper() == "IS":
                        is_match = True
                        anchor = code_segs[-2]
                        is_idx = chunk.index(code_segs[-2])
                        target_segs = chunk[:is_idx]
                        is_positive = lit == "TRUE"

            if is_match and anchor:
                # Find active span bounds within chunk
                first_span_idx = 0
                while first_span_idx < len(chunk) and chunk[first_span_idx].is_type(
                    "whitespace", "newline"
                ):
                    first_span_idx += 1
                last_span_idx = len(chunk)
                while last_span_idx > 0 and chunk[last_span_idx - 1].is_type(
                    "whitespace", "newline"
                ):
                    last_span_idx -= 1
                active_span = chunk[first_span_idx:last_span_idx]

                while target_segs and target_segs[0].is_type("whitespace", "newline"):
                    target_segs = target_segs[1:]
                while target_segs and target_segs[-1].is_type("whitespace", "newline"):
                    target_segs = target_segs[:-1]

                # Determine case style based on boolean literal and keywords
                is_upper = True
                if boolean_lit_seg is not None:
                    if boolean_lit_seg.raw.islower():
                        is_upper = False
                    elif boolean_lit_seg.raw.isupper():
                        is_upper = True
                else:
                    for s in chunk:
                        if s.is_type(
                            "keyword", "boolean_literal", "literal", "null_literal"
                        ):
                            if s.raw.isupper():
                                is_upper = True
                                break
                            if s.raw.islower():
                                is_upper = False
                                break

                not_kw_str = "NOT" if is_upper else "not"

                target_code = [s for s in target_segs if s.is_code]
                if is_positive:
                    replacement = target_segs
                else:
                    if target_code and target_code[0].raw.upper() == "NOT":
                        # Double negative cancellation: NOT x -> x
                        first_code_idx = next(
                            i for i, s in enumerate(target_segs) if s.is_code
                        )
                        remaining = target_segs[first_code_idx + 1 :]
                        while remaining and remaining[0].is_type(
                            "whitespace", "newline"
                        ):
                            remaining = remaining[1:]
                        replacement = remaining
                    else:
                        replacement = [
                            KeywordSegment(not_kw_str),
                            WhitespaceSegment(),
                        ] + target_segs

                fixes = [LintFix.replace(active_span[0], replacement)]
                for s in active_span[1:]:
                    fixes.append(LintFix.delete(s))

                results.append(
                    LintResult(
                        anchor=anchor,
                        fixes=fixes,
                        description="Redundant boolean comparison in expression.",
                    )
                )

        return results or None
