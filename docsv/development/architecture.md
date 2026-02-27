# Architecture

At a high level, the behaviour of SQLFluff is divided into a few key stages.
Whether calling `sqlfluff lint`, `sqlfluff fix` or `sqlfluff parse`, the
internal flow is largely the same.

## Stage 1, the templater

This stage only applies to templated SQL. Vanilla SQL is sent straight to
stage 2, the lexer.

In order to lint templated SQL, SQLFluff must first convert the 'raw' or
pre-templated code into valid SQL, which can then be parsed. The templater
returns both the raw and post-templated SQL so that any rule violations which
occur in templated sections can be ignored and the rest mapped to their
original line location for user feedback.

*SQLFluff* supports multiple templating engines:

   * [Jinja](https://jinja.palletsprojects.com/)
   * SQL placeholders (e.g. SQLAlchemy parameters)
   * [Python format strings](https://docs.python.org/3/library/string.html#format-string-syntax)
   * [dbt](https://docs.getdbt.com/) (via plugin)

Under the hood dbt also uses Jinja, but in *SQLFluff* uses a separate
mechanism which interfaces directly with the dbt python package.

For more details on how to configure the templater see [Templating Configuration](../configuration/templating/index).


## Stage 2, the lexer

The lexer takes SQL and separates it into segments of whitespace and
code. Where we can impart some high level meaning to segments, we
do, but the result of this operation is still a flat sequence of
typed segments (all subclasses of `RawSegment`).


## Stage 3, the parser

The parser is arguably the most complicated element of SQLFluff, and is
relied on by all the other elements of the tool to do most of the heavy
lifting.

1. The lexed segments are parsed using the specified dialect's grammars. In
   SQLFluff, grammars describe the shape of SQL statements (or their
   components). The parser attempts to apply each potential grammar to the
   lexed segments until all the segments have been matched.

2. In SQLFluff, segments form a tree-like structure. The top-level segment is
   a `FileSegment`, which contains zero or more
   `StatementSegment`s, and so on. Before the segments have been parsed
   and named according to their type, they are 'raw', meaning they have no
   classification other than their literal value.

3. A segment's `.match()` method uses the `match_grammar`, on
   which `.match()` is called. SQLFluff parses in a single pass through
   the file, so segments will recursively match the file based on their
   respective grammars. In the example of a `FileSegment`, it
   first divides up the query into statements, and then the `.match()`
   method of those segments works out the structure within them.

   * *Segments* must implement a `match_grammar`. When `.match()`
      is called on a segment, this is the grammar which is used to decide
      whether there is a match.

   * *Grammars* combine *segments* or other *grammars* together in a
      pre-defined way. For example the `OneOf` grammar will match if any
      one of its child elements match.

   #. During the recursion, the parser eventually reaches segments which have
      no children (raw segments containing a single token), and so the
      recursion naturally finishes.

4. If no match is found for a segment, the contents will be wrapped in an
   `UnparsableSegment` which is picked up as a *parsing* error later.
   This is usually facilitated by the `ParseMode` on some grammars
   which can be set to `GREEDY`, allowing the grammar to capture
   additional segments as unparsable. As an example, bracketed sections
   are often configured to capture anything unexpected as unparsable rather
   than simply failing to match if there is more than expected (which would
   be the default, `STRICT`, behaviour).

5. The result of the `.match()` method is a `MatchResult` which
   contains the instructions on how to turn the flat sequence of raw segments
   into a nested tree of segments. Calling `.apply()` on this result
   at the end of the matching process is what finally creates the nested
   structure.

When working on the parser there are a couple of design principles
to keep in mind.

- Grammars are contained in *dialects*, the root dialect being
  the *ansi* dialect. The ansi dialect is used to host logic common
  to all dialects, and so does not necessarily adhere to the formal
  ansi specification. Other SQL dialects inherit from the ansi dialect,
  replacing or patching any segments they need to. One reason for the *Ref*
  grammar is that it allows name resolution of grammar elements at runtime
  and so a *patched* grammar with some elements overridden can still rely on
  lower-level elements which haven't been redeclared within the dialect
- All grammars and segments attempt to match as much as they can and will
  return partial matches where possible. It is up to the calling grammar
  or segment to decide whether a partial or complete match is required
  based on the context it is matching in.

## Stage 4, the linter

Given the complete parse tree, rule classes check for linting errors by
traversing the tree, looking for segments and patterns of concern. If
the rule discovers a violation, it returns a
`sqlfluff.core.rules.base.LintResult` pointing to the segment
which caused the violation.

Some rules are able to *fix* the problems they find. If this is the case,
the rule will return a list of fixes, which describe changes to be made to
the tree. This can include edits, inserts, or deletions. Once the fixes
have been applied, the updated tree is written to the original file.
