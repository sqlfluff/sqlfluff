"""Defines the templaters."""

import logging
from bisect import bisect_left
from collections.abc import Iterable, Iterator
from typing import (
    Any,
    Callable,
    NamedTuple,
    Optional,
    TypeVar,
)

from sqlfluff.core.config import FluffConfig
from sqlfluff.core.errors import SQLFluffSkipFile, SQLTemplaterError
from sqlfluff.core.formatter import FormatterInterface
from sqlfluff.core.helpers.slice import zero_slice

# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")


def iter_indices_of_newlines(raw_str: str) -> Iterator[int]:
    """Find the indices of all newlines in a string."""
    init_idx = -1
    while True:
        nl_pos = raw_str.find("\n", init_idx + 1)
        if nl_pos >= 0:
            yield nl_pos
            init_idx = nl_pos
        else:
            break  # pragma: no cover TODO?


T = TypeVar("T")


def large_file_check(func: Callable[..., T]) -> Callable[..., T]:
    """Raise an exception if the file is over a defined size.

    Designed to be implemented as a decorator on `.process()` methods.

    If no config is provided or the relevant config value is set
    to zero then the check is skipped.
    """

    def _wrapped(
        self: Any,
        *,
        in_str: str,
        fname: str,
        config: Optional[FluffConfig] = None,
        formatter: Optional[FormatterInterface] = None,
    ) -> T:
        if config:
            limit = config.get("large_file_skip_char_limit")
            if limit:
                templater_logger.warning(
                    "The config value large_file_skip_char_limit was found set. "
                    "This feature will be removed in a future release, please "
                    "use the more efficient 'large_file_skip_byte_limit' instead."
                )
            if limit and len(in_str) > limit:
                raise SQLFluffSkipFile(
                    f"Length of file {fname!r} is over {limit} characters. "
                    "Skipping to avoid parser lock. Users can increase this limit "
                    "in their config by setting the 'large_file_skip_char_limit' "
                    "value, or disable by setting it to zero."
                )
        return func(
            self, in_str=in_str, fname=fname, config=config, formatter=formatter
        )

    return _wrapped


class RawFileSlice(NamedTuple):
    """A slice referring to a raw file."""

    raw: str  # Source string
    slice_type: str
    source_idx: int  # Offset from beginning of source string
    # Block index, incremented on start or end block tags, e.g. "if", "for".
    # This is used in `BaseRule.discard_unsafe_fixes()` to reject any fixes
    # which span multiple templated blocks.
    block_idx: int = 0
    # The command of a templated tag, e.g. "if", "for"
    # This is used in template tracing as a kind of cache to identify the kind
    # of template element this is without having to re-extract it each time.
    tag: Optional[str] = None

    def end_source_idx(self) -> int:
        """Return the closing index of this slice."""
        return self.source_idx + len(self.raw)

    def source_slice(self) -> slice:
        """Return a slice object for this slice."""
        return slice(self.source_idx, self.end_source_idx())

    def is_source_only_slice(self) -> bool:
        """Based on its slice_type, does it only appear in the *source*?

        There are some slice types which are automatically source only.
        There are *also* some which are source only because they render
        to an empty string.
        """
        # TODO: should any new logic go here?
        return self.slice_type in ("comment", "block_end", "block_start", "block_mid")


class TemplatedFileSlice(NamedTuple):
    """A slice referring to a templated file."""

    slice_type: str
    source_slice: slice
    templated_slice: slice


class RawSliceBlockInfo(NamedTuple):
    """Template-related info about the raw slices in a TemplateFile."""

    # Given a raw file slace, return its block ID. Useful for identifying
    # regions of a file with respect to template control structures (for, if).
    block_ids: dict[RawFileSlice, int]

    # List of block IDs that have the following characteristics:
    # - Loop body
    # - Containing only literals (no templating)
    literal_only_loops: list[int]


