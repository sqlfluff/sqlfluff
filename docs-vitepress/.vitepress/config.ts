import { defineConfig } from 'vitepress'
import type { DefaultTheme } from 'vitepress'

// Auto-generated configurations
import sidebarRules from './sidebar-rules.json'
import redirects from './redirects.json'

const GUIDES: DefaultTheme.NavItemWithLink[] = [
    { text: 'Getting Started', link: '/guide/' },
    { text: 'Installation', link: '/guide/install' },
]

const REFERENCES: DefaultTheme.NavItemWithLink[] = [
    { text: 'Dialect', link: '/reference/dialect' },
    { text: 'Rules', link: '/reference/rules' },
    { text: 'CLI', link: '/reference/cli' },
]

export default defineConfig({
    title: 'SQLFluff',
    description: 'The SQL Linter for Humans',

    head: [
        ['link', { rel: 'icon', href: '/favicon.ico' }]
    ],

    themeConfig: {
        logo: '/logo.svg',

        nav: [
            { text: 'Home', link: '/' },
            {
                text: 'Guide',

                items: [
                    {
                        items: GUIDES,
                    }
                ]
            },
            { text: 'Reference', link: '/reference/rules/' },
            { text: 'Configuration', link: '/configuration/' },
        ],

        sidebar: Object.assign(
            {},
            {
                '/': [
                    {
                        text: 'Guide',
                        items: GUIDES,
                    },
                    {
                        text: 'References',
                        items: REFERENCES,
                    },
                ]
            }),

        search: {
            provider: 'local',
            options: {
                detailedView: true,
            }
        },

        socialLinks: [
            { icon: 'github', link: 'https://github.com/sqlfluff/sqlfluff' }
        ],

        editLink: {
            pattern: 'https://github.com/sqlfluff/sqlfluff/edit/main/docs-vitepress/:path',
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
