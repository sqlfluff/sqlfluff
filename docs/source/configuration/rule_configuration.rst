.. _ruleconfig:

Rule Configuration
------------------

Rules can be configured with the :code:`.sqlfluff` config files.

Common rule configurations can be set in the :code:`[sqlfluff:rules]` section.

For example:

.. code-block:: cfg

   [sqlfluff:rules]
   allow_scalar = True
   single_table_references = consistent
   unquoted_identifiers_policy = all

Rule specific configurations are set in rule specific subsections.

For example, enforce that keywords are upper case by configuring the rule
:sqlfluff:ref:`CP01`:

.. code-block:: cfg

    [sqlfluff:rules:capitalisation.keywords]
    # Keywords
    capitalisation_policy = upper

All possible options for rule sections are documented in :ref:`ruleref`.

For an overview of the most common rule configurations that you may want to
tweak, see :ref:`defaultconfig` (and use :ref:`ruleref` to find the
available alternatives).

.. _ruleselection:

Enabling and Disabling Rules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The decision as to which rules are applied to a given file is applied on a file
by file basis, by the effective configuration for that file. There are two
configuration values which you can use to set this:

* :code:`rules`, which explicitly *enables* the specified rules. If this
  parameter is unset or empty for a file, this implies "no selection" and
  so "all rules" is taken to be the meaning.
* :code:`exclude_rules`, which explicitly *disables* the specified rules.
  This parameter is applied *after* the :code:`rules` parameter so can be
  used to *subtract* from the otherwise enabled set.

Each of these two configuration values accept a comma separated list of
*references*. Each of those references can be:

* a rule *code* e.g. :code:`LN01`
* a rule *name* e.g. :code:`layout.indent`
* a rule *alias*, which is often a deprecated *code* e.g. :code:`L003`
* a rule *group* e.g. :code:`layout` or :code:`capitalisation`

These different references can be mixed within a given expression, which
results in a very powerful syntax for selecting exactly which rules are
active for a given file.

.. note::

    It's worth mentioning here that the application of :code:`rules` and
    :code:`exclude_rules`, with *groups*, *aliases* and *names*, in projects
    with potentially multiple nested configuration files defining different
    rules for different areas of a project can get very confusing very fast.
    While this flexibility is intended for users to take advantage of, we do
    have some recommendations about how to do this is a way that remains
    manageable.

    When considering configuration inheritance, each of :code:`rules` and
    :code:`exclude_rules` will totally overwrite any values in parent config
    files if they are set in a child file. While the subtraction operation
    between both of them is calculated *"per file"*, there is no combination
    operation between two definitions of :code:`rules` (just one overwrites
    the other).

    The effect of this is that we recommend one of two approaches:

    #. Simply only use :code:`rules`. This has the upshot of each area of
       your project being very explicit in which rules are enabled. When
       that changes for part of your project you just reset the whole list
       of applicable rules for that part of the project.
    #. Set a single :code:`rules` value in your master project config file
       and then only use :code:`exclude_rules` in sub-configuration files
       to *turn off* specific rules for parts of the project where those
       rules are inappropriate. This keeps the simplicity of only having
       one value which is inherited, but allows slightly easier and simpler
       rollout of new rules because we manage by exception.


For example, to disable the rules :sqlfluff:ref:`LT08`
and :sqlfluff:ref:`RF02`:

.. code-block:: cfg

    [sqlfluff]
    exclude_rules = LT08, RF02

To enable individual rules, configure :code:`rules`, respectively.

For example, to enable :sqlfluff:ref:`RF02`:

.. code-block:: cfg

    [sqlfluff]
    rules = RF02

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

The default values can be seen in :ref:`defaultconfig`.

See :ref:`ignoreconfig` for more information on how to turn ignore particular
rules for specific lines, sections or files.

Downgrading rules to warnings
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To keep displaying violations for specific rules, but not have those
issues lead to a failed run, rules can be downgraded to *warnings*.
Rules set as *warnings* won't cause a file to fail, but will still
be shown in the CLI to warn users of their presence.

The configuration of this behaves very like :code:`exclude_rules`
above:

.. code-block:: cfg

    [sqlfluff]
    warnings = LT01, LT04

With this configuration, files with no other issues (other than
those set to warn) will pass. If there are still other issues, then
the file will still fail, but will show both warnings and failures.

.. code-block::

    == [test.sql] PASS
    L:   2 | P:   9 | LT01 | WARNING: Missing whitespace before +
    == [test2.sql] FAIL
    L:   2 | P:   8 | CP02 | Unquoted identifiers must be consistently upper case.
    L:   2 | P:  11 | LT01 | WARNING: Missing whitespace before +

This is particularly useful as a transitional tool when considering
the introduction on new rules on a project where you might want to
make users aware of issues without blocking their workflow (yet).

You can use either rule code or rule name for this setting.

Layout & Spacing Configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :code:`[sqlfluff:layout]` section of the config controls the
treatment of spacing and line breaks across all rules. To understand
more about this section, see the section of the docs dedicated to
layout: :ref:`layoutconfig`.
