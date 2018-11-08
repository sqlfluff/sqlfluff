""" Contains the CLI """

import click

import sqlfluff
from .linter import Linter


def format_filename(filename, verbosity='std'):
    return "### [{0}]: Violations:".format(filename)


def format_violation(violation, verbosity='std'):
    return "L:{0}|P:{1}|{2}| {3}".format(
        violation.chunk.line_no,
        violation.chunk.start_pos + 1,
        violation.rule.code,
        violation.rule.description)


def format_violations(violations, verbosity='std'):
    # Violations should be a dict
    keys = sorted(violations.keys())
    text_buffer = []
    for key in keys:
        text_buffer.append(format_filename(key))
        # first sort by position
        s = sorted(violations[key], key=lambda v: v.chunk.start_pos)
        # the primarily sort by line no
        s = sorted(s, key=lambda v: v.chunk.line_no)
        for violation in s:
            text_buffer.append(format_violation(violation))
    return text_buffer


@click.group()
def cli():
    """ The generic linting command (and root of the cli) """
    pass


@cli.command()
def version():
    """ The version command """
    click.echo(sqlfluff.__version__)


@cli.command()
@click.option('--dialect', default='ansi', help='The dialect of SQL to lint')
@click.argument('paths', nargs=-1)
def lint(dialect, paths):
    """ Lint SQL files """
    click.echo('Linting... [Dialect: {0}]'.format(dialect))
    click.echo(paths)
    lnt = Linter()
    if len(paths) == 0:
        # No paths specified - assume local
        paths = ('.',)
    for path in paths:
        click.echo('Linting: {0}'.format(path))
        # Iterate through files recursively in the specified directory (if it's a directory)
        # or read the file directly if it's not
        violations = lnt.lint_path(path)
        formatted = format_violations(violations)
        for line in formatted:
            click.echo(line)
