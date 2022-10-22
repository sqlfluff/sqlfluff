.. _config:

Configuration
=============

SQLFluff accepts configuration either through the command line or
through configuration files. There is *rough* parity between the
two approaches with the exception that *templating* configuration
must be done via a file, because it otherwise gets slightly complicated.

For details of what's available on the command line check out
the :ref:`cliref`.

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
    indented_joins = false
    indented_using_on = true
    template_blocks_indent = false

    [sqlfluff:templater]
    unwrap_wrapped_queries = true

    [sqlfluff:templater:jinja]
    apply_dbt_builtins = true

For the `pyproject.toml file`_, all valid sections start with
:code:`tool.sqlfluff` and subsections are delimited by a dot. For example the
*jinjacontext* section will be indicated in the section started with
:code:`[tool.sqlfluff.jinjacontext]`.

For example, a snippet from a :code:`pyproject.toml` file:

.. code-block:: cfg

    [tool.sqlfluff.core]
    templater = jinja
    sql_file_exts = .sql,.sql.j2,.dml,.ddl

    [tool.sqlfluff.indentation]
    indented_joins = false
    indented_using_on = true
    template_blocks_indent = false

    [tool.sqlfluff.templater]
    unwrap_wrapped_queries = true

    [tool.sqlfluff.templater.jinja]
    apply_dbt_builtins = true

.. _`cfg file`: https://docs.python.org/3/library/configparser.html
.. _`pyproject.toml file`: https://www.python.org/dev/peps/pep-0518/

.. _nesting:

