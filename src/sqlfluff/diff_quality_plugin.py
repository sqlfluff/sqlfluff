"""This module integrates SQLFluff with diff_cover's "diff-quality" tool."""
import copy
import json
import logging
import os
import sys

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

    def __init__(self):
        super().__init__(
            "sqlfluff",
            [".sql"],
            [
                s.encode(sys.getfilesystemencoding())
                for s in ["sqlfluff", "lint", "--format=json"]
            ],
            exit_codes=[0, 1],
        )

    def parse_reports(self, reports):
        """Parse report output. Not used by SQLFluff."""
        pass

    def installed(self):
        """Check if SQLFluff is installed."""
        return run_command_for_code("sqlfluff") == 0


class SQLFluffViolationReporter(QualityReporter):
    """Class that implements diff-quality integration."""

    supported_extensions = ["sql"]

    def __init__(self, reports=None, options=None):
        """Calls the base class constructor to set the object's name."""
        super().__init__(SQLFluffDriver())

    def violations_batch(self, src_paths):
        """Return a dictionary of Violations recorded in `src_paths`."""
        # Check if SQLFluff is installed.
        if self.driver_tool_installed is None:
            self.driver_tool_installed = self.driver.installed()
        if not self.driver_tool_installed:
            raise OSError(f"{self.driver.name} is not installed")

        # Prepare the SQLFluff command to run.
        command = copy.deepcopy(self.driver.command)
        if self.options:
            for arg in self.options.split():
                command.append(arg)
        for src_path in src_paths:
            if src_path.endswith(".sql") and os.path.exists(src_path):
                command.append(src_path.encode(sys.getfilesystemencoding()))

        # Run SQLFluff.
        logger.warning(
            f"{' '.join([c.decode(sys.getfilesystemencoding()) for c in command])}"
        )
        output = execute(command, self.driver.exit_codes)
        if self.driver.output_stderr:
            output = output[1]
        else:
            output = output[0]

        # Parse the output.
        report = json.loads(output)
        for file in report:
            self.violations_dict[file["filepath"]] = [
                Violation(v["line_no"], v["description"]) for v in file["violations"]
            ]
        return self.violations_dict

    def measured_lines(self, src_path: str) -> None:  # pragma: no cover
        """Return list of the lines in src_path that were measured."""


@diff_cover_hookimpl
def diff_cover_report_quality() -> SQLFluffViolationReporter:
    """Returns the SQLFluff plugin.

    This function is registered as a diff_cover entry point. diff-quality calls
    it in order to "discover" the SQLFluff plugin.

    :return: Object that implements the BaseViolationReporter ABC
    """
    return SQLFluffViolationReporter()
