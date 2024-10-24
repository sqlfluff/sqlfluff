.. _contributing_dialect_changes:

Contributing dialect changes
============================

One of the best ways that SQLFluff users can improve SQLFluff for themselves
and others is in contributing dialect changes.

Users will likely know their syntax much better than the regular maintainers
and will have access to an instance of that SQL dialect to confirm changes are
valid SQL in that dialect.

If you can fix your own issues then that's often the quickest way of unblocking
any issues preventing you from using SQLFluff! The maintainers are all
volunteers doing this in our spare time and (like you all I'm sure!), we
only have so much time to work on this.

How SQLFluff reads (or parses) SQL
----------------------------------

SQLFluff has a lexer and parser which is built in a very modular fashion that
is easy to read, understand, and expand on without any core programming skills
or deep knowledge of Python or how SQLFluff operates. For more information see
the :ref:`Architecture Documentation <architecture>`, but will cover that
briefly here to give you enough to start contributing.

We also have a robust Continuous Integration pipeline in GitHub where you can
gain confidence your changes are correct and will not break other SQLFluff
users, even before a regular maintainer reviews the code.

SQLFluff defines the syntax it will used in dialect files (more on this later).
If you look at the `dialect_ansi.py`_ file you will see it has syntax like
this:

.. _`dialect_ansi.py`: https://github.com/sqlfluff/sqlfluff/blob/main/src/sqlfluff/dialects/dialect_ansi.py

.. code-block:: python

   class SelectClauseSegment(BaseSegment):
       """A group of elements in a select target statement."""

       type = "select_clause"
       match_grammar = StartsWith(
           Sequence("SELECT", Ref("WildcardExpressionSegment", optional=True)),
           terminator=OneOf(
               "FROM",
               "WHERE",
               "ORDER",
               "LIMIT",
               "OVERLAPS",
               Ref("SetOperatorSegment"),
           ),
           enforce_whitespace_preceding_terminator=True,
       )

       parse_grammar = Ref("SelectClauseSegmentGrammar")

This says the :code:`SelectClauseSegment` starts with :code:`SELECT` or
:code:`SELECT *` and ends when it encounters a :code:`FROM`, :code:`WHERE`,
:code:`ORDER`...etc. line.

The :code:`match_grammar` is what is used primarily to try to match and parse
the statement. It can be relatively simple (as in this case), to quickly match
just the start and terminating clauses. If that is the case, then a
:code:`parse_grammar` is needed to actually delve into the statement itself
with all the clauses and parts it is made up of. The :code:`parse_grammar`
can be fully defined in the class or, like above example, reference another
class with the definition.

The :code:`match_grammar` is used to quickly identify the start and end of
this block, as parsing can be quite intensive and complicated as the parser
tries various combinations of classes and segments to match the SQL
(particularly optional ones like the :code:`WildcardExpressionSegment` above,
or when there is a choice of statements that could be used).

For some statements a quick match is not needed, and so we can delve straight
into the full grammar definition. In that case the :code:`match_grammar` will
be sufficient and we don't need the optional :code:`parse_grammar`.

Here's another statement, which only uses the :code:`match_grammar` and doesn't
have (or need!) an optional :code:`parse_grammar`:

.. code-block:: python

   class JoinOnConditionSegment(BaseSegment):
       """The `ON` condition within a `JOIN` clause."""

       type = "join_on_condition"
       match_grammar = Sequence(
           "ON",
           Indent,
           OptionallyBracketed(Ref("ExpressionSegment")),
           Dedent,
       )


You may have noticed that a segment can refer to another segment, and that is
a good way of splitting up a complex SQL expression into its component parts
to manage and handle them separately.

Segment grammar options
^^^^^^^^^^^^^^^^^^^^^^^

There are a number of options when creating SQL grammar including:

.. list-table::
   :header-rows: 1

   * - Grammar
     - Used For
     - Example
   * - :code:`"KEYWORD"`
     - Having a raw SQL keyword
     - :code:`"SELECT"`
   * - :code:`Sequence()`
     - Having a known sequence of Keywords or Segments
     - :code:`Sequence("SELECT", Ref("SelectClauseElementSegment"), "FROM"...)`
   * - :code:`AnyNumberOf()`
     - Choose from a set of options which may be repeated
     - :code:`"SELECT", AnyNumberOf(Ref("WildcardExpressionSegment"), Ref("ColumnReferenceSegment")...)...`
   * - :code:`OneOf()`
     - A more restrictive from a set of `AnyNumberOf` limited to just one option
     - :code:`OneOf("INNER","OUTER","FULL"), "JOIN"`
   * - :code:`Delimited()`
     - Used for lists (e.g. comma-delimited - which is the default)
     - :code:`"SELECT", Delimited("SelectClauseElementSegment"), "FROM"...`
   * - :code:`Bracketed()`
     - Used for bracketed options - like function parameters
     - :code:`Ref("FunctionNameSegment"), Bracketed(Ref("FunctionContentsGrammar")`

Some of the keywords have extra params you can give them, the most commonly
used will be :code:`optional=True`. This allows you to further define the
make up of a SQL statement. Here's the :code:`DeleteStatementSegment`
definition:

.. code-block:: python

   parse_grammar = Sequence(
       "DELETE",
       Ref("FromClauseSegment"),
       Ref("WhereClauseSegment", optional=True),
   )

You can see the :code:`WHERE` clause is optional (many's a head has been
shaken because of deletes without :code:`WHERE` clauses I'm sure, but
that's what SQL syntax allows!).

Using these Grammar options, it's possible to build up complex structures
to define SQL syntax.

Segments and Grammars
^^^^^^^^^^^^^^^^^^^^^

A Segment is a piece of the syntax which defines a :code:`type` (which can
be useful to reference later in rules or parse trees). This can be through
one of the functions that creates a Segment (e.g. :code:`NamedParser`,
:code:`SegmentGenerator`...etc.) or through a class.

A Grammar is a section of syntax that can be used in a Segment. Typically
these are created to avoid repeating the same code in multiple places.
Think of a Grammar as an alias for a piece of syntax to avoid you having
to type out the same code again and again and again.

The other good thing about Grammars is it allows other dialects to override
a specific part of a Segment without having to redefine the whole thing just
to tweak one small part. For example ansi defines this:

.. code-block:: python

   NotOperatorGrammar=StringParser("NOT", KeywordSegment, type="keyword")

whereas mysql overrides this to:

.. code-block:: python

   NotOperatorGrammar=OneOf(
       StringParser("NOT", KeywordSegment, type="keyword"),
       StringParser("!", CodeSegment, name="not_operator", type="not_operator"),
   ),

This allows MySQL to use :code:`!` in all the places that :code:`NOT` was used
(providing they use :code:`NotOperatorGrammar` rather than hardcode the
:code:`NOT` keyword of course). This makes it much easier to customise
syntax to a particular dialect without having to copy and paste (and
maintain) nearly identical code multiple times just to add the extra
:code:`!` syntax that MySQL supports to mean :code:`NOT`.

Dialects
^^^^^^^^

A lot of SQL is the same no matter which particular type of SQL you are
using. The basic :code:`SELECT.. FROM... WHERE` statement is common to them
all. However lots of different SQL dialects (Postgres, Snowflake, Oracle...
etc.) have sprung up as different companies have implemented SQL, or expanded
it, for their own needs.

For this reason, SQLFluff allows creating *dialects*, which can have different
grammars from each other.

SQLFluff has all the dialects in the `src/sqlfluff/dialects`_ folder. The main
dialect file (that every other dialect ultimately inherits from) is the
`dialect_ansi.py`_ file.

In SQLFluff, a dialect is basically a file which inherits everything from the
original ANSI dialect, and then adds or overrides parsing segments. If a dialect
has the exact same :code:`SELECT`, :code:`FROM` and :code:`WHERE` clauses as
ANSI but a different ::code:`ORDER BY` syntax, then only the ::code:`ORDER BY`
clause needs to overridden so the dialect file will be very small. For some of
the other dialects where there's lots of differences (:ref:`tsql_dialect_ref`!)
you may be overriding a lot more.

.. _`src/sqlfluff/dialects`: https://github.com/sqlfluff/sqlfluff/tree/main/src/sqlfluff/dialects

Lexing
^^^^^^

I kind of skipped this part, but before a piece of SQL can be *parsed*, it is
*lexed* - that is split up into symbols, and logical groupings.

An inline comment, for example, is defined as this:

.. code-block:: python

   RegexLexer(
       "inline_comment",
       r"(--|#)[^\n]*",
       CommentSegment,
       segment_kwargs={"trim_start": ("--", "#")},
   ),


That is, anything after :code:`--` or :code:`#` to the newline. This allows us
to deal with that whole comment as one lexed block and so we don't need to
define how to parse it (we even give that a parsing segment name here -
:code:`CommentSegment`).

For simple grammar addition, you won't need to to touch the lexing definitions
as they usually cover most common ones already. But for slightly more
complicated ones, you may have to add to this. So if you see lexing errors
then you may have to add something here.

Lexing happens in order. So it starts reading the SQL from the start, until
it has the longest lexing match, then it chomps that up, files it away as a
symbol to deal with later in the parsing, and starts again with the remaining
text. So if you have :code:`SELECT * FROM table WHERE col1 = 12345` it will not
break that up into :code:`S`, :code:`E`, :code:`L`...etc., but instead into
:code:`SELECT`, :code:`*`, :code:`FROM`, :code:`table`...etc.

An example of where we had to override lexing, is in BigQuery we have
parameterised variables which are of the form :code:`@variable_name`. The ANSI
lexer doesn't recognise the :code:`@` sign, so you could add a grammar or
segment for that. But a better solution, since you don't need to know two parts
(:code:`@` and :code:`variable_name`) is to just tell the lexer to go ahead
and parse the whole thing into one big symbol, that we will then use later
in the parser:

.. code-block:: python

   bigquery_dialect.insert_lexer_matchers(
       [
           RegexLexer("atsign_literal", r"@[a-zA-Z_][\w]*", CodeSegment),
       ],
       before="equals",
   )


Note the :code:`before="equals"` which means we tell the lexer the order of
preference to try to match this symbol. For example if we'd defined an
:code:`at_sign` lexing rule for other, standalone :code:`@` usage, then we'd
want this to be considered first, and only fall back to that if we couldn't
match this.

.. _dialect_keywords:

Keywords
^^^^^^^^

Most dialects have a keywords file, listing all the keywords. Some dialects
just inherit the ANSI keywords and then add or remove keywords from that.
Not quite as accurate as managing the actual keywords, but a lot quicker
and easier to manage usually!

Keywords are separated into RESERVED and UNRESERVED lists. RESERVED keywords
have extra restrictions meaning they cannot be used as identifiers. If using
a keyword in grammar (e.g. :code:`"SELECT"`), then it needs to be in one of
the Keywords lists so you may have to add it or you might see error's like
this (showing :code:`"NAN"` has not been added as a Keyword in this dialect)::

   RuntimeError: Grammar refers to 'NanKeywordSegment' which was not found in the redshift dialect

Also if editing the main ANSI dialect, and adding the the ANSI keyword list,
then take care to consider if it needs added to the other dialects if they
will inherit this syntax - usually yes unless explicitly overridden in those
dialects.

Where to find the grammar for your database
-------------------------------------------

Now that you know about some of the tools SQLFluff provides for lexing and
parsing a SQL statement, what changes will you make to it?  While devising
ad-hoc changes to the grammar to fix particular issues can be better than
nothing, the best and most robust contributions will be created by consulting
the source of truth for the grammar of your dialect when mapping it to
SQLFluff segments and grammars. This will help you exhaustively find all
possible statements that would be accepted by the dialect.

Many computer languages are written using venerable tools like `Flex`_ and
`Bison`_, or similar parser generators, and SQL database engines are no
exception. You can refer to the parser specification in the source code of
your database engine for the ultimate source of truth of how a SQL statement
will be parsed: you might be surprised at what your SQL engine will parse
due to gaps in the documentation!

You should also refer to the reference documentation for your SQL dialect
to get a concise high-level overview of what the statement grammar looks
like, as well as read of any further restrictions and intended use of the
grammar that you find. If your SQL engine is closed-source, then you'll
likely have only the reference documentation to work with. However, this
will always be a less-accurate resource than the bison grammar that's
actually used for code generation inside the database engine itself.

It is also extremely helpful to try parsing the queries that you put into
the test fixtures to make sure that they are actually parsable by the
database engine. They don't have to be *valid* queries per se (can refer
to non-existing table names, etc), but you should confirm that they are
*parsable*. We do not want to *require* that SQLFluff be able to parse a
statement that the actual database engine would reject: overeager matching
logic can create parsing issues elsewhere.

Here is a list of grammars and parsing techniques for some of the dialects
implemented by SQLFluff:

.. _`Flex`: https://en.wikipedia.org/wiki/Flex_(lexical_analyser_generator)
.. _`Bison`: https://en.wikipedia.org/wiki/GNU_Bison

ANSI SQL
^^^^^^^^

Unfortunately, the ANSI SQL standard is not free. If you want a licensed
copy of the latest standard, it must be purchased: `Part 2`_ is the most
useful section for SQLFluff since it contains the grammar. There are,
however, other resources you can find on the Internet related to this
standard:

* `modern-sql.com/standard`_: has a discussion on the various parts
  of the standard, and links to some older/draft versions of it that are
  out there.

* `jakewheat.github.io/sql-overview`_: has a nice browsable view of (only) the
  BNF grammar.

* `web.cecs.pdx.edu/~len/sql1999.pdf`_: a copy of the (much older) SQL:1999
  standard.

* `developer.mimer.com/services/mimer-sql-validator/`_: the SQL-2016
  validator can be used to verify if a query can be parsed using the ANSI
  standard.

.. _`Part 2`: https://webstore.ansi.org/standards/iso/isoiec90752016-1646101
.. _`modern-sql.com/standard`: https://modern-sql.com/standard
.. _`jakewheat.github.io/sql-overview`: https://jakewheat.github.io/sql-overview/
.. _`web.cecs.pdx.edu/~len/sql1999.pdf`: http://web.cecs.pdx.edu/~len/sql1999.pdf
.. _`developer.mimer.com/services/mimer-sql-validator/`: https://developer.mimer.com/services/mimer-sql-validator/

PostgreSQL
^^^^^^^^^^

Simply Googling for :code:`pg <statement>` will often bring up the documentation
for an older PG version. Please be sure you're referring to the latest version
of the documentation, as well as refer to the bison grammar.

* `PostgreSQL Bison grammar <https://github.com/postgres/postgres/blob/master/src/backend/parser/gram.y>`_

* `PostgreSQL Flex scanner <https://github.com/postgres/postgres/blob/master/src/backend/parser/scan.l>`_

* `More information about the parsing stage <https://www.postgresql.org/docs/current/parser-stage.html>`_

* `Reference documentation for Postgres SQL statements <https://www.postgresql.org/docs/current/sql-commands.html>`_

* To check if a statement is parseable, simply paste it into :code:`psql`.
  If you get a :code:`ERROR:  syntax error` then it means that it can't be
  parsed. These queries do not need to be parsed by SQLFluff; please do not
  include them in the main test fixtures. If you get a different error, then
  it means the query was parsed successfully, and might have failed for a
  different reason (e.g. non-existing column name, etc). In that case,
  it's probably best if SQLFluff can also parse it.

* The `pgsql-parser <https://www.npmjs.com/package/pgsql-parser>`_ tool wraps
  the official PostgreSQL source code & bison grammar linked above into a
  simple CLI tool. You can use it if you want to view the exact parse
  tree that PG can see.

MySQL
^^^^^

* `Reference documentation for MySQL SQL statements <https://dev.mysql.com/doc/refman/8.0/en/sql-statements.html>`_

* `MySQL Bison grammar <https://github.com/mysql/mysql-server/blob/8.0/sql/sql_yacc.yy>`_

* To check if a statement is parsable, simply paste it into :code:`mysql`.
  Look for :code:`ERROR 1064 (42000): You have an error in your SQL syntax`
  to indicate a parse error.

Example of contributing a syntax fix
------------------------------------

So that's a bit of theory but let's go through some actual examples of how
to add to the SQLFluff code to address any issues you are seeing. In this
I'm not going to explain about how to set up your Python development
environment (see the :ref:`development` and the `CONTRIBUTING.md`_ file
for that), nor how to manage Git (see our :ref:`using_git` guide if new to
that, and we use the standard “Fork, and then open a PR” workflow common to
GitHub projects).

.. _`CONTRIBUTING.md`: https://github.com/sqlfluff/sqlfluff/blob/main/CONTRIBUTING.md

So assuming you know (or are willing to follow above guides to find out!)
how to set up Python environment, and commit via Git, how do you contribute
a simple fix to a dialect for syntax you want SQLFluff to support?

Example 1
^^^^^^^^^

If we look at issue `#1520 <https://github.com/sqlfluff/sqlfluff/issues/1520>`_
it was raised to say we couldn't parse this:

.. code-block:: sql

   CREATE OR REPLACE FUNCTION public.postgres_setof_test()
   RETURNS SETOF text

and instead returned this message::

   Found unparsable section: 'CREATE OR REPLACE FUNCTION crw_public.po...'

This was in the :code:`postgres` dialect, so I had a look at
`dialect_postgres.py`_ and found the code in
:code:`CreateFunctionStatementSegment` which had the following:

.. _`dialect_postgres.py`: https://github.com/sqlfluff/sqlfluff/blob/main/src/sqlfluff/dialects/dialect_postgres.py

.. code-block:: python

   parse_grammar = Sequence(
       "CREATE",
       Sequence("OR", "REPLACE", optional=True),
       Ref("TemporaryGrammar", optional=True),
       "FUNCTION",
       Sequence("IF", "NOT", "EXISTS", optional=True),
       Ref("FunctionNameSegment"),
       Ref("FunctionParameterListGrammar"),
       Sequence(  # Optional function return type
           "RETURNS",
           OneOf(
               Sequence(
                   "TABLE",
                   Bracketed(
                       Delimited(
                           OneOf(
                               Ref("DatatypeSegment"),
                               Sequence(
                                   Ref("ParameterNameSegment"), Ref("DatatypeSegment")
                               ),
                           ),
                           delimiter=Ref("CommaSegment"),
                       )
                   ),
                   optional=True,
               ),
               Ref("DatatypeSegment"),
           ),
           optional=True,
       ),
       Ref("FunctionDefinitionGrammar"),
   )

So it allowed returning a table, or a datatype.

Fixing the issue was as simple as adding the :code:`SETOF` structure as
another return option:

.. code-block:: python

   parse_grammar = Sequence(
       "CREATE",
       Sequence("OR", "REPLACE", optional=True),
       Ref("TemporaryGrammar", optional=True),
       "FUNCTION",
       Sequence("IF", "NOT", "EXISTS", optional=True),
       Ref("FunctionNameSegment"),
       Ref("FunctionParameterListGrammar"),
       Sequence(  # Optional function return type
           "RETURNS",
           OneOf(
               Sequence(
                   "TABLE",
                   Bracketed(
                       Delimited(
                           OneOf(
                               Ref("DatatypeSegment"),
                               Sequence(
                                   Ref("ParameterNameSegment"), Ref("DatatypeSegment")
                               ),
                           ),
                           delimiter=Ref("CommaSegment"),
                       )
                   ),
                   optional=True,
               ),
               Sequence(
                   "SETOF",
                   Ref("DatatypeSegment"),
               ),
               Ref("DatatypeSegment"),
           ),
           optional=True,
       ),
       Ref("FunctionDefinitionGrammar"),
   )

With that code the above item could parse.

I added a test case (covered below) and submitted
`pull request #1522 <https://github.com/sqlfluff/sqlfluff/pull/1522>`_
to fix this.

Example 2
^^^^^^^^^

If we look at issue `#1537 <https://github.com/sqlfluff/sqlfluff/issues/1537>`_
it was raised to say we couldn't parse this:

.. code-block:: sql

   select 1 from group

And threw this error::

    ==== parsing violations ====
    L:   1 | P:  10 |  PRS | Line 1, Position 10: Found unparsable section: 'from'
    L:   1 | P:  14 |  PRS | Line 1, Position 14: Found unparsable section: ' group'


The reporter had also helpfully included the parse tree (produced by
:code:`sqlfluff parse`)::

    [L:  1, P:  1]      |file:
    [L:  1, P:  1]      |    statement:
    [L:  1, P:  1]      |        select_statement:
    [L:  1, P:  1]      |            select_clause:
    [L:  1, P:  1]      |                keyword:                                      'select'
    [L:  1, P:  7]      |                [META] indent:
    [L:  1, P:  7]      |                whitespace:                                   ' '
    [L:  1, P:  8]      |                select_clause_element:
    [L:  1, P:  8]      |                    literal:                                  '1'
    [L:  1, P:  9]      |            whitespace:                                       ' '
    [L:  1, P: 10]      |            [META] dedent:
    [L:  1, P: 10]      |            from_clause:
    [L:  1, P: 10]      |                unparsable:                                   !! Expected: 'FromClauseSegment'
    [L:  1, P: 10]      |                    keyword:                                  'from'
    [L:  1, P: 14]      |            unparsable:                                       !! Expected: 'Nothing...'
    [L:  1, P: 14]      |                whitespace:                                   ' '
    [L:  1, P: 15]      |                raw:                                          'group'
    [L:  1, P: 20]      |    newline:                                                  '\n'

So the problem was it couldn't parse the :code:`FromClauseSegment`. Looking at
that definition showed this:

.. code-block:: python

   FromClauseTerminatorGrammar=OneOf(
       "WHERE",
       "LIMIT",
       "GROUP",
       "ORDER",
       "HAVING",
       "QUALIFY",
       "WINDOW",
       Ref("SetOperatorSegment"),
       Ref("WithNoSchemaBindingClauseSegment"),
   ),

So the parser was terminating as soon as it saw the :code:`GROUP` and saying
*"hey we must have reached the end of the :code:`FROM` clause"*.

This was a little restrictive so changing that to this solved the problem:

.. code-block:: python

   FromClauseTerminatorGrammar=OneOf(
       "WHERE",
       "LIMIT",
       Sequence("GROUP", "BY"),
       Sequence("ORDER", "BY"),
       "HAVING",
       "QUALIFY",
       "WINDOW",
       Ref("SetOperatorSegment"),
       Ref("WithNoSchemaBindingClauseSegment"),
   ),

You can see we simply replaced the :code:`"GROUP"` by a
:code:`Sequence("GROUP", "BY")` so it would *only* match if both words were
given. Rechecking the example with this changed code, showed it now parsed.
We did the same for :code:`"ORDER"`, and also changed a few other places in
the code with similar clauses and added a test case (covered below) and
submitted `pull request #1546 <https://github.com/sqlfluff/sqlfluff/pull/1546>`_
to fix this.

Example 3
^^^^^^^^^

As an example of using the reference grammar to fix an existing SQLFluff
grammar, `pull request #4744 <https://github.com/sqlfluff/sqlfluff/pull/4744>`_
contributed the :code:`CREATE CAST` / :code:`DROP CAST` statements to SQLFluff
from scratch for both ANSI and PostgreSQL dialects. The first step when
contributing a new statement is to check whether the statement is part of the
ANSI standard. If it is, then you very likely should first start by adding a
generally vendor-neutral version to the SQLFluff ANSI dialect so that other
dialects can inherit from it. Every database engine deviates from the ANSI
standard in practice, but by adding a reasonably standard segment to the ANSI
dialect, you'll probably do a reasonable thing for most other database
dialects.

In this case, `CREATE and DROP CAST were indeed defined in the ANSI standard <https://jakewheat.github.io/sql-overview/sql-2016-foundation-grammar.html#_11_63_user_defined_cast_definition>`,
as quickly revealed by a quick search of the document::


    <user-defined cast definition> ::=
        CREATE CAST <left paren>  <source data type>  AS <target data type>  <right paren>
            WITH <cast function>
            [ AS ASSIGNMENT ]

So the first step was to read this ANSI BNF grammar and use it to build a
corresponding vendor-neutral :code:`CreateCastSegment` in `dialect_ansi.py`_.

.. code-block:: python

   class CreateCastStatementSegment(BaseSegment):
       """A `CREATE CAST` statement.
       https://jakewheat.github.io/sql-overview/sql-2016-foundation-grammar.html#_11_63_user_defined_cast_definition
       """

       type = "create_cast_statement"

       match_grammar: Matchable = Sequence(
           "CREATE",
           "CAST",
           Bracketed(
               Ref("DatatypeSegment"),
               "AS",
               Ref("DatatypeSegment"),
           ),
           "WITH",
           Ref.keyword("SPECIFIC", optional=True),
           OneOf(
               "ROUTINE",
               "FUNCTION",
               "PROCEDURE",
               Sequence(
                   OneOf("INSTANCE", "STATIC", "CONSTRUCTOR", optional=True),
                   "METHOD",
               ),
           ),
           Ref("FunctionNameSegment"),
           Ref("FunctionParameterListGrammar", optional=True),
           Sequence("FOR", Ref("ObjectReferenceSegment"), optional=True),
           Sequence("AS", "ASSIGNMENT", optional=True),
       )

   # Not shown: register the CreateCastStatementSegment in StatementSegment

As you work your way through the grammar, think about whether other parts
of the SQL language might contain similar elements. For example, here we
noticed that there are already segments we can reuse for data types, function
names, and function parameter lists. This helped simplify our new grammar,
as well as make it easy to centrally change those particular areas of the
grammar in other dialects. Also consider whether there are entire new segments
and grammars you should separately define in addition to the root statement
segment you're writing. Introducing new and reusing existing segments adds
structure to the SQLFluff parse tree that can make it easier for lint rules
to analyze the tree. *A strong indicator that there should be a shared*
*segment or grammar is when the reference grammar has a symbol that is reused*
*from multiple other symbols/statements*.

After writing the ANSI segment (and corresponding tests), it was time to move
on to the PostgreSQL grammar. In this case, a quick glance at the
`documentation <https://www.postgresql.org/docs/15/sql-createcast.html>`_ shows
us that there are some notable differences from ANSI SQL:

* You can only specify :code:`FUNCTION`. Other keywords like :code:`ROUTINE`
  and :code:`PROCEDURE` are rejected.

* The `SPECIFIC` keyword is not supported.

* Most importantly: PG provides some non-standard extensions which we'd like
  to include, like :code:`WITHOUT FUNCTION` and :code:`AS IMPLICIT`.

However, we should also consult the `bison grammar for CREATE CAST`_. Bison
grammars tend to be very lengthy and daunting, but the right techniques can
help you quickly and easily find what you're looking for:


* Search for a symbol by adding a :code:`:` to the end of it.

* Start with the highest level of the thing you are looking for. For example,
  start with the top-level statement symbol. With PostgreSQL, all statements
  end with :code:`Stmt`. Putting it all together, if we search for
  :code:`CreateCastStmt:`, that takes us right to the definition for it.

* Drill down into deeper parts of the parser to learn more. For example, we
  see :code:`function_with_argtypes` in the sequence; if we want to know what
  that means, search for :code:`function_with_argtypes:` to find it.

Examining the Bison grammar can take a few extra minutes, but it can be
rewarding. You'll be surprised what you might learn. I've found entire
alternate spellings of keywords in there that were not in the documentation,
and which testing showed were indeed valid SQL!  The grammar in PG
documentation is `human-maintained`_ and not auto-generated, so there can
be and are gaps between what is parsable and what is documented.

.. _`bison grammar for CREATE CAST`: https://github.com/postgres/postgres/blob/e0693faf797f997f45bee8e572e8b4288cc7eaeb/src/backend/parser/gram.y#L8938
.. _`human-maintained`: https://github.com/postgres/postgres/blob/master/doc/src/sgml/ref/create_cast.sgml

A good approach if you're still learning might be to draft a segment from the
high-level documentation, and then systematically go through it with the bison
grammar and verify it's correct (and that you're not forgetting anything).

