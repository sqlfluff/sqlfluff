"""Contains the CLI."""

import sys

import click

from ..dialects import dialect_selector
from ..linter import Linter
from .formatters import (format_config, format_rules,
                         format_violation, format_linting_result_header,
                         format_linting_result_footer, colorize)
from .helpers import cli_table, get_package_version
from ..config import FluffConfig
from ..errors import SQLLintError


def common_options(f):
    """Add common options to commands via a decorator."""
    f = click.option('-v', '--verbose', count=True,
                     help=('Verbosity, how detailed should the output be. This is *stackable*, so `-vv`'
                           ' is more verbose than `-v`. For the most verbose option try `-vvvv` or `-vvvvv`.'))(f)
    f = click.option('-n', '--nocolor', is_flag=True,
                     help='No color - if this is set then the output will be without ANSI color codes.')(f)
    f = click.option('--dialect', default=None, help='The dialect of SQL to lint (default=ansi)')(f)
    f = click.option('--templater', default=None, help='The templater to use (default=jinja)')(f)
    f = click.option('--rules', default=None,
                     # short_help='Specify a particular rule, or comma seperated rules, to check',
                     help=('Narrow the search to only specific rules. For example '
                           'specifying `--rules L001` will only search for rule `L001` (Unnessesary '
                           'trailing whitespace). Multiple rules can be specified with commas e.g. '
                           '`--rules L001,L002` will specify only looking for violations of rule '
                           '`L001` and rule `L002`.'))(f)
    f = click.option('--exclude-rules', default=None,
                     # short_help='Specify a particular rule, or comma seperated rules to exclude',
                     help=('Exclude specific rules. For example '
                           'specifying `--exclude-rules L001` will remove rule `L001` (Unnessesary '
                           'trailing whitespace) from the set of considered rules. This could either '
                           'be the whitelist, or the general set if there is no specific whitelist. '
                           'Multiple rules can be specified with commas e.g. '
                           '`--exclude-rules L001,L002` will exclude violations of rule '
                           '`L001` and rule `L002`.'))(f)
    f = click.option('--ignore', default=None,
                     help=("Ignore particular families of errors so that they don't cause a failed "
                           "run. For example `--ignore parsing` would mean that any parsing errors "
                           "are ignored and don't influence the success or fail of a run. Multiple "
                           "options are possible if comma seperated e.g. `--ignore parsing,templating`."))(f)
    return f


def get_config(**kwargs):
    """Get a config object from kwargs."""
    if 'dialect' in kwargs:
        try:
            # We're just making sure it exists at this stage - it will be fetched properly in the linter
            dialect_selector(kwargs['dialect'])
        except KeyError:
            click.echo("Error: Unknown dialect {0!r}".format(kwargs['dialect']))
            sys.exit(66)
    # Instantiate a config object (filtering out the nulls)
    overrides = {k: kwargs[k] for k in kwargs if kwargs[k] is not None}
    return FluffConfig.from_root(overrides=overrides)


def get_linter(cfg, silent=False):
    """Get a linter object given a config."""
    try:
        # We're just making sure it exists at this stage - it will be fetched properly in the linter
        dialect_selector(cfg.get('dialect'))
    except KeyError:
        click.echo("Error: Unknown dialect {0!r}".format(cfg.get('dialect')))
        sys.exit(66)

    if not silent:
        # Instantiate the linter and return (with an output function)
        return Linter(config=cfg,
                      output_func=lambda m: click.echo(m, color=cfg.get('color')))
    else:
        # Instantiate the linter and return (with NO output function)
        return Linter(config=cfg, output_func=lambda m: None)


@click.group()
def cli():
    """Sqlfluff is a modular sql linter for humans."""


@cli.command()
@common_options
def version(**kwargs):
    """Show the version of sqlfluff."""
    c = get_config(**kwargs)
    if c.get('verbose') > 0:
        # Instantiate the linter
        lnt = get_linter(c)
        click.echo(format_config(lnt, verbose=c.get('verbose')))
    else:
        click.echo(get_package_version(), color=c.get('color'))


@cli.command()
@common_options
def rules(**kwargs):
    """Show the current rules is use."""
    c = get_config(**kwargs)
    lnt = get_linter(c)
    click.echo(format_rules(lnt), color=c.get('color'))


@cli.command()
@common_options
@click.argument('paths', nargs=-1)
def lint(paths, **kwargs):
    """Lint SQL files via passing a list of files or using stdin.

    PATH is the path to a sql file or directory to lint. This can be either a
    file ('path/to/file.sql'), a path ('directory/of/sql/files'), a single ('-')
    character to indicate reading from *stdin* or a dot/blank ('.'/' ') which will
    be interpreted like passing the current working directory as a path argument.

    Linting SQL files:

        sqlfluff lint path/to/file.sql
        sqlfluff lint directory/of/sql/files

    Linting a file via stdin (note the lone '-' character):

        cat path/to/file.sql | sqlfluff lint -
        echo 'select col from tbl' | sqlfluff lint -

    """
    c = get_config(**kwargs)
    lnt = get_linter(c)
    verbose = c.get('verbose')

    config_string = format_config(lnt, verbose=verbose)
    if len(config_string) > 0:
        lnt.log(config_string)
    # add stdin if specified via lone '-'
    if ('-',) == paths:
        result = lnt.lint_string_wrapped(sys.stdin.read(), fname='stdin', verbosity=verbose)
    else:
        # Output the results as we go
        lnt.log(format_linting_result_header(verbose=verbose))
        try:
            result = lnt.lint_paths(paths, verbosity=verbose)
        except IOError:
            click.echo(colorize('The path(s) {0!r} could not be accessed. Check it/they exist(s).'.format(paths), 'red'))
            sys.exit(1)
        # Output the final stats
        lnt.log(format_linting_result_footer(result, verbose=verbose))
    sys.exit(result.stats()['exit code'])


