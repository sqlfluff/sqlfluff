""" Code for parsing files """


import logging

from .tokens import Token, TokenMemory
from .markers import FilePositionMarker
from .errors import SQLParseError
from .segments_base import BaseSegment
from .segments_core import (CodeSegment, StatementSegment, StatementSeperatorSegment,
                            CommentSegment, QuotedSegment)


class FileSegment(BaseSegment):
    """ This is a bit of a special segment in that it does the initial splitting
    and probably defines structure a little further down than it should. """
    type = 'file'

    @classmethod
    def from_raw(cls, raw):
        """ Take Raw Text and Make a FileSegment """
        # Parsing files involves seperating comment segments and code segments and statements segments

        # Comments override everything unless we're in a string literal
        string_tokens = [
            Token('\'', '\''),
            Token('"', '"'),
            Token('`', '`')
        ]

        comment_tokens = [
            Token('/*', '*/'),
            Token('-- ', '\n'),
            Token('#', '\n')
        ]

        statement_seperators = [';']

        statement_stack = []
        segment_stack = []
        comment_entry = None
        string_entry = None
        skip = 0
        # This is the only time that we initialise the file position marker
        this_pos = FilePositionMarker.from_fresh()
        last_char = None
        last_seg_pos = this_pos  # The starting position of the "current" segment
        last_stmt_pos = this_pos  # The starting position of the "current" statement
        stmt_idx_buff = 0
        for c in raw:
            # Advance using the last character
            if last_char:
                this_pos = this_pos.advance_by(last_char, idx=stmt_idx_buff)
                stmt_idx_buff = 0
            # Save the last char
            last_char = c

            # Skip if we're in skip mode (we get a skip of 1 automatically, so only above one matters)
            if skip > 1:
                skip -= 1
                continue

            # Get a forward looking view for comparison
            forward = raw[this_pos.char_pos:]

            # What state are we in?
            if not comment_entry and not string_entry:
                for s in string_tokens:
                    if forward.startswith(s.start):
                        logging.debug("Found string start at pos {0}! [{1!r}]".format(this_pos, forward[:5]))
                        string_entry = TokenMemory(this_pos, s)
                        # check that we have a segment to add
                        if this_pos > last_seg_pos:
                            segment_stack.append(
                                CodeSegment(
                                    raw=raw[last_seg_pos.char_pos:this_pos.char_pos],
                                    pos_marker=last_seg_pos
                                )
                            )
                            last_seg_pos = this_pos
                        continue
                for c in comment_tokens:
                    if forward.startswith(c.start):
                        logging.debug("Found comment start at pos {0}! [{1!r}]".format(this_pos, forward[:5]))
                        comment_entry = TokenMemory(this_pos, c)
                        # check that we have a segment to add
                        if this_pos > last_seg_pos:
                            segment_stack.append(
                                CodeSegment(
                                    raw=raw[last_seg_pos.char_pos:this_pos.char_pos],
                                    pos_marker=last_seg_pos
                                )
                            )
                            last_seg_pos = this_pos
                        continue
                for e in statement_seperators:
                    if forward.startswith(e):
                        # Ok we've found a statement ender, not in a comment or a string
                        logging.debug("Found statement end at pos {0}! [{1!r}]".format(this_pos, forward[:5]))
                        # We need to end the current code segment FIRST
                        segment_stack.append(
                            CodeSegment(
                                raw=raw[last_seg_pos.char_pos:this_pos.char_pos],
                                pos_marker=last_seg_pos
                            )
                        )
                        last_seg_pos = this_pos
                        statement_stack.append(
                            StatementSegment(
                                segments=segment_stack,
                                pos_marker=last_stmt_pos))
                        statement_stack.append(
                            StatementSeperatorSegment(
                                raw=e, pos_marker=this_pos)
                        )
                        segment_stack = []
                        stmt_idx_buff = 1
                        last_stmt_pos = this_pos.advance_by(e, idx=stmt_idx_buff)
                        last_seg_pos = this_pos.advance_by(e, idx=stmt_idx_buff)
                        skip = len(e)
                        continue
                # logging.debug(raw[pos:])
            elif string_entry:
                # We're in a string, just look for the end, of THIS KIND of string
                if string_entry.token.end and forward.startswith(string_entry.token.end):
                    logging.debug("Found string end at pos {0}! [{1!r}]".format(this_pos, forward[:5]))
                    # End of segment
                    skip = len(string_entry.token.end)
                    segment_stack.append(
                        QuotedSegment(
                            raw[last_seg_pos.char_pos:this_pos.char_pos + skip],
                            pos_marker=last_seg_pos
                        )
                    )
                    last_seg_pos = this_pos.advance_by(string_entry.token.end)
                    string_entry = None
                    continue
            elif comment_entry:
                # We're in a string, just look for the end, of THIS KIND of string
                if comment_entry.token.end and forward.startswith(comment_entry.token.end):
                    logging.debug("Found comment end at pos {0}! [{1!r}]".format(this_pos, forward[:5]))
                    # End of segment
                    skip = len(comment_entry.token.end)
                    segment_stack.append(
                        CommentSegment(
                            raw[last_seg_pos.char_pos:this_pos.char_pos + skip],
                            pos_marker=last_seg_pos
                        )
                    )
                    last_seg_pos = this_pos.advance_by(comment_entry.token.end)
                    comment_entry = None
                    continue
            else:
                raise NotImplementedError("Aaargh!")
        # ok we got to the end, what did we finish in?
        if not comment_entry and not string_entry:
            # We ended on a code block. OK
            if this_pos.char_pos > last_seg_pos.char_pos:
                segment_stack.append(
                    CodeSegment(
                        raw[last_seg_pos.char_pos:this_pos.char_pos],
                        pos_marker=last_seg_pos
                    )
                )
        elif comment_entry:
            # We ended on a comment block
            # Should it have an ending?
            if comment_entry.token.end:
                raise SQLParseError("Final comment not terminated (Expected {0!r})".format(comment_entry.token.end))
            else:
                segment_stack.append(
                    CommentSegment(
                        raw[last_seg_pos.char_pos:this_pos.char_pos],
                        pos_marker=last_seg_pos
                    )
                )
        elif string_entry:
            if string_entry.token.end:
                raise SQLParseError("Final string not terminated (Expected {0!r})".format(string_entry.token.end))
            else:
                raise ValueError("Huh? safiihew")
        else:
            raise ValueError("Huh? eaiuyawren")

        if len(segment_stack) > 0:
            # Let's just terminate this as a statement
            statement_stack.append(
                StatementSegment(
                    segments=segment_stack,
                    pos_marker=last_stmt_pos))
        # We haven't expanded yet, just the base parsing...
        # We should call parse for that.
        return cls(segments=statement_stack)