One aspect of bison grammars to be aware of is that the tend to be very
recursive, because it doesn't have the high-level constructs such as
:code:`AnyOf`, :code:`Delimited`, :code:`Bracketed`, and so on that SQLFluff
provides. On the other hand, SQLFluff doesn't scale well with recursion.
Sometimes it's unavoidable and reasonable in many cases (e.g. parenthesized
expression) to refer to another segment recursively. But many times the
recursion is extremely trivial, and should always be rewritten using an
existing high-level SQLFluff concept. For example, this bison grammar defines
a bracketed comma-delimited list which would be better represented using
:code:`Bracketed` and :code:`Delimited` in SQLFluff::

    func_args:	'(' func_args_list ')'              { $$ = $2; }
                | '(' ')'                           { $$ = NIL; }
            ;

    func_args_list:
                func_arg                            { $$ = list_make1($1); }
                | func_args_list ',' func_arg       { $$ = lappend($1, $3); }
            ;

Example 4
^^^^^^^^^

As an example of using the reference grammar to fix an existing SQLFluff
grammar, `issue #4336 <https://github.com/sqlfluff/sqlfluff/issue/4336>`_
reported that array slices were not being parsed correctly in PostgreSQL.
A simple :code:`SELECT` statement was given that I further simplified to
the following test case:

