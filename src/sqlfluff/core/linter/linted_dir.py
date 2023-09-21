"""Defines the LintedDir class.

This stores the idea of a collection of linted files at a single start path

"""

from typing import Any, Dict, List, Optional, Union, overload

from typing_extensions import Literal

from sqlfluff.core.errors import CheckTuple
from sqlfluff.core.linter.linted_file import LintedFile
from sqlfluff.core.parser.segments.base import BaseSegment


class LintedDir:
    """A class to store the idea of a collection of linted files at a single start path.

    A LintedDir may contain files in subdirectories, but they all share
    a common root.
    """

    def __init__(self, path: str) -> None:
        self.files: List[LintedFile] = []
        self.path: str = path

    def add(self, file: LintedFile) -> None:
        """Add a file to this path."""
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

    def stats(self) -> Dict[str, int]:
        """Return a dict containing linting stats about this path."""
        return dict(
            files=len(self.files),
            clean=sum(file.is_clean() for file in self.files),
            unclean=sum(not file.is_clean() for file in self.files),
            violations=sum(file.num_violations() for file in self.files),
        )

    def persist_changes(
        self, formatter: Any = None, fixed_file_suffix: str = ""
    ) -> Dict[str, Union[bool, str]]:
        """Persist changes to files in the given path.

        This also logs the output as we go using the formatter if present.
        """
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
        if len(self.files) > 1:  # pragma: no cover
            raise ValueError(
                ".tree() cannot be called when a LintedDir contains more than one file."
            )
        elif not self.files:  # pragma: no cover
            raise ValueError(
                "LintedDir has no parsed files. There is probably a parsing error."
            )
        return self.files[0].tree
