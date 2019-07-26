
from collections import namedtuple

TokenMemory = namedtuple('TokenMemory', ['pos', 'token'], verbose=True)
Token = namedtuple('Token', ['start', 'end', 'terminator'], verbose=True)



class SQLParseError(ValueError):
    pass

print("Hello World!")

# Multi stage parser

## First strip comments, potentially extracting special comments (which start with sqlfluff:)
##   - this also makes comment sections, config sections (a subset of comments) and code sections


class BaseSegment(object):
    type = 'base'

    def __init__(self, raw, statement_index=1, line_no=1, line_pos=1, segments=None):
        self.raw = raw
        self.segments = segments
        self.statement_index = statement_index
        self.line_no = line_no
        self.line_pos = line_pos
    
    def parse(self):
        raise NotImplementedError("parse not implemented on type {0}".format(self.__class__))
    
    def __repr__(self):
        if self.segments:
            return "<{0}: ({1},{2},{3}) {4!s}>".format(
                self.__class__.__name__,
                self.statement_index,
                self.line_no,
                self.line_pos,
                self.segments)
        else:
            return "<{0}: ({1},{2},{3}) {4!r}>".format(
                self.__class__.__name__,
                self.statement_index,
                self.line_no,
                self.line_pos,
                self.raw)

    def reconstruct(self):
        if self.segments:
            return "".join([seg.reconstruct() for seg in self.segments])
        else:
            return self.raw


class FileSegment(BaseSegment):
    type = 'file'

    def parse(self):
        # Parsing files involves seperating comment segments and code segments and statements segments
        statement_index = self.statement_index
        line_no = self.line_no
        line_pos = self.line_pos

        # Comments override everything unless we're in a string literal
        string_tokens = [
            Token('\'', '\'', None),
            Token('"', '"', None),
            Token('`', '`', None)
        ]

        comment_tokens = [
            Token('/*', '*/', None),
            Token('-- ', None, '\n'),
            Token('#', None, '\n')
        ]

        statement_seperators = [';']

        last_statement_pos = 0
        last_pos = 0
        last_line_no = line_no
        last_line_pos = line_pos
        statement_stack = []
        segment_stack = []
        comment_entry = None
        string_entry = None
        skip = 0
        was_newline = False
        for pos in range(len(self.raw)):
            if was_newline:
                line_no += line_no
                line_pos = 0
            else:
                line_pos += 1
            # This will get picked up on the next round, hence WAS
            was_newline = (raw[pos] == '\n')

            if skip > 0:
                skip -= 1
                continue
            forward = raw[pos:]
            if not comment_entry and not string_entry:
                for s in string_tokens:
                    if forward.startswith(s.start):
                        print("Found string start at pos {0}! [{1!r}]".format(pos, forward[:5]))
                        string_entry = TokenMemory(pos, s)
                        # Don't store the segment, because we're only looking for
                        # strings at this stage so we can ignore "false" comments
                        continue
                for c in comment_tokens:
                    if forward.startswith(c.start):
                        print("Found comment start at pos {0}! [{1!r}]".format(pos, forward[:5]))
                        comment_entry = TokenMemory(pos, c)
                        # check that we have a segment to add
                        if pos - 1 > last_pos:
                            segment_stack.append(
                                CodeSegment(
                                    raw[last_pos:pos],
                                    statement_index=statement_index
                                )
                            )
                            last_pos = pos
                        continue
                for e in statement_seperators:
                    if forward.startswith(e):
                        # Ok we've found a statement ender, not in a comment or a string
                        print("Found statement end at pos {0}! [{1!r}]".format(pos, forward[:5]))
                        # We need to end the current code segment FIRST
                        if pos - 1 > last_pos:
                            segment_stack.append(
                                CodeSegment(
                                    raw[last_pos:pos],
                                    statement_index=statement_index
                                )
                            )
                            last_pos = pos
                        etl = len(e)
                        statement_stack.append(
                            StatementSegment(
                                raw[last_statement_pos:pos],
                                segments=segment_stack,
                                statement_index=statement_index))
                        statement_stack.append(
                            StatementSperatorSegment(
                                e,
                                statement_index=statement_index)
                        )
                        statement_index += 1
                        segment_stack = []
                        last_statement_pos = pos + etl
                        last_pos = pos + etl
                        skip = etl
                        continue
                # print(raw[pos:])
            elif string_entry:
                # We're in a string, just look for the end, of THIS KIND of string
                if string_entry.token.end and forward.startswith(string_entry.token.end):
                    print("Found string end at pos {0}! [{1!r}]".format(pos, forward[:5]))
                    # End of segment
                    # Don't save, remember, we're only looking for comments!
                    string_entry = None
                    continue
                elif string_entry.token.terminator and forward.startswith(string_entry.token.terminator):
                    print("Found string terminator at pos {0}! [{1!r}]".format(pos, forward[:5]))
                    # End of segment
                    # Don't save, remember, we're only looking for comments!
                    string_entry = None
                    continue
            elif comment_entry:
                # We're in a string, just look for the end, of THIS KIND of string
                if comment_entry.token.end and forward.startswith(comment_entry.token.end):
                    print("Found comment end at pos {0}! [{1!r}]".format(pos, forward[:5]))
                    # End of segment
                    if pos - 1 > last_pos:
                        etl = len(comment_entry.token.end)
                        segment_stack.append(
                            CommentSegment(
                                raw[last_pos:pos + etl],
                                statement_index=statement_index
                            )
                        )
                        last_pos = pos + etl
                        skip = etl
                    comment_entry = None
                    continue
                elif comment_entry.token.terminator and forward.startswith(comment_entry.token.terminator):
                    print("Found comment terminator at pos {0}! [{1!r}]".format(pos, forward[:5]))
                    # End of segment
                    if pos - 1 > last_pos:
                        segment_stack.append(
                            CommentSegment(
                                raw[last_pos:pos],
                                statement_index=statement_index
                            )
                        )
                        last_pos = pos
                    comment_entry = None
                    continue
            else:
                raise NotImplementedError("Aaargh!")
        # ok we got to the end, what did we finish in?
        if not comment_entry and not string_entry:
            # We ended on a code block. OK
            if len(raw) > last_pos:
                segment_stack.append(
                    CodeSegment(
                        raw[last_pos:len(raw)],
                        statement_index=statement_index
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
                        raw[last_pos:len(raw)],
                        statement_index=statement_index
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
                    raw[last_statement_pos:pos],
                    segments=segment_stack,
                    statement_index=statement_index))
            statement_index += 1
            segment_stack = []
            last_statement_pos = 0
            last_pos = 0
        
        self.segments = statement_stack
        return self

class StatementSperatorSegment(BaseSegment):
    type = 'statement_seperator'

    def parse(self):
        return self

class StatementSegment(BaseSegment):
    type = 'statement'

    def parse(self):
        return self

class CodeSegment(BaseSegment):
    type = 'code'

    def parse(self):
        return self

class CommentSegment(BaseSegment):
    type = 'comment'

    def parse(self):
        return self






raw = """\
# COMMENT
-- Another Comment
Select A from Sys.dual where a  
-- inline comment
in  ('RED',  /* Inline */  'GREEN','BLUE');
select * from tbl_b; # as another comment
insert into sch.tbl_b
    (col1)
values (123)
"""



tabsize = 4
SEMICOLON = ';'




if __name__ == "__main__":
    print("##### parsing:")
    print(raw)
    fs = FileSegment(raw)
    parsed = fs.parse()
    print(parsed.segments)
    print(parsed.reconstruct())
