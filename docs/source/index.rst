📜 The SQL Linter for humans
============================

Bored of not having a good SQL linter that works with whichever dialect
you're working with? Fluff is an extensible and modular linter designed
to help you write good SQL and catch errors and bad SQL before it hits
your database.

.. note::

    **SQLFluff** is still in an open alpha phase - expect the tool to
    change significantly over the coming months, and expect potentially
    non-backward compatible api changes to happen at any point. In
    particular:

* **0.1.x** involved a major re-write of the parser, completely changing
  the behaviour of the tool with respect to complex parsing.
* **0.2.x** added templating support and a big restructure of rules
  and changed how users might interact with SQLFluff on templated code.
* **0.3.x** drops support for python 2.7 and 3.4, and also reworks the
  handling of indentation linting in a potentially not backward
  compatible way.

Want to see where and how people are using SQLFluff in their projects?
Head over to :ref:`inthewildref` for inspiration.

Getting Started
^^^^^^^^^^^^^^^

To get started just install the package, make a sql file and then run
SQLFluff and point it at the file. For more details or if you don't
have python or pip already installed see :ref:`gettingstartedref`.

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
   :caption: Documentation for SQLFluff:

   gettingstarted
   realworld
   vision
   teamrollout
   indentation
   rules
   dialects
   production
   configuration
   architecture
   cli
   api
   developingplugins
   inthewild
   jointhecommunity


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
