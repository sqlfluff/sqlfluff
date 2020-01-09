📜 ✒️ ✨ The SQL Linter for humans
===================================

Bored of not having a good SQL linter that works with whichever dialiect
you're working with? Fluff is an extensible and modular linter designed
to help you write good SQL and catch errors and bad SQL before it hits
your database.

.. note::

    **Sqlfluff** is still in an open alpha phase - expect the tool to
    change significantly over the coming months, and expect potentially
    non-backward compatable api changes to happen at any point. In
    particular moving from 0.0.x to 0.1.x introduced some non backward
    compatible changes and potential loss in functionality.

Getting Started
^^^^^^^^^^^^^^^

To get started just install the package, make a sql file and then run
sqlfluff and point it at the file.

.. code-block:: bash

    $ pip install sqlfluff
    $ echo "  SELECT a  +  b FROM tbl;  " > test.sql
    $ sqlfluff lint test.sql
    == [test.sql] FAIL
    L:   1 | P:   1 | L003 | Single indentation uses a number of spaces not a multiple of 4
    L:   1 | P:  14 | L006 | Operators should be surrounded by a single space unless at the start/end of a line
    L:   1 | P:  27 | L001 | Unnecessary trailing whitespace

Contents
^^^^^^^^

.. toctree::
   :maxdepth: 3
   :caption: Documentation for sqlfluff:

   realworld
   indentation
   rules
   production
   configuration
   architecture
   cli


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
