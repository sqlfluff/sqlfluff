.. _setting_config:

Setting Configuration
=====================

SQLFluff accepts configuration either through the command line or
through configuration files. There is *rough* parity between the
two approaches with the exception that *templating* configuration
must be done via a file, because it otherwise gets slightly complicated.

For details of what's available on the command line check out
the :ref:`cliref`.

.. _`config-files`:

Configuration Files
-------------------

For file based configuration *SQLFluff* will look for the following
files in order. Later files will (if found) will be used to overwrite
any values read from earlier files.

- :code:`setup.cfg`
- :code:`tox.ini`
- :code:`pep8.ini`
- :code:`.sqlfluff`
- :code:`pyproject.toml`

Within these files, the first four will be read like a `cfg file`_, and
*SQLFluff* will look for sections which start with :code:`sqlfluff`, and where
subsections are delimited by a semicolon. For example the *jinjacontext*
section will be indicated in the section started with
:code:`[sqlfluff:jinjacontext]`.

For example, a snippet from a :code:`.sqlfluff` file (as well as any of the
supported cfg file types):

.. code-block:: cfg

    [sqlfluff]
    templater = jinja
    sql_file_exts = .sql,.sql.j2,.dml,.ddl

    [sqlfluff:indentation]
    indented_joins = False
    indented_using_on = True
    template_blocks_indent = False

    [sqlfluff:templater]
    unwrap_wrapped_queries = True

    [sqlfluff:templater:jinja]
    apply_dbt_builtins = True

For the `pyproject.toml file`_, all valid sections start with
:code:`tool.sqlfluff` and subsections are delimited by a dot. For example the
*jinjacontext* section will be indicated in the section started with
:code:`[tool.sqlfluff.jinjacontext]`.

For example, a snippet from a :code:`pyproject.toml` file:

.. code-block:: toml

    [tool.sqlfluff.core]
    templater = "jinja"
    sql_file_exts = ".sql,.sql.j2,.dml,.ddl"

    [tool.sqlfluff.indentation]
    indented_joins = false
    indented_using_on = true
    template_blocks_indent = false

    [tool.sqlfluff.templater]
    unwrap_wrapped_queries = true

    [tool.sqlfluff.templater.jinja]
    apply_dbt_builtins = true

    # For rule specific configuration, use dots between the names exactly
    # as you would in .sqlfluff. In the background, SQLFluff will unpack the
    # configuration paths accordingly.
    [tool.sqlfluff.rules.capitalisation.keywords]
    capitalisation_policy = "upper"

.. _`cfg file`: https://docs.python.org/3/library/configparser.html
.. _`pyproject.toml file`: https://www.python.org/dev/peps/pep-0518/


.. _starter_config:

New Project Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^

When setting up a new project with SQLFluff, we recommend keeping your
configuration file fairly minimal. The config file should act as a form
of *documentation* for your team i.e. a record of what decisions you've
made which govern how your format your SQL. By having a more concise
config file, and only defining config settings where they differ from the
defaults - you are more clearly stating to your team what choices you've made.

*However*, there are also a few places where the *default* configuration
is designed more for *existing projects*, rather than *fresh projects*, and
so there is an opportunity to be a little stricter than you might otherwise
be with an existing codebase.

Here is a simple configuration file which would be suitable for a starter
project:

.. literalinclude:: /_partials/starter_config.cfg
   :language: cfg


.. _nesting:

Nesting
^^^^^^^

**SQLFluff** uses **nesting** in its configuration files, with files
closer *overriding* (or *patching*, if you will) values from other files.
That means you'll end up with a final config which will be a patchwork
of all the values from the config files loaded up to that path. The exception
to this is the value for `templater`, which cannot be set in config files in
subdirectories of the working directory.
You don't **need** any config files to be present to make *SQLFluff*
work. If you do want to override any values though SQLFluff will use
files in the following locations in order, with values from later
steps overriding those from earlier:

0. *[...and this one doesn't really count]* There's a default config as
   part of the SQLFluff package. You can find this below, in the
   :ref:`defaultconfig` section.
1. It will look in the user's os-specific app config directory.
   On macOS and Unix this is `~/.config/sqlfluff`, Windows is
   `<home>\\AppData\\Local\\sqlfluff\\sqlfluff`, for any of the filenames
   above in the main :ref:`setting_config` section. If multiple are present, they will
   *patch*/*override* each other in the order above.
2. It will look for the same files in the user's home directory (~).
3. *[if the current working directory is a subdirectory of the user's home directory (~)]*
   It will look for the same files in all directories between the
   user's home directory (~), and the current working directory.
4. It will look for the same files in the current working directory.
5. *[if parsing a file in a subdirectory of the current working directory]*
   It will look for the same files in every subdirectory between the
   current working dir and the file directory.
6. It will look for the same files in the directory containing the file
   being linted.

This whole structure leads to efficient configuration, in particular
in projects which utilise a lot of complicated templating.

.. _in_file_config:

In-File Configuration Directives
--------------------------------

In addition to configuration files mentioned above, SQLFluff also supports
comment based configuration switching in files. This allows specific SQL
file to modify a default configuration if they have specific needs.

When used, these apply to the whole file, and are parsed from the file in
an initial step before the rest of the file is properly parsed. This means
they can be used for both rule configuration and also for parsing
configuration.

To use these, the syntax must start as an *inline sql comment* beginning
with :code:`sqlfluff` (i.e. :code:`-- sqlfluff`). The line is then interpreted
as a colon-separated address of the configuration value you wish to set.
A few common examples are shown below:

.. code-block:: sql

    -- Set Indented Joins
    -- sqlfluff:indentation:indented_joins:True

    -- Set a smaller indent for this file
    -- sqlfluff:indentation:tab_space_size:2

    -- Set keywords to be capitalised
    -- sqlfluff:rules:capitalisation.keywords:capitalisation_policy:upper

    SELECT *
    FROM a
      JOIN b USING(c)

We recommend only using this configuration approach for configuration that
applies to one file in isolation. For configuration changes for areas of
a project or for whole projects we recommend :ref:`nesting` of configuration
files.