.. code-block:: sql

   SELECT a[2:2+3];

Obviously, we know that a simple query like :code:`SELECT a;` would parse,
so it's surely related to the array access. I started by looking up the
bison grammar for PostgreSQL's :code:`SELECT` statement and drilling down
into it to find an array accessor symbol; searching for :code:`SelectStmt:`
proved to be a `lucky guess to start with`_::

    SelectStmt: select_no_parens            %prec UMINUS
                | select_with_parens        %prec UMINUS
            ;

.. _`lucky guess to start with`: https://github.com/postgres/postgres/blob/e0693faf797f997f45bee8e572e8b4288cc7eaeb/src/backend/parser/gram.y#L12497-L12504

Drilling down into the grammar via :code:`SelectStmt` -->
:code:`select_no_parens` --> :code:`simple_select` --> :code:`target_list`
--> :code:`target_el` show that we are dealing with an :code:`a_expr`, which
is the main symbol widely used to represent an expression throughout the
grammar. SQLFluff implements that as :code:`ExpressionSegment` (and more
specifically :code:`Expression_A_Grammar`). Looking further:
:code:`target_el` --> :code:`a_expr` --> :code:`c_expr` --> :code:`columnref`.
Which brings us to a key rule::

    columnref:	<snip>
                | ColId indirection
                    {
                        $$ = makeColumnRef($1, $2, @1, yyscanner);
                    }

