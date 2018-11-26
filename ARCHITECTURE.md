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


