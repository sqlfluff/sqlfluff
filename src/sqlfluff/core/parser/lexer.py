"""The code for the Lexer."""

import logging
from typing import Optional, List, Tuple, Union
from dataclasses import dataclass
import re

from sqlfluff.core.parser.markers import FilePositionMarker, EnrichedFilePositionMarker
from sqlfluff.core.parser.segments import (
    BaseSegment,
    RawSegment,
    Indent,
    Dedent,
    TemplateSegment,
)
from sqlfluff.core.errors import SQLLexError
from sqlfluff.core.templaters import TemplatedFile
from sqlfluff.core.config import FluffConfig

# Instantiate the lexer logger
lexer_logger = logging.getLogger("sqlfluff.lexer")


@dataclass
class LexedElement:
    raw: str
    matcher: "StringMatcher"

    def to_segment(self, pos_marker):
        """Create a segment from this lexed element."""
        # TODO: Review whether this is sensible later in refactor.
        SegmentClass = self.matcher._make_segment_class()
        return SegmentClass(self.raw, pos_marker)


@dataclass
class LexMatch:
    forward_string: str
    elements: Tuple[LexedElement, ...]
    """A class to hold matches from the Lexer."""

    def __bool__(self):
        """A LexMatch is truthy if it contains a non-zero number of matched segments."""
        return len(self.elements) > 0


class StringMatcher:
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
        subdivider=None,
        trim_post_subdivide=None,
        segment_kwargs=None,
    ):
        self.name = name
        self.template = template
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
        if self.template in forward_string:
            loc = forward_string.find(self.template)
            return loc, loc + len(self.template)
        else:
            return None

    def _trim_match(self, matched_str: str) -> Tuple[LexedElement, ...]:
        """Given a string, trim if we are allowed to.

        Returns:
            :obj:`tuple` of LexedElement

        """

        elem_buff: Tuple[LexedElement, ...] = ()
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
                    elem_buff += (LexedElement(
                        str_buff[:trim_pos[1]],
                        self.trim_post_subdivide,
                    ),)
                    str_buff = str_buff[trim_pos[1]:]
                # End Match?
                elif trim_pos[1] == len(str_buff):
                    elem_buff += (
                        LexedElement(
                            content_buff + str_buff[:trim_pos[0]],
                            self,
                        ),
                        LexedElement(
                            str_buff[trim_pos[0]:trim_pos[1]],
                            self.trim_post_subdivide,
                        )
                    )
                    content_buff, str_buff = "", ""
                # Mid Match? (carry on)
                else:
                    content_buff += str_buff[:trim_pos[1]]
                    str_buff = str_buff[trim_pos[1]:]

        # Do we have anything left? (or did nothing happen)
        if content_buff + str_buff:
            elem_buff += (
                LexedElement(content_buff + str_buff, self),
            )
        return elem_buff

    def _subdivide(self, matched: LexedElement) -> Tuple[LexedElement, ...]:
        """Given a string, subdivide if we area allowed to.

        Returns:
            :obj:`tuple` of segments

        """
        # Can we have to subdivide?
        if self.subdivider:
            # Yes subdivision
            elem_buff: Tuple[LexedElement, ...] = ()
            str_buff = matched.raw
            while str_buff:
                # Iterate through subdividing as appropriate
                div_pos = self.subdivider.search(str_buff)
                if div_pos:
                    # Found a division
                    trimmed_elems = self._trim_match(str_buff[: div_pos[0]])
                    div_elem = LexedElement(
                        str_buff[div_pos[0]: div_pos[1]],
                        self.subdivider
                    )
                    elem_buff += trimmed_elems + (div_elem,)
                    str_buff = str_buff[div_pos[1] :]
                else:
                    # No more division matches. Trim?
                    trimmed_elems = self._trim_match(str_buff)
                    elem_buff += trimmed_elems
                    break
            return elem_buff
        else:
            # NB: Tuple literal
            return (matched,)

    def match(self, forward_string: str) -> LexMatch:
        """Given a string, match what we can and return the rest.

        Returns:
            :obj:`LexMatch`

        """
        if len(forward_string) == 0:
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
            return LexMatch(forward_string, ())

    def _make_segment_class(self):
        # NOTE: Stub method to override later.
        # THIS NEEDS REFACTORING WITH FACTORIES
        return RawSegment.make(self.template, name=self.name, **self.segment_kwargs)


