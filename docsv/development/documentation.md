# Contributions

Contributing to the docs is one of the easiest and most helpful ways
to help the project. Documentation changes require relatively little
specialist knowledge apart from being familiar with how to use SQLFluff
and the docs are read by a very wide range of people.

Documentation takes two forms:

1. Embedded documentation found in function and module [docstrings](https://en.wikipedia.org/wiki/Docstring).

2. The free-standing documentation which you're reading now, hosted at
   [docs.sqlfluff.com](https://docs.sqlfluff.com) and built using [VitePress](https://vitepress.dev/).

The two are somewhat blurred by a set of custom generation scripts that emit Markdown pages
directly from [docstrings](https://en.wikipedia.org/wiki/Docstring) in the codebase — for example the
[Rules Reference](/reference/rules/index), [CLI Reference](/reference/cli/index),
[Dialect Reference](/reference/dialects/index), and [Internal API Reference](/reference/internals/index).
All generation is orchestrated by [`docsv/scripts/generate-all-docs.py`](https://github.com/sqlfluff/sqlfluff/blob/main/docsv/scripts/generate-all-docs.py).

For the active beta-docs migration and deployment work, see the
[Versioned Beta Docs Hosting Plan](/development/versioned-docs-hosting).


## Docstrings

Embedded documentation of functions, classes and modules is most useful
for *developer-focussed* documentation as it's most accessible in the places
which those developers are working: *directly in the codebase*. We enforce
that docstrings are present and correctly formatted using the
[pydocstyle rules for ruff](https://docs.astral.sh/ruff/rules/#pydocstyle-d), which we have configured to enforce the
[google style of docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html).

## VitePress Docs

The free-standing documentation is written in [Markdown](https://www.markdownguide.org/) (files ending
with `.md`) and built with [VitePress](https://vitepress.dev/). Source files live under `docsv/`.

### Writing Markdown

VitePress uses standard [CommonMark](https://commonmark.org/) Markdown with some extensions:

- `*single asterisks*` or `_underscores_` render as *italics*; `**double asterisks**` for **bold**.
- Inline code uses single backticks: `` `code` ``. Fenced code blocks use triple backticks with an
  optional language tag for syntax highlighting:

  ````md
  ```sql
  SELECT 1;
  ```
  ````

- VitePress supports custom containers for callouts:

  ```md
  ::: tip
  A helpful tip.
  :::

  ::: warning
  A warning.
  :::

  ::: info
  An informational note.
  :::
  ```

### Linking between pages

Use standard Markdown links with root-relative paths (no `.md` extension needed):

```md
See [Configuration](/configuration/) for details.
See [LT01](/reference/rules/layout#lt01) for the rule reference.
```

### Auto-generated pages

Several reference sections are generated automatically by scripts in `docsv/scripts/` and
should **not** be edited by hand — your changes will be overwritten on the next build:

| Section | Script |
|---|---|
| [Rules Reference](/reference/rules/index) | `generate-rules-docs.py` |
| [CLI Reference](/reference/cli/index) | `generate-cli-docs.py` |
| [Dialect Reference](/reference/dialects/index) | `generate-dialects-docs.py` |
| [Internal API Reference](/reference/internals/index) | `generate-internals-docs.py` |

To update auto-generated content, edit the relevant docstrings in the Python source and
re-run `python docsv/scripts/generate-all-docs.py`.

### Building the docs locally

```bash
cd docsv
pnpm install
pnpm run docs:build
pnpm run docs:preview
```

For a live-reloading dev server during writing, you must generate the auto-generated reference
pages first — otherwise all `/reference/...` links will 404:

```bash
pnpm run docs:prebuild   # generates rules, CLI, dialect, and API pages
pnpm run docs:dev        # then start the hot-reloading server
```

If you edit any Python source or docstrings, re-run `docs:prebuild` to update the reference pages.
