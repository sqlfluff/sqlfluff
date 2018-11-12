""" Contains the CLI """

import click
import sys
import os

from .. import __version__ as pkg_version
from ..dialects import dialect_selector
from ..linter import Linter
from .formatters import format_violations
from .helpers import cli_table


def get_python_version():
    return "{0[0]}.{0[1]}.{0[2]}".format(sys.version_info)


def get_package_version():
    return pkg_version


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
    color = False if nocolor else None
    if verbose > 0:
        click.echo(
            cli_table(
                [('sqlfluff', get_package_version()),
                 ('python', get_python_version())]),
            color=color)
    else:
        click.echo(get_package_version(), color=color)


@cli.command()
@click.option('--dialect', default='ansi', help='The dialect of SQL to lint')
@click.option('-v', '--verbose', count=True)
@click.option('-n', '--nocolor', is_flag=True)
@click.argument('paths', nargs=-1)
def lint(dialect, verbose, nocolor, paths):
    """ Lint SQL files """
    color = False if nocolor else None
    try:
        dialect_obj = dialect_selector(dialect)
    except KeyError:
        click.echo("Error: Unknown dialect {0!r}".format(dialect))
        sys.exit(66)

    # Only show version information if verbosity is high enough
    if verbose > 0:
        click.echo("==== sqlfluff ====")
        config_content = [
            ('sqlfluff', get_package_version()),
            ('python', get_python_version()),
            ('dialect', dialect_obj.name),
            ('verbosity', verbose)
        ]
        click.echo(cli_table(config_content), color=color)
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
