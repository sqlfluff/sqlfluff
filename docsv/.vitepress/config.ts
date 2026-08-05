import { readFileSync } from 'node:fs'
import { join } from 'node:path'
import { defineConfig } from 'vitepress'
import type { DefaultTheme, HeadConfig } from 'vitepress'

// Auto-generated sidebar and redirect configurations
import sidebarRules from './sidebar-rules.json'
import sidebarCli from './sidebar-cli.json'
import sidebarApi from './sidebar-api.json'
import sidebarDialects from './sidebar-dialects.json'
import { normalizeBase, withDocsBase } from './path-utils'
import { DESIGN_SOURCE, assertDesignPackage } from '../scripts/sync-design.mjs'

const GUIDE: DefaultTheme.NavItemWithLink[] = [
    { text: 'Introduction', link: '/guide/' },
    { text: 'Installation', link: '/guide/install' },
    { text: 'Basic Usage', link: '/guide/basic-usage' },
    { text: 'Custom Usage', link: '/guide/custom-usage' },
    { text: 'Why SQLFluff?', link: '/guide/why' },
    { text: 'Vision', link: '/guide/vision' },
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
]

const REFERENCES: DefaultTheme.NavItemWithLink[] = [
    { text: 'CLI', link: '/reference/cli' },
    { text: 'Rules', link: '/reference/rules' },
    { text: 'Dialects', link: '/reference/dialects' },
    { text: 'Python API', link: '/reference/api' },
    { text: 'Release Notes', link: '/reference/release-notes' },
]

const docsBase = normalizeBase(process.env.SQLFLUFF_DOCS_BASE, '/sqlfluff/')
const noIndex = process.env.SQLFLUFF_DOCS_NOINDEX === '1'

assertDesignPackage()

/**
 * Inlined rather than linked so the theme is applied before first paint without
 * a render-blocking request. Read from the submodule, which is the source of
 * truth; `design:sync` copies the rest of the package into `public/`.
 */
const themeBootstrap = readFileSync(join(DESIGN_SOURCE, 'js/theme.js'), 'utf-8')

const designAsset = (path: string) => withDocsBase(docsBase, `sqlfluff-design/${path}`)

const head: HeadConfig[] = [
    ['link', { rel: 'icon', href: withDocsBase(docsBase, 'favicon.ico') }],
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
        // Was '/logo.svg', which has never existed in this repo. Use the shared
        // brand asset so the mark comes from the design package. VitePress
        // applies the docs base to this itself.
        logo: '/sqlfluff-design/img/sqlfluff-avatar.png',

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
    }
})
