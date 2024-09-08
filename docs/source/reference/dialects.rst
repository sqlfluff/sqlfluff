.. _dialectref:

Dialects Reference
==================

SQLFluff is designed to be flexible in supporting a variety of dialects.
Not all potential dialects are supported so far, but several have been
implemented by the community. Below are a list of the currently available
dialects. Each inherits from another, up to the root `ansi` dialect.

For a canonical list of supported dialects, run the
:program:`sqlfluff dialects` command, which will output a list of the
current dialects available on your installation of SQLFluff.

.. note::

    For technical users looking to add new dialects or add new features
    to existing ones, the dependent nature of how dialects have been
    implemented is to try and reduce the amount of repetition in how
    different elements are defined. As an example, when we say that
    the :ref:`redshift_dialect_ref` dialect *inherits* from the
    :ref:`postgres_dialect_ref` dialect this is not because there
    is an agreement between those projects which means that features
    in one must end up in the other, but that the design of the
    :ref:`redshift_dialect_ref` dialect was heavily *inspired* by the
    postgres dialect and therefore when defining the dialect within
    sqlfuff it makes sense to use :ref:`postgres_dialect_ref` as a
    starting point rather than starting from scratch.

    Consider when adding new features to a dialect:

    - Should I be adding it just to this dialect, or adding it to
      a *parent* dialect?
    - If I'm creating a new dialect, which dialect would be best to
      inherit from?
    - Will the feature I'm adding break any *downstream* dependencies
      within dialects which inherit from this one?

.. We define a shortcut to render double backticks here, which can 
   then be referenced by individual dialects when they want to say
   how backtick quotes behave in that dialect. They would otherwise
   be interpreted as markup and so not shown as back quotes.

.. |back_quotes| raw:: html

    <code class="code docutils literal notranslate">``</code>

.. include:: ../_partials/dialect_summaries.rst
