""" Contains the CLI """

import click
import sys
import os

import sqlfluff
from .linter import Linter


def format_filename(filename, success=False, verbose=0):
    return "== [{0}] {1}".format(filename, 'PASS' if success else 'FAIL')


def format_violation(violation, verbose=0):
    return "L:{0:4d} | P:{1:4d} | {2} | {3}".format(
        violation.chunk.line_no,
        violation.chunk.start_pos + 1,
        violation.rule.code,
        violation.rule.description)


def format_violations(violations, verbose=0):
    # Violations should be a dict
    keys = sorted(violations.keys())
    text_buffer = []
    for key in keys:
        # Success is having no violations
        success = len(violations[key]) == 0

        # Only print the filename if it's either a failure or verbosity > 1
        if verbose > 1 or not success:
            text_buffer.append(format_filename(key, success=success))

        # If we have violations, print them
        if not success:
            # first sort by position
            s = sorted(violations[key], key=lambda v: v.chunk.start_pos)
            # the primarily sort by line no
            s = sorted(s, key=lambda v: v.chunk.line_no)
            for violation in s:
                text_buffer.append(format_violation(violation))
    return text_buffer


def format_version(verbose=0):
    if verbose > 0:
        return "sqlfluff: {0}  python: {1[0]}.{1[1]}.{1[2]}".format(
            sqlfluff.__version__, sys.version_info)
    else:
        return sqlfluff.__version__


def format_dialect(dialect):
    return "dialect: {0}".format(dialect.name)


@click.group()
def cli():
    """ sqlfluff is a modular sql linter for humans """
    pass


@cli.command()
@click.option('-v', '--verbose', count=True)
def version(verbose):
    """ Show the version of sqlfluff """
    click.echo(format_version(verbose=verbose))


@cli.command()
@click.option('--dialect', default='ansi', help='The dialect of SQL to lint')
@click.option('-v', '--verbose', count=True)
@click.argument('paths', nargs=-1)
def lint(dialect, verbose, paths):
    """ Lint SQL files """
    try:
        dialect_obj = sqlfluff.dialects.dialect_selector(dialect)
    except KeyError:
        click.echo("Error: Unknown dialect {0!r}".format(dialect))
        sys.exit(66)

    # Only show version information if verbosity is high enough
    if verbose > 0:
        click.echo("==== sqlfluff ====")
        click.echo(format_version(verbose=verbose))
        click.echo(format_dialect(dialect=dialect_obj))
        click.echo("verbosity: {0}".format(verbose))
        click.echo("==== readout ====")

    # Instantiate the linter
    lnt = Linter(dialect=dialect_obj)

    # If no paths specified - assume local
    if len(paths) == 0:
        paths = (os.getcwd(),)

    num_violations = 0
    for path in paths:
        if verbose > 0:
            click.echo('=== [{0}] ==='.format(path))
        # Iterate through files recursively in the specified directory (if it's a directory)
        # or read the file directly if it's not
        violations = lnt.lint_path(path)
        num_violations = num_violations + sum([len(violations[key]) for key in violations])
        formatted = format_violations(violations, verbose=verbose)
        for line in formatted:
            click.echo(line)
    if verbose > 0:
        click.echo('=== {0:4d} Violations ==='.format(num_violations))
    if num_violations > 0:
        sys.exit(65)
    else:
        sys.exit(0)
