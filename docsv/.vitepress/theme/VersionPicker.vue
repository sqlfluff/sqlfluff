<script setup lang="ts">
/**
 * The documentation version picker.
 *
 * This is a disclosure rather than a `<select>`. A native select cannot style
 * its popup, so the closed control and the open list were drawn in two
 * different visual languages — and VitePress's `base.css` strips the native
 * chevron from every select, which left the closed state with no affordance at
 * all. Both states are now ours to draw, and they follow the appearance of the
 * flyout menus the default theme puts next to this one in the nav bar.
 *
 * A disclosure of links is used in preference to `role="menu"`: menu semantics
 * oblige us to reimplement arrow-key focus movement, typeahead and Home/End,
 * whereas a list of links after the trigger in DOM order is already reachable
 * with Tab. Real links also restore middle-click, copy-link and open-in-new-tab,
 * which the old change handler could not support.
 */
import { computed, onUnmounted, ref, useId, watch } from 'vue'
import {
    isChannel,
    useVersions,
    versionTitle,
    type VersionEntry,
} from './versions'

const props = withDefaults(
    defineProps<{
        /**
         * `flyout` overlays the panel, for the nav bar. `list` keeps it in flow
         * and full width, for the mobile nav screen.
         */
        variant?: 'flyout' | 'list'
        showLabel?: boolean
    }>(),
    {
        variant: 'flyout',
        showLabel: false,
    }
)

const { entries, current, channels, releases, hrefFor, allVersionsHref } =
    useVersions()

const open = ref(false)
const root = ref<HTMLElement>()
const trigger = ref<HTMLButtonElement>()
const panelId = useId()

/** Headings only earn their space when there is more than one group. */
const showGroupTitles = computed(
    () => channels.value.length > 0 && releases.value.length > 0
)

/**
 * Until the manifest arrives there is only the version this build was published
 * as, and nothing to switch to. The version is still worth stating, so it
 * renders as a label rather than a control which would open an empty menu — the
 * state a failed manifest request leaves this in permanently.
 */
const interactive = computed(() => entries.value.length > 1)

/**
 * Releases get a `v` so the trigger reads as a version rather than a bare
 * number; the channel names already read as words.
 */
const triggerLabel = computed(() => {
    const entry = current.value
    if (!entry) return ''
    return isChannel(entry) ? entry.label : `v${entry.label}`
})

const dateFormat = new Intl.DateTimeFormat('en', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
    // `published_at` is a plain date, which parses as UTC midnight. Formatting
    // in the reader's zone would show the previous day west of Greenwich.
    timeZone: 'UTC',
})

/** Secondary line for an entry, or `null` when there is nothing to add. */
function entryMeta(entry: VersionEntry): string | null {
    if (!entry.published_at) return null

    const published = new Date(entry.published_at)
    if (Number.isNaN(published.getTime())) return null

    return dateFormat.format(published)
}

function close(): void {
    open.value = false
}

function onDocumentPointerDown(event: PointerEvent): void {
    if (!root.value?.contains(event.target as Node)) close()
}

watch(open, (isOpen) => {
    if (isOpen) {
        document.addEventListener('pointerdown', onDocumentPointerDown)
    } else {
        document.removeEventListener('pointerdown', onDocumentPointerDown)
    }
})

onUnmounted(() => {
    document.removeEventListener('pointerdown', onDocumentPointerDown)
})

function onKeydown(event: KeyboardEvent): void {
    if (event.key !== 'Escape' || !open.value) return

    close()
    // Escape must not also close the surrounding nav screen.
    event.stopPropagation()
    trigger.value?.focus()
}
</script>

<template>
    <div
        v-if="current"
        ref="root"
        class="version-picker"
        :class="`version-picker--${props.variant}`"
        @keydown="onKeydown"
    >
        <span v-if="props.showLabel" class="version-picker__label">Version</span>

        <button
            v-if="interactive"
            ref="trigger"
            type="button"
            class="version-picker__trigger"
            :aria-expanded="open"
            :aria-controls="panelId"
            @click="open = !open"
        >
            <span class="version-picker__trigger-text">
                <span class="sqlfluff-visually-hidden">Documentation version:</span>
                {{ triggerLabel }}
            </span>
            <span class="vpi-chevron-down version-picker__chevron" aria-hidden="true" />
        </button>

        <template v-else>
            <span class="version-picker__static">
                <span class="sqlfluff-visually-hidden">Documentation version:</span>
                {{ triggerLabel }}
            </span>

            <!--
              With nothing to switch to there is no panel, but the archive index
              still has to be reachable: if every other version is unlisted this
              is the reader's only route to them. Rendered as a link rather than
              as a one-item dropdown.
            -->
            <a
                v-if="allVersionsHref"
                class="version-picker__item version-picker__item--all version-picker__all-static"
                :href="allVersionsHref"
                target="_self"
            >
                <span>All versions</span>
                <span aria-hidden="true">&rarr;</span>
            </a>
        </template>

        <div v-if="interactive" :id="panelId" class="version-picker__panel" :hidden="!open">
            <template v-for="(group, index) in [channels, releases]" :key="index">
                <div v-if="group.length" class="version-picker__group">
                    <p v-if="showGroupTitles" class="version-picker__group-title">
                        {{ index === 0 ? 'Channels' : 'Releases' }}
                    </p>

                    <!--
                      `target` is load-bearing. VitePress's router intercepts
                      every same-origin link and would resolve another version's
                      page against this build; it skips any link which carries a
                      `target`, so this forces a real navigation.
                    -->
                    <a
                        v-for="entry in group"
                        :key="entry.key"
                        class="version-picker__item"
                        :class="{ 'is-current': entry.key === current.key }"
                        :href="hrefFor(entry)"
                        :aria-current="entry.key === current.key ? 'page' : undefined"
                        target="_self"
                        @click="close"
                    >
                        <span class="version-picker__item-title">
                            {{ versionTitle(entry) }}
                            <span v-if="entry.prerelease" class="version-picker__tag">
                                pre-release
                            </span>
                        </span>
                        <span
                            v-if="entryMeta(entry)"
                            class="version-picker__item-meta"
                        >{{ entryMeta(entry) }}</span>
                    </a>
                </div>
            </template>

            <!--
              The way to reach the versions this list leaves out. In its own
              group at the end, so it reads as an escape hatch rather than as
              another version to switch to.
            -->
            <div v-if="allVersionsHref" class="version-picker__group">
                <a
                    class="version-picker__item version-picker__item--all"
                    :href="allVersionsHref"
                    target="_self"
                    @click="close"
                >
                    <span>All versions</span>
                    <span aria-hidden="true">&rarr;</span>
                </a>
            </div>
        </div>
    </div>
