""" Defines the linter class """

import os
from collections import namedtuple

from .dialects import AnsiSQLDialiect
from .lexer import RecursiveLexer
from .rules.std import StandardRuleSet


class LintedFile(namedtuple('ProtoFile', ['path', 'violations'])):
    __slots__ = ()

    def check_tuples(self):
        return [v.check_tuple() for v in self.violations]

    def num_violations(self):
        return len(self.violations)

    def is_clean(self):
        return len(self.violations) == 0


class LintedPath(object):
    def __init__(self, path):
        self.files = []
        self.path = path

    def add(self, file):
        self.files.append(file)

    def check_tuples(self):
        """
        Just compress all the tuples into one list
        NB: This is a little crude, as you can't tell which
        file the violations are from. Good for testing though.
        """
        tuple_buffer = []
        for file in self.files:
            tuple_buffer += file.check_tuples()
        return tuple_buffer

    def num_violations(self):
        return sum([file.num_violations() for file in self.files])

    def violations(self):
        return {file.path: file.violations for file in self.files}

    def stats(self):
        return dict(
            files=len(self.files),
            clean=sum([file.is_clean() for file in self.files]),
            unclean=sum([not file.is_clean() for file in self.files]),
            violations=sum([file.num_violations() for file in self.files])
        )


class Linter(object):
    def __init__(self, dialect=AnsiSQLDialiect, sql_exts=('.sql',)):
        self.dialect = dialect
        self.sql_exts = sql_exts

    def paths_from_path(self, path):
        # take a path (potentially a directory) and return just the sql files
        if not os.path.exists(path):
            raise IOError("Specified path does not exist")
        elif os.path.isdir(path):
            # Then expand the path!
            buffer = set()
            for dirpath, _, filenames in os.walk(path):
                for fname in filenames:
                    for ext in self.sql_exts:
                        # is it a sql file?
                        if fname.endswith(ext):
                            # join the paths and normalise
                            buffer.add(os.path.normpath(os.path.join(dirpath, fname)))
            return buffer
        else:
            return set([path])

    def lint_path(self, path):
        linted_path = LintedPath(path)
        for fname in self.paths_from_path(path):
            with open(fname, 'r') as f:
                # Instantiate a rule set
                rule_set = StandardRuleSet()
                rl = RecursiveLexer(dialect=self.dialect)
                chunkstring = rl.lex_file_obj(f)
                vs = rule_set.evaluate_chunkstring(chunkstring)
                linted_path.add(LintedFile(fname, vs))
        return linted_path
