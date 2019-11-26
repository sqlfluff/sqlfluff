.. _ruleref:

Rules Reference
===============

`Rules` in `sqlfluff` are implemented as `crawlers`. These are entities
which work their way through the parsed structure of a query to evaluate
a particular rule or set of rules. The intent is that the definition of
each specific rule should be really streamlined and only contain the logic
for the rule itself, with all the other mechanics abstracted away.

Specific Rules
--------------

.. automodule:: sqlfluff.rules.std
   :members:
   :member-order: alphabetical


Implementation
--------------

.. autoclass:: sqlfluff.rules.base.RuleSet
   :members:

.. autoclass:: sqlfluff.rules.base.BaseCrawler
   :members:
   :private-members:

.. autoclass:: sqlfluff.rules.base.LintResult
   :members:

.. autoclass:: sqlfluff.rules.base.LintFix
   :members:


The `_eval` function of each rule should take enough arguments that it can
evaluate the position of the given segment in relation to it's neighbors,
and that the segment which finally "triggers" the error, should be the one
that would be corrected OR if the rule relates to something that is missing,
then it should flag on the segment FOLLOWING, the place that the desired
element is missing.
