# SqlFluff
## The SQL Linter for humans

# Architecture

The general architecture of parsing if that we have a few entities:
- `chunks`, which are positioned strings (they have both length, content and position).
  The relevant class is `Chunk`. `Chunks` can can be split as we iteratively detect
  tokens. MAYBE WE GET RID OF CHUNKS?
- `tokens`, which are contextualised `chunks`. Not all `chunks` are `tokens`,
  but all `tokens` are linked to a `chunk`. Specifically there are three classes
  related to `tokens`:
  - `Token`, which defines the rules for detecting a particular kind of token.
  - `TokenChunk`, which is an actual instance of a token being found.
- `syntax elements`, which are rules for how `tokens` can be put together. Generally
  these are the core elements which define a particular sql syntax. Similar to `tokens`
  there are:
  - `SyntaxRule`, which defines a rule of how tokens can be assembled.
  - `SyntaxTreeElement`, which is an instance of the above, linked to a sequence 
    of `TokenChunks` and `SyntaxTreeElements`.
- `dialect`, which represents a unique dialect of sql. This is a collection of `tokens`
  and `syntax elements`. These are defined so that inheritance can be used to define
  related syntaxes.
  

# More Notes...

We need a change of approach, especially in how the parser works.

## Principles:
- The parser is left to right, with no look ahead.
- It treats whitespace and comments as tokens.
- Patterns are *recursive*. They take a string, take what they can, pass some down to
  children and then return the unused part back to the parent.
- Patterns consist of *sequences*. A pattern can have sub-sequences at definition
  but these will get converted to their own sequences under the hood.
- Patterns are *greedy*, meaning they will take as much as they can before yielding
  and remaining string.
- A terminal behaves as a special case of a pattern. It exhibits the same behaviours
  as a pattern.
- Patterns either match, or not.
  - If a match is made, then the pattern extracts the part of the string which it
    has matched and returns the rest back up, along with a `node`.
  - If no match is made, then the pattern returns the whole string, the parent
    sequence decides whether this is an issue.
  - If at any point, we fail to match all the way up to the root `node` then that
    should raise a parsing error.
