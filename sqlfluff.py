""" The Main file for SQLFluff """

import click
import os
import re


def ordinalise(s):
    return [ord(c) for c in s]


class ParsedLine(object):
    whitespace_regex = re.compile('\s+')
    def __init__(self, line):
        self.initial_string = None
        self.terminal_string = None
        self.core_string = None
        #click.echo(len(line))
        # Iterate through whitespace matches
        for m in self.whitespace_regex.finditer(line):
            if m:
                #click.echo(m)
                #click.echo(repr(m.group()))
                match_start, match_end = m.span()
                if match_start == 0:
                    #click.echo("Initial String")
                    self.initial_string = m.group()
                elif match_end == len(line):
                    #click.echo("Terminal Match")
                    self.terminal_string = m.group()
        self.core_string = line[len(self.initial_string or '') : len(line) - len(self.terminal_string or '')]
        #click.echo(self.core_string)
    
    def __repr__(self):
        return '<Parsed Line - Core:%r, Initial=%r, Terminal=%r>' % (self.core_string, self.initial_string, self.terminal_string)


@click.command()
@click.option('--dialect', default='ansi', help='The dialect of SQL to lint')
@click.argument('paths', nargs=-1)
def sqlfluff_lint(dialect, paths):
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
            for line in f:
                #click.echo("##############")
                #click.echo(line)
                #click.echo("###")
                #click.echo(ordinalise(line))
                #click.echo("###")
                obj = ParsedLine(line)
                click.echo(obj)
                

if __name__ == '__main__':
    sqlfluff_lint()