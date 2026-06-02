# Versioned Beta Docs Hosting Plan

This document captures the proposed implementation for hosting the VitePress
documentation at `betadocs.sqlfluff.com` using Netlify for serving and
Cloudflare R2 as the persistent store for versioned builds.

The goal is to mirror the useful parts of the current Read the Docs model:

- `betadocs.sqlfluff.com/en/latest/` built from `main`
- `betadocs.sqlfluff.com/en/stable/` built from the newest non-prerelease release
- `betadocs.sqlfluff.com/en/<version>/` built from release tags
- A version picker which works across all published versions

## Summary

The recommended model is:

1. GitHub Actions builds one docs target at a time.
2. Cloudflare R2 stores the canonical assembled site tree.
3. Netlify serves the assembled site snapshot.
4. A shared manifest at `/en/versions.json` drives the version picker.
5. VitePress handles `latest`, `stable`, and all post-cutover releases.
6. Sphinx can later be used for pre-cutover releases.

This avoids rebuilding every historical release on every deployment. Each
workflow run rebuilds only the version which changed, merges that output into
the assembled site tree, updates the manifest, and republishes the assembled
site.

## Architecture

### Responsibilities

- GitHub Actions: Build docs, update the assembled site, and trigger deploys.
- Cloudflare R2: Durable store for the published multi-version site tree.
- Netlify: Serve the assembled snapshot at `betadocs.sqlfluff.com`.
- VitePress: Render `latest`, `stable`, and future release docs.
- Sphinx: Later fallback for versions older than the VitePress cutover.

### Why R2 Is The Source Of Truth

Netlify is good at serving static content, but each deploy effectively replaces
the deployed site. That is not a good fit for long-lived version archives.

R2 is a better canonical store because it lets the workflows:

- keep old built versions indefinitely
- update only one version subtree at a time
- recover older versions without rebuilding everything else
- survive dependency drift in historical tags

### Canonical Site Layout

The assembled site stored in R2 should look like this:

```text
site/
  en/
    latest/
    stable/
    4.3.0/
    4.2.1/
    versions.json
    shared/
      version-picker.js
      version-picker.css
```

Notes:

- `latest` is built from `main`.
- `stable` is built from the newest final release.
- Release folders are built from git tags.
- `shared/` holds assets reused by both VitePress and Sphinx outputs.

### Snapshot Storage Strategy

R2 should retain both of the following:

- an exploded assembled site tree for the current published view
- immutable assembled snapshot archives for rollback, audit, and manual imports

This keeps day-to-day publishing simple while preserving a stronger rollback and
recovery path.

## Build And Deploy Model

Each deploy follows the same high-level pattern:

1. Checkout the target ref.
2. Download the current assembled site snapshot from R2.
3. Build only the requested docs variant.
4. Replace only the relevant subtree in the assembled snapshot.
5. Regenerate `/en/versions.json`.
6. Upload the updated snapshot back to R2.
7. Deploy that assembled snapshot to Netlify.

This keeps the build incremental while still publishing a complete static site.

### Deploy From `main`

Trigger: push to `main`

Expected result:

- Build VitePress once with base `/en/latest/`
- Replace only `/en/latest/`
- Regenerate `versions.json`
- Leave `/en/stable/` and all release folders untouched
- Sync the assembled tree to R2
- Deploy the assembled tree to Netlify

### Deploy From Release Tag

Trigger: GitHub release published

Expected result:

- Checkout the release tag
- Build VitePress for `/en/<version>/`
- Replace only `/en/<version>/`
- If the release is not a prerelease, also build VitePress for `/en/stable/`
- Regenerate `versions.json`
- Sync the assembled tree to R2
- Deploy the assembled tree to Netlify

Important detail:

`stable` should be built separately rather than implemented as a redirect or a
copy of `/en/<version>/`. VitePress bakes the base path into links and asset
paths, so `/en/stable/` wants a dedicated build with its own base.

### Manual Rebuild Of Older Release

Trigger: `workflow_dispatch`

Expected result:

- Accept a version tag as input
- Validate the tag exists
- Determine whether to use VitePress or Sphinx
- Build only that version
- Replace only `/en/<version>/`
- Optionally refresh `/en/stable/` when explicitly requested and appropriate
- Regenerate `versions.json`
- Republish the assembled snapshot

## Version Picker Design

### Registry Model

Published versions should not need to register themselves with each other at
build time. Instead, the picker should read a shared runtime manifest from
`/en/versions.json`.

That manifest should be updated by the publishing workflow each time a version
is added, rebuilt, promoted to stable, or hidden.

### Initial Manifest Shape

The exact schema can evolve, but a practical initial contract is:

