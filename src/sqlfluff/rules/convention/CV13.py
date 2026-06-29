from typing import List

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext, EvalResultType
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CV13(BaseRule):
    """Require safety guards on ALTER TABLE ADD/DROP COLUMN.

    ADD COLUMN statements must include ``IF NOT EXISTS`` and DROP COLUMN
    statements must include ``IF EXISTS`` to avoid errors when columns
    already exist or are missing.

    **Anti-pattern**

    .. code-block:: sql

        ALTER TABLE my_table ADD COLUMN my_col INT;
        ALTER TABLE my_table DROP COLUMN my_col;

    **Best practice**

    .. code-block:: sql

        ALTER TABLE my_table ADD COLUMN IF NOT EXISTS my_col INT;
        ALTER TABLE my_table DROP COLUMN IF EXISTS my_col;
    """

    name = "convention.alter_table_safety_guard"
    aliases = ()
    groups = ("all", "convention")

    crawl_behaviour = SegmentSeekerCrawler({"alter_table_action_segment"})

    def _eval(self, context: RuleContext) -> EvalResultType:
        # Check each ALTER TABLE action segment for safety guards
        segment = context.segment
        assert segment.is_type("alter_table_action_segment")

        # Determine whether this is an ADD or DROP action by finding the first
        # keyword in the segment.
        action_keyword = next(
            (
                seg.raw_upper
                for seg in segment.segments
                if seg.type == "keyword"
            ),
            None,
        )

        keyword_tokens: List[str] = [
            seg.raw_upper for seg in segment.segments if seg.type == "keyword"
        ]

        def _contains_subsequence(tokens: List[str], subseq: List[str]) -> bool:
            subseq_len = len(subseq)
            for idx in range(len(tokens) - subseq_len + 1):
                if tokens[idx: idx + subseq_len] == subseq:
                    return True
            return False

        if action_keyword == "ADD":
            if not _contains_subsequence(keyword_tokens, ["IF", "NOT", "EXISTS"]):
                return LintResult(anchor=segment)
        elif action_keyword == "DROP":
            if not _contains_subsequence(keyword_tokens, ["IF", "EXISTS"]):
                return LintResult(anchor=segment)

        return None
