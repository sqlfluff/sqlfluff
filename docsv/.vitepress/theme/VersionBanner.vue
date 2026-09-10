<script setup lang="ts">
/**
 * A notice shown when the reader is not on the documentation they probably
 * want.
 *
 * Most readers arrive from a search engine, which favours whichever version has
 * accumulated links rather than the current one. They cannot act on that unless
 * they are told, so this states the version being read and offers the same page
 * in the recommended one. `useVersions` owns the decision about when a notice is
 * warranted.
 *
 * The manifest is fetched after mount — a build cannot know at compile time
 * which versions were published after it — so this appears slightly after first
 * paint and shifts the page down on the versions which need it. Reserving the
 * space on every version would trade a shift on old builds for wasted space on
 * the current one.
 */
import { onUnmounted, ref, watch } from 'vue'
import { useVersions } from './versions'

const { notice, hrefFor } = useVersions()

const banner = ref<HTMLElement>()
let observer: ResizeObserver | undefined

/**
 * The nav bar, sidebar, content and nav screen all offset themselves by
 * `--vp-layout-top-height`, and the default theme reserves a z-index layer above
 * the nav for this slot, so `layout-top` content is expected to be taken out of
 * flow and to publish its own height. Leaving the notice in flow instead
 * double-counts it: below 960px `.VPNav` is `position: relative` with
 * `top: var(--vp-layout-top-height)`, so it would drop a second banner's height
 * below the banner it already follows.
 *
 * The height is measured rather than hard-coded because the notice wraps to two
 * lines on narrow viewports.
 */
const TOP_HEIGHT = '--vp-layout-top-height'

function clearTopHeight(): void {
    document.documentElement.style.removeProperty(TOP_HEIGHT)
}

watch(banner, (el) => {
    observer?.disconnect()

    if (!el) {
        clearTopHeight()
        return
    }

    observer = new ResizeObserver(([entry]) => {
        // The border-box size rather than `offsetHeight`, which rounds to whole
        // pixels: at text sizes that wrap to a fractional height, rounding down
        // leaves the nav bar overlapping the notice by up to a pixel.
        const height =
            entry?.borderBoxSize?.[0]?.blockSize ?? el.getBoundingClientRect().height

        document.documentElement.style.setProperty(TOP_HEIGHT, `${height}px`)
    })
    observer.observe(el)
})

onUnmounted(() => {
    observer?.disconnect()
    clearTopHeight()
})
</script>

<template>
    <div v-if="notice" ref="banner" class="version-banner" role="status">
        <p class="version-banner__text">
            <template v-if="notice.kind === 'development'">
                You are reading the development documentation, which tracks the
                <code>main</code> branch.
            </template>
            <template v-else>
                You are reading the documentation for
                <strong>{{ notice.current.label }}</strong>, which is not the
                current release.
            </template>

            <!--
              A cross-version link must bypass VitePress's router, which would
              otherwise resolve the target against this build. The router skips
              any link carrying a `target`.
            -->
            <a
                v-if="notice.target"
                class="version-banner__link"
                :href="hrefFor(notice.target)"
                target="_self"
            >Switch to {{ notice.target.label }}</a>
        </p>
    </div>
</template>

<style scoped>
.version-banner {
    position: fixed;
    top: 0;
    right: 0;
    left: 0;
    z-index: var(--vp-z-index-layout-top);
    padding: 0.5rem 1.5rem;
    /* The shared accent is already the amber end of the palette, so it carries a
       cautionary tone without introducing a warning colour the design package
       does not define. */
    background: var(--vp-c-brand-soft);
    border-bottom: 1px solid var(--vp-c-divider);
}

.version-banner__text {
    max-width: var(--sqlfluff-content-width);
    margin: 0 auto;
    color: var(--vp-c-text-1);
    font-size: 14px;
    line-height: 1.5;
    text-align: center;
}

.version-banner__text code {
    font-family: var(--vp-font-family-mono);
    font-size: 0.9em;
}

.version-banner__link {
    margin-left: 0.5rem;
    color: var(--vp-c-brand-1);
    font-weight: 600;
    text-decoration: underline;
    text-underline-offset: 0.18em;
    white-space: nowrap;
}

.version-banner__link:hover {
    color: var(--vp-c-brand-2);
}

/* The notice is fixed, so every line it wraps to is vertical space taken from
   the page for as long as the reader stays on it. */
@media (max-width: 767px) {
    .version-banner {
        padding: 0.45rem 1rem;
    }

    .version-banner__text {
        font-size: 13px;
    }
}
</style>
