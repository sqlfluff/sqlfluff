.. _templateconfig:

Templating Configuration
------------------------

This section explains how to configure templating for SQL files.

When writing SQL files, users might utilise some kind of templating.
The SQL file itself is written with placeholders which get rendered to proper
SQL at run time.
This can range from very simple placeholder templating to complex Jinja
templating.

SQLFluff supports templated sections in SQL, see :ref:`templater`.
This is achieved by the following set of operations:

1. SQLFluff pre-renders the templated SQL
2. SQLFluff applies the lint and fix operations to the rendered file
3. SQLFluff backports the rule violations to the templated section of the SQL.

SQLFluff does not automatically have access to the same environment used in
production template setup. This means it is necessary to either provide that
environment or provide dummy values to effectively render the template and
generate valid SQL. Refer to the templater sections below for details.

SQLFluff natively supports the following templating engines

- :ref:`jinja_templater`
- :ref:`placeholder_templater`
- :ref:`python_templater`

Also, SQLFluff has an integration to use :code:`dbt` as a templater.

- :ref:`dbt_templater` (via plugin which is covered in a different section).

.. note::

    Templaters may not be able to generate a rendered SQL that cover
    the entire raw file.

    For example, if the raw SQL uses a :code:`{% if condition %}` block,
    the rendered version of the template will only include either the
    :code:`{% then %}` or the :code:`{% else %}` block (depending on the
    provided configuration for the templater), but not both.

    In this case, because SQLFluff linting can only operate on the output
    of the templater, some areas of the raw SQL will never be seen by the
    linter and will not be covered by lint rules.

    This is functionality we hope to support in future.

.. toctree::
   :maxdepth: 2
   :caption: Templater Specific Configuration:

   jinja
   placeholder
   python
   dbt

.. _generic_variable_templating:

Generic Variable Templating
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Variables are available in all the templaters.
By default the templating engine will expect variables for templating to be
available in the config, and the templater will be look in the section
corresponding to the context for that templater. By convention, the config for
the ``jinja`` templater is found in the ``sqlfluff:templater:jinja:context``
section, the config for the ``python`` templater is found in the
``sqlfluff:templater:python:context`` section, the one for the ``placeholder``
templater is found in the ``sqlfluff:templater:placeholder:context`` section.

For example, if passed the following *.sql* file:

.. code-block:: SQL+Jinja

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
    the current configuration context, then this will raise a
    `SQLTemplatingError` and this will appear as a violation without
    a line number, quoting the name of the variable that couldn't be found.
