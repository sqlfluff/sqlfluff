""" Defines the linter class """

import os

from .dialects import AnsiSQLDialiect
from sqlfluff.lexer import RecursiveLexer
from sqlfluff.rules.std import load_standard_set


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
        rules = load_standard_set()
        violations = {}
        for fname in self.paths_from_path(path):
            violations[path] = []
            with open(fname, 'r') as f:
                rl = RecursiveLexer(dialect=self.dialect)
                chunkstring = rl.lex_file_obj(f)
                vs = rules.evaluate_chunkstring(chunkstring)
                # Use a list method instead here!
                violations[path] = violations[path] + vs
        return violations
