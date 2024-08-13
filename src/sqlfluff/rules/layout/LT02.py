"""Implementation of Rule LT02."""

from typing import List

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

    def _eval(self, context: RuleContext) -> List[LintResult]:
        """Indentation not consistent with previous lines.

        To set the default tab size, set the `tab_space_size` value
        in the appropriate configuration. To correct indents to tabs
        use the `indent_unit` value set to `tab`.

        """
        return (
            ReflowSequence.from_root(context.segment, context.config)
            .reindent()
            .get_results()
        )
