"""Implementation of Rule L062."""

from typing import Optional

from sqlfluff.core.rules.base import BaseRule, LintResult, RuleContext
from sqlfluff.core.rules.doc_decorators import document_configuration


@document_configuration
class Rule_L062(BaseRule):
    """Block a list of configurable words from being used.

    This generic rule can be useful to prevent certain keywords, functions, or objects
    from being used. Only whole words can be blocked, not phrases, nor parts of words.

    This block list is case insensitive.

    **Example use cases**

    * We prefer ``BOOL`` over ``BOOLEAN`` and there is no existing rule to enforce
      this. Until such a rule is written, we can add ``BOOLEAN`` to the deny list
      to cause a linting error to flag this.
    * We have deprecated a schema/table/function and want to prevent it being used
      in future. We can add that to the denylist and then add a ``-- noqa: L062`` for
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

    config_keywords = [
        "blocked_words",
    ]

    def _eval(self, context: RuleContext) -> Optional[LintResult]:
        # Config type hints
        self.blocked_words: Optional[str]

        # Exit early if no block list set
        if not self.blocked_words:
            return None

        # Get the ignore list configuration and cache it
        try:
            blocked_words_list = self.blocked_words_list
        except AttributeError:
            # First-time only, read the settings from configuration.
            # So we can cache them for next time for speed.
            blocked_words_list = self._init_blocked_words()

        # Only look at child elements
        # Note: we do not need to ignore comments or meta types
        # or the like as they will not have single word raws
        if context.segment.segments:
            return None

        if context.segment.raw_upper in blocked_words_list:
            return LintResult(
                anchor=context.segment,
                description=f"Use of blocked word '{context.segment.raw}'.",
            )

        return None

    def _init_blocked_words(self):
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
