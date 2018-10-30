""" The Main file for SQLFluff """

import click
import os
import re


def ordinalise(s):
    return [ord(c) for c in s]


class PositionedChunk(object):
    def __init__(self, chunk, start_pos, line_no):
        self.chunk = chunk
        self.start_pos = start_pos
        self.line_no = line_no
    
    def __repr__(self):
        return "<PositionedChunk @(L:{line_no},P:{start_pos}) {chunk!r}>".format(
            **self.__dict__)
    
    def __len__(self):
        return len(self.chunk)


class ParsedLine(object):
    whitespace_regex = re.compile('\s+')
    def __init__(self, line, line_no):
        self.initial_chunk = None
        self.terminal_chunk = None
        self.core_chunk = None
        #click.echo(len(line))
        # Iterate through whitespace matches
        for m in self.whitespace_regex.finditer(line):
            if m:
                #click.echo(m)
                #click.echo(repr(m.group()))
                match_start, match_end = m.span()
                if match_start == 0:
                    #click.echo("Initial String")
                    self.initial_chunk = PositionedChunk(m.group(), match_start, line_no)    
                elif match_end == len(line):
                    #click.echo("Terminal Match")
                    self.terminal_chunk = PositionedChunk(m.group(), match_start, line_no)
        central_start = len(self.initial_chunk or '')
        central_end = len(line) - len(self.terminal_chunk or '')
        central_chunk = line[central_start : central_end]
        self.core_chunk = PositionedChunk(central_chunk, central_start, line_no)
        #click.echo(self.core_chunk)
    
    def __repr__(self):
        return '<Parsed Line - Core:%r, Initial=%r, Terminal=%r>' % (self.core_chunk, self.initial_chunk, self.terminal_chunk)


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
            for idx, line in enumerate(f):
                #click.echo("##############")
                #click.echo(line)
                #click.echo("###")
                #click.echo(ordinalise(line))
                #click.echo("###")
                obj = ParsedLine(line, idx)
                click.echo(obj)
                

if __name__ == '__main__':
    sqlfluff_lint()