class RegexMatcher(StringMatcher):
    """This RegexMatcher matches based on regular expressions."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # We might want to configure this at some point, but for now, newlines
        # do get matched by .
        flags = re.DOTALL
        self._compiled_regex = re.compile(self.template, flags)

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
                    f"Zero length Lex item returned from {self.name!r}. Report this as a bug."
                )
        return None

    def search(self, forward_string: str) -> Optional[Tuple[int, int]]:
        """Use regex to find a substring."""
        match = self._compiled_regex.search(forward_string)
        if match:
            # We can only match strings with length
            if match.group(0):
                return match.span()
            else:
                lexer_logger.warning(
                    f"Zero length Lex item returned from {self.name!r}. Report this as a bug."
                )
        return None


class Lexer:
    """The Lexer class actually does the lexing step."""

    def __init__(
        self,
        config: Optional[FluffConfig] = None,
        last_resort_lexer: Optional[StringMatcher] = None,
        dialect: Optional[str] = None,
    ):
        # Allow optional config and dialect
        self.config = FluffConfig.from_kwargs(config=config, dialect=dialect)
        # Store the matchers
        self.lexer_matchers = self.config.get("dialect_obj").get_lexer_struct()

        self.last_resort_lexer = last_resort_lexer or RegexMatcher(
            "<unlexable>",
            r"[^\t\n\,\.\ \-\+\*\\\/\'\"\;\:\[\]\(\)\|]*",
            segment_kwargs={"is_code": True}
        )

    def lex(
        self, raw: Union[str, TemplatedFile]
    ) -> Tuple[Tuple[BaseSegment, ...], List[SQLLexError]]:
        """Take a string or TemplatedFile and return segments.

        If we fail to match the *whole* string, then we must have
        found something that we cannot lex. If that happens we should
        package it up as unlexable and keep track of the exceptions.
        """

        element_buffer: Tuple[LexedElement, ...] = ()

        # Handle potential TemplatedFile for now
        str_buff = str(raw)

        while True:
            res = self.lex_match(str_buff, self.lexer_matchers)
            element_buffer += res.elements
            if res.forward_string:
                resort_res = self.last_resort_lexer.match(res.forward_string)
                if not resort_res:
                    # If we STILL can't match, then just panic out.
                    raise SQLLexError(
                        f"Fatal. Unable to lex characters: {0!r}".format(
                            res.forward_string[:10] + "..." if len(res.forward_string) > 9 else res.forward_string
                        )
                    )

                str_buff = resort_res.forward_string
                element_buffer += resort_res.elements
            else:
                break

        # Turn lexed elements into segments.
        return self.elements_to_segments(element_buffer, raw)

    def elements_to_segments(self, elements: Tuple[LexedElement, ...], raw: Union[str, TemplatedFile]) -> Tuple[Tuple[BaseSegment, ...], List[SQLLexError]]:
        """Convert a tuple of lexed elements into a tuple of segments."""
        # TODO: Refactor so we never create unenriched position markers.
        # TODO: Convert raw -> template, generate template if we don't have one, so it's always here.
        pos_marker = FilePositionMarker()
        segment_buff: Tuple[RawSegment, ...] = ()
        violations = []

        # Create basic position markers
        for element in elements:
            segment_buff += (element.to_segment(pos_marker),)
            # Generate a Lexing error if we hit the last resort
            if element.matcher is self.last_resort_lexer:
                violations.append(
                    SQLLexError(
                        "Unable to lex characters: {0!r}".format(
                            element.raw[:10] + "..." if len(element.raw) > 9 else element.raw
                        ),
                        pos=pos_marker,
                    )
                )
            # Update pos marker
            pos_marker = pos_marker.advance_by(element.raw)

        # Enrich the segments if we can using the templated file
        if isinstance(raw, TemplatedFile):
            return self.enrich_segments(segment_buff, raw), violations
        else:
            return segment_buff, violations

    @staticmethod
    def lex_match(forward_string, lexer_matchers):
        """Iteratively match strings using the selection of submatchers."""
        elem_buff = ()
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
                    continue
            else:
                # We've got so far, but now can't match. Return
                return LexMatch(forward_string, elem_buff)

    @staticmethod
    def enrich_segments(
        segment_buff: Tuple[BaseSegment, ...], templated_file: TemplatedFile
    ) -> Tuple[BaseSegment, ...]:
        """Enrich the segments using the templated file.

        We use the mapping in the template to provide positions
        in the source file.
        """
        # Make a new buffer to hold the enriched segments.
        # We need a new buffer to hold the new meta segments
        # introduced.
        new_segment_buff = []
        # Get the templated slices to re-insert tokens for them
        source_only_slices = templated_file.source_only_slices()

        lexer_logger.info(
            "Enriching Segments. Source-only slices: %s", source_only_slices
        )

        for segment in segment_buff:
            templated_slice = slice(
                segment.pos_marker.char_pos,
                segment.pos_marker.char_pos + len(segment.raw),
            )
            source_slice = templated_file.templated_slice_to_source_slice(
                templated_slice
            )

            # At this stage, templated slices will be INCLUDED in the source slice,
            # so we should consider whether we've captured any. If we have then
            # we need to re-evaluate whether it's a literal or not.

            for source_only_slice in source_only_slices:
                if source_only_slice.source_idx > source_slice.start:
                    break
                elif source_only_slice.source_idx == source_slice.start:
                    lexer_logger.debug(
                        "Found templated section! %s, %s, %s",
                        source_only_slice.source_slice(),
                        source_only_slice.slice_type,
                        templated_slice.start,
                    )
                    # Adjust the source slice accordingly.
                    source_slice = slice(
                        source_only_slice.end_source_idx(), source_slice.stop
                    )

                    # Add segments as appropriate.
                    # If it's a block end, add a dedent.
                    if source_only_slice.slice_type in ("block_end", "block_mid"):
                        new_segment_buff.append(
                            Dedent.when(template_blocks_indent=True)(
                                pos_marker=segment.pos_marker
                            )
                        )
                    # Always add a placeholder
                    new_segment_buff.append(
                        TemplateSegment(
                            pos_marker=segment.pos_marker,
                            source_str=source_only_slice.raw,
                            block_type=source_only_slice.slice_type,
                        )
                    )
                    # If it's a block end, add a dedent.
                    if source_only_slice.slice_type in ("block_start", "block_mid"):
                        new_segment_buff.append(
                            Indent.when(template_blocks_indent=True)(
                                pos_marker=segment.pos_marker
                            )
                        )

            source_line, source_pos = templated_file.get_line_pos_of_char_pos(
                source_slice.start
            )

            # Recalculate is_literal
            is_literal = templated_file.is_source_slice_literal(source_slice)

            segment.pos_marker = EnrichedFilePositionMarker(
                statement_index=segment.pos_marker.statement_index,
                line_no=segment.pos_marker.line_no,
                line_pos=segment.pos_marker.line_pos,
                char_pos=segment.pos_marker.char_pos,
                templated_slice=templated_slice,
                source_slice=source_slice,
                is_literal=is_literal,
                source_pos_marker=FilePositionMarker(
                    segment.pos_marker.statement_index,
                    source_line,
                    source_pos,
                    source_slice.start,
                ),
            )
            new_segment_buff.append(segment)

        # Finally, we pass through a final time, enriching any remaining
        # un-enriched segments using the position of their preceeding marker.
        for idx in range(len(new_segment_buff)):
            if not isinstance(
                new_segment_buff[idx].pos_marker, EnrichedFilePositionMarker
            ):
                # get previous marker
                if idx > 0:
                    prev_marker = new_segment_buff[idx - 1].pos_marker
                    prev_pos = (
                        prev_marker.source_slice.stop,
                        prev_marker.templated_slice.stop,
                    )
                    prev_line = prev_marker.source_pos_marker.line_no
                    prev_line_pos = prev_marker.source_pos_marker.line_pos
                else:
                    prev_pos = (0, 0)
                    prev_line = 0
                    prev_line_pos = 0
                # Is it a placeholder (i.e. does it have source length?)
                if isinstance(new_segment_buff[idx], TemplateSegment):
                    # Find the next enriched marker.
                    for elem in new_segment_buff[idx + 1 :]:
                        if isinstance(elem.pos_marker, EnrichedFilePositionMarker):
                            next_pos = (
                                elem.pos_marker.source_slice.start,
                                elem.pos_marker.templated_slice.start,
                            )
                            break
                    else:
                        # We're at the end of the file.
                        next_pos = (
                            len(templated_file.source_str),
                            len(templated_file.templated_str),
                        )
                else:
                    # It's a point and so we don't need to find the next one.
                    next_pos = prev_pos
                # Enrich by proxy
                new_segment_buff[idx].pos_marker = EnrichedFilePositionMarker(
                    statement_index=new_segment_buff[idx].pos_marker.statement_index,
                    line_no=new_segment_buff[idx].pos_marker.line_no,
                    line_pos=new_segment_buff[idx].pos_marker.line_pos,
                    char_pos=new_segment_buff[idx].pos_marker.char_pos,
                    templated_slice=slice(prev_pos[1], next_pos[1]),
                    source_slice=slice(prev_pos[0], next_pos[0]),
                    is_literal=False,
                    source_pos_marker=FilePositionMarker(
                        new_segment_buff[idx].pos_marker.statement_index,
                        prev_line,
                        prev_line_pos,
                        prev_pos[0],
                    ),
                )

        lexer_logger.debug("Enriched Segments:")
        for seg in new_segment_buff:
            lexer_logger.debug(
                "\tTmp: %s\tSrc: %s\tSeg: %s",
                getattr(seg.pos_marker, "templated_slice", None),
                getattr(seg.pos_marker, "source_slice", None),
                seg,
            )

        return tuple(new_segment_buff)
