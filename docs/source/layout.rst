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

Of the different elements of whitespace, spacing is likely the least
controversial. By default, all elements are separated by a single space
character. Except for very specific circumstances (see section on
:ref:`alignedelements`), any additional space between elements is
usually unwanted and a distraction for the reader. There are however
several common cases where *no whitespace* is more appropriate, which
fall into two cases (for more details on where to configure these see
:ref:`layoutspacingconfig`).

#. *No whitespace but a newline is allowed.* This option is configured
   using the :code:`touch` option in the :code:`spacing_*` configuration
   settings. The most common example of this is the spacing around commas.
   For example :code:`SELECT a , b` would be unusual and more normally be
   written :code:`SELECT a, b`. Inserting a newline between the :code:`a`
   and comma would not cause issues and may even be desired, for example:

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
   configured using the :code:`inline` option in the :code:`spacing_*`
   configuration settings. The most common example of this is spacing
   within the parts of qualified identifier e.g. :code:`my_schema.my_table`.
   If a newline were present between the :code:`.` and either
   :code:`my_schema` or :code:`my_table`, then the expression would not
   parse and so no newlines should be allowed.


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
To configure this, SQLFluff needs to know what elements to
align and how far to search to find elements which should be aligned
with each other. The configuration to achieve this layout is:

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
   align_scope = bracketed

Of these configuration values, the :code:`align_scope` is potentially
the least obvious. The following example illustrates the impact it has.

.. code-block:: sql

   -- With
   --    align_scope = bracketed
   --    align_within = select_clause

   WITH foo as (
      SELECT
         a,
         b,
         c     AS first_column
         d + e AS second_column
   )

   SELECT
      a           AS first_column,
      (a + b) / 2 AS third_column
   FROM foo AS bar;

   -- With
   --    align_scope = bracketed
   --    align_within = statement

   WITH foo as (
      SELECT
         a,
         b,
         c     AS first_column
         d + e AS second_column
   )

   SELECT
      a           AS first_column,
      (a + b) / 2 AS third_column
   FROM foo       AS bar            -- Now the FROM alias is also aligned.

   -- With
   --    align_scope = file
   --    align_within = select_clause

   WITH foo as (
      SELECT
         a,
         b,
         c        AS first_column   -- Now the aliases here are aligned
         d + e    AS second_column  -- with the outer query.
   )

   SELECT
      a           AS first_column,
      (a + b) / 2 AS third_column
   FROM foo AS bar

   -- With
   --    align_scope = file
   --    align_within = statement

   WITH foo as (
      SELECT
         a,
         b,
         c        AS first_column
         d + e    AS second_column
   )

   SELECT
      a           AS first_column,
      (a + b) / 2 AS third_column
   FROM foo       AS bar


Line Breaks
-----------

When controlling line breaks, we are trying to achieve a few different things:

#. Do we have *enough* line breaks that *line length* doesn't become
   excessive. Long lines are hard to read, especially given that readers
   may be on varying screen sizes or have multiple windows open. This is
   (of course) configurable, but the default is 80 characters (in line with
   the `dbt Labs SQL style guide`_.)

#. Is the positioning of *blank lines* (i.e. lines with nothing other
   than whitespace on them) appropriate. There are some circumstances
   where a blank line is *desired* (e.g. between CTEs). There are others
   where they are not, in particular *multiple blank lines*, for example
   at the beginning of a file.

#. Where we do have line breaks, are they positioned appropriately and
   consistently with regards to other elements around them. This is most
   common when it comes to *commas*, and whether they should be *leading*
   (e.g. :code:`, my_column`) or *trailing* (e.g. :code:`my_column,`). In
   less common cases, it may also be desirable for some elements to have both
   a line break *before and after* (e.g. a set operator such as `UNION`).


Indentation
-----------

Lastly, given we have multiple lines of SQL, to what extent should we indent
some lines to provide visual cues to the structure of that SQL. It's
important to note that SQL is *not* whitespace sensitive in its
interpretation and that means that any principles we apply here are entirely
for the benefit of humans. *Your database doesn't care*.

The indentation therefore should be treated as a *hint* to the reader of
the structure of the code. This explains the common practice within most
languages that nested elements (for example the contents of a set of brackets
in a function call) should be indented one step from the outer elements. It's
also convention that elements *with the same level* in a nested structure
should have *the same indentation*, at least with regards to their local
surroundings. As an example:

.. code-block:: sql

   SELECT
      nested_within_select AS first_column,
      some_function(
         nested_within_function,
         also_nested_within_function
      ) AS indented_the_same_as_opening_bracket
   FROM indented_the_same_as_select

Comment Indents
^^^^^^^^^^^^^^^

.. note::

      The notes here about block comments are not implemented prior
      to 2.0.x. They should be coming in that release or soon after.


