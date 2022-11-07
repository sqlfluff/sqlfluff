Internals
=========

It is recommended that the following is read in conjunction with exploring
the codebase. `dialect_ansi.py` in particular is helpful to understand the
recursive structure of segments and grammars. Some more detail is also given
on our Wiki_ including a `Contributing Dialect Changes`_ guide.

.. _Wiki: https://github.com/sqlfluff/sqlfluff/wiki/
.. _`Contributing Dialect Changes`: https://github.com/sqlfluff/sqlfluff/wiki/Contributing-Dialect-Changes


Architecture
------------

At a high level, the behaviour of SQLFluff is divided into a few key stages.
Whether calling `sqlfluff lint`, `sqlfluff fix` or `sqlfluff parse`, the
internal flow is largely the same.


Stage 1, the templater
^^^^^^^^^^^^^^^^^^^^^^

This stage only applies to templated SQL, most commonly Jinja and dbt. Vanilla
SQL is sent straight to stage 2, the lexer.

In order to lint templated SQL, SQLFluff must first convert the 'raw' or
pre-templated code into valid SQL, which can then be parsed. The templater
returns both the raw and post-templated SQL so that any rule violations which
occur in templated sections can be ignored and the rest mapped to their
original line location for user feedback.

.. _Jinja: https://jinja.palletsprojects.com/
.. _dbt: https://docs.getdbt.com/

*SQLFluff* supports two templating engines: Jinja_ and dbt_.

Under the hood dbt also uses Jinja, but in *SQLFluff* uses a separate
mechanism which interfaces directly with the dbt python package.

For more details on how to configure the templater see :ref:`templateconfig`.


Stage 2, the lexer
^^^^^^^^^^^^^^^^^^

The lexer takes SQL and separates it into segments of whitespace and
code. No meaning is imparted; that is the job of the parser.


Stage 3, the parser
^^^^^^^^^^^^^^^^^^^

The parser is arguably the most complicated element of SQLFluff, and is
relied on by all the other elements of the tool to do most of the heavy
lifting.

#. The lexed segments are parsed using the specified dialect's grammars. In
   SQLFluff, grammars describe the shape of SQL statements (or their
   components). The parser attempts to apply each potential grammar to the
   lexed segments until all the segments have been matched.

#. In SQLFluff, segments form a tree-like structure. The top-level segment is
   a :code:`FileSegment`, which contains zero or more
   :code:`StatementSegment`\ s, and so on. Before the segments have been parsed
   and named according to their type, they are 'raw', meaning they have no
   classification other than their literal value.

#. The three key components to the parser are segments,
   :code:`match_grammar`\ s and :code:`parse_grammar`\ s. A segment can be a
   leaf in the parse tree, such as a :code:`NumericLiteralSegment`, which is
   simply a number, or can contain many other segments, such as a
   :code:`SelectStatementSegment`. Each segment can specify a
   :code:`parse_grammar`, and a :code:`match_grammar`. If both a
   :code:`match_grammar` and :code:`parse_grammar` are defined in a segment,
   :code:`match_grammar` is used to quickly prune the tree for branches which
   do not match segments being parsed, and the :code:`parse_grammar` is then
   used to refine the branch identified as correct. If only a
   :code:`match_grammar` is defined, then it serves the purpose of both pruning
   and refining.

#. A segment's :code:`.parse()` method uses the :code:`parse_grammar`, on
   which :code:`.match()` is called. The *match* method of this grammar will
   return a potentially refined structure of the segments within the
   segment in greater detail. In the example of a :code:`FileSegment`, it
   first divides up the query into statements and then finishes.

   * *Segments* must implement a :code:`match_grammar`. When :code:`.match()`
      is called on a segment, this is the grammar which is used to decide
      whether there is a match.

   * *Grammars* combine *segments* or other *grammars* together in a
      pre-defined way. For example the :code:`OneOf` grammar will match if any
      one of its child elements match.

   #. Regardless of whether the :code:`parse_grammar` was used, the next step
      is to recursively call the :code:`.parse()` method of each of the child
      segments of the grammar. This operation is wrapped in a method called
      :code:`.expand()`. In the :code:`FileSegment`, the first step will have
      transformed a series of raw tokens into :code:`StatementSegment`
      segments, and the *expand* step will let each of those segments refine
      the content within them.

   #. During the recursion, the parser eventually reaches segments which have
      no children (raw segments containing a single token), and so the
      recursion naturally finishes.

#. If no match is found for a segment, the contents will be wrapped in an
:code:`UnparsableSegment` which is picked up as a *parsing* error later.

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


Stage 4, the linter
^^^^^^^^^^^^^^^^^^^

Given the complete parse tree, rule classes check for linting errors by
traversing the tree, looking for segments and patterns of concern. If
the rule discovers a violation, it returns a :code:`LintResult` pointing
to the segment which caused the violation.

Some rules are able to *fix* the problems they find. If this is the case,
the rule will return a list of fixes, which describe changes to be made to
the tree. This can include edits, inserts, or deletions. Once the fixes
have been applied, the updated tree is written to the original file.


.. _reflowinternals:

Reflow Internals
----------------

Many rules supported by SQLFluff involve the spacing and layout of different
elements, either to enforce a particular layout or just to add or remove
code elements in a way sensitive to the existing layout configuration. The
way this is achieved is through some centralised utilities in the
`sqlfluff.utils.reflow` module.

This module aims to achieve several things:
* Less code duplication by implementing reflow logic in only one place.

* Provide a streamlined interface for rules to easily utilise reflow logic.

  * Given this requirement, it's important that reflow utilities work
    within the existing framework for applying fixes to potentially
    templated code. We achieve this by returning `LintFix` objects which
    can then be returned by each rule wanting to use this logic.

* Provide a consistent way of *configuring* layout requirements. For more
  details on configuration see :ref:`layoutconfig`.

To support this, the module provides a :code:`ReflowSequence` class which
allows access to all of the relevant operations which can be used to
reformat sections of code, or even a whole file. Unless there is a very
good reason, all rules should use this same approach to ensure consistent
treatment of layout.

.. autoclass:: sqlfluff.utils.reflow.ReflowSequence
   :members:

.. autoclass:: sqlfluff.utils.reflow.elements.ReflowPoint
   :members:
   :inherited-members:

.. autoclass:: sqlfluff.utils.reflow.elements.ReflowBlock
   :members:
   :inherited-members:
