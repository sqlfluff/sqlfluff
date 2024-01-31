"""Defines the LintedDir class.

This stores the idea of a collection of linted files at a single start path

"""

from typing import Any, Dict, List, Optional, Tuple, Union, overload

from typing_extensions import Literal, TypedDict

from sqlfluff.core.errors import CheckTuple
from sqlfluff.core.linter.linted_file import LintedFile
from sqlfluff.core.parser.segments.base import BaseSegment

LintingRecord = TypedDict("LintingRecord", {"filepath": str, "violations": List[dict]})


class LintedDir:
    """A class to store the idea of a collection of linted files at a single start path.

    A LintedDir may contain files in subdirectories, but they all share
    a common root.

    Importantly, this class also abstracts away from the given LintedFile
    object and allows us to either _keep_ those objects for later use, or
    extract the results from them and allow the original object to be discarded
    and save memory overhead if not required.
    """

    def __init__(self, path: str, retain_files: bool = True) -> None:
        self.files: List[LintedFile] = []
        self.path: str = path
        self.retain_files: bool = retain_files
        # Records
        self._records: List[LintingRecord] = []
        # Stats
        self._num_files: int = 0
        self._num_clean: int = 0
        self._num_unclean: int = 0
        self._num_violations: int = 0
        # Timing
        self.step_timings: List[Dict[str, float]] = []
        self.rule_timings: List[Tuple[str, str, float]] = []

    def add(self, file: LintedFile) -> None:
        """Add a file to this path.

        This function _always_ updates the metadata tracking, but may
        or may not persist the `file` object itself depending on the
        `retain_files` argument given on instantiation.
        """
        # Generate serialised violations.
        violation_records = sorted(
            # Keep the warnings
            (v.to_dict() for v in file.get_violations(filter_warning=False)),
            # The tuple allows sorting by line number, then position, then code
            key=lambda v: (v["start_line_no"], v["start_line_pos"], v["code"]),
        )

        # Persist the records if there are violations.
        if violation_records:
            self._records.append(
                {
                    "filepath": file.path,
                    "violations": violation_records,
                }
            )

        # Update the stats
        self._num_files += 1
        if file.is_clean():
            self._num_clean += 1
        else:
            self._num_unclean += 1
        self._num_violations = file.num_violations()

        # Append timings if present
        if file.timings:
            self.step_timings.append(file.timings.step_timings)
            self.rule_timings.extend(file.timings.rule_timings)

        # Finally, if set to persist files, do that.
        if self.retain_files:
            self.files.append(file)

    @overload
    def check_tuples(self, by_path: Literal[False]) -> List[CheckTuple]:
        """Return a List of CheckTuples when by_path is False."""

    @overload
    def check_tuples(self, by_path: Literal[True]) -> Dict[str, List[CheckTuple]]:
        """Return a Dict of paths and CheckTuples when by_path is True."""

    @overload
    def check_tuples(self, by_path: bool = False):
        """Default overload method."""

    def check_tuples(
        self, by_path=False, raise_on_non_linting_violations=True
    ) -> Union[List[CheckTuple], Dict[str, List[CheckTuple]]]:
        """Compress all the tuples into one list.

        NB: This is a little crude, as you can't tell which
        file the violations are from. Good for testing though.
        For more control set the `by_path` argument to true.
        """
        assert self.retain_files, "cannot `check_tuples()` without `retain_files`"
        if by_path:
            return {
                file.path: file.check_tuples(
                    raise_on_non_linting_violations=raise_on_non_linting_violations
                )
                for file in self.files
            }
        else:
            tuple_buffer: List[CheckTuple] = []
            for file in self.files:
                tuple_buffer += file.check_tuples(
                    raise_on_non_linting_violations=raise_on_non_linting_violations
                )
            return tuple_buffer

    def num_violations(self, **kwargs) -> int:
        """Count the number of violations in the path."""
        return sum(file.num_violations(**kwargs) for file in self.files)

    def get_violations(self, **kwargs) -> list:
        """Return a list of violations in the path."""
        buff: list = []
        for file in self.files:
            buff += file.get_violations(**kwargs)
        return buff

    def violation_dict(self, **kwargs) -> Dict[str, list]:
        """Return a dict of violations by file path."""
        return {file.path: file.get_violations(**kwargs) for file in self.files}

    def as_records(self) -> List[LintingRecord]:
        """Return the result as a list of dictionaries.

        Each record contains a key specifying the filepath, and a list of violations.
        This method is useful for serialization as all objects will be builtin python
        types (ints, strs).
        """
        return self._records

    def stats(self) -> Dict[str, int]:
        """Return a dict containing linting stats about this path."""
        return {
            "files": self._num_files,
            "clean": self._num_clean,
            "unclean": self._num_unclean,
            "violations": self._num_violations,
        }

    def persist_changes(
        self, formatter: Any = None, fixed_file_suffix: str = ""
    ) -> Dict[str, Union[bool, str]]:
        """Persist changes to files in the given path.

        This also logs the output as we go using the formatter if present.
        """
        assert self.retain_files, "cannot `persist_changes()` without `retain_files`"
        # Run all the fixes for all the files and return a dict
        buffer: Dict[str, Union[bool, str]] = {}
        for file in self.files:
            buffer[file.path] = file.persist_tree(
                suffix=fixed_file_suffix, formatter=formatter
            )
        return buffer

    @property
    def tree(self) -> Optional[BaseSegment]:
        """A convenience method for when there is only one file and we want the tree."""
        assert self.retain_files, ".tree() cannot be called if `retain_files` is False."
        assert (
            len(self.files) == 1
        ), ".tree() cannot be called when a LintedDir contains more than one file."
        assert (
            self.files
        ), "LintedDir has no parsed files. There is probably a parsing error."
        return self.files[0].tree
