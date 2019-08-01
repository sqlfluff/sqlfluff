
import logging


from .markers import FilePositionMarker
from .tokens import Token, TokenMemory
from .errors import SQLParseError
from .base_segments import BaseSegment, RawSegment

# NOTE: There is a concept here, of parallel grammars.
# We use one (slightly more permissive) grammar to MATCH
# and then a more detailed one to PARSE. One is called first,
# then the other - which allows sections of the file to be
# parsed even when others won't.

# Multi stage parser

# First strip comments, potentially extracting special comments (which start with sqlfluff:)
#   - this also makes comment sections, config sections (a subset of comments) and code sections


class FileSegment(BaseSegment):
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
                            StatementSperatorSegment(
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


class StatementSperatorSegment(RawSegment):
    type = 'statement_seperator'


class BaseGrammar(object):
    """ Grammars are a way of composing match statements, any grammar
    must implment the `match` function. Segments can also be passed to
    most grammars. Segments implement `match` as a classmethod. Grammars
    implement it as an instance method """

    def match(self, segments):
        """
            Matching can be done from either the raw or the segments.
            This raw function can be overridden, or a grammar defined
            on the underlying class.
        """
        logging.debug("MATCH: {0}".format(self))
        raise NotImplementedError("{0} has no match function implemented".format(self.__class__.__name__))


class OneOf(BaseGrammar):
    """ Match any of the elements given once, if it matches
    multiple, it returns the first """
    def __init__(self, *args, **kwargs):
        self._options = args

    def match(self, segments):
        logging.debug("MATCH: {0}".format(self))
        # Match on each of the options
        matches = [opt.match(segments) for opt in self._options]

        if sum([1 if m is not None else 0 for m in matches]) > 1:
            logging.warning("WARNING! Ambiguous match!")

        for m in matches:
            if m:
                logging.debug("MATCH: {0}: Returning: {1}".format(self, m))
                return m
        else:
            return None


class GreedyUntil(BaseGrammar):
    """ Match anything, up to but not including the given options """
    def __init__(self, *args, **kwargs):
        self._options = args
        # `strict`, means the segment will not be matched WITHOUT
        # the ending clause. Normally, if we run out of segments,
        # then this will still match
        self.strict = kwargs.get('strict', False)

    def match(self, segments):
        logging.debug("MATCH: {0}".format(self))
        seg_buffer = []
        for seg in segments:
            for opt in self._options:
                if opt.match(seg):
                    # it's a match! Return everything up to this point
                    if seg_buffer:
                        return seg
                    else:
                        # if the buffer is empty, then no match
                        return None
                else:
                    continue
            else:
                # Add this to the buffer
                seg_buffer.append(seg)
        else:
            # We've gone through all the segments, and not found the end
            if self.strict:
                # Strict mode means this is NOT at match because we didn't find the end
                return None
            else:
                return seg_buffer


class Sequence(BaseGrammar):
    """ Match a specific sequence of elements """
    def __init__(self, *args, **kwargs):
        self._elems = args

    def match(self, segments):
        logging.debug("MATCH: {0}".format(self))
        # we should assume that segments aren't mutated in a grammar
        # so that the number we get back from a match is the same as
        # the number we should skip.
        if isinstance(segments, BaseSegment):
            segments = [segments]
        seg_idx = 0
        for elem in self._elems:
            logging.debug(elem)
            logging.debug("Sequence Matching at index: {0}".format(seg_idx))
            # sequentially try longer segments to see if it works
            seg_len = 1
            while True:
                if seg_idx + seg_len > len(segments):
                    # We failed to match an element, fail out.
                    logging.debug("FAIL")
                    return None
                m = elem.match(segments[seg_idx:seg_idx + seg_len])
                logging.debug(m)
                if m:
                    # deal with the matches
                    # advance the counter
                    if isinstance(m, BaseSegment):
                        seg_idx = 1
                    else:
                        seg_idx += len(m)
                    logging.debug(seg_idx)
                    break
                seg_len += 1
        else:
            # If the segments get mutated we might need to do something different here
            return segments


class ContainsOnly(BaseGrammar):
    """ match a sequence of segments which are only of the types,
    or only match the grammars in the list """
    def __init__(self, *args, **kwargs):
        self._options = args

    def match(self, segments):
        logging.debug("MATCH: {0}".format(self))
        for seg in segments:
            matched = False
            for opt in self._options:
                if isinstance(opt, str) and seg.type == opt:
                    matched = True
                    break
                elif isinstance(opt, (BaseGrammar, BaseSegment)) and opt.match([seg]):
                    matched = True
                    break
            if not matched:
                logging.debug("Non Matching Segment! {0!r}".format(seg))
                # found a non matching segment:
                return None
        else:
            # Should we also be returning a raw here?
            return segments


class StartsWith(BaseGrammar):
    """ Match if the first element is the same, with configurable
    whitespace and comment handling """
    def __init__(self, target, code_only=True, **kwargs):
        self.target = target
        self.code_only = code_only
        # Implement config handling later...

    def match(self, segments):
        logging.debug("MATCH: {0}".format(self))
        if self.code_only:
            first_code = None
            first_code_idx = None
            for idx, seg in enumerate(segments):
                if seg.type == 'strippedcode':
                    first_code_idx = idx
                    first_code = seg
                    break
            else:
                return None

            match = self.target.match(segments=[first_code])
            if match:
                # Let's actually make it a keyword segment
                segments[first_code_idx] = match
                return segments
            else:
                return None
        else:
            raise NotImplementedError("Not expecting to match StartsWith and also not just code!?")


class Keyword(BaseGrammar):
    """ Match a keyword, optionally case sensitive """
    def __init__(self, word, case_sensitive=False, **kwargs):
        # NB We store the word as upper case unless case sensitive
        # For this one we won't accept whitespace or comments
        self.case_sensitive = case_sensitive
        if self.case_sensitive:
            self.word = word
        else:
            self.word = word.upper()

    def match(self, segments):
        logging.debug("MATCH: {0}".format(self))
        # We can only match segments of length 1
        if isinstance(segments, BaseSegment):
            segments = [segments]
        logging.debug(len(segments))
        if len(segments) == 1:
            raw = segments[0].raw
            pos = segments[0].pos_marker
            logging.debug(raw)
            if ((self.case_sensitive and self.word == raw) or (not self.case_sensitive and self.word == raw.upper())):
                return KeywordSegment(raw=raw, pos_marker=pos)
        return None

# Note on SQL Grammar
# https://www.cockroachlabs.com/docs/stable/sql-grammar.html#select_stmt


class KeywordSegment(RawSegment):
    type = 'keyword'


class SelectTargetGroupStatementSegment(BaseSegment):
    type = 'select_target_group'
    # From here down, comments are printed seperately.
    comment_seperate = True
    # match grammar - doesn't exist - don't match, only parse
    grammar = None
    parse_grammar = Sequence(GreedyUntil(Keyword('from')))


class SelectStatementSegment(BaseSegment):
    type = 'select_statement'
    # From here down, comments are printed seperately.
    comment_seperate = True
    # match grammar
    grammar = StartsWith(Keyword('select'))
    parse_grammar = Sequence(Keyword('select'), SelectTargetGroupStatementSegment, GreedyUntil(Keyword('limit')))


class InsertStatementSegment(BaseSegment):
    type = 'insert_statement'
    # From here down, comments are printed seperately.
    comment_seperate = True
    grammar = StartsWith(Keyword('insert'))


class EmptyStatementSegment(BaseSegment):
    type = 'empty_statement'
    # From here down, comments are printed seperately.
    comment_seperate = True
    grammar = ContainsOnly('comment', 'newline')
    # TODO: At some point - we should lint that these are only
    # allowed at the END - otherwise it's probably a parsing error


class StatementSegment(BaseSegment):
    type = 'statement'
    # From here down, comments are printed seperately.
    comment_seperate = True
    # Let's define a grammar from here on in
    grammar = OneOf(SelectStatementSegment, InsertStatementSegment, EmptyStatementSegment)


class CodeSegment(RawSegment):
    type = 'code'

    def parse(self):
        # Split into whitespace, newline and StrippedCode
        whitespace_chars = [' ', '\t']
        newline_chars = ['\n']
        this_pos = self.pos_marker
        segment_stack = []
        started = None
        last_char = None
        for idx, c in enumerate(self.raw):
            if last_char:
                this_pos = this_pos.advance_by(last_char)
            # Save the last char
            last_char = c
            if c in newline_chars:
                if started:
                    if started[0] == 'whitespace':
                        segment_stack.append(
                            WhitespaceSegment(
                                self.raw[started[2]:idx],
                                pos_marker=started[1])
                        )
                        started = None
                    elif started[0] == 'code':
                        segment_stack.append(
                            StrippedCodeSegment(
                                self.raw[started[2]:idx],
                                pos_marker=started[1])
                        )
                        started = None
                    else:
                        raise ValueError("Unexpected `started` value?!")
                segment_stack.append(
                    NewlineSegment(c, pos_marker=this_pos)
                )
            elif c in whitespace_chars:
                if started:
                    if started[0] == 'whitespace':
                        # We don't want to reset the whitespace counter!
                        continue
                    elif started[0] == 'code':
                        segment_stack.append(
                            StrippedCodeSegment(
                                self.raw[started[2]:idx],
                                pos_marker=started[1])
                        )
                    else:
                        raise ValueError("Unexpected `started` value?!")
                started = ('whitespace', this_pos, idx)
            else:
                # This isn't whitespace or a newline
                if started:
                    if started[0] == 'code':
                        # We don't want to reset the code counter!
                        continue
                    elif started[0] == 'whitespace':
                        segment_stack.append(
                            WhitespaceSegment(
                                self.raw[started[2]:idx],
                                pos_marker=started[1])
                        )
                    else:
                        raise ValueError("Unexpected `started` value?!")
                started = ('code', this_pos, idx)
        return segment_stack


class QuotedSegment(RawSegment):
    type = 'quoted'


class StrippedCodeSegment(RawSegment):
    type = 'strippedcode'


class WhitespaceSegment(RawSegment):
    type = 'whitespace'
    is_whitespace = True


class NewlineSegment(WhitespaceSegment):
    type = 'newline'


class CommentSegment(RawSegment):
    type = 'comment'

    def parse(self):
        # Split into several types of comment? Or just parse as is?
        # Probably parse as is.
        return self
