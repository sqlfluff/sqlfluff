"""This module integrates SQLFluff with diff_cover's "diff-quality" tool."""

import copy
import json
import logging
import os
import pathlib
import sys
import tempfile
from typing import List

from diff_cover.command_runner import execute, run_command_for_code
from diff_cover.hook import hookimpl as diff_cover_hookimpl
from diff_cover.violationsreporters.base import (
    QualityDriver,
    QualityReporter,
    Violation,
)

logger = logging.getLogger(__name__)


class SQLFluffDriver(QualityDriver):
    """SQLFluff driver for use by SQLFluffViolationReporter."""

    def __init__(self) -> None:
        super().__init__(
            [sys.executable, "-m", "sqlfluff.cli.commands"],
            [".sql"],
            [
                s.encode(sys.getfilesystemencoding())
                for s in ["sqlfluff", "lint", "--format=json"]
            ],
            exit_codes=[0, 1],
        )

    def parse_reports(self, reports) -> None:  # pragma: no cover
        """Parse report output. Not used by SQLFluff."""
        pass

    def installed(self) -> bool:
        """Check if SQLFluff is installed."""
        return run_command_for_code("sqlfluff") == 0


class SQLFluffViolationReporter(QualityReporter):
    """Class that implements diff-quality integration."""

    supported_extensions = ["sql"]

    def __init__(self, **kw) -> None:
        """Calls the base class constructor to set the object's name."""
        super().__init__(SQLFluffDriver(), **kw)

    def violations_batch(self, src_paths):
        """Return a dictionary of Violations recorded in `src_paths`."""
        # Check if SQLFluff is installed.
        if self.driver_tool_installed is None:
            self.driver_tool_installed = self.driver.installed()
        if not self.driver_tool_installed:  # pragma: no cover
            raise OSError(f"{self.driver.name} is not installed")

        if src_paths:
            output = self.reports if self.reports else self._run_sqlfluff(src_paths)
            for o in output:
                # Load and parse SQLFluff JSON output.
                try:
                    report = json.loads(o)
                except json.JSONDecodeError as e:  # pragma: no cover
                    print(f"Error parsing JSON output ({e}): {repr(o)}")
                    raise
                else:
                    for file in report:
                        self.violations_dict[file["filepath"]] = [
                            Violation(v["start_line_no"], v["description"])
                            for v in file["violations"]
                        ]
        else:
            logger.warning("Not running SQLFluff: No files to check")
        return self.violations_dict

    def _run_sqlfluff(self, src_paths) -> List[str]:
        # Prepare the SQLFluff command to run.
        command = copy.deepcopy(self.driver.command)
        if self.options:
            for arg in self.options.split():
                command.append(arg)
        for src_path in src_paths:
            if src_path.endswith(".sql") and os.path.exists(src_path):
                command.append(src_path.encode(sys.getfilesystemencoding()))

        with tempfile.NamedTemporaryFile(
            prefix="sqlfluff-", suffix=".json", delete=False
        ) as f:
            f.close()
            try:
                # Write output to a temporary file. This avoids issues where
                # extraneous SQLFluff or dbt output results in the JSON output
                # being invalid.
                command += ["--write-output", f.name]

                # Run SQLFluff.
                printable_command = " ".join(
                    [
                        (
                            c.decode(sys.getfilesystemencoding())
                            if isinstance(c, bytes)
                            else c
                        )
                        for c in command
                    ]
                )
                logger.warning(f"{printable_command}")
                execute(command, self.driver.exit_codes)
                return [pathlib.Path(f.name).read_text()]
            finally:
                os.remove(f.name)

    def measured_lines(self, src_path: str) -> None:  # pragma: no cover
        """Return list of the lines in src_path that were measured."""


@diff_cover_hookimpl
def diff_cover_report_quality(**kw) -> SQLFluffViolationReporter:
    """Returns the SQLFluff plugin.

    This function is registered as a diff_cover entry point. diff-quality calls
    it in order to "discover" the SQLFluff plugin.

    :return: Object that implements the BaseViolationReporter ABC
    """
    return SQLFluffViolationReporter(**kw)
