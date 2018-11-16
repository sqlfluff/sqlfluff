""" Defines the formatters for the CLI """


from six import StringIO

from .helpers import colorize


def format_filename(filename, success=False, color=True, verbose=0):
    if color:
        fname_col = 'lightgrey'
        status_col = 'green' if success else 'red'
    else:
        fname_col = None
        status_col = None

    return (
        "== ["
        + colorize("{0}".format(filename), fname_col)
        + "] "
        + colorize('PASS' if success else 'FAIL', status_col)
    )


def format_violation(violation, color=True, verbose=0):
    return (
        colorize(
            "L:{0:4d} | P:{1:4d} | {2} |".format(
                violation.chunk.line_no,
                violation.chunk.start_pos + 1,
                violation.rule.code),
            'blue' if color else None)
        + " {0}".format(violation.rule.description)
    )


def format_violations(violations, color=True, verbose=0):
    # Violations should be a dict
    keys = sorted(violations.keys())
    text_buffer = StringIO()
    for key in keys:
        # Success is having no violations
        success = len(violations[key]) == 0

        # Only print the filename if it's either a failure or verbosity > 1
        if verbose > 1 or not success:
            text_buffer.write(format_filename(key, success=success, color=color, verbose=verbose))
            text_buffer.write('\n')

        # If we have violations, print them
        if not success:
            # first sort by position
            s = sorted(violations[key], key=lambda v: v.chunk.start_pos)
            # the primarily sort by line no
            s = sorted(s, key=lambda v: v.chunk.line_no)
            for violation in s:
                text_buffer.write(format_violation(violation, color=color, verbose=verbose))
                text_buffer.write('\n')
    str_buffer = text_buffer.getvalue()
    # Remove the trailing newline if there is one
    if str_buffer[-1] == '\n':
        str_buffer = str_buffer[:-1]
    return str_buffer


def format_linting_result(result, color=True, verbose=0):
    """ Assume we're passed a LintingResult """
    text_buffer = StringIO()
    for path in result.paths:
        if verbose > 0:
            text_buffer.write('=== [ path: {0} ] ===\n'.format(colorize(path.path, 'lightgrey')))
        text_buffer.write(format_violations(path.violations(), verbose=verbose))
    return text_buffer.getvalue()
