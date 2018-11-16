""" Contains the CLI """

import click
import sys
import os

from .. import __version__ as pkg_version
from ..dialects import dialect_selector
from ..linter import Linter
from .formatters import format_linting_result
from .helpers import cli_table


def get_python_version():
    return "{0[0]}.{0[1]}.{0[2]}".format(sys.version_info)


def get_package_version():
    return pkg_version


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

    # If no paths specified - assume local
    if len(paths) == 0:
        paths = (os.getcwd(),)

    # Instantiate the linter and lint the paths
    lnt = Linter(dialect=dialect_obj)
    result = lnt.lint_paths(paths)
    output = format_linting_result(result, verbose=verbose)

    click.echo(output, color=color)

    all_stats = result.stats()

    sys.exit(all_stats['exit code'])
