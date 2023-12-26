"""Defines container classes for handling noqa comments."""

import fnmatch
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Set, Tuple, cast

from sqlfluff.core.errors import SQLBaseError, SQLParseError, SQLUnusedNoQaWarning
from sqlfluff.core.parser import BaseSegment, RawSegment, RegexLexer

# Instantiate the linter logger
linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")


@dataclass
class NoQaDirective:
    """Parsed version of a 'noqa' comment."""

    line_no: int  # Source line number
    line_pos: int  # Source line position
    rules: Optional[Tuple[str, ...]]  # Affected rule names
    action: Optional[str]  # "enable", "disable", or "None"
    raw_str: str = ""  # The raw representation of the directive for warnings.
    used: bool = False  # Has it been used.

    def _filter_violations_single_line(
        self, violations: List[SQLBaseError]
    ) -> List[SQLBaseError]:
        """Filter a list of violations based on this single line noqa.

        Also record whether this class was _used_ in any of that filtering.

        The "ignore" list is assumed to ONLY contain NoQaDirectives with
        action=None.
        """
        assert not self.action
        matched_violations = [
            v
            for v in violations
            if (
                v.line_no == self.line_no
                and (self.rules is None or v.rule_code() in self.rules)
            )
        ]
        if matched_violations:
            # Successful match, mark ignore as used.
            self.used = True
            return [v for v in violations if v not in matched_violations]
        else:
            return violations


