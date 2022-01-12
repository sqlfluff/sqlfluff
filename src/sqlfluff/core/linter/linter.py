"""Defines the linter class."""

import fnmatch
import os
import time
import logging
from typing import (
    Any,
    List,
    Sequence,
    Optional,
    Tuple,
    cast,
    Iterable,
    Iterator,
)

import pathspec
import regex
from tqdm import tqdm

from sqlfluff.core.errors import (
    SQLBaseError,
    SQLLexError,
    SQLLintError,
    SQLParseError,
    SQLTemplaterSkipFile,
)
from sqlfluff.core.parser import Lexer, Parser
from sqlfluff.core.file_helpers import get_encoding
from sqlfluff.core.templaters import TemplatedFile
from sqlfluff.core.rules import get_ruleset
from sqlfluff.core.config import FluffConfig, ConfigLoader, progress_bar_configuration

# Classes needed only for type checking
from sqlfluff.core.parser.segments.base import BaseSegment
from sqlfluff.core.parser.segments.meta import MetaSegment
from sqlfluff.core.parser.segments.raw import RawSegment
from sqlfluff.core.rules.base import BaseRule

from sqlfluff.core.linter.common import (
    RuleTuple,
    ParsedString,
    NoQaDirective,
    RenderedFile,
)
from sqlfluff.core.linter.linted_file import LintedFile
from sqlfluff.core.linter.linted_dir import LintedDir
from sqlfluff.core.linter.linting_result import LintingResult


WalkableType = Iterable[Tuple[str, Optional[List[str]], List[str]]]

# Instantiate the linter logger
linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")


