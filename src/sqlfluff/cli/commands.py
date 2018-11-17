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


def common_options(f):
    f = click.option('-v', '--verbose', count=True)(f)
    f = click.option('-n', '--nocolor', is_flag=True)(f)
    return f


@click.group()
def cli():
    """ sqlfluff is a modular sql linter for humans """
    pass


@cli.command()
@common_options
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
@common_options
@click.option('--dialect', default='ansi', help='The dialect of SQL to lint')
@click.option('--rules', default=None, help='Specify a particular rule, or comma seperated rules to check')
@click.argument('paths', nargs=-1)
def lint(verbose, nocolor, dialect, rules, paths):
    """ Lint SQL files """
    color = False if nocolor else None
    try:
        dialect_obj = dialect_selector(dialect)
    except KeyError:
        click.echo("Error: Unknown dialect {0!r}".format(dialect))
        sys.exit(66)

    # Work out if rules have been specified
    if rules:
        rule_list = rules.split(',')
    else:
        rule_list = None

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
        if rule_list:
            click.echo(cli_table([('rules', ', '.join(rule_list))], col_width=41), color=color)

    # If no paths specified - assume local
    if len(paths) == 0:
        paths = (os.getcwd(),)

    # Instantiate the linter and lint the paths
    lnt = Linter(dialect=dialect_obj, rule_whitelist=rule_list)
    result = lnt.lint_paths(paths)
    output = format_linting_result(result, verbose=verbose)

    click.echo(output, color=color)

    all_stats = result.stats()

    sys.exit(all_stats['exit code'])
