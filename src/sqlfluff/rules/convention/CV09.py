"""Implementation of Rule CV09."""

from typing import List, Optional

import regex

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler


class Rule_CV09(BaseRule):
    """Block a list of configurable words from being used.

    This generic rule can be useful to prevent certain keywords, functions, or objects
    from being used. Only whole words can be blocked, not phrases, nor parts of words.

    This block list is case insensitive.

    **Example use cases**

    * We prefer ``BOOL`` over ``BOOLEAN`` and there is no existing rule to enforce
      this. Until such a rule is written, we can add ``BOOLEAN`` to the deny list
      to cause a linting error to flag this.
    * We have deprecated a schema/table/function and want to prevent it being used
      in future. We can add that to the denylist and then add a ``-- noqa: CV09`` for
      the few exceptions that still need to be in the code base for now.

    **Anti-pattern**

    If the ``blocked_words`` config is set to ``deprecated_table,bool`` then the
    following will flag:

    .. code-block:: sql

        SELECT * FROM deprecated_table WHERE 1 = 1;
        CREATE TABLE myschema.t1 (a BOOL);

    **Best practice**

    Do not used any blocked words:

    .. code-block:: sql

        SELECT * FROM another_table WHERE 1 = 1;
        CREATE TABLE myschema.t1 (a BOOLEAN);

    """

    name = "convention.blocked_words"
    aliases = ("L062",)
    groups = ("all", "convention")
    # It's a broad selector, but only trigger on raw segments.
    crawl_behaviour = SegmentSeekerCrawler({"raw"})
    config_keywords = [
        "blocked_words",
        "blocked_regex",
        "match_source",
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        # Config type hints
        self.blocked_words: Optional[str]
        self.blocked_regex: Optional[str]
        self.match_source: Optional[bool]

        # Exit early if no block list set
        if not self.blocked_words and not self.blocked_regex:
            return None

        if context.segment.type == "comment":
            return None

        # Get the ignore list configuration and cache it
        try:
            blocked_words_list = self.blocked_words_list
        except AttributeError:
            # First-time only, read the settings from configuration.
            # So we can cache them for next time for speed.
            blocked_words_list = self._init_blocked_words()

        if context.segment.raw_upper in blocked_words_list:
            return LintResult(
                anchor=context.segment,
                description=f"Use of blocked word '{context.segment.raw}'.",
            )

        if self.blocked_regex:
            if regex.search(self.blocked_regex, context.segment.raw):
                return LintResult(
                    anchor=context.segment,
                    description=f"Use of blocked regex '{context.segment.raw}'.",
                )

            if self.match_source:
                for segment in context.segment.raw_segments:
                    source_str = segment.pos_marker.source_str()
                    if regex.search(self.blocked_regex, source_str):
                        return LintResult(
                            anchor=context.segment,
                            description=f"Use of blocked regex '{source_str}'.",
                        )

        return None

    def _init_blocked_words(self) -> List[str]:
        """Called first time rule is evaluated to fetch & cache the blocked_words."""
        blocked_words_config = getattr(self, "blocked_words")
        if blocked_words_config:
            self.blocked_words_list = self.split_comma_separated_string(
                blocked_words_config.upper()
            )
        else:  # pragma: no cover
            # Shouldn't get here as we exit early if no block list
            self.blocked_words_list = []

        return self.blocked_words_list
