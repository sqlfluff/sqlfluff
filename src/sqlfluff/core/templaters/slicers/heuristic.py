"""Heuristic-based template slicing algorithm.

This is the original slicing algorithm. It has limitations that may surface
when templates include similar strings multiple places in the file.
"""

import logging
import regex
from typing import Iterator, List

from jinja2 import Environment

from sqlfluff.core.templaters.base import RawFileSlice


# Instantiate the templater logger
templater_logger = logging.getLogger("sqlfluff.templater")


re_open_tag = regex.compile(r"^\s*{%[\+\-]?\s*")
re_close_tag = regex.compile(r"\s*[\+\-]?%}\s*$")


def slice_template(in_str: str, env: Environment) -> List[RawFileSlice]:
    """Slice template in jinja."""
    return list(_slice_template(in_str, env))


def _slice_template(in_str: str, env: Environment) -> Iterator[RawFileSlice]:
    """Helper function for slice template in jinja.

    NB: Starts and ends of blocks are not distinguished.
    """
    str_buff = ""
    idx = 0
    # We decide the "kind" of element we're dealing with
    # using it's _closing_ tag rather than it's opening
    # tag. The types here map back to similar types of
    # sections in the python slicer.
    block_types = {
        "variable_end": "templated",
        "block_end": "block",
        "comment_end": "comment",
        # Raw tags should behave like blocks. Note that
        # raw_end and raw_begin are whole tags rather
        # than blocks and comments where we get partial
        # tags.
        "raw_end": "block",
        "raw_begin": "block",
    }

    # https://jinja.palletsprojects.com/en/2.11.x/api/#jinja2.Environment.lex
    for _, elem_type, raw in env.lex(in_str):
        if elem_type == "data":
            yield RawFileSlice(raw, "literal", idx)
            idx += len(raw)
        else:  # pragma: no cover
            str_buff += raw

            if elem_type.endswith("_begin"):
                # When a "begin" tag (whether block, comment, or data) uses
                # whitespace stripping
                # (https://jinja.palletsprojects.com/en/3.0.x/templates/#whitespace-control),
                # the Jinja lex() function handles this by discarding adjacent
                # whitespace from in_str. For more insight, see the tokeniter()
                # function in this file:
                # https://github.com/pallets/jinja/blob/main/src/jinja2/lexer.py
                # We want to detect and correct for this in order to:
                # - Correctly update "idx" (if this is wrong, that's a
                #   potential DISASTER because lint fixes use this info to
                #   update the source file, and incorrect values often result in
                #   CORRUPTING the user's file so it's no longer valid SQL. :-O
                # - Guarantee that the slices we return fully "cover" the
                #   contents of in_str.
                #
                # We detect skipped characters by looking ahead in in_str for
                # the token just returned from lex(). The token text will either
                # be at the current 'idx' position (if whitespace stripping did
                # not occur) OR it'll be farther along in in_str, but we're
                # GUARANTEED that lex() only skips over WHITESPACE; nothing else.

                # Find the token returned. Did lex() skip over any characters?
                num_chars_skipped = in_str.index(raw, idx) - idx
                if num_chars_skipped:
                    # Yes. It skipped over some characters. Compute a string
                    # containing the skipped characters.
                    skipped_str = in_str[idx : idx + num_chars_skipped]

                    # Sanity check: Verify that Jinja only skips over
                    # WHITESPACE, never anything else.
                    if not skipped_str.isspace():  # pragma: no cover
                        templater_logger.warning(
                            "Jinja lex() skipped non-whitespace: %s", skipped_str
                        )
                    # Treat the skipped whitespace as a literal.
                    yield RawFileSlice(skipped_str, "literal", idx)
                    idx += num_chars_skipped

            # raw_end and raw_begin behave a little differently in
            # that the whole tag shows up in one go rather than getting
            # parts of the tag at a time.
            if elem_type.endswith("_end") or elem_type == "raw_begin":
                block_type = block_types[elem_type]
                block_subtype = None
                # Handle starts and ends of blocks
                if block_type == "block":
                    # Trim off the brackets and then the whitespace
                    m_open = re_open_tag.search(str_buff)
                    m_close = re_close_tag.search(str_buff)
                    trimmed_content = ""
                    if m_open and m_close:
                        trimmed_content = str_buff[
                            len(m_open.group(0)) : -len(m_close.group(0))
                        ]
                    if trimmed_content.startswith("end"):
                        block_type = "block_end"
                    elif trimmed_content.startswith("el"):
                        # else, elif
                        block_type = "block_mid"  # pragma: no cover
                    else:
                        block_type = "block_start"
                        if trimmed_content.split()[0] == "for":
                            block_subtype = "loop"  # pragma: no cover
                m = regex.search(r"\s+$", raw, regex.MULTILINE | regex.DOTALL)
                if raw.startswith("-") and m:
                    # Right whitespace was stripped. Split off the trailing
                    # whitespace into a separate slice. The desired behavior is
                    # to behave similarly as the left stripping case above.
                    # Note that the stakes are a bit different, because lex()
                    # hasn't *omitted* any characters from the strings it
                    # returns, it has simply grouped them differently than we
                    # want.
                    trailing_chars = len(m.group(0))
                    yield RawFileSlice(
                        str_buff[:-trailing_chars], block_type, idx, block_subtype
                    )
                    idx += len(str_buff) - trailing_chars
                    yield RawFileSlice(str_buff[-trailing_chars:], "literal", idx)
                    idx += trailing_chars
                else:
                    yield RawFileSlice(str_buff, block_type, idx, block_subtype)
                    idx += len(str_buff)
                str_buff = ""
