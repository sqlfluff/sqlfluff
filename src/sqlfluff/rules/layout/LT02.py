"""Implementation of Rule LT02."""

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.utils.reflow.sequence import ReflowSequence


class Rule_LT02(BaseRule):
    """Incorrect Indentation.

    **Anti-pattern**

    The ``•`` character represents a space and the ``→`` character represents a tab.
    In this example, the third line contains five spaces instead of four and
    the second line contains two spaces and one tab.

    .. code-block:: sql
       :force:

        SELECT
        ••→a,
        •••••b
        FROM foo


    **Best practice**

    Change the indentation to use a multiple of four spaces. This example also
    assumes that the ``indent_unit`` config value is set to ``space``. If it
    had instead been set to ``tab``, then the indents would be tabs instead.

    .. code-block:: sql
       :force:

        SELECT
        ••••a,
        ••••b
        FROM foo

    """

    name = "layout.indent"
    # NOTE: We're combining three legacy rules here into one.
    aliases = ("L002", "L003", "L004")
    groups = ("all", "core", "layout")
    crawl_behaviour = RootOnlyCrawler()
    is_fix_compatible = True
    targets_templated = True
    template_safe_fixes = True
    _adjust_anchors = True

    def _eval(self, context: RuleContext) -> list[LintResult]:
        """Indentation not consistent with previous lines.

        To set the default tab size, set the `tab_space_size` value
        in the appropriate configuration. To correct indents to tabs
        use the `indent_unit` value set to `tab`.

        """
        results = (
            ReflowSequence.from_root(context.segment, context.config)
            .reindent()
            .get_results()
        )

        # LT07 owns whether an otherwise correctly indented multi-line CTE
        # closing bracket should move onto its own line. Reflow sees the dedent
        # immediately before the bracket and can independently propose the same
        # line break as LT02, so excluding LT07 would not disable that behavior.
        #
        # Keep the line break when LT02 is also repairing indentation inside the
        # same CTE, because that is part of making the whole indentation block
        # coherent rather than duplicating LT07.
        cte_segments_by_line_break_anchor = {}
        for cte in context.segment.recursive_crawl("common_table_expression"):
            bracketed_segments = [
                segment for segment in cte.segments if segment.is_type("bracketed")
            ]
            if bracketed_segments:
                end_bracket = bracketed_segments[-1].get_child("end_bracket")
                if end_bracket:
                    cte_raw_segments = list(cte.raw_segments)
                    cte_segment_uuids = {segment.uuid for segment in cte_raw_segments}
                    end_bracket_idx = next(
                        idx
                        for idx, segment in enumerate(cte_raw_segments)
                        if segment.uuid == end_bracket.uuid
                    )
                    cte_segments_by_line_break_anchor[end_bracket.uuid] = (
                        cte_segment_uuids
                    )
                    for segment in reversed(cte_raw_segments[:end_bracket_idx]):
                        if segment.is_meta:
                            continue
                        if not segment.is_type("whitespace"):
                            break
                        cte_segments_by_line_break_anchor[segment.uuid] = (
                            cte_segment_uuids
                        )

        filtered_results = []
        for result in results:
            cte_segments = None
            for fix in result.fixes:
                if not any(edit.is_type("newline") for edit in (fix.edit or [])):
                    continue
                cte_segments = cte_segments_by_line_break_anchor.get(fix.anchor.uuid)
                if cte_segments is not None:
                    break

            is_standalone_cte_line_break = cte_segments is not None and not any(
                other is not result
                and other.anchor is not None
                and other.anchor.uuid in cte_segments
                for other in results
            )
            if not is_standalone_cte_line_break:
                filtered_results.append(result)

        return filtered_results
