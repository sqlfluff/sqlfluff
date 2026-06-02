import { h } from 'vue'
import DefaultTheme from 'vitepress/theme'
import type { Theme } from 'vitepress'
import redirects from '../redirects.json'
import { normalizeBase, normalizePath, toRedirectPath } from '../path-utils'
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

        const docsBase = normalizeBase(siteData.value.base)

        // Handle redirects on route change
        router.onBeforeRouteChange = (to) => {
            const cleanPath = normalizePath(to, docsBase)

            // Check if redirect exists
            const redirectMap = redirects as Record<string, string>
            if (redirectMap[cleanPath]) {
                window.location.href = toRedirectPath(redirectMap[cleanPath], docsBase)
                return false // Cancel default navigation
            }
        }
    }
} satisfies Theme
