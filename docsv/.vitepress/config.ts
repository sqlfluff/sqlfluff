import { defineConfig } from 'vitepress'
import type { DefaultTheme } from 'vitepress'

// Auto-generated sidebar and redirect configurations
import sidebarRules from './sidebar-rules.json'
import sidebarCli from './sidebar-cli.json'
import redirects from './redirects.json'
import sidebarApi from './sidebar-api.json'
import sidebarDialects from './sidebar-dialects.json'

const GUIDE: DefaultTheme.NavItemWithLink[] = [
    { text: 'Introduction', link: '/guide/' },
    { text: 'Installation', link: '/guide/install' },
    { text: 'Basic Usage', link: '/guide/basic-usage' },
    { text: 'Custom Usage', link: '/guide/custom-usage' },
    { text: 'Why SQLFluff?', link: '/guide/why' },
    { text: 'Vision', link: '/guide/vision' },
]

const CONFIGURATION: DefaultTheme.NavItemWithLink[] = [
    { text: 'Overview', link: '/configuration/' },
    { text: 'Rules', link: '/configuration/rules' },
    { text: 'Layout & Formatting', link: '/configuration/layout' },
    { text: 'Templating', link: '/configuration/templating' },
    { text: 'Ignoring Errors', link: '/configuration/ignoring' },
    { text: "Default Configuration", link: '/configuration/defaults' },
]

const USAGE_GUIDES: DefaultTheme.NavItemWithLink[] = [
    { text: 'Production Usage', link: '/usage/production' },
    { text: 'CI/CD Integration', link: '/usage/ci-cd' },
    { text: 'Pre-commit', link: '/usage/pre-commit' },
    { text: 'Diff Quality', link: '/usage/diff-quality' },
    { text: 'Team Rollout', link: '/usage/team-rollout' },
    { text: 'Troubleshooting', link: '/usage/troubleshooting' },
]

const DEVELOPMENT: DefaultTheme.NavItemWithLink[] = [
    { text: 'Architecture', link: '/development/architecture' },
    { text: 'Developing Rules', link: '/development/developing-rules' },
    { text: 'Plugins', link: '/development/plugins' },
    { text: 'Documentation', link: '/development/documentation' },
]

const REFERENCES: DefaultTheme.NavItemWithLink[] = [
    { text: 'CLI', link: '/reference/cli' },
    { text: 'Rules', link: '/reference/rules' },
    { text: 'Dialects', link: '/reference/dialects' },
    { text: 'Python API', link: '/reference/api' },
    { text: 'Release Notes', link: '/reference/release-notes' },
]

export default defineConfig({
    title: 'SQLFluff',
    description: 'The SQL Linter for Humans',

    head: [
        ['link', { rel: 'icon', href: '/favicon.ico' }]
    ],
    ignoreDeadLinks: true,

    themeConfig: {
        logo: '/logo.svg',

        nav: [
            { text: 'Guide', items: GUIDE },
            { text: 'Configuration', items: CONFIGURATION },
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
            { icon: 'slack', link: 'https://join.slack.com/t/sqlfluff/shared_invite/zt-2qtu36kdt-OS4iONPbQ3aCz2DIbYJdWg' },
        ],

        editLink: {
            pattern: 'https://github.com/sqlfluff/sqlfluff/edit/main/docsv/:path',
            text: 'Edit this page on GitHub'
        },

        footer: {
            message: 'Released under the MIT License.',
            copyright: 'Copyright © 2025 SQLFluff Contributors'
        }
    },

    // Auto-generated redirects from Sphinx conf.py
    rewrites: redirects as Record<string, string>,

    markdown: {
        theme: {
            light: 'github-light',
            dark: 'github-dark'
        },
        lineNumbers: false
    }
})
