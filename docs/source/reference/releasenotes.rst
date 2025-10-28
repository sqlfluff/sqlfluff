.. _releasenotes:

Release Notes
=============

This page aims to act as a guide for migrating between major SQLFluff
releases. Necessarily this means that bugfix releases, or releases
requiring no change for the user are not mentioned. For full details
of each individual release, see the detailed changelog_.

.. _changelog: https://github.com/sqlfluff/sqlfluff/blob/main/CHANGELOG.md

Upgrading to 4.x
----------------

This release is the first where the optional Rust routines are available.
For most users, no difference will be visible, as currently the rust libraries
are *opt-in*, and must be explicitly installed with :code:`pip install sqlfluff[rs]`.

Rust libraries are built for most major platforms, and we believe are ready for
public beta testing, but they should be considered experimental until the 5.x release.

.. _upgrading_3_0:

Upgrading to 3.x
----------------

This release makes a couple of potentially breaking changes:

* It drops support for python 3.7, which reached end of life in June 2023.

* It migrates to :code:`pyproject.toml` rather than :code:`setup.cfg` as
  the python packaging configuration file (although keeping :code:`setuptools`
  as the default backend).

* The serialised output for :code:`sqlfluff lint` now contains more information
  about the span of linting issues and initial proposed fixes. Beside the *new*
  fields, the original fields of :code:`line_pos` and :code:`line_no` have been
  renamed to :code:`start_line_pos` and :code:`start_line_no`, to distinguish
  them from the new fields starting :code:`end_*`.

* When linting from stdin, if there are no violations found - before this version,
  the serialised response would be simply an empty list (:code:`[]`). From 3.0
  onwards, there will now  be a record for the *file* with some statistics,
  but the *violations* section of the response for that file will still be an
  empty list.

* The default :code:`annotation_level` set by the :code:`--annotation-level`
  option on the :code:`sqlfluff lint` command has been changed from :code:`notice`
  to :code:`warning`, to better distinguish linting errors from warnings, which
  always now have the level of :code:`notice`. This is only relevant when using
  the :code:`github-annotation` or :code:`github-annotation-native` formats.

* The previously deprecated :code:`--disable_progress_bar` on `:code:lint`,
  :code:`fix` and :code:`format` has now been removed entirely. Please migrate
  to :code:`--disable-progress-bar` to continue using this option.

* The :code:`--force` option on :code:`sqlfluff fix` is now the default behaviour
  and so the option has been deprecated. A new :code:`--check` option has been
  introduced which mimics the old default behaviour. This has been changed as it
  enables significantly lower memory overheads when linting and fixing large
  projects.

Upgrading to 2.3
----------------

This release include two minor breaking changes which will only affect
users engaged in performance optimisation of SQLFluff itself.

* The :code:`--profiler` option on :code:`sqlfluff parse` has been removed.
  It was only present on the `parse` command and not `lint` or `fix`, and
  it is just as simple to invoke the python `cProfiler` directly.

* The :code:`--recurse` cli option and :code:`sqlfluff.recurse` configuration
  option have both been removed. They both existed purely for debugging the
  parser, and were never used in a production setting. The improvement in
  other debugging messages when unparsable sections are found means that
  this option is no longer necessary.

Upgrading to 2.2
----------------

This release changes some of the interfaces between SQLFluff core and
our plugin ecosystem. The only *breaking* change is in the interface
between SQLFluff and *templater* plugins (which are not common in the
ecosystem, hence why this is only a minor and not a major release).

For all plugins, we also recommend a different structure for their
imports (especially for rule plugins which are more common in the
ecosystem) - for performance and stability reasons. Some users had
been experiencing very long import times with previous releases as
a result of the layout of plugin imports. Users with affected plugins
will begin to see a warning from this release onward, which can be
resolved for their plugin by updating to a new version of that plugin
which follows the guidelines.

Templater plugins
^^^^^^^^^^^^^^^^^