Nesting
-------

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
1. It will look in the user's os-specific app config directory. On OSX this is
   `~/Library/Preferences/sqlfluff`, Unix is `~/.config/sqlfluff`, Windows is
   `<home>\\AppData\\Local\\sqlfluff\\sqlfluff`, for any of the filenames
   above in the main :ref:`config` section. If multiple are present, they will
   *patch*/*override* each other in the order above.
2. It will look for the same files in the user's home directory (~).
3. It will look for the same files in the current working directory.
4. *[if parsing a file in a subdirectory of the current working directory]*
   It will look for the same files in every subdirectory between the
   current working dir and the file directory.
5. It will look for the same files in the directory containing the file
   being linted.

This whole structure leads to efficient configuration, in particular
in projects which utilise a lot of complicated templating.

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
as a colon-seperated address of the configuation value you wish to set.
A few common examples are shown below:

.. code-block:: sql

    -- Set Indented Joins
    -- sqlfluff:indentation:indented_joins:true
    -- Set a smaller indent for this file
    -- sqlfluff:indentation:tab_space_size:2
    -- Set keywords to be capitalised
    -- sqlfluff:rules:L010:capitalisation_policy:upper

    SELECT *
    FROM a
      JOIN b USING(c)

We recommend only using this configuration approach for configuration that
applies to one file in isolation. For configuration changes for areas of
a project or for whole projects we recommend :ref:`nesting` of configuration
files.

.. _ruleconfig:

Rule Configuration
------------------

Rules can be configured with the :code:`.sqlfluff` config files.

Common rule configurations can be set in the :code:`[sqlfluff:rules]` section.

For example:

.. code-block:: cfg

   [sqlfluff:rules]
   tab_space_size = 4
   max_line_length = 80
   indent_unit = space
   allow_scalar = True
   single_table_references = consistent
   unquoted_identifiers_policy = all

Rule specific configurations are set in rule specific subsections.

For example, enforce that keywords are upper case by configuring the rule
:class:`L010 <sqlfluff.core.rules.Rule_L010>`:

.. code-block:: cfg

    [sqlfluff:rules:L010]
    # Keywords
    capitalisation_policy = upper

All possible options for rule sections are documented in :ref:`ruleref`.

For an overview of the most common rule configurations that you may want to
tweak, see `Default Configuration`_ (and use :ref:`ruleref` to find the
available alternatives).

Enabling and Disabling Rules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To disable individual rules, set :code:`exclude_rules` in the top level section
of sqlfluff configuration. The value is a comma separated list of rule ids.

For example, to disable the rules :class:`L022 <sqlfluff.core.rules.Rule_L022>`
and :class:`L027 <sqlfluff.core.rules.Rule_L027>`:

.. code-block:: cfg

    [sqlfluff]
    exclude_rules = L022, L027

To enable individual rules, configure :code:`rules`, respectively.

For example, to enable :class:`L027 <sqlfluff.core.rules.Rule_L027>`:

.. code-block:: cfg

    [sqlfluff]
    rules = L027

If both :code:`exclude_rules` and :code:`rules` have non-empty value, then the
excluded rules are removed from the rules list. This allows for example
enabling common rules on top level but excluding some on subdirectory level.

Rules can also be enabled/disabled by their grouping. Right now, the only
rule grouping is :code:`core`. This will enable (or disable) a select group
of rules that have been deemed 'core rules'.

.. code-block:: cfg

    [sqlfluff]
    rules = core

More information about 'core rules' can be found in the :ref:`ruleref`.

Additionally, some rules have a special :code:`force_enable` configuration
option, which allows to enable the given rule even for dialects where it is
disabled by default. The rules that support this can be found in the
:ref:`ruleref`.

The default values can be seen in `Default Configuration`_.

See also: `Ignoring Errors & Files`_.


Layout & Spacing Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :code:`[sqlfluff:layout]` section of the config controls the
treatment of spacing and line breaks across all rules. To understand
more about this section, see the section of the docs dedicated to
layout: :ref:`layoutconfig`.


.. _templateconfig:

Jinja Templating Configuration
------------------------------

When thinking about Jinja templating there are two different kinds of things
that a user might want to fill into a templated file, *variables* and
*functions/macros*. Currently *functions* aren't implemented in any
of the templaters.

Variable Templating
^^^^^^^^^^^^^^^^^^^

Variables are available in the *jinja*, *python* and *placeholder* templaters.
By default the templating engine will expect variables for templating to be
available in the config, and the templater will be look in the section
corresponding to the context for that templater. By convention, the config for
the *jinja* templater is found in the *sqlfluff:templater:jinja:context
section, the config for the *python* templater is found in the
*sqlfluff:templater:python:context* section, the one for the *placeholder*
templater is found in the *sqlfluff:templater:placeholder:context* section

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
    the current configuration context, then this will raise a `SQLTemplatingError`
    and this will appear as a violation without a line number, quoting
    the name of the variable that couldn't be found.

Placeholder templating
^^^^^^^^^^^^^^^^^^^^^^

Libraries such as SQLAlchemy or Psycopg use different parameter placeholder
styles to mark where a parameter has to be inserted in the query.

For example a query in SQLAlchemy can look like this:

.. code-block:: sql

    SELECT * FROM table WHERE id = :myid

At runtime `:myid` will be replace by a value provided by the application and
escaped as needed, but this is not standard SQL and cannot be parsed as is.

In order to parse these queries is then necessary to replace these
placeholders with sample values, and this is done with the placeholder
templater.

Placeholder templating can be enabled in the config using:

.. code-block:: cfg

    [sqlfluff]
    templater = placeholder

A few common styles are supported:

.. code-block:: sql
   :force:

    -- colon
    WHERE bla = :my_name

    -- colon_nospaces
    -- (use with caution as more prone to false positives)
    WHERE bla = table:my_name

    -- numeric_colon
    WHERE bla = :2

    -- pyformat
    WHERE bla = %(my_name)s

    -- dollar
    WHERE bla = $my_name or WHERE bla = ${my_name}

    -- question_mark
    WHERE bla = ?

    -- numeric_dollar
    WHERE bla = $3 or WHERE bla = ${3}

    -- percent
    WHERE bla = %s

    -- ampersand
    WHERE bla = &s or WHERE bla = &{s} or USE DATABASE MARK_{ENV}

These can be configured by setting `param_style` to the names above:

.. code-block:: cfg

    [sqlfluff:templater:placeholder]
    param_style = colon
    my_name = 'john'

then it is necessary to set sample values for each parameter, like `my_name`
above. Notice that the value needs to be escaped as it will be replaced as a
string during parsing.

When parameters are positional, like `question_mark`, then their name is
simply the order in which they appear, starting with `1`.

.. code-block:: cfg

    [sqlfluff:templater:placeholder]
    param_style = question_mark
    1 = 'john'

In case you need a parameter style different from the ones above, you can pass
a custom regex.

.. code-block:: cfg

    [sqlfluff:templater:placeholder]
    param_regex = __(?P<param_name>[\w_]+)__
    my_name = 'john'

N.B. quotes around `param_regex` in the config are
interpreted literally by the templater.
e.g. `param_regex='__(?P<param_name>[\w_]+)__'` matches
`'__some_param__'` not `__some_param__`

the named parameter `param_name` will be used as the key to replace, if
missing, the parameter is assumed to be positional and numbers are used
instead.

Also consider making a pull request to the project to have your style added,
it may be useful to other people and simplify your configuration.

Complex Variable Templating
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Two more advanced features of variable templating are *case sensitivity*
and *native python types*. Both are illustrated in the following example:

.. code-block:: cfg

    [sqlfluff:templater:jinja:context]
    my_list = ['a', 'b', 'c']
    MY_LIST = ("d", "e", "f")
    my_where_dict = {"field_1": 1, "field_2": 2}

.. code-block:: SQL+Jinja

    SELECT
        {% for elem in MY_LIST %}
            '{{elem}}' {% if not loop.last %}||{% endif %}
        {% endfor %} as concatenated_list
    FROM tbl
    WHERE
        {% for field, value in my_where_dict.items() %}
            {{field}} = {{value}} {% if not loop.last %}and{% endif %}
        {% endfor %}

...will render as...

.. code-block:: sql

    SELECT
        'd' || 'e' || 'f' as concatenated_list
    FROM tbl
    WHERE
        field_1 = 1 and field_2 = 2

Note that the variable was replaced in a case sensitive way and that the
settings in the config file were interpreted as native python types.

Macro Templating
^^^^^^^^^^^^^^^^

Macros (which also look and feel like *functions* are available only in the
*jinja* templater. Similar to `Variable Templating`_, these are specified in
config files, what's different in this case is how they are named. Similar to
the *context* section above, macros are configured separately in the *macros*
section of the config. Consider the following example.

If passed the following *.sql* file:

.. code-block:: SQL+Jinja

    SELECT {{ my_macro(6) }} FROM some_table

...and the following configuration in *.sqlfluff* in the same directory (note
the tight control of whitespace):

.. code-block:: cfg

    [sqlfluff:templater:jinja:macros]
    a_macro_def = {% macro my_macro(n) %}{{ n }} + {{ n * 2 }}{% endmacro %}

...then before parsing, the sql will be transformed to:

.. code-block:: sql

    SELECT 6 + 12 FROM some_table

Note that in the code block above, the variable name in the config is
*a_macro_def*, and this isn't apparently otherwise used anywhere else.
Broadly this is accurate, however within the configuration loader this will
still be used to overwrite previous *values* in other config files. As such
this introduces the idea of config *blocks* which could be selectively
overwritten by other configuration files downstream as required.

In addition to macros specified in the config file, macros can also be
loaded from files or folders. This is specified in the config file:

.. code-block:: cfg

    [sqlfluff:templater:jinja]
    load_macros_from_path = my_macros

``load_macros_from_path`` is a comma-separated list of :code:`.sql` files or
folders. Locations are *relative to the config file*. For example, if the
config file above was found at :code:`/home/my_project/.sqlfluff`, then
SQLFluff will look for macros in the folder :code:`/home/my_project/my_macros/`
(but not subfolders). Any macros defined in the config will always take
precedence over a macro defined in the path.

* :code:`.sql` files: Macros in these files are available in every :code:`.sql`
  file without requiring a Jinja :code:`include` or :code:`import`.
* Folders: To use macros from the :code:`.sql` files in folders, use Jinja
  :code:`include` or :code:`import` as explained below.

**Note:** The :code:`load_macros_from_path` setting also defines the search
path for Jinja
`include <https://jinja.palletsprojects.com/en/3.0.x/templates/#include>`_ or
`import <https://jinja.palletsprojects.com/en/3.0.x/templates/#import>`_.
Unlike with macros (as noted above), subdirectories are supported. For example,
if :code:`load_macros_from_path` is set to :code:`my_macros`, and there is a
file :code:`my_macros/subdir/my_file.sql`, you can do:

.. code-block:: jinja

   {% include 'subdir/include_comment.sql' %}

.. note::

    Throughout the templating process **whitespace** will still be treated
    rigorously, and this includes **newlines**. In particular you may choose
    to provide *dummy* macros in your configuration different from the actual
    macros used in production.

    **REMEMBER:** The reason SQLFluff supports macros is to *enable* it to parse
    templated sql without it being a blocker. It shouldn't be a requirement that
    the *templating* is accurate - it only needs to work well enough that
    *parsing* and *linting* are helpful.

Builtin Macro Blocks
^^^^^^^^^^^^^^^^^^^^

One of the main use cases which inspired *SQLFluff* as a project was `dbt`_.
It uses jinja templating extensively and leads to some users maintaining large
repositories of sql files which could potentially benefit from some linting.

.. note::
    *SQLFluff* has now a tighter integration with dbt through the "dbt" templater.
    It is the recommended templater for dbt projects. If used, it eliminates the
    need for the overrides described in this section.

    To use the dbt templater, go to `dbt Project Configuration`_.

*SQLFluff* anticipates this use case and provides some built in macro blocks
in the `Default Configuration`_ which assist in getting started with `dbt`_
projects. In particular it provides mock objects for:

* *ref*: The mock version of this provided simply returns the model reference
  as the name of the table. In most cases this is sufficient.
* *config*: A regularly used macro in `dbt`_ to set configuration values. For
  linting purposes, this makes no difference and so the provided macro simply
  returns nothing.

.. note::
    If there are other builtin macros which would make your life easier,
    consider submitting the idea (or even better a pull request) on `github`_.

.. _`dbt`: https://www.getdbt.com/
.. _`github`: https://www.github.com/sqlfluff/sqlfluff

Interaction with ``--ignore=templating``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Ignoring Jinja templating errors provides a way for users to use SQLFluff
while reducing or avoiding the need to spend a lot of time adding variables
to ``[sqlfluff:templater:jinja:context]``.

When ``--ignore=templating`` is enabled, the Jinja templater behaves a bit
differently. This additional behavior is *usually* but not *always* helpful
for making the file at least partially parsable and fixable. It definitely
doesn’t **guarantee** that every file can be fixed, but it’s proven useful for
some users.

Here's how it works:

* Within the expanded SQL, undefined variables are automatically *replaced*
  with the corresponding string value.
* If you do: ``{% include query %}``, and the variable ``query`` is not
  defined, it returns a “file” containing the string ``query``.
* If you do: ``{% include "query_file.sql" %}``, and that file does not exist
  or you haven’t configured a setting for ``load_macros_from_path``, it
  returns a “file” containing the text ``query_file``.

For example:

.. code-block:: SQL+Jinja

   select {{ my_variable }}
   from {% include "my_table.sql" %}

is interpreted as:

.. code-block:: sql

   select my_variable
   from my_table

The values provided by the Jinja templater act *a bit* (not exactly) like a
mixture of several types:

* ``str``
* ``int``
* ``list``
* Jinja's ``Undefined`` `class <https://jinja.palletsprojects.com/en/3.0.x/api/#jinja2.Undefined>`_

Because the values behave like ``Undefined``, it's possible to replace them
using Jinja's ``default()`` `filter <https://jinja.palletsprojects.com/en/3.1.x/templates/#jinja-filters.default>`_.
For example:

.. code-block:: SQL+Jinja

      select {{ my_variable | default("col_a") }}
      from my_table

is interpreted as:

.. code-block:: sql

      select col_a
      from my_table

Library Templating
^^^^^^^^^^^^^^^^^^

If using *SQLFluff* for dbt with jinja as your templater, you may have library
function calls within your sql files that can not be templated via the
normal macro templating mechanisms:

.. code-block:: SQL+Jinja

    SELECT foo, bar FROM baz {{ dbt_utils.group_by(2) }}

To template these libraries, you can use the `sqlfluff:jinja:library_path`
config option:

.. code-block:: cfg

    [sqlfluff:templater:jinja]
    library_path = sqlfluff_libs

This will pull in any python modules from that directory and allow sqlfluff
to use them in templates. In the above example, you might define a file at
`sqlfluff_libs/dbt_utils.py` as:

.. code-block:: python

    def group_by(n):
        return "GROUP BY 1,2"


If an `__init__.py` is detected, it will be loaded alongside any modules and
submodules found within the library path.

.. code-block:: SQL+Jinja

   SELECT
      {{ custom_sum('foo', 'bar') }},
      {{ foo.bar.another_sum('foo', 'bar') }}
   FROM
      baz

`sqlfluff_libs/__init__.py`:

.. code-block:: python

    def custom_sum(a: str, b: str) -> str:
        return a + b

`sqlfluff_libs/foo/__init__.py`:

.. code-block:: python

    # empty file

`sqlfluff_libs/foo/bar.py`:

.. code-block:: python

     def another_sum(a: str, b: str) -> str:
        return a + b

dbt Project Configuration
-------------------------

.. note::
    From sqlfluff version 0.7.0 onwards, the dbt templater has been moved
    to a separate plugin and python package. Projects that were already using
    the dbt templater may initially fail after an upgrade to 0.7.0+. See the
    installation instructions below to install the dbt templater.

    dbt templating is still a relatively new feature added in 0.4.0 and
    is still in very active development! If you encounter an issue, please
    let us know in a GitHub issue or on the SQLFluff slack workspace.

:code:`dbt` is not the default templater for *SQLFluff* (it is :code:`jinja`).
:code:`dbt` is a complex tool, so using the default :code:`jinja` templater
will be simpler. You should be aware when using the :code:`dbt` templater that
you will be exposed to some of the complexity of :code:`dbt`. Users may wish to
try both templaters and choose according to how they intend to use *SQLFluff*.

A simple rule of thumb might be:

- If you are using *SQLFluff* in a CI/CD context, where speed is not
  critical but accuracy in rendering sql is, then the `dbt` templater
  may be more appropriate.
- If you are using *SQLFluff* in an IDE or on a git hook, where speed
  of response may be more important, then the `jinja` templater may
  be more appropriate.

Pros:

* Most (potentially all) macros will work

Cons:

* More complex, e.g. using it successfully may require deeper
  understanding of your models and/or macros (including third-party macros)

  * More configuration decisions to make
  * Best practices are not yet established or documented

* If your :code:`dbt` model files access a database at compile time, using
  SQLFluff with the :code:`dbt` templater will **also** require access to a
  database.

  * Note that you can often point SQLFluff and the :code:`dbt` templater at a
    test database (i.e. it doesn't have to be the production database).

* Runs slower

Installation & Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to get started using *SQLFluff* with a dbt project you will
first need to install the relevant `dbt adapter`_ for your dialect
and the :code:`sqlfluff-templater-dbt` package using
your package manager of choice (e.g.
:code:`pip install dbt-postgres sqlfluff-templater-dbt`) and then will need the
following configuration:

.. _`dbt adapter`: https://docs.getdbt.com/docs/available-adapters

In *.sqlfluff*:

.. code-block:: cfg

    [sqlfluff]
    templater = dbt

In *.sqlfluffignore*:

.. code-block:: text

    target/
    # dbt <1.0.0
    dbt_modules/
    # dbt >=1.0.0
    dbt_packages/
    macros/

You can set the dbt project directory, profiles directory and profile with:

.. code-block:: cfg

    [sqlfluff:templater:dbt]
    project_dir = <relative or absolute path to dbt_project directory>
    profiles_dir = <relative or absolute path to the directory that contains the profiles.yml file>
    profile = <dbt profile>
    target = <dbt target>

.. note::

    If the `profiles_dir` setting is omitted, SQLFluff will look for the profile
    in the default location, which varies by operating system. On Unix-like
    operating systems (e.g. Linux or macOS), the default profile directory is
    `~/.dbt/`. On Windows, you can determine your default profile directory by
    running `dbt debug --config-dir`.

To use builtin dbt Jinja functions SQLFluff provides a configuration option
that enables usage within templates.

.. code-block:: cfg

    [sqlfluff:templater:jinja]
    apply_dbt_builtins = True

This will provide dbt macros like `ref`, `var`, `is_incremental()`. If the need
arises builtin dbt macros can be customised via Jinja macros in `.sqlfluff`
configuration file.

.. code-block:: cfg

    [sqlfluff:templater:jinja:macros]
    # Macros provided as builtins for dbt projects
    dbt_ref = {% macro ref(model_ref) %}{{model_ref}}{% endmacro %}
    dbt_source = {% macro source(source_name, table) %}{{source_name}}_{{table}}{% endmacro %}
    dbt_config = {% macro config() %}{% for k in kwargs %}{% endfor %}{% endmacro %}
    dbt_var = {% macro var(variable, default='') %}item{% endmacro %}
    dbt_is_incremental = {% macro is_incremental() %}True{% endmacro %}

If your project requires that you pass variables to dbt through command line,
you can specify them in `template:dbt:context` section of `.sqlfluff`.
See below configuration and its equivalent dbt command:

.. code-block:: cfg

    [sqlfluff:templater:dbt:context]
    my_variable = 1

.. code-block:: text

    dbt run --vars '{"my_variable": 1}'

Known Caveats
^^^^^^^^^^^^^

- To use the dbt templater, you must set `templater = dbt` in the `.sqlfluff`
  config file in the directory where sqlfluff is run. The templater cannot
  be changed in `.sqlfluff` files in subdirectories.
- In SQLFluff 0.4.0 using the dbt templater requires that all files
  within the root and child directories of the dbt project must be part
  of the project. If there are deployment scripts which refer to SQL files
  not part of the project for instance, this will result in an error.
  You can overcome this by adding any non-dbt project SQL files to
  .sqlfluffignore.


CLI Arguments
-------------

You already know you can pass arguments (:code:`--verbose`,
:code:`--exclude-rules`, etc.) through the CLI commands (:code:`lint`,
:code:`fix`, etc.):

.. code-block:: text

    $ sqlfluff lint my_code.sql -v --exclude-rules L022,L027

You might have arguments that you pass through every time, e.g rules you
*always* want to ignore. These can also be configured:

.. code-block:: cfg

    [sqlfluff]
    verbose = 1
    exclude_rules = L022,L027

Note that while the :code:`exclude_rules` config looks similar to the
above example, the :code:`verbose` config has an integer value. This is
because :code:`verbose` is *stackable* meaning there are multiple levels
of verbosity that are available for configuration. See :ref:`cliref` for
more details about the available CLI arguments. For more details about rule
exclusion, see `Enabling and Disabling Rules`_.

Ignoring Errors & Files
-----------------------

Ignoring individual lines
^^^^^^^^^^^^^^^^^^^^^^^^^

Similar to `flake8's ignore`_, individual lines can be ignored by adding
:code:`-- noqa` to the end of the line. Additionally, specific rules can
be ignored by quoting their code or the category.

.. code-block:: sql

    -- Ignore all errors
    SeLeCt  1 from tBl ;    -- noqa

    -- Ignore rule L014 & rule L030
    SeLeCt  1 from tBl ;    -- noqa: L014,L030

    -- Ignore all parsing errors
    SeLeCt from tBl ;       -- noqa: PRS

.. _`flake8's ignore`: https://flake8.pycqa.org/en/3.1.1/user/ignoring-errors.html#in-line-ignoring-errors

Ignoring line ranges
^^^^^^^^^^^^^^^^^^^^

Similar to `pylint's "pylint" directive"`_, ranges of lines can be ignored by
adding :code:`-- noqa:disable=<rule>[,...] | all` to the line. Following this
directive, specified rules (or all rules, if "all" was specified) will be
ignored until a corresponding `-- noqa:enable=<rule>[,...] | all` directive.

.. code-block:: sql

    -- Ignore rule L012 from this line forward
    SELECT col_a a FROM foo -- noqa: disable=L012

    -- Ignore all rules from this line forward
    SELECT col_a a FROM foo -- noqa: disable=all

    -- Enforce all rules from this line forward
    SELECT col_a a FROM foo -- noqa: enable=all


.. _`pylint's "pylint" directive"`: http://pylint.pycqa.org/en/latest/user_guide/message-control.html

.. _sqlfluffignore:

Ignoring types of errors
^^^^^^^^^^^^^^^^^^^^^^^^
General *categories* of errors can be ignored using the ``--ignore`` command
line option or the ``ignore`` setting in ``.sqlfluffignore``. Types of errors
that can be ignored include:

* ``lexing``
* ``linting``
* ``parsing``
* ``templating``

.sqlfluffignore
^^^^^^^^^^^^^^^

Similar to `Git's`_ :code:`.gitignore` and `Docker's`_ :code:`.dockerignore`,
SQLFluff supports a :code:`.sqlfluffignore` file to control which files are and
aren't linted. Under the hood we use the python `pathspec library`_ which also
has a brief tutorial in their documentation.

An example of a potential :code:`.sqlfluffignore` placed in the root of your
project would be:

.. code-block:: cfg

    # Comments start with a hash.

    # Ignore anything in the "temp" path
    /temp/

    # Ignore anything called "testing.sql"
    testing.sql

    # Ignore any ".tsql" files
    *.tsql

Ignore files can also be placed in subdirectories of a path which is being
linted and the sub files will also be applied within that subdirectory.


.. _`Git's`: https://git-scm.com/docs/gitignore#_pattern_format
.. _`Docker's`: https://docs.docker.com/engine/reference/builder/#dockerignore-file
.. _`pathspec library`: https://python-path-specification.readthedocs.io/

.. _defaultconfig:

Default Configuration
---------------------

The default configuration is as follows, note the `Builtin Macro Blocks`_ in
section *[sqlfluff:templater:jinja:macros]* as referred to above.

.. literalinclude:: ../../src/sqlfluff/core/default_config.cfg
   :language: cfg
   :linenos:
