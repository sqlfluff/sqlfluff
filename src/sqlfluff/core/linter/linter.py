"""Defines the linter class."""

import sys
import os
import time
import logging
from typing import (
    Any,
    Generator,
    List,
    Sequence,
    Optional,
    Tuple,
    Union,
    cast,
    Iterable,
)

from benchit import BenchIt
import pathspec

from sqlfluff.core.errors import (
    SQLBaseError,
    SQLLexError,
    SQLLintError,
    SQLParseError,
    SQLTemplaterSkipFile,
)
from sqlfluff.core.parser import Lexer, Parser
from sqlfluff.core.templaters import TemplatedFile
from sqlfluff.core.rules import get_ruleset
from sqlfluff.core.config import FluffConfig, ConfigLoader

# Classes needed only for type checking
from sqlfluff.core.linter import runner as runner_module
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.segments.meta import MetaSegment
from sqlfluff.core.parser.segments.raw import RawSegment
from sqlfluff.core.rules.base import BaseRule

from sqlfluff.core.linter.common import RuleTuple, ParsedString, NoQaDirective
from sqlfluff.core.linter.linted_file import LintedFile
from sqlfluff.core.linter.linted_dir import LintedDir
from sqlfluff.core.linter.linting_result import LintingResult


WalkableType = Iterable[Tuple[str, Optional[List[str]], List[str]]]

# Instantiate the linter logger
linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")


