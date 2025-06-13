"""Defines the linter class."""

import fnmatch
import logging
import os
import time
from collections.abc import Iterator, Sequence
from typing import TYPE_CHECKING, Optional, cast

import regex
from tqdm import tqdm

from sqlfluff.core.config import FluffConfig, progress_bar_configuration
from sqlfluff.core.errors import (
    SQLBaseError,
    SQLFluffSkipFile,
    SQLLexError,
    SQLLintError,
    SQLParseError,
    SQLTemplaterError,
)
from sqlfluff.core.formatter import FormatterInterface
from sqlfluff.core.helpers.file import get_encoding
from sqlfluff.core.linter.common import (
    ParsedString,
    ParsedVariant,
    RenderedFile,
    RuleTuple,
)
from sqlfluff.core.linter.discovery import paths_from_path
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
from sqlfluff.core.rules.fix import LintFix
from sqlfluff.core.rules.noqa import IgnoreMask

if TYPE_CHECKING:  # pragma: no cover
    from sqlfluff.core.dialects import Dialect
    from sqlfluff.core.parser.segments.meta import MetaSegment
    from sqlfluff.core.templaters import RawTemplater, TemplatedFile


RuleTimingsType = list[tuple[str, str, float]]

# Instantiate the linter logger
linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")


