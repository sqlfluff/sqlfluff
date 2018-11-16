""" Contains the Lexer Class """

from .chunks import ChunkString, PositionedChunk
from .dialects import AnsiSQLDialiect


class RecursiveLexer(object):
    def __init__(self, dialect=AnsiSQLDialiect):
        self.dialect = dialect

    def lex(self, chunk, **start_context):
        # Match based on available matchers
        if start_context.get('block_comment_open', False):
            matches = self.dialect.inside_block_comment_matchers.chunkmatch(chunk)

            if len(matches) == 0:
                # No Match, just comment
                return ChunkString(chunk.contextualise('comment')), start_context

            # examine first match
            first_match = matches[0]
            if first_match[0].chunk == chunk.chunk:
                # We've matched the whole string!
                cs = ChunkString(chunk.contextualise(first_match[2].name))
                if first_match[2].name == 'open_block_comment_end':
                    new_context = start_context.copy()
                    new_context['block_comment_open'] = False
                    return cs, new_context
                else:
                    return cs, start_context
            elif first_match[0].start_pos == chunk.start_pos:
                # The match starts at the beginning, but isn't the whole string
                matched_chunk, remainder_chunk = chunk.split_at(len(first_match[0]))
                new_context = start_context.copy()
                if first_match[2].name == 'open_block_comment_end':
                    new_context['block_comment_open'] = False
                remainder_string, end_context = self.lex(remainder_chunk, **new_context)
                return ChunkString(matched_chunk.contextualise(first_match[2].name)) + remainder_string, end_context
            elif first_match[0].start_pos:
                raise RuntimeError("Found content, in an open block comment, before matching an end!? This shouldn't happen")
            else:
                # No Match, just content
                return ChunkString(chunk.contextualise('comment')), start_context
        else:
            matches = self.dialect.outside_block_comment_matchers.chunkmatch(chunk)

            if len(matches) == 0:
                # No Match, just content
                return ChunkString(chunk.contextualise('content')), start_context

            # examine first match
            first_match = matches[0]
            if first_match[0].chunk == chunk.chunk:
                # We've matched the whole string!
                cs = ChunkString(chunk.contextualise(first_match[2].name))
                if first_match[2].name == 'open_block_comment_start':
                    new_context = start_context.copy()
                    new_context['block_comment_open'] = True
                    return cs, new_context
                else:
                    return cs, start_context
            elif first_match[0].start_pos == chunk.start_pos:
                # The match starts at the beginning, but isn't the whole string
                matched_chunk, remainder_chunk = chunk.split_at(len(first_match[0]))
                new_context = start_context.copy()
                if first_match[2].name == 'open_block_comment_start':
                    new_context['block_comment_open'] = True
                remainder_string, end_context = self.lex(remainder_chunk, **new_context)
                return ChunkString(matched_chunk.contextualise(first_match[2].name)) + remainder_string, end_context
            elif first_match[0].start_pos:
                # The match doesn't start at the beginning, we've got content first
                content_chunk, remainder_chunk = chunk.split_at(first_match[1])
                remainder_string, end_context = self.lex(remainder_chunk, **start_context)
                return ChunkString(content_chunk.contextualise('content')) + remainder_string, end_context
            else:
                # No Match, just content
                return ChunkString(chunk.contextualise('content')), start_context

    def lex_chunk_buffer(self, chunk_iterable, **start_context):
        """ Iterate through chunks adding to the string """
        cs = ChunkString()
        context_cache = start_context.copy()
        for new_chunk in chunk_iterable:
            ncs, context_cache = self.lex(new_chunk, **context_cache)
            cs += ncs
        return cs, context_cache

    def lex_file_obj(self, file_obj):
        chunk_buffer = []
        for idx, line in enumerate(file_obj, start=1):
            chunk_buffer.append(PositionedChunk(line, 0, idx, None))
        # We just pull the first element of the tuple, we don't care about the remaining context
        res = self.lex_chunk_buffer(chunk_buffer)[0]
        return res
