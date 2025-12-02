.. _ruleref:

Rules Reference
===============

This page is an index of available rules which are bundled with SQLFluff.

* For information on how to configure which rules are enabled for your
  project see :ref:`ruleselection`.

* If you just want to turn rules on or off for specific files, or specific
  sections of files, see :ref:`ignoreconfig`.

* For more information on how to configure the rules which you do enable
  see :ref:`ruleconfig`.

Core Rules
----------

Certain rules belong to the :code:`core` rule group. In order for
a rule to be designated as :code:`core`, it must meet the following
criteria:

* Stable
* Applies to most dialects
* Could detect a syntax issue
* Isn’t too opinionated toward one style (e.g. the :code:`dbt` style guide)

Core rules can also make it easier to roll out SQLFluff to a team by
only needing to follow a 'common sense' subset of rules initially,
rather than spending time understanding and configuring all the
rules, some of which your team may not necessarily agree with.

We believe teams will eventually want to enforce more than just
the core rules, and we encourage everyone to explore all the rules
and customize a rule set that best suites their organization.

See the :ref:`config` section for more information on how to enable
only :code:`core` rules by default.

Rule Index
----------

.. include:: ../_partials/rule_table.rst

.. include:: ../_partials/rule_summaries.rst