Digging into :code:`indirection`, we finally find where the array accessor
is happening::

    indirection:
                indirection_el                      { $$ = list_make1($1); }
                | indirection indirection_el        { $$ = lappend($1, $2); }
            ;
    indirection_el: <snip>
                | '[' a_expr ']'
                    {
                        A_Indices *ai = makeNode(A_Indices);

                        ai->is_slice = false;
                        ai->lidx = NULL;
                        ai->uidx = $2;
                        $$ = (Node *) ai;
                    }
                | '[' opt_slice_bound ':' opt_slice_bound ']'
                    {
                        A_Indices *ai = makeNode(A_Indices);

                        ai->is_slice = true;
                        ai->lidx = $2;
                        ai->uidx = $4;
                        $$ = (Node *) ai;
                    }
            ;
    opt_slice_bound:
                a_expr                              { $$ = $1; }
                | /*EMPTY*/                         { $$ = NULL; }
            ;

From this we observe:

* There is a sequence of indirection elements.

* There can be a simple array index provided, which is an expression.

* Most importantly, and most immediate to our problem, is the observation that
  each slice bound is optional, and if it is present, then it is an expression.

Now that we looked up the relevant PG grammar, we can dig into the
corresponding SQLFluff grammar in a similar top-down way:
:code:`postgres.SelectStatementSegment` --> we see it's mostly a copy of
the ANSI select statement, so --> :code:`ansi.SelectStatementSegment` -->
remember :code:`Ref` always picks the dialect-specific grammar first -->
:code:`postgres.SelectClauseSegment` -->
:code:`ansi.SelectClauseSegment.parse_grammar` -->
:code:`postgres.SelectClauseSegmentGrammar` -->
:code:`ansi.SelectClauseElementSegment` -->
:code:`ansi.BaseExpressionElementGrammar` -->
:code:`ansi.ExpressionSegment` --> :code:`ansi.Expression_A_Grammar` -->
:code:`ansi.Expression_C_Grammar` --> :code:`ansi.Expression_D_Grammar` -->
notice this at the end of the sequence --> :code:`postgres.Accessor_Grammar`
--> :code:`postgres.ArrayAccessorSegment`. As you navigate, always remember to
check for dialect-specific grammar before falling back to the inherited grammar
(e.g. ANSI). Finally, we have found the part of the grammar that corresponds to
the :code:`indirection_el` in the bison grammar!