class Linter:
    """The interface class to interact with the linter."""

    # Default to allowing process parallelism
    allow_process_parallelism = True

    def __init__(
        self,
        config: Optional[FluffConfig] = None,
        formatter: Any = None,
        dialect: Optional[str] = None,
        rules: Optional[List[str]] = None,
        user_rules: Optional[List[BaseRule]] = None,
        exclude_rules: Optional[List[str]] = None,
    ) -> None:
        # Store the config object
        self.config = FluffConfig.from_kwargs(
            config=config,
            dialect=dialect,
            rules=rules,
            exclude_rules=exclude_rules,
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

    # #### Static methods
    # These are the building blocks of the linting process.

    @staticmethod
    def _load_raw_file_and_config(
        fname: str, root_config: FluffConfig
    ) -> Tuple[str, FluffConfig, str]:
        """Load a raw file and the associated config."""
        file_config = root_config.make_child_from_path(fname)
        encoding = get_encoding(fname=fname, config=file_config)
        with open(fname, encoding=encoding, errors="backslashreplace") as target_file:
            raw_file = target_file.read()
        # Scan the raw file for config commands.
        file_config.process_raw_file_for_config(raw_file)
        # Return the raw file and config
        return raw_file, file_config, encoding

    @staticmethod
    def _normalise_newlines(string: str) -> str:
        """Normalise newlines to unix-style line endings."""
        return regex.sub(r"\r\n|\r", "\n", string)

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

        if not tokens:  # pragma: no cover TODO?
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
        tokens: Sequence[BaseSegment],
        config: FluffConfig,
        recurse: bool = True,
        fname: Optional[str] = None,
    ) -> Tuple[Optional[BaseSegment], List[SQLParseError]]:
        parser = Parser(config=config)
        violations = []
        # Parse the file and log any problems
        try:
            parsed: Optional[BaseSegment] = parser.parse(
                tokens,
                recurse=recurse,
                fname=fname,
            )
        except SQLParseError as err:
            linter_logger.info("PARSING FAILED! : %s", err)
            violations.append(err)
            return None, violations

        if parsed:
            linter_logger.info("\n###\n#\n# {}\n#\n###".format("Parsed Tree:"))
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
    def parse_noqa(
        comment: str,
        line_no: int,
        rule_codes: List[str],
    ):
        """Extract ignore mask entries from a comment string."""
        # Also trim any whitespace afterward

        # Comment lines can also have noqa e.g.
        # --dafhsdkfwdiruweksdkjdaffldfsdlfjksd -- noqa: L016
        # Therefore extract last possible inline ignore.
        comment = [c.strip() for c in comment.split("--")][-1]

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
                        if action not in {"disable", "enable"}:  # pragma: no cover
                            return SQLParseError(
                                "Malformed 'noqa' section. "
                                "Expected 'noqa: enable=<rule>[,...] | all' "
                                "or 'noqa: disable=<rule>[,...] | all",
                                line_no=line_no,
                            )
                    else:
                        action = None
                        rule_part = comment_remainder
                        if rule_part in {"disable", "enable"}:
                            return SQLParseError(
                                "Malformed 'noqa' section. "
                                "Expected 'noqa: enable=<rule>[,...] | all' "
                                "or 'noqa: disable=<rule>[,...] | all",
                                line_no=line_no,
                            )
                    rules: Optional[Tuple[str, ...]]
                    if rule_part != "all":
                        # Rules can be globs therefore we compare to the rule_set to expand the globs.
                        unexpanded_rules = tuple(
                            r.strip() for r in rule_part.split(",")
                        )
                        expanded_rules = []
                        for r in unexpanded_rules:
                            expanded_rule = [
                                x
                                for x in fnmatch.filter(rule_codes, r)
                                if x not in expanded_rules
                            ]
                            if expanded_rule:
                                expanded_rules.extend(expanded_rule)
                            elif r not in expanded_rules:
                                # We were unable to expand the glob.
                                # Therefore assume the user is referencing
                                # a special error type (e.g. PRS, LXR, or TMP)
                                # and add this to the list of rules to ignore.
                                expanded_rules.append(r)
                        rules = tuple(expanded_rules)
                    else:
                        rules = None
                    return NoQaDirective(line_no, rules, action)
            return NoQaDirective(line_no, None, None)
        return None

    @staticmethod
    def remove_templated_errors(
        linting_errors: List[SQLBaseError],
    ) -> List[SQLBaseError]:
        """Filter a list of lint errors, removing those which only occur in templated slices."""
        # Filter out any linting errors in templated sections if relevant.
        result: List[SQLBaseError] = []
        for e in linting_errors:
            if isinstance(e, SQLLintError):
                if (
                    # Is it in a literal section?
                    e.segment.pos_marker.is_literal()
                    # Is it a rule that is designed to work on templated sections?
                    or e.rule.targets_templated
                ):
                    result.append(e)
            else:
                # If it's another type, just keep it. (E.g. SQLParseError from
                # malformed "noqa" comment).
                result.append(e)
        return result

    @staticmethod
    def _warn_unfixable(code: str):
        linter_logger.warning(
            f"One fix for {code} not applied, it would re-cause the same error."
        )

    # ### Class Methods
    # These compose the base static methods into useful recipes.

    @classmethod
    def parse_rendered(
        cls,
        rendered: RenderedFile,
        recurse: bool = True,
    ):
        """Parse a rendered file."""
        t0 = time.monotonic()
        violations = cast(List[SQLBaseError], rendered.templater_violations)
        tokens: Optional[Sequence[BaseSegment]]
        if rendered.templated_file:
            tokens, lvs, config = cls._lex_templated_file(
                rendered.templated_file, rendered.config
            )
            violations += lvs
        else:
            tokens = None

        t1 = time.monotonic()
        linter_logger.info("PARSING (%s)", rendered.fname)

        if tokens:
            parsed, pvs = cls._parse_tokens(
                tokens,
                rendered.config,
                recurse=recurse,
                fname=rendered.fname,
            )
            violations += pvs
        else:
            parsed = None

        time_dict = {
            **rendered.time_dict,
            "lexing": t1 - t0,
            "parsing": time.monotonic() - t1,
        }
        return ParsedString(
            parsed,
            violations,
            time_dict,
            rendered.templated_file,
            rendered.config,
            rendered.fname,
        )

    @classmethod
    def extract_ignore_from_comment(
        cls,
        comment: RawSegment,
        rule_codes: List[str],
    ):
        """Extract ignore mask entries from a comment segment."""
        # Also trim any whitespace afterward
        comment_content = comment.raw_trimmed().strip()
        comment_line, _ = comment.pos_marker.source_position()
        result = cls.parse_noqa(comment_content, comment_line, rule_codes)
        if isinstance(result, SQLParseError):
            result.segment = comment
        return result

    @classmethod
    def extract_ignore_mask(
        cls,
        tree: BaseSegment,
        rule_codes: List[str],
    ) -> Tuple[List[NoQaDirective], List[SQLBaseError]]:
        """Look for inline ignore comments and return NoQaDirectives."""
        ignore_buff: List[NoQaDirective] = []
        violations: List[SQLBaseError] = []
        for comment in tree.recursive_crawl("comment"):
            if comment.name == "inline_comment":
                ignore_entry = cls.extract_ignore_from_comment(comment, rule_codes)
                if isinstance(ignore_entry, SQLParseError):
                    violations.append(ignore_entry)
                elif ignore_entry:
                    ignore_buff.append(ignore_entry)
        if ignore_buff:
            linter_logger.info("Parsed noqa directives from file: %r", ignore_buff)
        return ignore_buff, violations

    @classmethod
    def lint_fix_parsed(
        cls,
        tree: BaseSegment,
        config: FluffConfig,
        rule_set: List[BaseRule],
        fix: bool = False,
        fname: Optional[str] = None,
        templated_file: Optional[TemplatedFile] = None,
        formatter: Any = None,
    ) -> Tuple[BaseSegment, List[SQLBaseError], List[NoQaDirective]]:
        """Lint and optionally fix a tree object."""
        # Keep track of the linting errors
        all_linting_errors = []
        # A placeholder for the fixes we had on the previous loop
        last_fixes = None
        # Keep a set of previous versions to catch infinite loops.
        previous_versions = {tree.raw}

        # If we are fixing then we want to loop up to the runaway_limit, otherwise just once for linting.
        loop_limit = config.get("runaway_limit") if fix else 1

        # Dispatch the output for the lint header
        if formatter:
            formatter.dispatch_lint_header(fname)

        # Look for comment segments which might indicate lines to ignore.
        if not config.get("disable_noqa"):
            rule_codes = [r.code for r in rule_set]
            ignore_buff, ivs = cls.extract_ignore_mask(tree, rule_codes)
            all_linting_errors += ivs
        else:
            ignore_buff = []

        for loop in range(loop_limit):
            changed = False

            progress_bar_crawler = tqdm(
                rule_set,
                desc="lint by rules",
                leave=False,
                disable=progress_bar_configuration.disable_progress_bar,
            )

            for crawler in progress_bar_crawler:
                progress_bar_crawler.set_description(f"rule {crawler.code}")

                # fixes should be a dict {} with keys edit, delete, create
                # delete is just a list of segments to delete
                # edit and create are list of tuples. The first element is the
                # "anchor", the segment to look for either to edit or to insert BEFORE.
                # The second is the element to insert or create.
                linting_errors, _, fixes, _ = crawler.crawl(
                    tree,
                    ignore_mask=ignore_buff,
                    dialect=config.get("dialect_obj"),
                    fname=fname,
                    templated_file=templated_file,
                )
                all_linting_errors += linting_errors

                if fix and fixes:
                    linter_logger.info(f"Applying Fixes [{crawler.code}]: {fixes}")
                    # Do some sanity checks on the fixes before applying.
                    if fixes == last_fixes:  # pragma: no cover
                        cls._warn_unfixable(crawler.code)
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
                            cls._warn_unfixable(crawler.code)

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
            initial_linting_errors = cls.remove_templated_errors(initial_linting_errors)

        return tree, initial_linting_errors, ignore_buff

    @classmethod
    def lint_parsed(
        cls,
        parsed: ParsedString,
        rule_set: List[BaseRule],
        fix: bool = False,
        formatter: Any = None,
        encoding: str = "utf8",
    ):
        """Lint a ParsedString and return a LintedFile."""
        violations = parsed.violations
        time_dict = parsed.time_dict
        tree: Optional[BaseSegment]
        if parsed.tree:
            t0 = time.monotonic()
            linter_logger.info("LINTING (%s)", parsed.fname)
            tree, initial_linting_errors, ignore_buff = cls.lint_fix_parsed(
                parsed.tree,
                config=parsed.config,
                rule_set=rule_set,
                fix=fix,
                fname=parsed.fname,
                templated_file=parsed.templated_file,
                formatter=formatter,
            )
            # Update the timing dict
            time_dict["linting"] = time.monotonic() - t0

            # We're only going to return the *initial* errors, rather
            # than any generated during the fixing cycle.
            violations += initial_linting_errors
        else:
            # If no parsed tree, set to None
            tree = None
            ignore_buff = []

        # We process the ignore config here if appropriate
        for violation in violations:
            violation.ignore_if_in(parsed.config.get("ignore"))

        linted_file = LintedFile(
            parsed.fname,
            violations,
            time_dict,
            tree,
            ignore_mask=ignore_buff,
            templated_file=parsed.templated_file,
            encoding=encoding,
        )

        # This is the main command line output from linting.
        if formatter:
            formatter.dispatch_file_violations(
                parsed.fname, linted_file, only_fixable=fix
            )

        # Safety flag for unset dialects
        if parsed.config.get("dialect") == "ansi" and linted_file.get_violations(
            fixable=True if fix else None, types=SQLParseError
        ):
            if formatter:  # pragma: no cover TODO?
                formatter.dispatch_dialect_warning()

        return linted_file

    @classmethod
    def lint_rendered(
        cls,
        rendered: RenderedFile,
        rule_set: List[BaseRule],
        fix: bool = False,
        formatter: Any = None,
    ) -> LintedFile:
        """Take a RenderedFile and return a LintedFile."""
        parsed = cls.parse_rendered(rendered)
        return cls.lint_parsed(
            parsed,
            rule_set=rule_set,
            fix=fix,
            formatter=formatter,
            encoding=rendered.encoding,
        )

    # ### Instance Methods
    # These are tied to a specific instance and so are not necessarily
    # safe to use in parallel operations.

    def render_string(
        self, in_str: str, fname: str, config: FluffConfig, encoding: str
    ) -> RenderedFile:
        """Template the file."""
        linter_logger.info("TEMPLATING RAW [%s] (%s)", self.templater.name, fname)

        # Start the templating timer
        t0 = time.monotonic()

        # Newlines are normalised to unix-style line endings (\n).
        # The motivation is that Jinja normalises newlines during templating and
        # we want consistent mapping between the raw and templated slices.
        in_str = self._normalise_newlines(in_str)

        if not config.get("templater_obj") == self.templater:
            linter_logger.warning(
                (
                    f"Attempt to set templater to {config.get('templater_obj').name} failed. Using {self.templater.name} "
                    "templater. Templater cannot be set in a .sqlfluff file in a subdirectory of the current working "
                    "directory. It can be set in a .sqlfluff in the current working directory. See Nesting section of the "
                    "docs for more details."
                )
            )
        try:
            templated_file, templater_violations = self.templater.process(
                in_str=in_str, fname=fname, config=config, formatter=self.formatter
            )
        except SQLTemplaterSkipFile as s:  # pragma: no cover
            linter_logger.warning(str(s))
            templated_file = None
            templater_violations = []

        if not templated_file:
            linter_logger.info("TEMPLATING FAILED: %s", templater_violations)

        # Record time
        time_dict = {"templating": time.monotonic() - t0}

        return RenderedFile(
            templated_file, templater_violations, config, time_dict, fname, encoding
        )

    def render_file(self, fname: str, root_config: FluffConfig) -> RenderedFile:
        """Load and render a file with relevant config."""
        # Load the raw file.
        raw_file, config, encoding = self._load_raw_file_and_config(fname, root_config)
        # Render the file
        return self.render_string(raw_file, fname, config, encoding)

    def parse_string(
        self,
        in_str: str,
        fname: str = "<string>",
        recurse: bool = True,
        config: Optional[FluffConfig] = None,
        encoding: str = "utf-8",
    ) -> ParsedString:
        """Parse a string."""
        violations: List[SQLBaseError] = []

        # Dispatch the output for the template header (including the config diff)
        if self.formatter:
            self.formatter.dispatch_template_header(fname, self.config, config)

        # Just use the local config from here:
        config = config or self.config

        # Scan the raw file for config commands.
        config.process_raw_file_for_config(in_str)
        rendered = self.render_string(in_str, fname, config, encoding)
        violations += rendered.templater_violations

        # Dispatch the output for the parse header
        if self.formatter:
            self.formatter.dispatch_parse_header(fname)

        return self.parse_rendered(rendered, recurse=recurse)

    def fix(
        self,
        tree: BaseSegment,
        config: Optional[FluffConfig] = None,
        fname: Optional[str] = None,
        templated_file: Optional[TemplatedFile] = None,
    ) -> Tuple[BaseSegment, List[SQLBaseError]]:
        """Return the fixed tree and violations from lintfix when we're fixing."""
        config = config or self.config
        rule_set = self.get_ruleset(config=config)
        fixed_tree, violations, _ = self.lint_fix_parsed(
            tree,
            config,
            rule_set,
            fix=True,
            fname=fname,
            templated_file=templated_file,
            formatter=self.formatter,
        )
        return fixed_tree, violations

    def lint(
        self,
        tree: BaseSegment,
        config: Optional[FluffConfig] = None,
        fname: Optional[str] = None,
        templated_file: Optional[TemplatedFile] = None,
    ) -> List[SQLBaseError]:
        """Return just the violations from lintfix when we're only linting."""
        config = config or self.config
        rule_set = self.get_ruleset(config=config)
        _, violations, _ = self.lint_fix_parsed(
            tree,
            config,
            rule_set,
            fix=False,
            fname=fname,
            templated_file=templated_file,
            formatter=self.formatter,
        )
        return violations

    def lint_string(
        self,
        in_str: str = "",
        fname: str = "<string input>",
        fix: bool = False,
        config: Optional[FluffConfig] = None,
        encoding: str = "utf8",
    ) -> LintedFile:
        """Lint a string.

        Returns:
            :obj:`LintedFile`: an object representing that linted file.

        """
        # Sort out config, defaulting to the built in config if no override
        config = config or self.config
        # Parse the string.
        parsed = self.parse_string(
            in_str=in_str,
            fname=fname,
            config=config,
        )
        # Get rules as appropriate
        rule_set = self.get_ruleset(config=config)
        # Lint the file and return the LintedFile
        return self.lint_parsed(
            parsed,
            rule_set,
            fix=fix,
            formatter=self.formatter,
            encoding=encoding,
        )

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
                raise OSError("Specified path does not exist")

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
        ignores = {}
        for dirpath, _, filenames in path_walk:
            for fname in filenames:
                fpath = os.path.join(dirpath, fname)
                # Handle potential .sqlfluffignore files
                if ignore_files and fname == ignore_file_name:
                    with open(fpath) as fh:
                        spec = pathspec.PathSpec.from_lines("gitwildmatch", fh)
                        ignores[dirpath] = spec
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
            abs_fpath = os.path.abspath(fpath)
            for ignore_base, ignore_spec in ignores.items():
                abs_ignore_base = os.path.abspath(ignore_base)
                if abs_fpath.startswith(
                    abs_ignore_base + os.sep
                ) and ignore_spec.match_file(
                    os.path.relpath(abs_fpath, abs_ignore_base)
                ):
                    # This file is ignored, skip it.
                    if is_exact_file:
                        linter_logger.warning(
                            "Exact file path %s was given but "
                            "it was ignored by a %s pattern in %s, "
                            "re-run with `--disregard-sqlfluffignores` to "
                            "skip %s"
                            % (
                                path,
                                ignore_file_name,
                                ignore_base,
                                ignore_file_name,
                            )
                        )
                    break
            else:
                filtered_buffer.append(os.path.normpath(fpath))

        # Return
        return sorted(filtered_buffer)

    def lint_string_wrapped(
        self,
        string: str,
        fname: str = "<string input>",
        fix: bool = False,
    ) -> LintingResult:
        """Lint strings directly."""
        result = LintingResult()
        linted_path = LintedDir(fname)
        linted_path.add(self.lint_string(string, fname=fname, fix=fix))
        result.add(linted_path)
        result.stop_timer()
        return result

    def lint_path(
        self,
        path: str,
        fix: bool = False,
        ignore_non_existent_files: bool = False,
        ignore_files: bool = True,
        processes: int = 1,
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

        # to avoid circular import
        from sqlfluff.core.linter.runner import get_runner

        runner = get_runner(
            self,
            self.config,
            processes=processes,
            allow_process_parallelism=self.allow_process_parallelism,
        )

        # Show files progress bar only when there is more than one.
        files_count = len(fnames)
        progress_bar_files = tqdm(
            total=files_count,
            desc=f"file {os.path.basename(fnames[0] if fnames else '')}",
            leave=False,
            disable=files_count <= 1 or progress_bar_configuration.disable_progress_bar,
        )

        for i, linted_file in enumerate(runner.run(fnames, fix), start=1):
            linted_path.add(linted_file)
            # If any fatal errors, then stop iteration.
            if any(v.fatal for v in linted_file.violations):  # pragma: no cover
                linter_logger.error("Fatal linting error. Halting further linting.")
                break

            # Progress bar for files is rendered only when there is more than one file.
            # Additionally as it's updated after each loop, we need to get file name
            # from the next loop. This is why `enumerate` starts with `1` and there
            # is `i < len` to not exceed files list length.
            progress_bar_files.update(n=1)
            if i < len(fnames):
                progress_bar_files.set_description(
                    f"file {os.path.basename(fnames[i])}"
                )

        return linted_path

    def lint_paths(
        self,
        paths: Tuple[str, ...],
        fix: bool = False,
        ignore_non_existent_files: bool = False,
        ignore_files: bool = True,
        processes: int = 1,
    ) -> LintingResult:
        """Lint an iterable of paths."""
        paths_count = len(paths)

        # If no paths specified - assume local
        if not paths_count:  # pragma: no cover
            paths = (os.getcwd(),)
        # Set up the result to hold what we get back
        result = LintingResult()

        progress_bar_paths = tqdm(
            total=paths_count,
            desc="path",
            leave=False,
            disable=paths_count <= 1 or progress_bar_configuration.disable_progress_bar,
        )
        for path in paths:
            progress_bar_paths.set_description(f"path {path}")

            # Iterate through files recursively in the specified directory (if it's a directory)
            # or read the file directly if it's not
            result.add(
                self.lint_path(
                    path,
                    fix=fix,
                    ignore_non_existent_files=ignore_non_existent_files,
                    ignore_files=ignore_files,
                    processes=processes,
                )
            )

            progress_bar_paths.update(1)

        result.stop_timer()
        return result

    def parse_path(
        self,
        path: str,
        recurse: bool = True,
    ) -> Iterator[ParsedString]:
        """Parse a path of sql files.

        NB: This a generator which will yield the result of each file
        within the path iteratively.
        """
        for fname in self.paths_from_path(path):
            if self.formatter:
                self.formatter.dispatch_path(path)
            # Load the file with the config and yield the result.
            raw_file, config, encoding = self._load_raw_file_and_config(
                fname, self.config
            )
            yield self.parse_string(
                raw_file,
                fname=fname,
                recurse=recurse,
                config=config,
                encoding=encoding,
            )
