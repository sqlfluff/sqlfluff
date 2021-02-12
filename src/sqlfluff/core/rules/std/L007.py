"""Implementation of Rule L007."""

from sqlfluff.core.rules.base import BaseCrawler, LintResult


class Rule_L007(BaseCrawler):
    """Operators near newlines should be after, not before the newline.

    | **Anti-pattern**
    | The • character represents a space.
    | In this example, the operator '+' should not be at the end of the second line.

    .. code-block:: sql

        SELECT
            a +
            b
        FROM foo


    | **Best practice**
    | Place the operator after the newline.

    .. code-block:: sql

        SELECT
            a
            + b
        FROM foo
    """

    def _eval(self, segment, memory, parent_stack, **kwargs):
        """Operators near newlines should be after, not before the newline.

        We use the memory to keep track of whitespace up to now, and
        whether the last code segment was an operator or not.
        Anchor is our signal as to whether there's a problem.

        We only trigger if we have an operator FOLLOWED BY a newline
        before the next meaningful code segment.

        """
        anchor = None

        # The parent stack tells us whether we're in an expression or not.
        if parent_stack and parent_stack[-1].is_type("expression"):
            if segment.is_code:
                # This is code, what kind?
                if segment.is_type("binary_operator", "comparison_operator"):
                    # We only trigger if the last was an operator, not if this is.
                    pass
                elif memory["last_code"] and memory["last_code"].is_type(
                    "binary_operator", "comparison_operator"
                ):
                    # It's not an operator, but the last code was. Now check to see
                    # there is a newline between us and the last operator.
                    for s in memory["since_code"]:
                        if s.name == "newline":
                            anchor = memory["last_code"]
                            # TODO: Work out a nice fix for this.
                # Prepare memory for later
                memory["last_code"] = segment
                memory["since_code"] = []
            else:
                # This isn't a code segment...
                # Prepare memory for later
                memory["since_code"].append(segment)
        else:
            # Reset the memory if we're not in an expression
            memory = {"last_code": None, "since_code": []}

        # Anchor is our signal as to whether there's a problem
        if anchor:
            return LintResult(anchor=anchor, memory=memory)
        else:
            return LintResult(memory=memory)
