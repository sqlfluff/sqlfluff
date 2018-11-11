""" Contains the CLI """

import click
import sys
import os

import sqlfluff
from .linter import Linter


def format_filename(filename, success=False, verbose=0):
    return "== [\u001b[30;1m{0}\u001b[0m] {1}".format(filename, '\u001b[32mPASS\u001b[0m' if success else '\u001b[31mFAIL\u001b[0m')


def format_violation(violation, verbose=0):
    return "\u001b[36mL:{0:4d} | P:{1:4d} | {2} |\u001b[0m {3}".format(
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
        return "\u001b[30;1msqlfluff:\u001b[0m {0}  \u001b[30;1m python:\u001b[0m {1[0]}.{1[1]}.{1[2]}".format(
            sqlfluff.__version__, sys.version_info)
    else:
        return sqlfluff.__version__


def format_dialect(dialect):
    return "\u001b[30;1mdialect:\u001b[0m {0}".format(dialect.name)


@click.group()
def cli():
    """ sqlfluff is a modular sql linter for humans """
    pass


@cli.command()
@click.option('-v', '--verbose', count=True)
def version(verbose, nocolor=None):
    """ Show the version of sqlfluff """
    click.echo(format_version(verbose=verbose))


@cli.command()
@click.option('--dialect', default='ansi', help='The dialect of SQL to lint')
@click.option('-v', '--verbose', count=True)
@click.option('-n', '--nocolor', is_flag=True)
@click.argument('paths', nargs=-1)
def lint(dialect, verbose, nocolor, paths):
    """ Lint SQL files """
    color = False if nocolor else None
    try:
        dialect_obj = sqlfluff.dialects.dialect_selector(dialect)
    except KeyError:
        click.echo("Error: Unknown dialect {0!r}".format(dialect))
        sys.exit(66)

    # Only show version information if verbosity is high enough
    if verbose > 0:
        click.echo("==== sqlfluff ====")
        click.echo(format_version(verbose=verbose), color=color)
        click.echo(format_dialect(dialect=dialect_obj), color=color)
        click.echo("\u001b[30;1mverbosity:\u001b[0m {0}".format(verbose), color=color)
        click.echo("==== readout ====")

    # Instantiate the linter
    lnt = Linter(dialect=dialect_obj)

    # If no paths specified - assume local
    if len(paths) == 0:
        paths = (os.getcwd(),)

    num_violations = 0
    for path in paths:
        if verbose > 0:
            click.echo('=== [ path: \u001b[30;1m{0}\u001b[0m ] ==='.format(path), color=color)
        # Iterate through files recursively in the specified directory (if it's a directory)
        # or read the file directly if it's not
        violations = lnt.lint_path(path)
        num_violations = num_violations + sum([len(violations[key]) for key in violations])
        formatted = format_violations(violations, verbose=verbose)
        for line in formatted:
            click.echo(line, color=color)

    if verbose >= 2:
        click.echo('=== {0:d} violations (across {1:d} files) ==='.format(num_violations, len(violations)))
        click.echo('=== [{0:d} clean files - {1:d} unclean files] ==='.format(
            sum([1 if len(violations[key]) > 0 else 0 for key in violations]),
            sum([0 if len(violations[key]) > 0 else 1 for key in violations])))
        if num_violations > 0:
            click.echo('=== avg {0:.2f} violations / file  ==='.format(num_violations * 1.0 / len(violations)))
    elif verbose >= 1:
        click.echo('=== {0:4d} violations ==='.format(num_violations))

    if num_violations > 0:
        sys.exit(65)
    else:
        sys.exit(0)