.. code-block:: python

   class ArrayAccessorSegment(ansi.ArrayAccessorSegment):
       """Overwrites Array Accessor in ANSI to allow n many consecutive brackets.

       Postgres can also have array access like python [:2] or [2:] so
       numbers on either side of the slice segment are optional.
       """

       match_grammar = Sequence(
           AnyNumberOf(
               Bracketed(
                   Sequence(
                       OneOf(
                           OneOf(
                               Ref("QualifiedNumericLiteralSegment"),
                               Ref("NumericLiteralSegment"),
                           ),
                           Sequence(
                               OneOf(
                                   Ref("QualifiedNumericLiteralSegment"),
                                   Ref("NumericLiteralSegment"),
                                   optional=True,
                               ),
                               Ref("SliceSegment"),
                               OneOf(
                                   Ref("QualifiedNumericLiteralSegment"),
                                   Ref("NumericLiteralSegment"),
                               ),
                           ),
                           Sequence(
                               OneOf(
                                   Ref("QualifiedNumericLiteralSegment"),
                                   Ref("NumericLiteralSegment"),
                               ),
                               Ref("SliceSegment"),
                               OneOf(
                                   Ref("QualifiedNumericLiteralSegment"),
                                   Ref("NumericLiteralSegment"),
                                   optional=True,
                               ),
                           ),
                       ),
                   ),
                   bracket_type="square",
               )
           )
       )