```json
{
  "default": "latest",
  "latest": "latest",
  "stable": "4.3.0",
  "versions": [
    {
      "key": "latest",
      "label": "latest",
      "title": "Development",
      "path": "/en/latest/",
      "kind": "channel",
      "builder": "vitepress",
      "prerelease": false
    },
    {
      "key": "stable",
      "label": "stable",
      "title": "Stable",
      "path": "/en/stable/",
      "kind": "channel",
      "builder": "vitepress",
      "prerelease": false
    },
    {
      "key": "4.3.0",
      "label": "4.3.0",
      "title": "4.3.0",
      "path": "/en/4.3.0/",
      "kind": "release",
      "builder": "vitepress",
      "prerelease": false,
      "published_at": "2026-05-19"
    }
  ]
}
```

### Picker Behavior

The initial picker behavior should stay simple:

1. First rollout: switch to the selected version root.
2. Later enhancement: attempt to preserve the current relative page path, with
  fallback to the selected version root if the page does not exist.

Root-only switching is the default until redirect parity and mixed VitePress or
Sphinx path compatibility are good enough to justify a smarter switch.

### Shared Runtime Assets

The final picker should not be VitePress-only. Instead, publish shared assets
under `/en/shared/` so both VitePress and Sphinx versions can load the same
runtime picker and manifest.

This avoids having to rebuild every historical version whenever a new version is
published.

## Workflow Layout

The workflows should be organized around one reusable deploy workflow plus thin
trigger workflows.

### Reusable Workflow

Purpose: perform the shared assembly and deploy steps.

Inputs should include:

- git ref or tag to build
- output target such as `latest`, `stable`, or `4.3.0`
- builder type: `vitepress` or `sphinx`
- whether to refresh `stable`
- whether the target is prerelease

### Trigger Workflows

1. Main docs deploy
   - Trigger: push to `main`
   - Builder: VitePress
   - Target: `latest`

2. Release docs deploy
   - Trigger: release published
   - Builder: VitePress or Sphinx depending on cutover policy
   - Target: `<version>`
   - Also refresh `stable` for non-prereleases

3. Manual docs rebuild
   - Trigger: workflow_dispatch
   - Builder: auto-detected from version and cutover policy
   - Target: explicit version tag

## Compatibility And Operational Policy

### Redirect Compatibility Scope

- Hard requirement: documentation URLs emitted by CLI and runtime surfaces in
  SQLFluff `2.0.0` and later must continue to resolve.
- Strong parity target: preserve all currently declared Sphinx permalinks and
  redirects.
- Best-effort target: preserve broader historical site structure where it helps
  with SEO or older inbound links.

This is a link-resolution guarantee, not a promise that every historical
version is fully hosted on day one. When an older CLI or runtime link already
targets a stable or permalink route, preserving that canonical route is
sufficient.

### Rebuild And Import Policy

- Historical rebuilds should default to rebuilding the tagged source with the
  currently approved builder image.
- A rebuild is considered acceptable when it preserves materially equivalent
  user-facing content, version identity, and important permalinks or redirects.
  It does not need to reproduce byte-identical HTML or search output.
- If a historical tag no longer builds cleanly with the maintained toolchain,
  maintainers may publish an archived static snapshot for that version instead.
- If neither a rebuild nor a snapshot import is practical, the version remains
  unpublished until a manual artifact is supplied.
- For the initial beta launch, it is enough to prove that historical versions
  can be hosted; broad backfill can happen later.

### Release Channel Policy

- Final releases should publish `/en/<version>/` and automatically refresh
  `/en/stable/`.
- Prereleases may be published at their direct version URLs, but should be
  hidden from the version picker.
- `latest` is the only channel where edit links are important. Other channels
  may either omit edit links or point to `main`; version-accurate edit links
  are not required for the first rollout.
- The beta site may be publicly reachable, but it should remain `noindex`
  until cutover work begins.

### Recommended Serving Defaults

- Treat HTML pages and `/en/versions.json` as mutable content and serve them
  with `no-cache` or `must-revalidate` semantics.
- Treat `latest` and `stable` as mutable channels.
- Cache fingerprinted static assets aggressively as immutable.
- If shared picker assets are not fingerprinted, keep them on a short cache.

### Stable Promotion Safeguard

- Automatic promotion of `stable` is the default behavior for final releases.
- Maintainers should retain a manual override so `stable` can be repointed to
  an older version or snapshot if needed.

## Staged Implementation Plan

### Stage 0: Infrastructure Bootstrap

Deliverables:

- Create the R2 bucket
- Create an R2 API token for GitHub Actions
- Create or reuse the Netlify site for beta docs
- Wire `betadocs.sqlfluff.com`
- Add repository secrets
- Set the first VitePress-native release tag to `4.2.0`
- Decide whether prereleases appear in the picker

Stopping point:

- No code deployed yet, but infrastructure and policies are ready

### Stage 1: `latest` Only On Beta

Deliverables:

- Make the VitePress base configurable at build time
- Replace the current GitHub Pages-only docs deploy path
- Add a workflow for pushes to `main`
- Build and publish only `/en/latest/`
- Generate a minimal `versions.json`

Stopping point:

- `betadocs.sqlfluff.com/en/latest/` is live
- R2 is storing the canonical assembled tree
- Netlify is serving the assembled tree

