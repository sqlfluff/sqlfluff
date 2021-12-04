"""The code for the Lexer."""

import logging
from typing import Optional, List, Tuple, Union, NamedTuple
import regex

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
        return self.segment_class(
            raw=raw, pos_marker=pos_marker, name=self.name, **self.segment_kwargs
        )


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
            else:  # pragma: no cover
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
        # Working buffer to build up segments
        segment_buffer: List[RawSegment] = []

        lexer_logger.info("Elements to Segments.")
        # Get the templated slices to re-insert tokens for them
        source_only_slices = templated_file.source_only_slices()
        lexer_logger.info("Source-only slices: %s", source_only_slices)
        stash_source_slice, last_source_slice = None, None

        # Now work out source slices, and add in template placeholders.
        for idx, element in enumerate(elements):
            # Calculate Source Slice
            if idx != 0:
                last_source_slice = stash_source_slice
            source_slice = templated_file.templated_slice_to_source_slice(
                element.template_slice
            )
            stash_source_slice = source_slice
            # Output the slice as we lex.
            lexer_logger.debug(
                "  %s, %s, %s, %r",
                idx,
                element,
                source_slice,
                templated_file.templated_str[element.template_slice],
            )

            # The calculated source slice will include any source only slices.
            # We should consider all of them in turn to see whether we can
            # insert them.
            so_slices = []
            # Only look for source only slices if we've got a new source slice to
            # avoid unnecessary duplication.
            if last_source_slice != source_slice:
                for source_only_slice in source_only_slices:
                    # If it's later in the source, stop looking. Any later
                    # ones *also* won't match.
                    if source_only_slice.source_idx >= source_slice.stop:
                        break
                    elif source_only_slice.source_idx >= source_slice.start:
                        so_slices.append(source_only_slice)

            if so_slices:
                lexer_logger.debug("    Collected Source Only Slices")
                for so_slice in so_slices:
                    lexer_logger.debug("       %s", so_slice)

                # Calculate some things which will be useful
                templ_str = templated_file.templated_str[element.template_slice]
                source_str = templated_file.source_str[source_slice]

                # For reasons which aren't entirely clear right now, if there is
                # an included literal, it will always be at the end. Let's see if it's
                # there.
                if source_str.endswith(templ_str):
                    existing_len = len(templ_str)
                else:
                    existing_len = 0

                # Calculate slices
                placeholder_slice = slice(
                    source_slice.start, source_slice.stop - existing_len
                )
                placeholder_str = source_str[:-existing_len]
                source_slice = slice(
                    source_slice.stop - existing_len, source_slice.stop
                )
                # If it doesn't manage to extract a placeholder string from the source
                # just concatenate the source only strings. There is almost always
                # only one of them.
                if not placeholder_str:
                    placeholder_str = "".join(s.raw for s in so_slices)
                # The Jinja templater sometimes returns source-only slices with
                # gaps between. For example, in this section:
                #
                #   {% else %}
                #   JOIN
                #       {{action}}_raw_effect_sizes
                #   USING
                #       ({{ states }})
                #   {% endif %}
                #
                # we might get {% else %} and {% endif %} slices, without the
                # 4 lines between. This indicates those lines were not executed
                # In this case, generate a placeholder where the skipped code is
                # omitted but noted with a brief string, e.g.:
                #
                # "{% else %}... [103 unused template characters] ...{% endif %}".
                #
                # This is more readable -- it would be REALLY confusing for a
                # placeholder to include code that wasn't even executed!!
                if len(so_slices) >= 2:
                    has_gap = False
                    gap_placeholder_parts = []
                    last_slice = None
                    # For each slice...
                    for so_slice in so_slices:
                        # If it's not the first slice, was there a gap?
                        if last_slice:
                            end_last = last_slice.source_idx + len(last_slice.raw)
                            chars_skipped = so_slice.source_idx - end_last
                            if chars_skipped:
                                # Yes, gap between last_slice and so_slice.
                                has_gap = True

                                # Generate a string documenting the gap.
                                if chars_skipped >= 10:
                                    gap_placeholder_parts.append(
                                        f"... [{chars_skipped} unused template characters] ..."
                                    )
                                else:
                                    gap_placeholder_parts.append("...")
                        # Now add the slice's source.
                        gap_placeholder_parts.append(so_slice.raw)
                        last_slice = so_slice
                    if has_gap:
                        placeholder_str = "".join(gap_placeholder_parts)
                lexer_logger.debug(
                    "    Overlap Length: %s. PS: %s, LS: %s, p_str: %r, templ_str: %r",
                    existing_len,
                    placeholder_slice,
                    source_slice,
                    placeholder_str,
                    templ_str,
                )

                # Calculate potential indent/dedent
                block_slices = sum(s.slice_type.startswith("block_") for s in so_slices)
                block_balance = sum(
                    s.slice_type == "block_start" for s in so_slices
                ) - sum(s.slice_type == "block_end" for s in so_slices)
                lead_dedent = so_slices[0].slice_type in ("block_end", "block_mid")
                trail_indent = so_slices[-1].slice_type in ("block_start", "block_mid")
                add_indents = self.config.get("template_blocks_indent", "indentation")
                lexer_logger.debug(
                    "    Block Slices: %s. Block Balance: %s. Lead: %s, Trail: %s, Add: %s",
                    block_slices,
                    block_balance,
                    lead_dedent,
                    trail_indent,
                    add_indents,
                )

                # Add a dedent if appropriate.
                if lead_dedent and add_indents:
                    lexer_logger.debug("      DEDENT")
                    segment_buffer.append(
                        Dedent(
                            pos_marker=PositionMarker.from_point(
                                placeholder_slice.start,
                                element.template_slice.start,
                                templated_file,
                            )
                        )
                    )

                # Always add a placeholder
                segment_buffer.append(
                    TemplateSegment(
                        pos_marker=PositionMarker(
                            placeholder_slice,
                            slice(
                                element.template_slice.start,
                                element.template_slice.start,
                            ),
                            templated_file,
                        ),
                        source_str=placeholder_str,
                        block_type=so_slices[0].slice_type
                        if len(so_slices) == 1
                        else "compound",
                    )
                )
                lexer_logger.debug(
                    "      Placeholder: %s, %r", segment_buffer[-1], placeholder_str
                )

                # Add an indent if appropriate.
                if trail_indent and add_indents:
                    lexer_logger.debug("      INDENT")
                    segment_buffer.append(
                        Indent(
                            is_template=True,
                            pos_marker=PositionMarker.from_point(
                                placeholder_slice.stop,
                                element.template_slice.start,
                                templated_file,
                            ),
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
                    f"happen {element.raw!r} != {template.templated_str[template_slice]!r}"
                )
        return templated_buff
