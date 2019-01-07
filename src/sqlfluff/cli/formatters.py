""" Defines the formatters for the CLI """


from six import StringIO

from .helpers import colorize, cli_table, get_package_version, get_python_version


def format_filename(filename, success=False, verbose=0, success_text='PASS'):
    status_string = colorize(
        success_text if success else 'FAIL',
        'green' if success else 'red')
    return (
        "== ["
        + colorize("{0}".format(filename), 'lightgrey')
        + "] " + status_string)


def format_violation(violation, verbose=0):
    return (
        colorize(
            "L:{0:4d} | P:{1:4d} | {2} |".format(
                violation.chunk.line_no,
                violation.chunk.start_pos + 1,
                violation.rule.code),
            'blue')
        + " {0}".format(violation.rule.description)
    )


def format_fix(fix, verbose=0):
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


def format_violations(violations, verbose=0):
    # Violations should be a dict
    keys = sorted(violations.keys())
    text_buffer = StringIO()
    for key in keys:
        # Success is having no violations
        success = len(violations[key]) == 0

        # Only print the filename if it's either a failure or verbosity > 1
        if verbose > 1 or not success:
            text_buffer.write(format_filename(key, success=success, verbose=verbose))
            text_buffer.write('\n')

        # If we have violations, print them
        if not success:
            # first sort by position
            s = sorted(violations[key], key=lambda v: v.chunk.start_pos)
            # the primarily sort by line no
            s = sorted(s, key=lambda v: v.chunk.line_no)
            for violation in s:
                text_buffer.write(format_violation(violation, verbose=verbose))
                text_buffer.write('\n')
    return text_buffer.getvalue()


def format_linting_stats(result, verbose=0):
    """ Assume we're passed a LintingResult """
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


def format_linting_violations(result, verbose=0):
    """ Assume we're passed a LintingResult """
    text_buffer = StringIO()
    for path in result.paths:
        if verbose > 0:
            text_buffer.write('=== [ path: {0} ] ===\n'.format(colorize(path.path, 'lightgrey')))
        text_buffer.write(format_violations(path.violations(), verbose=verbose))

    str_buffer = text_buffer.getvalue()
    # Remove the trailing newline if there is one
    if len(str_buffer) > 0 and str_buffer[-1] == '\n':
        str_buffer = str_buffer[:-1]
    return str_buffer


def format_linting_fixes(fixes, verbose=0):
    """ Assume we're passed a dict of fix results """
    text_buffer = StringIO()
    for file in fixes:
        if len(fixes[file]) > 0:
            fix_buff = fixes[file]
            success = all([fix.success for fix in fix_buff])
            text_buffer.write(format_filename(file, success=success, verbose=verbose, success_text='FIXED'))
            text_buffer.write('\n')
            for fix in fix_buff:
                text_buffer.write(format_fix(fix, verbose=verbose))
                text_buffer.write('\n')
    return text_buffer.getvalue()


def format_linting_result(result, verbose=0):
    """ Assume we're passed a LintingResult """
    text_buffer = StringIO()
    if verbose >= 1:
        text_buffer.write("==== readout ====\n")
    text_buffer.write(format_linting_violations(result, verbose=verbose))
    text_buffer.write('\n')
    text_buffer.write(format_linting_stats(result, verbose=verbose))
    return text_buffer.getvalue()


def format_config(linter, verbose=0):
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
        if linter.rule_whitelist:
            text_buffer.write(cli_table([('rules', ', '.join(linter.rule_whitelist))], col_width=41))
    return text_buffer.getvalue()


def format_rules(linter, verbose=0):
    text_buffer = StringIO()
    text_buffer.write("==== sqlfluff - rules ====\n")
    text_buffer.write(
        cli_table(
            linter.rule_tuples(), col_width=80,
            cols=1, label_color='blue', val_align='left'))
    return text_buffer.getvalue()