class Linter:
    """The interface class to interact with the linter."""

    def __init__(
        self,
        config: Optional[FluffConfig] = None,
        formatter: Any = None,
        dialect: Optional[str] = None,
        rules: Optional[Union[str, List[str]]] = None,
        user_rules: Optional[Union[str, List[str]]] = None,
    ) -> None:
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

    def get_ruleset(self, config: Optional[FluffConfig] = None) -> List[BaseRule]:
        """Get hold of a set of rules."""
        rs = get_ruleset()
        # Register any user rules
        for rule in self.user_rules:
            rs.register(rule)
        cfg = config or self.config
        return rs.get_rulelist(config=cfg)

    def rule_tuples(self) -> List[RuleTuple]:
        """A simple pass through to access the rule tuples of the rule set."""
        rs = self.get_ruleset()
        return [RuleTuple(rule.code, rule.description) for rule in rs]

    @staticmethod
    def _lex_templated_file(
        templated_file: TemplatedFile, config: FluffConfig
    ) -> Tuple[Optional[Sequence[BaseSegment]], List[SQLLexError], FluffConfig]:
        """Lex a templated file.

        NOTE: This potentially mutates the config, so make sure to
        use the returned one.
        """
        violations = []
        linter_logger.info("LEXING RAW (%s)", templated_file.fname)
        # Get the lexer
        lexer = Lexer(config=config)
        # Lex the file and log any problems
        try:
            tokens, lex_vs = lexer.lex(templated_file)
            # We might just get the violations as a list
            violations += lex_vs
            linter_logger.info(
                "Lexed tokens: %s", [seg.raw for seg in tokens] if tokens else None
            )
        except SQLLexError as err:
            linter_logger.info("LEXING FAILED! (%s): %s", templated_file.fname, err)
            violations.append(err)
            return None, violations, config

        if not tokens:
            return None, violations, config

        # Check that we've got sensible indentation from the lexer.
        # We might need to suppress if it's a complicated file.
        templating_blocks_indent = config.get("template_blocks_indent", "indentation")
        if isinstance(templating_blocks_indent, str):
            force_block_indent = templating_blocks_indent.lower().strip() == "force"
        else:
            force_block_indent = False
        templating_blocks_indent = bool(templating_blocks_indent)
        # If we're forcing it through we don't check.
        if templating_blocks_indent and not force_block_indent:
            indent_balance = sum(
                getattr(elem, "indent_val", 0)
                for elem in cast(Tuple[BaseSegment, ...], tokens)
            )
            if indent_balance != 0:
                linter_logger.debug(
                    "Indent balance test failed for %r. Template indents will not be linted for this file.",
                    templated_file.fname,
                )
                # Don't enable the templating blocks.
                templating_blocks_indent = False
                # Disable the linting of L003 on templated tokens.
                config.set_value(["rules", "L003", "lint_templated_tokens"], False)

        # The file will have been lexed without config, so check all indents
        # are enabled.
        new_tokens = []
        for token in cast(Tuple[BaseSegment, ...], tokens):
            if token.is_meta:
                token = cast(MetaSegment, token)
                if token.indent_val != 0:
                    # Don't allow it if we're not linting templating block indents.
                    if not templating_blocks_indent:
                        continue
            new_tokens.append(token)
        # Return new buffer
        return new_tokens, violations, config

    @staticmethod
    def _parse_tokens(
        tokens: Sequence[BaseSegment], config: FluffConfig, recurse: bool = True
    ) -> Tuple[Optional[BaseSegment], List[SQLParseError]]:
        parser = Parser(config=config)
        violations = []
        # Parse the file and log any problems
        try:
            parsed: Optional[BaseSegment] = parser.parse(tokens, recurse=recurse)
        except SQLParseError as err:
            linter_logger.info("PARSING FAILED! : %s", err)
            violations.append(err)
            return None, violations

        if parsed:
            linter_logger.info("\n###\n#\n# {0}\n#\n###".format("Parsed Tree:"))
            linter_logger.info("\n" + parsed.stringify())
            # We may succeed parsing, but still have unparsable segments. Extract them here.
            for unparsable in parsed.iter_unparsables():
                # No exception has been raised explicitly, but we still create one here
                # so that we can use the common interface
                violations.append(
                    SQLParseError(
                        "Line {0[0]}, Position {0[1]}: Found unparsable section: {1!r}".format(
                            unparsable.pos_marker.working_loc,
                            unparsable.raw
                            if len(unparsable.raw) < 40
                            else unparsable.raw[:40] + "...",
                        ),
                        segment=unparsable,
                    )
                )
                linter_logger.info("Found unparsable segment...")
                linter_logger.info(unparsable.stringify())
        return parsed, violations

    @staticmethod
    def _generate_short_fname(fname: Optional[str] = None):
        # Handle nulls gracefully
        if not fname:
            return None
        return os.path.basename(fname)

    def render_string(self, in_str: str, fname: Optional[str], config: FluffConfig):
        """Template the file."""
        linter_logger.info("TEMPLATING RAW [%s] (%s)", self.templater.name, fname)

        try:
            templated_file, templater_violations = self.templater.process(
                in_str=in_str, fname=fname, config=config, formatter=self.formatter
            )
        except SQLTemplaterSkipFile as s:
            linter_logger.warning(str(s))
            templated_file = None
            templater_violations = []

        if not templated_file:
            linter_logger.info("TEMPLATING FAILED: %s", templater_violations)

        return templated_file, templater_violations

    def parse_string(
        self,
        in_str: str,
        fname: Optional[str] = None,
        recurse: bool = True,
        config: Optional[FluffConfig] = None,
    ) -> ParsedString:
        """Parse a string."""
        violations: List[SQLBaseError] = []
        t0 = time.monotonic()
        bencher = BenchIt()  # starts the timer
        short_fname = self._generate_short_fname(fname)
        bencher("Staring parse_string for {0!r}".format(short_fname))

        # Dispatch the output for the template header (including the config diff)
        if self.formatter:
            self.formatter.dispatch_template_header(fname, self.config, config)

        # Just use the local config from here:
        config = config or self.config

        # Scan the raw file for config commands.
        config.process_raw_file_for_config(in_str)

        templated_file, templater_violations = self.render_string(in_str, fname, config)
        violations += templater_violations

        t1 = time.monotonic()
        bencher("Templating {0!r}".format(short_fname))

        # Dispatch the output for the parse header
        if self.formatter:
            self.formatter.dispatch_parse_header(fname)

        tokens: Optional[Sequence[BaseSegment]]
        if templated_file:
            tokens, lvs, config = self._lex_templated_file(templated_file, config)
            violations += lvs
        else:
            tokens = None

        t2 = time.monotonic()
        bencher("Lexing {0!r}".format(short_fname))
        linter_logger.info("PARSING (%s)", fname)

        if tokens:
            parsed, pvs = self._parse_tokens(tokens, config, recurse=recurse)
            violations += pvs
        else:
            parsed = None

        t3 = time.monotonic()
        time_dict = {"templating": t1 - t0, "lexing": t2 - t1, "parsing": t3 - t2}
        bencher("Finish parsing {0!r}".format(short_fname))
        return ParsedString(parsed, violations, time_dict, templated_file, config)

    @classmethod
    def parse_noqa(cls, comment: str, line_no: int):
        """Extract ignore mask entries from a comment string."""
        # Also trim any whitespace afterward
        if comment.startswith("noqa"):
            # This is an ignore identifier
            comment_remainder = comment[4:]
            if comment_remainder:
                if not comment_remainder.startswith(":"):
                    return SQLParseError(
                        "Malformed 'noqa' section. Expected 'noqa: <rule>[,...]",
                        line_no=line_no,
                    )
                comment_remainder = comment_remainder[1:].strip()
                if comment_remainder:
                    action: Optional[str]
                    if "=" in comment_remainder:
                        action, rule_part = comment_remainder.split("=", 1)
                        if action not in {"disable", "enable"}:
                            return SQLParseError(
                                "Malformed 'noqa' section. Expected 'noqa: enable=<rule>[,...] | all' or 'noqa: disable=<rule>[,...] | all",
                                line_no=line_no,
                            )
                    else:
                        action = None
                        rule_part = comment_remainder
                        if rule_part in {"disable", "enable"}:
                            return SQLParseError(
                                "Malformed 'noqa' section. Expected 'noqa: enable=<rule>[,...] | all' or 'noqa: disable=<rule>[,...] | all",
                                line_no=line_no,
                            )
                    rules: Optional[Tuple[str, ...]]
                    if rule_part != "all":
                        rules = tuple(r.strip() for r in rule_part.split(","))
                    else:
                        rules = None
                    return NoQaDirective(line_no, rules, action)
            return NoQaDirective(line_no, None, None)
        return None

    @classmethod
    def extract_ignore_from_comment(cls, comment: RawSegment):
        """Extract ignore mask entries from a comment segment."""
        # Also trim any whitespace afterward
        comment_content = comment.raw_trimmed().strip()
        comment_line, _ = comment.pos_marker.source_position()
        result = cls.parse_noqa(comment_content, comment_line)
        if isinstance(result, SQLParseError):
            result.segment = comment
        return result

    @staticmethod
    def _warn_unfixable(code: str):
        linter_logger.warning(
            f"One fix for {code} not applied, it would re-cause the same error."
        )

    def lint_fix(
        self,
        tree: BaseSegment,
        config: Optional[FluffConfig] = None,
        fix: bool = False,
        fname: Optional[str] = None,
        templated_file: Optional[TemplatedFile] = None,
    ) -> Tuple[BaseSegment, List[SQLLintError]]:
        """Lint and optionally fix a tree object."""
        config = config or self.config
        # Keep track of the linting errors
        all_linting_errors = []
        # A placeholder for the fixes we had on the previous loop
        last_fixes = None
        # Keep a set of previous versions to catch infinite loops.
        previous_versions = {tree.raw}

        # If we are fixing then we want to loop up to the runaway_limit, otherwise just once for linting.
        loop_limit = config.get("runaway_limit") if fix else 1

        # Dispatch the output for the lint header
        if self.formatter:
            self.formatter.dispatch_lint_header(fname)

        for loop in range(loop_limit):
            changed = False
            for crawler in self.get_ruleset(config=config):
                # fixes should be a dict {} with keys edit, delete, create
                # delete is just a list of segments to delete
                # edit and create are list of tuples. The first element is the
                # "anchor", the segment to look for either to edit or to insert BEFORE.
                # The second is the element to insert or create.
                linting_errors, _, fixes, _ = crawler.crawl(
                    tree,
                    dialect=config.get("dialect_obj"),
                    fname=fname,
                    templated_file=templated_file,
                )
                all_linting_errors += linting_errors

                if fix and fixes:
                    linter_logger.info(f"Applying Fixes: {fixes}")
                    # Do some sanity checks on the fixes before applying.
                    if fixes == last_fixes:
                        self._warn_unfixable(crawler.code)
                    else:
                        last_fixes = fixes
                        new_tree, _ = tree.apply_fixes(fixes)
                        # Check for infinite loops
                        if new_tree.raw not in previous_versions:
                            # We've not seen this version of the file so far. Continue.
                            tree = new_tree
                            previous_versions.add(tree.raw)
                            changed = True
                            continue
                        else:
                            # Applying these fixes took us back to a state which we've
                            # seen before. Abort.
                            self._warn_unfixable(crawler.code)

            if loop == 0:
                # Keep track of initial errors for reporting.
                initial_linting_errors = all_linting_errors.copy()

            if fix and not changed:
                # We did not change the file. Either the file is clean (no fixes), or
                # any fixes which are present will take us back to a previous state.
                linter_logger.info(
                    f"Fix loop complete. Stability achieved after {loop}/{loop_limit} loops."
                )
                break
        if fix and loop + 1 == loop_limit:
            linter_logger.warning(f"Loop limit on fixes reached [{loop_limit}].")

        if config.get("ignore_templated_areas", default=True):
            initial_linting_errors = self.remove_templated_errors(
                initial_linting_errors
            )

        return tree, initial_linting_errors

    def remove_templated_errors(
        self, linting_errors: List[SQLLintError]
    ) -> List[SQLLintError]:
        """Filter a list of lint errors, removing those which only occur in templated slices."""
        # Filter out any linting errors in templated sections if relevant.
        linting_errors = list(
            filter(
                lambda e: (
                    # Is it in a literal section?
                    e.segment.pos_marker.is_literal()
                    # Is it a rule that is designed to work on templated sections?
                    or e.rule.targets_templated
                ),
                linting_errors,
            )
        )
        return linting_errors

    def fix(
        self,
        tree: BaseSegment,
        config: Optional[FluffConfig] = None,
        fname: Optional[str] = None,
        templated_file: Optional[TemplatedFile] = None,
    ) -> Tuple[BaseSegment, List[SQLLintError]]:
        """Return the fixed tree and violations from lintfix when we're fixing."""
        fixed_tree, violations = self.lint_fix(
            tree, config, fix=True, fname=fname, templated_file=templated_file
        )
        return fixed_tree, violations

    def lint(
        self,
        tree: BaseSegment,
        config: Optional[FluffConfig] = None,
        fname: Optional[str] = None,
        templated_file: Optional[TemplatedFile] = None,
    ) -> List[SQLLintError]:
        """Return just the violations from lintfix when we're only linting."""
        _, violations = self.lint_fix(
            tree, config, fix=False, fname=fname, templated_file=templated_file
        )
        return violations

    def lint_string(
        self,
        in_str: str = "",
        fname: str = "<string input>",
        fix: bool = False,
        config: Optional[FluffConfig] = None,
    ) -> LintedFile:
        """Lint a string.

        Returns:
            :obj:`LintedFile`: an object representing that linted file.

        """
        # Sort out config, defaulting to the built in config if no override
        config = config or self.config

        # Using the new parser, read the file object.
        parsed = self.parse_string(in_str=in_str, fname=fname, config=config)
        time_dict = parsed.time_dict
        vs = parsed.violations
        tree = parsed.tree

        # Look for comment segments which might indicate lines to ignore.
        ignore_buff = []
        if tree:
            for comment in tree.recursive_crawl("comment"):
                if comment.name == "inline_comment":
                    ignore_entry = self.extract_ignore_from_comment(comment)
                    if isinstance(ignore_entry, SQLParseError):
                        vs.append(ignore_entry)
                    elif ignore_entry:
                        ignore_buff.append(ignore_entry)
            if ignore_buff:
                linter_logger.info("Parsed noqa directives from file: %r", ignore_buff)

        if tree:
            t0 = time.monotonic()
            linter_logger.info("LINTING (%s)", fname)
            tree, initial_linting_errors = self.lint_fix(
                tree,
                config=config,
                fix=fix,
                fname=fname,
                templated_file=parsed.templated_file,
            )
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
            tree,
            ignore_mask=ignore_buff,
            templated_file=parsed.templated_file,
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
        self,
        path: str,
        ignore_file_name: str = ".sqlfluffignore",
        ignore_non_existent_files: bool = False,
        ignore_files: bool = True,
        working_path: str = os.getcwd(),
    ) -> List[str]:
        """Return a set of sql file paths from a potentially more ambiguous path string.

        Here we also deal with the .sqlfluffignore file if present.

        When a path to a file to be linted is explicitly passed
        we look for ignore files in all directories that are parents of the file,
        up to the current directory.

        If the current directory is not a parent of the file we only
        look for an ignore file in the direct parent of the file.

        """
        if not os.path.exists(path):
            if ignore_non_existent_files:
                return []
            else:
                raise IOError("Specified path does not exist")

        # Files referred to exactly are also ignored if
        # matched, but we warn the users when that happens
        is_exact_file = os.path.isfile(path)

        if is_exact_file:
            # When the exact file to lint is passed, we
            # fill path_walk with an input that follows
            # the structure of `os.walk`:
            #   (root, directories, files)
            dirpath = os.path.dirname(path)
            files = [os.path.basename(path)]
            ignore_file_paths = ConfigLoader.find_ignore_config_files(
                path=path, working_path=working_path, ignore_file_name=ignore_file_name
            )
            # Add paths that could contain "ignore files"
            # to the path_walk list
            path_walk_ignore_file = [
                (
                    os.path.dirname(ignore_file_path),
                    None,
                    # Only one possible file, since we only
                    # have one "ignore file name"
                    [os.path.basename(ignore_file_path)],
                )
                for ignore_file_path in ignore_file_paths
            ]
            path_walk: WalkableType = [(dirpath, None, files)] + path_walk_ignore_file
        else:
            path_walk = os.walk(path)

        # If it's a directory then expand the path!
        buffer = []
        ignore_set = set()
        for dirpath, _, filenames in path_walk:
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                # Handle potential .sqlfluffignore files
                if ignore_files and fname == ignore_file_name:
                    with open(fpath, "r") as fh:
                        spec = pathspec.PathSpec.from_lines("gitwildmatch", fh)
                    matches = spec.match_tree(dirpath)
                    for m in matches:
                        ignore_path = os.path.join(dirpath, m)
                        ignore_set.add(os.path.abspath(ignore_path))
                    # We don't need to process the ignore file any futher
                    continue

                # We won't purge files *here* because there's an edge case
                # that the ignore file is processed after the sql file.

                # Scan for remaining files
                for ext in self.config.get("sql_file_exts", default=".sql").split(","):
                    # is it a sql file?
                    if fname.endswith(ext):
                        buffer.append(fpath)

        if not ignore_files:
            return sorted(buffer)

        # Check the buffer for ignore items and normalise the rest.
        filtered_buffer = []

        for fpath in buffer:
            if os.path.abspath(fpath) not in ignore_set:
                filtered_buffer.append(os.path.normpath(fpath))
            elif is_exact_file:
                linter_logger.warning(
                    "Exact file path %s was given but "
                    "it was ignored by a %s pattern, "
                    "re-run with `--disregard-sqlfluffignores` to "
                    "skip %s"
                    % (
                        path,
                        ignore_file_name,
                        ignore_file_name,
                    )
                )

        # Return
        return sorted(filtered_buffer)

    def lint_string_wrapped(
        self, string: str, fname: str = "<string input>", fix: bool = False
    ) -> LintingResult:
        """Lint strings directly."""
        result = LintingResult()
        linted_path = LintedDir(fname)
        linted_path.add(self.lint_string(string, fname=fname, fix=fix))
        result.add(linted_path)
        return result

    MIN_THRESHOLD_PARALLEL = 2
    PARALLEL_CLS = runner_module.MultiProcessRunner

    def lint_path(
        self,
        path: str,
        fix: bool = False,
        ignore_non_existent_files: bool = False,
        ignore_files: bool = True,
        parallel: int = 1,
    ) -> LintedDir:
        """Lint a path."""
        linted_path = LintedDir(path)
        if self.formatter:
            self.formatter.dispatch_path(path)
        fnames = list(
            self.paths_from_path(
                path,
                ignore_non_existent_files=ignore_non_existent_files,
                ignore_files=ignore_files,
            )
        )
        runner: runner_module.BaseRunner
        if parallel >= self.MIN_THRESHOLD_PARALLEL and sys.version_info > (3, 7):
            runner = self.PARALLEL_CLS(
                type(self), self, self.config, self.dialect.name, parallel
            )
        else:
            if parallel > 1:
                linter_logger.warning(
                    "Parallel linting is not supported in Python %s.%s.",
                    sys.version_info.major,
                    sys.version_info.minor,
                )
            runner = runner_module.SequentialRunner(
                type(self), self, self.config, self.dialect.name
            )
        for linted_file in runner.run(fnames, fix):
            linted_path.add(linted_file)
            # If any fatal errors, then stop iteration.
            if any(v.fatal for v in linted_file.violations):
                linter_logger.error("Fatal linting error. Halting further linting.")
                break
        return linted_path

    def lint_paths(
        self,
        paths: Tuple[str, ...],
        fix: bool = False,
        ignore_non_existent_files: bool = False,
        ignore_files: bool = True,
        parallel: int = 1,
    ) -> LintingResult:
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
                    path,
                    fix=fix,
                    ignore_non_existent_files=ignore_non_existent_files,
                    ignore_files=ignore_files,
                    parallel=parallel,
                )
            )
        return result

    def parse_path(
        self, path: str, recurse: bool = True
    ) -> Generator[ParsedString, None, None]:
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
                yield self.parse_string(
                    target_file.read(), fname=fname, recurse=recurse, config=config
                )
