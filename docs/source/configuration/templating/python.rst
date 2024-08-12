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
