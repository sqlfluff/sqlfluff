"""Defines the linter class."""

import logging
import os
import time
from typing import (
    TYPE_CHECKING,
    Any,
    Iterable,
    Iterator,
    List,
    Optional,
    Sequence,
    Set,
    Tuple,
    Type,
    cast,
)

import pathspec
import regex
from tqdm import tqdm

from sqlfluff.core.config import ConfigLoader, FluffConfig, progress_bar_configuration
from sqlfluff.core.errors import (
    SQLBaseError,
    SQLFluffSkipFile,
    SQLFluffUserError,
    SQLLexError,
    SQLLintError,
    SQLParseError,
)
from sqlfluff.core.helpers.file import get_encoding
from sqlfluff.core.linter.common import ParsedString, RenderedFile, RuleTuple
from sqlfluff.core.linter.fix import apply_fixes, compute_anchor_edit_info
from sqlfluff.core.linter.linted_dir import LintedDir
from sqlfluff.core.linter.linted_file import (
    TMP_PRS_ERROR_TYPES,
    FileTimings,
    LintedFile,
)
from sqlfluff.core.linter.linting_result import LintingResult
from sqlfluff.core.parser import Lexer, Parser
from sqlfluff.core.parser.segments.base import BaseSegment, SourceFix
from sqlfluff.core.rules import BaseRule, RulePack, get_ruleset
from sqlfluff.core.rules.noqa import IgnoreMask

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.parser.segments.meta import MetaSegment
    from sqlfluff.core.templaters import TemplatedFile


