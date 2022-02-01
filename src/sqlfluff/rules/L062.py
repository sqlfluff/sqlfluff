"""Implementation of Rule L062."""

from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_configuration


@document_configuration
class Rule_L062(BaseRule):
    """Block a list of configurable phrases from being used.

    This generic rule can be useful to prevent certain keywords, functions, or objects
    from being used. Only whole words can be blocked, not phrases, nor parts of words.

    This block list is case insensitive.

    Example use cases:

    * We prefer ``BOOL`` over ``BOOLEAN`` and there is no existing rule to enforce
      this. We can add ``BOOLEAN`` to the deny list until such a rule is written to
      cause a linting error.
    * We have deprecated a schema/table/function and want to prevent it being used
      in future. We can add that to the denylist and then add a ``-- noqa: L062`` for
      the few exceptions that still need to be in the code base.

    | **Anti-pattern**
    | If the block_word_list is set to ``deprecated_table,bool`` then the following
    | will flag:

    .. code-block:: sql

        SELECT * FROM deprecated_table WHERE 1 = 1;
        CREATE TABLE myschema.t1 (a BOOL);

    | **Best practice**
    | Do not used any blocked words

    .. code-block:: sql

        SELECT * FROM another_table WHERE 1 = 1;
        CREATE TABLE myschema.t1 (a BOOLEAN);

    """

    config_keywords = [
        "block_word_list",
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        # Config type hints
        self.block_word_list: Optional[str]

        # Exit early if no block list set
        if not self.block_word_list:
            return None

        # Only look at child elements
        # Note: we do not need to ignore comments or meta types
        # or the like as they will not have single word raws
        if context.segment.segments:
            return None

        if str(context.segment.raw_upper) in (
            self.split_comma_separated_string(self.block_word_list.upper())
        ):
            return LintResult(
                anchor=context.segment,
                description=f"Use of blocked word '{context.segment.raw}'.",
            )

        return None