Observing this, we can make a few observations. The most glaring are that:

* Only numeric literals are accepted! No expressions. Clearly, that's the
  source of the issue that the person reported.

* But while we are here, notice another problem we can fix: when a
  :code:`SliceSegment` (a |colon|) is present, you're forced to include a
  numeric literal either before or after the SliceSegment. You can't have
  :code:`[:]`, even though that's valid SQL that PG can parse.

.. |colon| raw:: html

    <code class="code docutils literal notranslate">:</code>

At this point, it's a simple matter of simplifying & rewriting the grammar
to fix these shortcomings and better align it with the bison grammar, which
was done in
`pull request #4748 <https://github.com/sqlfluff/sqlfluff/pull/4748>`_.

Testing your changes
--------------------

So you've made your fix, you've tested it fixed the original problem so just
submit that change, and all is good now?

Well, no. You want to do two further things:

* Test your change hasn't broken anything else. To do that you run the test
  suite.

* Add a test case, so others can check this in future.

To test your changes you'll need to have your environment set up (again see
the `CONTRIBUTING.md`_ file for how to do that).

Adding test cases for your changes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Adding a test case is simple. Just add a SQL file to `test/fixtures/dialects/`_
in the appropriate dialect directory. You can either expand an existing SQL
file test case (e.g. if adding something similar to what's in there) or create
a new one.

I advise adding the original SQL raised in the issue, and if you have examples
from the official syntax, then they are always good test cases to add as well.
For example, the `Snowflake documentation has an example section`_ at the
bottom of every syntax definition so just copy all them into your example file
too.

You should also use the reference grammar to exhaustively test various pedantic
combinations of syntax. It doesn't have to be runnable. It just needs to parse
correctly into the right structure, and be a statement that can get past the
parsing stage of the database engine. The documentation often includes more
simple examples that might not reflect all the real-world possibilities. While
referring to the reference documentation / bison grammar, try to come up with
a statement that uses as much of the grammar as it can!

Be sure that you verify that the SQL statements in your test are
*actually parsable by the database engine!*  An easy way to do that is often
to copy/paste the statement into the console and try running it, or use a
CLI parsing tool that *uses the same source code as the database engine*
(e.g. pgsql-parser). An error is ok (e.g. invalid column name), as long as
it's not a syntax error from parsing. Check the reference section at the
top of this document for dialect-specific resources.

.. _`test/fixtures/dialects/`: https://github.com/sqlfluff/sqlfluff/tree/main/test/fixtures/dialects
.. _`Snowflake documentation has an example section`: https://docs.snowflake.com/en/sql-reference/sql/select.html#examples

YML test fixture files
^^^^^^^^^^^^^^^^^^^^^^

In addition to the SQL files, we have auto-generated YAML counterparts for
them. The YAML contains the parsed version of the SQL, and having these in
our source code, allows us to easily see if they change, so if someone
redefines a syntax, which changes how a SQL statement is parsed, then
the SQL won't change but the parse tree does, so by having that in our
source code, and so checking that in with any pull request, we can spot
that and make sure we're comfortable the change is expected. For most
cases (except adding new test cases obviously!) you would not expect
unrelated YML files to change so this is a good check.

To regenerate all the YAML files when you add or edit any test fixture
SQL files run the following command:

.. code-block:: bash

   tox -e generate-fixture-yml

You can also do the following to only generate for a particular dialect,
or only for new and changed files, which is often quicker:

.. code-block:: bash

   tox -e generate-fixture-yml -- --dialect postgres
   tox -e generate-fixture-yml -- --new-only

It takes a few mins to run, and regenerates all the YAML files. You can
then do a :code:`git status` to see any differences.

When making changes, make sure to check the post-parse structure from the
test output or from the associated YAML file: check that each query element
is typed correctly. Typical bugs can be that a standalone keyword (such
as :code:`INTERVAL`) is parsed as a function name, or that an element that
should be :code:`date_part` is parsed as an :code:`identifier`. Typically
there is no need to write assertions by hand, but it's the developer's
responsibility to verify the structure from auto-generated YAML. One should
not assume that everything is working just because no parsing error is raised.

Running the test suite
^^^^^^^^^^^^^^^^^^^^^^

For the basic setup, see the local testing section of the `CONTRIBUTING.md`_
file first.

There's a few ways of running the test suite. You could just run the
:code:`tox` command, but this will run all the test suites, for various
python versions, and with and without dbt, and take a long time. Best to
leave that to our CI infrastructure. You just want to run what you need
to have reasonable confidence before submitting.

Testing a single fixture
^^^^^^^^^^^^^^^^^^^^^^^^

The :code:`dialects_test` is parametrized to automatically pick all files
under :code:`test/fixtures/dialects/`.

For example if you're adding or modifying
:code:`dialects/hive/select_interval.sql`, you can test that with:

.. code-block:: bash

   tox -e py38 -- -s test/dialects/dialects_test.py -k hive-select_interval.sql

The :code:`-s` flag for pytest enables printing of post-parse structure,
which allows you to quickly check that each query element is typed
correctly. Same can be seen in the generated fixture YAML file.

To run it a bit faster, you can invoke :code:`pytest` directly (requires
that you have activated the project venv):

.. code-block:: bash

   pytest -s test/dialects/dialects_test.py -k hive-select_interval.sql

Running all dialect tests
^^^^^^^^^^^^^^^^^^^^^^^^^

The following command runs just the dialect tests, for **all** dialects:

.. code-block:: bash

   tox -e py38 -- test/dialects/dialects_test.py

The following command runs just the dialect tests, for **a specific** dialect:

.. code-block:: bash

   tox -e py38 -- test/dialects/dialects_test.py -k ansi

Or, if making a dialect change to fix a rule that is incorrectly flagging,
you can just run the tests for that one rule, for example to run the
:sqlfluff:ref:`LT01` tests:

.. code-block:: bash

   tox -e py38 -- -k LT01 test

Final checks before committing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For formatting and linting it's usually enough to rely on the `pre-commit hook`_.

.. _`pre-commit hook`: https://github.com/sqlfluff/sqlfluff/blob/main/CONTRIBUTING.md#pre-commit-config

Run all tests (but only on one Python version, and without dbt):

.. code-block:: bash

   tox -e py311

I like to kick that off just before opening a PR but does take ~10 minutes
to run.

If you want also coverage & linting, run this instead (takes even more time):

.. code-block:: bash

   tox -e generate-fixture-yml,cov-init,py311,cov-report,linting

Also it should be noted that the coverage tests require several versions to
run (windows, and dbt) so can report missing coverage when run locally.

The rest can be left for the CI to check.

Regardless of what testing you do, GitHub will run the full regression suite
when the PR is opened or updated. Note first time contributors will need a
maintainer to kick off the tests until their first PR is merged.

Black code linting
^^^^^^^^^^^^^^^^^^

These tools are run automatically by the `pre-commit hook`_, but can also be
run manually for those not using that.

We use `ruff`_ to lint our python code (being a linter ourselves we should
have high quality code!). Our CI, or the :code:`tox` commands above will run
this and flag any errors.

In most cases running `black`_ on the python file(s) will correct any simple
errors (e.g. line formatting) but for some you'll need to run `ruff` to see the
issues and manually correct them.

.. _`ruff`: https://docs.astral.sh/ruff/
.. _`black`: https://github.com/psf/black

Submitting your change
----------------------

We use the standard GitHub workflow so simply fork the repo, clone it locally,
make the change, push it to your fork, then open a pull request back to the
original SQLFluff repo. There’s lots more info in our :ref:`using_git` guide
if you're new to Git.

Once you open the PR CI tests will run, and after 5-10mins should complete.
If all green, then a maintainer will pick it up as soon as they can. Have a
good, easy to understand, small PR with all the tests passing, makes it easier
to review so more likely to be merged quickly.

Questions
---------

Feel free to open up any issues on GitHub, or join the :ref:`sqlfluff_slack`
for any quick questions to the community/maintainers.
