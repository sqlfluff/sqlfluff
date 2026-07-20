"""Implementation of Rule CP03."""

from typing import Optional

from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.rules import LintFix, LintResult, RuleContext
from sqlfluff.core.rules.crawlers import SegmentSeekerCrawler
from sqlfluff.rules.capitalisation.CP01 import Rule_CP01

try:
    import sqlfluffrs

    _HAS_SQLFLUFFRS = True
except ImportError:  # pragma: no cover
    _HAS_SQLFLUFFRS = False


class Rule_CP03(Rule_CP01):
    """Inconsistent capitalisation of function names.

    **Anti-pattern**

    In this example, the two ``SUM`` functions don't have the same capitalisation.

    .. code-block:: sql

        SELECT
            sum(a) AS aa,
            SUM(b) AS bb
        FROM foo

    **Best practice**

    Make the case consistent.

    .. code-block:: sql

        SELECT
            sum(a) AS aa,
            sum(b) AS bb
        FROM foo

    """

    name = "capitalisation.functions"
    aliases = ("L030",)
    is_fix_compatible = True

    crawl_behaviour = SegmentSeekerCrawler(
        {"function_name_identifier", "bare_function"}
    )
    _exclude_types = ()
    _exclude_parent_types = ()

    config_keywords = [
        "extended_capitalisation_policy",
        "ignore_words",
        "ignore_words_regex",
    ]
    _description_elem = "Function names"

    def _eval_rust(self, context: RuleContext) -> Optional[list[LintResult]]:
        """Rust-native CP03 detection over the arena.

        Runs the whole detection in Rust (`sqlfluffrs.cp03_violations` over
        `root._rs_tree`) and maps each `(leaf_index, fixed_raw)` back to its
        Python segment to emit a standard `LintFix`. Returns ``None`` (Python
        fallback) when the Rust extension/arena is unavailable, or for a regex
        word-ignore. See ``BaseRule._eval_rust``/``Rule_CP01._eval_rust``.

        Deliberately its own override (not shared dispatch through CP01's) so
        there's nothing for a future capitalisation subclass to hijack, same as
        CP04's.
        """
        if not _HAS_SQLFLUFFRS:
            return None  # pragma: no cover
        if self.name != "capitalisation.functions":
            # Defensive only: no rule currently subclasses CP03, so this is
            # unreachable today — guards against a future subclass silently
            # inheriting this override the way pre-fix CP04 inherited CP01's.
            return None  # pragma: no cover
        if getattr(self, "ignore_words_regex", None):
            return None
        policy = str(getattr(self, "extended_capitalisation_policy"))
        return self._eval_rust_capitalisation(
            context, sqlfluffrs.cp03_violations, policy
        )

    def _get_fix(self, segment: BaseSegment, fixed_raw: str) -> LintFix:
        return super()._get_fix(segment, fixed_raw)
