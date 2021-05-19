"""The code for the Lexer."""

import logging
from typing import Optional, List, Tuple, Union, NamedTuple
import re

from sqlfluff.core.parser.segments import (
    BaseSegment,
    RawSegment,
    Indent,
    Dedent,
    TemplateSegment,
    UnlexableSegment,
)
from sqlfluff.core.parser.markers import PositionMarker
from sqlfluff.core.errors import SQLLexError
from sqlfluff.core.templaters import TemplatedFile
from sqlfluff.core.config import FluffConfig

# Instantiate the lexer logger
lexer_logger = logging.getLogger("sqlfluff.lexer")


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

    def to_segment(self, pos_marker):
        """Create a segment from this lexed element."""
        return self.matcher.construct_segment(self.raw, pos_marker=pos_marker)


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
            return LexMatch(forward_string, [])

    def construct_segment(self, raw, pos_marker):
        """Construct a segment using the given class a properties."""
        return self.segment_class(
            raw=raw, pos_marker=pos_marker, name=self.name, **self.segment_kwargs
        )


class RegexLexer(StringLexer):
    """This RegexLexer matches based on regular expressions."""

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
            else:
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
        # Working buffer to build up segments
        segment_buffer: List[RawSegment] = []

        lexer_logger.info("Elements to Segments.")
        # Get the templated slices to re-insert tokens for them
        source_only_slices = templated_file.source_only_slices()
        lexer_logger.info("Source-only slices: %s", source_only_slices)

        # Now work out source slices, and add in template placeholders.
        for element in elements:
            # Calculate Source Slice
            source_slice = templated_file.templated_slice_to_source_slice(
                element.template_slice
            )
            # The calculated source slice will include any source only slices.
            # We should consider all of them in turn to see whether we can
            # insert them.
            for source_only_slice in source_only_slices:
                # If it's later in the source, stop looking. Any later
                # ones *also* won't match.
                if source_only_slice.source_idx > source_slice.start:
                    break
                # Is there a templated section within this source slice?
                # If there is then for some reason I can't quite explain,
                # it will always be at the start of the section. This is
                # very convenient beause it means we'll always have the
                # start and end of it in a definite position. This makes
                # slicing and looping much easier.
                elif source_only_slice.source_idx == source_slice.start:
                    lexer_logger.debug(
                        "Found templated section! %s, %s, %s",
                        source_only_slice.source_slice(),
                        source_only_slice.slice_type,
                        element.template_slice.start,
                    )
                    # Calculate a slice for any placeholders
                    placeholder_source_slice = slice(
                        source_slice.start, source_only_slice.end_source_idx()
                    )
                    # Adjust the source slice accordingly.
                    source_slice = slice(
                        source_only_slice.end_source_idx(), source_slice.stop
                    )

                    # TODO: Readjust this to remove .when once ProtoSegment is in.

                    # Add segments as appropriate.
                    # If it's a block end, add a dedent.
                    # Check config to see whether we should be addind indents.
                    if self.config.get(
                        "template_blocks_indent", "indentation"
                    ) and source_only_slice.slice_type in ("block_end", "block_mid"):
                        segment_buffer.append(
                            Dedent(
                                pos_marker=PositionMarker.from_point(
                                    placeholder_source_slice.start,
                                    element.template_slice.start,
                                    templated_file,
                                )
                            )
                        )
                    # Always add a placeholder
                    segment_buffer.append(
                        TemplateSegment(
                            pos_marker=PositionMarker(
                                placeholder_source_slice,
                                slice(
                                    element.template_slice.start,
                                    element.template_slice.start,
                                ),
                                templated_file,
                            ),
                            source_str=source_only_slice.raw,
                            block_type=source_only_slice.slice_type,
                        )
                    )
                    # If it's a block end, add a dedent.
                    if self.config.get(
                        "template_blocks_indent", "indentation"
                    ) and source_only_slice.slice_type in ("block_start", "block_mid"):
                        segment_buffer.append(
                            Indent(
                                pos_marker=PositionMarker.from_point(
                                    placeholder_source_slice.stop,
                                    element.template_slice.start,
                                    templated_file,
                                )
                            )
                        )

            # Add the actual segment
            segment_buffer.append(
                element.to_segment(
                    pos_marker=PositionMarker(
                        source_slice,
                        element.template_slice,
                        templated_file,
                    ),
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
                        "Unable to lex characters: {0!r}".format(
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
            if template.templated_str[template_slice] != element.raw:
                raise ValueError(
                    "Template and lexed elements do not match. This should never "
                    f"happen {element.raw!r} != {template.templated_str[template_slice]!r}"
                )
        return templated_buff
