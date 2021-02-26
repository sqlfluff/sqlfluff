"""Defines the linter class."""

import os
import time
import logging
import traceback
from typing import (
    Any,
    Dict,
    Generator,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
    cast,
    overload,
)
from typing_extensions import Literal

from benchit import BenchIt
import pathspec

from sqlfluff.core.errors import (
    SQLBaseError,
    SQLLexError,
    SQLLintError,
    SQLParseError,
    CheckTuple,
)
from sqlfluff.core.parser import Lexer, Parser
from sqlfluff.core.string_helpers import findall
from sqlfluff.core.templaters import TemplatedFile
from sqlfluff.core.rules import get_ruleset
from sqlfluff.core.config import FluffConfig, ConfigLoader

# Classes needed only for type checking
from sqlfluff.core.parser.segments.base import BaseSegment, FixPatch
from sqlfluff.core.parser.segments.meta import MetaSegment
from sqlfluff.core.parser.segments.raw import RawSegment
from sqlfluff.core.rules.base import BaseCrawler

# Instantiate the linter logger
linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")


class RuleTuple(NamedTuple):
    """Rule Tuple object for describing rules."""

    code: str
    description: str


class ProtoFile(NamedTuple):
    """Proto object to be inherited by LintedFile."""

    path: str
    violations: list
    time_dict: dict
    tree: Any
    ignore_mask: list


class ParsedString(NamedTuple):
    """An object to store the result of parsing a string."""

    tree: Optional[BaseSegment]
    violations: List[SQLBaseError]
    time_dict: dict
    templated_file: TemplatedFile
    config: FluffConfig


class EnrichedFixPatch(NamedTuple):
    """An edit patch for a source file."""

    source_slice: slice
    templated_slice: slice
    fixed_raw: str
    # The patch type, functions mostly for debugging and explanation
    # than for function. It allows traceability of *why* this patch was
    # generated.
    patch_type: str
    templated_str: str
    source_str: str

    def dedupe_tuple(self):
        """Generate a tuple of this fix for deduping."""
        return (self.source_slice, self.fixed_raw)


