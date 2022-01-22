.. _developingrulesref:

Developing Rules
================

`Rules` in `SQLFluff` are implemented as `crawlers`. These are entities
which work their way through the parsed structure of a query to evaluate
a particular rule or set of rules. The intent is that the definition of
each specific rule should be really streamlined and only contain the logic
for the rule itself, with all the other mechanics abstracted away.

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
