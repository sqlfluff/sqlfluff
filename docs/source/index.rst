📜 The SQL Linter for Humans
============================

Bored of not having a good SQL linter that works with whichever dialect
you're working with? Fluff is an extensible and modular linter designed
to help you write good SQL and catch errors and bad SQL before it hits
your database.

Notable releases:

* **1.0.x**: First *stable* release, no major changes to take advantage of a
  point of relative stability.
* **2.0.x**: Recode of rules, whitespace fixing consolidation,
  :code:`sqlfluff format` and removal of support for dbt versions pre `1.1`.
  Note, that this release brings with it some breaking changes to rule coding
  and configuration, see :ref:`upgrading_2_0`.
* **3.0.x**: :code:`sqlfluff fix` now defaults to *not* asking for confirmation
  and the `--force` option was removed. Richer information returned by the
  :code:`sqlfluff lint` command (although in a different structure to previous
  versions). See :ref:`upgrading_3_0`.
* **4.0.x**: First release with optional rust routines. An install with
  :code:`sqlfluff[rs]` will now include the rust routines. See :ref:`upgrading_4_0`.

For more detail on other releases, see our :ref:`releasenotes`.

Want to see where and how people are using SQLFluff in their projects?
Head over to :ref:`inthewildref` for inspiration.

Getting Started
^^^^^^^^^^^^^^^

To get started just install the package, make a sql file and then run
SQLFluff and point it at the file. For more details or if you don't
have python or pip already installed see :ref:`gettingstartedref`.

.. code-block:: text

    $ pip install sqlfluff
    $ echo "  SELECT a  +  b FROM tbl;  " > test.sql
    $ sqlfluff lint test.sql --dialect ansi
    == [test.sql] FAIL
    L:   1 | P:   1 | LT01 | Expected only single space before 'SELECT' keyword.
                           | Found '  '. [layout.spacing]
    L:   1 | P:   1 | LT02 | First line should not be indented.
                           | [layout.indent]
    L:   1 | P:   1 | LT13 | Files must not begin with newlines or whitespace.
                           | [layout.start_of_file]
    L:   1 | P:  11 | LT01 | Expected only single space before binary operator '+'.
                           | Found '  '. [layout.spacing]
    L:   1 | P:  14 | LT01 | Expected only single space before naked identifier.
                           | Found '  '. [layout.spacing]
    L:   1 | P:  27 | LT01 | Unnecessary trailing whitespace at end of file.
                           | [layout.spacing]
    L:   1 | P:  27 | LT12 | Files must end with a single trailing newline.
                           | [layout.end_of_file]
    All Finished 📜 🎉!

Contents
^^^^^^^^

.. toctree::
   :maxdepth: 3
   :caption: Documentation for SQLFluff:

   gettingstarted
   why_sqlfluff
   guides/index
   configuration/index
   production/index
   reference/index
   inthewild
   jointhecommunity


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