class TemplatedFile:
    """A templated SQL file.

    This is the response of a templaters .process() method
    and contains both references to the original file and also
    the capability to split up that file when lexing.
    """

    def __init__(
        self,
        source_str: str,
        fname: str,
        templated_str: Optional[str] = None,
        sliced_file: Optional[list[TemplatedFileSlice]] = None,
        raw_sliced: Optional[list[RawFileSlice]] = None,
    ):
        """Initialise the TemplatedFile.

        If no templated_str is provided then we assume that the file is NOT
        templated and that the templated view is the same as the source view.

        Args:
            source_str (str): The source string.
            fname (str): The file name.
            templated_str (Optional[str], optional): The templated string.
                Defaults to None.
            sliced_file (Optional[list[TemplatedFileSlice]], optional): The sliced file.
                Defaults to None.
            raw_sliced (Optional[list[RawFileSlice]], optional): The raw sliced file.
                Defaults to None.
        """
        self.source_str = source_str
        # An empty string is still allowed as the templated string.
        self.templated_str = source_str if templated_str is None else templated_str
        # If no fname, we assume this is from a string or stdin.
        self.fname = fname
        # Assume that no sliced_file, means the file is not templated
        self.sliced_file: list[TemplatedFileSlice]
        if sliced_file is None:
            if self.templated_str != self.source_str:  # pragma: no cover
                raise ValueError("Cannot instantiate a templated file unsliced!")
            # If we get here and we don't have sliced files,
            # then it's raw, so create them.
            self.sliced_file = [
                TemplatedFileSlice(
                    "literal", slice(0, len(source_str)), slice(0, len(source_str))
                )
            ]
            assert (
                raw_sliced is None
            ), "Templated file was not sliced, but not has raw slices."
            self.raw_sliced: list[RawFileSlice] = [
                RawFileSlice(source_str, "literal", 0)
            ]
        else:
            self.sliced_file = sliced_file
            assert raw_sliced is not None, "Templated file was sliced, but not raw."
            self.raw_sliced = raw_sliced

        # Precalculate newlines, character positions.
        self._source_newlines = list(iter_indices_of_newlines(self.source_str))
        self._templated_newlines = list(iter_indices_of_newlines(self.templated_str))

        # Consistency check raw string and slices.
        pos = 0
        rfs: RawFileSlice
        for rfs in self.raw_sliced:
            assert rfs.source_idx == pos, (
                "TemplatedFile. Consistency fail on running source length"
                f": {pos} != {rfs.source_idx}"
            )
            pos += len(rfs.raw)
        assert pos == len(self.source_str), (
            "TemplatedFile. Consistency fail on total source length"
            f": {pos} != {len(self.source_str)}"
        )

        # Consistency check templated string and slices.
        previous_slice: Optional[TemplatedFileSlice] = None
        tfs: Optional[TemplatedFileSlice] = None
        for tfs in self.sliced_file:
            if previous_slice:
                if tfs.templated_slice.start != previous_slice.templated_slice.stop:
                    raise SQLFluffSkipFile(  # pragma: no cover
                        "Templated slices found to be non-contiguous. "
                        f"{tfs.templated_slice} (starting"
                        f" {self.templated_str[tfs.templated_slice]!r})"
                        f" does not follow {previous_slice.templated_slice} "
                        "(starting "
                        f"{self.templated_str[previous_slice.templated_slice]!r}"
                        ")"
                    )
            else:
                if tfs.templated_slice.start != 0:
                    raise SQLFluffSkipFile(  # pragma: no cover
                        "First Templated slice not started at index 0 "
                        f"(found slice {tfs.templated_slice})"
                    )
            previous_slice = tfs
        if self.sliced_file and templated_str is not None and tfs:
            if tfs.templated_slice.stop != len(templated_str):
                raise SQLFluffSkipFile(  # pragma: no cover
                    "Length of templated file mismatch with final slice: "
                    f"{len(templated_str)} != {tfs.templated_slice.stop}."
                )

    @classmethod
    def from_string(cls, raw: str) -> "TemplatedFile":
        """Create TemplatedFile from a string."""
        return cls(source_str=raw, fname="<string>")

    def __repr__(self) -> str:  # pragma: no cover TODO?
        """Return a string representation of the 'TemplatedFile' object."""
        return "<TemplatedFile>"

    def __str__(self) -> str:
        """Return the templated file if coerced to string."""
        return self.templated_str

    def get_line_pos_of_char_pos(
        self, char_pos: int, source: bool = True
    ) -> tuple[int, int]:
        """Get the line number and position of a point in the source file.

        Args:
            char_pos: The character position in the relevant file.
            source: Are we checking the source file (as opposed to the
                templated file)

        Returns:
            line_number, line_position

        """
        if source:
            ref_str = self._source_newlines
        else:
            ref_str = self._templated_newlines

        nl_idx = bisect_left(ref_str, char_pos)

        if nl_idx > 0:
            return nl_idx + 1, char_pos - ref_str[nl_idx - 1]
        else:
            # NB: line_pos is char_pos+1 because character position is 0-indexed,
            # but the line position is 1-indexed.
            return 1, char_pos + 1

    def _find_slice_indices_of_templated_pos(
        self,
        templated_pos: int,
        start_idx: Optional[int] = None,
        inclusive: bool = True,
    ) -> tuple[int, int]:
        """Find a subset of the sliced file which touch this point.

        NB: the last_idx is exclusive, as the intent is to use this as a slice.
        """
        start_idx = start_idx or 0
        first_idx: Optional[int] = None
        last_idx = start_idx
        # Work through the sliced file, starting at the start_idx if given
        # as an optimisation hint. The sliced_file is a list of TemplatedFileSlice
        # which reference parts of the templated file and where they exist in the
        # source.
        for idx, elem in enumerate(self.sliced_file[start_idx:]):
            last_idx = idx + start_idx
            if elem[2].stop >= templated_pos:
                if first_idx is None:
                    first_idx = idx + start_idx
                if elem[2].start > templated_pos:
                    break
                elif not inclusive and elem[2].start >= templated_pos:
                    break
        # If we got to the end add another index
        else:
            last_idx += 1
        if first_idx is None:  # pragma: no cover
            raise ValueError("Position Not Found")
        return first_idx, last_idx

    def raw_slices_spanning_source_slice(
        self, source_slice: slice
    ) -> list[RawFileSlice]:
        """Return a list of the raw slices spanning a set of indices."""
        # Special case: The source_slice is at the end of the file.
        last_raw_slice = self.raw_sliced[-1]
        if source_slice.start >= last_raw_slice.source_idx + len(last_raw_slice.raw):
            return []
        # First find the start index
        raw_slice_idx = 0
        # Move the raw pointer forward to the start of this patch
        while (
            raw_slice_idx + 1 < len(self.raw_sliced)
            and self.raw_sliced[raw_slice_idx + 1].source_idx <= source_slice.start
        ):
            raw_slice_idx += 1
        # Find slice index of the end of this patch.
        slice_span = 1
        while (
            raw_slice_idx + slice_span < len(self.raw_sliced)
            and self.raw_sliced[raw_slice_idx + slice_span].source_idx
            < source_slice.stop
        ):
            slice_span += 1
        # Return the raw slices:
        return self.raw_sliced[raw_slice_idx : raw_slice_idx + slice_span]

    def templated_slice_to_source_slice(
        self,
        template_slice: slice,
    ) -> slice:
        """Convert a template slice to a source slice."""
        if not self.sliced_file:
            return template_slice  # pragma: no cover TODO?

        ts_start_sf_start, ts_start_sf_stop = self._find_slice_indices_of_templated_pos(
            template_slice.start
        )

        ts_start_subsliced_file = self.sliced_file[ts_start_sf_start:ts_start_sf_stop]

        # Work out the insertion point
        insertion_point = -1
        for elem in ts_start_subsliced_file:
            # Do slice starts and ends:
            for slice_elem in ("start", "stop"):
                if getattr(elem[2], slice_elem) == template_slice.start:
                    # Store the lowest.
                    point = getattr(elem[1], slice_elem)
                    if insertion_point < 0 or point < insertion_point:
                        insertion_point = point
                    # We don't break here, because we might find ANOTHER
                    # later which is actually earlier.

        # Zero length slice.
        if template_slice.start == template_slice.stop:
            # Is it on a join?
            if insertion_point >= 0:
                return zero_slice(insertion_point)
            # It's within a segment.
            else:
                if (
                    ts_start_subsliced_file
                    and ts_start_subsliced_file[0][0] == "literal"
                ):
                    offset = template_slice.start - ts_start_subsliced_file[0][2].start
                    return zero_slice(
                        ts_start_subsliced_file[0][1].start + offset,
                    )
                else:
                    raise ValueError(  # pragma: no cover
                        "Attempting a single length slice within a templated section! "
                        f"{template_slice} within {ts_start_subsliced_file}."
                    )

        # Otherwise it's a slice with length.

        # Use a non inclusive match to get the end point.
        ts_stop_sf_start, ts_stop_sf_stop = self._find_slice_indices_of_templated_pos(
            template_slice.stop, inclusive=False
        )

        # Update starting position based on insertion point:
        if insertion_point >= 0:
            for elem in self.sliced_file[ts_start_sf_start:]:
                if elem[1].start != insertion_point:
                    ts_start_sf_start += 1
                else:
                    break

        subslices = self.sliced_file[
            # Very inclusive slice
            min(ts_start_sf_start, ts_stop_sf_start) : max(
                ts_start_sf_stop, ts_stop_sf_stop
            )
        ]
        if ts_start_sf_start == ts_start_sf_stop:
            if ts_start_sf_start > len(self.sliced_file):  # pragma: no cover
                # We should never get here
                raise ValueError("Starting position higher than sliced file position")
            if ts_start_sf_start < len(self.sliced_file):  # pragma: no cover
                return self.sliced_file[1].source_slice
            else:
                return self.sliced_file[-1].source_slice  # pragma: no cover
        else:
            start_slices = self.sliced_file[ts_start_sf_start:ts_start_sf_stop]
        if ts_stop_sf_start == ts_stop_sf_stop:  # pragma: no cover TODO?
            stop_slices = [self.sliced_file[ts_stop_sf_start]]
        else:
            stop_slices = self.sliced_file[ts_stop_sf_start:ts_stop_sf_stop]

        # if it's a literal segment then we can get the exact position
        # otherwise we're greedy.

        # Start.
        if insertion_point >= 0:
            source_start = insertion_point
        elif start_slices[0][0] == "literal":
            offset = template_slice.start - start_slices[0][2].start
            source_start = start_slices[0][1].start + offset
        else:
            source_start = start_slices[0][1].start
        # Stop.
        if stop_slices[-1][0] == "literal":
            offset = stop_slices[-1][2].stop - template_slice.stop
            source_stop = stop_slices[-1][1].stop - offset
        else:
            source_stop = stop_slices[-1][1].stop

        # Does this slice go backward?
        if source_start > source_stop:
            # If this happens, it's because one was templated and
            # the other isn't, or because a loop means that the segments
            # are in a different order.

            # Take the widest possible span in this case.
            source_start = min(elem[1].start for elem in subslices)
            source_stop = max(elem[1].stop for elem in subslices)

        source_slice = slice(source_start, source_stop)

        return source_slice

    def is_source_slice_literal(self, source_slice: slice) -> bool:
        """Work out whether a slice of the source file is a literal or not."""
        # No sliced file? Everything is literal
        if not self.raw_sliced:  # pragma: no cover TODO?
            return True
        # Zero length slice. It's a literal, because it's definitely not templated.
        if source_slice.start == source_slice.stop:
            return True
        is_literal = True
        for raw_slice in self.raw_sliced:
            # Reset if we find a literal and we're up to the start
            # otherwise set false.
            if raw_slice.source_idx <= source_slice.start:
                is_literal = raw_slice.slice_type == "literal"
            elif raw_slice.source_idx >= source_slice.stop:
                # We've gone past the end. Break and Return.
                break
            else:
                # We're in the middle. Check type
                if raw_slice.slice_type != "literal":
                    is_literal = False
        return is_literal

    def source_only_slices(self) -> list[RawFileSlice]:
        """Return a list a slices which reference the parts only in the source.

        All of these slices should be expected to have zero-length
        in the templated file.

        The results are NECESSARILY sorted.
        """
        ret_buff = []
        for elem in self.raw_sliced:
            if elem.is_source_only_slice():
                ret_buff.append(elem)
        return ret_buff

    def source_position_dict_from_slice(self, source_slice: slice) -> dict[str, int]:
        """Create a source position dict from a slice."""
        start = self.get_line_pos_of_char_pos(source_slice.start, source=True)
        stop = self.get_line_pos_of_char_pos(source_slice.stop, source=True)
        return {
            "start_line_no": start[0],
            "start_line_pos": start[1],
            "start_file_pos": source_slice.start,
            "end_line_no": stop[0],
            "end_line_pos": stop[1],
            "end_file_pos": source_slice.stop,
        }


