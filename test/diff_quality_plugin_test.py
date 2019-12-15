from sqlfluff import diff_quality_plugin


def test_diff_quality_plugin():
    violation_reporter = diff_quality_plugin.diff_cover_report_quality()
    violations = violation_reporter.violations(
        'test/fixtures/linter/indentation_errors.sql')
    assert isinstance(violations, list)
    assert len(violations) > 0
    violations_lines = {v.line for v in violations}
    for line in range(2, 7):
        assert line in violations_lines
