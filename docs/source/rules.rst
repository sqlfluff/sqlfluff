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

.. autoclass:: sqlfluff.core.rules.base.BaseRule
   :members:
   :private-members:

.. autoclass:: sqlfluff.core.rules.base.LintResult
   :members:

.. autoclass:: sqlfluff.core.rules.base.LintFix
   :members:

The `_eval` function of each rule takes a `RuleContext` parameter. It
evaluate the given segment for violations, returning a `LintResult` if it
finds an error. The `LintResult` includes a reference to the segment which
"triggered" the error. Usually, it is the segment that needs correcting, **or**
if the rule relates to something that is missing, then it should reference on
the segment **following** the location where the missing element should be.

Functional API
--------------
These newer modules provide a higher-level API for rules working with segments
and slices. Rules that need to navigate or search the parse tree may benefit
from using these. Eventually, the plan is for **all** rules to use these
modules. As of December 30, 2021, 17+ rules use these modules.

The modules listed below are submodules of `sqlfluff.core.rules.functional`.

`segments` Module
^^^^^^^^^^^^^^^^^

.. automodule:: sqlfluff.core.rules.functional.segments
   :members:

`segment_predicates` Module
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: sqlfluff.core.rules.functional.segment_predicates
   :members:

`raw_file_slices` Module
^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: sqlfluff.core.rules.functional.raw_file_slices
   :members:

`raw_file_slice_predicates` Module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: sqlfluff.core.rules.functional.raw_file_slice_predicates
   :members:

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
    SELECT col_a a FROM foo --noqa: disable=L012

    -- Ignore all rules from this line forward
    SELECT col_a a FROM foo --noqa: disable=all

    -- Enforce all rules from this line forward
    SELECT col_a a FROM foo --noqa: enable=all


.. _`pylint's "pylint" directive"`: http://pylint.pycqa.org/en/latest/user_guide/message-control.html
