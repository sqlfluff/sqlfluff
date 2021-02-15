"""This module integrates SQLFluff with diff_cover's "diff-quality" tool."""
from diff_cover.hook import hookimpl as diff_cover_hookimpl
from diff_cover.violationsreporters.base import BaseViolationReporter, Violation

from sqlfluff.core import FluffConfig, Linter


class SQLFluffViolationReporter(BaseViolationReporter):
    """Class that implements diff-quality integration."""

    supported_extensions = ["sql"]

    def __init__(self):
        """Calls the base class constructor to set the object's name."""
        super(SQLFluffViolationReporter, self).__init__("sqlfluff")

    @staticmethod
    def violations(src_path):
        """Return list of violations.

        Given the path to a .sql file, analyze it and return a list of
        violations (i.e. formatting or style issues).

        :param src_path:
        :return: list of Violation
        """
        linter = Linter(config=FluffConfig.from_root())
        linted_path = linter.lint_path(src_path, ignore_non_existent_files=True)
        result = []
        for violation in linted_path.get_violations():
            try:
                # Normal SQLFluff warnings
                message = violation.description
            except AttributeError:
                # Parse errors
                message = str(violation)
            result.append(Violation(violation.line_no(), message))
        return result


@diff_cover_hookimpl
def diff_cover_report_quality():
    """Returns the SQLFluff plugin.

    This function is registered as a diff_cover entry point. diff-quality calls
    it in order to "discover" the SQLFluff plugin.

    :return: Object that implements the BaseViolationReporter ABC
    """
    return SQLFluffViolationReporter()
