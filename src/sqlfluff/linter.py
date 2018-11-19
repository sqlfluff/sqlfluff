""" Defines the linter class """

import os
from collections import namedtuple
import itertools

from six import StringIO

from .dialects import AnsiSQLDialiect
from .lexer import RecursiveLexer
from .rules.std import StandardRuleSet


class FixResult(namedtuple('ProtoFix', ['violation', 'success', 'detail'])):
    __slots__ = ()


class LintedFile(namedtuple('ProtoFile', ['path', 'violations'])):
    __slots__ = ()

    def check_tuples(self):
        return [v.check_tuple() for v in self.violations]

    def num_violations(self):
        return len(self.violations)

    def is_clean(self):
        return len(self.violations) == 0

    @staticmethod
    def apply_corrections_to_fileobj(fileobj, corrections):
        """ We don't validate here, we just apply to a file object """
        # NB: Make sure here that things don't overlap.
        # I don't know how it will behave if they do

        # Make a buffer to hold the new version of the file
        buff = StringIO()
        # Sort the corrections into a list (first ordered by line pos, then line no)
        # first sort by position
        correction_queue = sorted(corrections, key=lambda c: c.chunk.start_pos)
        # the primarily sort by line no
        correction_queue = sorted(correction_queue, key=lambda c: c.chunk.line_no)

        # Define a couple of helpers
        def next_correction():
            try:
                return correction_queue.pop(0)
            except IndexError:
                return None

        # Begin reading the existing file
        fileobj.seek(0)
        # Get the first correction
        correction = next_correction()
        # Start iterating through the source file
        for lineno, line in enumerate(fileobj, 1):
            # If we're not at the right line to correct yet, just pass through
            # (or we've done all our corrections)
            if correction is None or lineno < correction.chunk.line_no:
                buff.write(line)
            elif lineno == correction.chunk.line_no:
                # Reset the skip counter for this line
                skip = 0
                for idx, c in enumerate(line):
                    if skip > 0:
                        skip -= 1
                    # If we're past the last correction (correction is None)
                    # then we should just write the characters
                    elif correction is None or idx < correction.chunk.start_pos:
                        buff.write(c)
                    elif idx == correction.chunk.start_pos:
                        # So here we write the correction instead of the original characters
                        buff.write(correction.correction)
                        # and remember how many characters to skip (bear in mind we're on one already)
                        skip = len(correction.chunk.chunk) - 1
                        # and fetch the next correction
                        correction = next_correction()
                    else:
                        raise ValueError("This shouldn't happen! [sdkdjhf] idx:{0} skip:{1} corr:{2}".format(
                            idx, skip, correction))
            else:
                raise ValueError("This shouldn't happen! [awdjakh] line: {0!r} no:{1} corr: {2}".format(
                    line, lineno, correction))
        # We've now read the whole file, seek back to the beginning to truncate and overwrite
        fileobj.seek(0)
        fileobj.write(buff.getvalue())
        fileobj.truncate()

    def apply_corrections_to_file(self, corrections):
        """ We don't validate here, we just apply corrections to a path """
        # NB: Make sure here that things don't overlap.
        # I don't know how it will behave if they do
        with open(self.path, 'r+') as f:
            self.apply_corrections_to_fileobj(f, corrections)

    def fix(self):
        """ Find and attempt to fix the violations we found """
        fix_buffer = []
        pending_fix_buffer = []
        correction_buffer = []
        for v in self.violations:
            corrections = v.corrections
            # First check if any corrections are available
            if len(corrections) == 0:
                fix_buffer.append(FixResult(v, False, 'No correction available'))
            # Second check if the corrections overlap any existing corrections
            elif any([a.same_pos_as(b) for a, b in itertools.product(correction_buffer, corrections)]):
                fix_buffer.append(FixResult(v, False, 'The correction overlaps an existing correction in this round. Try again'))
            else:
                # We still buffer the corrections
                correction_buffer += corrections
                # We buffer the violations that it looks like we're going to fix
                pending_fix_buffer.append(v)
        # Let's try appling all these corrections now, and then update the fix buffer as a result
        try:
            self.apply_corrections_to_file(correction_buffer)
            application_success = True
            application_message = None
        except Exception as exc: # noqa
            # Assume if it's unsuccessful in any way that the whole thing failed
            application_success = False
            # Spit out the name of the exception for debugging
            application_message = 'Error occurred in applying the changes ({0})'.format(
                exc.__class__.__name__)
        # Use the result of applying the changes to see if the rest were successful
        for v in pending_fix_buffer:
            fix_buffer.append(FixResult(v, application_success, application_message))
        return fix_buffer


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

    def fix(self):
        # Run all the fixes for all the files and return a dict
        return {file.path: file.fix() for file in self.files}