WalkableType = Iterable[Tuple[str, Optional[List[str]], List[str]]]
RuleTimingsType = List[Tuple[str, str, float]]

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
        user_rules: Optional[List[Type[BaseRule]]] = None,
        exclude_rules: Optional[List[str]] = None,
    ) -> None:
        # Store the config object
        self.config = FluffConfig.from_kwargs(
            config=config,
            dialect=dialect,
            rules=rules,
            exclude_rules=exclude_rules,
            # Don't require a dialect to be provided yet. Defer this until we
            # are actually linting something, since the directory we are linting
            # from may provide additional configuration, including a dialect.
            require_dialect=False,
        )
        # Get the dialect and templater
        self.dialect = self.config.get("dialect_obj")
        self.templater = self.config.get("templater_obj")
        # Store the formatter for output
        self.formatter = formatter
        # Store references to user rule classes
        self.user_rules = user_rules or []

    def get_rulepack(self, config: Optional[FluffConfig] = None) -> RulePack:
        """Get hold of a set of rules."""
        rs = get_ruleset()
        # Register any user rules
        for rule in self.user_rules:
            rs.register(rule)
        cfg = config or self.config
        return rs.get_rulepack(config=cfg)

    def rule_tuples(self) -> List[RuleTuple]:
        """A simple pass through to access the rule tuples of the rule set."""
        rs = self.get_rulepack()
        return [
            RuleTuple(rule.code, rule.name, rule.description, rule.groups, rule.aliases)
            for rule in rs.rules
        ]

    # #### Static methods
    # These are the building blocks of the linting process.

    @staticmethod
    def load_raw_file_and_config(
        fname: str, root_config: FluffConfig
    ) -> Tuple[str, FluffConfig, str]:
        """Load a raw file and the associated config."""
        file_config = root_config.make_child_from_path(fname)
        config_encoding: str = file_config.get("encoding", default="autodetect")
        encoding = get_encoding(fname=fname, config_encoding=config_encoding)
        # Check file size before loading.
        limit = file_config.get("large_file_skip_byte_limit")
        if limit:
            # Get the file size
            file_size = os.path.getsize(fname)
            if file_size > limit:
                raise SQLFluffSkipFile(
                    f"Length of file {fname!r} is {file_size} bytes which is over "
                    f"the limit of {limit} bytes. Skipping to avoid parser lock. "
                    "Users can increase this limit in their config by setting the "
                    "'large_file_skip_byte_limit' value, or disable by setting it "
                    "to zero."
                )
        with open(fname, encoding=encoding, errors="backslashreplace") as target_file:
            raw_file = target_file.read()
        # Scan the raw file for config commands.
        file_config.process_raw_file_for_config(raw_file, fname)
        # Return the raw file and config
        return raw_file, file_config, encoding

    @staticmethod
    def _normalise_newlines(string: str) -> str:
        """Normalise newlines to unix-style line endings."""
        return regex.sub(r"\r\n|\r", "\n", string)

    @staticmethod
    def _lex_templated_file(
        templated_file: "TemplatedFile", config: FluffConfig
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
        except SQLLexError as err:  # pragma: no cover
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
            indent_balance = sum(getattr(elem, "indent_val", 0) for elem in tokens)
            if indent_balance != 0:  # pragma: no cover
                linter_logger.debug(
                    "Indent balance test failed for %r. Template indents will not be "
                    "linted for this file.",
                    templated_file.fname,
                )
                # Don't enable the templating blocks.
                templating_blocks_indent = False

        # The file will have been lexed without config, so check all indents
        # are enabled.
        new_tokens = []
        for token in tokens:
            if token.is_meta:
                token = cast("MetaSegment", token)
                if token.indent_val != 0:
                    # Don't allow it if we're not linting templating block indents.
                    if not templating_blocks_indent:
                        continue  # pragma: no cover
            new_tokens.append(token)

        # Return new buffer
        return new_tokens, violations, config

    @staticmethod
    def _parse_tokens(
        tokens: Sequence[BaseSegment],
        config: FluffConfig,
        fname: Optional[str] = None,
        parse_statistics: bool = False,
    ) -> Tuple[Optional[BaseSegment], List[SQLParseError]]:
        parser = Parser(config=config)
        violations = []
        # Parse the file and log any problems
        try:
            parsed: Optional[BaseSegment] = parser.parse(
                # Regardless of how the sequence was passed in, we should
                # coerce it to a tuple here, before we head deeper into
                # the parsing process.
                tuple(tokens),
                fname=fname,
                parse_statistics=parse_statistics,
            )
        except SQLParseError as err:
            linter_logger.info("PARSING FAILED! : %s", err)
            violations.append(err)
            return None, violations

        if parsed is None:  # pragma: no cover
            return None, violations

        linter_logger.info("\n###\n#\n# {}\n#\n###".format("Parsed Tree:"))
        linter_logger.info("\n" + parsed.stringify())
        # We may succeed parsing, but still have unparsable segments. Extract them
        # here.
        for unparsable in parsed.iter_unparsables():
            # No exception has been raised explicitly, but we still create one here
            # so that we can use the common interface
            assert unparsable.pos_marker
            violations.append(
                SQLParseError(
                    "Line {0[0]}, Position {0[1]}: Found unparsable section: "
                    "{1!r}".format(
                        unparsable.pos_marker.working_loc,
                        (
                            unparsable.raw
                            if len(unparsable.raw) < 40
                            else unparsable.raw[:40] + "..."
                        ),
                    ),
                    segment=unparsable,
                )
            )
            linter_logger.info("Found unparsable segment...")
            linter_logger.info(unparsable.stringify())
        return parsed, violations

    @staticmethod
    def remove_templated_errors(
        linting_errors: List[SQLBaseError],
    ) -> List[SQLBaseError]:
        """Filter a list of lint errors, removing those from the templated slices."""
        # Filter out any linting errors in templated sections if relevant.
        result: List[SQLBaseError] = []
        for e in linting_errors:
            if isinstance(e, SQLLintError):
                assert e.segment.pos_marker
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
    def _report_conflicting_fixes_same_anchor(message: str) -> None:  # pragma: no cover
        # This function exists primarily in order to let us monkeypatch it at
        # runtime (replacing it with a function that raises an exception).
        linter_logger.critical(message)

    @staticmethod
    def _warn_unfixable(code: str) -> None:
        linter_logger.warning(
            f"One fix for {code} not applied, it would re-cause the same error."
        )

    # ### Class Methods
    # These compose the base static methods into useful recipes.

    @classmethod
    def parse_rendered(
        cls,
        rendered: RenderedFile,
        parse_statistics: bool = False,
    ) -> ParsedString:
        """Parse a rendered file."""
        t0 = time.monotonic()
        violations = cast(List[SQLBaseError], rendered.templater_violations)
        tokens: Optional[Sequence[BaseSegment]]
        if rendered.templated_file is not None:
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
                fname=rendered.fname,
                parse_statistics=parse_statistics,
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
            rendered.source_str,
        )

    @classmethod
    def lint_fix_parsed(
        cls,
        tree: BaseSegment,
        config: FluffConfig,
        rule_pack: RulePack,
        fix: bool = False,
        fname: Optional[str] = None,
        templated_file: Optional["TemplatedFile"] = None,
        formatter: Any = None,
    ) -> Tuple[BaseSegment, List[SQLBaseError], Optional[IgnoreMask], RuleTimingsType]:
        """Lint and optionally fix a tree object."""
        # Keep track of the linting errors on the very first linter pass. The
        # list of issues output by "lint" and "fix" only includes issues present
        # in the initial SQL code, EXCLUDING any issues that may be created by
        # the fixes themselves.
        initial_linting_errors = []
        # A placeholder for the fixes we had on the previous loop
        last_fixes = None
        # Keep a set of previous versions to catch infinite loops.
        previous_versions: Set[Tuple[str, Tuple["SourceFix", ...]]] = {(tree.raw, ())}
        # Keep a buffer for recording rule timings.
        rule_timings: RuleTimingsType = []

        # If we are fixing then we want to loop up to the runaway_limit, otherwise just
        # once for linting.
        loop_limit = config.get("runaway_limit") if fix else 1

        # Dispatch the output for the lint header
        if formatter:
            formatter.dispatch_lint_header(fname, sorted(rule_pack.codes()))

        # Look for comment segments which might indicate lines to ignore.
        if not config.get("disable_noqa"):
            ignore_mask, ivs = IgnoreMask.from_tree(tree, rule_pack.reference_map)
            initial_linting_errors += ivs
        else:
            ignore_mask = None

        save_tree = tree
        # There are two phases of rule running.
        # 1. The main loop is for most rules. These rules are assumed to
        # interact and cause a cascade of fixes requiring multiple passes.
        # These are run the `runaway_limit` number of times (default 10).
        # 2. The post loop is for post-processing rules, not expected to trigger
        # any downstream rules, e.g. capitalization fixes. They are run on the
        # first loop and then twice at the end (once to fix, and once again to
        # check result of fixes), but not in the intervening loops.
        phases = ["main"]
        if fix:
            phases.append("post")
        for phase in phases:
            if len(phases) > 1:
                rules_this_phase = [
                    rule for rule in rule_pack.rules if rule.lint_phase == phase
                ]
            else:
                rules_this_phase = rule_pack.rules
            for loop in range(loop_limit if phase == "main" else 2):

                def is_first_linter_pass() -> bool:
                    return phase == phases[0] and loop == 0

                # Additional newlines are to assist in scanning linting loops
                # during debugging.
                linter_logger.info(
                    f"\n\nEntering linter phase {phase}, "
                    f"loop {loop + 1}/{loop_limit}\n"
                )
                changed = False

                if is_first_linter_pass():
                    # In order to compute initial_linting_errors correctly, need
                    # to run all rules on the first loop of the main phase.
                    rules_this_phase = rule_pack.rules
                progress_bar_crawler = tqdm(
                    rules_this_phase,
                    desc="lint by rules",
                    leave=False,
                    disable=progress_bar_configuration.disable_progress_bar,
                )

                for crawler in progress_bar_crawler:
                    # Performance: After first loop pass, skip rules that don't
                    # do fixes. Any results returned won't be seen by the user
                    # anyway (linting errors ADDED by rules changing SQL, are
                    # not reported back to the user - only initial linting errors),
                    # so there's absolutely no reason to run them.
                    if (
                        fix
                        and not is_first_linter_pass()
                        and not crawler.is_fix_compatible
                    ):
                        continue

                    progress_bar_crawler.set_description(f"rule {crawler.code}")
                    t0 = time.monotonic()

                    # fixes should be a dict {} with keys edit, delete, create
                    # delete is just a list of segments to delete
                    # edit and create are list of tuples. The first element is
                    # the "anchor", the segment to look for either to edit or to
                    # insert BEFORE. The second is the element to insert or create.
                    linting_errors, _, fixes, _ = crawler.crawl(
                        tree,
                        dialect=config.get("dialect_obj"),
                        fix=fix,
                        templated_file=templated_file,
                        ignore_mask=ignore_mask,
                        fname=fname,
                        config=config,
                    )
                    if is_first_linter_pass():
                        initial_linting_errors += linting_errors

                    if fix and fixes:
                        linter_logger.info(f"Applying Fixes [{crawler.code}]: {fixes}")
                        # Do some sanity checks on the fixes before applying.
                        anchor_info = compute_anchor_edit_info(fixes)
                        if any(
                            not info.is_valid for info in anchor_info.values()
                        ):  # pragma: no cover
                            message = (
                                f"Rule {crawler.code} returned conflicting "
                                "fixes with the same anchor. This is only "
                                "supported for create_before+create_after, so "
                                "the fixes will not be applied. "
                            )
                            for uuid, info in anchor_info.items():
                                if not info.is_valid:
                                    message += f"\n{uuid}:"
                                    for _fix in info.fixes:
                                        message += f"\n    {_fix}"
                            cls._report_conflicting_fixes_same_anchor(message)
                            for lint_result in linting_errors:
                                lint_result.fixes = []
                        elif fixes == last_fixes:  # pragma: no cover
                            # If we generate the same fixes two times in a row,
                            # that means we're in a loop, and we want to stop.
                            # (Fixes should address issues, hence different
                            # and/or fewer fixes next time.)
                            cls._warn_unfixable(crawler.code)
                        else:
                            # This is the happy path. We have fixes, now we want to
                            # apply them.
                            last_fixes = fixes
                            new_tree, _, _, _valid = apply_fixes(
                                tree,
                                config.get("dialect_obj"),
                                crawler.code,
                                anchor_info,
                            )
                            # Check for infinite loops. We use a combination of the
                            # fixed templated file and the list of source fixes to
                            # apply.
                            loop_check_tuple = (
                                new_tree.raw,
                                tuple(new_tree.source_fixes),
                            )
                            if not _valid:
                                # The fixes result in an invalid file. Don't apply
                                # the fix and skip onward. Show a warning.
                                linter_logger.warning(
                                    f"Fixes for {crawler.code} not applied, as it "
                                    "would result in an unparsable file. Please "
                                    "report this as a bug with a minimal query "
                                    "which demonstrates this warning."
                                )
                            elif loop_check_tuple not in previous_versions:
                                # We've not seen this version of the file so
                                # far. Continue.
                                tree = new_tree
                                previous_versions.add(loop_check_tuple)
                                changed = True
                                continue
                            else:
                                # Applying these fixes took us back to a state
                                # which we've seen before. We're in a loop, so
                                # we want to stop.
                                cls._warn_unfixable(crawler.code)

                    # Record rule timing
                    rule_timings.append(
                        (crawler.code, crawler.name, time.monotonic() - t0)
                    )

                if fix and not changed:
                    # We did not change the file. Either the file is clean (no
                    # fixes), or any fixes which are present will take us back
                    # to a previous state.
                    linter_logger.info(
                        f"Fix loop complete for {phase} phase. Stability "
                        f"achieved after {loop}/{loop_limit} loops."
                    )
                    break
            else:
                if fix:
                    # The linter loop hit the limit before reaching a stable point
                    # (i.e. free of lint errors). If this happens, it's usually
                    # because one or more rules produced fixes which did not address
                    # the original issue **or** created new issues.
                    linter_logger.warning(
                        f"Loop limit on fixes reached [{loop_limit}]."
                    )

                    # Discard any fixes for the linting errors, since they caused a
                    # loop. IMPORTANT: By doing this, we are telling SQLFluff that
                    # these linting errors are "unfixable". This is important,
                    # because when "sqlfluff fix" encounters unfixable lint errors,
                    # it exits with a "failure" exit code, which is exactly what we
                    # want in this situation. (Reason: Although this is more of an
                    # internal SQLFluff issue, users deserve to know about it,
                    # because it means their file(s) weren't fixed.
                    for violation in initial_linting_errors:
                        if isinstance(violation, SQLLintError):
                            violation.fixes = []

                    # Return the original parse tree, before any fixes were applied.
                    # Reason: When the linter hits the loop limit, the file is often
                    # messy, e.g. some of the fixes were applied repeatedly, possibly
                    # other weird things. We don't want the user to see this junk!
                    return save_tree, initial_linting_errors, ignore_mask, rule_timings

        if config.get("ignore_templated_areas", default=True):
            initial_linting_errors = cls.remove_templated_errors(initial_linting_errors)

        linter_logger.info("\n###\n#\n# {}\n#\n###".format("Fixed Tree:"))
        linter_logger.info("\n" + tree.stringify())

        return tree, initial_linting_errors, ignore_mask, rule_timings

    @classmethod
    def lint_parsed(
        cls,
        parsed: ParsedString,
        rule_pack: RulePack,
        fix: bool = False,
        formatter: Any = None,
        encoding: str = "utf8",
    ) -> LintedFile:
        """Lint a ParsedString and return a LintedFile."""
        violations = parsed.violations
        time_dict = parsed.time_dict
        tree: Optional[BaseSegment]
        if parsed.tree:
            t0 = time.monotonic()
            linter_logger.info("LINTING (%s)", parsed.fname)
            (
                tree,
                initial_linting_errors,
                ignore_mask,
                rule_timings,
            ) = cls.lint_fix_parsed(
                parsed.tree,
                config=parsed.config,
                rule_pack=rule_pack,
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
            ignore_mask = None
            rule_timings = []
            if not parsed.config.get("disable_noqa"):
                # Templating and/or parsing have failed. Look for "noqa"
                # comments (the normal path for identifying these comments
                # requires access to the parse tree, and because of the failure,
                # we don't have a parse tree).
                ignore_mask, ignore_violations = IgnoreMask.from_source(
                    parsed.source_str,
                    [
                        lm
                        for lm in parsed.config.get("dialect_obj").lexer_matchers
                        if lm.name == "inline_comment"
                    ][0],
                    rule_pack.reference_map,
                )
                violations += ignore_violations

        # We process the ignore config here if appropriate
        for violation in violations:
            violation.ignore_if_in(parsed.config.get("ignore"))
            violation.warning_if_in(parsed.config.get("warnings"))

        linted_file = LintedFile(
            parsed.fname,
            # Deduplicate violations
            LintedFile.deduplicate_in_source_space(violations),
            FileTimings(time_dict, rule_timings),
            tree,
            ignore_mask=ignore_mask,
            templated_file=parsed.templated_file,
            encoding=encoding,
        )

        # This is the main command line output from linting.
        if formatter:
            formatter.dispatch_file_violations(
                parsed.fname,
                linted_file,
                only_fixable=fix,
                warn_unused_ignores=parsed.config.get("warn_unused_ignores"),
            )

        # Safety flag for unset dialects
        if linted_file.get_violations(
            fixable=True if fix else None, types=SQLParseError
        ):
            if formatter:  # pragma: no cover TODO?
                formatter.dispatch_dialect_warning(parsed.config.get("dialect"))

        return linted_file

    @classmethod
    def lint_rendered(
        cls,
        rendered: RenderedFile,
        rule_pack: RulePack,
        fix: bool = False,
        formatter: Any = None,
    ) -> LintedFile:
        """Take a RenderedFile and return a LintedFile."""
        parsed = cls.parse_rendered(rendered)
        return cls.lint_parsed(
            parsed,
            rule_pack=rule_pack,
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

        # Since Linter.__init__() does not require a dialect to be specified,
        # check for one now. (We're processing a string, not a file, so we're
        # not going to pick up a .sqlfluff or other config file to provide a
        # missing dialect at this point.)
        config.verify_dialect_specified()
        if not config.get("templater_obj") == self.templater:
            linter_logger.warning(
                (
                    f"Attempt to set templater to {config.get('templater_obj').name} "
                    f"failed. Using {self.templater.name} templater. Templater cannot "
                    "be set in a .sqlfluff file in a subdirectory of the current "
                    "working directory. It can be set in a .sqlfluff in the current "
                    "working directory. See Nesting section of the docs for more "
                    "details."
                )
            )
        try:
            templated_file, templater_violations = self.templater.process(
                in_str=in_str, fname=fname, config=config, formatter=self.formatter
            )
        except SQLFluffSkipFile as s:  # pragma: no cover
            linter_logger.warning(str(s))
            templated_file = None
            templater_violations = []

        if templated_file is None:
            linter_logger.info("TEMPLATING FAILED: %s", templater_violations)

        # Record time
        time_dict = {"templating": time.monotonic() - t0}

        return RenderedFile(
            templated_file,
            templater_violations,
            config,
            time_dict,
            fname,
            encoding,
            in_str,
        )

    def render_file(self, fname: str, root_config: FluffConfig) -> RenderedFile:
        """Load and render a file with relevant config."""
        # Load the raw file.
        raw_file, config, encoding = self.load_raw_file_and_config(fname, root_config)
        # Render the file
        return self.render_string(raw_file, fname, config, encoding)

    def parse_string(
        self,
        in_str: str,
        fname: str = "<string>",
        config: Optional[FluffConfig] = None,
        encoding: str = "utf-8",
        parse_statistics: bool = False,
    ) -> ParsedString:
        """Parse a string."""
        violations: List[SQLBaseError] = []

        # Dispatch the output for the template header (including the config diff)
        if self.formatter:
            self.formatter.dispatch_template_header(fname, self.config, config)

        # Just use the local config from here:
        config = config or self.config

        # Scan the raw file for config commands.
        config.process_raw_file_for_config(in_str, fname)
        rendered = self.render_string(in_str, fname, config, encoding)
        violations += rendered.templater_violations

        # Dispatch the output for the parse header
        if self.formatter:
            self.formatter.dispatch_parse_header(fname)

        return self.parse_rendered(rendered, parse_statistics=parse_statistics)

    def fix(
        self,
        tree: BaseSegment,
        config: Optional[FluffConfig] = None,
        fname: Optional[str] = None,
        templated_file: Optional["TemplatedFile"] = None,
    ) -> Tuple[BaseSegment, List[SQLBaseError]]:
        """Return the fixed tree and violations from lintfix when we're fixing."""
        config = config or self.config
        rule_pack = self.get_rulepack(config=config)
        fixed_tree, violations, _, _ = self.lint_fix_parsed(
            tree,
            config,
            rule_pack,
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
        templated_file: Optional["TemplatedFile"] = None,
    ) -> List[SQLBaseError]:
        """Return just the violations from lintfix when we're only linting."""
        config = config or self.config
        rule_pack = self.get_rulepack(config=config)
        _, violations, _, _ = self.lint_fix_parsed(
            tree,
            config,
            rule_pack,
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
        rule_pack = self.get_rulepack(config=config)
        # Lint the file and return the LintedFile
        return self.lint_parsed(
            parsed,
            rule_pack,
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
                raise SQLFluffUserError(
                    f"Specified path does not exist. Check it/they exist(s): {path}."
                )

        # Files referred to exactly are also ignored if
        # matched, but we warn the users when that happens
        is_exact_file = os.path.isfile(path)

        path_walk: WalkableType
        if is_exact_file:
            # When the exact file to lint is passed, we
            # fill path_walk with an input that follows
            # the structure of `os.walk`:
            #   (root, directories, files)
            dirpath = os.path.dirname(path)
            files = [os.path.basename(path)]
            path_walk = [(dirpath, None, files)]
        else:
            path_walk = list(os.walk(path))

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
        path_walk += path_walk_ignore_file

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
                    # We don't need to process the ignore file any further
                    continue

                # We won't purge files *here* because there's an edge case
                # that the ignore file is processed after the sql file.

                # Scan for remaining files
                for ext in (
                    self.config.get("sql_file_exts", default=".sql").lower().split(",")
                ):
                    # is it a sql file?
                    if fname.lower().endswith(ext):
                        buffer.append(fpath)

        if not ignore_files:
            return sorted(buffer)

        # Check the buffer for ignore items and normalise the rest.
        # It's a set, so we can do natural deduplication.
        filtered_buffer = set()

        for fpath in buffer:
            abs_fpath = os.path.abspath(fpath)
            for ignore_base, ignore_spec in ignores.items():
                abs_ignore_base = os.path.abspath(ignore_base)
                if abs_fpath.startswith(
                    abs_ignore_base
                    + (
                        ""
                        if os.path.dirname(abs_ignore_base) == abs_ignore_base
                        else os.sep
                    )
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
                npath = os.path.normpath(fpath)
                # For debugging, log if we already have the file.
                if npath in filtered_buffer:
                    linter_logger.debug(  # pragma: no cover
                        "Developer Warning: Path crawler attempted to "
                        "requeue the same file twice. %s is already in "
                        "filtered buffer.",
                        npath,
                    )
                filtered_buffer.add(npath)

        # Return a sorted list
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
        processes: Optional[int] = None,
    ) -> LintedDir:
        """Lint a path."""
        return self.lint_paths(
            (path,), fix, ignore_non_existent_files, ignore_files, processes
        ).paths[0]

    def lint_paths(
        self,
        paths: Tuple[str, ...],
        fix: bool = False,
        ignore_non_existent_files: bool = False,
        ignore_files: bool = True,
        processes: Optional[int] = None,
        apply_fixes: bool = False,
        fixed_file_suffix: str = "",
        fix_even_unparsable: bool = False,
        retain_files: bool = True,
    ) -> LintingResult:
        """Lint an iterable of paths."""
        # If no paths specified - assume local
        if not paths:  # pragma: no cover
            paths = (os.getcwd(),)
        # Set up the result to hold what we get back
        result = LintingResult()

        expanded_paths: List[str] = []
        expanded_path_to_linted_dir = {}
        for path in paths:
            linted_dir = LintedDir(path, retain_files=retain_files)
            result.add(linted_dir)
            for fname in self.paths_from_path(
                path,
                ignore_non_existent_files=ignore_non_existent_files,
                ignore_files=ignore_files,
            ):
                expanded_paths.append(fname)
                expanded_path_to_linted_dir[fname] = linted_dir

        files_count = len(expanded_paths)
        if processes is None:
            processes = self.config.get("processes", default=1)
        # Hard set processes to 1 if only 1 file is queued.
        # The overhead will never be worth it with one file.
        if files_count == 1:
            processes = 1

        # to avoid circular import
        from sqlfluff.core.linter.runner import get_runner

        runner, effective_processes = get_runner(
            self,
            self.config,
            processes=processes,
            allow_process_parallelism=self.allow_process_parallelism,
        )

        if self.formatter and effective_processes != 1:
            self.formatter.dispatch_processing_header(effective_processes)

        # Show files progress bar only when there is more than one.
        first_path = expanded_paths[0] if expanded_paths else ""
        progress_bar_files = tqdm(
            total=files_count,
            desc=f"file {first_path}",
            leave=False,
            disable=files_count <= 1 or progress_bar_configuration.disable_progress_bar,
        )

        for i, linted_file in enumerate(runner.run(expanded_paths, fix), start=1):
            linted_dir = expanded_path_to_linted_dir[linted_file.path]
            linted_dir.add(linted_file)
            # If any fatal errors, then stop iteration.
            if any(v.fatal for v in linted_file.violations):  # pragma: no cover
                linter_logger.error("Fatal linting error. Halting further linting.")
                break

            # If we're applying fixes, then do that here.
            if apply_fixes:
                num_tmp_prs_errors = linted_file.num_violations(
                    types=TMP_PRS_ERROR_TYPES,
                    filter_ignore=False,
                    filter_warning=False,
                )
                if fix_even_unparsable or num_tmp_prs_errors == 0:
                    linted_file.persist_tree(
                        suffix=fixed_file_suffix, formatter=self.formatter
                    )

            # Progress bar for files is rendered only when there is more than one file.
            # Additionally, as it's updated after each loop, we need to get file name
            # from the next loop. This is why `enumerate` starts with `1` and there
            # is `i < len` to not exceed files list length.
            progress_bar_files.update(n=1)
            if i < len(expanded_paths):
                progress_bar_files.set_description(f"file {expanded_paths[i]}")

        result.stop_timer()
        return result

    def parse_path(
        self,
        path: str,
        parse_statistics: bool = False,
    ) -> Iterator[ParsedString]:
        """Parse a path of sql files.

        NB: This a generator which will yield the result of each file
        within the path iteratively.
        """
        for fname in self.paths_from_path(path):
            if self.formatter:
                self.formatter.dispatch_path(path)
            # Load the file with the config and yield the result.
            try:
                raw_file, config, encoding = self.load_raw_file_and_config(
                    fname, self.config
                )
            except SQLFluffSkipFile as s:
                linter_logger.warning(str(s))
                continue
            yield self.parse_string(
                raw_file,
                fname=fname,
                config=config,
                encoding=encoding,
                parse_statistics=parse_statistics,
            )