class LintedFile(NamedTuple):
    """A class to store the idea of a linted file."""

    path: str
    violations: list
    time_dict: dict
    tree: Optional[BaseSegment]
    ignore_mask: list
    templated_file: TemplatedFile

    def check_tuples(self) -> List[CheckTuple]:
        """Make a list of check_tuples.

        This assumes that all the violations found are
        linting violations (and therefore implement `check_tuple()`).
        If they don't then this function raises that error.
        """
        vs: List[CheckTuple] = []
        v: SQLLintError
        for v in self.get_violations():
            if hasattr(v, "check_tuple"):
                vs.append(v.check_tuple())
            else:
                raise v
        return vs

    def get_violations(
        self,
        rules: Optional[Union[str, Tuple[str, ...]]] = None,
        types: Optional[Union[Any, Iterable[Any]]] = None,
        filter_ignore: bool = True,
        fixable: bool = None,
    ) -> list:
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

    def num_violations(self, **kwargs) -> int:
        """Count the number of violations.

        Optionally now with filters.
        """
        violations = self.get_violations(**kwargs)
        return len(violations)

    def is_clean(self) -> bool:
        """Return True if there are no ignorable violations."""
        return not any(self.get_violations(filter_ignore=True))

    def fix_string(self) -> Tuple[Any, bool]:
        """Obtain the changes to a path as a string.

        We use the source mapping features of TemplatedFile
        to generate a list of "patches" which cover the non
        templated parts of the file and refer back to the locations
        in the original file.

        NB: This is MUCH FASTER than the original approach
        using difflib in pre 0.4.0.

        There is an important distinction here between Slices and
        Segments. A Slice is a portion of a file which is determined
        by the templater based on which portions of the source file
        are templated or not, and therefore before Lexing and so is
        completely dialect agnostic. A Segment is determined by the
        Lexer from portions of strings after templating.
        """
        bencher = BenchIt()
        bencher("fix_string: start")

        linter_logger.debug("Original Tree: %r", self.templated_file.templated_str)
        linter_logger.debug("Fixed Tree: %r", self.tree.raw)  # type: ignore

        # The sliced file is contiguous in the TEMPLATED space.
        # NB: It has gaps and repeats in the source space.
        # It's also not the FIXED file either.
        linter_logger.debug("### Templated File.")
        for idx, file_slice in enumerate(self.templated_file.sliced_file):
            t_str = self.templated_file.templated_str[file_slice.templated_slice]
            s_str = self.templated_file.source_str[file_slice.source_slice]
            if t_str == s_str:
                linter_logger.debug(
                    "    File slice: %s %r [invariant]", idx, file_slice
                )
            else:
                linter_logger.debug("    File slice: %s %r", idx, file_slice)
                linter_logger.debug("    \t\t\ttemplated: %r\tsource: %r", t_str, s_str)

        original_source = self.templated_file.source_str

        # Make sure no patches overlap and divide up the source file into slices.
        # Any Template tags in the source file are off limits.
        source_only_slices = self.templated_file.source_only_slices()

        linter_logger.debug("Source-only slices: %s", source_only_slices)

        # Iterate patches, filtering and translating as we go:
        linter_logger.debug("### Beginning Patch Iteration.")
        filtered_source_patches = []
        dedupe_buffer = []
        # We use enumerate so that we get an index for each patch. This is entirely
        # so when debugging logs we can find a given patch again!
        patch: Union[EnrichedFixPatch, FixPatch]
        for idx, patch in enumerate(
            self.tree.iter_patches(templated_str=self.templated_file.templated_str)  # type: ignore
        ):
            linter_logger.debug("  %s Yielded patch: %s", idx, patch)

            # This next bit is ALL FOR LOGGING AND DEBUGGING
            if patch.templated_slice.start >= 10:
                pre_hint = self.templated_file.templated_str[
                    patch.templated_slice.start - 10 : patch.templated_slice.start
                ]
            else:
                pre_hint = self.templated_file.templated_str[
                    : patch.templated_slice.start
                ]
            if patch.templated_slice.stop + 10 < len(self.templated_file.templated_str):
                post_hint = self.templated_file.templated_str[
                    patch.templated_slice.stop : patch.templated_slice.stop + 10
                ]
            else:
                post_hint = self.templated_file.templated_str[
                    patch.templated_slice.stop :
                ]
            linter_logger.debug(
                "        Templated Hint: ...%r <> %r...", pre_hint, post_hint
            )

            # Attempt to convert to source space.
            try:
                source_slice = self.templated_file.templated_slice_to_source_slice(
                    patch.templated_slice,
                )
            except ValueError:
                linter_logger.info(
                    "      - Skipping. Source space Value Error. i.e. attempted insertion within templated section."
                )
                # If we try and slice within a templated section, then we may fail
                # in which case, we should skip this patch.
                continue

            # Check for duplicates
            dedupe_tuple = (source_slice, patch.fixed_raw)
            if dedupe_tuple in dedupe_buffer:
                linter_logger.info(
                    "      - Skipping. Source space Duplicate: %s", dedupe_tuple
                )
                continue

            # We now evaluate patches in the source-space for whether they overlap
            # or disrupt any templated sections.
            # The intent here is that unless explicitly stated, a fix should never
            # disrupt a templated section.
            # NOTE: We rely here on the patches being sorted.
            # TODO: Implement a mechanism for doing templated section fixes. For
            # now it's just not allowed.

            # Get the affected raw slices.
            local_raw_slices = self.templated_file.raw_slices_spanning_source_slice(
                source_slice
            )
            local_type_list = [slc.slice_type for slc in local_raw_slices]

            enriched_patch = EnrichedFixPatch(
                source_slice=source_slice,
                templated_slice=patch.templated_slice,
                patch_type=patch.patch_type,
                fixed_raw=patch.fixed_raw,
                templated_str=self.templated_file.templated_str[patch.templated_slice],
                source_str=self.templated_file.source_str[source_slice],
            )

            # Deal with the easy case of only literals
            if set(local_type_list) == {"literal"}:
                linter_logger.info(
                    "      * Keeping patch on literal-only section: %s", enriched_patch
                )
                filtered_source_patches.append(enriched_patch)
                dedupe_buffer.append(enriched_patch.dedupe_tuple())
            # Is it a zero length patch.
            elif (
                enriched_patch.source_slice.start == enriched_patch.source_slice.stop
                and enriched_patch.source_slice.start == local_raw_slices[0].source_idx
            ):
                linter_logger.info(
                    "      * Keeping insertion patch on slice boundary: %s",
                    enriched_patch,
                )
                filtered_source_patches.append(enriched_patch)
                dedupe_buffer.append(enriched_patch.dedupe_tuple())
            # If it's ONLY templated then we should skip it.
            elif "literal" not in local_type_list:
                linter_logger.info(
                    "      - Skipping patch over templated section: %s", enriched_patch
                )
            # If we span more than two slices then we should just skip it. Too Hard.
            elif len(local_raw_slices) > 2:
                linter_logger.info(
                    "      - Skipping patch over more than two raw slices: %s",
                    enriched_patch,
                )
            # If it's an insertion (i.e. the string in the pre-fix template is '') then we
            # won't be able to place it, so skip.
            elif not enriched_patch.templated_str:
                linter_logger.info(
                    "      - Skipping insertion patch in templated section: %s",
                    enriched_patch,
                )
            # If the string from the templated version isn't in the source, then we can't fix it.
            elif enriched_patch.templated_str not in enriched_patch.source_str:
                linter_logger.info(
                    "      - Skipping edit patch on templated content: %s",
                    enriched_patch,
                )
            else:
                # Identify all the places the string appears in the source content.
                positions = list(
                    findall(enriched_patch.templated_str, enriched_patch.source_str)
                )
                if len(positions) != 1:
                    linter_logger.debug(
                        "        - Skipping edit patch on non-unique templated content: %s",
                        enriched_patch,
                    )
                    continue
                # We have a single occurrences of the thing we want to patch. This
                # means we can use its position to place our patch.
                new_source_slice = slice(
                    enriched_patch.source_slice.start + positions[0],
                    enriched_patch.source_slice.start
                    + positions[0]
                    + len(enriched_patch.templated_str),
                )
                enriched_patch = EnrichedFixPatch(
                    source_slice=new_source_slice,
                    templated_slice=enriched_patch.templated_slice,
                    patch_type=enriched_patch.patch_type,
                    fixed_raw=enriched_patch.fixed_raw,
                    templated_str=enriched_patch.templated_str,
                    source_str=enriched_patch.source_str,
                )
                linter_logger.debug(
                    "      * Keeping Tricky Case. Positions: %s, New Slice: %s, Patch: %s",
                    positions,
                    new_source_slice,
                    enriched_patch,
                )
                filtered_source_patches.append(enriched_patch)
                dedupe_buffer.append(enriched_patch.dedupe_tuple())
                continue

        # Sort the patches before building up the file.
        filtered_source_patches = sorted(
            filtered_source_patches, key=lambda x: x.source_slice.start
        )
        # We now slice up the file using the patches and any source only slices.
        # This gives us regions to apply changes to.
        slice_buff = []
        source_idx = 0
        for patch in filtered_source_patches:
            # Are there templated slices at or before the start of this patch?
            while (
                source_only_slices
                and source_only_slices[0].source_idx < patch.source_slice.start
            ):
                next_so_slice = source_only_slices.pop(0).source_slice()
                # Add a pre-slice before the next templated slices if needed.
                if next_so_slice.start > source_idx:
                    slice_buff.append(slice(source_idx, next_so_slice.start))
                # Add the templated slice.
                slice_buff.append(next_so_slice)
                source_idx = next_so_slice.stop

            # Is there a gap between current position and this patch?
            if patch.source_slice.start > source_idx:
                # Add a slice up to this patch.
                slice_buff.append(slice(source_idx, patch.source_slice.start))

            # Is this patch covering an area we've already covered?
            if patch.source_slice.start < source_idx:
                linter_logger.info(
                    "Skipping overlapping patch at Index %s, Patch: %s",
                    source_idx,
                    patch,
                )
                # Ignore the patch for now...
                continue

            # Add this patch.
            slice_buff.append(patch.source_slice)
            source_idx = patch.source_slice.stop
        # Add a tail slice.
        if source_idx < len(self.templated_file.source_str):
            slice_buff.append(slice(source_idx, len(self.templated_file.source_str)))

        linter_logger.debug("Final slice buffer: %s", slice_buff)

        # Iterate through the patches, building up the new string.
        str_buff = ""
        for source_slice in slice_buff:
            # Is it one in the patch buffer:
            for patch in filtered_source_patches:
                if patch.source_slice == source_slice:
                    # Use the patched version
                    linter_logger.debug(
                        "%-30s    %s    %r > %r",
                        "Appending {} Patch:".format(patch.patch_type),
                        patch.source_slice,
                        patch.source_str,
                        patch.fixed_raw,
                    )
                    str_buff += patch.fixed_raw
                    break
            else:
                # Use the raw string
                linter_logger.debug(
                    "Appending Raw:                    %s     %r",
                    source_slice,
                    self.templated_file.source_str[source_slice],
                )
                str_buff += self.templated_file.source_str[source_slice]

        bencher("fix_string: Fixing loop done")
        # The success metric here is whether anything ACTUALLY changed.
        return str_buff, str_buff != original_source

    def persist_tree(self, suffix: str = "") -> bool:
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

    def __init__(self, path: str) -> None:
        self.files: List[LintedFile] = []
        self.path: str = path

    def add(self, file: LintedFile) -> None:
        """Add a file to this path."""
        self.files.append(file)

    @overload
    def check_tuples(self, by_path: Literal[False]) -> List[CheckTuple]:
        """Return a List of CheckTuples when by_path is False."""
        ...

    @overload
    def check_tuples(self, by_path: Literal[True]) -> Dict[str, List[CheckTuple]]:
        """Return a Dict of paths and CheckTuples when by_path is True."""
        ...

    @overload
    def check_tuples(self, by_path: bool = False):
        """Default overload method."""
        ...

    def check_tuples(self, by_path=False):
        """Compress all the tuples into one list.

        NB: This is a little crude, as you can't tell which
        file the violations are from. Good for testing though.
        For more control set the `by_path` argument to true.
        """
        if by_path:
            return {file.path: file.check_tuples() for file in self.files}
        else:
            tuple_buffer: List[CheckTuple] = []
            for file in self.files:
                tuple_buffer += file.check_tuples()
            return tuple_buffer

    def num_violations(self, **kwargs) -> int:
        """Count the number of violations in the path."""
        return sum(file.num_violations(**kwargs) for file in self.files)

    def get_violations(self, **kwargs) -> list:
        """Return a list of violations in the path."""
        buff: list = []
        for file in self.files:
            buff += file.get_violations(**kwargs)
        return buff

    def violation_dict(self, **kwargs) -> Dict[str, list]:
        """Return a dict of violations by file path."""
        return {file.path: file.get_violations(**kwargs) for file in self.files}

    def stats(self) -> Dict[str, int]:
        """Return a dict containing linting stats about this path."""
        return dict(
            files=len(self.files),
            clean=sum(file.is_clean() for file in self.files),
            unclean=sum(not file.is_clean() for file in self.files),
            violations=sum(file.num_violations() for file in self.files),
        )

    def persist_changes(
        self, formatter: Any = None, fixed_file_suffix: str = "", **kwargs
    ) -> Dict[str, Union[bool, str]]:
        """Persist changes to files in the given path.

        This also logs the output as we go using the formatter if present.
        """
        # Run all the fixes for all the files and return a dict
        buffer: Dict[str, Union[bool, str]] = {}
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

    @property
    def tree(self) -> Optional[BaseSegment]:
        """A convenience method for when there is only one file and we want the tree."""
        if len(self.files) > 1:
            raise ValueError(
                ".tree() cannot be called when a LintedPath contains more than one file."
            )
        return self.files[0].tree


