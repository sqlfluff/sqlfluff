"""Defines the formatters for the CLI."""


from six import StringIO

from .helpers import colorize, cli_table, get_package_version, get_python_version
from ..errors import SQLBaseError


def format_filename(filename, success=False, verbose=0, success_text='PASS'):
    """Format filenames."""
    status_string = colorize(
        success_text if success else 'FAIL',
        'green' if success else 'red')
    return (
        "== ["
        + colorize("{0}".format(filename), 'lightgrey')
        + "] " + status_string)


def format_path(path):
    """Format paths."""
    return '=== [ path: {0} ] ===\n'.format(colorize(path, 'lightgrey'))


def format_violation(violation, verbose=0):
    """Format a violation."""
    if isinstance(violation, SQLBaseError):
        code, line, pos, desc = violation.get_info_tuple()
    elif hasattr('chunk', violation):
        code = violation.rule.code
        line = violation.chunk.line_no
        pos = violation.chunk.start_pos + 1
        desc = violation.rule.description
    else:
        raise ValueError("Unexpected violation format: {0}".format(violation))

    return (
        colorize(
            "L:{0:4d} | P:{1:4d} | {2} |".format(line, pos, code),
            'blue')
        + " {0}".format(desc)
    )


def format_fix(fix, verbose=0):
    """Format a fix."""
    return (
        colorize(
            "L:{0:4d} | P:{1:4d} | {2} | ".format(
                fix.violation.chunk.line_no,
                fix.violation.chunk.start_pos + 1,
                fix.violation.rule.code),
            'blue')
        + (colorize("SUCCESS", 'green') if fix.success else colorize("FAIL", 'red'))
        + " | "
        + " {0}".format(fix.detail or "")
    )


def format_file_violations(fname, res, verbose=0):
    """Format a set of violations in a `LintingResult`."""
    text_buffer = StringIO()
    # Success is having no violations
    success = len(res) == 0

    # Only print the filename if it's either a failure or verbosity > 1
    if verbose > 1 or not success:
        text_buffer.write(format_filename(fname, success=success, verbose=verbose))
        text_buffer.write('\n')

    # If we have violations, print them
    if not success:
        # sort by position in file
        s = sorted(res, key=lambda v: v.char_pos())
        for violation in s:
            text_buffer.write(format_violation(violation, verbose=verbose))
            text_buffer.write('\n')
    str_buffer = text_buffer.getvalue()
    # Remove the trailing newline if there is one
    if len(str_buffer) > 0 and str_buffer[-1] == '\n':
        str_buffer = str_buffer[:-1]
    return str_buffer


def format_path_violations(violations, verbose=0):
    """Format a set of violations from a dict of paths and violations."""
    # Violations should be a dict
    keys = sorted(violations.keys())
    text_buffer = StringIO()
    for key in keys:
        text_buffer.write(format_file_violations(key, violations[key], verbose=verbose))
        text_buffer.write('\n')
    str_buffer = text_buffer.getvalue()
    # Remove the trailing newline if there is one
    if len(str_buffer) > 0 and str_buffer[-1] == '\n':
        str_buffer = str_buffer[:-1]
    return str_buffer


def format_linting_stats(result, verbose=0):
    """Format a set of stats given a `LintingResult`."""
    text_buffer = StringIO()
    all_stats = result.stats()
    if verbose >= 1:
        text_buffer.write("==== summary ====\n")
        if verbose >= 2:
            output_fields = ['files', 'violations', 'clean files', 'unclean files',
                             'avg per file', 'unclean rate', 'status']
            special_formats = {'unclean rate': "{0:.0%}"}
        else:
            output_fields = ['violations', 'status']
            special_formats = {}
        # Generate content tuples, applying special formats for some fields
        summary_content = [
            (key, special_formats[key].format(all_stats[key])
                if key in special_formats
                else all_stats[key]) for key in output_fields]
        # Render it all as a table
        text_buffer.write(cli_table(summary_content, max_label_width=14))
    return text_buffer.getvalue()


def format_linting_path(p, verbose=0):
    """Format a linting path."""
    text_buffer = StringIO()
    if verbose > 0:
        text_buffer.write(format_path(p))
    return text_buffer.getvalue()


def _format_path_linting_violations(result, verbose=0):
    text_buffer = StringIO()
    text_buffer.write(format_linting_path(result.path))
    text_buffer.write(format_path_violations(result.violations(), verbose=verbose))
    return text_buffer.getvalue()


def format_linting_violations(result, verbose=0):
    """Format a set of violations given a `LintingResult`."""
    text_buffer = StringIO()
    if hasattr(result, 'paths'):
        # We've got a full path
        for path in result.paths:
            text_buffer.write(_format_path_linting_violations(path, verbose=verbose))
    else:
        # We've got an individual
        text_buffer.write(_format_path_linting_violations(result, verbose=verbose))
    return text_buffer.getvalue()


def format_linting_result_header(verbose=0):
    """Format the header of a linting result output."""
    text_buffer = StringIO()
    if verbose >= 1:
        text_buffer.write("==== readout ====\n")
    return text_buffer.getvalue()


def format_linting_result_footer(result, verbose=0):
    """Format the footer of a linting result output given a `LintingResult`."""
    text_buffer = StringIO()
    text_buffer.write('\n')
    text_buffer.write(format_linting_stats(result, verbose=verbose))
    return text_buffer.getvalue()


def format_linting_result(result, verbose=0):
    """Format the output of a `LintingResult`."""
    text_buffer = StringIO()
    text_buffer.write(format_linting_result_header(verbose=verbose))
    text_buffer.write(format_linting_violations(result, verbose=verbose))
    text_buffer.write(format_linting_result_footer(result, verbose=verbose))
    return text_buffer.getvalue()


def format_config(linter, verbose=0):
    """Format the config of a `Linter`."""
    text_buffer = StringIO()
    # Only show version information if verbosity is high enough
    if verbose > 0:
        text_buffer.write("==== sqlfluff ====\n")
        config_content = [
            ('sqlfluff', get_package_version()),
            ('python', get_python_version()),
            ('dialect', linter.dialect.name),
            ('verbosity', verbose)
        ]
        text_buffer.write(cli_table(config_content))
        text_buffer.write("\n")
        if linter.config.get('rule_whitelist'):
            text_buffer.write(cli_table([('rules', ', '.join(linter.config.get('rule_whitelist')))], col_width=41))
    return text_buffer.getvalue()


def format_rules(linter, verbose=0):
    """Format the a set of rules given a `Linter`."""
    text_buffer = StringIO()
    text_buffer.write("==== sqlfluff - rules ====\n")
    text_buffer.write(
        cli_table(
            linter.rule_tuples(), col_width=80,
            cols=1, label_color='blue', val_align='left'))
    return text_buffer.getvalue()
