Documentation Contributions
===========================

Contributing to the docs is one of the easiest and most helpful ways
to help the project. Documentation changes require relatively little
specialist knowledge apart from being familiar with how to use SQLFluff
and the docs are read by a very wide range of people.

Documentation takes two forms:

1. Embedded documentation found in function and module `docstrings`_.

2. The free-standing documentation which you're reading now, and hosted
   at `docs.sqlfluff.com`_ (built using `sphinx`_ and `ReadtheDocs`_).

The two are somewhat blurred by the use of `autodoc`_ (and some other custom
integrations), where documentation is generated directly off `docstrings`_
within the codebase, for example the :ref:`ruleref`, :ref:`cliref` and
:ref:`dialectref`. To understand more about how the custom integrations
we use to generate these docs, see the `generate-auto-docs.py`_ file.

.. _`docstrings`:  https://en.wikipedia.org/wiki/Docstring
.. _`docs.sqlfluff.com`:  https://docs.sqlfluff.com
.. _`autodoc`: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html
.. _`generate-auto-docs.py`: https://github.com/sqlfluff/sqlfluff/blob/main/docs/generate-auto-docs.py

.. _`ReadtheDocs`: https://about.readthedocs.com/

Docstrings
----------

Embedded documentation of functions, classes and modules is most useful
for *developer-focussed* documentation as it's most accessible in the places
which those developers are working: *directly in the codebase*. We enforce
that docstrings are present and correctly formatted using the
`pydocstyle rules for ruff`_, which we have configured to enforce the
`google style of docstrings`_.

.. _`pydocstyle rules for ruff`:  https://docs.astral.sh/ruff/rules/#pydocstyle-d
.. _`google style of docstrings`:  https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html

Sphinx Docs
-----------

The main documentation (which you're reading now), is build using `sphinx`_,
and written using `reStructuredText`_ (files ending with :code:`.rst`). The
`sphinx`_ project offers a `reStructuredText primer`_ for people who are new
to the syntax (and the SQLFluff project uses `doc8`_ in the CI process to try
and catch any issues early).

On top of those docs, there are a few areas worth highlighting for new (or
returning) users, which are either specific to the SQLFluff project, or not
particularly clear in the sphinx docs:

* `reStructuredText`_ is very similar to, but differs from (the somewhat more
  well known) `Markdown`_ syntax. Importantly:

  * :code:`*text with single asterisks*` renders as *italics*. Use
    :code:`**double asterisks**` for **bold text**.

  * :code:`code snippets` are created using the |codesnippet|
    directive, rather than just lone backticks (|backquotes|) as found in
    most `Markdown`_.

* To create links to other parts of the documentation (i.e.
  `Cross-referencing`_), use either the :code:`:ref:` syntax.

  * Docs for all the SQL dialects are auto generated with associated anchors
    to use for referencing. For example to link to the
    :ref:`postgres_dialect_ref` dialect docs, you can use the |postgresref|.
    Replace the :code:`postgres` portion with the :code:`name` of the
    dialect you want to link to.

  * Docs for all the bundled rules and handled using a customer `sphinx`_
    plugin, which means you can refer to them using their name or code:
    |LT01ref| resolves to :sqlfluff:ref:`LT01` and |layoutspacingref|
    resolves to :sqlfluff:ref:`layout.spacing`.

  * Docs for any of the python classes and modules handled using `autodoc`_
    can be referenced as per their docs, so the
    :py:class:`sqlfluff.core.rules.base.BaseRule` class can be referenced
    with |baseruleref|. You can also use the :code:`~` prefix (i.e.
    |shortbaseruleref|) so that it just renders as
    :py:class:`~sqlfluff.core.rules.base.BaseRule`. See the docs for
    `Cross-referencing`_ for more details.

.. _`sphinx`: https://www.sphinx-doc.org/en/master/
.. _`reStructuredText`: https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html
.. _`reStructuredText primer`: https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
.. _`doc8`: https://github.com/PyCQA/doc8
.. _`Markdown`: https://www.markdownguide.org/
.. _`Cross-referencing`: https://www.sphinx-doc.org/en/master/usage/referencing.html
.. _`autodoc`: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

.. |codesnippet| raw:: html

    <code class="code docutils literal notranslate">:code:`...`</code>

.. |backquotes| raw:: html

    <code class="code docutils literal notranslate">`...`</code>

.. |postgresref| raw:: html

    <code class="code docutils literal notranslate">:ref:`postgres_dialect_ref`</code>

.. |LT01ref| raw:: html

    <code class="code docutils literal notranslate">:sqlfluff:ref:`LT01`</code>

.. |layoutspacingref| raw:: html

    <code class="code docutils literal notranslate">:sqlfluff:ref:`layout.spacing`</code>

.. |baseruleref| raw:: html

    <code class="code docutils literal notranslate">:py:class:`sqlfluff.core.rules.base.BaseRule`</code>

.. |shortbaseruleref| raw:: html

    <code class="code docutils literal notranslate">:py:class:`~sqlfluff.core.rules.base.BaseRule`</code>
