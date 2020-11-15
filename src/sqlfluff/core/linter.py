"""Defines the linter class."""

import os
import time
from collections import namedtuple
import logging
from typing import List

from benchit import BenchIt
import pathspec

from .errors import SQLLexError, SQLParseError
from .parser import Lexer, Parser
from .rules import get_ruleset
from .config import FluffConfig

from .parser.segments.base import FixPatch


# Instantiate the linter logger
linter_logger = logging.getLogger("sqlfluff.linter")


class LintedFile(
    namedtuple(
        "ProtoFile",
        ["path", "violations", "time_dict", "tree", "ignore_mask", "templated_file"],
    )
):
    """A class to store the idea of a linted file."""

    __slots__ = ()

    def check_tuples(self):
        """Make a list of check_tuples.

        This assumes that all the violations found are
        linting violations (and therefore implement `check_tuple()`).
        If they don't then this function raises that error.
        """
        vs = []
        for v in self.get_violations():
            if hasattr(v, "check_tuple"):
                vs.append(v.check_tuple())
            else:
                raise v
        return vs

    def get_violations(self, rules=None, types=None, filter_ignore=True, fixable=None):
        """Get a list of violations, respecting filters and ignore options.

        Optionally now with filters.
        """
        violations = self.violations
        # Filter types
        if types:
            try:
                types = tuple(types)
            except TypeError:
                types = (types,)
            violations = [v for v in violations if isinstance(v, types)]
        # Filter rules
        if rules:
            if isinstance(rules, str):
                rules = (rules,)
            else:
                rules = tuple(rules)
            violations = [v for v in violations if v.rule_code() in rules]
        # Filter fixable
        if fixable is not None:
            # Assume that fixable is true or false if not None
            violations = [v for v in violations if v.fixable is fixable]
        # Filter ignorable violations
        if filter_ignore:
            violations = [v for v in violations if not v.ignore]
            # Ignore any rules in the ignore mask
            if self.ignore_mask:
                for line_no, rules in self.ignore_mask:
                    violations = [
                        v
                        for v in violations
                        if not (
                            v.line_no() == line_no
                            and (rules is None or v.rule_code() in rules)
                        )
                    ]
        return violations

    def num_violations(self, **kwargs):
        """Count the number of violations.

        Optionally now with filters.
        """
        violations = self.get_violations(**kwargs)
        return len(violations)

    def is_clean(self):
        """Return True if there are no ignorable violations."""
        return not any(self.get_violations(filter_ignore=True))

    def fix_string(self):
        """Obtain the changes to a path as a string.

        We use the source mapping features of TemplatedFile
        to generate a list of "patches" which cover the non
        templated parts of the file and refer back to the locations
        in the original file.

        NB: This is MUCH FASTER than the original approach
        using difflib in pre 0.4.0.
        """
        bencher = BenchIt()
        bencher("fix_string: start")

        linter_logger.debug("Original Tree: %r", self.templated_file.templated_str)
        linter_logger.debug("Fixed Tree: %r", self.tree.raw)

        # The sliced file is contigious in the TEMPLATED space.
        # NB: It has gaps and repeats in the source space.
        # It's also not the FIXED file either.
        linter_logger.debug("### Templated File.")
        for idx, file_slice in enumerate(self.templated_file.sliced_file):
            linter_logger.debug("    File slice: %s %r", idx, file_slice)

        original_source = self.templated_file.source_str

        # Make sure no patches overlap and divide up the source file into slices.
        # Any Template tags in the source file should be "untouchable".
        untouchable_slices = self.templated_file.untouchable_slices()

        linter_logger.debug("Untouchables: %s", untouchable_slices)

        # Patches, sorted by start
        template_space_patches: List[FixPatch] = sorted(
            list(
                self.tree.iter_patches(templated_str=self.templated_file.templated_str)
            ),
            key=lambda x: x[0].start,
        )
        linter_logger.debug("Templated-space patches: %s", template_space_patches)

        # We now convert enrich the patches into source space
        source_space_patches = []
        for patch in template_space_patches:
            try:
                source_slice = self.templated_file.templated_slice_to_source_slice(
                    patch.templated_slice,
                )
            except ValueError:
                # If we try and slice within a templated section, then we may fail
                # in which case, we should skip this edit.
                continue
            source_space_patches.append((source_slice, patch.fixed_raw))
        linter_logger.debug("Fresh source-space patches: %s", source_space_patches)

        # Dedupe on source space
        source_space_patches = [
            patch
            for idx, patch in enumerate(source_space_patches)
            if patch not in source_space_patches[:idx]
        ]
        linter_logger.debug("Deduped source-space patches: %s", source_space_patches)

        # We now slice up the file using the patches and any untouchables.
        # This gives us regions to apply changes to.
        slice_buff = []
        source_idx = 0
        for patch in source_space_patches:
            # Are there untouchables at or before the start of this patch?
            while (
                untouchable_slices and untouchable_slices[0][0].start < patch[0].start
            ):
                next_untouchable_slice = untouchable_slices.pop(0)[0]
                # Add a pre-slice before the next untouchable if needed.
                if next_untouchable_slice.start > source_idx:
                    slice_buff.append(slice(source_idx, next_untouchable_slice.start))
                # Add the untouchable.
                slice_buff.append(next_untouchable_slice)
                source_idx = next_untouchable_slice.stop

            # Is there a gap between current position and this patch?
            if patch[0].start > source_idx:
                # Add a slice up to this patch.
                slice_buff.append(slice(source_idx, patch[0].start))

            # Is this patch covering an area we've already covered?
            if patch[0].start < source_idx:
                linter_logger.info(
                    "Skipping overlapping patch at Index %s, Patch: %s, Patches: %s",
                    source_idx,
                    patch,
                    source_space_patches,
                )
                # Ignore the patch for now...
                continue

            # Add this patch.
            slice_buff.append(patch[0])
            source_idx = patch[0].stop
        # Add a tail slice.
        if source_idx < len(self.templated_file.source_str):
            slice_buff.append(slice(source_idx, len(self.templated_file.source_str)))

        linter_logger.debug("Final slice buffer: %s", slice_buff)

        # Iterate through the patches, building up the new string.
        str_buff = ""
        for source_slice in slice_buff:
            # Is it one in the patch buffer:
            for patch in source_space_patches:
                if patch[0] == source_slice:
                    # Use the patched version
                    linter_logger.debug(
                        "Appending Patch:    %s %r > %r",
                        patch[0],
                        self.templated_file.source_str[patch[0]],
                        patch[1],
                    )
                    str_buff += patch[1]
                    break
            else:
                # Use the raw string
                linter_logger.debug(
                    "Appending Raw:      %s %r",
                    source_slice,
                    self.templated_file.source_str[source_slice],
                )
                str_buff += self.templated_file.source_str[source_slice]

        bencher("fix_string: Fixing loop done")
        # The success metric here is whether anything ACTUALLY changed.
        return str_buff, str_buff != original_source

    def persist_tree(self, suffix=""):
        """Persist changes to the given path."""
        write_buff, success = self.fix_string()

        if success:
            fname = self.path
            # If there is a suffix specified, then use it.s
            if suffix:
                root, ext = os.path.splitext(fname)
                fname = root + suffix + ext
            # Actually write the file.
            with open(fname, "w") as f:
                f.write(write_buff)
        return success


