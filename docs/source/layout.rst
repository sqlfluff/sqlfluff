.. _layoutref:

Let's talk about whitespace
===========================

If there is one part of building a linter that is going to be controversial
it's going to be **whitespace** (closely followed by **cApiTaLiSaTiOn** 😁).

More specifically, **whitespace** divides into three key themes:

#. **Spacing**: The amount of whitespace between elements on the same line.

#. **Line Breaks**: The choice of where within the code it is inappropriate,
   appropriate or even compulsory to have a line break.

#. **Indentation**: Given a line break, how much whitespace should precede
   the first code element on that line.

*SQLFluff* aims to be *opinionated* on this theme, but also *configurable*
(see :ref:`layoutconfig`). The tool will have a default viewpoint and will aim
to have views on all of the important aspects of SQL layout, but if you
(or your organisation) don't like those views then we aim to allow enough
configuration that you can lint in line with your views, and still use
*SQLFluff*. For more information on how to configure rules to your own
viewpoint see :ref:`config`.

.. note::

    This section of the docs handles the intent and reasoning behind how
    layout is handled by SQLFluff. For a deeper look at how this is achieved
    internally see :ref:`reflowinternals`.


Spacing
-------

Of the different elements of whitespace, spacing it likely the least
controversial. By default all elements are separated by a single space
character. Except for very specific circumstances (see section on
:ref:`alignedelements`), any additional space between elements is
usually unwanted and a distraction for the reader. There are however
several common cases where *no whitespace* is more appropriate, which
fall into two cases.

#. *No whitespace but a newline is allowed.* This option is configured
   using the :code:`touch` setting. The most common example of
   this is the spacing around commas. For example :code:`SELECT a , b`
   would be unusual and more normally be written :code:`SELECT a, b`.
   Inserting a newline between the :code:`a` and comma would not
   cause issues and may even be desired, for example:

   .. code-block:: sql

      SELECT
         col_a
         , col_b
         -- Newline present before column
         , col_c
         -- When inline, comma should still touch element before.
         , GREATEST(col_d, col_e) as col_f
      FROM tbl_a

#. *No whitespace and a newline is not allowed.* This option is
   configured using the :code:`inline` setting. The most common example
   of this is spacing within the parts of qualified identifier e.g.
   :code:`my_schema.my_table`. If a newline were present between the
   :code:`.` and either :code:`my_schema` or :code:`my_table`, then
   the expression would not parse and so no newlines should be allowed.


.. _alignedelements:

Aligned elements
^^^^^^^^^^^^^^^^

A special case of spacing is where elements are set to be aligned
within some limits. This is not enabled by default, but can be
be configured to achieve layouts like:

.. code-block:: sql

   SELECT
      a           AS first_column,
      b           AS second_column,
      (a + b) / 2 AS third_column
   FROM foo AS bar

In this example, the alias expressions are all aligned with each other.
Practically to configure this, SQLFluff needs to know what elements to
align and how far to search to find elements which should be aligned
with eachother. The configuration to achieve this layout is:

.. code-block:: ini

   [sqlfluff:layout:type:alias_expression]
   # We want non-default spacing _before_ the alias expressions.
   spacing_before = align
   # We want to align them within the next outer select clause.
   # This means for example that alias expressions within the FROM
   # or JOIN clause would _not_ be aligned with them.
   align_within = select_clause
   # The point at which to stop searching outward for siblings, which
   # in this example would likely be the boundary of a CTE. Stopping
   # when we hit brackets is usually a good rule of thumb for this
   # configuration.
   align_boundary = bracketed


Line Breaks
-----------

When controlling line breaks we are trying to achieve a few different things:

#. Do we have *enough* line breaks that *line length* doesn't become
   excessive. Long lines are hard to read, especially given that readers
   may be on varying screen sizes or have multiple windows open.

#. Are the positioning of *blank lines* (i.e. lines with nothing other
   than whitespace on them) appropriate. There are some circumstances
   where a blank line is *desired* (e.g. between CTEs). There are others
   where they are not, in particular *multiple blank lines*, for example
   at the beginning of a file.

