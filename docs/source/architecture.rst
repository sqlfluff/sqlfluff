Architecture
============

Stage 1, the templater
----------------------

The templater takes raw files and optionally fills in any configurable
sections before passing onto the linter. In particular most templating
systems use curly brackets *{}* to indicate templatable sections and
these are not currently set up in any of the lexers, and so will fail
at the next step if not dealt with here.

Most templated SQL in the wild uses Jinja_ and so that is the default
templater for *sqlfluff*. It uses the config framework to get at any
templating variables.

For more details on how to configure the templater see :ref:`templateconfig`.

.. _Jinja: https://jinja.palletsprojects.com/

Stage 2, the lexer
------------------

The lexer takes raw text and splits it into tokens. Nothing is *removed* but
whitepace and code are seperated. In principle all identifiers should be
seperated at this stage, but they should not be imparted any meaning at this
stage. Any files which cannot be lexed, should raise a *SQLLexError*.

While the Lexer is passed a series of raw segments, it will return a single
segment, usually a :code:`FileSegment`, which will be used to initite parsing.

Stage 3, the parser
-------------------

We recursively parse each of the elements, using their in built grammars.

#. Initially we start with a segment, which contains only raw segments. This
   is normally a :code:`FileSegment`, but it could in theory be any kind of
   segment, and as we recurse it will be lower and lower sublevels.

#. We then *parse* this element by calling :code:`.parse()`.

   #. This first calls uses the :code:`parse_grammar` if that is present, on
      which we call :code:`.match()`. The *match* method of this grammar will
      return a potentially refined structure of the segments within this
      segment in greater detail than what was initially there. In the example
      of a :code:`FileSegment`, it first divides up the query into statements
      and then finishes.

   #. The :code:`.match()` method of any grammar is naturally recursive, and
      is comprised of *segments* and *grammars*. The match step is still not
      inert however and child elements of a match grammar may return more
      specific versions of segments during this phase even though we are not
      calling :code:`.parse()`

      * *Segments* must implement a :code:`match_grammar` to be used in this
        way. When :code:`.match()` is called on a segment, this is the grammar
        which is used to decide whether there is a match.

      * *Grammars* are objects which combine *segments* or other *grammars*
        together in a pre-defined way. For example the :code:`OneOf` grammar
        will match if any one of it's child elements match.

   #. Regardless of whether the :code:`parse_grammar` was used, the next step
      is to recursively call the :code:`.parse()` method of each of the child
      segments of the grammar. This operation is wrapped in a method called
      :code:`.expand()`. In the :code:`FileSegment`, the first step will have
      transformed a seried of raw tokens into :code:`StatmentSegment` segments,
      and the *expand* step will let each of those segments refine the content
      within them.

   #. Eventually in that recursive operation we reach segments which have no
      children (raw elements containing a single token), and so the recursion
      naturally finishes.

#. If no match is found for the current segment, the contents will be wrapped
   in an :code:`UnparsableSegment` which can be picked up as a *parsing* error
   later.

#. In analysing the eventual tree, any *UnparsableSegment* objects should
   raise a *SQLParseError* which can then be formatted and raised to the user.

Principles within the parser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The parser is arguably the most complicated element of sqlfluff, and is
relied on by all the other elements of the tool to do most of the heavy
lifting. When working on the parser there are a couple of design principles
to keep in mind.

- The core of the grammar is stored in a *dialect*, the root dialect being
  the *ansi* dialect. The intent here is that for other SQL dialects that
  they will inherit most of the logic from a parent dialect and then just
  reimplement the sections that they need to. One reason for the *Ref*
  grammar is that it allows name resolution of grammar elements at runtime
  and so a *patched* grammar with some elements overriden can still rely on
  lower level elements which haven't been overwritten.
- *Segments* and *Grammars* operate roughly interchangably from a dialect.
  A grammar is something which can be matched against and return a result.
  These will be used as instantiated classes and usually contain a set of
  elements (stored in the *_elements* attribute) which are the sub elements
  which the grammar will use for matching. These may in turn be a mixture
  of segments and grammars. A segment can be used as either a class or an
  instance of a class. While matching, the class itself is used, but if
  it does match, rather than just returning the original segments it was
  passed unchanged, it will optionally return mutated versions of those
  segments which may have been given a more specific meaning by the
  matcher. For example a *RawSegment* containing *123.4* may actually
  be mutated to an instance of the *NumericLiteralSegment* class when
  matched against the *NumericLiteralSegment* class.
- All grammars and segments attempt to match as much as they can and will
  return partial matches where possible. It is up to the calling grammar
  or segment to decide whether a partial or complete match is required
  based on the context it is matching in.

Stage 4, the linter
-------------------

Given the complete parse tree, we now walk that tree to assess the tree
for linting errors. A linter is an object which is able to traverse the
tree itself, allowing it to choose which objects it examines and which
it alerts as a problem.

Some linters, may optionally be able to *fix* the problems they find. If
this is the case, they will optionally return a mutated tree as one of
their return values, which can be passed to the next linter. In normal
operation this will not be what is returned, because it becomes confusing
with line references for a user fixing issues manually.
