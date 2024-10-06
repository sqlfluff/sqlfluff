.. _guides:

Guides & How-tos
================

This section is of short guides and articles is meant to be read alongside
the rest of the documentation which is more reference-oriented.

Setting up SQLFluff
-------------------

.. toctree::
   :maxdepth: 1

   setup/teamrollout

Troubleshooting SQLFluff
------------------------

.. _development:

Contributing to SQLFluff
------------------------

It is recommended that the following is read in conjunction with exploring
the codebase. `dialect_ansi.py`_ in particular is helpful to understand the
recursive structure of segments and grammars.

You may also need to reference the :ref:`internal_api_docs`.

.. _`dialect_ansi.py`: https://github.com/sqlfluff/sqlfluff/blob/main/src/sqlfluff/dialects/dialect_ansi.py

.. toctree::
   :maxdepth: 1

   contributing/architecture
   contributing/dialect
   contributing/rules
   contributing/plugins
   contributing/docs
