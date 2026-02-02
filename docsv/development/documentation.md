# Contributions

Contributing to the docs is one of the easiest and most helpful ways
to help the project. Documentation changes require relatively little
specialist knowledge apart from being familiar with how to use SQLFluff
and the docs are read by a very wide range of people.

Documentation takes two forms:

1. Embedded documentation found in function and module [docstrings](https://en.wikipedia.org/wiki/Docstring).

2. The free-standing documentation which you're reading now, and hosted
   at [docs.sqlfluff.com](https://docs.sqlfluff.com) (built using `sphinx` and [ReadtheDocs](https://about.readthedocs.com/)).

The two are somewhat blurred by the use of [autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html) (and some other custom
integrations), where documentation is generated directly off [docstrings](https://en.wikipedia.org/wiki/Docstring)
within the codebase, for example the [Rules Reference](/reference/rules/index), [CLI Reference](/reference/cli/index) and
[Dialect Reference](/reference/dialects/index). To understand more about how the custom integrations
we use to generate these docs, see the [generate-auto-docs.py](https://github.com/sqlfluff/sqlfluff/blob/main/docs/generate-auto-docs.py) file.


## Docstrings

Embedded documentation of functions, classes and modules is most useful
for *developer-focussed* documentation as it's most accessible in the places
which those developers are working: *directly in the codebase*. We enforce
that docstrings are present and correctly formatted using the
[pydocstyle rules for ruff](https://docs.astral.sh/ruff/rules/#pydocstyle-d), which we have configured to enforce the
[google style of docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).

## Sphinx Docs

The main documentation (which you're reading now), is build using [sphinx](https://www.sphinx-doc.org/en/master/),
and written using [reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html) (files ending with `.rst`). The
[sphinx](https://www.sphinx-doc.org/en/master/) project offers a [reStructuredText primer](https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html) for people who are new
to the syntax (and the SQLFluff project uses [doc8](https://github.com/PyCQA/doc8) in the CI process to try
and catch any issues early).

On top of those docs, there are a few areas worth highlighting for new (or
returning) users, which are either specific to the SQLFluff project, or not
particularly clear in the sphinx docs:

* [reStructuredText](https://www.sphinx-doc.org/en/master/usage/restructuredtext/index.html) is very similar to, but differs from (the somewhat more
  well known) [Markdown](https://www.markdownguide.org/) syntax. Importantly:

  * `*text with single asterisks*` renders as *italics*. Use
    `**double asterisks**` for **bold text**.

  * `code snippets` are created using the |codesnippet|
    directive, rather than just lone backticks (|backquotes|) as found in
    most [Markdown](https://www.markdownguide.org/).

* To create links to other parts of the documentation (i.e.
  [Cross-referencing](https://www.sphinx-doc.org/en/master/usage/referencing.html)), use either the `:ref:` syntax.

  * Docs for all the SQL dialects are auto generated with associated anchors
    to use for referencing. For example to link to the
    `:ref:postgres_dialect_ref` dialect docs, you can use the |postgresref|.
    Replace the `postgres` portion with the `name` of the
    dialect you want to link to.

  * Docs for all the bundled rules and handled using a customer [sphinx](https://www.sphinx-doc.org/en/master/)
    plugin, which means you can refer to them using their name or `code:
    |LT01ref|` resolves to [LT01](/reference/rules/layout#lt01) and `|layoutspacingref|`
    resolves to [layout.spacing](/reference/rules/layout#lt01).

  * Docs for any of the python classes and modules handled using [autodoc](https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html)
    can be referenced as per their docs, so the
    `sqlfluff.core.rules.base.BaseRule` class can be referenced
    with |baseruleref|. You can also use the `~` prefix (i.e.
    |shortbaseruleref|) so that it just renders as
    `~sqlfluff.core.rules.base.BaseRule`. See the docs for
    [Cross-referencing](https://www.sphinx-doc.org/en/master/usage/referencing.html) for more details.

```html
    <code class="code docutils literal notranslate">`...`</code>
```

```html
    <code class="code docutils literal notranslate">`...`</code>
```

```html
    <code class="code docutils literal notranslate">:ref:`postgres_dialect_ref`</code>
```

```html
    <code class="code docutils literal notranslate">:sqlfluff:ref:`LT01`</code>
```

```html
    <code class="code docutils literal notranslate">:sqlfluff:ref:`layout.spacing`</code>
```

```html
    <code class="code docutils literal notranslate">`sqlfluff.core.rules.base.BaseRule`</code>
```

```html
    <code class="code docutils literal notranslate">`~sqlfluff.core.rules.base.BaseRule`</code>
```
