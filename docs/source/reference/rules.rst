.. _ruleref:

Rules Reference
===============

`Rules` in `SQLFluff` are implemented as `crawlers`. These are entities
which work their way through the parsed structure of a query to evaluate
a particular rule or set of rules. The intent is that the definition of
each specific rule should be really streamlined and only contain the logic
for the rule itself, with all the other mechanics abstracted away. To
understand how rules are enabled and disabled see :ref:`ruleselection`.

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

Inline Ignoring Errors
-----------------------

`SQLFluff` features inline error ignoring. For example, the following will
ignore the lack of whitespace surrounding the ``*`` operator.

.. code-block:: sql

   a.a*a.b AS bad_1  -- noqa: LT01

Multiple rules can be ignored by placing them in a comma-delimited list.

.. code-block:: sql

   a.a *  a.b AS bad_2,  -- noqa: LT01, LT03

It is also possible to ignore non-rule based errors, and instead opt to
ignore templating (``TMP``) & parsing (``PRS``) errors.

.. code-block:: sql

   WHERE
     col1 = 2 AND
     dt >= DATE_ADD(CURRENT_DATE(), INTERVAL -2 DAY) -- noqa: PRS

.. note::
   It should be noted that ignoring ``TMP`` and ``PRS`` errors can lead to
   incorrect ``sqlfluff lint`` and ``sqfluff fix`` results as `SQLFluff` can
   misinterpret the SQL being analysed.

Should the need arise, not specifying specific rules to ignore will ignore
all rules on the given line.

.. code-block:: sql

   a.a*a.b AS bad_3  -- noqa

.. _inline_ignoring_errors:

Ignoring line ranges
^^^^^^^^^^^^^^^^^^^^

Similar to `pylint's "pylint" directive"`_, ranges of lines can be ignored by
adding :code:`-- noqa:disable=<rule>[,...] | all` to the line. Following this
directive, specified rules (or all rules, if "all" was specified) will be
ignored until a corresponding `-- noqa:enable=<rule>[,...] | all` directive.

.. code-block:: sql

    -- Ignore rule AL02 from this line forward
    SELECT col_a a FROM foo -- noqa: disable=AL02

    -- Ignore all rules from this line forward
    SELECT col_a a FROM foo -- noqa: disable=all

    -- Enforce all rules from this line forward
    SELECT col_a a FROM foo -- noqa: enable=all


.. _`pylint's "pylint" directive"`: http://pylint.pycqa.org/en/latest/user_guide/message-control.html

Rule Index
----------

.. include:: ../_partials/rule_table.rst

.. include:: ../_partials/rule_summaries.rst