#. Where we do have line breaks, are they positioned appropriately and
   consistently with regards to other elements around them. This is most
   common when it comes to *commas*, and whether they should be *leading*
   (e.g. :code:`, my_column`) or *trailing* (e.g. :code:`my_column,`). In
   less common cases it may also be desirable for some elements to have both
   and line break *before and after* (e.g. a set operator such as `UNION`).


Indentation
-----------

So, without further ado, here are the principles we think apply to indentation:

1. **For Keywords within a statement, the first root keyword of each line should be
   aligned.** For :code:`SELECT` statements, this means that :code:`SELECT`,
   :code:`FROM`, :code:`WHERE`, :code:`GROUP`, :code:`ORDER`, :code:`HAVING`
   and :code:`LIMIT`, should all have the same indent. Occasionally, it's
   actually more legible to have one-line or more compressed statements,
   and so additionally, if two (or more) of these keywords are on *the same*
   line, then the second (and any further) keywords won't raise a violation,
   provided that the *first* was correctly aligned.

   * This same logic applies to keywords within subsections, but the
     likelihood of them being on the same line to start is higher. one
     example of where this might occur regularly is within aggregate
     functions.

     .. code-block:: sql

         SELECT
            col_a,
            col_b,
            COUNT(*) as num,
            SUM(num) OVER (
               PARTITION BY col_a
               ORDER BY col_b
            ) as an_aggregate_function
         FROM tbl_a
         GROUP BY 1, 2

     Note that :code:`PARTITION` and :code:`ORDER` are both aligned on
     the same line. This also follows the rules around brackets described
     below.

2. **Line Length**. Long lines are hard to read and many SQL guidelines
   include a line length restriction. This is (of course) configurable, but
   the default is 80 characters (in line with the `dbt Labs SQL style guide`_.)

