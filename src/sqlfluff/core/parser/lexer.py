"""The code for the Lexer."""

import logging
from typing import Iterator, Optional, List, Tuple, Union, NamedTuple
from uuid import UUID, uuid4
import regex

from sqlfluff.core.parser.segments import (
    BaseSegment,
    RawSegment,
    Indent,
    Dedent,
    TemplateSegment,
    UnlexableSegment,
    EndOfFile,
    TemplateLoop,
)
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.errors import SQLLexError
from sqlfluff.core.templaters import TemplatedFile
from sqlfluff.core.config import FluffConfig
from sqlfluff.core.templaters.base import TemplatedFileSlice

# Instantiate the lexer logger
lexer_logger = logging.getLogger("sqlfluff.lexer")


def _slice_length(s: slice) -> int:
    return s.stop - s.start


def _is_zero_slice(s: slice) -> bool:
    return s.stop == s.start


class LexedElement(NamedTuple):
    """An element matched during lexing."""

    raw: str
    matcher: "StringLexer"


class TemplateElement(NamedTuple):
    """A LexedElement, bundled with it's position in the templated file."""

    raw: str
    template_slice: slice
    matcher: "StringLexer"

    @classmethod
    def from_element(cls, element: LexedElement, template_slice: slice):
        """Make a TemplateElement from a LexedElement."""
        return cls(
            raw=element.raw, template_slice=template_slice, matcher=element.matcher
        )

    def to_segment(self, pos_marker, subslice=None):
        """Create a segment from this lexed element."""
        return self.matcher.construct_segment(
            self.raw[subslice] if subslice else self.raw, pos_marker=pos_marker
        )


class LexMatch(NamedTuple):
    """A class to hold matches from the Lexer."""

    forward_string: str
    elements: List[LexedElement]

    def __bool__(self):
        """A LexMatch is truthy if it contains a non-zero number of matched elements."""
        return len(self.elements) > 0


class StringLexer:
    """This singleton matcher matches strings exactly.

    This is the simplest usable matcher, but it also defines some of the
    mechanisms for more complicated matchers, which may simply override the
    `_match` function rather than the public `match` function.  This acts as
    the base class for matchers.
    """

    def __init__(
        self,
        name,
        template,
        segment_class,
        subdivider=None,
        trim_post_subdivide=None,
        segment_kwargs=None,
    ):
        self.name = name
        self.template = template
        self.segment_class = segment_class
        self.subdivider = subdivider
        self.trim_post_subdivide = trim_post_subdivide
        self.segment_kwargs = segment_kwargs or {}

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"

    def _match(self, forward_string: str) -> Optional[LexedElement]:
        """The private match function. Just look for a literal string."""
        if forward_string.startswith(self.template):
            return LexedElement(self.template, self)
        else:
            return None

    def search(self, forward_string: str) -> Optional[Tuple[int, int]]:
        """Use string methods to find a substring."""
        loc = forward_string.find(self.template)
        if loc >= 0:
            return loc, loc + len(self.template)
        else:
            return None

    def _trim_match(self, matched_str: str) -> List[LexedElement]:
        """Given a string, trim if we are allowed to.

        Returns:
            :obj:`tuple` of LexedElement

        """
        elem_buff: List[LexedElement] = []
        content_buff = ""
        str_buff = matched_str

        if self.trim_post_subdivide:
            while str_buff:
                # Iterate through subdividing as appropriate
                trim_pos = self.trim_post_subdivide.search(str_buff)
                # No match? Break
                if not trim_pos:
                    break
                # Start match?
                elif trim_pos[0] == 0:
                    elem_buff.append(
                        LexedElement(
                            str_buff[: trim_pos[1]],
                            self.trim_post_subdivide,
                        )
                    )
                    str_buff = str_buff[trim_pos[1] :]
                # End Match?
                elif trim_pos[1] == len(str_buff):
                    elem_buff += [
                        LexedElement(
                            content_buff + str_buff[: trim_pos[0]],
                            self,
                        ),
                        LexedElement(
                            str_buff[trim_pos[0] : trim_pos[1]],
                            self.trim_post_subdivide,
                        ),
                    ]
                    content_buff, str_buff = "", ""
                # Mid Match? (carry on)
                else:
                    content_buff += str_buff[: trim_pos[1]]
                    str_buff = str_buff[trim_pos[1] :]

        # Do we have anything left? (or did nothing happen)
        if content_buff + str_buff:
            elem_buff.append(
                LexedElement(content_buff + str_buff, self),
            )
        return elem_buff

    def _subdivide(self, matched: LexedElement) -> List[LexedElement]:
        """Given a string, subdivide if we area allowed to.

        Returns:
            :obj:`tuple` of segments

        """
        # Can we have to subdivide?
        if self.subdivider:
            # Yes subdivision
            elem_buff: List[LexedElement] = []
            str_buff = matched.raw
            while str_buff:
                # Iterate through subdividing as appropriate
                div_pos = self.subdivider.search(str_buff)
                if div_pos:
                    # Found a division
                    trimmed_elems = self._trim_match(str_buff[: div_pos[0]])
                    div_elem = LexedElement(
                        str_buff[div_pos[0] : div_pos[1]], self.subdivider
                    )
                    elem_buff += trimmed_elems + [div_elem]
                    str_buff = str_buff[div_pos[1] :]
                else:
                    # No more division matches. Trim?
                    trimmed_elems = self._trim_match(str_buff)
                    elem_buff += trimmed_elems
                    break
            return elem_buff
        else:
            return [matched]

    def match(self, forward_string: str) -> LexMatch:
        """Given a string, match what we can and return the rest.

        Returns:
            :obj:`LexMatch`

        """
        if len(forward_string) == 0:  # pragma: no cover
            raise ValueError("Unexpected empty string!")
        matched = self._match(forward_string)

        if matched:
            # Handle potential subdivision elsewhere.
            new_elements = self._subdivide(matched)

            return LexMatch(
                forward_string[len(matched.raw) :],
                new_elements,
            )
        else:
            return LexMatch(forward_string, [])

    def construct_segment(self, raw, pos_marker):
        """Construct a segment using the given class a properties."""
        return self.segment_class(raw=raw, pos_marker=pos_marker, **self.segment_kwargs)


