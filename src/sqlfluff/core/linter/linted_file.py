"""Defines the LintedFile class.

This holds linting results for a single file, and also
contains all of the routines to apply fixes to that file
post linting.
"""

import os
import logging
from typing import (
    Any,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Union,
    cast,
    Type,
)

from sqlfluff.core.errors import (
    SQLBaseError,
    SQLLintError,
    CheckTuple,
)
from sqlfluff.core.string_helpers import findall
from sqlfluff.core.templaters import TemplatedFile

# Classes needed only for type checking
from sqlfluff.core.parser.segments.base import BaseSegment, FixPatch

from sqlfluff.core.linter.common import NoQaDirective, EnrichedFixPatch

# Instantiate the linter logger
linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")


class LintedFile(NamedTuple):
    """A class to store the idea of a linted file."""

    path: str
    violations: List[SQLBaseError]
    time_dict: dict
    tree: Optional[BaseSegment]
    ignore_mask: List[NoQaDirective]
    templated_file: TemplatedFile
    encoding: str

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
        types: Optional[Union[Type[SQLBaseError], Iterable[Type[SQLBaseError]]]] = None,
        filter_ignore: bool = True,
        fixable: bool = None,
    ) -> list:
        """Get a list of violations, respecting filters and ignore options.

        Optionally now with filters.
        """
        violations = self.violations
        # Filter types
        if types:
            # If it's a singular type, make it a single item in a tuple
            # otherwise coerce to tuple normally so that we can use it with
            # isinstance.
            if isinstance(types, type) and issubclass(types, SQLBaseError):
                types = (types,)
            else:
                types = tuple(types)  # pragma: no cover TODO?
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
                violations = self._ignore_masked_violations(violations)
        return violations

    @staticmethod
    def _ignore_masked_violations_single_line(
        violations: List[SQLBaseError], ignore_mask: List[NoQaDirective]
    ):
        """Returns whether to ignore error for line-specific directives.

        The "ignore" list is assumed to ONLY contain NoQaDirectives with
        action=None.
        """
        for ignore in ignore_mask:
            violations = [
                v
                for v in violations
                if not (
                    v.line_no == ignore.line_no
                    and (ignore.rules is None or v.rule_code() in ignore.rules)
                )
            ]
        return violations

    @staticmethod
    def _should_ignore_violation_line_range(
        line_no: int, ignore_rule: List[NoQaDirective]
    ):
        """Returns whether to ignore a violation at line_no."""
        # Loop through the NoQaDirectives to find the state of things at
        # line_no. Assumptions about "ignore_rule":
        # - Contains directives for only ONE RULE, i.e. the rule that was
        #   violated at line_no
        # - Sorted in ascending order by line number
        disable = False
        for ignore in ignore_rule:
            if ignore.line_no > line_no:
                break
            disable = ignore.action == "disable"
        return disable

    @classmethod
    def _ignore_masked_violations_line_range(
        cls, violations: List[SQLBaseError], ignore_mask: List[NoQaDirective]
    ):
        """Returns whether to ignore error for line-range directives.

        The "ignore" list is assumed to ONLY contain NoQaDirectives where
        action is "enable" or "disable".
        """
        result = []
        for v in violations:
            # Find the directives that affect the violated rule "v", either
            # because they specifically reference it or because they don't
            # specify a list of rules, thus affecting ALL rules.
            ignore_rule = sorted(
                (
                    ignore
                    for ignore in ignore_mask
                    if not ignore.rules
                    or (v.rule_code() in cast(Tuple[str, ...], ignore.rules))
                ),
                key=lambda ignore: ignore.line_no,
            )
            # Determine whether to ignore the violation, based on the relevant
            # enable/disable directives.
            if not cls._should_ignore_violation_line_range(v.line_no, ignore_rule):
                result.append(v)
        return result

    def _ignore_masked_violations(
        self, violations: List[SQLBaseError]
    ) -> List[SQLBaseError]:
        """Remove any violations specified by ignore_mask.

        This involves two steps:
        1. Filter out violations affected by single-line "noqa" directives.
        2. Filter out violations affected by disable/enable "noqa" directives.
        """
        ignore_specific = [ignore for ignore in self.ignore_mask if not ignore.action]
        ignore_range = [ignore for ignore in self.ignore_mask if ignore.action]
        violations = self._ignore_masked_violations_single_line(
            violations, ignore_specific
        )
        violations = self._ignore_masked_violations_line_range(violations, ignore_range)
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

    @staticmethod
    def _log_hints(
        patch: Union[EnrichedFixPatch, FixPatch], templated_file: TemplatedFile
    ):
        """Log hints for debugging during patch generation."""
        # This next bit is ALL FOR LOGGING AND DEBUGGING
        if patch.templated_slice.start >= 10:
            pre_hint = templated_file.templated_str[
                patch.templated_slice.start - 10 : patch.templated_slice.start
            ]
        else:
            pre_hint = templated_file.templated_str[: patch.templated_slice.start]
        if patch.templated_slice.stop + 10 < len(templated_file.templated_str):
            post_hint = templated_file.templated_str[
                patch.templated_slice.stop : patch.templated_slice.stop + 10
            ]
        else:
            post_hint = templated_file.templated_str[patch.templated_slice.stop :]
        linter_logger.debug(
            "        Templated Hint: ...%r <> %r...", pre_hint, post_hint
        )

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
        linter_logger.debug("Original Tree: %r", self.templated_file.templated_str)
        assert self.tree
        linter_logger.debug("Fixed Tree: %r", self.tree.raw)

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
            self.tree.iter_patches(templated_str=self.templated_file.templated_str)
        ):
            linter_logger.debug("  %s Yielded patch: %s", idx, patch)
            self._log_hints(patch, self.templated_file)

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
                patch_category=patch.patch_category,
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
            elif not enriched_patch.templated_str:  # pragma: no cover TODO?
                linter_logger.info(
                    "      - Skipping insertion patch in templated section: %s",
                    enriched_patch,
                )
            # If the string from the templated version isn't in the source, then we can't fix it.
            elif (
                enriched_patch.templated_str not in enriched_patch.source_str
            ):  # pragma: no cover TODO?
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
                    patch_category=enriched_patch.patch_category,
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
                        f"Appending {patch.patch_category} Patch:",
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
            with open(fname, "w", encoding=self.encoding) as f:
                f.write(write_buff)
        return success
