"""Defines the LintedFile class.

This holds linting results for a single file, and also
contains all of the routines to apply fixes to that file
post linting.
"""

import os
import logging
import shutil
import stat
import tempfile
from collections import defaultdict
from dataclasses import dataclass, field
from typing import (
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Set,
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
from sqlfluff.core.templaters.base import (
    TemplatedFile,
    RawFileSlice,
    TemplatedFileSlice,
)

# Classes needed only for type checking
from sqlfluff.core.parser.segments import BaseSegment, FixPatch

from sqlfluff.core.linter.common import NoQaDirective

# Instantiate the linter logger
linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")


class LintedVariant(NamedTuple):
    """A class to store the idea of a linted variant of a file."""

    path: str
    violations: List[SQLBaseError]
    time_dict: Dict[str, float]
    # Parse tree after any fixes have been applied
    tree: Optional[BaseSegment]
    ignore_mask: List[NoQaDirective]
    templated_file: TemplatedFile
    encoding: str
    # Original parse tree (before fixes)
    original_tree: Optional[BaseSegment]

    @staticmethod
    def deduplicate_in_source_space(
        violations: List[SQLBaseError],
    ) -> List[SQLBaseError]:
        """Removes duplicates in the source space.

        This is useful for templated files with loops, where we'll
        get a violation for each pass around the loop, but the user
        only cares about it once and we're only going to fix it once.

        By filtering them early we get a more helpful CLI output *and* more
        efficient fixing routine (by handling fewer fixes).
        """
        new_violations = []
        dedupe_buffer = set()
        for v in violations:
            signature = v.source_signature()
            if signature not in dedupe_buffer:
                new_violations.append(v)
                dedupe_buffer.add(signature)
            else:
                linter_logger.debug("Removing duplicate source violation: %r", v)
        return new_violations

    def get_violations(
        self,
        rules: Optional[Union[str, Tuple[str, ...]]] = None,
        types: Optional[Union[Type[SQLBaseError], Iterable[Type[SQLBaseError]]]] = None,
        filter_ignore: bool = True,
        filter_warning: bool = True,
        fixable: Optional[bool] = None,
    ) -> List[SQLBaseError]:
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
            # Assume that fixable is true or false if not None.
            # Fatal errors should always come through, regardless.
            violations = [v for v in violations if v.fixable is fixable or v.fatal]
        # Filter ignorable violations
        if filter_ignore:
            violations = [v for v in violations if not v.ignore]
            # Ignore any rules in the ignore mask
            if self.ignore_mask:
                violations = self.ignore_masked_violations(violations, self.ignore_mask)
        # Filter warning violations
        if filter_warning:
            violations = [v for v in violations if not v.warning]
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

    @classmethod
    def ignore_masked_violations(
        cls, violations: List[SQLBaseError], ignore_mask: List[NoQaDirective]
    ) -> List[SQLBaseError]:
        """Remove any violations specified by ignore_mask.

        This involves two steps:
        1. Filter out violations affected by single-line "noqa" directives.
        2. Filter out violations affected by disable/enable "noqa" directives.
        """
        ignore_specific = [ignore for ignore in ignore_mask if not ignore.action]
        ignore_range = [ignore for ignore in ignore_mask if ignore.action]
        violations = cls._ignore_masked_violations_single_line(
            violations, ignore_specific
        )
        violations = cls._ignore_masked_violations_line_range(violations, ignore_range)
        return violations

    @staticmethod
    def _log_hints(patch: FixPatch, templated_file: TemplatedFile):
        """Log hints for debugging during patch generation."""
        # This next bit is ALL FOR LOGGING AND DEBUGGING
        max_log_length = 10
        if patch.templated_slice.start >= max_log_length:
            pre_hint = templated_file.templated_str[
                patch.templated_slice.start
                - max_log_length : patch.templated_slice.start
            ]
        else:
            pre_hint = templated_file.templated_str[: patch.templated_slice.start]
        if patch.templated_slice.stop + max_log_length < len(
            templated_file.templated_str
        ):
            post_hint = templated_file.templated_str[
                patch.templated_slice.stop : patch.templated_slice.stop + max_log_length
            ]
        else:
            post_hint = templated_file.templated_str[patch.templated_slice.stop :]
        linter_logger.debug(
            "        Templated Hint: ...%r <> %r...", pre_hint, post_hint
        )

    def generate_and_log_source_patches(self, tree) -> List[FixPatch]:
        """Generate source patches and log them."""
        linter_logger.debug("Original Tree: %r", self.templated_file.templated_str)
        assert tree
        linter_logger.debug("Fixed Tree: %r", tree.raw)

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

        # Generate patches from the fixed tree. In the process we sort
        # and deduplicate them so that the resultant list is in the
        # the right order for the source file without any duplicates.
        filtered_source_patches = self._generate_source_patches(
            tree, self.templated_file
        )
        linter_logger.debug("Filtered source patches:")
        for idx, patch in enumerate(filtered_source_patches):
            linter_logger.debug("    %s: %s", idx, patch)
        return filtered_source_patches

    @classmethod
    def _generate_source_patches(
        cls, tree: BaseSegment, templated_file: TemplatedFile
    ) -> List[FixPatch]:
        """Use the fixed tree to generate source patches.

        Importantly here we deduplicate and sort the patches
        from their position in the templated file into their
        intended order in the source file.
        """
        # Iterate patches, filtering and translating as we go:
        linter_logger.debug("### Beginning Patch Iteration.")
        filtered_source_patches = []
        dedupe_buffer = []
        # We use enumerate so that we get an index for each patch. This is entirely
        # so when debugging logs we can find a given patch again!
        for idx, patch in enumerate(tree.iter_patches(templated_file=templated_file)):
            linter_logger.debug("  %s Yielded patch: %s", idx, patch)
            cls._log_hints(patch, templated_file)

            # Check for duplicates
            if patch.dedupe_tuple() in dedupe_buffer:
                linter_logger.info(
                    "      - Skipping. Source space Duplicate: %s",
                    patch.dedupe_tuple(),
                )
                continue

            # We now evaluate patches in the source-space for whether they overlap
            # or disrupt any templated sections.
            # The intent here is that unless explicitly stated, a fix should never
            # disrupt a templated section.
            # NOTE: We rely here on the patches being generated in order.
            # TODO: Implement a mechanism for doing templated section fixes. Given
            # these patches are currently generated from fixed segments, there will
            # likely need to be an entirely different mechanism

            # Get the affected raw slices.
            local_raw_slices = templated_file.raw_slices_spanning_source_slice(
                patch.source_slice
            )
            local_type_list = [slc.slice_type for slc in local_raw_slices]

            # Deal with the easy cases of 1) New code at end 2) only literals
            if not local_type_list or set(local_type_list) == {"literal"}:
                linter_logger.info(
                    "      * Keeping patch on new or literal-only section.",
                )
                filtered_source_patches.append(patch)
                dedupe_buffer.append(patch.dedupe_tuple())
            # Handle the easy case of an explicit source fix
            elif patch.patch_category == "source":
                linter_logger.info(
                    "      * Keeping explicit source fix patch.",
                )
                filtered_source_patches.append(patch)
                dedupe_buffer.append(patch.dedupe_tuple())
            # Is it a zero length patch.
            elif (
                patch.source_slice.start == patch.source_slice.stop
                and patch.source_slice.start == local_raw_slices[0].source_idx
            ):
                linter_logger.info(
                    "      * Keeping insertion patch on slice boundary.",
                )
                filtered_source_patches.append(patch)
                dedupe_buffer.append(patch.dedupe_tuple())
            else:  # pragma: no cover
                # We've got a situation where the ends of our patch need to be
                # more carefully mapped. This used to happen with greedy template
                # element matching, but should now never happen. In the event that
                # it does, we'll warn but carry on.
                linter_logger.warning(
                    "Skipping edit patch on uncertain templated section [%s], "
                    "Please report this warning on GitHub along with the query "
                    "that produced it.",
                    (patch.patch_category, patch.source_slice),
                )
                continue

        # Sort the patches before building up the file.
        return sorted(filtered_source_patches, key=lambda x: x.source_slice.start)


@dataclass
class LintedFile:
    """Stores one or more linted variants of the same file."""

    variants: List[LintedVariant] = field(default_factory=list)

    def add_variant(self, variant: LintedVariant):
        """Add a variant to the file."""
        if self.variants:
            if self.variants[0].path != variant.path:
                raise ValueError(  # pragma: no cover
                    "Cannot add variant to file with different path: "
                    f"{self.variants[0].path} != {variant.path}"
                )
        self.variants.append(variant)

    def get_violations(
        self,
        rules: Optional[Union[str, Tuple[str, ...]]] = None,
        types: Optional[Union[Type[SQLBaseError], Iterable[Type[SQLBaseError]]]] = None,
        filter_ignore: bool = True,
        filter_warning: bool = True,
        fixable: Optional[bool] = None,
    ) -> List:
        """Get a list of violations for this file.

        The list of violations returned is suitable for lint output, but not
        for fixing because the fixes are specific to the variant's tree. We'll
        address this when generating and applying file patches.
        """
        # Trivial case: Just one variant
        if len(self.variants) == 1:
            return self.variants[0].get_violations(
                rules=rules,
                types=types,
                filter_ignore=filter_ignore,
                filter_warning=filter_warning,
                fixable=fixable,
            )

        # In order to be included, a violation must meet one of the following
        # criteria.
        # - Case 1: It appears in _all_ variants
        # - Case 2: It appears in one variant and is "source only" in the other
        #   variant. (For now, we assume there are at most 2 variants.)

        # Case 1 bookkeeping
        violations_dict = defaultdict(set)
        for idx, variant in enumerate(self.variants):
            for violation in variant.get_violations(
                rules=rules,
                types=types,
                filter_ignore=filter_ignore,
                filter_warning=filter_warning,
                fixable=fixable,
            ):
                violations_dict[violation].add(idx)
        result = [
            violation
            for violation, idxs in violations_dict.items()
            if len(idxs) == len(self.variants)
        ]

        # Case 2 bookkeeping
        if len(self.variants) == 2:
            for idx, variant in enumerate(self.variants):
                violations = variant.get_violations(
                    rules=rules,
                    types=types,
                    filter_ignore=filter_ignore,
                    filter_warning=filter_warning,
                    fixable=fixable,
                )
                for violation in violations:
                    if violation in result or not isinstance(violation, SQLLintError):
                        continue
                    # Get the source slices touched by the violation.
                    violation_source_slices: Set[Tuple[int, int]] = set()
                    if violation.fixes:
                        for fix in violation.fixes:
                            temp_slice = fix.anchor.pos_marker.source_slice
                            violation_source_slices.add(
                                (temp_slice.start, temp_slice.stop)
                            )
                    else:
                        temp_slice = violation.segment.pos_marker.source_slice
                        violation_source_slices.add((temp_slice.start, temp_slice.stop))
                    # Check if any of these slices appear in *templated* slices in the
                    # other variant. If so, don't include the violation.
                    other_variant_idx = 1 - idx
                    if self._include_violation(
                        violation_source_slices,
                        self.variants[other_variant_idx].templated_file.sliced_file,
                    ):
                        result.append(violation)
        return result

    @staticmethod
    def _include_violation(
        raw_slices: Set[Tuple[int, int]],
        templated_slices: List[TemplatedFileSlice],
    ) -> bool:
        """Return True if any raw_slices appear in templated_slices."""
        for raw_slice in raw_slices:
            for ts in templated_slices:
                if (
                    raw_slice[1] > ts.source_slice.start
                    and ts.source_slice.stop > raw_slice[0]
                ):
                    return False
        return True

    @property
    def violations(self) -> List:
        """Return a list of all violations for this file."""
        return self.get_violations()

    def is_clean(self) -> bool:
        """Return True if there are no ignorable violations."""
        return not any(self.get_violations(filter_ignore=True))

    def num_violations(self, **kwargs) -> int:
        """Count the number of violations.

        Optionally now with filters.
        """
        violations = self.get_violations(**kwargs)
        return len(violations)

    @property
    def path(self) -> str:
        """Return the path of the file."""
        if self.variants:
            return self.variants[0].path
        else:
            raise ValueError(
                "'path' is not defined for an empty LintedFile"
            )  # pragma: no cover

    @property
    def templated_file(self) -> Optional[TemplatedFile]:
        """Return the templated file."""
        if self.variants:
            return self.variants[0].templated_file
        else:
            return None  # pragma: no cover

    @property
    def tree(self) -> Optional[BaseSegment]:
        """Return the tree for the first variant."""
        return self.variants[0].tree

    def check_tuples(self, raise_on_non_linting_violations=True) -> List[CheckTuple]:
        """Make a list of check_tuples.

        This assumes that all the violations found are
        linting violations. If they don't then this function
        raises that error.
        """
        vs: List[CheckTuple] = []
        v: SQLLintError
        for v in self.get_violations():
            if isinstance(v, SQLLintError):
                vs.append(v.check_tuple())
            elif raise_on_non_linting_violations:
                raise v
        return vs

    @property
    def time_dict(self) -> Dict[str, float]:
        """Return a dictionary of timings."""
        timings: Dict[str, float] = {}
        for variant in self.variants:
            for k, v in variant.time_dict.items():
                timings[k] = timings.get(k, 0) + v
        return timings

    def fix_string(
        self, violations: Optional[List[SQLBaseError]] = None
    ) -> Tuple[str, bool]:
        """Return the fixed string and a boolean indicating success."""
        fixed_trees: List[BaseSegment]
        if violations is None:
            fixed_trees = [variant.tree for variant in self.variants if variant.tree]
        else:
            # Partition the violations to fix based on the variant they belong to.
            violations_by_variant: Dict[int, List[SQLBaseError]] = defaultdict(list)
            variant: LintedVariant
            for violation in violations:
                for idx, variant in enumerate(self.variants):
                    if violation in variant.violations:
                        violations_by_variant[idx].append(violation)
                        break
                else:
                    raise ValueError(f"Violation {violation} not found in any variant.")
            # Now start over from the original string for each variant and apply the
            # fixes.
            # Reference: Linter.lint_rendered()
            fixed_trees = []
            for idx, variant in enumerate(self.variants):
                fixes_by_rule_code: Dict[str, List] = defaultdict(list)
                for violation in violations_by_variant[idx]:
                    if isinstance(violation, SQLLintError):
                        fixes_by_rule_code[violation.rule_code()] += violation.fixes
                tree = variant.original_tree
                assert tree
                for rule_code, fixes in fixes_by_rule_code.items():
                    anchor_info = BaseSegment.compute_anchor_edit_info(fixes)
                    tree, _, _ = tree.apply_fixes(None, rule_code, anchor_info)
                fixed_trees.append(tree)

        filtered_source_patches: List[FixPatch] = []
        main_variant = self.variants[0]
        for idx, variant in enumerate(self.variants):
            linter_logger.debug(f"Variant #{idx}")
            # Do we need to deduplicate the patches using FixPatch.dedupe_tuple()?
            filtered_source_patches += variant.generate_and_log_source_patches(
                fixed_trees[idx]
            )

        # Any Template tags in the source file are off limits, unless
        # we're explicitly fixing the source file.
        source_only_slices = main_variant.templated_file.source_only_slices()
        linter_logger.debug("Source-only slices: %s", source_only_slices)

        # We now slice up the file using the patches and any source only slices.
        # This gives us regions to apply changes to.
        slice_buff = self._slice_source_file_using_patches(
            filtered_source_patches,
            source_only_slices,
            main_variant.templated_file.source_str,
        )

        linter_logger.debug("Final slice buffer: %s", slice_buff)

        # Iterate through the patches, building up the new string.
        fixed_source_string = self._build_up_fixed_source_string(
            slice_buff, filtered_source_patches, main_variant.templated_file.source_str
        )

        # The success metric here is whether anything ACTUALLY changed.
        return (
            fixed_source_string,
            fixed_source_string != main_variant.templated_file.source_str,
        )

    @staticmethod
    def _slice_source_file_using_patches(
        source_patches: List[FixPatch],
        source_only_slices: List[RawFileSlice],
        raw_source_string: str,
    ) -> List[slice]:
        """Use patches to safely slice up the file before fixing.

        This uses source only slices to avoid overwriting sections
        of templated code in the source file (when we don't want to).

        We assume that the source patches have already been
        sorted and deduplicated. Sorting is important. If the slices
        aren't sorted then this function will miss chunks.
        If there are overlaps or duplicates then this function
        may produce strange results.
        """
        # We now slice up the file using the patches and any source only slices.
        # This gives us regions to apply changes to.
        slice_buff = []
        source_idx = 0
        for patch in source_patches:
            # Are there templated slices at or before the start of this patch?
            # TODO: We'll need to explicit handling for template fixes here, because
            # they ARE source only slices. If we can get handling to work properly
            # here then this is the last hurdle and it will flow through
            # smoothly from here.
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

            # Does this patch cover the next source-only slice directly?
            if (
                source_only_slices
                and patch.source_slice == source_only_slices[0].source_slice()
            ):
                linter_logger.info(
                    "Removing next source only slice from the stack because it "
                    "covers the same area of source file as the current patch: %s %s",
                    source_only_slices[0],
                    patch,
                )
                # If it does, remove it so that we don't duplicate it.
                source_only_slices.pop(0)

            # Is there a gap between current position and this patch?
            if patch.source_slice.start > source_idx:
                # Add a slice up to this patch.
                slice_buff.append(slice(source_idx, patch.source_slice.start))

            # Is this patch covering an area we've already covered?
            if patch.source_slice.start < source_idx:  # pragma: no cover
                # NOTE: This shouldn't happen. With more detailed templating
                # this shouldn't happen - but in the off-chance that this does
                # happen - then this code path remains.
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
        if source_idx < len(raw_source_string):
            slice_buff.append(slice(source_idx, len(raw_source_string)))

        return slice_buff

    @staticmethod
    def _build_up_fixed_source_string(
        source_file_slices: List[slice],
        source_patches: List[FixPatch],
        raw_source_string: str,
    ) -> str:
        """Use patches and raw file to fix the source file.

        This assumes that patches and slices have already
        been coordinated. If they haven't then this will
        fail because we rely on patches having a corresponding
        slice of exactly the right file in the list of file
        slices.
        """
        # Iterate through the patches, building up the new string.
        str_buff = ""
        for source_slice in source_file_slices:
            # Is it one in the patch buffer:
            for patch in source_patches:
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
                    raw_source_string[source_slice],
                )
                str_buff += raw_source_string[source_slice]
        return str_buff

    def persist_tree(self, violations: List[SQLBaseError], suffix: str = "") -> bool:
        """Persist changes to the given path."""
        write_buff, success = self.fix_string(violations)

        if success:
            fname = self.path
            # If there is a suffix specified, then use it.
            if suffix:
                root, ext = os.path.splitext(fname)
                fname = root + suffix + ext
            self._safe_create_replace_file(
                self.path, fname, write_buff, self.variants[0].encoding
            )
        return success

    @staticmethod
    def _safe_create_replace_file(
        input_path: str, output_path: str, write_buff: str, encoding: str
    ):
        # Write to a temporary file first, so in case of encoding or other
        # issues, we don't delete or corrupt the user's existing file.

        # Get file mode (i.e. permissions) on existing file. We'll preserve the
        # same permissions on the output file.
        mode = None
        try:
            status = os.stat(input_path)
        except FileNotFoundError:
            pass
        else:
            if stat.S_ISREG(status.st_mode):
                mode = stat.S_IMODE(status.st_mode)
        dirname, basename = os.path.split(output_path)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding=encoding,
            prefix=basename,
            dir=dirname,
            suffix=os.path.splitext(output_path)[1],
            delete=False,
        ) as tmp:
            tmp.file.write(write_buff)
            tmp.flush()
            os.fsync(tmp.fileno())
        # Once the temp file is safely written, replace the existing file.
        if mode is not None:
            os.chmod(tmp.name, mode)
        shutil.move(tmp.name, output_path)