class LintingResult(object):
    def __init__(self, rule_whitelist=None):
        self.paths = []
        # Store the rules we're using
        self.rule_whitelist = rule_whitelist

    @staticmethod
    def sum_dicts(d1, d2):
        """ Take the keys of two dictionaries and add them """
        keys = set(d1.keys()) | set(d2.keys())
        return {key: d1.get(key, 0) + d2.get(key, 0) for key in keys}

    @staticmethod
    def combine_dicts(*d):
        """ Take any set of dictionaries and combine them """
        dict_buffer = {}
        for dct in d:
            dict_buffer.update(dct)
        return dict_buffer

    def add(self, path):
        self.paths.append(path)

    def check_tuples(self):
        """
        Just compress all the tuples into one list
        NB: This is a little crude, as you can't tell which
        file the violations are from. Good for testing though.
        """
        tuple_buffer = []
        for path in self.paths:
            tuple_buffer += path.check_tuples()
        return tuple_buffer

    def num_violations(self):
        return sum([path.num_violations() for path in self.paths])

    def violations(self):
        return self.combine_dicts(path.violations() for path in self.paths)

    def stats(self):
        all_stats = dict(files=0, clean=0, unclean=0, violations=0)
        for path in self.paths:
            all_stats = self.sum_dicts(path.stats(), all_stats)
        all_stats['avg per file'] = all_stats['violations'] * 1.0 / all_stats['files']
        all_stats['unclean rate'] = all_stats['unclean'] * 1.0 / all_stats['files']
        all_stats['clean files'] = all_stats['clean']
        all_stats['unclean files'] = all_stats['unclean']
        all_stats['exit code'] = 65 if all_stats['violations'] > 0 else 0
        all_stats['status'] = 'FAIL' if all_stats['violations'] > 0 else 'PASS'
        return all_stats

    def fix(self):
        # Run all the fixes for all the files and return a dict
        return self.combine_dicts(*[path.fix() for path in self.paths])


class Linter(object):
    def __init__(self, dialect=AnsiSQLDialiect, sql_exts=('.sql',), rule_whitelist=None):
        self.dialect = dialect
        self.sql_exts = sql_exts
        # restrict the search to only specific rules.
        # assume that this is a list of rule codes
        self.rule_whitelist = rule_whitelist

    def get_ruleset(self):
        """
        A way of getting hold of a set of rules.
        We should probably extend this later for differing rules.
        """
        return StandardRuleSet()

    def rule_tuples(self):
        """ A simple pass through to access the rule tuples of the rule set """
        rt = self.get_ruleset().rule_tuples()
        if self.rule_whitelist:
            return [elem for elem in rt if elem[0] in self.rule_whitelist]
        else:
            return rt

    def lint_file(self, f, fname=None):
        """ Lint a file object - fname is optional for testing """
        # Instantiate a rule set
        rule_set = self.get_ruleset()
        rl = RecursiveLexer(dialect=self.dialect)
        chunkstring = rl.lex_file_obj(f)
        vs = rule_set.evaluate_chunkstring(chunkstring, rule_whitelist=self.rule_whitelist)
        return LintedFile(fname, vs)

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
                linted_path.add(self.lint_file(f, fname=fname))
        return linted_path

    def lint_paths(self, paths):
        # If no paths specified - assume local
        if len(paths) == 0:
            paths = (os.getcwd(),)
        # Set up the result to hold what we get back
        result = LintingResult(rule_whitelist=self.rule_whitelist)
        for path in paths:
            # Iterate through files recursively in the specified directory (if it's a directory)
            # or read the file directly if it's not
            result.add(self.lint_path(path))
        return result
