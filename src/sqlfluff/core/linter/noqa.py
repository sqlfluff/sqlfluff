"""Defines container classes for handling noqa comments."""

from typing import NamedTuple, Optional, Tuple, List, cast

from sqlfluff.core.errors import SQLBaseError


class NoQaDirective(NamedTuple):
    """Parsed version of a 'noqa' comment."""

    line_no: int  # Source line number
    rules: Optional[Tuple[str, ...]]  # Affected rule names
    action: Optional[str]  # "enable", "disable", or "None"


class IgnoreMask:
    """Structure to hold a set of 'noqa' directives."""

    def __init__(self, ignores: List[NoQaDirective]):
        self._ignore_list = ignores

    @staticmethod
    def _ignore_masked_violations_single_line(
        violations: List[SQLBaseError], ignore_mask: List[NoQaDirective]
    ):
        """Returns whether to ignore error for line-specific directives.

        The "ignore" list is assumed to ONLY contain NoQaDirectives with
        action=None.
        """
        for ignore in ignore_mask:
            violations = [
                v
                for v in violations
                if not (
                    v.line_no == ignore.line_no
                    and (ignore.rules is None or v.rule_code() in ignore.rules)
                )
            ]
        return violations

    @staticmethod
    def _should_ignore_violation_line_range(
        line_no: int, ignore_rule: List[NoQaDirective]
    ):
        """Returns whether to ignore a violation at line_no."""
        # Loop through the NoQaDirectives to find the state of things at
        # line_no. Assumptions about "ignore_rule":
        # - Contains directives for only ONE RULE, i.e. the rule that was
        #   violated at line_no
        # - Sorted in ascending order by line number
        disable = False
        for ignore in ignore_rule:
            if ignore.line_no > line_no:
                break
            disable = ignore.action == "disable"
        return disable

    @classmethod
    def _ignore_masked_violations_line_range(
        cls, violations: List[SQLBaseError], ignore_mask: List[NoQaDirective]
    ):
        """Returns whether to ignore error for line-range directives.

        The "ignore" list is assumed to ONLY contain NoQaDirectives where
        action is "enable" or "disable".
        """
        result = []
        for v in violations:
            # Find the directives that affect the violated rule "v", either
            # because they specifically reference it or because they don't
            # specify a list of rules, thus affecting ALL rules.
            ignore_rule = sorted(
                (
                    ignore
                    for ignore in ignore_mask
                    if not ignore.rules
                    or (v.rule_code() in cast(Tuple[str, ...], ignore.rules))
                ),
                key=lambda ignore: ignore.line_no,
            )
            # Determine whether to ignore the violation, based on the relevant
            # enable/disable directives.
            if not cls._should_ignore_violation_line_range(v.line_no, ignore_rule):
                result.append(v)
        return result

    def ignore_masked_violations(
        self, violations: List[SQLBaseError]
    ) -> List[SQLBaseError]:
        """Remove any violations specified by ignore_mask.

        This involves two steps:
        1. Filter out violations affected by single-line "noqa" directives.
        2. Filter out violations affected by disable/enable "noqa" directives.
        """
        ignore_specific = [ignore for ignore in self._ignore_list if not ignore.action]
        ignore_range = [ignore for ignore in self._ignore_list if ignore.action]
        violations = self._ignore_masked_violations_single_line(
            violations, ignore_specific
        )
        violations = self._ignore_masked_violations_line_range(violations, ignore_range)
        return violations
