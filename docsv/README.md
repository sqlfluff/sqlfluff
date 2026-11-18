# SQLFluff documentation

The live documentation at [docs.sqlfluff.com](https://docs.sqlfluff.com) is
built from this VitePress project. Write pages in Markdown under `docsv/`.
The [documentation contribution guide](development/documentation.md) covers
links, formatting, and generated reference pages.

## Build locally

Install SQLFluff from the repository root and then install the docs package:

```bash
pip install -e .
cd docsv
corepack enable
corepack pnpm install --frozen-lockfile
corepack pnpm run docs:build
corepack pnpm run docs:preview
```

`docs:build` syncs the shared design assets, generates the rules, dialect,
CLI, API, and internal API reference pages, then builds VitePress. The output
is `docsv/.vitepress/dist/`. For live editing, run `docs:prebuild` once before
`docs:dev`; repeat it after changes to Python code or docstrings.

The default local base is `/en/latest/`. Set `SQLFLUFF_DOCS_BASE` to preview
a release path, such as `/en/4.4.0/`. The development version picker reads
`.vitepress/dev-versions.json`; its other release entries are fixtures and
are not built by the local development server.

## Publishing and compatibility

The [Deploy Docs workflow](../.github/workflows/publish-docs.yaml) builds
`main` as `latest` and release tags as numbered versions. Final releases
also update `stable`. It merges each build into the site tree stored in R2
and deploys the assembled tree to Netlify. Deployment and indexing behavior
are described in the [hosting guide](development/versioned-docs-hosting.md).

The checked-in [permalink map](.vitepress/redirects.json) preserves URLs
emitted by SQLFluff and linked from older content. `assemble-site.py`
validates targets and writes the redirect rules. Keep it in sync when moving
pages. Historical releases built with Sphinx remain hosted as archives;
`shared/version-picker.*` and `scripts/inject-shared-picker.py` support those
published builds. They do not require the current repository to retain the
old Sphinx source tree.
