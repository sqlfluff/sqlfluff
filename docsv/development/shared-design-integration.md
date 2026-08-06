# Shared Design Integration

This document records how the VitePress documentation consumes the shared
SQLFluff design system, and why the integration is shaped the way it is.

The design system lives in `sqlfluff.com` under `packages/design/`, and that
repository is the source of truth for it. Its own `INTEGRATION.md` is the
contract; this document only covers what is specific to these docs.

The legacy Sphinx documentation is out of scope and is deliberately unchanged.

## Summary

- `vendor/sqlfluff.com` is a pinned Git submodule containing the design package.
- `design:sync` copies the package's static assets into `docsv/public/`.
- The shared tokens, base styles, and component styles are loaded from `head`.
- A narrow adapter maps VitePress's own theme variables onto the shared tokens.
- The shared theme script is the single owner of light and dark mode, and
  VitePress's own appearance handling is switched off.

## Why a submodule

The design package is not published to a registry. Each consuming site pins a
reviewed commit and advances it through an ordinary pull request, so a design
change never reaches a site without a diff someone approved.

This matters more here than elsewhere because these docs publish immutable
versioned builds. Every `/en/<version>/` build bundles the design assets it was
built with, so historical documentation keeps the design it shipped with, and no
published version depends on `sqlfluff.com` being reachable at runtime.

### Working with the submodule

After cloning, or after the pin moves:

```sh
git submodule update --init vendor/sqlfluff.com
```

The build fails with a clear message when the submodule is missing. CI checks it
out with `submodules: true`, which initialises the direct submodule only.

To move to a newer design commit, review the package diff first:

```sh
git -C vendor/sqlfluff.com fetch origin
git -C vendor/sqlfluff.com checkout <reviewed-commit-or-design-tag>
git add vendor/sqlfluff.com
```

Then run `design:sync`, rebuild, and check both themes before merging.

Treat `vendor/sqlfluff.com` as read-only. Changes to shared styles belong
upstream, in the design package.

### Current pin