class IgnoreMask:
    """Structure to hold a set of 'noqa' directives."""

    def __init__(self, ignores: List[NoQaDirective]):
        self._ignore_list = ignores

    def __repr__(self):  # pragma: no cover
        return "<IgnoreMask>"

    # ### Construction class methods.

    @staticmethod
    def _parse_noqa(
        comment: str,
        line_no: int,
        line_pos: int,
        reference_map: Dict[str, Set[str]],
    ):
        """Extract ignore mask entries from a comment string."""
        # Also trim any whitespace afterward

        # Comment lines can also have noqa e.g.
        # --dafhsdkfwdiruweksdkjdaffldfsdlfjksd -- noqa: LT05
        # Therefore extract last possible inline ignore.
        comment = [c.strip() for c in comment.split("--")][-1]

        if comment.startswith("noqa"):
            # This is an ignore identifier
            comment_remainder = comment[4:]
            if comment_remainder:
                if not comment_remainder.startswith(":"):
                    return SQLParseError(
                        "Malformed 'noqa' section. Expected 'noqa: <rule>[,...]",
                        line_no=line_no,
                    )
                comment_remainder = comment_remainder[1:].strip()
                if comment_remainder:
                    action: Optional[str]
                    if "=" in comment_remainder:
                        action, rule_part = comment_remainder.split("=", 1)
                        if action not in {"disable", "enable"}:  # pragma: no cover
                            return SQLParseError(
                                "Malformed 'noqa' section. "
                                "Expected 'noqa: enable=<rule>[,...] | all' "
                                "or 'noqa: disable=<rule>[,...] | all",
                                line_no=line_no,
                            )
                    else:
                        action = None
                        rule_part = comment_remainder
                        if rule_part in {"disable", "enable"}:
                            return SQLParseError(
                                "Malformed 'noqa' section. "
                                "Expected 'noqa: enable=<rule>[,...] | all' "
                                "or 'noqa: disable=<rule>[,...] | all",
                                line_no=line_no,
                            )
                    rules: Optional[Tuple[str, ...]]
                    if rule_part != "all":
                        # Rules can be globs therefore we compare to the rule_set to
                        # expand the globs.
                        unexpanded_rules = tuple(
                            r.strip() for r in rule_part.split(",")
                        )
                        # We use a set to do natural deduplication.
                        expanded_rules: Set[str] = set()
                        for r in unexpanded_rules:
                            matched = False
                            for expanded in (
                                reference_map[x]
                                for x in fnmatch.filter(reference_map.keys(), r)
                            ):
                                expanded_rules |= expanded
                                matched = True

                            if not matched:
                                # We were unable to expand the glob.
                                # Therefore assume the user is referencing
                                # a special error type (e.g. PRS, LXR, or TMP)
                                # and add this to the list of rules to ignore.
                                expanded_rules.add(r)
                        # Sort for consistency
                        rules = tuple(sorted(expanded_rules))
                    else:
                        rules = None
                    return NoQaDirective(line_no, line_pos, rules, action, comment)
            return NoQaDirective(line_no, line_pos, None, None, comment)
        return None

    @classmethod
    def _extract_ignore_from_comment(
        cls,
        comment: RawSegment,
        reference_map: Dict[str, Set[str]],
    ):
        """Extract ignore mask entries from a comment segment."""
        # Also trim any whitespace
        comment_content = comment.raw_trimmed().strip()
        # If we have leading or trailing block comment markers, also strip them.
        # NOTE: We need to strip block comment markers from the start
        # to ensure that noqa directives in the following form are followed:
        # /* noqa: disable=all */
        if comment_content.endswith("*/"):
            comment_content = comment_content[:-2].rstrip()
        if comment_content.startswith("/*"):
            comment_content = comment_content[2:].lstrip()
        comment_line, comment_pos = comment.pos_marker.source_position()
        result = cls._parse_noqa(
            comment_content, comment_line, comment_pos, reference_map
        )
        if isinstance(result, SQLParseError):
            result.segment = comment
        return result

    @classmethod
    def from_tree(
        cls,
        tree: BaseSegment,
        reference_map: Dict[str, Set[str]],
    ) -> Tuple["IgnoreMask", List[SQLBaseError]]:
        """Look for inline ignore comments and return NoQaDirectives."""
        ignore_buff: List[NoQaDirective] = []
        violations: List[SQLBaseError] = []
        for comment in tree.recursive_crawl("comment"):
            if comment.is_type("inline_comment", "block_comment"):
                ignore_entry = cls._extract_ignore_from_comment(
                    cast(RawSegment, comment), reference_map
                )
                if isinstance(ignore_entry, SQLParseError):
                    violations.append(ignore_entry)
                elif ignore_entry:
                    ignore_buff.append(ignore_entry)
        if ignore_buff:
            linter_logger.info("Parsed noqa directives from file: %r", ignore_buff)
        return cls(ignore_buff), violations

    @classmethod
    def from_source(
        cls,
        source: str,
        inline_comment_regex: RegexLexer,
        reference_map: Dict[str, Set[str]],
    ) -> Tuple["IgnoreMask", List[SQLBaseError]]:
        """Look for inline ignore comments and return NoQaDirectives.

        Very similar to .from_tree(), but can be run on raw source
        (i.e. does not require the code to have parsed successfully).
        """
        ignore_buff: List[NoQaDirective] = []
        violations: List[SQLBaseError] = []
        for idx, line in enumerate(source.split("\n")):
            match = inline_comment_regex.search(line) if line else None
            if match:
                ignore_entry = cls._parse_noqa(
                    line[match[0] : match[1]], idx + 1, match[0], reference_map
                )
                if isinstance(ignore_entry, SQLParseError):
                    violations.append(ignore_entry)  # pragma: no cover
                elif ignore_entry:
                    ignore_buff.append(ignore_entry)
        if ignore_buff:
            linter_logger.info("Parsed noqa directives from file: %r", ignore_buff)
        return cls(ignore_buff), violations

    # ### Application methods.

    @staticmethod
    def _ignore_masked_violations_single_line(
        violations: List[SQLBaseError], ignore_mask: List[NoQaDirective]
    ):
        """Filter a list of violations based on this single line noqa.

        The "ignore" list is assumed to ONLY contain NoQaDirectives with
        action=None.
        """
        for ignore in ignore_mask:
            violations = ignore._filter_violations_single_line(violations)
        return violations

    @staticmethod
    def _should_ignore_violation_line_range(
        line_no: int, ignore_rules: List[NoQaDirective]
    ) -> Tuple[bool, Optional[NoQaDirective]]:
        """Returns whether to ignore a violation at line_no.

        Loop through the NoQaDirectives to find the state of things at
        line_no. Assumptions about "ignore_rules":
        - Contains directives for only ONE RULE, i.e. the rule that was
          violated at line_no
        - Sorted in ascending order by line number
        """
        ignore = False
        last_ignore = None
        for idx, ignore_rule in enumerate(ignore_rules):
            if ignore_rule.line_no > line_no:
                # Peak at the next rule to see if it's a matching disable
                # and if it is, then mark it as used.
                if ignore_rule.action == "enable":
                    # Mark as used
                    ignore_rule.used = True
                break

            if ignore_rule.action == "enable":
                # First, if this enable did counteract a
                # corresponding _disable_, then it has been _used_.
                if last_ignore:
                    ignore_rule.used = True
                last_ignore = None
                ignore = False
            elif ignore_rule.action == "disable":
                last_ignore = ignore_rule
                ignore = True

        return ignore, last_ignore

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
                    if not ignore.rules or (v.rule_code() in ignore.rules)
                ),
                key=lambda ignore: ignore.line_no,
            )
            # Determine whether to ignore the violation, based on the relevant
            # enable/disable directives.
            ignore, last_ignore = cls._should_ignore_violation_line_range(
                v.line_no, ignore_rule
            )
            if not ignore:
                result.append(v)
            # If there was a previous ignore which mean that we filtered out
            # a violation, then mark it as used.
            elif last_ignore:
                last_ignore.used = True

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

    def generate_warnings_for_unused(self) -> List[SQLBaseError]:
        """Generates warnings for any unused NoQaDirectives."""
        return [
            SQLUnusedNoQaWarning(
                line_no=ignore.line_no,
                line_pos=ignore.line_pos,
                description=f"Unused noqa: {ignore.raw_str!r}",
            )
            for ignore in self._ignore_list
            if not ignore.used
        ]
