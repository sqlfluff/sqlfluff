"""Defines the LintedFile class.

This holds linting results for a single file, and also
contains all of the routines to apply fixes to that file
post linting.
"""

import logging
import os
import shutil
import stat
import tempfile
from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, NamedTuple, Optional, Tuple, Type, Union

from sqlfluff.core.errors import (
    CheckTuple,
    SQLBaseError,
    SQLLintError,
    SQLParseError,
    SQLTemplaterError,
)
from sqlfluff.core.linter.patch import FixPatch, generate_source_patches

# Classes needed only for type checking
from sqlfluff.core.parser.segments import BaseSegment
from sqlfluff.core.rules.noqa import IgnoreMask
from sqlfluff.core.templaters import RawFileSlice, TemplatedFile

# Instantiate the linter logger
linter_logger: logging.Logger = logging.getLogger("sqlfluff.linter")

TMP_PRS_ERROR_TYPES = (SQLTemplaterError, SQLParseError)


@dataclass
class FileTimings:
    """A dataclass for holding the timings information for a file."""

    step_timings: Dict[str, float]
    # NOTE: Because rules may run more than once for any
    # given file we record each run and then we can post
    # process this as we wish later.
    rule_timings: List[Tuple[str, str, float]]

    def __repr__(self):  # pragma: no cover
        return "<FileTimings>"

    def get_rule_timing_dict(self) -> Dict[str, float]:
        """Generate a summary to total time in each rule.

        This is primarily for csv export.
        """
        total_times: Dict[str, float] = defaultdict(float)

        for code, _, time in self.rule_timings:
            total_times[code] += time

        # Return as plain dict
        return dict(total_times.items())


class LintedFile(NamedTuple):
    """A class to store the idea of a linted file."""

    path: str
    violations: List[SQLBaseError]
    timings: Optional[FileTimings]
    tree: Optional[BaseSegment]
    ignore_mask: Optional[IgnoreMask]
    templated_file: TemplatedFile
    encoding: str

    def check_tuples(
        self, raise_on_non_linting_violations: bool = True
    ) -> List[CheckTuple]:
        """Make a list of check_tuples.

        This assumes that all the violations found are
        linting violations. If they don't then this function
        raises that error.
        """
        vs: List[CheckTuple] = []
        for v in self.get_violations():
            if isinstance(v, SQLLintError):
                vs.append(v.check_tuple())
            elif raise_on_non_linting_violations:
                raise v
        return vs

    @staticmethod
    def deduplicate_in_source_space(
        violations: List[SQLBaseError],
    ) -> List[SQLBaseError]:
        """Removes duplicates in the source space.

        This is useful for templated files with loops, where we'll
        get a violation for each pass around the loop, but the user
        only cares about it once and we're only going to fix it once.

        By filtering them early we get a more a more helpful CLI
        output *and* and more efficient fixing routine (by handling
        fewer fixes).
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
        warn_unused_ignores: bool = False,
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
                violations = self.ignore_mask.ignore_masked_violations(violations)
        # Filter warning violations
        if filter_warning:
            violations = [v for v in violations if not v.warning]
        # Add warnings for unneeded noqa if applicable
        if warn_unused_ignores and not filter_warning and self.ignore_mask:
            violations += self.ignore_mask.generate_warnings_for_unused()
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

    def fix_string(self) -> Tuple[str, bool]:
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

        # Generate patches from the fixed tree. In the process we sort
        # and deduplicate them so that the resultant list is in the
        # the right order for the source file without any duplicates.
        filtered_source_patches = generate_source_patches(
            self.tree, self.templated_file
        )
        linter_logger.debug("Filtered source patches:")
        for idx, patch in enumerate(filtered_source_patches):
            linter_logger.debug("    %s: %s", idx, patch)

        # Any Template tags in the source file are off limits, unless
        # we're explicitly fixing the source file.
        source_only_slices = self.templated_file.source_only_slices()
        linter_logger.debug("Source-only slices: %s", source_only_slices)

        # We now slice up the file using the patches and any source only slices.
        # This gives us regions to apply changes to.
        slice_buff = self._slice_source_file_using_patches(
            filtered_source_patches, source_only_slices, self.templated_file.source_str
        )

        linter_logger.debug("Final slice buffer: %s", slice_buff)

        # Iterate through the patches, building up the new string.
        fixed_source_string = self._build_up_fixed_source_string(
            slice_buff, filtered_source_patches, self.templated_file.source_str
        )

        # The success metric here is whether anything ACTUALLY changed.
        return fixed_source_string, fixed_source_string != original_source

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

    def persist_tree(self, suffix: str = "", formatter: Any = None) -> bool:
        """Persist changes to the given path."""
        if self.num_violations(fixable=True) > 0:
            write_buff, success = self.fix_string()

            if success:
                fname = self.path
                # If there is a suffix specified, then use it.s
                if suffix:
                    root, ext = os.path.splitext(fname)
                    fname = root + suffix + ext
                self._safe_create_replace_file(
                    self.path, fname, write_buff, self.encoding
                )
                result_label = "FIXED"
            else:  # pragma: no cover
                result_label = "FAIL"
        else:
            result_label = "SKIP"
            success = True

        if formatter:
            formatter.dispatch_persist_filename(filename=self.path, result=result_label)

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
            newline="",  # NOTE: No newline conversion. Write as read.
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
