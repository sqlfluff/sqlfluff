""" Contains the CLI """

import click
import sys


from ..dialects import dialect_selector
from ..linter import Linter
from .formatters import (format_linting_result, format_config, format_rules,
                         format_linting_violations, format_linting_fixes)
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
    config_string = format_config(lnt, verbose=verbose)
    if len(config_string) > 0:
        click.echo(config_string, color=color)
    # Lint the paths
    result = lnt.lint_paths(paths)
    # Output the results
    output = format_linting_result(result, verbose=verbose)
    # Echo the output out, without adding a newline
    click.echo(output, color=color, nl=False)
    sys.exit(result.stats()['exit code'])


@cli.command()
@common_options
@click.option('-f', '--force', is_flag=True)
@click.argument('paths', nargs=-1)
def fix(verbose, nocolor, dialect, rules, force, paths):
    """ Fix SQL files """
    # Configure Color
    color = False if nocolor else None
    # Instantiate the linter
    lnt = get_linter(dialiect_string=dialect, rule_string=rules)
    config_string = format_config(lnt, verbose=verbose)
    if len(config_string) > 0:
        click.echo(config_string, color=color)
    # Check that if fix is specified, that we have picked only a subset of rules
    if lnt.rule_whitelist is None:
        click.echo(("The fix option is only available in combination"
                    " with --rules. This is for your own safety!"))
        sys.exit(1)
    # Lint the paths
    result = lnt.lint_paths(paths)

    if result.num_violations() > 0:
        click.echo("==== violations found ====")
        click.echo(format_linting_violations(result, verbose=verbose), color=color)
        click.echo("==== fixing violations ====")
        click.echo("{0} violations found of rule{1} {2}".format(
            result.num_violations(),
            "s" if len(result.rule_whitelist) > 1 else "",
            ", ".join(result.rule_whitelist)
        ))
        if force:
            click.echo('FORCE MODE: Attempting fixes...')
            fixes = result.fix()
            click.echo(format_linting_fixes(fixes, verbose=verbose), color=color)
            click.echo('Done. Please check your files to confirm.')
        else:
            click.echo('Are you sure you wish to attempt to fix these? [Y/n] ', nl=False)
            c = click.getchar()
            if c == 'Y':
                click.echo('Attempting fixes...')
                fixes = result.fix()
                click.echo(format_linting_fixes(fixes, verbose=verbose), color=color)
                click.echo('Done. Please check your files to confirm.')
            elif c == 'n':
                click.echo('Aborting...')
            else:
                click.echo('Invalid input :(')
                click.echo('Aborting...')
    else:
        click.echo("==== no violations found ====")
    sys.exit(0)