class RawTemplater:
    """A templater which does nothing.

    This also acts as the base templating class.
    """

    name = "raw"
    templater_selector = "templater"
    config_subsection: tuple[str, ...] = ()

    def __init__(
        self,
        override_context: Optional[dict[str, Any]] = None,
    ) -> None:
        """Placeholder init function.

        We allow override context here even though the raw templater doesn't apply
        any templating variables. That's to enable classes which inherit from this
        class to reuse that logic.
        """
        self.default_context = dict(test_value="__test__")
        self.override_context = override_context or {}

    def sequence_files(
        self,
        fnames: list[str],
        config: Optional[FluffConfig] = None,
        formatter: Optional[FormatterInterface] = None,
    ) -> Iterable[str]:
        """Given files to be processed, return a valid processing sequence."""
        # Default is to process in the original order.
        return fnames

    @large_file_check
    def process(
        self,
        *,
        in_str: str,
        fname: str,
        config: Optional[FluffConfig] = None,
        formatter: Optional[FormatterInterface] = None,
    ) -> tuple[TemplatedFile, list[SQLTemplaterError]]:
        """Process a string and return a TemplatedFile.

        Note that the arguments are enforced as keywords because Templaters
        can have differences in their `process` method signature.
        A Templater that only supports reading from a file
        would need the following signature:
            process(*, fname, in_str=None, config=None)
        (arguments are swapped)

        Args:
            in_str (:obj:`str`): The input string.
            fname (:obj:`str`, optional): The filename of this string. This is
                mostly for loading config files at runtime.
            config (:obj:`FluffConfig`): A specific config to use for this
                templating operation. Only necessary for some templaters.
            formatter (:obj:`CallbackFormatter`): Optional object for output.

        Returns:
            :obj:`tuple` of :obj:`TemplatedFile` and a list of SQLTemplaterError
            if templating was successful enough that we may move to attempt parsing.

        Raises:
            SQLTemplaterError: If templating fails fatally, then this method
                should raise a :obj:`SQLTemplaterError` instead which will be
                caught and displayed appropriately.

        """
        return TemplatedFile(in_str, fname=fname), []

    @large_file_check
    def process_with_variants(
        self,
        *,
        in_str: str,
        fname: str,
        config: Optional[FluffConfig] = None,
        formatter: Optional[FormatterInterface] = None,
    ) -> Iterator[tuple[TemplatedFile, list[SQLTemplaterError]]]:
        """Extended version of `process` which returns multiple variants.

        Unless explicitly defined, this simply yields the result of .process().
        """
        yield self.process(
            in_str=in_str, fname=fname, config=config, formatter=formatter
        )

    def __eq__(self, other: Any) -> bool:
        """Return true if `other` is of the same class as this one.

        NB: This is useful in comparing configs.
        """
        return isinstance(other, self.__class__)

    def config_pairs(self) -> list[tuple[str, str]]:
        """Returns info about the given templater for output by the cli.

        Returns:
            list[tuple[str, str]]: A list of tuples containing information
                about the given templater. Each tuple contains two strings:
                the string 'templater' and the name of the templater.
        """
        return [("templater", self.name)]

    def get_context(
        self,
        fname: Optional[str],
        config: Optional[FluffConfig],
    ) -> dict[str, Any]:
        """Get the templating context from the config.

        This function retrieves the templating context from the config by
        loading the config and updating the live_context dictionary with the
        loaded_context and other predefined context dictionaries. It then goes
        through the loaded_context dictionary returns the live_context dictionary.

        Args:
            fname (str, optional): The file name.
            config (`FluffConfig`, optional): The config object.

        Returns:
            dict: The templating context.
        """
        # TODO: The config loading should be done outside the templater code. Here
        # is a silly place.
        if config:
            # This is now a nested section
            loaded_context = (
                config.get_section(
                    (self.templater_selector, self.name) + self.config_subsection
                )
                or {}
            )
        else:
            loaded_context = {}
        live_context = {}
        live_context.update(self.default_context)
        live_context.update(loaded_context)
        live_context.update(self.override_context)

        return live_context