The submodule points at `12b76ac` on `sqlfluff.com` `main`, the squash merge of
[PR #18](https://github.com/sqlfluff/sqlfluff.com/pull/18), which carries the
shared design package including the consumer changes from
[PR #19](https://github.com/sqlfluff/sqlfluff.com/pull/19).

This is a commit on `main` rather than on a feature branch, so unlike the
development pins it will not be orphaned. Both of those PRs were squash-merged
with their branches deleted, which did orphan the commits pinned at the time; if
future design work is pinned from a branch before it merges, expect the same and
re-pin afterwards.

To check whether the current pin is still reachable:

```sh
git -C vendor/sqlfluff.com fetch origin
git -C vendor/sqlfluff.com merge-base --is-ancestor HEAD origin/main \
  && echo reachable || echo orphaned
```

Upstream has no `design-v*` tags yet. Once it does, pinning a tag rather than a
commit would make the intended version obvious in the diff.

## Asset flow

`design:sync` mirrors
`vendor/sqlfluff.com/packages/design/static/sqlfluff-design/` into
`docsv/public/sqlfluff-design/`, so the assets are served from this site at
`/sqlfluff-design/` under whatever base the build uses.

The copied directory is generated and is not committed. The sync runs
automatically before `docs:dev` and `docs:build`, and can be run on its own with
`pnpm run design:sync`.

Every image the site serves comes from the package, including the favicon set
and both home page lockups, so `docsv/public/` holds nothing but generated
output. It does not exist at all in a fresh clone until the sync has run, which
is why the sync is wired into the scripts rather than left as a manual step.

It is a Node script rather than the `rsync` invocation the upstream guide shows
as an example, because the docs are also built on Windows.

The shared stylesheets are linked from `head`, with paths run through
`withDocsBase` so they resolve under versioned bases such as `/en/latest/`. The
theme script is different: its contents are read from the submodule at build
time and inlined, so the theme is applied before first paint without a
render-blocking request.

## Theme and dark mode

This is the part of the integration with the most design in it, so the reasoning
is worth recording.

### Why the preference is a cookie

The preference is meant to follow a reader between `sqlfluff.com` and the docs
and statistics sites. `localStorage` cannot do that: it is scoped to a single
origin, and the usual hidden-iframe workaround is both asynchronous, so it cannot
run before first paint, and partitioned by top-level site in current browsers.

A cookie scoped to `sqlfluff.com` is the only channel which is both shared across
the subdomains and readable synchronously before paint. The shared script keeps a
same-origin `localStorage` copy purely as a fallback for readers whose browser
rejects cookies.

The cookie name and its `auto`, `light`, and `dark` vocabulary are a frozen
contract upstream. Because each published docs version bundles the copy of the
theme script it was built with, an old build must keep interoperating with
current ones indefinitely.

### Why VitePress's own appearance handling is off

VitePress and the design package both want to own the theme. VitePress keys its
styling on a `dark` class on `<html>`, driven by its own `localStorage` key and
its own inline script; the design package sets `data-theme` from the cookie. Two
owners of one piece of state is the kind of thing which works until it does not.

The config sets `appearance: false`, which removes VitePress's inline dark-mode
script and its own two-state toggle, leaving the shared script as the single
owner. Two things make that cheap rather than invasive:

- VitePress's dark styling, including the dual-theme Shiki code blocks, is keyed
  on the `dark` class in CSS which ships regardless of the setting. The shared
  script sets that class alongside `data-theme`, so all of it keeps working.
- In VitePress's whole default theme, the only consumer of `useData().isDark` is
  the appearance toggle, which `appearance: false` hides and the shared
  three-state control replaces. Nothing else observes the value.

The one thing to keep in mind: a future VitePress version, or a third-party
component, could start reading `isDark`, which is inert under this setting. That
is worth rechecking on major VitePress upgrades.

### The theme control

`ThemeSwitcher.vue` renders the markup from the upstream contract and nothing
else. The shared script delegates clicks from the document, so the control works
even though Vue mounts it after load and re-renders it across navigation. The
component only keeps `aria-pressed` in sync, via `window.sqlfluffTheme.subscribe`.

It offers three states where VitePress offered two, since `auto` is part of the
shared contract and follows the operating system.

## The adapter

`.vitepress/theme/design-adapter.css` maps VitePress's variables onto the shared
tokens. It is imported after the default theme so it wins on the cascade, and it
should stay narrow: translation between the two variable systems, plus layout
which only exists here.

It does not restate the shared palette. Anything which turns out to represent the
same component on more than one SQLFluff site belongs upstream in the design
package instead.

Two mappings are worth explaining:

- `--vp-c-bg` maps to the shared `surface` and `--vp-c-bg-alt` to `canvas`, not
  the other way around. VitePress expects the reading surface to sit above a
  recessed chrome surface, and this preserves that relationship in both themes.
- Button text maps to `accent-contrast` because VitePress hardcodes white button
  text, which fails against the lighter accent used in dark mode.

Docs code blocks intentionally keep VitePress's own surfaces and Shiki themes.
The shared `--sqlfluff-color-code-*` tokens style the terminal component on the
marketing site and are not the same thing.

## Upstream changes this required

Vendoring the package surfaced three problems which were fixed upstream rather
than worked around here, on the `design/framework-neutral-chrome` branch:

1. The theme control and navigation handlers were bound once at
   `DOMContentLoaded`. That suits server-rendered markup, but a client-rendered
   consumer mounts its chrome later and recreates it across route changes, so the
   documented markup would have rendered and then done nothing. They are now
   delegated from the document.
2. The shared script set only `data-theme`, so a framework keyed on a `dark`
   class needed a per-consumer shim. It now sets both, and the tokens accept
   either signal.
3. `base.css` restyled bare elements unlayered, so whichever stylesheet loaded
   last won, and the shared `body` background overrode VitePress's reading
   surface. Those rules now sit in a `sqlfluff-base` cascade layer, which makes
   them a floor rather than a ceiling.

The package also gained a `window.sqlfluffTheme` API for adapters, and its guide
now describes two adoption tiers, because the shared header, navigation, and
footer markup assumes a consumer which renders its own page shell.

Upstream then refined the package further before merging. The one change which
is visible here is that `:focus-visible` was moved out of the cascade layer, so
the shared focus ring is no longer overridable by an application reset. In these
docs that replaces the browser default focus ring, since VitePress only styles
focus on buttons and inputs specifically, and those more specific rules still
win. The rest were robustness fixes: a `color-mix` fallback on the header
background, and `try`/`catch` around cookie reads and the first subscriber call.

## Not done yet

- **Shared header, navigation, and footer.** These docs are on the foundations
  tier: they take tokens, typography, and the theme, but VitePress still renders
  its own chrome. Adopting the shared chrome means replacing the default layout
  with one which renders the shared skeleton around VitePress's own sidebar,
  content, and search components. That is a larger change and is worth doing once
  the visual direction has settled.
- **Nothing outstanding on brand artwork.** The nav uses the shared
  `sqlfluff-wide.png` wordmark, matching sqlfluff.com, with the site title
  hidden because the mark already reads "SQLfluff". The artwork is deliberately
  the same in both themes. The home page hero keeps the stacked
  `sqlfluff-lrg.png` lockup where the main site's hero uses the wide one, which
  is intended rather than an inconsistency.

  If a theme-specific mark is ever wanted, VitePress supports
  `logo: { light, dark }`, switched on the same `dark` class the shared script
  sets. At 132px wide against a 617px source the header mark is already about
  4.7 times oversampled, so this is a colour question rather than a resolution
  one, and would not need vector artwork.
- **Visual regression checks** at representative widths in both themes, which the
  upstream design plan calls for across all three sites.
