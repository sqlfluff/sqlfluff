"""Defines the linter class."""

import os
from collections import namedtuple

from .errors import SQLLexError, SQLParseError, SQLTemplaterError
from .helpers import get_time
from .parser.segments_file import FileSegment
from .parser.segments_base import verbosity_logger, frame_msg, ParseContext
from .rules.std import standard_rule_set

from .cli.formatters import format_linting_path, format_file_violations


class LintedFile(namedtuple('ProtoFile', ['path', 'violations', 'time_dict', 'tree'])):
    """A class to store the idea of a linted file."""
    __slots__ = ()

    def check_tuples(self):
        """Make a list of check_tuples.

        This assumes that all the violations found are
        linting violations (and therefore implement `check_tuple()`).
        If they don't then this function raises that error.
        """
        vs = []
        for v in self.violations:
            if hasattr(v, 'check_tuple'):
                vs.append(v.check_tuple())
            else:
                raise v
        return vs

    def num_violations(self):
        """Count the number of violations."""
        return len(self.violations)

    def is_clean(self):
        """Return True if there are no violations."""
        return len(self.violations) == 0

    def persist_tree(self):
        """Persist changes to the given path."""
        with open(self.path, 'w') as f:
            # TODO: We should probably have a seperate function for checking what's
            # already there and doing a diff. For now we'll just go an overwrite.
            f.write(self.tree.raw)
        # TODO: Make this return value more interesting...
        # TODO: Deal with templating and fixing elegantly.
        return True


class LintedPath(object):
    """A class to store the idea of a collection of linted files at a single start path."""
    def __init__(self, path):
        self.files = []
        self.path = path

    def add(self, file):
        """Add a file to this path."""
        self.files.append(file)

    def check_tuples(self, by_path=False):
        """Compress all the tuples into one list.

        NB: This is a little crude, as you can't tell which
        file the violations are from. Good for testing though.
        For more control set the `by_path` argument to true.
        """
        if by_path:
            return {file.path: file.check_tuples() for file in self.files}
        else:
            tuple_buffer = []
            for file in self.files:
                tuple_buffer += file.check_tuples()
            return tuple_buffer

    def num_violations(self):
        """Count the number of violations in the path."""
        return sum([file.num_violations() for file in self.files])

    def violations(self):
        """Return a dict of violations by file path."""
        return {file.path: file.violations for file in self.files}

    def stats(self):
        """Return a dict containing linting stats about this path."""
        return dict(
            files=len(self.files),
            clean=sum([file.is_clean() for file in self.files]),
            unclean=sum([not file.is_clean() for file in self.files]),
            violations=sum([file.num_violations() for file in self.files])
        )

    def persist_changes(self):
        """Persist changes to files in the given path."""
        # Run all the fixes for all the files and return a dict
        return {file.path: file.persist_tree() for file in self.files}


class LintingResult(object):
    """A class to represent the result of a linting operation.

    Notably this might be a collection of paths, all with multiple
    potential files within them.
    """

    def __init__(self, rule_whitelist=None):
        self.paths = []
        # Store the rules we're using
        self.rule_whitelist = rule_whitelist

    @staticmethod
    def sum_dicts(d1, d2):
        """Take the keys of two dictionaries and add them."""
        keys = set(d1.keys()) | set(d2.keys())
        return {key: d1.get(key, 0) + d2.get(key, 0) for key in keys}

    @staticmethod
    def combine_dicts(*d):
        """Take any set of dictionaries and combine them."""
        dict_buffer = {}
        for dct in d:
            dict_buffer.update(dct)
        return dict_buffer

    def add(self, path):
        self.paths.append(path)

    def check_tuples(self, by_path=False):
        """
        Just compress all the tuples into one list
        NB: This is a little crude, as you can't tell which
        file the violations are from. Good for testing though.
        """
        if by_path:
            buff = {}
            for path in self.paths:
                buff.update(path.check_tuples(by_path=by_path))
            return buff
        else:
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

    def persist_changes(self):
        # Run all the fixes for all the files and return a dict
        return self.combine_dicts(*[path.persist_changes() for path in self.paths])


