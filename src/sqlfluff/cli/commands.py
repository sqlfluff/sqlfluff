""" Contains the CLI """

import click
import sys
import os


from ..dialects import dialect_selector
from ..linter import Linter
from .formatters import format_linting_result, format_config, format_rules
from .helpers import get_package_version


def common_options(f):
    f = click.option('-v', '--verbose', count=True)(f)
    f = click.option('-n', '--nocolor', is_flag=True)(f)
    f = click.option('--dialect', default='ansi', help='The dialect of SQL to lint')(f)
    f = click.option('--rules', default=None, help='Specify a particular rule, or comma seperated rules to check')(f)
    return f


def get_linter(dialiect_string, rule_string):
    """ A generic way of getting hold of a linter """
    try:
        dialect_obj = dialect_selector(dialiect_string)
    except KeyError:
        click.echo("Error: Unknown dialect {0!r}".format(dialiect_string))
        sys.exit(66)
    # Work out if rules have been specified
    if rule_string:
        rule_list = rule_string.split(',')
    else:
        rule_list = None
    # Instantiate the linter and return
    return Linter(dialect=dialect_obj, rule_whitelist=rule_list)


@click.group()
def cli():
    """ sqlfluff is a modular sql linter for humans """
    pass


@cli.command()
@common_options
def version(verbose, nocolor, dialect, rules):
    """ Show the version of sqlfluff """
    # Configure Color
    color = False if nocolor else None
    if verbose > 0:
        # Instantiate the linter
        lnt = get_linter(dialiect_string=dialect, rule_string=rules)
        click.echo(format_config(lnt, verbose=verbose))
    else:
        click.echo(get_package_version(), color=color)


@cli.command()
@common_options
def rules(verbose, nocolor, dialect, rules):
    """ Show the current rules is use """
    # Configure Color
    color = False if nocolor else None
    # Instantiate the linter
    lnt = get_linter(dialiect_string=dialect, rule_string=rules)
    click.echo(format_rules(lnt), color=color)


@cli.command()
@common_options
@click.argument('paths', nargs=-1)
def lint(verbose, nocolor, dialect, rules, paths):
    """ Lint SQL files """
    # Configure Color
    color = False if nocolor else None
    # Instantiate the linter
    lnt = get_linter(dialiect_string=dialect, rule_string=rules)
    click.echo(format_config(lnt, verbose=verbose))

    # If no paths specified - assume local
    if len(paths) == 0:
        paths = (os.getcwd(),)

    # Lint the paths
    result = lnt.lint_paths(paths)
    output = format_linting_result(result, verbose=verbose)

    click.echo(output, color=color)
    sys.exit(result.stats()['exit code'])
