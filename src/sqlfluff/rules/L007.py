"""Implementation of Rule L007."""

from sqlfluff.core.rules.base import BaseRule, LintResult

after_description = "Operators near newlines should be after, not before the newline"
before_description = "Operators near newlines should be before, not after the newline"


class Rule_L007(BaseRule):
    """Operators should follow a standard for being before/after newlines.

    | **Anti-pattern**
    | The • character represents a space.
    | If ``operator_new_lines = after`` (or unspecified, as this is the default)
    | In this example, the operator '+' should not be at the end of the second line.

    .. code-block:: sql

        SELECT
            a +
            b
        FROM foo


    | **Best practice**
    | If ``operator_new_lines = after`` (or unspecified, as this is the default)
    | Place the operator after the newline.

    .. code-block:: sql

        SELECT
            a
            + b
        FROM foo

    | If ``operator_new_lines = before``
    | Place the operator before the newline.

    .. code-block:: sql

        SELECT
            a +
            b
        FROM foo
    """

    config_keywords = ["operator_new_lines"]

    def _eval(self, segment, memory, parent_stack, **kwargs):
        """Operators should follow a standard for being before/after newlines.

        We use the memory to keep track of whitespace up to now, and
        whether the last code segment was an operator or not.
        Anchor is our signal as to whether there's a problem.

        We only trigger if we have an operator FOLLOWED BY a newline
        before the next meaningful code segment.

        """
        anchor = None
        description = after_description
        if self.operator_new_lines == "before":
            description = before_description

        # The parent stack tells us whether we're in an expression or not.
        if parent_stack and parent_stack[-1].is_type("expression"):
            if segment.is_code:
                # This is code, what kind?
                if segment.is_type("binary_operator", "comparison_operator"):
                    # If it's an operator, then check if in "before" mode
                    if self.operator_new_lines == "before":
                        # If we're in "before" mode, then check if newline since last code
                        for s in memory["since_code"]:
                            if s.name == "newline":
                                # Had a newline - so mark this operator as a fail
                                anchor = segment
                                # TODO: Work out a nice fix for this failure.
                elif memory["last_code"] and memory["last_code"].is_type(
                    "binary_operator", "comparison_operator"
                ):
                    # It's not an operator, but the last code was.
                    if self.operator_new_lines != "before":
                        # If in "after" mode, then check to see
                        # there is a newline between us and the last operator.
                        for s in memory["since_code"]:
                            if s.name == "newline":
                                # Had a newline - so mark last operator as a fail
                                anchor = memory["last_code"]
                                # TODO: Work out a nice fix for this failure.
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
            return LintResult(anchor=anchor, memory=memory, description=description)
        else:
            return LintResult(memory=memory)
