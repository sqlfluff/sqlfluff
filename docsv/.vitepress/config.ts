import { existsSync, readFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vitepress'
import type { DefaultTheme, HeadConfig } from 'vitepress'

// Auto-generated sidebar and redirect configurations
import sidebarRules from './sidebar-rules.json'
import sidebarCli from './sidebar-cli.json'
import sidebarApi from './sidebar-api.json'
import sidebarDialects from './sidebar-dialects.json'
import sidebarInternals from './sidebar-internals.json'
import { manifestPath, normalizeBase, withDocsBase } from './path-utils'
import { DESIGN_SOURCE, assertDesignPackage } from '../scripts/sync-design.mjs'

const GUIDE: DefaultTheme.NavItemWithLink[] = [
    { text: 'Introduction', link: '/guide/' },
    { text: 'Installation', link: '/guide/install' },
    { text: 'Basic Usage', link: '/guide/basic-usage' },
    { text: 'Custom Usage', link: '/guide/custom-usage' },
    { text: 'Why SQLFluff?', link: '/guide/why' },
    { text: 'Vision', link: '/guide/vision' },
    { text: 'SQLFluff in the Wild', link: '/guide/in-the-wild' },
]

const TEMPLATING: DefaultTheme.SidebarItem = {
    text: 'Templating',
    collapsed: true,
    items: [
        { text: 'Overview', link: '/configuration/templating/' },
        { text: 'Variants Rendering', link: '/configuration/templating/variants/' },
        { text: 'Jinja', link: '/configuration/templating/jinja' },
        { text: 'Placeholder', link: '/configuration/templating/placeholder' },
        { text: 'Python', link: '/configuration/templating/python' },
        { text: 'dbt', link: '/configuration/templating/dbt' },
        { text: 'Generic Templater', link: '/configuration/templating/generic' },
    ]
}

const CONFIGURATION: DefaultTheme.SidebarItem[] = [
    { text: 'Overview', link: '/configuration/' },
    { text: 'Rules', link: '/configuration/rules' },
    { text: 'Layout & Formatting', link: '/configuration/layout' },
    TEMPLATING,
    { text: 'Ignoring Errors', link: '/configuration/ignoring' },
    { text: "Default Configuration", link: '/configuration/defaults' },
]

const CONFIGURATION_NAV: DefaultTheme.NavItemWithLink[] = [
    { text: 'Overview', link: '/configuration/' },
    { text: 'Rules', link: '/configuration/rules' },
    { text: 'Layout & Formatting', link: '/configuration/layout' },
]

const USAGE_GUIDES: DefaultTheme.NavItemWithLink[] = [
    { text: 'Production Usage', link: '/usage/' },
    { text: 'CLI Exit Codes', link: '/usage/cli' },
    { text: 'Security', link: '/usage/security' },
    { text: 'Team Rollout', link: '/usage/team-rollout' },
    { text: 'CI/CD Integration', link: '/usage/ci-cd' },
    { text: 'Pre-commit', link: '/usage/pre-commit' },
    { text: 'Diff Quality', link: '/usage/diff-quality' },
    { text: 'Troubleshooting', link: '/usage/troubleshooting' },
]

const DEVELOPMENT: DefaultTheme.NavItemWithLink[] = [
    { text: 'Architecture', link: '/development/architecture' },
    { text: 'Dialect Changes', link: '/development/dialect' },
    { text: 'Developing Rules', link: '/development/developing-rules' },
    { text: 'Plugins', link: '/development/plugins' },
    { text: 'Custom Rules', link: '/development/custom-rules' },
    { text: 'Documentation', link: '/development/documentation' },
    { text: 'Using Git', link: '/development/git' },
]

const REFERENCES: DefaultTheme.NavItemWithLink[] = [
    { text: 'CLI', link: '/reference/cli' },
    { text: 'Rules', link: '/reference/rules' },
    { text: 'Dialects', link: '/reference/dialects' },
    { text: 'Python API', link: '/reference/api' },
    { text: 'Release Notes', link: '/reference/release-notes' },
]

/**
 * Defaults to the layout the site is actually published under, so a local build
 * matches production without being told to. `/sqlfluff/` matched nothing that is
 * deployed, and because the version picker reads the current version out of the
 * base, an unversioned default meant the picker and the version notice could not
 * appear locally at all. Every publishing path sets this explicitly.
 */
const docsBase = normalizeBase(process.env.SQLFLUFF_DOCS_BASE, '/en/latest/')
const noIndex = process.env.SQLFLUFF_DOCS_NOINDEX === '1'

assertDesignPackage()

/**
 * Inlined rather than linked so the theme is applied before first paint without
 * a render-blocking request. Read from the installed package, which is the
 * source of truth; `design:sync` copies the rest of the package into `public/`.
 */
const themeBootstrap = readFileSync(join(DESIGN_SOURCE, 'js/theme.js'), 'utf-8')

const designAsset = (path: string) => withDocsBase(docsBase, `sqlfluff-design/${path}`)

const head: HeadConfig[] = [
    // The shared favicon set, so the docs and sqlfluff.com show the same mark
    // in a tab and move together when it changes.
    ['link', { rel: 'icon', href: designAsset('img/favicon.ico'), sizes: 'any' }],
    ['link', { rel: 'icon', type: 'image/png', sizes: '32x32', href: designAsset('img/favicon-32x32.png') }],
    ['link', { rel: 'icon', type: 'image/png', sizes: '16x16', href: designAsset('img/favicon-16x16.png') }],
    ['link', { rel: 'apple-touch-icon', href: designAsset('img/apple-touch-icon.png') }],
    // The bootstrap rewrites this to match the resolved theme.
    ['meta', { name: 'theme-color', content: '#f7f8f8' }],
    ['script', {}, themeBootstrap],
    ['link', { rel: 'stylesheet', href: designAsset('css/tokens.css') }],
    ['link', { rel: 'stylesheet', href: designAsset('css/base.css') }],
    ['link', { rel: 'stylesheet', href: designAsset('css/components.css') }],
]

if (noIndex) {
    head.push(['meta', { name: 'robots', content: 'noindex,nofollow' }])
}

/**
 * Serve the versions manifest during local development.
 *
 * In production `scripts/assemble-site.py` writes the manifest at the language
 * root, one level above this build's base, so that every published version reads
 * the same file. The dev server only serves `public/` beneath its own base, which
 * puts that path out of reach: the request 404s, and the version picker correctly
 * degrades to a static label. That made the picker and the version notice
 * impossible to work on locally, so this serves `dev-versions.json` at the same
 * path the deployed site uses.
 *
 * The fixture is read per request, so editing it to try a different set of
 * versions only needs a browser reload. Deleting it exercises the degraded path.
 * The release entries it names are not built locally, so following one of those
 * links in dev lands on the dev server's own 404.
 *
 * The picker takes the current version from the base, so this only resolves to
 * anything under a versioned base. That is now the default, and
 * `SQLFLUFF_DOCS_BASE` overrides it to preview another version.
 *
 * `apply: 'serve'` keeps this out of production builds, and registering the
 * middleware directly in `configureServer` runs it ahead of Vite's own base
 * handling, which would otherwise reject the path first.
 */
const devVersionsFixture = join(dirname(fileURLToPath(import.meta.url)), 'dev-versions.json')

const serveDevVersions = {
    name: 'sqlfluff-dev-versions',
    apply: 'serve' as const,
    configureServer(server: { middlewares: { use: (path: string, fn: unknown) => void } }) {
        server.middlewares.use(
            manifestPath(docsBase),
            (_req: unknown, res: { statusCode: number; setHeader: (k: string, v: string) => void; end: (body?: string) => void }) => {
                if (!existsSync(devVersionsFixture)) {
                    res.statusCode = 404
                    res.end()
                    return
                }

                res.setHeader('Content-Type', 'application/json')
                res.end(readFileSync(devVersionsFixture, 'utf-8'))
            }
        )
    },
}

export default defineConfig({
    title: 'SQLFluff',
    description: 'The SQL Linter for Humans',
    srcExclude: ['**/README.md',],

    base: docsBase,

    head,

    // The shared design script is the single owner of the theme signals, so
    // VitePress must not also manage them. This drops its inline dark-mode
    // script and its own two-state toggle, which the shared three-state control
    // replaces. `useData().isDark` becomes inert; nothing in the default theme
    // reads it apart from the toggle being replaced, and VitePress dark styling
    // keys off the `dark` class which the shared script sets.
    appearance: false,

    themeConfig: {
        // The shared wordmark, matching what sqlfluff.com shows in the same
        // position. VitePress applies the docs base to this itself. The alt
        // text carries the accessible name for the home link, since the site
        // title below is hidden.
        logo: { src: '/sqlfluff-design/img/sqlfluff-wide.png', alt: 'SQLFluff' },

        // The wordmark already reads "SQLfluff", so the adjacent title would
        // repeat it. sqlfluff.com shows the mark alone for the same reason.
        siteTitle: false,

        nav: [
            { text: 'Guide', items: GUIDE },
            { text: 'Configuration', items: CONFIGURATION_NAV },
            { text: 'Reference', items: REFERENCES },
        ],

        sidebar: [
            { text: 'Getting Started', items: GUIDE },
            { text: 'Usage Guides', items: USAGE_GUIDES },
            { text: 'Development', items: DEVELOPMENT },
            { text: 'Configuration', items: CONFIGURATION },
            {
                text: 'Reference',
                items: [
                    sidebarCli,
                    sidebarRules,
                    sidebarApi,
                    sidebarDialects,
                    { text: 'Release Notes', link: '/reference/release-notes' },
                    sidebarInternals,
                ]
            },
        ],

        search: {
            provider: 'local',
            options: {
                detailedView: true,
            }
        },

        socialLinks: [
            { icon: 'github', link: 'https://github.com/sqlfluff/sqlfluff' },
            { icon: 'twitter', link: 'https://twitter.com/sqlfluff' },
            { icon: 'bluesky', link: 'https://bsky.app/profile/sqlfluff.com' },
            { icon: 'slack', link: 'https://join.slack.com/t/sqlfluff/shared_invite/zt-3qprhrisj-ClUo_1tLmYBzrVu5ZoDwIw' },
        ],

        editLink: {
            pattern: 'https://github.com/sqlfluff/sqlfluff/edit/main/docsv/:path',
            text: 'Edit this page on GitHub'
        },

        footer: {
            message: 'Released under the MIT License.',
            copyright: 'Copyright © 2026 SQLFluff Contributors'
        }
    },

    markdown: {
        theme: {
            light: 'github-light',
            dark: 'github-dark'
        },
        lineNumbers: false
    },

    vite: {
        plugins: [serveDevVersions]
    }
})
