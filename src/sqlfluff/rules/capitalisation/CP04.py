"""Implementation of Rule CP04."""

from typing import Optional

from sqlfluff.core.rules import LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.rules.capitalisation.CP01 import Rule_CP01

try:
    import sqlfluffrs

    _HAS_SQLFLUFFRS = True
except ImportError:  # pragma: no cover
    _HAS_SQLFLUFFRS = False


class Rule_CP04(Rule_CP01):
    """Inconsistent capitalisation of boolean/null literal.

    **Anti-pattern**

    In this example, ``null`` and ``false`` are in lower-case whereas ``TRUE`` is in
    upper-case.

    .. code-block:: sql

        select
            a,
            null,
            TRUE,
            false
        from foo

    **Best practice**

    Ensure all literal ``null``/``true``/``false`` literals are consistently
    upper or lower case

    .. code-block:: sql

        select
            a,
            NULL,
            TRUE,
            FALSE
        from foo

        -- Also good

        select
            a,
            null,
            true,
            false
        from foo

    """

    name = "capitalisation.literals"
    aliases = ("L040",)
    is_fix_compatible = True

    crawl_behaviour = SegmentSeekerCrawler({"null_literal", "boolean_literal"})
    _exclude_types = ()
    _exclude_parent_types = ()
    _description_elem = "Boolean/null literals"

    def _eval_rust(self, context: RuleContext) -> Optional[list[LintResult]]:
        """Rust-native CP04 detection over the arena.

        Runs the whole detection in Rust (`sqlfluffrs.cp04_violations` over
        `root._rs_tree`) and maps each `(leaf_index, fixed_raw)` back to its
        Python segment to emit a standard `LintFix`. Returns ``None`` (Python
        fallback) when the Rust extension/arena is unavailable, or for a regex
        word-ignore. See ``BaseRule._eval_rust``/``Rule_CP01._eval_rust``.

        Deliberately its own override, not shared dispatch through CP01's —
        CP04 shares `capitalisation_policy` with CP01, so a policy-only check
        in an inherited hook would silently run CP01's keyword detection here
        instead of falling back to Python.
        """
        if not _HAS_SQLFLUFFRS:
            return None  # pragma: no cover
        if self.name != "capitalisation.literals":
            # Defensive only: no rule currently subclasses CP04, so this is
            # unreachable today — guards against a future subclass silently
            # inheriting this override the way pre-fix CP04 inherited CP01's.
            return None  # pragma: no cover
        if getattr(self, "ignore_words_regex", None):
            return None
        policy = str(getattr(self, "capitalisation_policy"))
        return self._eval_rust_capitalisation(
            context, sqlfluffrs.cp04_violations, policy
        )