class Linter:
    """The interface class to interact with the linter."""

    # Default to allowing process parallelism
    allow_process_parallelism = True

    def __init__(
        self,
        config: Optional[FluffConfig] = None,
        formatter: Optional[FormatterInterface] = None,
        dialect: Optional[str] = None,
        rules: Optional[list[str]] = None,
        user_rules: Optional[list[type[BaseRule]]] = None,
        exclude_rules: Optional[list[str]] = None,
    ) -> None:
        if config and (dialect or rules or exclude_rules):
            raise ValueError(  # pragma: no cover
                "Linter does not support setting both `config` and any of "
                "`dialect`, `rules` or `exclude_rules`. The latter are "
                "provided as convenience methods to avoid needing to "
                "set the `config` object. If using `config`, please "
                "provide all the other values within that object."
            )
        # Use the provided config or create one from the kwargs.
        self.config = config or FluffConfig.from_kwargs(
            dialect=dialect,
            rules=rules,
            exclude_rules=exclude_rules,
            # Don't require a dialect to be provided yet. Defer this until we
            # are actually linting something, since the directory we are linting
            # from may provide additional configuration, including a dialect.
            require_dialect=False,
        )
        # Get the dialect and templater
        self.dialect: "Dialect" = cast("Dialect", self.config.get("dialect_obj"))
        self.templater: "RawTemplater" = cast(
            "RawTemplater", self.config.get("templater_obj")
        )
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

    def rule_tuples(self) -> list[RuleTuple]:
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
    ) -> tuple[str, FluffConfig, str]:
        """Load a raw file and the associated config."""
        file_config = root_config.make_child_from_path(fname)
        config_encoding: str = file_config.get("encoding", default="autodetect")
        encoding = get_encoding(fname=fname, config_encoding=config_encoding)
        # Check file size before loading.
        limit = file_config.get("large_file_skip_byte_limit")

        if limit:
            # make sure the limit becomes an integer
            try:
                limit = int(limit)
            except ValueError:
                raise ValueError(
                    f"""
                large_file_skip_byte_limit parameter from config
                cannot be converted to integer,
                current value {limit}, type {type(limit)}
                """
                )
            except TypeError:
                raise TypeError(
                    f"""
                failed to get large_file_skip_byte_limit parameter from config,
                or it is of invalid type {type(limit)}
                """
                )
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
    ) -> tuple[Optional[Sequence[BaseSegment]], list[SQLLexError]]:
        """Lex a templated file."""
        violations = []
        linter_logger.info("LEXING RAW (%s)", templated_file.fname)
        # Get the lexer
        lexer = Lexer(config=config)
        # Lex the file and log any problems
        try:
            segments, lex_vs = lexer.lex(templated_file)
            # NOTE: There will always be segments, even if it's
            # just an end of file marker.
            assert segments, "The token sequence should never be empty."
            # We might just get the violations as a list
            violations += lex_vs
            linter_logger.info("Lexed segments: %s", [seg.raw for seg in segments])
        except SQLLexError as err:  # pragma: no cover
            linter_logger.info("LEXING FAILED! (%s): %s", templated_file.fname, err)
            violations.append(err)
            return None, violations

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
            indent_balance = sum(getattr(elem, "indent_val", 0) for elem in segments)
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
        new_segments = []
        for segment in segments:
            if segment.is_meta:
                meta_segment = cast("MetaSegment", segment)
                if meta_segment.indent_val != 0:
                    # Don't allow it if we're not linting templating block indents.
                    if not templating_blocks_indent:
                        continue  # pragma: no cover
            new_segments.append(segment)

        # Return new buffer
        return new_segments, violations

    @staticmethod
    def _parse_tokens(
        tokens: Sequence[BaseSegment],
        config: FluffConfig,
        fname: Optional[str] = None,
        parse_statistics: bool = False,
    ) -> tuple[Optional[BaseSegment], list[SQLParseError]]:
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
        linting_errors: list[SQLBaseError],
    ) -> list[SQLBaseError]:
        """Filter a list of lint errors, removing those from the templated slices."""
        # Filter out any linting errors in templated sections if relevant.
        result: list[SQLBaseError] = []
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
        tokens: Optional[Sequence[BaseSegment]]
        parsed_variants: list[ParsedVariant] = []
        _lexing_time = 0.0
        _parsing_time = 0.0

        for idx, variant in enumerate(rendered.templated_variants):
            t0 = time.monotonic()
            linter_logger.info("Parse Rendered. Lexing Variant %s", idx)
            tokens, lex_errors = cls._lex_templated_file(variant, rendered.config)
            t1 = time.monotonic()
            linter_logger.info("Parse Rendered. Parsing Variant %s", idx)
            if tokens:
                parsed, parse_errors = cls._parse_tokens(
                    tokens,
                    rendered.config,
                    fname=rendered.fname,
                    parse_statistics=parse_statistics,
                )
            else:  # pragma: no cover
                parsed = None
                parse_errors = []
            _lt = t1 - t0
            _pt = time.monotonic() - t1
            linter_logger.info(
                "Parse Rendered. Variant %s. Lex in %s. Parse in %s.", idx, _lt, _pt
            )
            parsed_variants.append(
                ParsedVariant(
                    variant,
                    parsed,
                    lex_errors,
                    parse_errors,
                )
            )
            _lexing_time += _lt
            _parsing_time += _pt

        time_dict = {
            **rendered.time_dict,
            "lexing": _lexing_time,
            "parsing": _parsing_time,
        }
        return ParsedString(
            parsed_variants=parsed_variants,
            templating_violations=rendered.templater_violations,
            time_dict=time_dict,
            config=rendered.config,
            fname=rendered.fname,
            source_str=rendered.source_str,
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
        formatter: Optional[FormatterInterface] = None,
    ) -> tuple[BaseSegment, list[SQLBaseError], Optional[IgnoreMask], RuleTimingsType]:
        """Lint and optionally fix a tree object."""
        # Keep track of the linting errors on the very first linter pass. The
        # list of issues output by "lint" and "fix" only includes issues present
        # in the initial SQL code, EXCLUDING any issues that may be created by
        # the fixes themselves.
        initial_linting_errors = []
        # A placeholder for the fixes we had on the previous loop
        last_fixes: Optional[list[LintFix]] = None
        # Keep a set of previous versions to catch infinite loops.
        previous_versions: set[tuple[str, tuple["SourceFix", ...]]] = {(tree.raw, ())}
        # Keep a buffer for recording rule timings.
        rule_timings: RuleTimingsType = []

        # If we are fixing then we want to loop up to the runaway_limit, otherwise just
        # once for linting.
        loop_limit = config.get("runaway_limit") if fix else 1

        # Dispatch the output for the lint header
        if formatter:
            formatter.dispatch_lint_header(
                fname or "<filename>", sorted(rule_pack.codes())
            )

        # Look for comment segments which might indicate lines to ignore.
        disable_noqa_except: Optional[str] = config.get("disable_noqa_except")
        if not config.get("disable_noqa") or disable_noqa_except:
            allowed_rules_ref_map = cls.allowed_rule_ref_map(
                rule_pack.reference_map, disable_noqa_except
            )
            ignore_mask, ivs = IgnoreMask.from_tree(tree, allowed_rules_ref_map)
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
                    f"\n\nEntering linter phase {phase}, loop {loop + 1}/{loop_limit}\n"
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
                        elif fixes == last_fixes:
                            # If we generate the same fixes two times in a row,
                            # that means we're in a loop, and we want to stop.
                            # (Fixes should address issues, hence different
                            # and/or fewer fixes next time.)
                            # This is most likely because fixes could not be safely
                            # applied last time, so we should stop gracefully.
                            linter_logger.debug(
                                f"Fixes generated for {crawler.code} are the same as "
                                "the previous pass. Assuming that we cannot apply them "
                                "safely. Passing gracefully."
                            )
                        else:
                            # This is the happy path. We have fixes, now we want to
                            # apply them.
                            last_fixes = fixes
                            new_tree, _, _, _valid = apply_fixes(
                                tree,
                                config.get("dialect_obj"),
                                crawler.code,
                                anchor_info,
                                fix_even_unparsable=config.get("fix_even_unparsable"),
                            )

                            # Check for infinite loops. We use a combination of the
                            # fixed templated file and the list of source fixes to
                            # apply.
                            loop_check_tuple = (
                                new_tree.raw,
                                tuple(new_tree.source_fixes),
                            )
                            # Was anything actually applied? If not, then the fixes we
                            # had cannot be safely applied and we should stop trying.
                            if loop_check_tuple == (tree.raw, tuple(tree.source_fixes)):
                                linter_logger.debug(
                                    f"Fixes for {crawler.code} could not be safely be "
                                    "applied. Likely due to initially unparsable file."
                                )
                            elif not _valid:
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
        formatter: Optional[FormatterInterface] = None,
        encoding: str = "utf8",
    ) -> LintedFile:
        """Lint a ParsedString and return a LintedFile."""
        violations = parsed.violations
        time_dict = parsed.time_dict
        tree: Optional[BaseSegment] = None
        templated_file: Optional[TemplatedFile] = None
        t0 = time.monotonic()

        # First identify the root variant. That's the first variant
        # that successfully parsed.
        root_variant: Optional[ParsedVariant] = None
        for variant in parsed.parsed_variants:
            if variant.tree:
                root_variant = variant
                break
        else:
            linter_logger.info(
                "lint_parsed found no valid root variant for %s", parsed.fname
            )

        # If there is a root variant, handle that first.
        if root_variant:
            linter_logger.info("lint_parsed - linting root variant (%s)", parsed.fname)
            assert root_variant.tree  # We just checked this.
            (
                fixed_tree,
                initial_linting_errors,
                ignore_mask,
                rule_timings,
            ) = cls.lint_fix_parsed(
                root_variant.tree,
                config=parsed.config,
                rule_pack=rule_pack,
                fix=fix,
                fname=parsed.fname,
                templated_file=variant.templated_file,
                formatter=formatter,
            )

            # Set legacy variables for now
            # TODO: Revise this
            templated_file = variant.templated_file
            tree = fixed_tree

            # We're only going to return the *initial* errors, rather
            # than any generated during the fixing cycle.
            violations += initial_linting_errors

            # Attempt to lint other variants if they exist.
            # TODO: Revise whether this is sensible...
            for idx, alternate_variant in enumerate(parsed.parsed_variants):
                if alternate_variant is variant or not alternate_variant.tree:
                    continue
                linter_logger.info("lint_parsed - linting alt variant (%s)", idx)
                (
                    _,  # Fixed Tree
                    alt_linting_errors,
                    _,  # Ignore Mask
                    _,  # Timings
                ) = cls.lint_fix_parsed(
                    alternate_variant.tree,
                    config=parsed.config,
                    rule_pack=rule_pack,
                    fix=fix,
                    fname=parsed.fname,
                    templated_file=alternate_variant.templated_file,
                    formatter=formatter,
                )
                violations += alt_linting_errors

        # If no root variant, we should still apply ignores to any parsing
        # or templating fails.
        else:
            rule_timings = []
            disable_noqa_except: Optional[str] = parsed.config.get(
                "disable_noqa_except"
            )
            if parsed.config.get("disable_noqa") and not disable_noqa_except:
                # NOTE: This path is only accessible if there is no valid `tree`
                # which implies that there was a fatal templating fail. Even an
                # unparsable file will still have a valid tree.
                ignore_mask = None
            else:
                # Templating and/or parsing have failed. Look for "noqa"
                # comments (the normal path for identifying these comments
                # requires access to the parse tree, and because of the failure,
                # we don't have a parse tree).
                allowed_rules_ref_map = cls.allowed_rule_ref_map(
                    rule_pack.reference_map, disable_noqa_except
                )
                ignore_mask, ignore_violations = IgnoreMask.from_source(
                    parsed.source_str,
                    [
                        lm
                        for lm in parsed.config.get("dialect_obj").lexer_matchers
                        if lm.name == "inline_comment"
                    ][0],
                    allowed_rules_ref_map,
                )
                violations += ignore_violations

        # Update the timing dict
        time_dict["linting"] = time.monotonic() - t0

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
            templated_file=templated_file,
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
                formatter.dispatch_dialect_warning(
                    # The dialect property is the string, not the dialect object
                    cast(str, parsed.config.get("dialect"))
                )

        return linted_file

    @classmethod
    def allowed_rule_ref_map(
        cls, reference_map: dict[str, set[str]], disable_noqa_except: Optional[str]
    ) -> dict[str, set[str]]:
        """Generate a noqa rule reference map."""
        # disable_noqa_except is not set, return the entire map.
        if not disable_noqa_except:
            return reference_map
        output_map = reference_map
        # Add the special rules so they can be excluded for `disable_noqa_except` usage
        for special_rule in ["PRS", "LXR", "TMP"]:
            output_map[special_rule] = {special_rule}
        # Expand glob usage of rules
        unexpanded_rules = tuple(r.strip() for r in disable_noqa_except.split(","))
        noqa_set = set()
        for r in unexpanded_rules:
            for x in fnmatch.filter(output_map.keys(), r):
                noqa_set |= output_map.get(x, set())
        # Return a new map with only the excluded rules
        return {k: v.intersection(noqa_set) for k, v in output_map.items()}

    @classmethod
    def lint_rendered(
        cls,
        rendered: RenderedFile,
        rule_pack: RulePack,
        fix: bool = False,
        formatter: Optional[FormatterInterface] = None,
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
        linter_logger.info("Rendering String [%s] (%s)", self.templater.name, fname)

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
                f"Attempt to set templater to {config.get('templater_obj').name} "
                f"failed. Using {self.templater.name} templater. Templater cannot "
                "be set in a .sqlfluff file in a subdirectory of the current "
                "working directory. It can be set in a .sqlfluff in the current "
                "working directory. See Nesting section of the docs for more "
                "details."
            )

        variant_limit = config.get("render_variant_limit")
        templated_variants: list[TemplatedFile] = []
        templater_violations: list[SQLTemplaterError] = []

        try:
            for variant, templater_errs in self.templater.process_with_variants(
                in_str=in_str, fname=fname, config=config, formatter=self.formatter
            ):
                if variant:
                    templated_variants.append(variant)
                # NOTE: We could very easily end up with duplicate errors between
                # different variants and this code doesn't currently do any
                # deduplication between them. That will be resolved in further
                # testing.
                # TODO: Resolve potential duplicate templater violations between
                # variants before we enable jinja variant linting by default.
                templater_violations += templater_errs
                if len(templated_variants) >= variant_limit:
                    # Stop if we hit the limit.
                    break
        except SQLTemplaterError as templater_err:
            # Fatal templating error. Capture it and don't generate a variant.
            templater_violations.append(templater_err)
        except SQLFluffSkipFile as skip_file_err:  # pragma: no cover
            linter_logger.warning(str(skip_file_err))

        if not templated_variants:
            linter_logger.info("TEMPLATING FAILED: %s", templater_violations)

        linter_logger.info("Rendered %s variants", len(templated_variants))

        # Record time
        time_dict = {"templating": time.monotonic() - t0}

        return RenderedFile(
            templated_variants,
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
        violations: list[SQLBaseError] = []

        # Dispatch the output for the template header (including the config diff)
        if self.formatter:
            self.formatter.dispatch_template_header(fname, self.config, config)

        # Just use the local config from here:
        config = (config or self.config).copy()

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
    ) -> tuple[BaseSegment, list[SQLBaseError]]:
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
    ) -> list[SQLBaseError]:
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
        paths: tuple[str, ...],
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

        expanded_paths: list[str] = []
        expanded_path_to_linted_dir = {}
        sql_exts = self.config.get("sql_file_exts", default=".sql").lower().split(",")

        for path in paths:
            linted_dir = LintedDir(path, retain_files=retain_files)
            result.add(linted_dir)
            for fname in paths_from_path(
                path,
                ignore_non_existent_files=ignore_non_existent_files,
                ignore_files=ignore_files,
                target_file_exts=sql_exts,
            ):
                expanded_paths.append(fname)
                expanded_path_to_linted_dir[fname] = linted_dir

        files_count = len(expanded_paths)
        if processes is None:
            processes = self.config.get("processes", default=1)
        assert processes is not None
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
        sql_exts = self.config.get("sql_file_exts", default=".sql").lower().split(",")
        for fname in paths_from_path(
            path,
            target_file_exts=sql_exts,
        ):
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