def do_fixes(lnt, paths, **kwargs):
    """Actually do the fixes."""
    result = lnt.lint_paths(paths, fix=True)
    click.echo('Persisting Changes...')
    res = result.persist_changes(output_func=lnt.output_func, **kwargs)
    if all(res.values()):
        click.echo('Done. Please check your files to confirm.')
        return True
    # If some failed then return false
    click.echo('Done. Some operations failed. Please check your files to confirm.')
    click.echo('Some errors cannot be fixed or there is another error blocking it.')
    return False


@cli.command()
@common_options
@click.option('-f', '--force', is_flag=True,
              help=('skip the confirmation prompt and go straight to applying '
                    'fixes. **Use this with caution.**'))
@click.argument('paths', nargs=-1)
def fix(force, paths, **kwargs):
    """Fix SQL files.

    PATH is the path to a sql file or directory to lint. This can be either a
    file ('path/to/file.sql'), a path ('directory/of/sql/files'), a single ('-')
    character to indicate reading from *stdin* or a dot/blank ('.'/' ') which will
    be interpreted like passing the current working directory as a path argument.
    """
    c = get_config(**kwargs)
    lnt = get_linter(c)
    verbose = c.get('verbose')

    config_string = format_config(lnt, verbose=verbose)
    if len(config_string) > 0:
        lnt.log(config_string)
    # Check that if fix is specified, that we have picked only a subset of rules
    if lnt.config.get('rule_whitelist') is None:
        lnt.log(("The fix option is only available in combination"
                 " with --rules. This is for your own safety!"))
        sys.exit(1)

    # handle stdin case. should output formatted sql to stdout and nothing else.
    if ('-',) == paths:
        stdin = sys.stdin.read()
        result = lnt.lint_string_wrapped(stdin, fname='stdin', verbosity=verbose, fix=True)
        stdout = result.paths[0].files[0].fix_string()
        click.echo(stdout, nl=False)
        sys.exit()

    # Lint the paths (not with the fix argument at this stage), outputting as we go.
    lnt.log("==== finding violations ====")
    try:
        result = lnt.lint_paths(paths, verbosity=verbose)
    except IOError:
        click.echo(colorize('The path(s) {0!r} could not be accessed. Check it/they exist(s).'.format(paths), 'red'))
        sys.exit(1)

    # NB: We filter to linting violations here, because they're
    # the only ones which can be potentially fixed.
    if result.num_violations(types=SQLLintError) > 0:
        click.echo("==== fixing violations ====")
        click.echo("{0} linting violations found".format(
            result.num_violations(types=SQLLintError)))
        if force:
            click.echo('FORCE MODE: Attempting fixes...')
            success = do_fixes(lnt, paths, types=SQLLintError)
            if not success:
                sys.exit(1)
        else:
            click.echo('Are you sure you wish to attempt to fix these? [Y/n] ', nl=False)
            c = click.getchar().lower()
            click.echo('...')
            if c == 'y':
                click.echo('Attempting fixes...')
                success = do_fixes(lnt, paths)
                if not success:
                    sys.exit(1)
            elif c == 'n':
                click.echo('Aborting...')
            else:
                click.echo('Invalid input :(')
                click.echo('Aborting...')
    else:
        click.echo("==== no linting violations found ====")
    sys.exit(0)


@cli.command()
@common_options
@click.argument('path', nargs=1)
@click.option('--recurse', default=0, help='The depth to recursively parse to (0 for unlimited)')
@click.option('-c', '--code-only', is_flag=True,
              help='Output only the code elements of the parse tree.')
@click.option('-f', '--format', default='human',
              type=click.Choice(['human', 'yaml'], case_sensitive=False),
              help='What format to return the parse result in.')
def parse(path, code_only, format, **kwargs):
    """Parse SQL files and just spit out the result.

    PATH is the path to a sql file or directory to lint. This can be either a
    file ('path/to/file.sql'), a path ('directory/of/sql/files'), a single ('-')
    character to indicate reading from *stdin* or a dot/blank ('.'/' ') which will
    be interpreted like passing the current working directory as a path argument.
    """
    c = get_config(**kwargs)
    # We don't want anything else to be logged if we want a yaml output
    lnt = get_linter(c, silent=format == 'yaml')
    verbose = c.get('verbose')
    recurse = c.get('recurse')

    config_string = format_config(lnt, verbose=verbose)
    if len(config_string) > 0:
        lnt.log(config_string)

    # TODO: do this better
    nv = 0
    try:
        # A single path must be specified for this command
        for parsed, violations, time_dict in lnt.parse_path(path, verbosity=verbose, recurse=recurse):
            if parsed:
                if format == 'human':
                    lnt.log(parsed.stringify(code_only=code_only))
                elif format == 'yaml':
                    click.echo(parsed.to_yaml(code_only=code_only, show_raw=True))
            else:
                # TODO: Make this prettier
                lnt.log('...Failed to Parse...')
            nv += len(violations)
            for v in violations:
                lnt.log(format_violation(v, verbose=verbose))
            if verbose >= 2:
                lnt.log("==== timings ====")
                lnt.log(cli_table(time_dict.items()))
    except IOError:
        click.echo(colorize('The path {0!r} could not be accessed. Check it exists.'.format(path), 'red'))
        sys.exit(1)

    if nv > 0:
        sys.exit(66)
    else:
        sys.exit(0)
