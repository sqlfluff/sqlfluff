""" Contains the CLI """

import click

from .lexer import RecursiveLexer


@click.command()
@click.option('--dialect', default='ansi', help='The dialect of SQL to lint')
@click.argument('paths', nargs=-1)
def main(dialect, paths):
    """Lint SQL files"""
    click.echo('Linting... [Dialect: {0}]'.format(dialect))
    click.echo(paths)
    if len(paths) == 0:
        # No paths specified - assume local
        paths = ('.',)
    for path in paths:
        click.echo('Linting: {0}'.format(path))
        # Iterate through files recursively in the specified directory (if it's a directory)
        # or read the file directly if it's not
    click.echo("Loading the example file...")
    for fname in ['example.sql', 'example-tab.sql']:
        click.echo(fname)
        with open(fname) as f:
            rl = RecursiveLexer()
            res = rl.lex_file_obj(f)
            click.echo(res.string_list())
            click.echo(res.context_list())


if __name__ == '__main__':
    main()
