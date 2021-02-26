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


Implementation
--------------

.. autoclass:: sqlfluff.core.rules.base.RuleSet
   :members:

.. autoclass:: sqlfluff.core.rules.base.BaseCrawler
   :members:
   :private-members:

.. autoclass:: sqlfluff.core.rules.base.LintResult
   :members:

.. autoclass:: sqlfluff.core.rules.base.LintFix
   :members:


The `_eval` function of each rule should take enough arguments that it can
evaluate the position of the given segment in relation to its neighbors,
and that the segment which finally "triggers" the error, should be the one
that would be corrected OR if the rule relates to something that is missing,
then it should flag on the segment FOLLOWING, the place that the desired
element is missing.


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