class Linter(object):
    def __init__(self, sql_exts=('.sql',), output_func=None,
                 config=None):
        if config is None:
            raise ValueError("No config object provided to linter!")
        self.dialect = config.get('dialect_obj')
        self.templater = config.get('templater_obj')
        self.sql_exts = sql_exts
        # restrict the search to only specific rules.
        # assume that this is a list of rule codes
        self.rule_whitelist = config.get('rule_whitelist')
        self.rule_blacklist = config.get('rule_blacklist')
        # Used for logging as we go
        self.output_func = output_func
        # Store the config object
        self.config = config

    def get_parse_context(self, config=None):
        # Try to use a given config
        if config:
            return ParseContext.from_config(config)
        # Default to the instance config
        elif self.config:
            return ParseContext.from_config(self.config)
        else:
            raise ValueError("No config object!")

    def log(self, msg):
        if self.output_func:
            # Check we've actually got a meaningful message
            if msg.strip(' \n\t'):
                self.output_func(msg)

    def get_ruleset(self, config=None):
        """
        A way of getting hold of a set of rules.
        We should probably extend this later for differing rules.
        """
        rs = standard_rule_set
        cfg = config or self.config
        # default the whitelist to all the rules if not set
        whitelist = cfg.get('rule_whitelist') or [r.code for r in rs]
        blacklist = cfg.get('rule_blacklist') or []
        rs = [r for r in rs if r.code in whitelist and r.code not in blacklist]
        return rs

    def rule_tuples(self):
        """ A simple pass through to access the rule tuples of the rule set """
        rs = self.get_ruleset()
        rt = [(rule.code, rule.description) for rule in rs]

        if self.rule_whitelist:
            return [elem for elem in rt if elem[0] in self.rule_whitelist]
        else:
            return rt

    def parse_string(self, s, fname=None, verbosity=0, recurse=True, config=None):
        violations = []
        t0 = get_time()

        verbosity_logger("TEMPLATING RAW [{0}] ({1})".format(self.templater.name, fname), verbosity=verbosity)
        # Lex the file and log any problems
        try:
            s = self.templater.process(s, fname=fname, config=config)
        except SQLTemplaterError as err:
            violations.append(err)
            fs = None
            # NB: We'll carry on if we fail to template, it might still lex

        if s:
            verbosity_logger("LEXING RAW ({0})".format(fname), verbosity=verbosity)
            # Lex the file and log any problems
            try:
                fs = FileSegment.from_raw(s)
            except SQLLexError as err:
                violations.append(err)
                fs = None
        else:
            fs = None

        if fs:
            verbosity_logger(fs.stringify(), verbosity=verbosity)

        t1 = get_time()
        verbosity_logger("PARSING ({0})".format(fname), verbosity=verbosity)
        # Parse the file and log any problems
        if fs:
            try:
                # Make a parse context and parse
                context = self.get_parse_context()
                parsed = fs.parse(parse_context=context)
            except SQLParseError as err:
                violations.append(err)
                parsed = None
            if parsed:
                verbosity_logger(frame_msg("Parsed Tree:"), verbosity=verbosity)
                verbosity_logger(parsed.stringify(), verbosity=verbosity)
        else:
            parsed = None

        t2 = get_time()
        time_dict = {'lexing': t1 - t0, 'parsing': t2 - t1}

        return parsed, violations, time_dict

    def lint_string(self, s, fname='<string input>', verbosity=0, fix=False, config=None):
        """ Lint a file object - fname is optional for testing """
        # TODO: Tidy this up - it's a mess
        # Using the new parser, read the file object.
        parsed, vs, time_dict = self.parse_string(s=s, fname=fname, verbosity=verbosity, config=config)

        if parsed:
            # Now extract all the unparsable segments
            for unparsable in parsed.iter_unparsables():
                # # print("FOUND AN UNPARSABLE!")
                # # print(unparsable)
                # # print(unparsable.stringify())
                # No exception has been raised explicitly, but we still create one here
                # so that we can use the common interface
                vs.append(
                    SQLParseError(
                        "Found unparsable segment @ {0},{1}: {2!r}".format(
                            unparsable.pos_marker.line_no,
                            unparsable.pos_marker.line_pos,
                            unparsable.raw[:20] + "..."),
                        segment=unparsable
                    )
                )
                if verbosity >= 2:
                    verbosity_logger("Found unparsable segment...", verbosity=verbosity)
                    verbosity_logger(unparsable.stringify(), verbosity=verbosity)

            t0 = get_time()
            # At this point we should evaluate whether any parsing errors have occured
            if verbosity >= 2:
                verbosity_logger("LINTING ({0})".format(fname), verbosity=verbosity)

            # NOW APPLY EACH LINTER
            if fix:
                # If we're in fix mode, then we need to progressively call and reconstruct
                working = parsed
                linting_errors = []
                last_fixes = None
                while True:
                    for crawler in self.get_ruleset(config=config):
                        # fixes should be a dict {} with keys edit, delete, create
                        # delete is just a list of segments to delete
                        # edit and create are list of tuples. The first element is the
                        # "anchor", the segment to look for either to edit or to insert BEFORE.
                        # The second is the element to insert or create.

                        lerrs, _, fixes, _ = crawler.crawl(working, fix=True)
                        linting_errors += lerrs
                        if fixes:
                            verbosity_logger("Applying Fixes: {0}".format(fixes), verbosity=verbosity)
                            if fixes == last_fixes:
                                raise RuntimeError(
                                    ("Fixes appear to not have been applied, they are "
                                     "the same as last time! {0}").format(
                                        fixes))
                            else:
                                last_fixes = fixes
                            working, fixes = working.apply_fixes(fixes)
                            break
                        else:
                            # No fixes, move on to next crawler
                            continue
                    else:
                        # No more fixes to apply
                        break
                # Set things up to return the altered version
                parsed = working
            else:
                # Just get the violations
                linting_errors = []
                for crawler in self.get_ruleset(config=config):
                    lerrs, _, _, _ = crawler.crawl(parsed)
                    linting_errors += lerrs

            # Update the timing dict
            t1 = get_time()
            time_dict['linting'] = t1 - t0

            vs += linting_errors

        res = LintedFile(fname, vs, time_dict, parsed)
        # Do the logging as appropriate
        self.log(format_file_violations(fname, res.violations, verbose=verbosity))
        return res

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

    def lint_string_wrapped(self, string, fname='<string input>', verbosity=0, fix=False):
        """ Use to lint strings directly """
        result = LintingResult(rule_whitelist=self.rule_whitelist)
        linted_path = LintedPath(fname)
        linted_path.add(
            self.lint_string(string, fname=fname, verbosity=verbosity, fix=fix)
        )
        result.add(linted_path)
        return result

    def lint_path(self, path, verbosity=0, fix=False):
        linted_path = LintedPath(path)
        self.log(format_linting_path(path, verbose=verbosity))
        for fname in self.paths_from_path(path):
            config = self.config.make_child_from_path(fname)
            with open(fname, 'r') as f:
                linted_path.add(self.lint_string(f.read(), fname=fname, verbosity=verbosity, fix=fix, config=config))
        return linted_path

    def lint_paths(self, paths, verbosity=0, fix=False):
        # If no paths specified - assume local
        if len(paths) == 0:
            paths = (os.getcwd(),)
        # Set up the result to hold what we get back
        result = LintingResult(rule_whitelist=self.rule_whitelist)
        for path in paths:
            # Iterate through files recursively in the specified directory (if it's a directory)
            # or read the file directly if it's not
            result.add(self.lint_path(path, verbosity=verbosity, fix=fix))
        return result

    def parse_path(self, path, verbosity=0, recurse=True):
        for fname in self.paths_from_path(path):
            self.log('=== [\u001b[30;1m{0}\u001b[0m] ==='.format(fname))
            config = self.config.make_child_from_path(fname)
            with open(fname, 'r') as f:
                yield self.parse_string(f.read(), fname=fname, verbosity=verbosity, recurse=recurse, config=config)
