""" Contains the CLI """

import click
import sys
import os

from .. import __version__ as pkg_version
from ..dialects import dialect_selector
from ..linter import Linter
from .formatters import format_violations
from .helpers import cli_table, colorize, sum_dicts


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

    # Instantiate the linter
    lnt = Linter(dialect=dialect_obj)

    # If no paths specified - assume local
    if len(paths) == 0:
        paths = (os.getcwd(),)

    all_stats = {}
    for path in paths:
        if verbose > 0:
            click.echo('=== [ path: {0} ] ==='.format(colorize(path, 'lightgrey')), color=color)
        # Iterate through files recursively in the specified directory (if it's a directory)
        # or read the file directly if it's not
        linted_path = lnt.lint_path(path)
        formatted = format_violations(linted_path.violations(), verbose=verbose)
        for line in formatted:
            click.echo(line, color=color)
        all_stats = sum_dicts(linted_path.stats(), all_stats)

    exit_state = {
        'code': 65 if all_stats['violations'] > 0 else 0,
        'status': 'FAIL' if all_stats['violations'] > 0 else 0
    }
    if verbose >= 1:
        click.echo("==== summary ====")
        if verbose >= 2:
            summary_content = [
                ('files', all_stats['files']),
                ('violations', all_stats['violations']),
                ('clean files', all_stats['clean']),
                ('unclean files', all_stats['unclean']),
                ('avg per file', all_stats['violations'] * 1.0 / all_stats['files']),
                ('status', exit_state['status'])
            ]
        else:
            summary_content = [
                ('violations', all_stats['violations']),
                ('status', exit_state['status'])]
        click.echo(cli_table(summary_content), color=color)

    sys.exit(exit_state['code'])
