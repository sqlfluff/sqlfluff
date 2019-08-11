# New Parser
(working doc)

## Stage 1, the lexer
The lexer takes raw text and splits it into tokens. Nothing is _removed_ but whitepace and code
are seperated. In principle all identifiers should be seperated at this stage, but they should
not be imparted any meaning at this stage. Any files which cannot be lexed, should raise a `SQLLexError`.

The lexer is normally not called directly, but through the `from_raw` method of the `FileSegment`.

## Stage 2, the parser
We recursively parse each of the elements, using their in built grammars.

1. Initially we start with a segment, which contains only raw segments. This is normally a `FileSegment`,
   but it could in theory be any kind of segment, and as we recurse it will be lower and lower sublevels.
2. We then _parse_ this element. This calls the `parse` method on the segment, and uses the _parse grammar_
   if that is present. If no _parse grammar_ is present then the _match_ grammar will be used instead on
   the segment in question. This will return either a new list of segments (where we expect that some are
   likely no longer just raw segments), or it will return `None` or an empty list, to indicate it has not
   matched. If no match is found for the current segment, the contents will be wrapped in an `UnparsableSegment`
   which can be picked up as a _parsing_ error later.
   *NB* any _segments_ referenced in the grammar, will have their _match grammar_
   used rather than their _parse grammar_. Their _parse grammar_ will only be called when they are currently
   the subject of the _parse_.
3. When the segment is _parsed_, we then iterate through all the child segments, calling their `parse` method,
   as above. There are options which can be passed to the `parse` method to limit how many layers deep the
   _parse_ will go. Raw elements, return themselves with no sub-segments, which means that they effectively
   limit how deep a parse can go to avoid infinite recursion.
4. In analysing the eventual tree, any `UnparsableSegment` objects should raise a `SQLParseError` which can
   then be formatted and raised to the user.

## Stage 3, the linter
Given the complete parse tree, we now walk that tree to assess the tree for linting errors. A linter is an
object which is able to traverse the tree itself, allowing it to choose which objects it examines and which
it alerts as a problem.

Some linters, may optionally be able to _fix_ the problems they find. If this is the case, they will optionally
return a mutated tree as one of their return values, which can be passed to the next linter. In normal operation
this will not be what is returned, because it becomes confusing with line references for a user fixing issues
manually.
