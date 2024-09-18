.. _python_templater:

Python templater
^^^^^^^^^^^^^^^^

Uses native Python f-strings. As described in
:ref:`generic_variable_templating`, an example usage would look be
configured as follows:

If passed the following *.sql* file:

.. code-block::

    SELECT * FROM {tbl_name}

...and the following configuration in *.sqlfluff* in the same directory:

.. code-block:: cfg

    [sqlfluff]
    templater = python

    [sqlfluff:templater:python:context]
    tbl_name = my_table

...then before parsing, the sql will be transformed to:

.. code-block:: sql

    SELECT * FROM my_table


Complex Python Variable Templating
""""""""""""""""""""""""""""""""""""

`Python string formatting`_ supports accessing object attributes
via dot notation (e.g. :code:`{foo.bar}`).  However, since we cannot create Python
objects within configuration files, we need a workaround in order to provide
dummy values to render templates containing these values.  The SQLFluff
python templater will interpret any variable containing a "." as a
dictionary lookup on the *magic* fixed context key :code:`sqlfluff`.

.. code-block::

    -- this SQL
    SELECT * FROM {foo.bar}

    -- becomes this
    SELECT * FROM {sqlfluff["foo.bar"]}

..which can be populated using the following configuration:

.. code-block:: cfg

    [sqlfluff:templater:python:context]
    sqlfluff = {"foo.bar": "abc"}

.. _`Python string formatting`: https://docs.python.org/3/library/string.html#format-string-syntax
