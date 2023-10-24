"""Defines the templaters."""

import ast
from string import Formatter
from typing import (
    Any,
    Callable,
    Dict,
    Iterable,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Tuple,
)

from sqlfluff.core.errors import SQLTemplaterError
from sqlfluff.core.helpers.slice import offset_slice, zero_slice
from sqlfluff.core.helpers.string import findall
from sqlfluff.core.templaters.base import (
    RawFileSlice,
    RawTemplater,
    TemplatedFile,
    TemplatedFileSlice,
    large_file_check,
    templater_logger,
)


class IntermediateFileSlice(NamedTuple):
    """An intermediate representation of a partially sliced File."""

    intermediate_type: str
    source_slice: slice
    templated_slice: slice
    slice_buffer: List[RawFileSlice]

    def _trim_end(
        self, templated_str: str, target_end: str = "head"
    ) -> Tuple["IntermediateFileSlice", List[TemplatedFileSlice]]:
        """Trim the ends of a intermediate segment."""
        target_idx = 0 if target_end == "head" else -1
        terminator_types = ("block_start") if target_end == "head" else ("block_end")
        main_source_slice = self.source_slice
        main_templated_slice = self.templated_slice
        slice_buffer = self.slice_buffer

        end_buffer = []

        # Yield any leading literals, comments or blocks.
        while len(slice_buffer) > 0 and slice_buffer[target_idx].slice_type in (
            "literal",
            "block_start",
            "block_end",
            "comment",
        ):
            focus = slice_buffer[target_idx]
            templater_logger.debug("            %s Focus: %s", target_end, focus)
            # Is it a zero length item?
            if focus.slice_type in ("block_start", "block_end", "comment"):
                # Only add the length in the source space.
                templated_len = 0
            else:
                # Assume it's a literal, check the literal actually matches.
                templated_len = len(focus.raw)
                if target_end == "head":
                    check_slice = offset_slice(
                        main_templated_slice.start,
                        templated_len,
                    )
                else:
                    check_slice = slice(
                        main_templated_slice.stop - templated_len,
                        main_templated_slice.stop,
                    )

                if templated_str[check_slice] != focus.raw:
                    # It doesn't match, we can't use it. break
                    templater_logger.debug("                Nope")
                    break

            # If it does match, set up the new slices
            if target_end == "head":
                division = (
                    main_source_slice.start + len(focus.raw),
                    main_templated_slice.start + templated_len,
                )
                new_slice = TemplatedFileSlice(
                    focus.slice_type,
                    slice(main_source_slice.start, division[0]),
                    slice(main_templated_slice.start, division[1]),
                )
                end_buffer.append(new_slice)
                main_source_slice = slice(division[0], main_source_slice.stop)
                main_templated_slice = slice(division[1], main_templated_slice.stop)
            else:
                division = (
                    main_source_slice.stop - len(focus.raw),
                    main_templated_slice.stop - templated_len,
                )
                new_slice = TemplatedFileSlice(
                    focus.slice_type,
                    slice(division[0], main_source_slice.stop),
                    slice(division[1], main_templated_slice.stop),
                )
                end_buffer.insert(0, new_slice)
                main_source_slice = slice(main_source_slice.start, division[0])
                main_templated_slice = slice(main_templated_slice.start, division[1])

            slice_buffer.pop(target_idx)
            if focus.slice_type in terminator_types:
                break
        # Return a new Intermediate slice and the buffer.
        # NB: Don't check size of slice buffer here. We can do that later.
        new_intermediate = self.__class__(
            "compound", main_source_slice, main_templated_slice, slice_buffer
        )
        return new_intermediate, end_buffer

    def trim_ends(
        self, templated_str: str
    ) -> Tuple[
        List[TemplatedFileSlice], "IntermediateFileSlice", List[TemplatedFileSlice]
    ]:
        """Trim both ends of an intermediate slice."""
        # Trim start:
        new_slice, head_buffer = self._trim_end(
            templated_str=templated_str, target_end="head"
        )
        # Trim end:
        new_slice, tail_buffer = new_slice._trim_end(
            templated_str=templated_str, target_end="tail"
        )
        # Return
        return head_buffer, new_slice, tail_buffer

    def try_simple(self) -> TemplatedFileSlice:
        """Try to turn this intermediate slice into a simple slice."""
        # Yield anything simple
        if len(self.slice_buffer) == 1:
            return TemplatedFileSlice(
                self.slice_buffer[0].slice_type,
                self.source_slice,
                self.templated_slice,
            )
        else:
            raise ValueError("IntermediateFileSlice is not simple!")

    def coalesce(self) -> TemplatedFileSlice:
        """Coalesce this whole slice into a single one. Brutally."""
        return TemplatedFileSlice(
            PythonTemplater._coalesce_types(self.slice_buffer),
            self.source_slice,
            self.templated_slice,
        )