Templaters before this version would pass a :code:`make_template()`
callable to the slicing methods as part of being able to map the source
file. This method would accept a :code:`str` and return a
:code:`jinja2.environment.Template` object to allow the templater to
render multiple variants of the template to do the slicing operation
(which allows linting issues found in templated files to be mapped
accurately back to their position in the unrendered source file).
This approach is not very generalisable, and did not support templating
operations with libraries other than :code:`jinja2`.

As a result, we have amended the interface to instead pass a
:code:`render_func()` callable, which accepts a :code:`str` and returns
a :code:`str`. This works fine for the :code:`jinja` templater (and
by extension the :code:`dbt` templater) as they can simply wrap the
original callable with a method that calls :code:`render()` on the
original :code:`Template` object. It also however opens up the door
to other templating engines, and in particular to *remote* templaters
which might pass unrendered code over a HTTP connection for rendering.

Specifically:

* The :code:`slice_file()` method of the base templater classes no longer
  accepts an optional :code:`make_template` argument or a
  :code:`templated_str` argument.

* Instead a :code:`render_func` callable should be passed which can be
  called to generate the :code:`templated_str` on demand.

* Unlike the optional :code:`make_template` - :code:`render_func` is **not**
  optional and should always be present.

Rule plugins
^^^^^^^^^^^^

We recommend that the module in a plugin which defines all
of the hook implementations (anything using the :code:`@hookimpl` decorator)
must be able to fully import before any rule implementations are imported.
More specifically, SQLFluff must be able to both *import* **and**
*run* any implementations of :code:`get_configs_info()` before any plugin
rules (i.e. any derivatives of
:py:class:`BaseRule <sqlfluff.core.rules.base.BaseRule>`) are *imported*.
Because of this, we recommend that rules are defined in a
separate module to the root of the plugin and then only imported *within*
the :code:`get_rules()` method.

Importing in the main body of the module was previously our recommendation
and so may be the case for versions of some plugins. If one of your plugins
does use imports in this way, a warning will be presented from this version
onward, recommending that you update your plugin.

See the :ref:`developingpluginsref` section of the docs for an example.

.. _upgrading_2_0:

Upgrading from 1.x to 2.0
-------------------------

Upgrading to 2.0 brings several important breaking changes:

* All bundled rules have been recoded, both from generic :code:`L00X` formats
  into groups within similar codes (e.g. an *aliasing* group with codes
  of the format :code:`AL0X`), but also given *names* to allow much clearer
  referencing (e.g. :code:`aliasing.column`).
* :ref:`ruleconfig` now uses the rule *name* rather than the rule *code* to
  specify the section. Any unrecognised references in config files (whether
  they are references which *do* match existing rules by code or alias, or
  whether the match no rules at all) will raise warnings at runtime.
* A complete re-write of layout and whitespace handling rules (see
  :ref:`layoutref`), and with that a change in how layout is configured
  (see :ref:`layoutconfig`) and the combination of some rules that were
  previously separate. One example of this is that the legacy rules
  :code:`L001`, :code:`L005`, :code:`L006`, :code:`L008`, :code:`L023`,
  :code:`L024`, :code:`L039`, :code:`L048` & :code:`L071` have been combined
  simply into :sqlfluff:ref:`LT01`.

Recommended upgrade steps
^^^^^^^^^^^^^^^^^^^^^^^^^

To upgrade smoothly between versions, we recommend the following sequence:

#. The upgrade path will be simpler if you have a slimmer configuration file.
   Before upgrading, consider removing any sections from your configuration
   file (often :code:`.sqlfluff`, see :ref:`config`) which match the current
   :ref:`defaultconfig`. There is no need to respecify defaults in your local
   config if they are not different to the stock config.

#. In a local (or other *non-production*) environment, upgrade to SQLFluff
   2.0.x. We recommend using a `compatible release`_ specifier such
   as :code:`~=2.0.0`, to ensure any minor bugfix releases are automatically
   included.

