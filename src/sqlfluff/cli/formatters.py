"""Defines the formatters for the CLI."""


from io import StringIO

from .helpers import colorize, cli_table, get_package_version, get_python_version, pad_line
from ..errors import SQLBaseError


def format_filename(filename, success=False, verbose=0, success_text='PASS'):
    """Format filenames."""
    if isinstance(success, str):
        status_string = success
    else:
        status_string = colorize(
            success_text if success else 'FAIL',
            'green' if success else 'red')
    return (
        "== ["
        + colorize("{0}".format(filename), 'lightgrey')
        + "] " + status_string)


def format_dialect_warning():
    """Output a warning for parsing errors found on the ansi dialect."""
    return colorize(
        ("WARNING: Parsing errors found and dialect is set to "
         "'ansi'. Have you configured your dialect?"),
        'lightgrey'
    )


def format_path(path):
    """Format paths."""
    return '=== [ path: {0} ] ===\n'.format(colorize(path, 'lightgrey'))


def split_string_on_spaces(s, line_length=100):
    """Split a string into lines based on whitespace."""
    line_buff = []
    str_buff = ""
    for token in s.split():
        # Can we put this token on this line without going over?
        if str_buff:
            if len(str_buff) + len(token) > line_length:
                line_buff.append(str_buff)
                str_buff = token
            else:
                str_buff += ' ' + token
        else:
            # In the case that the buffer is already empty, add it without checking,
            # otherwise there might be things that we might never.
            str_buff = token
    # If we have left over buff, add it in
    if str_buff:
        line_buff.append(str_buff)
    return line_buff


def format_violation(violation, verbose=0, max_line_length=90):
    """Format a violation."""
    if isinstance(violation, SQLBaseError):
        code, line, pos, desc = violation.get_info_tuple()
        if line is not None:
            line_elem = '{0:4d}'.format(line)
        else:
            line_elem = '   -'
        if pos is not None:
            pos_elem = '{0:4d}'.format(pos)
        else:
            pos_elem = '   -'
    else:
        raise ValueError("Unexpected violation format: {0}".format(violation))

    if violation.ignore:
        desc = 'IGNORE: ' + desc

    split_desc = split_string_on_spaces(desc, line_length=max_line_length - 25)

    out_buff = ""
    for idx, line in enumerate(split_desc):
        if idx == 0:
            out_buff += colorize(
                "L:{0} | P:{1} | {2} | ".format(line_elem, pos_elem, code.rjust(4)),
                # Grey out the violation if we're ignoring it.
                'lightgrey' if violation.ignore else 'blue'
            )
        else:
            out_buff += '\n' + (' ' * 23) + colorize("| ", 'lightgrey' if violation.ignore else 'blue')
        out_buff += line
    return out_buff


def format_file_violations(fname, res, verbose=0, max_line_length=90):
    """Format a set of violations in a `LintingResult`."""
    text_buffer = StringIO()
    # Success is having no violations (which aren't ignored)
    success = sum(int(not violation.ignore) for violation in res) == 0

    # Only print the filename if it's either a failure or verbosity > 1
    if verbose > 1 or not success:
        text_buffer.write(format_filename(fname, success=success, verbose=verbose))
        text_buffer.write('\n')

    # If we have violations, print them
    if not success:
        # sort by position in file
        s = sorted(res, key=lambda v: v.char_pos())
        for violation in s:
            text_buffer.write(
                format_violation(
                    violation, verbose=verbose,
                    max_line_length=max_line_length))
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


def format_config_vals(config_vals):
    """Format an iterable of config values from a config object."""
    text_buffer = StringIO()
    for i, k, v in config_vals:
        val = '' if v is None else str(v)
        text_buffer.write(("    " * i) + colorize(pad_line(str(k) + ':', 20, 'left'), color='lightgrey') + pad_line(val, 20, 'left') + '\n')
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
        text_buffer.write(cli_table(config_content, col_width=25))
        text_buffer.write("\n")
        if linter.config.get('rule_whitelist'):
            text_buffer.write(cli_table([('rules', ', '.join(linter.config.get('rule_whitelist')))], col_width=41))
        if verbose > 1:
            text_buffer.write("== Raw Config:\n")
            text_buffer.write(format_config_vals(linter.config.iter_vals()))
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