3. **Bracket behaviour**. For brackets there are three accepted ways:

   a. *Inline brackets*. Bracket expressions that start and end on the same line are
      fine (providing we don't fall foul of the line length rules above).

      .. code-block:: sql

         SELECT GREATEST(1, 6) AS col1 FROM my_table

   b. *Brackets with immediate linebreak*. If brackets are followed by an immediate
      line break (or at least with no other non-code elements after them on that
      line), then the following line should be indented +1 relative to the
      indent of the previous line. All elements of the bracketed block should
      be at this level of indent or deeper. The *closing* bracket of this block
      should have the same indent as the first element of the line containing
      the opening bracket.

      .. code-block:: sql

         SELECT GREATEST(
             1, 3, 7,
             6, 8, 9
         ) AS col1
         FROM my_table

   c. *Brackets with delayed linebreak*. If brackets are followed by content,
      and then a linebreak *before* the closing bracket, then we assume a
      *hanging* indent, where the following items of content should have the
      same indent as the first item of content. In this case, the *closing*
      bracket should come after the final element *on the same line*.

      .. code-block:: sql

         SELECT GREATEST(1, 6, 8,
                         6, 7) AS col1
         FROM my_table

4. **Comments** are dealt with differently, depending on whether they're
   *block* comments (:code:`/* like this */`), which might optionally
   include newlines, or *inline* comments (:code:`-- like this`) which
   are necessarily only on one line.

   a. *Block comments* cannot share a line with any code elements (so
      in effect they must start on their own new line), they cannot be
      followed by any code elements on the same line (and so in effect
      must be followed by a newline, if we are to avoid trailing
      whitespace). None of the lines within the block comment may have
      an indent less than the first line of the block comment (although
      additional indentation within a comment is allowed), and that first
      line should be aligned with the first code element *following*
      the block comment.

      .. code-block:: sql

         SELECT
            /* This is a block comment starting on a new line
            which contains a newline (continuing with at least
            the same indent.
               - potentially containing greater indents
               - having no other code following it in the same line
               - and aligned with the line of code following it */
            this_column as what_we_align_the_column_to
         FROM my_table

   b. *Inline comments* can be on the same line as other code, but are
      subject to the same line-length restrictions. If they don't fit
      on the same line (or if it just looks nicer) they can also be
      the only element on a line. In this latter case they should be
      aligned with the first code element *following* the comment.

      .. code-block:: sql

         SELECT
            -- This is fine
            this_column as what_we_align_to,
            another_column as something_short,  -- Is ok
            case
               -- This is aligned correctly with below
               when indented then take_care
               else try_harder
            end as the_general_guidance
         -- Even here we align with the line below
         FROM my_table

      .. note::

         When fixing issues with comment indentation, SQLFluff
         will attempt to keep comments in their original position
         but if line length concerns make this difficult, it will
         either abort the fix, or move *same line* comments up and
         *before* the line they are currently on. This is in line
         with the assumption that comments on their own line refer
         to the elements of code which they come *before*, not *after*.


.. _layoutconfig:

Configuring Layout
------------------

How indentation is linted is controlled in the rules, but what indentation
is expected to be present is controlled by the parser, and therefore
configured separately. One of the key areas for this is the indentation
of the :code:`JOIN` expression.

Semantically, a :code:`JOIN` expression is part of the :code:`FROM` expression
and therefore would be expected to be indented. However according to many
of the most common SQL style guides (including the `dbt Labs SQL style guide`_
and the `Mozilla SQL style guide`_) the :code:`JOIN` keyword is expected to at
the same indent as the :code:`FROM` keyword. By default, *SQLFluff* sides with
the current consensus, which is to *not* indent the :code:`JOIN` keyword,
however this is one element which is configurable.

By setting values in the :code:`sqlfluff:indentation` section of your config
file you can control how this is parsed.

For example, the default indentation would be as follows:

.. code-block:: sql

   SELECT
      a,
      b
   FROM my_table
   JOIN another_table
      ON condition1
         AND condition2

By setting your config file to:

.. code-block:: cfg

   [sqlfluff:indentation]
   indented_joins = True

Then the expected indentation will be:

.. code-block:: sql

   SELECT
      a,
      b
   FROM my_table
      JOIN another_table
         ON condition1
            AND condition2

There is a similar :code:`indented_using_on` config (defaulted to :code:`True`)
which can be set to :code:`False` to prevent the :code:`USING` or :code:`ON`
clause from being indented, in which case the original SQL would become:

.. code-block:: sql

   SELECT
      a,
      b
   FROM my_table
   JOIN another_table
   ON condition1
      AND condition2

There is also a similar :code:`indented_on_contents` config (defaulted to
:code:`True`) which can be set to :code:`False` to align any :code:`AND`
subsections of an :code:`ON` block with each other. If set to :code:`False`
the original SQL would become:

.. code-block:: sql

   SELECT
      a,
      b
   FROM my_table
   JOIN another_table
      ON condition1
      AND condition2

These can also be combined, so if :code:`indented_using_on` config is set to
:code:`False`, and :code:`indented_on_contents` is also set to :code:`False`
then the SQL would become:

.. code-block:: sql

   SELECT
      a,
      b
   FROM my_table
   JOIN another_table
   ON condition1
   AND condition2

There is also a similar :code:`indented_ctes` config (defaulted to
:code:`False`) which can be set to :code:`True` to enforce CTEs to be
indented within the :code:`WITH` clause:

.. code-block:: sql

   WITH
      some_cte AS (
         SELECT 1 FROM table1
      ),

      some_other_cte AS (
         SELECT 1 FROM table1
      )

   SELECT 1 FROM some_cte

By default, *SQLFluff* aims to follow the indentation most common approach
to indentation. However, if you have other versions of indentation which are
supported by published style guides, then please submit an issue on GitHub
to have that variation supported by *SQLFluff*.

.. _`dbt Labs SQL style guide`: https://github.com/dbt-labs/corp/blob/main/dbt_style_guide.md
.. _`Mozilla SQL style guide`: https://docs.telemetry.mozilla.org/concepts/sql_style.html#joins
.. _`Rule L018`: ./rules.html#sqlfluff.core.rules.Rule_L018