class LintingResult:
    """A class to represent the result of a linting operation.

    Notably this might be a collection of paths, all with multiple
    potential files within them.
    """

    def __init__(self) -> None:
        self.paths: List[LintedPath] = []

    @staticmethod
    def sum_dicts(d1: Dict[str, Any], d2: Dict[str, Any]) -> Dict[str, Any]:
        """Take the keys of two dictionaries and add them."""
        keys = set(d1.keys()) | set(d2.keys())
        return {key: d1.get(key, 0) + d2.get(key, 0) for key in keys}

    @staticmethod
    def combine_dicts(*d: dict) -> dict:
        """Take any set of dictionaries and combine them."""
        dict_buffer: dict = {}
        for dct in d:
            dict_buffer.update(dct)
        return dict_buffer

    def add(self, path: LintedPath) -> None:
        """Add a new `LintedPath` to this result."""
        self.paths.append(path)

    @overload
    def check_tuples(self, by_path: Literal[False]) -> List[CheckTuple]:
        """Return a List of CheckTuples when by_path is False."""
        ...

    @overload
    def check_tuples(
        self, by_path: Literal[True]
    ) -> Dict[LintedPath, List[CheckTuple]]:
        """Return a Dict of LintedPath and CheckTuples when by_path is True."""
        ...

    @overload
    def check_tuples(self, by_path: bool = False):
        """Default overload method."""
        ...

    def check_tuples(self, by_path=False):
        """Fetch all check_tuples from all contained `LintedPath` objects.

        Args:
            by_path (:obj:`bool`, optional): When False, all the check_tuples
                are aggregated into one flat list. When True, we return a `dict`
                of paths, each with its own list of check_tuples. Defaults to False.

        """
        if by_path:
            buff: Dict[LintedPath, List[CheckTuple]] = {}
            for path in self.paths:
                buff.update(path.check_tuples(by_path=by_path))
            return buff
        else:
            tuple_buffer: List[CheckTuple] = []
            for path in self.paths:
                tuple_buffer += path.check_tuples()
            return tuple_buffer

    def num_violations(self, **kwargs) -> int:
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

    def stats(self) -> Dict[str, Any]:
        """Return a stats dictionary of this result."""
        all_stats: Dict[str, Any] = dict(files=0, clean=0, unclean=0, violations=0)
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

    def as_records(self) -> List[dict]:
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

    def persist_changes(self, formatter, **kwargs) -> dict:
        """Run all the fixes for all the files and return a dict."""
        return self.combine_dicts(
            *[
                path.persist_changes(formatter=formatter, **kwargs)
                for path in self.paths
            ]
        )

    @property
    def tree(self) -> Optional[BaseSegment]:
        """A convenience method for when there is only one file and we want the tree."""
        if len(self.paths) > 1:
            raise ValueError(
                ".tree() cannot be called when a LintingResult contains more than one path."
            )
        return self.paths[0].tree


