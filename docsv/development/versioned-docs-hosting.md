# Versioned docs hosting

The documentation at `docs.sqlfluff.com` is built from `docsv/`, stored as an
assembled site in Cloudflare R2, and served by Netlify. The
[Deploy Docs workflow](https://github.com/sqlfluff/sqlfluff/blob/main/.github/workflows/publish-docs.yaml)
updates one version at a time. Netlify receives the complete assembled site
on each deployment, so R2 is the persistent source of the published tree.

## Versions

- `/en/latest/` is built from `main`.
- `/en/stable/` is rebuilt from the newest final release. The site root and
  `/en/` redirect to it when it exists.
- `/en/<version>/` is built from the corresponding release tag.
- `/en/versions.json` drives the version picker and records each release's
  title, date, kind, and builder.
- `/en/shared/` holds assets used by the historical version picker.

Final releases from `2.0.0` onward were backfilled. Releases before the
VitePress cutover at `4.2.2` retain their published Sphinx HTML. The current
repository no longer builds Sphinx pages; historical archives remain in R2.
`scripts/inject-shared-picker.py` and `shared/version-picker.*` support those
archives without changing their original documentation content.

## Publishing

The workflow runs when `main` is updated, when a release is published, or
when a maintainer dispatches it manually. It checks out the source for the
requested build and the current deployment scripts, downloads the existing
site from R2, builds the requested version, updates the manifest and routing
files, then uploads the complete tree to R2 and deploys it to Netlify.

A final release publishes both its numbered path and `stable`. A prerelease
publishes only its numbered path and is labeled as a prerelease in the picker.
The manual dispatch accepts a release tag in `version`; `refresh_stable`
repoints `stable` only when that tag is a final release. Use `published_at`
only when restoring a release date that is missing from the manifest. A
manual build without a tag updates `latest`.

The publish workflow runs
`scripts/smoke-check-assembled-site.py` before upload. Pull requests build
VitePress in CI, and Python tests cover site assembly and redirects.

## URLs and indexing

The checked-in [permalink map](https://github.com/sqlfluff/sqlfluff/blob/main/docsv/.vitepress/redirects.json) maps legacy
`/perma/` URLs to current pages. `scripts/assemble-site.py` validates every
target against the build and writes Netlify `_redirects` and `_headers`.
Keep the map when moving a page: older SQLFluff versions and external links
may still use those URLs.

Production indexing mode is the default for new deployments. It makes the
stable version canonical on `docs.sqlfluff.com` and indexable, while `latest`
and numbered releases remain available with `noindex`. The versions listing
may be indexed. The beta and native Netlify hostnames redirect to the same
path on `docs.sqlfluff.com`. Set the repository variable
`DOCS_INDEXING_MODE=beta` only when deliberately publishing a beta snapshot;
that mode adds a site-wide `noindex` policy.

After changing indexing or DNS, verify the live `stable`, `latest`, numbered
release, beta hostname, Netlify hostname, permalink, `robots.txt`, and
`sitemap.xml` responses. In particular, check the `X-Robots-Tag` header on
the production stable page.

## Deployment configuration

The workflow uses the repository secrets `R2_ACCOUNT_ID`,
`R2_ACCESS_KEY_ID`, `R2_SECRET_ACCESS_KEY`, `R2_BUCKET`,
`NETLIFY_AUTH_TOKEN`, and `NETLIFY_SITE_ID`. R2 stores the assembled tree
under the `site/` prefix. The Netlify project serves that snapshot and does
not build the repository itself.
