import diff_cover
from diff_cover.violationsreporters.base import BaseViolationReporter, Violation

from sqlfluff.cli.commands import get_config, get_linter

class SQLFluffViolationReporter(BaseViolationReporter):
    supported_extensions=['sql']

    def __init__(self):
        super(SQLFluffViolationReporter, self).__init__('sqlfluff')
        self.driver = self

    def violations(self, src_path):
        linter = get_linter(get_config())
        linter.output_func = None
        linted_path = linter.lint_path(src_path)
        result = []
        for violation in linted_path.files[0].violations:
            try:
                # Normal SQLFluff warnings
                message = violation.description
            except AttributeError:
                # Parse errors
                message = violation.message
            result.append(Violation(violation.line_no(), message))
        return result

    def measured_lines(self, src_path):
        return None

    @staticmethod
    def name():
        return 'sqlfluff'

    @staticmethod
    def installed():
        return True


@diff_cover.hookimpl
def diff_cover_report_quality():
    return 'sqlfluff', SQLFluffViolationReporter
