"""Implementation of Rule L008."""

from sqlfluff.core.rules.base import BaseCrawler, LintResult, LintFix
from sqlfluff.core.rules.doc_decorators import document_fix_compatible


@document_fix_compatible
class Rule_L008(BaseCrawler):
    """Commas should be followed by a single whitespace unless followed by a comment.

    | **Anti-pattern**
    | The • character represents a space.
    | In this example, there is no space between the comma and 'zoo'.

    .. code-block::

        SELECT
            *
        FROM foo
        WHERE a IN ('plop','zoo')

    | **Best practice**
    | Keep a single space after the comma.

    .. code-block::

        SELECT
            *
        FROM foo
        WHERE a IN ('plop',•'zoo')
    """

    def _eval(self, segment, raw_stack, **kwargs):
        """Commas should be followed by a single whitespace unless followed by a comment.

        This is a slightly odd one, because we'll almost always evaluate from a point a few places
        after the problem site. NB: We need at least two segments behind us for this to work.
        """
        if len(raw_stack) < 2:
            return None

        cm1 = raw_stack[-1]
        cm2 = raw_stack[-2]
        if cm2.name == "comma":
            # comma followed by something that isn't whitespace?
            if cm1.name not in ["whitespace", "newline"]:
                ins = self.make_whitespace(raw=" ", pos_marker=cm1.pos_marker)
                return LintResult(anchor=cm1, fixes=[LintFix("create", cm1, ins)])
            # comma followed by too much whitespace?
            if (cm1.raw != " " and cm1.name != "newline") and not segment.is_comment:
                repl = cm1.__class__(raw=" ", pos_marker=cm1.pos_marker)
                return LintResult(anchor=cm1, fixes=[LintFix("edit", cm1, repl)])
        # Otherwise we're fine
        return None