class LintedPath:
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

    def num_violations(self, **kwargs):
        """Count the number of violations in the path."""
        return sum(file.num_violations(**kwargs) for file in self.files)

    def get_violations(self, **kwargs):
        """Return a list of violations in the path."""
        buff = []
        for file in self.files:
            buff += file.get_violations(**kwargs)
        return buff

    def violation_dict(self, **kwargs):
        """Return a dict of violations by file path."""
        return {file.path: file.get_violations(**kwargs) for file in self.files}

    def stats(self):
        """Return a dict containing linting stats about this path."""
        return dict(
            files=len(self.files),
            clean=sum(file.is_clean() for file in self.files),
            unclean=sum(not file.is_clean() for file in self.files),
            violations=sum(file.num_violations() for file in self.files),
        )

    def persist_changes(self, formatter=None, fixed_file_suffix="", **kwargs):
        """Persist changes to files in the given path.

        This also logs the output as we go using the formatter if present.
        """
        # Run all the fixes for all the files and return a dict
        buffer = {}
        for file in self.files:
            if file.num_violations(fixable=True, **kwargs) > 0:
                buffer[file.path] = file.persist_tree(suffix=fixed_file_suffix)
                result = buffer[file.path]
            else:
                buffer[file.path] = True
                result = "SKIP"

            if formatter:
                formatter.dispatch_persist_filename(filename=file.path, result=result)
        return buffer


