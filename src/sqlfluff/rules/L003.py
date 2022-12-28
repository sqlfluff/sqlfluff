"""Implementation of Rule L003."""
from typing import List

from sqlfluff.core.rules import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import RootOnlyCrawler
from sqlfluff.core.rules.doc_decorators import (
    document_configuration,
    document_fix_compatible,
    document_groups,
)
from sqlfluff.utils.reflow.sequence import ReflowSequence


@document_groups
@document_fix_compatible
@document_configuration
class Rule_L003(BaseRule):
    """Indentation not consistent with previous lines.

    **Anti-pattern**

    The ``•`` character represents a space.
    In this example, the third line contains five spaces instead of four.

    .. code-block:: sql
       :force:

        SELECT
        ••••a,
        •••••b
        FROM foo


    **Best practice**

    Change the indentation to use a multiple of four spaces.

    .. code-block:: sql
       :force:

        SELECT
        ••••a,
        ••••b
        FROM foo

    """

    groups = ("all", "core")
    crawl_behaviour = RootOnlyCrawler()
    targets_templated = True
    template_safe_fixes = True
    _adjust_anchors = True

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Indentation not consistent with previous lines.

        To set the default tab size, set the `tab_space_size` value
        in the appropriate configuration.

        We compare each line (first non-whitespace element of the
        line), with the indentation of previous lines. The presence
        (or lack) of indent or dedent meta-characters indicate whether
        the indent is appropriate.

        - Any line is assessed by the indent level at the first non
          whitespace element.
        - Any increase in indentation may be _up to_ the number of
          indent characters.
        - Any line must be in line with the previous line which had
          the same indent balance at its start.
        - Apart from "whole" indents, a "hanging" indent is possible
          if the line starts in line with either the indent of the
          previous line or if it starts at the same indent as the *last*
          indent meta segment in the previous line.

        """
        # NOTE: Until rule consolidation, we're going to filter out
        # any long line fixes. After that we'll consolidate the two
        # into one rule.
        results = (
            ReflowSequence.from_root(context.segment, context.config)
            .reindent()
            .get_results()
        )
        return [res for res in results if res.source != "reflow.long_line"]