class Linter:
    """The interface class to interact with the linter."""

    def __init__(
        self,
        sql_exts: Tuple[str, ...] = (".sql",),
        config: Optional[FluffConfig] = None,
        formatter: Any = None,
        dialect: Optional[str] = None,
        rules: Optional[Union[str, List[str]]] = None,
        user_rules: Optional[Union[str, List[str]]] = None,
    ) -> None:
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

    def get_ruleset(self, config: Optional[FluffConfig] = None) -> List[BaseCrawler]:
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

    def parse_string(
        self,
        in_str: str,
        fname: Optional[str] = None,
        recurse: bool = True,
        config: Optional[FluffConfig] = None,
    ) -> ParsedString:
        """Parse a string.

        Returns:
            `ParsedString` of (`parsed`, `violations`, `time_dict`, `templated_file`).
                `parsed` is a segment structure representing the parsed file. If
                    parsing fails due to an unrecoverable violation then we will
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
            short_fname: Optional[str] = fname.replace("\\", "/").split("/")[-1]
        else:
            # this handles the potential case of a null fname
            short_fname = fname
        bencher("Staring parse_string for {0!r}".format(short_fname))

        # Dispatch the output for the parse header (including the config diff)
        if self.formatter:
            self.formatter.dispatch_parse_header(fname, self.config, config)

        # Just use the local config from here:
        config = config or self.config

        # Scan the raw file for config commands.
        for raw_line in in_str.splitlines():
            if raw_line.startswith("-- sqlfluff"):
                # Found a in-file config command
                config.process_inline_config(raw_line)

        linter_logger.info("TEMPLATING RAW [%s] (%s)", self.templater.name, fname)
        templated_file, templater_violations = self.templater.process(
            in_str=in_str, fname=fname, config=config
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
            lexer = Lexer(config=config)
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

        if tokens:
            # Check that we've got sensible indentation from the lexer.
            # We might need to suppress if it's a complicated file.
            templating_blocks_indent = config.get(
                "template_blocks_indent", "indentation"
            )
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
                    linter_logger.warning(
                        "Indent balance test failed for %r. Template indents will not be linted for this file.",
                        fname,
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
                        # Don't allow if it's not configure to function.
                        elif not token.is_enabled(
                            indent_config=config.get_section("indentation")
                        ):
                            continue
                new_tokens.append(token)
            # Swap the buffers
            tokens = new_tokens  # type: ignore

        t2 = time.monotonic()
        bencher("Lexing {0!r}".format(short_fname))
        linter_logger.info("PARSING (%s)", fname)
        parser = Parser(config=config)
        # Parse the file and log any problems
        if tokens:
            try:
                parsed: Optional[BaseSegment] = parser.parse(tokens, recurse=recurse)
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
        return ParsedString(parsed, violations, time_dict, templated_file, config)

    @staticmethod
    def extract_ignore_from_comment(comment: RawSegment):
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

    @staticmethod
    def _warn_unfixable(code: str):
        linter_logger.warning(
            f"One fix for {code} not applied, it would re-cause the same error."
        )

    def lint_fix(
        self, tree: BaseSegment, config: Optional[FluffConfig] = None, fix: bool = False
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

        for loop in range(loop_limit):
            changed = False
            for crawler in self.get_ruleset(config=config):
                # fixes should be a dict {} with keys edit, delete, create
                # delete is just a list of segments to delete
                # edit and create are list of tuples. The first element is the
                # "anchor", the segment to look for either to edit or to insert BEFORE.
                # The second is the element to insert or create.
                linting_errors, _, fixes, _ = crawler.crawl(
                    tree, dialect=config.get("dialect_obj")
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
                lambda e: getattr(e.segment.pos_marker, "is_literal", True),
                linting_errors,
            )
        )
        return linting_errors

    def fix(
        self, tree: BaseSegment, config: Optional[FluffConfig] = None
    ) -> Tuple[BaseSegment, List[SQLLintError]]:
        """Return the fixed tree and violations from lintfix when we're fixing."""
        fixed_tree, violations = self.lint_fix(tree, config, fix=True)
        return fixed_tree, violations

    def lint(
        self, tree: BaseSegment, config: Optional[FluffConfig] = None
    ) -> List[SQLLintError]:
        """Return just the violations from lintfix when we're only linting."""
        _, violations = self.lint_fix(tree, config, fix=False)
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

            if fix:
                tree, initial_linting_errors = self.fix(tree, config=config)
            else:
                initial_linting_errors = self.lint(tree, config=config)

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
        is_exact_file = not os.path.isdir(path)

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
            path_walk: Union[
                Iterator[Tuple[str, List[str], List[str]]],
                List[Tuple[str, None, List[str]]],
            ] = [(dirpath, None, files)] + path_walk_ignore_file
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
                for ext in self.sql_exts:
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
        linted_path = LintedPath(fname)
        linted_path.add(self.lint_string(string, fname=fname, fix=fix))
        result.add(linted_path)
        return result

    def lint_path(
        self,
        path: str,
        fix: bool = False,
        ignore_non_existent_files: bool = False,
        ignore_files: bool = True,
    ) -> LintedPath:
        """Lint a path."""
        linted_path = LintedPath(path)
        if self.formatter:
            self.formatter.dispatch_path(path)
        for fname in self.paths_from_path(
            path,
            ignore_non_existent_files=ignore_non_existent_files,
            ignore_files=ignore_files,
        ):
            config = self.config.make_child_from_path(fname)
            # Handle unicode issues gracefully
            with open(
                fname, "r", encoding="utf8", errors="backslashreplace"
            ) as target_file:
                try:
                    linted_path.add(
                        self.lint_string(
                            target_file.read(), fname=fname, fix=fix, config=config
                        )
                    )
                except IOError as e:  # IOErrors caught in commands.py, so still raise it
                    raise (e)
                except Exception:
                    linter_logger.warning(
                        f"""Unable to lint {fname} due to an internal error. \
Please report this as an issue with your query's contents and stacktrace below!
To hide this warning, add the failing file to .sqlfluffignore
{traceback.format_exc()}""",
                    )
        return linted_path

    def lint_paths(
        self,
        paths: Tuple[str, ...],
        fix: bool = False,
        ignore_non_existent_files: bool = False,
        ignore_files: bool = True,
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