class LintingResult:
    """A class to represent the result of a linting operation.

    Notably this might be a collection of paths, all with multiple
    potential files within them.
    """

    def __init__(self):
        self.paths = []

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
        """Add a new `LintedPath` to this result."""
        self.paths.append(path)

    def check_tuples(self, by_path=False):
        """Fetch all check_tuples from all contained `LintedPath` objects.

        Args:
            by_path (:obj:`bool`, optional): When False, all the check_tuples
                are aggregated into one flat list. When True, we return a `dict`
                of paths, each with it's own list of check_tuples. Defaults to False.

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

    def num_violations(self, **kwargs):
        """Count the number of violations in the result."""
        return sum(path.num_violations(**kwargs) for path in self.paths)

    def get_violations(self, **kwargs):
        """Return a list of violations in the result."""
        buff = []
        for path in self.paths:
            buff += path.get_violations(**kwargs)
        return buff

    def violation_dict(self, **kwargs):
        """Return a dict of paths and violations."""
        return self.combine_dicts(path.violation_dict(**kwargs) for path in self.paths)

    def stats(self):
        """Return a stats dictionary of this result."""
        all_stats = dict(files=0, clean=0, unclean=0, violations=0)
        for path in self.paths:
            all_stats = self.sum_dicts(path.stats(), all_stats)
        if all_stats["files"] > 0:
            all_stats["avg per file"] = (
                all_stats["violations"] * 1.0 / all_stats["files"]
            )
            all_stats["unclean rate"] = all_stats["unclean"] * 1.0 / all_stats["files"]
        else:
            all_stats["avg per file"] = 0
            all_stats["unclean rate"] = 0
        all_stats["clean files"] = all_stats["clean"]
        all_stats["unclean files"] = all_stats["unclean"]
        all_stats["exit code"] = 65 if all_stats["violations"] > 0 else 0
        all_stats["status"] = "FAIL" if all_stats["violations"] > 0 else "PASS"
        return all_stats

    def as_records(self):
        """Return the result as a list of dictionaries.

        Each record contains a key specifying the filepath, and a list of violations. This
        method is useful for serialization as all objects will be builtin python types
        (ints, strs).
        """
        return [
            {
                "filepath": path,
                "violations": sorted(
                    # Sort violations by line and then position
                    [v.get_info_dict() for v in violations],
                    # The tuple allows sorting by line number, then position, then code
                    key=lambda v: (v["line_no"], v["line_pos"], v["code"]),
                ),
            }
            for lintedpath in self.paths
            for path, violations in lintedpath.violation_dict().items()
            if violations
        ]

    def persist_changes(self, formatter=None, **kwargs):
        """Run all the fixes for all the files and return a dict."""
        return self.combine_dicts(
            *[
                path.persist_changes(formatter=formatter, **kwargs)
                for path in self.paths
            ]
        )

    @property
    def tree(self):
        """A convenience method for when there is only one file and we want the tree."""
        if len(self.paths) > 1:
            raise ValueError(
                ".tree() cannot be called when a LintingResult contains more than one path."
            )
        if len(self.paths[0].files) > 1:
            raise ValueError(
                ".tree() cannot be called when a LintingResult contains more than one file."
            )
        return self.paths[0].files[0].tree


class Linter:
    """The interface class to interact with the linter."""

    def __init__(
        self,
        sql_exts=(".sql",),
        config=None,
        formatter=None,
        dialect=None,
        rules=None,
        user_rules=None,
    ):
        self.sql_exts = sql_exts
        # Store the config object
        self.config = FluffConfig.from_kwargs(
            config=config, dialect=dialect, rules=rules
        )
        # Get the dialect and templater
        self.dialect = self.config.get("dialect_obj")
        self.templater = self.config.get("templater_obj")
        # Store the formatter for output
        self.formatter = formatter
        # Store references to user rule classes
        self.user_rules = user_rules or []

    def get_ruleset(self, config=None):
        """Get hold of a set of rules."""
        rs = get_ruleset()
        # Register any user rules
        for rule in self.user_rules:
            rs.register(rule)
        cfg = config or self.config
        return rs.get_rulelist(config=cfg)

    def rule_tuples(self):
        """A simple pass through to access the rule tuples of the rule set."""
        rs = self.get_ruleset()
        return [(rule.code, rule.description) for rule in rs]

    def parse_string(self, in_str, fname=None, recurse=True, config=None):
        """Parse a string.

        Returns:
            `tuple` of (`parsed`, `violations`, `time_dict`, `templated_file`).
                `parsed` is a segment structure representing the parsed file. If
                    parsing fails due to an inrecoverable violation then we will
                    return None.
                `violations` is a :obj:`list` of violations so far, which will either be
                    templating, lexing or parsing violations at this stage.
                `time_dict` is a :obj:`dict` containing timings for how long each step
                    took in the process.
                `templated_file` is a :obj:`TemplatedFile` containing the details
                    of the templated file.

        """
        violations = []
        t0 = time.monotonic()
        bencher = BenchIt()  # starts the timer
        if fname:
            short_fname = fname.replace("\\", "/").split("/")[-1]
        else:
            # this handles the potential case of a null fname
            short_fname = fname
        bencher("Staring parse_string for {0!r}".format(short_fname))

        # Dispatch the output for the parse header (including the config diff)
        if self.formatter:
            self.formatter.dispatch_parse_header(fname, self.config, config)

        linter_logger.info("TEMPLATING RAW [%s] (%s)", self.templater.name, fname)
        templated_file, templater_violations = self.templater.process(
            in_str, fname=fname, config=config or self.config
        )
        violations += templater_violations
        # Detect the case of a catastrophic templater fail. In this case
        # we don't continue. We'll just bow out now.
        if not templated_file:
            linter_logger.info("TEMPLATING FAILED: %s", templater_violations)
            tokens = None

        t1 = time.monotonic()
        bencher("Templating {0!r}".format(short_fname))

        if templated_file:
            linter_logger.info("LEXING RAW (%s)", fname)
            # Get the lexer
            lexer = Lexer(config=config or self.config)
            # Lex the file and log any problems
            try:
                tokens, lex_vs = lexer.lex(templated_file)
                # We might just get the violations as a list
                violations += lex_vs
            except SQLLexError as err:
                linter_logger.info("LEXING FAILED! (%s): %s", fname, err)
                violations.append(err)
                tokens = None
        else:
            tokens = None

        if tokens:
            linter_logger.info("Lexed tokens: %s", [seg.raw for seg in tokens])
        else:
            linter_logger.info("NO LEXED TOKENS!")

        t2 = time.monotonic()
        bencher("Lexing {0!r}".format(short_fname))
        linter_logger.info("PARSING (%s)", fname)
        parser = Parser(config=config or self.config)
        # Parse the file and log any problems
        if tokens:
            try:
                parsed = parser.parse(tokens, recurse=recurse)
            except SQLParseError as err:
                linter_logger.info("PARSING FAILED! (%s): %s", fname, err)
                violations.append(err)
                parsed = None
            if parsed:
                linter_logger.info("\n###\n#\n# {0}\n#\n###".format("Parsed Tree:"))
                linter_logger.info("\n" + parsed.stringify())
                # We may succeed parsing, but still have unparsable segments. Extract them here.
                for unparsable in parsed.iter_unparsables():
                    # No exception has been raised explicitly, but we still create one here
                    # so that we can use the common interface
                    violations.append(
                        SQLParseError(
                            "Found unparsable section: {0!r}".format(
                                unparsable.raw
                                if len(unparsable.raw) < 40
                                else unparsable.raw[:40] + "..."
                            ),
                            segment=unparsable,
                        )
                    )
                    linter_logger.info("Found unparsable segment...")
                    linter_logger.info(unparsable.stringify())
        else:
            parsed = None

        t3 = time.monotonic()
        time_dict = {"templating": t1 - t0, "lexing": t2 - t1, "parsing": t3 - t2}
        bencher("Finish parsing {0!r}".format(short_fname))
        return parsed, violations, time_dict, templated_file

    @staticmethod
    def extract_ignore_from_comment(comment):
        """Extract ignore mask entries from a comment segment."""
        # Also trim any whitespace afterward
        comment_content = comment.raw_trimmed().strip()
        if comment_content.startswith("noqa"):
            # This is an ignore identifier
            comment_remainder = comment_content[4:]
            if comment_remainder:
                if not comment_remainder.startswith(":"):
                    return SQLParseError(
                        "Malformed 'noqa' section. Expected 'noqa: <rule>[,...]",
                        segment=comment,
                    )
                comment_remainder = comment_remainder[1:]
                rules = [r.strip() for r in comment_remainder.split(",")]
                return (comment.pos_marker.line_no, tuple(rules))
            else:
                return (comment.pos_marker.line_no, None)
        return None

    def lint(self, parsed, config=None):
        """Lint a parsed file object."""
        config = config or self.config
        linting_errors = []
        for crawler in self.get_ruleset(config=config):
            lerrs, _, _, _ = crawler.crawl(parsed, dialect=config.get("dialect_obj"))
            linting_errors += lerrs
        return linting_errors

    def fix(self, parsed, config=None):
        """Fix a parsed file object."""
        # Set up our config
        config = config or self.config
        # If we're in fix mode, then we need to progressively call and reconstruct
        working = parsed
        # Keep a set of previous versions to catch infinite loops.
        previous_versions = {working.raw}
        # A placeholder for the fixes we had on the previous loop
        last_fixes = None
        # How many loops have we had
        fix_loop_idx = 0
        # How many loops are we allowed
        loop_limit = config.get("runaway_limit")
        # Keep track of the errors from round 1
        linting_errors = []
        initial_linting_errors = []
        # Enter into the main fix loop. Some fixes may introduce other
        # problems and so we loop around this until we reach stability
        # or we reach the limit.
        while fix_loop_idx < loop_limit:
            fix_loop_idx += 1
            changed = False
            # Iterate through each rule.
            for crawler in self.get_ruleset(config=config):
                # fixes should be a dict {} with keys edit, delete, create
                # delete is just a list of segments to delete
                # edit and create are list of tuples. The first element is the
                # "anchor", the segment to look for either to edit or to insert BEFORE.
                # The second is the element to insert or create.
                lerrs, _, fixes, _ = crawler.crawl(
                    working, dialect=config.get("dialect_obj"), fix=True
                )
                linting_errors += lerrs
                # Are there fixes to apply?
                if fixes:
                    linter_logger.info("Applying Fixes: %s", fixes)
                    # Do some sanity checks on the fixes before applying.
                    if last_fixes and fixes == last_fixes:
                        linter_logger.warning(
                            "One fix for %s not applied, it would re-cause the same error.",
                            crawler.code,
                        )
                    else:
                        last_fixes = fixes
                        # Actually apply fixes.
                        new_working, _ = working.apply_fixes(fixes)
                        # Check for infinite loops
                        if new_working.raw not in previous_versions:
                            # We've not seen this version of the file so far. Continue.
                            working = new_working
                            previous_versions.add(working.raw)
                            changed = True
                            continue
                        # Applying these fixes took us back to a state which we've
                        # seen before. Abort.
                        linter_logger.warning(
                            "One fix for %s not applied, it would re-cause the same error.",
                            crawler.code,
                        )
            # Keep track of initial errors for reporting.
            if fix_loop_idx == 1:
                initial_linting_errors = linting_errors.copy()
            # We did not change the file. Either the file is clean (no fixes), or
            # any fixes which are present will take us back to a previous state.
            if not changed:
                linter_logger.info(
                    "Fix loop complete. Stability achieved after %s/%s loops.",
                    fix_loop_idx,
                    loop_limit,
                )
                break
        else:
            linter_logger.warning(
                "Loop limit on fixes reached [%s]. Some fixes may be overdone.",
                loop_limit,
            )
        return working, initial_linting_errors

    def lint_string(self, in_str, fname="<string input>", fix=False, config=None):
        """Lint a string.

        Returns:
            :obj:`LintedFile`: an object representing that linted file.

        """
        # Sort out config, defaulting to the built in config if no override
        config = config or self.config

        # Using the new parser, read the file object.
        parsed, vs, time_dict, templated_file = self.parse_string(
            in_str=in_str, fname=fname, config=config
        )

        # Look for comment segments which might indicate lines to ignore.
        ignore_buff = []
        if parsed:
            for comment in parsed.recursive_crawl("comment"):
                if comment.name == "inline_comment":
                    ignore_entry = self.extract_ignore_from_comment(comment)
                    if isinstance(ignore_entry, SQLParseError):
                        vs.append(ignore_entry)
                    elif ignore_entry:
                        ignore_buff.append(ignore_entry)
            if ignore_buff:
                linter_logger.info("Parsed noqa directives from file: %r", ignore_buff)

        if parsed:
            t0 = time.monotonic()
            linter_logger.info("LINTING (%s)", fname)
            # If we're in fix mode, apply those fixes.
            # NB: We don't pass in the linting errors, because the fix function
            # regenerates them on each loop.
            if fix:
                parsed, initial_linting_errors = self.fix(parsed, config=config)
            else:
                initial_linting_errors = self.lint(parsed, config=config)

            # Update the timing dict
            t1 = time.monotonic()
            time_dict["linting"] = t1 - t0

            # We're only going to return the *initial* errors, rather
            # than any generated during the fixing cycle.
            vs += initial_linting_errors

        # We process the ignore config here if appropriate
        if config:
            for violation in vs:
                violation.ignore_if_in(config.get("ignore"))

        linted_file = LintedFile(
            fname,
            vs,
            time_dict,
            parsed,
            ignore_mask=ignore_buff,
            templated_file=templated_file,
        )

        # This is the main command line output from linting.
        if self.formatter:
            self.formatter.dispatch_file_violations(
                fname, linted_file, only_fixable=fix
            )

        # Safety flag for unset dialects
        if config.get("dialect") == "ansi" and linted_file.get_violations(
            fixable=True if fix else None, types=SQLParseError
        ):
            if self.formatter:
                self.formatter.dispatch_dialect_warning()

        return linted_file

    def paths_from_path(
        self, path, ignore_file_name=".sqlfluffignore", ignore_non_existent_files=False
    ):
        """Return a set of sql file paths from a potentially more ambigious path string.

        Here we also deal with the .sqlfluffignore file if present.

        """
        if not os.path.exists(path):
            if ignore_non_existent_files:
                return []
            else:
                raise IOError("Specified path does not exist")

        # Files referred to exactly are never ignored.
        if not os.path.isdir(path):
            return [path]

        # If it's a directory then expand the path!
        ignore_set = set()
        buffer = []
        for dirpath, _, filenames in os.walk(path):
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                # Handle potential .sqlfluffignore files
                if fname == ignore_file_name:
                    with open(fpath, "r") as fh:
                        spec = pathspec.PathSpec.from_lines("gitwildmatch", fh)
                    matches = spec.match_tree(dirpath)
                    for m in matches:
                        ignore_path = os.path.join(dirpath, m)
                        ignore_set.add(ignore_path)
                    # We don't need to process the ignore file any futher
                    continue

                # We won't purge files *here* because there's an edge case
                # that the ignore file is processed after the sql file.

                # Scan for remaining files
                for ext in self.sql_exts:
                    # is it a sql file?
                    if fname.endswith(ext):
                        buffer.append(fpath)

        # Check the buffer for ignore items and normalise the rest.
        filtered_buffer = []
        for fpath in buffer:
            if fpath not in ignore_set:
                filtered_buffer.append(os.path.normpath(fpath))

        # Return
        return sorted(filtered_buffer)

    def lint_string_wrapped(self, string, fname="<string input>", fix=False):
        """Lint strings directly."""
        result = LintingResult()
        linted_path = LintedPath(fname)
        linted_path.add(self.lint_string(string, fname=fname, fix=fix))
        result.add(linted_path)
        return result

    def lint_path(self, path, fix=False, ignore_non_existent_files=False):
        """Lint a path."""
        linted_path = LintedPath(path)
        if self.formatter:
            self.formatter.dispatch_path(path)
        for fname in self.paths_from_path(
            path, ignore_non_existent_files=ignore_non_existent_files
        ):
            config = self.config.make_child_from_path(fname)
            # Handle unicode issues gracefully
            with open(
                fname, "r", encoding="utf8", errors="backslashreplace"
            ) as target_file:
                linted_path.add(
                    self.lint_string(
                        target_file.read(), fname=fname, fix=fix, config=config
                    )
                )
        return linted_path

    def lint_paths(self, paths, fix=False, ignore_non_existent_files=False):
        """Lint an iterable of paths."""
        # If no paths specified - assume local
        if len(paths) == 0:
            paths = (os.getcwd(),)
        # Set up the result to hold what we get back
        result = LintingResult()
        for path in paths:
            # Iterate through files recursively in the specified directory (if it's a directory)
            # or read the file directly if it's not
            result.add(
                self.lint_path(
                    path, fix=fix, ignore_non_existent_files=ignore_non_existent_files
                )
            )
        return result

    def parse_path(self, path, recurse=True):
        """Parse a path of sql files.

        NB: This a generator which will yield the result of each file
        within the path iteratively.
        """
        for fname in self.paths_from_path(path):
            if self.formatter:
                self.formatter.dispatch_path(path)
            config = self.config.make_child_from_path(fname)
            # Handle unicode issues gracefully
            with open(
                fname, "r", encoding="utf8", errors="backslashreplace"
            ) as target_file:
                yield (
                    *self.parse_string(
                        target_file.read(), fname=fname, recurse=recurse, config=config
                    ),
                    # Also yield the config
                    config,
                )