#. Examine your configuration file (as mentioned above), and evaluate how
   rules are currently specified. We recommend primarily using *either*
   :code:`rules` *or* :code:`exclude_rules` rather than both, as detailed
   in :ref:`ruleselection`. Using either the :code:`sqlfluff rules` CLI
   command or the online :ref:`ruleref`, replace *all references* to legacy
   rule codes (i.e. codes of the form :code:`L0XX`). Specifically:

   * In the :code:`rules` and :code:`exclude_rules` config values. Here,
     consider using group specifiers or names to make your config simpler
     to read and understand (e.g. :code:`capitalisation`, is much more
     understandable than :code:`CP01,CP02,CP03,CP04,CP05`, but the two
     specifiers will have the same effect). Note that while legacy codes
     *will still be understood* here (because they remain valid as aliases
     for those rules) - you may find that some rules no longer exist in
     isolation and so these references may be misleading. e.g. :code:`L005`
     is now an alias for :sqlfluff:ref:`layout.spacing` but
     that rule is much more broad ranging than the original scope of
     :code:`L005`, which was only spacing around commas.

   * In :ref:`ruleconfig`. In particular here, legacy references to rule
     codes are *no longer valid*, will raise warnings, and until resolved,
     the configuration in those sections will be ignored. The new section
     references should include the rule *name* (e.g.
     :code:`[sqlfluff:rules:capitalisation.keywords]` rather than
     :code:`[sqlfluff:rules:L010]`). This switch is designed to make
     configuration files more readable, but we cannot support backward
     compatibility here without also having to resolve the potential
     ambiguity of the scenario where both *code-based* and *name-based*
     are both used.

   * Review the :ref:`layoutconfig` documentation, and check whether any
     indentation or layout configuration should be revised.

#. Check your project for :ref:`in_file_config` which refer to rule codes.
   Alter these in the same manner as described above for configuration files.

#. Test linting your project for unexpected linting issues. Where found,
   consider whether to use :code:`sqlfluff fix` to repair them in bulk,
   or (if you disagree with the changes) consider changing which rules
   you enable or their configuration accordingly. In particular you may notice:

   * The indentation rule (:code:`L003` as was, now :sqlfluff:ref:`LT02`) has
     had a significant rewrite, and while much more flexible and accurate, it
     is also more specific. Note that :ref:`hangingindents` are no longer
     supported, and that while not enabled by default, many users may find
     the enabling :ref:`implicitindents` fits their organisation's style
     better.

   * The spacing rule (:sqlfluff:ref:`LT01`: :sqlfluff:ref:`layout.spacing`)
     has a much wider scope, and so may pick up spacing issues that were not
     previously enforced. If you disagree with any of these, you can
     override the :code:`sqlfluff:layout` sections of the config with
     different (or just more liberal settings, like :code:`any`).

.. _`compatible release`: https://peps.python.org/pep-0440/#compatible-release


Example 2.0 config
^^^^^^^^^^^^^^^^^^

To illustrate the points above, this is an illustrative example config
for a 2.0 compatible project. Note that the config is fairly brief and
sets only the values which differ from the default config.

.. code-block:: cfg

    [sqlfluff]
    dialect = snowflake
    templater = dbt
    max_line_length = 120

    # Exclude some specific rules based on a mixture of codes and names
    exclude_rules = RF02, RF03, RF04, ST06, ST07, AM05, AM06, convention.left_join, layout.select_targets

    [sqlfluff:indentation]
    # Enabling implicit indents for this project.
    # See https://docs.sqlfluff.com/en/stable/perma/indent_locations.html
    allow_implicit_indents = True

    # Add a few specific rule configurations, referenced by the rule names
    # and not by the rule codes.
    [sqlfluff:rules:capitalisation.keywords]
    capitalisation_policy = lower

    [sqlfluff:rules:capitalisation.identifiers]
    capitalisation_policy = lower

    [sqlfluff:rules:capitalisation.functions]
    extended_capitalisation_policy = lower

    # An example of setting a custom layout specification which
    # is more lenient than default config.
    [sqlfluff:layout:type:set_operator]
    line_position = alone


