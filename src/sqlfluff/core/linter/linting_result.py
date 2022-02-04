"""Defines the linter class."""

import time
from typing import (
    Any,
    Dict,
    List,
    Optional,
    overload,
    Tuple,
)
from typing_extensions import Literal


from sqlfluff.core.errors import (
    CheckTuple,
    SQLLintError,
    SQLParseError,
    SQLTemplaterError,
)

from sqlfluff.core.timing import TimingSummary

# Classes needed only for type checking
from sqlfluff.core.parser.segments.base import BaseSegment


from sqlfluff.core.linter.linted_dir import LintedDir


class LintingResult:
    """A class to represent the result of a linting operation.

    Notably this might be a collection of paths, all with multiple
    potential files within them.
    """

    def __init__(self) -> None:
        self.paths: List[LintedDir] = []
        self._start_time: float = time.monotonic()
        self.total_time: float = 0.0

    @staticmethod
    def sum_dicts(d1: Dict[str, Any], d2: Dict[str, Any]) -> Dict[str, Any]:
        """Take the keys of two dictionaries and add them."""
        keys = set(d1.keys()) | set(d2.keys())
        return {key: d1.get(key, 0) + d2.get(key, 0) for key in keys}

    @staticmethod
    def combine_dicts(*d: dict) -> dict:
        """Take any set of dictionaries and combine them."""
        dict_buffer: dict = {}
        for dct in d:
            dict_buffer.update(dct)
        return dict_buffer

    def add(self, path: LintedDir) -> None:
        """Add a new `LintedDir` to this result."""
        self.paths.append(path)

    def stop_timer(self):
        """Stop the linting timer."""
        self.total_time = time.monotonic() - self._start_time

    @overload
    def check_tuples(
        self, by_path: Literal[False]
    ) -> List[CheckTuple]:  # pragma: no cover
        """Return a List of CheckTuples when by_path is False."""
        ...

    @overload
    def check_tuples(
        self, by_path: Literal[True]
    ) -> Dict[LintedDir, List[CheckTuple]]:  # pragma: no cover
        """Return a Dict of LintedDir and CheckTuples when by_path is True."""
        ...

    @overload
    def check_tuples(self, by_path: bool = False):  # pragma: no cover
        """Default overload method."""
        ...

    def check_tuples(self, by_path=False):
        """Fetch all check_tuples from all contained `LintedDir` objects.

        Args:
            by_path (:obj:`bool`, optional): When False, all the check_tuples
                are aggregated into one flat list. When True, we return a `dict`
                of paths, each with its own list of check_tuples. Defaults to False.

        """
        if by_path:
            buff: Dict[LintedDir, List[CheckTuple]] = {}
            for path in self.paths:
                buff.update(path.check_tuples(by_path=by_path))
            return buff
        else:
            tuple_buffer: List[CheckTuple] = []
            for path in self.paths:
                tuple_buffer += path.check_tuples()
            return tuple_buffer

    def num_violations(self, **kwargs) -> int:
        """Count the number of violations in the result."""
        return sum(path.num_violations(**kwargs) for path in self.paths)

    def get_violations(self, **kwargs):
        """Return a list of violations in the result."""
        buff = []
        for path in self.paths:
            buff += path.get_violations(**kwargs)
        return buff

    def violation_dict(self, **kwargs):
        """Return a dict of paths and violations."""
        return self.combine_dicts(
            path.violation_dict(**kwargs) for path in self.paths
        )  # pragma: no cover TODO?

    def stats(self) -> Dict[str, Any]:
        """Return a stats dictionary of this result."""
        all_stats: Dict[str, Any] = dict(files=0, clean=0, unclean=0, violations=0)
        for path in self.paths:
            all_stats = self.sum_dicts(path.stats(), all_stats)
        if all_stats["files"] > 0:
            all_stats["avg per file"] = (
                all_stats["violations"] * 1.0 / all_stats["files"]
            )
            all_stats["unclean rate"] = all_stats["unclean"] * 1.0 / all_stats["files"]
        else:
            all_stats["avg per file"] = 0
            all_stats["unclean rate"] = 0
        all_stats["clean files"] = all_stats["clean"]
        all_stats["unclean files"] = all_stats["unclean"]
        all_stats["exit code"] = 65 if all_stats["violations"] > 0 else 0
        all_stats["status"] = "FAIL" if all_stats["violations"] > 0 else "PASS"
        return all_stats

    def timing_summary(self) -> Dict[str, Dict[str, float]]:
        """Return a timing summary."""
        timing = TimingSummary()
        for dir in self.paths:
            for file in dir.files:
                timing.add(file.time_dict)
        return timing.summary()

    def as_records(self) -> List[dict]:
        """Return the result as a list of dictionaries.

        Each record contains a key specifying the filepath, and a list of violations.
        This method is useful for serialization as all objects will be builtin python
        types (ints, strs).
        """
        return [
            {
                "filepath": path,
                "violations": sorted(
                    # Sort violations by line and then position
                    (v.get_info_dict() for v in violations),
                    # The tuple allows sorting by line number, then position, then code
                    key=lambda v: (v["line_no"], v["line_pos"], v["code"]),
                ),
            }
            for LintedDir in self.paths
            for path, violations in LintedDir.violation_dict().items()
            if violations
        ]

    def persist_changes(self, formatter, **kwargs) -> dict:
        """Run all the fixes for all the files and return a dict."""
        return self.combine_dicts(
            *(
                path.persist_changes(formatter=formatter, **kwargs)
                for path in self.paths
            )
        )

    @property
    def tree(self) -> Optional[BaseSegment]:  # pragma: no cover
        """A convenience method for when there is only one file and we want the tree."""
        if len(self.paths) > 1:
            raise ValueError(
                ".tree() cannot be called when a LintingResult contains more than one "
                "path."
            )
        return self.paths[0].tree

    TMP_PRS_ERROR_TYPES = (SQLTemplaterError, SQLParseError)

    def count_tmp_prs_errors(self) -> Tuple[int, int]:
        """Count templating or parse errors before and after filtering."""
        total_errors = self.num_violations(
            types=self.TMP_PRS_ERROR_TYPES, filter_ignore=False
        )
        num_filtered_errors = 0
        for linted_dir in self.paths:
            for linted_file in linted_dir.files:
                num_filtered_errors += linted_file.num_violations(
                    types=self.TMP_PRS_ERROR_TYPES
                )
        return total_errors, num_filtered_errors

    def discard_fixes_for_lint_errors_in_files_with_tmp_or_prs_errors(self) -> None:
        """Discard lint fixes for files with templating or parse errors."""
        total_errors = self.num_violations(
            types=self.TMP_PRS_ERROR_TYPES, filter_ignore=False
        )
        if total_errors:
            for linted_dir in self.paths:
                for linted_file in linted_dir.files:
                    num_errors = linted_file.num_violations(
                        types=self.TMP_PRS_ERROR_TYPES, filter_ignore=False
                    )
                    if num_errors:
                        # File has errors. Discard all the SQLLintError fixes:
                        # they are potentially unsafe.
                        for violation in linted_file.violations:
                            if isinstance(violation, SQLLintError):
                                violation.fixes = []
