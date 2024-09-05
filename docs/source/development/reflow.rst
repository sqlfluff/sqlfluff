.. _reflowinternals:

Reflow Internals
----------------

Many rules supported by SQLFluff involve the spacing and layout of different
elements, either to enforce a particular layout or just to add or remove
code elements in a way sensitive to the existing layout configuration. The
way this is achieved is through some centralised utilities in the
`sqlfluff.utils.reflow` module.

This module aims to achieve several things:

* Less code duplication by implementing reflow logic in only one place.

* Provide a streamlined interface for rules to easily utilise reflow logic.

  * Given this requirement, it's important that reflow utilities work
    within the existing framework for applying fixes to potentially
    templated code. We achieve this by returning `LintFix` objects which
    can then be returned by each rule wanting to use this logic.

* Provide a consistent way of *configuring* layout requirements. For more
  details on configuration see :ref:`layoutconfig`.

To support this, the module provides a :code:`ReflowSequence` class which
allows access to all of the relevant operations which can be used to
reformat sections of code, or even a whole file. Unless there is a very
good reason, all rules should use this same approach to ensure consistent
treatment of layout.

.. autoclass:: sqlfluff.utils.reflow.ReflowSequence
   :members:

.. autoclass:: sqlfluff.utils.reflow.elements.ReflowPoint
   :members:
   :inherited-members:

.. autoclass:: sqlfluff.utils.reflow.elements.ReflowBlock
   :members:
   :inherited-members:
