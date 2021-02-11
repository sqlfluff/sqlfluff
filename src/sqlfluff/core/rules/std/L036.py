"""Implementation of Rule L036."""

from collections import namedtuple

from src.sqlfluff.core.rules.base import BaseCrawler, LintResult


class Rule_L036(BaseCrawler):
    """Select targets should be on a new line unless there is only one select target.

    | **Anti-pattern**

    .. code-block:: sql

        select
            *
        from x


    | **Best practice**

    .. code-block:: sql

        select
            a,
            b,
            c
        from x

    """

    def _eval(self, segment, raw_stack, **kwargs):
        if segment.is_type("select_clause"):
            eval_result = self._get_indexes(segment)
            if eval_result.cnt_select_targets == 1:
                return self._eval_single_select_target_element(eval_result, segment)
            if eval_result.cnt_select_targets > 1:
                return self._eval_multiple_select_target_elements(eval_result, segment)

    @staticmethod
    def _get_indexes(segment):
        EvalResult = namedtuple(
            "EvalResults",
            [
                "cnt_select_targets",
                "select_idx",
                "first_new_line_idx",
                "first_select_target_idx",
                "first_whitespace_idx",
            ],
        )
        cnt_select_targets = 0
        select_idx = -1
        first_new_line_idx = -1
        first_select_target_idx = -1
        first_whitespace_idx = -1
        for fname_idx, seg in enumerate(segment.segments):
            if seg.is_type("select_target_element"):
                cnt_select_targets += 1
                if first_select_target_idx == -1:
                    first_select_target_idx = fname_idx
            if seg.is_type("keyword") and seg.name == "SELECT" and select_idx == -1:
                select_idx = fname_idx
            if seg.is_type("newline") and first_new_line_idx == -1:
                first_new_line_idx = fname_idx
            # TRICKY: Ignore whitespace prior to the first newline, e.g. if
            # the line with "SELECT" (before any select targets) has trailing
            # whitespace.
            if (
                seg.is_type("whitespace")
                and first_new_line_idx != -1
                and first_whitespace_idx == -1
            ):
                first_whitespace_idx = fname_idx

        eval_result = EvalResult(
            cnt_select_targets,
            select_idx,
            first_new_line_idx,
            first_select_target_idx,
            first_whitespace_idx,
        )

        return eval_result

    @staticmethod
    def _eval_multiple_select_target_elements(eval_result, segment):
        if eval_result.first_new_line_idx == -1:
            # there are multiple select targets but no new lines
            return LintResult(anchor=segment)
        else:
            # ensure newline before select target and whitespace segment
            if (
                eval_result.first_new_line_idx
                < eval_result.first_whitespace_idx
                < eval_result.first_select_target_idx
            ):
                return None
            else:
                return LintResult(anchor=segment)

    @staticmethod
    def _eval_single_select_target_element(eval_result, select_clause):
        is_wildcard = False
        for segment in select_clause.segments:
            if segment.is_type("select_target_element"):
                for sub_segment in segment.segments:
                    if sub_segment.is_type("wildcard_expression"):
                        is_wildcard = True

        if is_wildcard:
            return None
        elif (
            eval_result.select_idx
            < eval_result.first_new_line_idx
            < eval_result.first_select_target_idx
        ):
            # there is a newline between select and select target
            return LintResult(anchor=select_clause)
        else:
            return None