class RegexLexer(StringLexer):
    """This RegexLexer matches based on regular expressions."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We might want to configure this at some point, but for now, newlines
        # do get matched by .
        flags = regex.DOTALL
        self._compiled_regex = regex.compile(self.template, flags)

    def _match(self, forward_string: str) -> Optional[LexedElement]:
        """Use regexes to match chunks."""
        match = self._compiled_regex.match(forward_string)
        if match:
            # We can only match strings with length
            match_str = match.group(0)
            if match_str:
                return LexedElement(match_str, self)
            else:
                lexer_logger.warning(
                    f"Zero length Lex item returned from {self.name!r}. Report this as "
                    "a bug."
                )
        return None

    def search(self, forward_string: str) -> Optional[Tuple[int, int]]:
        """Use regex to find a substring."""
        match = self._compiled_regex.search(forward_string)
        if match:
            # We can only match strings with length
            if match.group(0):
                return match.span()
            else:  # pragma: no cover
                lexer_logger.warning(
                    f"Zero length Lex item returned from {self.name!r}. Report this as "
                    "a bug."
                )
        return None


def _handle_zero_length_slice(
    tfs: TemplatedFileSlice,
    next_tfs: Optional[TemplatedFileSlice],
    block_stack: List[UUID],
    templated_file: TemplatedFile,
    add_indents: bool,
):
    """Generate placeholders and loop segments from a zero length slice.

    This method checks for:
    1. Backward jumps (inserting :obj:`TemplateLoop`).
    2. Forward jumps (inserting :obj:`TemplateSegment`).
    3. Blocks (inserting :obj:`TemplateSegment`).
    4. Unrendered template elements(inserting :obj:`TemplateSegment`).

    For blocks and loops, :obj:`Indent` and :obj:`Dedent` segments are
    yielded around them as appropriate.

    NOTE: block_stack is _mutated_ by this method.
    """
    assert _is_zero_slice(tfs.templated_slice)
    # First check for jumps. Backward initially, because in the backward
    # case we don't render the element we find first.
    # That requires being able to look past to the next element.
    if tfs.slice_type.startswith("block") and next_tfs:
        # Look for potential backward jump
        if next_tfs.source_slice.start < tfs.source_slice.start:
            lexer_logger.debug("      Backward jump detected. Inserting Loop Marker")
            # If we're here remember we're on the tfs which is the block end
            # i.e. not the thing we want to render.
            pos_marker = PositionMarker.from_point(
                tfs.source_slice.start,
                tfs.templated_slice.start,
                templated_file,
            )
            if add_indents:
                yield Dedent(
                    is_template=True,
                    pos_marker=pos_marker,
                )

            yield TemplateLoop(pos_marker=pos_marker, block_uuid=block_stack[-1])

            if add_indents:
                yield Indent(
                    is_template=True,
                    pos_marker=pos_marker,
                )
            # Move on to the next templated slice. Don't render this directly.
            return

    # Then handle blocks (which aren't jumps backward)
    if tfs.slice_type.startswith("block"):
        # It's a block. Yield a placeholder with potential indents.
        if add_indents and tfs.slice_type in ("block_end", "block_mid"):
            yield Dedent(
                is_template=True,
                pos_marker=PositionMarker.from_point(
                    tfs.source_slice.start,
                    tfs.templated_slice.start,
                    templated_file,
                ),
            )

        # Update block stack
        if tfs.slice_type == "block_start":
            block_stack.append(uuid4())

        yield TemplateSegment.from_slice(
            tfs.source_slice,
            tfs.templated_slice,
            block_type=tfs.slice_type,
            templated_file=templated_file,
            block_uuid=block_stack[-1],
        )

        # Update block stack
        if tfs.slice_type == "block_end":
            block_stack.pop()

        if add_indents and tfs.slice_type in ("block_start", "block_mid"):
            yield Indent(
                is_template=True,
                pos_marker=PositionMarker.from_point(
                    tfs.source_slice.stop,
                    tfs.templated_slice.stop,
                    templated_file,
                ),
            )

        # Before we move on, we might have a _forward_ jump to the next
        # element. That element can handle itself, but we'll add a
        # placeholder for it here before we move on.
        if next_tfs:
            # Identify whether we have a skip.
            skipped_chars = next_tfs.source_slice.start - tfs.source_slice.stop
            placeholder_str = ""
            if skipped_chars >= 10:
                placeholder_str = (
                    f"... [{skipped_chars} unused template " "characters] ..."
                )
            elif skipped_chars:
                placeholder_str = "..."

            # Handle it if we do.
            if placeholder_str:
                lexer_logger.debug("      Forward jump detected. Inserting placeholder")
                yield TemplateSegment(
                    pos_marker=PositionMarker(
                        slice(tfs.source_slice.stop, next_tfs.source_slice.start),
                        # Zero slice in the template.
                        tfs.templated_slice,
                        templated_file,
                    ),
                    source_str=placeholder_str,
                    block_type="skipped_source",
                )

        # Move on
        return

    # We've got a zero slice. This could be a block, unrendered templates
    # or unrendered code (either because of loops of consumption).
    if not _is_zero_slice(tfs.source_slice):
        yield TemplateSegment.from_slice(
            tfs.source_slice,
            tfs.templated_slice,
            tfs.slice_type,
            templated_file,
        )
    return


def _iter_segments(
    lexed_elements: List[TemplateElement],
    templated_file_slices: List[TemplatedFileSlice],
    templated_file: TemplatedFile,
    add_indents: bool = True,
) -> Iterator[RawSegment]:
    # An index to track where we've got to in the templated file.
    tfs_idx = 0
    block_stack: List[UUID] = []

    # Now work out source slices, and add in template placeholders.
    for idx, element in enumerate(lexed_elements):
        # We're working through elements in the rendered file.
        # When they enter this code they don't have a position in the source.
        # We already have a map of how templated elements map to the source file
        # so we work through them to work out what's going on. In theory we can
        # step through the two lists in lock step.

        # i.e. we worked through the lexed elements, but check off the templated
        # file slices as we go.

        # Output the slice as we lex.
        lexer_logger.debug("  %s: %s. [tfs_idx = %s]", idx, element, tfs_idx)

        # All lexed elements, by definition, have a position in the templated
        # file. That means we've potentially got zero-length elements we also
        # need to consider. We certainly need to consider templated slices
        # at tfs_idx. But we should consider some others after that which we
        # might also need to consider.

        # A lexed element is either a literal in the raw file or the result
        # (or part of the result) of a template placeholder. We don't make
        # placeholders for any variables which return a non-zero length of
        # code. We do add placeholders for others.

        # The amount of the current element which has already been consumed.
        consumed_element_length = 0
        # The position in the source which we still need to yield from.
        stashed_source_idx = None

        for tfs_idx, tfs in enumerate(templated_file_slices[tfs_idx:], tfs_idx):
            lexer_logger.debug("      %s: %s", tfs_idx, tfs)

            # Is it a zero slice?
            if _is_zero_slice(tfs.templated_slice):
                next_tfs = (
                    templated_file_slices[tfs_idx + 1]
                    if tfs_idx + 1 < len(templated_file_slices)
                    else None
                )
                yield from _handle_zero_length_slice(
                    tfs, next_tfs, block_stack, templated_file, add_indents
                )
                continue

            if tfs.slice_type == "literal":
                # There's a literal to deal with here. Yield as much as we can.

                # Can we cover this whole lexed element with the current templated
                # slice without moving on?
                tfs_offset = tfs.source_slice.start - tfs.templated_slice.start
                # NOTE: Greater than OR EQUAL, to include the case of it matching
                # length exactly.
                if element.template_slice.stop <= tfs.templated_slice.stop:
                    lexer_logger.debug(
                        "     Consuming whole from literal. Existing Consumed: %s",
                        consumed_element_length,
                    )
                    # If we have a stashed start use that. Otherwise infer start.
                    if stashed_source_idx is not None:
                        slice_start = stashed_source_idx
                    else:
                        slice_start = (
                            element.template_slice.start
                            + consumed_element_length
                            + tfs_offset
                        )
                    yield element.to_segment(
                        pos_marker=PositionMarker(
                            slice(
                                slice_start,
                                element.template_slice.stop + tfs_offset,
                            ),
                            element.template_slice,
                            templated_file,
                        ),
                        subslice=slice(consumed_element_length, None),
                    )

                    # If it was an exact match, consume the templated element too.
                    if element.template_slice.stop == tfs.templated_slice.stop:
                        tfs_idx += 1
                    # In any case, we're done with this element. Move on
                    break
                elif element.template_slice.start == tfs.templated_slice.stop:
                    # Did we forget to move on from the last tfs and there's
                    # overlap?
                    # NOTE: If the rest of the logic works, this should never
                    # happen. Unless it's got a zero length in the rendered file
                    # i.e. it's a consumed bit of whitespace or similar.
                    if _is_zero_slice(tfs.templated_slice):
                        lexer_logger.debug("     Found consumed literal.")
                        yield TemplateSegment.from_slice(
                            tfs.source_slice,
                            tfs.templated_slice,
                            tfs.slice_type,
                            templated_file,
                        )
                    else:
                        lexer_logger.debug("     NOTE: Missed Skip")  # pragma: no cover
                    continue  # pragma: no cover
                else:
                    # This means that the current lexed element spans across
                    # multiple templated file slices.
                    lexer_logger.debug("     Consuming whole spanning literal")
                    # This almost certainly means there's a templated element
                    # in the middle of a whole lexed element.

                    # What we do here depends on whether we're allowed to split
                    # lexed elements. This is basically only true if it's whitespace.
                    # NOTE: We should probably make this configurable on the
                    # matcher object, but for now we're going to look for the
                    # name of the lexer.
                    if element.matcher.name == "whitespace":
                        # We *can* split it!
                        # Consume what we can from this slice and move on.
                        lexer_logger.debug(
                            "     Consuming split whitespace from literal. "
                            "Existing Consumed: %s",
                            consumed_element_length,
                        )
                        if stashed_source_idx is not None:
                            raise NotImplementedError(
                                "Found literal whitespace with stashed idx!"
                            )
                        incremental_length = (
                            tfs.templated_slice.stop - element.template_slice.start
                        )
                        yield element.to_segment(
                            pos_marker=PositionMarker(
                                slice(
                                    element.template_slice.start
                                    + consumed_element_length
                                    + tfs_offset,
                                    tfs.templated_slice.stop + tfs_offset,
                                ),
                                element.template_slice,
                                templated_file,
                            ),
                            # Subdivide the existing segment.
                            subslice=slice(
                                consumed_element_length,
                                consumed_element_length + incremental_length,
                            ),
                        )
                        consumed_element_length += incremental_length
                        continue
                    else:
                        # We can't split it. We're going to end up yielding a segment
                        # which spans multiple slices. Stash the type, and if we haven't
                        # set the start yet, stash it too.
                        lexer_logger.debug("     Spilling over literal slice.")
                        if stashed_source_idx is None:
                            stashed_source_idx = (
                                element.template_slice.start + tfs_offset
                            )
                            lexer_logger.debug(
                                "     Stashing a source start. %s", stashed_source_idx
                            )
                        continue

            elif tfs.slice_type == "templated":
                # Found a templated slice. Does it have length in the templated file?
                # If it doesn't, then we'll pick it up next.
                if not _is_zero_slice(tfs.templated_slice):
                    # Is our current element totally contained in this slice?
                    if element.template_slice.stop <= tfs.templated_slice.stop:
                        lexer_logger.debug("     Contained templated slice.")
                        # Yes it is. Add lexed element with source slices as the whole
                        # span of the source slice for the file slice.
                        # If we've got an existing stashed source start, use that
                        # as the start of the source slice.
                        if stashed_source_idx is not None:
                            slice_start = stashed_source_idx
                        else:
                            slice_start = (
                                tfs.source_slice.start + consumed_element_length
                            )
                        yield element.to_segment(
                            pos_marker=PositionMarker(
                                slice(
                                    slice_start,
                                    # The end in the source is the end of the templated
                                    # slice. We can't subdivide any better.
                                    tfs.source_slice.stop,
                                ),
                                element.template_slice,
                                templated_file,
                            ),
                            subslice=slice(consumed_element_length, None),
                        )

                        # If it was an exact match, consume the templated element too.
                        if element.template_slice.stop == tfs.templated_slice.stop:
                            tfs_idx += 1
                        # Carry on to the next lexed element
                        break
                    # We've got an element which extends beyond this templated slice.
                    # This means that a _single_ lexed element claims both some
                    # templated elements and some non-templated elements. That could
                    # include all kinds of things (and from here we don't know what
                    # else is yet to come, comments, blocks, literals etc...).

                    # What we do here depends on whether the current lexed element is
                    # separable or not. If it is (i.e. it's whitespace), then we split
                    # and claim what we can. If it's not then we don't yield the lexed
                    # element yet, but stash a start position in the source and move
                    # on to the next file slice before returning.
                    elif element.matcher.name == "whitespace":
                        # Consume what we can from this slice and move on.
                        # Because we're currently in a templated element, the start
                        # position in the source is always the start in the template.
                        # i.e. we don't consume _partial_ elements of a templated tag
                        # in the source.
                        if stashed_source_idx is not None:
                            raise NotImplementedError(
                                "Found templated whitespace with stashed idx!"
                            )
                        lexer_logger.debug(
                            "     Consuming split whitespace from templated. "
                            "Offset: %s",
                            consumed_element_length,
                        )
                        yield element.to_segment(
                            pos_marker=PositionMarker(
                                tfs.source_slice,
                                tfs.templated_slice,
                                templated_file,
                            ),
                            # Subdivide the existing segment.
                            subslice=slice(0, _slice_length(tfs.templated_slice)),
                        )

                        consumed_element_length = _slice_length(tfs.templated_slice)
                        # Move on to the next templated slice because we just consumed
                        # the whole thing.
                        continue
                    else:
                        # Stash the source idx for later when we do make a segment.
                        lexer_logger.debug("     Spilling over templated slice.")
                        if stashed_source_idx is None:
                            stashed_source_idx = tfs.source_slice.start
                            lexer_logger.debug(
                                "     Stashing a source start as lexed element spans "
                                "over the end of a template slice. %s",
                                stashed_source_idx,
                            )
                        # Move on to the next template slice
                        continue

            raise NotImplementedError(
                f"Unable to process slice: {tfs}"
            )  # pragma: no cover

    # If templated elements are left, yield them.
    # We can assume they're all zero length if we're here.
    for tfs_idx, tfs in enumerate(templated_file_slices[tfs_idx:], tfs_idx):
        next_tfs = (
            templated_file_slices[tfs_idx + 1]
            if tfs_idx + 1 < len(templated_file_slices)
            else None
        )
        yield from _handle_zero_length_slice(
            tfs, next_tfs, block_stack, templated_file, add_indents
        )


class Lexer:
    """The Lexer class actually does the lexing step."""

    def __init__(
        self,
        config: Optional[FluffConfig] = None,
        last_resort_lexer: Optional[StringLexer] = None,
        dialect: Optional[str] = None,
    ):
        # Allow optional config and dialect
        self.config = FluffConfig.from_kwargs(config=config, dialect=dialect)
        # Store the matchers
        self.lexer_matchers = self.config.get("dialect_obj").get_lexer_matchers()

        self.last_resort_lexer = last_resort_lexer or RegexLexer(
            "<unlexable>",
            r"[^\t\n\,\.\ \-\+\*\\\/\'\"\;\:\[\]\(\)\|]*",
            UnlexableSegment,
        )

    def lex(
        self, raw: Union[str, TemplatedFile]
    ) -> Tuple[Tuple[BaseSegment, ...], List[SQLLexError]]:
        """Take a string or TemplatedFile and return segments.

        If we fail to match the *whole* string, then we must have
        found something that we cannot lex. If that happens we should
        package it up as unlexable and keep track of the exceptions.
        """
        # Make sure we've got a string buffer and a template
        # regardless of what was passed in.
        if isinstance(raw, str):
            template = TemplatedFile.from_string(raw)
            str_buff = raw
        else:
            template = raw
            str_buff = str(template)

        # Lex the string to get a tuple of LexedElement
        element_buffer: List[LexedElement] = []
        while True:
            res = self.lex_match(str_buff, self.lexer_matchers)
            element_buffer += res.elements
            if res.forward_string:
                resort_res = self.last_resort_lexer.match(res.forward_string)
                if not resort_res:
                    # If we STILL can't match, then just panic out.
                    raise SQLLexError(
                        f"Fatal. Unable to lex characters: {0!r}".format(
                            res.forward_string[:10] + "..."
                            if len(res.forward_string) > 9
                            else res.forward_string
                        )
                    )
                str_buff = resort_res.forward_string
                element_buffer += resort_res.elements
            else:  # pragma: no cover TODO?
                break

        # Map tuple LexedElement to list of TemplateElement.
        # This adds the template_slice to the object.
        templated_buffer = self.map_template_slices(element_buffer, template)

        # Turn lexed elements into segments.
        segments: Tuple[RawSegment, ...] = self.elements_to_segments(
            templated_buffer, template
        )

        # Generate any violations
        violations: List[SQLLexError] = self.violations_from_segments(segments)

        return segments, violations

    def elements_to_segments(
        self, elements: List[TemplateElement], templated_file: TemplatedFile
    ) -> Tuple[RawSegment, ...]:
        """Convert a tuple of lexed elements into a tuple of segments."""
        lexer_logger.info("Elements to Segments.")
        add_indents = self.config.get("template_blocks_indent", "indentation")
        # Delegate to _iter_segments
        segment_buffer: List[RawSegment] = list(
            _iter_segments(
                elements, templated_file.sliced_file, templated_file, add_indents
            )
        )
        lexer_logger.warning("SADFKLADJ: %s", segment_buffer)
        # Add an end of file marker
        segment_buffer.append(
            EndOfFile(
                pos_marker=segment_buffer[-1].pos_marker.end_point_marker()
                if segment_buffer
                else PositionMarker.from_point(0, 0, templated_file)
            )
        )
        # Convert to tuple before return
        return tuple(segment_buffer)

    @staticmethod
    def violations_from_segments(segments: Tuple[RawSegment, ...]) -> List[SQLLexError]:
        """Generate any lexing errors for any unlexables."""
        violations = []
        for segment in segments:
            if segment.is_type("unlexable"):
                violations.append(
                    SQLLexError(
                        "Unable to lex characters: {!r}".format(
                            segment.raw[:10] + "..."
                            if len(segment.raw) > 9
                            else segment.raw
                        ),
                        pos=segment.pos_marker,
                    )
                )
        return violations

    @staticmethod
    def lex_match(forward_string: str, lexer_matchers: List[StringLexer]) -> LexMatch:
        """Iteratively match strings using the selection of submatchers."""
        elem_buff: List[LexedElement] = []
        while True:
            if len(forward_string) == 0:
                return LexMatch(forward_string, elem_buff)
            for matcher in lexer_matchers:
                res = matcher.match(forward_string)
                if res.elements:
                    # If we have new segments then whoop!
                    elem_buff += res.elements
                    forward_string = res.forward_string
                    # Cycle back around again and start with the top
                    # matcher again.
                    break
            else:
                # We've got so far, but now can't match. Return
                return LexMatch(forward_string, elem_buff)

    @staticmethod
    def map_template_slices(
        elements: List[LexedElement], template: TemplatedFile
    ) -> List[TemplateElement]:
        """Create a tuple of TemplateElement from a tuple of LexedElement.

        This adds slices in the templated file to the original lexed
        elements. We'll need this to work out the position in the source
        file.
        """
        idx = 0
        templated_buff: List[TemplateElement] = []
        for element in elements:
            template_slice = slice(idx, idx + len(element.raw))
            idx += len(element.raw)
            templated_buff.append(TemplateElement.from_element(element, template_slice))
            if (
                template.templated_str[template_slice] != element.raw
            ):  # pragma: no cover
                raise ValueError(
                    "Template and lexed elements do not match. This should never "
                    f"happen {element.raw!r} != "
                    f"{template.templated_str[template_slice]!r}"
                )
        return templated_buff
