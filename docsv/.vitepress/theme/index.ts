import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import redirects from '../redirects.json'
import NotFound from './NotFound.vue'

export default {
    extends: DefaultTheme,
    Layout: () => {
        return h(DefaultTheme.Layout, null, {
            'not-found': () => h(NotFound)
        })
    },
    enhanceApp({ app, router, siteData }) {
        // Only run in browser
        if (typeof window === 'undefined') return

        // Handle redirects on route change
        router.onBeforeRouteChange = (to) => {
            // Clean the path (remove leading/trailing slashes)
            const cleanPath = to.replace(/^\//, '').replace(/\/$/, '')

            // Check if redirect exists
            const redirectMap = redirects as Record<string, string>
            if (redirectMap[cleanPath]) {
                const target = redirectMap[cleanPath]

                // Handle anchor links - use window.location.href for simplicity
                if (target.includes('#')) {
                    window.location.href = `/${target}`
                } else {
                    router.go(`/${target}`)
                }
                return false // Cancel default navigation
            }
        }
    }
} satisfies Theme
