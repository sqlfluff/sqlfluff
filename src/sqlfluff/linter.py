""" Defines the linter class """

import os

from .dialects import AnsiSQLDialiect


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
            for dirpath, dirnames, filenames in os.walk(path):
                for fname in filenames:
                    for ext in self.sql_exts:
                        # is it a sql file?
                        if fname.endswith(ext):
                            # join the paths and normalise
                            buffer.add(os.path.normpath(os.path.join(dirpath, fname)))
            return buffer
        else:
            return path

    def files_from_path(self, path):
        pass

    def lint_path(self, target):
        pass