class PythonTemplater(RawTemplater):
    """A templater using python format strings.

    See: https://docs.python.org/3/library/string.html#format-string-syntax

    For the python templater we don't allow functions or macros because there isn't
    a good way of doing it securely. Use the jinja templater for this.

    The python templater also defines a lot of the logic for how
    to allow fixing and translation in a templated file.
    """

    name = "python"

    def __init__(self, override_context=None, **kwargs) -> None:
        self.default_context = dict(test_value="__test__")
        self.override_context = override_context or {}

    @staticmethod
    def infer_type(s) -> Any:
        """Infer a python type from a string and convert.

        Given a string value, convert it to a more specific built-in Python type
        (e.g. int, float, list, dictionary) if possible.

        """
        try:
            return ast.literal_eval(s)
        except (SyntaxError, ValueError):
            return s

    def get_context(self, fname=None, config=None, **kw) -> Dict:
        """Get the templating context from the config.

        This function retrieves the templating context from the config by
        loading the config and updating the live_context dictionary with the
        loaded_context and other predefined context dictionaries. It then goes
        through the loaded_context dictionary and infers the types of the values
        before returning the live_context dictionary.

        Args:
            fname (str, optional): The file name.
            config (dict, optional): The config dictionary.
            **kw: Additional keyword arguments.

        Returns:
            dict: The templating context.
        """
        # TODO: The config loading should be done outside the templater code. Here
        # is a silly place.
        if config:
            # This is now a nested section
            loaded_context = (
                config.get_section((self.templater_selector, self.name, "context"))
                or {}
            )
        else:
            loaded_context = {}
        live_context = {}
        live_context.update(self.default_context)
        live_context.update(loaded_context)
        live_context.update(self.override_context)

        # Infer types
        for k in loaded_context:
            live_context[k] = self.infer_type(live_context[k])
        return live_context

    @large_file_check
    def process(
        self, *, in_str: str, fname: str, config=None, formatter=None
    ) -> Tuple[Optional[TemplatedFile], List]:
        """Process a string and return a TemplatedFile.

        Note that the arguments are enforced as keywords
        because Templaters can have differences in their
        `process` method signature.
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

        """
        live_context = self.get_context(fname=fname, config=config)

        def render_func(raw_str: str) -> str:
            """Render the string using the captured live_context."""
            try:
                rendered_str = raw_str.format(**live_context)
            except KeyError as err:
                raise SQLTemplaterError(
                    "Failure in Python templating: {}. Have you configured your "
                    "variables? https://docs.sqlfluff.com/en/stable/"
                    "configuration.html#templating-configuration".format(err)
                )
            return rendered_str

        raw_sliced, sliced_file, new_str = self.slice_file(
            in_str,
            render_func=render_func,
            config=config,
        )
        return (
            TemplatedFile(
                source_str=in_str,
                templated_str=new_str,
                fname=fname,
                sliced_file=sliced_file,
                raw_sliced=raw_sliced,
            ),
            [],
        )

    def slice_file(
        self, raw_str: str, render_func: Callable[[str], str], config=None, **kwargs
    ) -> Tuple[List[RawFileSlice], List[TemplatedFileSlice], str]:
        """Slice the file to determine regions where we can fix."""
        templater_logger.info("Slicing File Template")
        templater_logger.debug("    Raw String: %r", raw_str)
        # Render the templated string.
        # NOTE: This seems excessive in this simple example, but for other templating
        # engines we need more control over the rendering so may need to call this
        # method more than once.
        templated_str = render_func(raw_str)
        templater_logger.debug("    Templated String: %r", templated_str)
        # Slice the raw file
        raw_sliced = list(self._slice_template(raw_str))
        templater_logger.debug("    Raw Sliced:")
        for idx, raw_slice in enumerate(raw_sliced):
            templater_logger.debug("        %s: %r", idx, raw_slice)
        # Find the literals
        literals = [
            raw_slice.raw
            for raw_slice in raw_sliced
            if raw_slice.slice_type == "literal"
        ]
        templater_logger.debug("    Literals: %s", literals)
        for loop_idx in range(2):
            templater_logger.debug("    # Slice Loop %s", loop_idx)
            # Calculate occurrences
            raw_occurrences = self._substring_occurrences(raw_str, literals)
            templated_occurrences = self._substring_occurrences(templated_str, literals)
            templater_logger.debug(
                "    Occurrences: Raw: %s, Templated: %s",
                raw_occurrences,
                templated_occurrences,
            )
            # Split on invariants
            split_sliced = list(
                self._split_invariants(
                    raw_sliced,
                    literals,
                    raw_occurrences,
                    templated_occurrences,
                    templated_str,
                )
            )
            templater_logger.debug("    Split Sliced:")
            for idx, split_slice in enumerate(split_sliced):
                templater_logger.debug("        %s: %r", idx, split_slice)
            # Deal with uniques and coalesce the rest
            sliced_file = list(
                self._split_uniques_coalesce_rest(
                    split_sliced, raw_occurrences, templated_occurrences, templated_str
                )
            )
            templater_logger.debug("    Fully Sliced:")
            for idx, templ_slice in enumerate(sliced_file):
                templater_logger.debug("        %s: %r", idx, templ_slice)
            unwrap_wrapped = (
                True
                if config is None
                else config.get(
                    "unwrap_wrapped_queries", section="templater", default=True
                )
            )
            sliced_file, new_templated_str = self._check_for_wrapped(
                sliced_file, templated_str, unwrap_wrapped=unwrap_wrapped
            )
            if new_templated_str == templated_str:
                # If we didn't change it then we're done.
                break
            else:
                # If it's not equal, loop around
                templated_str = new_templated_str
        return raw_sliced, sliced_file, new_templated_str

    @classmethod
    def _check_for_wrapped(
        cls,
        slices: List[TemplatedFileSlice],
        templated_str: str,
        unwrap_wrapped: bool = True,
    ) -> Tuple[List[TemplatedFileSlice], str]:
        """Identify a wrapped query (e.g. dbt test) and handle it.

        If unwrap_wrapped is true, we trim the wrapping from the templated
        file.
        If unwrap_wrapped is false, we add a slice at start and end.
        """
        if not slices:
            # If there are no slices, return
            return slices, templated_str
        first_slice = slices[0]
        last_slice = slices[-1]

        if unwrap_wrapped:
            # If we're unwrapping, there is no need to edit the slices, but we do need
            # to trim the templated string. We should expect that the template will need
            # to be re-sliced but we should assume that the function calling this one
            # will deal with that eventuality.
            return (
                slices,
                templated_str[
                    first_slice.templated_slice.start : last_slice.templated_slice.stop
                ],
            )

        if (
            first_slice.source_slice.start == 0
            and first_slice.templated_slice.start != 0
        ):
            # This means that there is text at the start of the templated file which
            # doesn't exist in the raw file. Handle this by adding a templated slice
            # (though it's not really templated) between 0 and 0 in the raw, and 0 and
            # the current first slice start index in the templated.
            slices.insert(
                0,
                TemplatedFileSlice(
                    "templated",
                    slice(0, 0),
                    slice(0, first_slice.templated_slice.start),
                ),
            )
        if last_slice.templated_slice.stop != len(templated_str):
            # This means that there is text at the end of the templated file which
            # doesn't exist in the raw file. Handle this by adding a templated slice
            # beginning and ending at the end of the raw, and the current last slice
            # stop and file end in the templated.
            slices.append(
                TemplatedFileSlice(
                    "templated",
                    zero_slice(last_slice.source_slice.stop),
                    slice(last_slice.templated_slice.stop, len(templated_str)),
                )
            )
        return slices, templated_str

    @classmethod
    def _substring_occurrences(
        cls, in_str: str, substrings: Iterable[str]
    ) -> Dict[str, List[int]]:
        """Find every occurrence of the given substrings."""
        occurrences = {}
        for substring in substrings:
            occurrences[substring] = list(findall(substring, in_str))
        return occurrences

    @staticmethod
    def _sorted_occurrence_tuples(
        occurrences: Dict[str, List[int]]
    ) -> List[Tuple[str, int]]:
        """Sort a dict of occurrences into a sorted list of tuples."""
        return sorted(
            ((raw, idx) for raw in occurrences.keys() for idx in occurrences[raw]),
            # Sort first by position, then by lexical (for stability)
            key=lambda x: (x[1], x[0]),
        )

    @classmethod
    def _slice_template(cls, in_str: str) -> Iterator[RawFileSlice]:
        """Slice a templated python string into token tuples.

        This uses Formatter() as per:
        https://docs.python.org/3/library/string.html#string.Formatter
        """
        fmt = Formatter()
        in_idx = 0
        for literal_text, field_name, format_spec, conversion in fmt.parse(in_str):
            if literal_text:
                escape_chars = cls._sorted_occurrence_tuples(
                    cls._substring_occurrences(literal_text, ["}", "{"])
                )
                idx = 0
                while escape_chars:
                    first_char = escape_chars.pop()
                    # Is there a literal first?
                    if first_char[1] > idx:
                        yield RawFileSlice(
                            literal_text[idx : first_char[1]], "literal", in_idx
                        )
                        in_idx += first_char[1] - idx
                    # Add the escaped
                    idx = first_char[1] + len(first_char[0])
                    # We double them here to make the raw
                    yield RawFileSlice(
                        literal_text[first_char[1] : idx] * 2, "escaped", in_idx
                    )
                    # Will always be 2 in this case.
                    # This is because ALL escape sequences in the python formatter
                    # are two characters which reduce to one.
                    in_idx += 2
                # Deal with last one (if present)
                if literal_text[idx:]:
                    yield RawFileSlice(literal_text[idx:], "literal", in_idx)
                    in_idx += len(literal_text) - idx
            # Deal with fields
            if field_name:
                constructed_token = "{{{field_name}{conv}{spec}}}".format(
                    field_name=field_name,
                    conv=f"!{conversion}" if conversion else "",
                    spec=f":{format_spec}" if format_spec else "",
                )
                yield RawFileSlice(constructed_token, "templated", in_idx)
                in_idx += len(constructed_token)

    @classmethod
    def _split_invariants(
        cls,
        raw_sliced: List[RawFileSlice],
        literals: List[str],
        raw_occurrences: Dict[str, List[int]],
        templated_occurrences: Dict[str, List[int]],
        templated_str: str,
    ) -> Iterator[IntermediateFileSlice]:
        """Split a sliced file on its invariant literals.

        We prioritise the _longest_ invariants first as they
        are more likely to the the anchors.
        """
        # Calculate invariants
        invariants = [
            literal
            for literal in literals
            if len(raw_occurrences[literal]) == 1
            and len(templated_occurrences[literal]) == 1
        ]
        # Work through the invariants and make sure they appear
        # in order.
        for linv in sorted(invariants, key=len, reverse=True):
            # Any invariants which have templated positions, relative
            # to source positions, which aren't in order, should be
            # ignored.

            # Is this one still relevant?
            if linv not in invariants:
                continue  # pragma: no cover

            source_pos, templ_pos = raw_occurrences[linv], templated_occurrences[linv]
            # Copy the list before iterating because we're going to edit it.
            for tinv in invariants.copy():
                if tinv != linv:
                    src_dir = source_pos > raw_occurrences[tinv]
                    tmp_dir = templ_pos > templated_occurrences[tinv]
                    # If it's not in the same direction in the source and template
                    # remove it.
                    if src_dir != tmp_dir:  # pragma: no cover
                        templater_logger.debug(
                            "          Invariant found out of order: %r", tinv
                        )
                        invariants.remove(tinv)

        # Set up some buffers
        buffer: List[RawFileSlice] = []
        idx: Optional[int] = None
        templ_idx = 0
        # Loop through
        for raw_file_slice in raw_sliced:
            if raw_file_slice.raw in invariants:
                if buffer:
                    yield IntermediateFileSlice(
                        "compound",
                        slice(idx, raw_file_slice.source_idx),
                        slice(templ_idx, templated_occurrences[raw_file_slice.raw][0]),
                        buffer,
                    )
                buffer = []
                idx = None
                yield IntermediateFileSlice(
                    "invariant",
                    offset_slice(
                        raw_file_slice.source_idx,
                        len(raw_file_slice.raw),
                    ),
                    offset_slice(
                        templated_occurrences[raw_file_slice.raw][0],
                        len(raw_file_slice.raw),
                    ),
                    [
                        RawFileSlice(
                            raw_file_slice.raw,
                            raw_file_slice.slice_type,
                            templated_occurrences[raw_file_slice.raw][0],
                        )
                    ],
                )
                templ_idx = templated_occurrences[raw_file_slice.raw][0] + len(
                    raw_file_slice.raw
                )
            else:
                buffer.append(
                    RawFileSlice(
                        raw_file_slice.raw,
                        raw_file_slice.slice_type,
                        raw_file_slice.source_idx,
                    )
                )
                if idx is None:
                    idx = raw_file_slice.source_idx
        # If we have a final buffer, yield it
        if buffer:
            yield IntermediateFileSlice(
                "compound",
                slice((idx or 0), (idx or 0) + sum(len(slc.raw) for slc in buffer)),
                slice(templ_idx, len(templated_str)),
                buffer,
            )

    @staticmethod
    def _filter_occurrences(
        file_slice: slice, occurrences: Dict[str, List[int]]
    ) -> Dict[str, List[int]]:
        """Filter a dict of occurrences to just those within a slice."""
        filtered = {
            key: [
                pos
                for pos in occurrences[key]
                if pos >= file_slice.start and pos < file_slice.stop
            ]
            for key in occurrences.keys()
        }
        return {key: filtered[key] for key in filtered.keys() if filtered[key]}

    @staticmethod
    def _coalesce_types(elems: List[RawFileSlice]) -> str:
        """Coalesce to the priority type."""
        # Make a set of types
        types = {elem.slice_type for elem in elems}
        # Replace block types with templated
        for typ in list(types):
            if typ.startswith("block_"):  # pragma: no cover
                types.remove(typ)
                types.add("templated")
        # Take the easy route if they're all the same type
        if len(types) == 1:
            return types.pop()
        # Then deal with priority
        priority = ["templated", "escaped", "literal"]
        for p in priority:
            if p in types:
                return p
        raise RuntimeError(
            f"Exhausted priorities in _coalesce_types! {types!r}"
        )  # pragma: no cover

    @classmethod
    def _split_uniques_coalesce_rest(
        cls,
        split_file: List[IntermediateFileSlice],
        raw_occurrences: Dict[str, List[int]],
        templ_occurrences: Dict[str, List[int]],
        templated_str: str,
    ) -> Iterator[TemplatedFileSlice]:
        """Within each of the compound sections split on unique literals.

        For everything else we coalesce to the dominant type.

        Returns:
            Iterable of the type of segment, the slice in the raw file
                and the slice in the templated file.

        """
        # A buffer to capture tail segments
        tail_buffer: List[TemplatedFileSlice] = []

        templater_logger.debug("    _split_uniques_coalesce_rest: %s", split_file)

        for int_file_slice in split_file:
            # Yield anything from the tail buffer
            if tail_buffer:  # pragma: no cover
                templater_logger.debug(
                    "        Yielding Tail Buffer [start]: %s", tail_buffer
                )
                yield from tail_buffer
                tail_buffer = []

            # Check whether we're handling a zero length slice.
            if (
                int_file_slice.templated_slice.stop
                - int_file_slice.templated_slice.start
                == 0
            ):  # pragma: no cover
                point_combo = int_file_slice.coalesce()
                templater_logger.debug(
                    "        Yielding Point Combination: %s", point_combo
                )
                yield point_combo
                continue

            # Yield anything simple
            try:
                simple_elem = int_file_slice.try_simple()
                templater_logger.debug("        Yielding Simple: %s", simple_elem)
                yield simple_elem
                continue
            except ValueError:
                pass

            # Trim ends and overwrite the current working copy.
            head_buffer, int_file_slice, tail_buffer = int_file_slice.trim_ends(
                templated_str=templated_str
            )
            if head_buffer:
                yield from head_buffer  # pragma: no cover
            # Have we consumed the whole thing?
            if not int_file_slice.slice_buffer:
                continue  # pragma: no cover

            # Try to yield simply again (post trim)
            try:  # pragma: no cover
                simple_elem = int_file_slice.try_simple()
                templater_logger.debug("        Yielding Simple: %s", simple_elem)
                yield simple_elem
                continue
            except ValueError:
                pass

            templater_logger.debug("        Intermediate Slice: %s", int_file_slice)
            # Generate the coalesced version in case we need it
            coalesced = int_file_slice.coalesce()

            # Look for anchors
            raw_occs = cls._filter_occurrences(
                int_file_slice.source_slice, raw_occurrences
            )
            templ_occs = cls._filter_occurrences(
                int_file_slice.templated_slice, templ_occurrences
            )
            # Do we have any uniques to split on?
            # NB: We use `get` on the templated occurrences, because it's possible
            # that because of an if statement, something is in the source, but
            # not in the templated at all. In that case, we shouldn't use it.
            one_way_uniques = [
                key
                for key in raw_occs.keys()
                if len(raw_occs[key]) == 1 and len(templ_occs.get(key, [])) >= 1
            ]
            two_way_uniques = [
                key for key in one_way_uniques if len(templ_occs[key]) == 1
            ]
            # if we don't have anything to anchor on, then just return (coalescing
            # types)
            if not raw_occs or not templ_occs or not one_way_uniques:
                templater_logger.debug(
                    "        No Anchors or Uniques. Yielding Whole: %s", coalesced
                )
                yield coalesced
                continue

            # Deal with the inner segment itself.
            templater_logger.debug(
                "        Intermediate Slice [post trim]: %s: %r",
                int_file_slice,
                templated_str[int_file_slice.templated_slice],
            )
            templater_logger.debug("        One Way Uniques: %s", one_way_uniques)
            templater_logger.debug("        Two Way Uniques: %s", two_way_uniques)

            # Hang onto the starting position, which we'll advance as we go.
            starts = (
                int_file_slice.source_slice.start,
                int_file_slice.templated_slice.start,
            )

            # Deal with two way uniques first, because they are easier.
            # If we do find any we use recursion, because we'll want to do
            # all of the above checks again.
            if two_way_uniques:
                # Yield the uniques and coalesce anything between.
                bookmark_idx = 0
                for idx, raw_slice in enumerate(int_file_slice.slice_buffer):
                    pos = 0
                    unq: Optional[str] = None
                    # Does this element contain one of our uniques? If so, where?
                    for unique in two_way_uniques:
                        if unique in raw_slice.raw:
                            pos = raw_slice.raw.index(unique)
                            unq = unique

                    if unq:
                        # Yes it does. Handle it.

                        # Get the position of the unique section.
                        unique_position = (
                            raw_occs[unq][0],
                            templ_occs[unq][0],
                        )
                        templater_logger.debug(
                            "            Handling Unique: %r, %s, %s, %r",
                            unq,
                            pos,
                            unique_position,
                            raw_slice,
                        )

                        # Handle full slices up to this one
                        if idx > bookmark_idx:
                            # Recurse to deal with any loops separately
                            yield from cls._split_uniques_coalesce_rest(
                                [
                                    IntermediateFileSlice(
                                        "compound",
                                        # slice up to this unique
                                        slice(starts[0], unique_position[0] - pos),
                                        slice(starts[1], unique_position[1] - pos),
                                        int_file_slice.slice_buffer[bookmark_idx:idx],
                                    )
                                ],
                                raw_occs,
                                templ_occs,
                                templated_str,
                            )

                        # Handle any potential partial slice if we're part way through
                        # this one.
                        if pos > 0:
                            yield TemplatedFileSlice(
                                raw_slice.slice_type,
                                slice(unique_position[0] - pos, unique_position[0]),
                                slice(unique_position[1] - pos, unique_position[1]),
                            )

                        # Handle the unique itself and update the bookmark
                        starts = (
                            unique_position[0] + len(unq),
                            unique_position[1] + len(unq),
                        )
                        yield TemplatedFileSlice(
                            raw_slice.slice_type,
                            slice(unique_position[0], starts[0]),
                            slice(unique_position[1], starts[1]),
                        )
                        # Move the bookmark after this position
                        bookmark_idx = idx + 1

                        # Handle any remnant after the unique.
                        if raw_slice.raw[pos + len(unq) :]:
                            remnant_length = len(raw_slice.raw) - (len(unq) + pos)
                            _starts = starts
                            starts = (
                                starts[0] + remnant_length,
                                starts[1] + remnant_length,
                            )
                            yield TemplatedFileSlice(
                                raw_slice.slice_type,
                                slice(_starts[0], starts[0]),
                                slice(_starts[1], starts[1]),
                            )

                if bookmark_idx == 0:  # pragma: no cover
                    # This is a SAFETY VALVE. In Theory we should never be here
                    # and if we are it implies an error elsewhere. This clause
                    # should stop any potential infinite recursion in its tracks
                    # by simply classifying the whole of the current block as
                    # templated and just stopping here.
                    # Bugs triggering this eventuality have been observed in 0.4.0.
                    templater_logger.info(
                        "        Safety Value Info: %s, %r",
                        two_way_uniques,
                        templated_str[int_file_slice.templated_slice],
                    )
                    templater_logger.warning(
                        "        Python templater safety value unexpectedly triggered. "
                        "Please report your raw and compiled query on github for "
                        "debugging."
                    )
                    # NOTE: If a bug is reported here, this will incorrectly
                    # classify more of the query as "templated" than it should.
                    yield coalesced
                    continue

                # At the end of the loop deal with any remaining slices.
                # The above "Safety Valve"TM should keep us safe from infinite
                # recursion.
                if len(int_file_slice.slice_buffer) > bookmark_idx:
                    # Recurse to deal with any loops separately
                    yield from cls._split_uniques_coalesce_rest(
                        [
                            IntermediateFileSlice(
                                "compound",
                                # Slicing is easy here, we have no choice
                                slice(starts[0], int_file_slice.source_slice.stop),
                                slice(starts[1], int_file_slice.templated_slice.stop),
                                # Calculate the subsection to deal with.
                                int_file_slice.slice_buffer[
                                    bookmark_idx : len(int_file_slice.slice_buffer)
                                ],
                            )
                        ],
                        raw_occs,
                        templ_occs,
                        templated_str,
                    )
                # We continue here because the buffer should be exhausted,
                # and if there's more to do we'll do it in the recursion.
                continue

            # If we get here, then there ARE uniques, but they are only ONE WAY.
            # This means loops. Loops are tricky.
            # We're very unlikely to get here (impossible?) with just python
            # formatting, but this class is also the base for the jinja templater
            # (and others?) so it may be used there.
            # One way uniques give us landmarks to try and estimate what to do with
            # them.
            owu_templ_tuples = cls._sorted_occurrence_tuples(  # pragma: no cover
                {key: templ_occs[key] for key in one_way_uniques}
            )

            templater_logger.debug(  # pragma: no cover
                "        Handling One Way Uniques: %s", owu_templ_tuples
            )

            # Hang onto out *ending* position too from here.
            stops = (  # pragma: no cover
                int_file_slice.source_slice.stop,
                int_file_slice.templated_slice.stop,
            )

            # OWU in this context refers to "One Way Unique"
            this_owu_idx: Optional[int] = None  # pragma: no cover
            last_owu_idx: Optional[int] = None  # pragma: no cover
            # Iterate through occurrence tuples of the one-way uniques.
            for raw, template_idx in owu_templ_tuples:  # pragma: no cover
                raw_idx = raw_occs[raw][0]
                raw_len = len(raw)

                # Find the index of this owu in the slice_buffer, store the previous
                last_owu_idx = this_owu_idx
                try:
                    this_owu_idx = next(
                        idx
                        for idx, slc in enumerate(int_file_slice.slice_buffer)
                        if slc.raw == raw
                    )
                except StopIteration:  # pragma: no cover
                    # This can happen if the unique was detected, but was introduced
                    # by a templater step. This is a false positive. Skip and move on.
                    templater_logger.info(
                        "One Way Unique %r not found in slice buffer. Skipping...", raw
                    )
                    continue

                templater_logger.debug(
                    "        Handling OWU: %r @%s (raw @%s) [this_owu_idx: %s, "
                    "last_owu_dx: %s]",
                    raw,
                    template_idx,
                    raw_idx,
                    this_owu_idx,
                    last_owu_idx,
                )

                if template_idx > starts[1]:
                    # Yield the bit before this literal. We yield it
                    # all as a tuple, because if we could do any better
                    # we would have done it by now.

                    # Can we identify a meaningful portion of the patch
                    # to recurse a split?
                    sub_section: Optional[List[RawFileSlice]] = None
                    # If it's the start, the slicing is easy
                    if (
                        starts[1] == int_file_slice.templated_slice.stop
                    ):  # pragma: no cover TODO?
                        sub_section = int_file_slice.slice_buffer[:this_owu_idx]
                    # If we are AFTER the previous in the template, then it's
                    # also easy. [assuming it's not the same owu]
                    elif (
                        raw_idx > starts[0] and last_owu_idx != this_owu_idx
                    ):  # pragma: no cover
                        if last_owu_idx:
                            sub_section = int_file_slice.slice_buffer[
                                last_owu_idx + 1 : this_owu_idx
                            ]
                        else:
                            sub_section = int_file_slice.slice_buffer[:this_owu_idx]

                    # If we succeeded in one of the above, we can also recurse
                    # and be more intelligent with the other sections.
                    if sub_section:
                        templater_logger.debug(
                            "        Attempting Subsplit [pre]: %s, %r",
                            sub_section,
                            templated_str[slice(starts[1], template_idx)],
                        )
                        yield from cls._split_uniques_coalesce_rest(
                            [
                                IntermediateFileSlice(
                                    "compound",
                                    # Slicing is easy here, we have no choice
                                    slice(starts[0], raw_idx),
                                    slice(starts[1], template_idx),
                                    sub_section,
                                )
                            ],
                            raw_occs,
                            templ_occs,
                            templated_str,
                        )
                    # Otherwise, it's the tricky case.
                    else:
                        # In this case we've found a literal, coming AFTER another
                        # in the templated version, but BEFORE (or the same) in the
                        # raw version. This only happens during loops, but it means
                        # that identifying exactly what the intervening bit refers
                        # to is a bit arbitrary. In this case we're going to OVER
                        # estimate and refer to the whole loop segment.

                        # TODO: Maybe this should make two chunks instead, one
                        # working backward, and one working forward. But that's
                        # a job for another day.

                        # First find where we are starting this remainder
                        # in the template (as an index in the buffer).
                        # Any segments *after* cur_idx are involved.
                        if last_owu_idx is None or last_owu_idx + 1 >= len(
                            int_file_slice.slice_buffer
                        ):
                            cur_idx = 0
                        else:
                            cur_idx = last_owu_idx + 1

                        # We need to know how many block_ends are after this.
                        block_ends = sum(
                            slc.slice_type == "block_end"
                            for slc in int_file_slice.slice_buffer[cur_idx:]
                        )
                        # We can allow up to this number of preceding block starts
                        block_start_indices = [
                            idx
                            for idx, slc in enumerate(
                                int_file_slice.slice_buffer[:cur_idx]
                            )
                            if slc.slice_type == "block_start"
                        ]

                        # Trim anything which we're not allowed to use.
                        if len(block_start_indices) > block_ends:  # pragma: no cover
                            offset = block_start_indices[-1 - block_ends] + 1
                            elem_sub_buffer = int_file_slice.slice_buffer[offset:]
                            cur_idx -= offset
                        else:
                            elem_sub_buffer = int_file_slice.slice_buffer

                        # We also need to know whether any of the *starting*
                        # segments are involved.
                        # Anything up to start_idx (exclusive) is included.
                        include_start = raw_idx > elem_sub_buffer[0].source_idx

                        # The ending point of this slice, is already decided.
                        end_point = elem_sub_buffer[-1].end_source_idx()

                        # If start_idx is None, we're in luck. We don't need to include
                        # the beginning.
                        if include_start:
                            start_point = elem_sub_buffer[0].source_idx
                        # Otherwise we know it's looped round, we need to include the
                        # whole slice.
                        else:  # pragma: no cover
                            start_point = elem_sub_buffer[cur_idx].source_idx

                        tricky = TemplatedFileSlice(
                            "templated",
                            slice(start_point, end_point),
                            slice(starts[1], template_idx),
                        )

                        templater_logger.debug(
                            "        Yielding Tricky Case : %s",
                            tricky,
                        )

                        yield tricky

                # Yield the literal
                owu_literal_slice = TemplatedFileSlice(
                    "literal",
                    offset_slice(raw_idx, raw_len),
                    offset_slice(template_idx, raw_len),
                )
                templater_logger.debug(
                    "    Yielding Unique: %r, %s",
                    raw,
                    owu_literal_slice,
                )
                yield owu_literal_slice
                # Update our bookmark
                starts = (
                    raw_idx + raw_len,
                    template_idx + raw_len,
                )

            if starts[1] < stops[1] and last_owu_idx is not None:  # pragma: no cover
                # Yield the end bit
                templater_logger.debug("        Attempting Subsplit [post].")
                yield from cls._split_uniques_coalesce_rest(
                    [
                        IntermediateFileSlice(
                            "compound",
                            # Slicing is easy here, we have no choice
                            slice(raw_idx + raw_len, stops[0]),
                            slice(starts[1], stops[1]),
                            int_file_slice.slice_buffer[last_owu_idx + 1 :],
                        )
                    ],
                    raw_occs,
                    templ_occs,
                    templated_str,
                )

        # Yield anything from the tail buffer
        if tail_buffer:  # pragma: no cover
            templater_logger.debug(
                "        Yielding Tail Buffer [end]: %s", tail_buffer
            )
            yield from tail_buffer
