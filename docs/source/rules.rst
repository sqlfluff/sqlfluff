.. _ruleref:

Rules Reference
===============

`Rules` in `SQLFluff` are implemented as `crawlers`. These are entities
which work their way through the parsed structure of a query to evaluate
a particular rule or set of rules. The intent is that the definition of
each specific rule should be really streamlined and only contain the logic
for the rule itself, with all the other mechanics abstracted away.

Specific Rules
--------------

.. automodule:: sqlfluff.core.rules
   :members:
   :member-order: alphabetical

.. _inline_ignoring_errors:

Inline Ignoring Errors
-----------------------
`SQLFluff` features inline error ignoring. For example, the following will
ignore the lack of whitespace surrounding the ``*`` operator.

.. code-block:: sql

   a.a*a.b AS bad_1  -- noqa: L006

Multiple rules can be ignored by placing them in a comma-delimited list.

.. code-block:: sql

   a.a *  a.b AS bad_2,  -- noqa: L007, L006

It is also possible to ignore non-rule based errors, and instead opt to
ignore templating (``TMP``) & parsing (``PRS``) errors.

.. code-block:: sql

   WHERE dt >= DATE_ADD(CURRENT_DATE(), INTERVAL -2 DAY) -- noqa: PRS

Should the need arise, not specifying specific rules to ignore will ignore
all rules on the given line.

.. code-block:: sql

   a.a*a.b AS bad_3  -- noqa


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