### Stage 2: Manifest And Initial Version Picker

Deliverables:

- Define the `versions.json` schema
- Add a basic picker to the VitePress theme
- Read version data from the shared manifest at runtime
- Keep initial switching behavior simple by targeting version roots only

Stopping point:

- `latest` has a working picker framework
- The registry model is validated before release builds depend on it

### Stage 3: Tagged Releases And `stable`

Deliverables:

- Add release-triggered docs deployment
- Build and publish `/en/<version>/`
- For final releases, also build and publish `/en/stable/`
- Promote `stable` automatically using the existing non-prerelease semantics
  already used by the release process
- Retain a manual override so maintainers can repoint `stable` if required
- Update the manifest so release versions appear in the picker

Stopping point:

- `/en/latest/`, `/en/stable/`, and `/en/<version>/` all work for VitePress
  releases
- The cutover point remains configurable so `4.2.0` can be moved back to Sphinx
  later if unresolved VitePress issues are found

### Stage 4: Manual Rebuild Workflow

Deliverables:

- Add `workflow_dispatch` for rebuilding a chosen version tag
- Validate the tag exists before build
- Rebuild only the requested version subtree
- Support importing an archived static snapshot when rebuilding is not practical
- Keep immutable assembled snapshots so rollback and manual imports use the same
  artifact model
- Optionally refresh `stable` in controlled cases

Stopping point:

- Historical versions can be republished without reissuing releases

### Stage 5: Shared Picker Assets For Cross-Builder Support

Deliverables:

- Move picker runtime logic into shared JS and CSS under `/en/shared/`
- Keep `versions.json` as the single registry source of truth
- Load the same picker assets in VitePress and future Sphinx outputs

Stopping point:

- Older published versions do not need rebuilding just to learn about new
  versions

### Stage 6: Sphinx Backfill For Pre-Cutover Versions

Deliverables:

- Add a cutover version config with an initial value of `4.2.0` as the first
  VitePress-native release
- Build versions older than that cutoff using the existing Sphinx toolchain
- Inject shared picker assets into Sphinx output
- Add a controlled backfill workflow for selected historical releases
- Treat the initial proof as successful once `latest`, `stable`, and one older
  Sphinx-hosted version are live under the beta domain

Stopping point:

- Beta can host a mixed set of VitePress and Sphinx versions under one domain

### Stage 7: Redirect And Compatibility Hardening

Deliverables:

- Review parity with current `docs.sqlfluff.com` URLs
- Preserve documentation URLs emitted by CLI and runtime surfaces in supported
  SQLFluff versions from `2.0.0` onward
- Preserve or replace important `.html`, permalink, and declared redirect
  routes
- Add or refine Netlify redirects where needed
- Improve picker behavior to preserve current page paths where possible
- Review edit links, 404 behavior, and search behavior across versions

Stopping point:

- Beta is close enough to production parity to be considered for cutover

### Stage 8: Final Cutover

Deliverables:

- Point `docs.sqlfluff.com` at the Netlify-hosted assembled site
- Preserve the `latest`, `stable`, and versioned URL structure
- Retire or reduce dependency on Read the Docs

Stopping point:

- The new docs hosting becomes the primary production site

## Repository Changes Expected In Early Stages

These files are likely to be touched first:

- `docsv/.vitepress/config.ts`
- `docsv/.vitepress/theme/index.ts`
- `docsv/package.json`
- `.github/workflows/publish-docs.yaml`
- one or more new helper scripts for manifest generation and site assembly

These files are likely to be touched later:

- `pyproject.toml`
- `util.py`
- `docs/source/conf.py`
- `docs/generate-auto-docs.py`

## Secrets And Configuration

Expected repository secrets:

- `R2_ACCOUNT_ID`
- `R2_ACCESS_KEY_ID`
- `R2_SECRET_ACCESS_KEY`
- `R2_BUCKET`
- `NETLIFY_AUTH_TOKEN`
- `NETLIFY_SITE_ID`

Expected repository or project-level configuration values:

- first VitePress-native release tag, initially `4.2.0`
- redirect compatibility floor, starting at SQLFluff `2.0.0`
- whether manual rebuilds may promote `stable`
- whether the beta environment should emit `noindex`

## Deferred Decisions

The following can be revisited after the initial beta proof:

1. How much historical Sphinx backfill should be added beyond the first older
  hosted version?

## Success Criteria

The plan should be considered successful when:

- `main` automatically publishes to `/en/latest/`
- each release automatically publishes to `/en/<version>/`
- the newest final release is available at `/en/stable/`
- the picker lists available versions from a shared manifest
- prereleases can be published directly without appearing in the picker
- rebuilding a historical version does not require rebuilding every other version
- documentation URLs emitted by SQLFluff `2.0.0` and later continue to resolve
- pre-cutover versions can still be hosted under the same beta domain
- the beta site can remain public while staying `noindex` until cutover
- the beta site is close enough to replace `docs.sqlfluff.com` when desired