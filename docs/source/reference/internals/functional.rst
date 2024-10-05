:code:`sqlfluff.utils.functional`: Functional Traversal API
-----------------------------------------------------------

These newer modules provide a higher-level API for rules working with segments
and slices. Rules that need to navigate or search the parse tree may benefit
from using these. Eventually, the plan is for **all** rules to use these
modules. As of December 30, 2021, 17+ rules use these modules.

The modules listed below are submodules of `sqlfluff.utils.functional`.

:code:`segments` Module
^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: sqlfluff.utils.functional.segments
   :members:

:code:`segment_predicates` Module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: sqlfluff.utils.functional.segment_predicates
   :members:

:code:`raw_file_slices` Module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: sqlfluff.utils.functional.raw_file_slices
   :members:

:code:`raw_file_slice_predicates` Module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. automodule:: sqlfluff.utils.functional.raw_file_slice_predicates
   :members:
