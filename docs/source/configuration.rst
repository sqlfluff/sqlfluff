Configuration
=============

sqlfluff accepts configuration either through the command line or
through configuration files. There is *rough* parity between the
two approaches with the exception that *templating* configuration
must be done via a file, because it otherwise gets slightly complicated.

For details of what's available on the command line check out
the :ref:`cliref`.

For file based configuration *sqlfluff* will look for the following
files in order. Later files will (if found) will be used to overwrite
any vales read from earlier files.

- *setup.cfg*
- *tox.ini*
- *pep8.ini*
- *.sqlfluff*

Within these files, they will be read like an `cfg file`_, and *sqlfluff*
will look for sections which start with *sqlfluff*, and where subsections
are delimited by a semicolon. For example the *jinjacontext* section will
be indicated in the section started with *[sqlfluff:jinjacontext]*.

.. _`cfg file`: https://docs.python.org/3/library/configparser.html

Nesting
-------

**Sqlfluff** uses **nesting** in it's configuration files, with files
closer to the file being parsed being favoured over other config. The
following locations are checked:

1. The current user's home directory
2. The current working directory
3. *(if the file in question is in a subpath of the current working*
   *directory)* every directory in between
4. Any configuration passed at the command line is then used as a final
    overlay.

This whole structure leads to efficient configuration, in particular
in projects which utilise a lot of complicated templating.

.. _templateconfig:

Templating Configuration
------------------------

When thinking about templating there are two different kinds of things
that a user might want to fill into a templated file, *variables* and
*functions/macros*. Currently *functions* aren't implemented in any
of the templaters.

Variable Templating
^^^^^^^^^^^^^^^^^^^

Variables are available in the *jinja* and *python* templaters. By default
the templating engine will expect variables for templating to be available
in the config, and the templater will be look in the section corresponding
to the context for that templater. By convention, the config for the *jinja*
templater is found in the *sqlfluff:templater:jinja:context* section and the
config for the *python* templater is found in the
*sqlfluff:templater:python:context* section.

For example, if passed the following *.sql* file:

.. code-block:: sql

    SELECT {{ num_things }} FROM {{ tbl_name }} WHERE id > 10 LIMIT 5

...and the following configuration in *.sqlfluff* in the same directory:

.. code-block:: cfg

    [sqlfluff:templater:jinja:context]
    num_things=456
    tbl_name=my_table

...then before parsing, the sql will be transformed to:

.. code-block:: sql

    SELECT 456 FROM my_table WHERE id > 10 LIMIT 5

.. note::

    If there are variables in the template which cannot be found in
    the current configuration context, then this will raise a `SQLTemplatingError`
    and this will appear as a violation without a line number, quoting
    the name of the variable that couldn't be found.