Upgrading to 1.4
----------------

This release brings several internal changes, and acts as a prelude
to 2.0.0. In particular, the following config values have changed:

* :code:`sqlfluff:rules:L007:operator_new_lines` has been changed to
  :code:`sqlfluff:layout:type:binary_operator:line_position`.
* :code:`sqlfluff:rules:comma_style` and
  :code:`sqlfluff:rules:L019:comma_style` have both been consolidated
  into :code:`sqlfluff:layout:type:comma:line_position`.

If any of these values have been set in your config, they will be
automatically translated to the new values at runtime, and a warning
will be shown. To silence the warning, update your config file to the
new values. For more details on configuring layout see :ref:`layoutconfig`.


Upgrading to 1.3
----------------

This release brings several potentially breaking changes to the underlying
parse tree. For users of the cli tool in a linting context you should notice
no change. If however your application relies on the structure of the SQLFluff
parse tree or the naming of certain elements within the yaml format, then
this may not be a drop-in replacement. Specifically:

* The addition of a new :code:`end_of_file`` meta segment at the end of
  the parse structure.
* The addition of a :code:`template_loop`` meta segment to signify a jump
  backward in the source file within a loop structure (e.g. a jinja
  :code:`for`` loop).
* Much more specific types on some raw segments, in particular
  :code:`identifier` and :code:`literal` type segments will now appear
  in the parse tree with their more specific type (which used to be called
  :code:`name`) e.g. :code:`naked_identifier`, :code:`quoted_identifier`,
  :code:`numeric_literal` etc...

If using the python api, the *parent* type (such as :code:`identifier`)
will still register if you call :code:`.is_type("identifier")`, as this
function checks all inherited types. However the eventual type returned
by :code:`.get_type()`` will now be (in most cases) what used to be
accessible at :code:`.name`. The :code:`name` attribute will be deprecated
in a future release.


Upgrading to 1.2
----------------

This release introduces the capability to automatically skip large files, and
sets default limits on the maximum file size before a file is skipped. Users
should see a performance gain, but may experience warnings associated with
these skipped files.


Upgrades pre 1.0
----------------

* **0.13.x** new rule for quoted literals, option to remove hanging indents in
  rule L003, and introduction of ``ignore_words_regex``.
* **0.12.x** dialect is now mandatory, the ``spark3`` dialect was renamed to
  ``sparksql`` and  datatype capitalisation was extracted from L010 to it's own
  rule L063.
* **0.11.x** rule L030 changed to use ``extended_capitalisation_policy``.
* **0.10.x** removed support for older dbt versions < 0.20 and stopped ``fix``
  attempting to fix unparsable SQL.
* **0.9.x** refinement of the Simple API, dbt 1.0.0 compatibility,
  and the official SQLFluff Docker image.
* **0.8.x** an improvement to the performance of the parser, a rebuild of the
  Jinja Templater, and a progress bar for the CLI.
* **0.7.x** extracted the dbt templater to a separate plugin and removed the
  ``exasol_fs`` dialect (now merged in with the main ``exasol``).
* **0.6.x** introduced parallel processing, which necessitated a big re-write
  of several innards.
* **0.5.x** introduced some breaking changes to the API.
* **0.4.x** dropped python 3.5, added the dbt templater, source mapping and
  also introduced the python API.
* **0.3.x** drops support for python 2.7 and 3.4, and also reworks the
  handling of indentation linting in a potentially not backward
  compatible way.
* **0.2.x** added templating support and a big restructure of rules
  and changed how users might interact with SQLFluff on templated code.
* **0.1.x** involved a major re-write of the parser, completely changing
  the behaviour of the tool with respect to complex parsing.