</template>

<style scoped>
.version-picker {
    position: relative;
}

/* The trigger takes the theme switcher's height, radius and surface so the two
   read as one cluster of controls, while the panel below follows the default
   theme's own flyout menus. Each half matches what sits nearest to it. */
.version-picker__trigger {
    display: flex;
    height: 36px;
    align-items: center;
    gap: 0.35rem;
    padding: 0 0.6rem;
    color: var(--vp-c-text-1);
    font-size: 14px;
    font-weight: 500;
    background: var(--vp-c-bg-soft);
    border: 1px solid var(--vp-c-divider);
    border-radius: var(--sqlfluff-radius-md);
    transition: color 0.25s, border-color 0.25s;
}

.version-picker__trigger:hover {
    color: var(--vp-c-brand-1);
    border-color: var(--vp-c-border);
}

.version-picker__trigger-text,
.version-picker__static {
    font-variant-numeric: tabular-nums;
}

/* No border or chevron: it is a statement of fact, not something to press. It
   keeps the trigger's height and side padding so gaining the control shifts the
   row as little as possible. */
.version-picker__static {
    display: flex;
    height: 36px;
    align-items: center;
    padding: 0 0.6rem;
    color: var(--vp-c-text-2);
    font-size: 14px;
    font-weight: 500;
}

.version-picker__chevron {
    width: 14px;
    height: 14px;
    color: var(--vp-c-text-2);
    transition: transform 0.25s;
}

/* `vpi-chevron-down` is a right-pointing glyph already turned by `rotate(90deg)`,
   so pointing it up means replacing that rotation rather than adding to it. */
.version-picker__trigger[aria-expanded='true'] .version-picker__chevron {
    transform: rotate(270deg);
}

.version-picker__panel {
    padding: 12px;
    background: var(--vp-c-bg-elv);
    border: 1px solid var(--vp-c-divider);
    /* Matches VPMenu, so this panel and the nav menus beside it agree. */
    border-radius: 12px;
    box-shadow: var(--vp-shadow-3);
}

.version-picker__panel[hidden] {
    display: none;
}

.version-picker--flyout .version-picker__panel {
    position: absolute;
    top: calc(100% + 12px);
    right: 0;
    z-index: 30;
    min-width: 15rem;
    max-height: calc(100vh - var(--vp-nav-height) - 2rem);
    overflow-y: auto;
}

.version-picker__group + .version-picker__group {
    margin-top: 12px;
    padding-top: 12px;
    border-top: 1px solid var(--vp-c-divider);
}

.version-picker__group-title {
    margin: 0 0 4px;
    padding: 0 12px;
    color: var(--vp-c-text-2);
    font-size: 12px;
    font-weight: 500;
    line-height: 20px;
}

.version-picker__item {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 1rem;
    padding: 4px 12px;
    border-radius: 6px;
    color: var(--vp-c-text-1);
    font-size: 14px;
    font-weight: 500;
    line-height: 24px;
    text-decoration: none;
    white-space: nowrap;
    transition: background-color 0.25s, color 0.25s;
}

.version-picker__item:hover {
    color: var(--vp-c-brand-1);
    background-color: var(--vp-c-default-soft);
}

.version-picker__item.is-current {
    color: var(--vp-c-brand-1);
}

.version-picker__item-title {
    font-variant-numeric: tabular-nums;
}

/* Weight as well as colour, so the current version is still distinguishable
   without relying on hue. */
.version-picker__item.is-current .version-picker__item-title {
    font-weight: 700;
}

.version-picker__item-meta {
    color: var(--vp-c-text-2);
    font-size: 12px;
    font-weight: 400;
}

.version-picker__item--all {
    color: var(--vp-c-brand-1);
}

/* Outside the panel it has no surface behind it, so it needs the panel's own
   left padding removed to line up with the static label above it. */
.version-picker__all-static {
    padding-left: 0;
    font-size: 13px;
}

.version-picker__tag {
    margin-left: 0.35rem;
    padding: 0 0.35rem;
    color: var(--vp-c-text-2);
    font-size: 11px;
    font-weight: 500;
    background: var(--vp-c-default-soft);
    border-radius: var(--sqlfluff-radius-sm);
}

/* Nav screen: the panel sits in flow under a full-width trigger, matching how
   the default theme expands its own nav groups there. */
.version-picker--list .version-picker__label {
    display: block;
    margin-bottom: 0.5rem;
    color: var(--vp-c-text-2);
    font-size: 14px;
    font-weight: 500;
}

.version-picker--list .version-picker__trigger {
    width: 100%;
    justify-content: space-between;
}

.version-picker--list .version-picker__panel {
    margin-top: 0.5rem;
}
</style>