**Comments** are dealt with differently, depending on whether they're
*block* comments (:code:`/* like this */`), which might optionally
include newlines, or *inline* comments (:code:`-- like this`) which
are necessarily only on one line.

*  *Block comments* cannot share a line with any code elements (so
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

*  *Inline comments* can be on the same line as other code, but are
   subject to the same line-length restrictions. If they don't fit
   on the same line (or if it just looks nicer) they can also be
   the only element on a line. In this latter case, they should be
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
      either abandon the fix, or move *same line* comments up and
      *before* the line they are currently on. This is in line
      with the assumption that comments on their own line refer
      to the elements of code which they come *before*, not *after*.


.. _hangingindents:

Hanging Indents
^^^^^^^^^^^^^^^

One approach to indenting nested elements is a layout called a
*hanging indent*. In this layout, there is no line break before the
first nested element, but subsequent elements are indented to
match the line position of that first element. Two examples might be:

.. code-block:: sql

   -- A select statement with two hanging indents:
   SELECT no_line_break_before_me,
          indented_to_match_the_first,
          1 + (a
               + b) AS another_more_complex_example
   FROM my_table;

   -- This TSQL example is also in essence a hanging indent:
   DECLARE @prv_qtr_1st_dt DATETIME,
           @last_qtr INT,
           @last_qtr_first_mn INT,
           @last_qtr_yr INT;

In some circumstances this layout can be quite neat (the
:code:`DECLARE` statement is a good example of this), however
once indents are nested or indentation styles are mixed it
can rapidly become confusing (as partially shown in the first
example). Additionally, unless the leading element of the first
line is very short, hanging indents use much *larger indents*
than a traditional simple indent where a line break is used before
the first element.

Hanging indents have been supported in SQLFluff up to the 1.x
versions, however **they will no longer by supported from 2.0.0**
onwards. This is due to the ambiguity which they bring to
fixing poorly formatted SQL. Take the following code:

.. code-block:: sql

   SELECT   this_is,
   badly_formatted, code_and,
      not_obvious,
         what_was,
   intended FROM my_table

Given the lack of line break between :code:`SELECT` and
:code:`this_is`, it would appear that the user is intending
a hanging indent, however it is also plausible that they did
not and they just forgot to add a line break between them.
This ambiguity is unhelpful, both for SQLFluff as a tool,
but also for people who write SQL that there two ways of
indenting their SQL. Given SQLFluff aims to provide consistency
in SQL layout and remove some of the burden of needing to make
choices like this - and that it would be very unusual to keep
*only hanging indents and disable traditional ones* - the only
route left to consistency is to **not allow hanging indents**.
Starting in 2.0.0, any hanging indents detected will be
converted to traditional indents.

.. _templatedindents:

Templated Indents
^^^^^^^^^^^^^^^^^

SQLFluff supports templated elements in code, such as those
offered by jinja2 (or dbt which relies on it). For simple
cases, templated elements are handled as you would expect
by introducing additional indents into the layout.

.. code-block:: SQL+Jinja

   SELECT
      a,
      {% for n in ['b', 'c', 'd'] %}
         -- This section is indented relative to 'a' because
         -- it is inside a jinja for loop.
         {{ n }},
      {% endfor %}
      e
   FROM my_table

This functionality can be turned off if you wish using the
:code:`template_blocks_indent` option in your :ref:`config`.

It's important to note here, that SQLFluff lints the code after
it has been rendered, and so only has access to code which is
still present after that process.

.. code-block:: SQL+Jinja

   SELECT
      a,
      {% if False %}
      -- This section of the code cannot be linted because
      -- it is never rendered due to the `if False` condition.
      my    + poorly
         +   spaced - and/indented AS    section_of_code
      {% endif %}
      e
   FROM my_table

More complex templated cases are usually characterised by templated
tags *cutting across the parse tree*. This more formally is where the
opening and closing tags of a templated section exist at different
levels in the parsed structure. Starting in version 2.x, these will
be treated differently (Prior to version 2.x, situations like this were sometimes
handled inconsistently or incorrectly).

Indentation should act as a visual cue to the structure of the
written SQL, and as such, the most important thing is that template tags
belonging to the same block structure use the same indentation.
In the example below, this is the opening and closing elements of the
second :code:`if` statement. If treated as a simple case, these tags
would have different indents, because they are at different levels of
the parse tree and so clearly there is a conflict to be resolved.

The view SQLFluff takes on how to resolve this conflict is to pull
all of the tags in this section down to the indent of the
*least indented* (in the example below that would be the closing
:code:`endif` tag). This is similar to the treatment of
`C Preprocessor Directives`_, which are treated somewhat as being
outside the structure of the rest of the file. In these cases,
the content is also *not further indented* as in the simple case
because it makes it harder to line up elements within the affected
section and outside (in the example below the :code:`SELECT` and
:code:`FROM` are a good illustration).

.. code-block:: SQL+Jinja

   SELECT
      a,
      {% if True %}
         -- This is a simple case. The opening and closing tag are
         -- both at the same level within the SELECT clause.
         simple_case AS example,
      {% endif %}
      b,
   {% if True %}
      -- This is a complex case. The opening tag is within the SELECT
      -- clause, but the closing tag is outside the statement
      -- entirely.
      complex_case AS example
   FROM table_option_one
   {% else %
      complex_case_two AS example
   FROM table_option_two
   {% endif %}


.. _layoutconfig:

Configuring Layout
------------------

Configuration for layout is spread across three places:

#. Indent behavior for particular dialect elements is controlled by the parser.
   This is because in the background SQLFluff inserts :code:`Indent`
   and :code:`Dedent` tokens into the parse tree where those things
   are expected. For more detail see :ref:`layoutindentconfig`.

#. Configuration for the spacing and line position of particular
   types of element (such as commas or operators) is set in the
   :code:`layout` section of the config file. For more detail see
   :ref:`layoutspacingconfig`.

#. Some elements of layout are still controlled by rules directly.
   These are usually very specific cases, see :ref:`ruleref` for
   more details.


.. _layoutindentconfig:

Configuring indent locations
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

One of the key areas for this is the indentation of the
:code:`JOIN` expression, which we'll use as an example.

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

By default, *SQLFluff* aims to follow the most common approach
to indentation. However, if you have other versions of indentation which are
supported by published style guides, then please submit an issue on GitHub
to have that variation supported by *SQLFluff*.

.. _layoutspacingconfig:

Configuring layout and spacing
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :code:`[sqlfluff:layout]` section of the config controls the treatment of
spacing and line breaks across all rules. The syntax of this section is very
expressive; however in normal use, only very small alterations should be
necessary from the :ref:`defaultconfig`.

The syntax of the section headings here select by *type*, which corresponds
to the :code:`type` defined in the dialect. For example the following section
applies to elements of the *type* :code:`comma`, i.e. :code:`,`.

.. code-block:: cfg

   [sqlfluff:layout:type:comma]
   spacing_before = touch
   line_position = trailing

Within these configurable sections there are a few key elements which are
available:

*  **Spacing Elements**: :code:`spacing_before`, :code:`spacing_after` and
   :code:`spacing_within`. For each of these options, there are a few possible
   settings:

   *  The default spacing for all elements is :code:`single` unless otherwise
      specified. In this state, elements will be spaced with a single space
      character unless there is a line break between them.

   *  The value of :code:`touch` allows line breaks, but if no line break is
      present, then no space should be present. A great example of this is
      the spacing before commas (as shown in the config above), where line
      breaks may be allowed, but if not they should *touch* the element before.

   *  The value of :code:`inline` is effectively the same as :code:`touch`
      but in addition, no line breaks are allowed. This is best illustrated
      by the spacing found in a qualified identifier like
      :code:`my_schema.my_table`.

*  **Line Position**: set using the :code:`line_position` option. By default
   this is unset, which implies no particular line position requirements. The
   available options are:

   *  :code:`trailing` and :code:`leading`, which are most common in the
      placement of commas. Both of these settings *also* allow the option
      of a comma on its own on a line, or in the middle of a line, *but*
      if there is a line break on *either side* then they make sure it's
      on the *correct side*. By default we assume *trailing* commas, but if
      you (or your organisation) have settled on *leading* commas then
      you should add the following section to your config:

      .. code-block:: cfg

         [sqlfluff:layout:type:comma]
         line_position = leading

   *  :code:`alone`, which means if there is a line break on either side,
      then there must be a line break on *both sides* (i.e. that it should
      be the only thing on that line.

   *  All of the above options can be qualified with the :code:`:strict`
      modifier - which prevents the *inline* case. For example:

      .. code-block:: sql

         -- Setting line_position to just `alone`
         -- within [sqlfluff:layout:type:set_operator]
         -- would not allow:
         SELECT a
         UNION SELECT b;
         -- ...or...
         SELECT a UNION
         SELECT b;
         -- but *would* allow both of the following:
         SELECT a UNION SELECT b;
         SELECT a
         UNION
         SELECT b;

         -- However the default is set to `alone:strict`
         -- then the *only* acceptable configuration is:
         SELECT a
         UNION
         SELECT b;


.. _`C Preprocessor Directives`: https://www.cprogramming.com/reference/preprocessor/
.. _`dbt Labs SQL style guide`: https://github.com/dbt-labs/corp/blob/main/dbt_style_guide.md
.. _`Mozilla SQL style guide`: https://docs.telemetry.mozilla.org/concepts/sql_style.html#joins
