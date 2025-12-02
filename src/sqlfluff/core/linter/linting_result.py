"""Defines the linter class."""

import csv
import time
from collections.abc import Iterable, Mapping
from typing import TYPE_CHECKING, Any, Optional, TypeVar, Union

from sqlfluff.core.errors import CheckTuple, SQLBaseError
from sqlfluff.core.formatter import FormatterInterface
from sqlfluff.core.linter.linted_dir import LintedDir, LintingRecord
from sqlfluff.core.timing import RuleTimingSummary, TimingSummary

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.segments.base import BaseSegment


def sum_dicts(d1: Mapping[str, int], d2: Mapping[str, int]) -> dict[str, int]:
    """Take the keys of two dictionaries and add their values."""
    keys = set(d1.keys()) | set(d2.keys())
    return {key: d1.get(key, 0) + d2.get(key, 0) for key in keys}


T = TypeVar("T")


def combine_dicts(*d: dict[str, T]) -> dict[str, T]:
    """Take any set of dictionaries and combine them."""
    dict_buffer: dict[str, T] = {}
    for dct in d:
        dict_buffer.update(dct)
    return dict_buffer


class LintingResult:
    """A class to represent the result of a linting operation.

    Notably this might be a collection of paths, all with multiple
    potential files within them.
    """

    def __init__(self) -> None:
        self.paths: list[LintedDir] = []
        self._start_time: float = time.monotonic()
        self.total_time: float = 0.0

    def add(self, path: LintedDir) -> None:
        """Add a new `LintedDir` to this result."""
        self.paths.append(path)

    def stop_timer(self) -> None:
        """Stop the linting timer."""
        self.total_time = time.monotonic() - self._start_time

    def check_tuples(
        self, raise_on_non_linting_violations: bool = True
    ) -> list[CheckTuple]:
        """Fetch all check_tuples from all contained `LintedDir` objects.

        Returns:
            A list of check tuples.
        """
        return [
            t
            for path in self.paths
            for t in path.check_tuples(
                raise_on_non_linting_violations=raise_on_non_linting_violations
            )
        ]

    def check_tuples_by_path(self) -> dict[str, list[CheckTuple]]:
        """Fetch all check_tuples from all contained `LintedDir` objects.

        Returns:
            A dict, with lists of tuples grouped by path.
        """
        buff: dict[str, list[CheckTuple]] = {}
        for path in self.paths:
            buff.update(path.check_tuples_by_path())
        return buff

    def num_violations(
        self,
        types: Optional[Union[type[SQLBaseError], Iterable[type[SQLBaseError]]]] = None,
        fixable: Optional[bool] = None,
    ) -> int:
        """Count the number of violations in the result."""
        return sum(
            path.num_violations(types=types, fixable=fixable) for path in self.paths
        )

    def get_violations(
        self, rules: Optional[Union[str, tuple[str, ...]]] = None
    ) -> list[SQLBaseError]:
        """Return a list of violations in the result."""
        return [v for path in self.paths for v in path.get_violations(rules=rules)]

    def stats(
        self, fail_code: int, success_code: int
    ) -> dict[str, Union[int, float, str]]:
        """Return a stats dictionary of this result."""
        # Add up all the counts for each file.
        # NOTE: Having a more strictly typed dict for the counts also helps with
        # typing later in this method.
        counts: dict[str, int] = dict(files=0, clean=0, unclean=0, violations=0)
        for path in self.paths:
            counts = sum_dicts(path.stats(), counts)
        # Set up the overall dictionary.
        all_stats: dict[str, Union[int, float, str]] = {}
        all_stats.update(counts)
        if counts["files"] > 0:
            all_stats["avg per file"] = counts["violations"] * 1.0 / counts["files"]
            all_stats["unclean rate"] = counts["unclean"] * 1.0 / counts["files"]
        else:
            all_stats["avg per file"] = 0
            all_stats["unclean rate"] = 0
        all_stats["clean files"] = all_stats["clean"]
        all_stats["unclean files"] = all_stats["unclean"]
        all_stats["exit code"] = fail_code if counts["violations"] > 0 else success_code
        all_stats["status"] = "FAIL" if counts["violations"] > 0 else "PASS"
        return all_stats

    def timing_summary(self) -> dict[str, dict[str, Any]]:
        """Return a timing summary."""
        timing = TimingSummary()
        rules_timing = RuleTimingSummary()
        for dir in self.paths:
            # Add timings from cached values.
            # NOTE: This is so we don't rely on having the raw file objects any more.
            for t in dir.step_timings:
                timing.add(t)
            rules_timing.add(dir.rule_timings)
        return {**timing.summary(), **rules_timing.summary()}

    def persist_timing_records(self, filename: str) -> None:
        """Persist the timing records as a csv for external analysis."""
        meta_fields = [
            "path",
            "source_chars",
            "templated_chars",
            "segments",
            "raw_segments",
        ]
        timing_fields = ["templating", "lexing", "parsing", "linting"]

        # Iterate through all the files to get rule timing information so
        # we know what headings we're going to need.
        rule_codes: set[str] = set()
        for path in self.paths:
            for record in path.as_records():
                if "timings" not in record:  # pragma: no cover
                    continue
                rule_codes.update(record["timings"].keys())

        rule_codes -= set(timing_fields)

        with open(filename, "w", newline="") as f:
            writer = csv.DictWriter(
                # Metadata first, then step timings and then _sorted_ rule codes.
                f,
                fieldnames=meta_fields + timing_fields + sorted(rule_codes),
            )

            # Write the header
            writer.writeheader()

            for path in self.paths:
                for record in path.as_records():
                    if "timings" not in record:  # pragma: no cover
                        continue

                    writer.writerow(
                        {
                            "path": record["filepath"],
                            **record["statistics"],  # character and segment lengths.
                            **record["timings"],  # step and rule timings.
                        }
                    )

    def as_records(self) -> list[LintingRecord]:
        """Return the result as a list of dictionaries.

        Each record contains a key specifying the filepath, and a list of violations.
        This method is useful for serialization as all objects will be builtin python
        types (ints, strs).
        """
        return sorted(
            (record for linted_dir in self.paths for record in linted_dir.as_records()),
            # Sort records by filename
            key=lambda record: record["filepath"],
        )

    def persist_changes(
        self, formatter: Optional[FormatterInterface], fixed_file_suffix: str = ""
    ) -> dict[str, Union[bool, str]]:
        """Run all the fixes for all the files and return a dict."""
        return combine_dicts(
            *(
                path.persist_changes(
                    formatter=formatter, fixed_file_suffix=fixed_file_suffix
                )
                for path in self.paths
            )
        )

    @property
    def tree(self) -> Optional["BaseSegment"]:  # pragma: no cover
        """A convenience method for when there is only one file and we want the tree."""
        if len(self.paths) > 1:
            raise ValueError(
                ".tree() cannot be called when a LintingResult contains more than one "
                "path."
            )
        return self.paths[0].tree

    def count_tmp_prs_errors(self) -> tuple[int, int]:
        """Count templating or parse errors before and after filtering."""
        total_errors = sum(path.num_unfiltered_tmp_prs_errors for path in self.paths)
        num_filtered_errors = sum(path.num_tmp_prs_errors for path in self.paths)
        return total_errors, num_filtered_errors

    def discard_fixes_for_lint_errors_in_files_with_tmp_or_prs_errors(self) -> None:
        """Discard lint fixes for files with templating or parse errors."""
        for path in self.paths:
            path.discard_fixes_for_lint_errors_in_files_with_tmp_or_prs_errors()
