/**
 * Shared access to the published versions manifest.
 *
 * `scripts/assemble-site.py` writes the manifest at the language root, outside
 * any single version's base, so a build learns about versions published after
 * it. That makes the manifest a runtime fetch rather than build-time data, and
 * it is the reason the picker and the banner can only render after mount.
 *
 * The fetch is cached at module scope so the two components share one request.
 * Nothing populates the cache during SSR — the fetch only runs from `onMounted`
 * — so this module holds no cross-request state when the site is prerendered.
 */
import { computed, onMounted, ref, type ComputedRef, type Ref } from 'vue'
import { useData, useRoute } from 'vitepress'
import { languageRoot, manifestPath, normalizeBase } from '../path-utils'

export interface VersionEntry {
    key: string
    label: string
    /** Display title from the publishing workflow; `--title` is optional. */
    title?: string | null
    path: string
    kind?: 'channel' | 'release'
    prerelease?: boolean
    published_at?: string
}

export interface VersionManifest {
    /** The channel the site root redirects to. */
    default?: string
    latest?: string
    /** The release the `stable` channel currently points at. */
    stable?: string
    versions: VersionEntry[]
}

/** The mutable channels, which name a moving target rather than a release. */
const CHANNEL_KEYS = new Set(['latest', 'stable'])

const manifest = ref<VersionManifest | null>(null)
let pending: Promise<void> | null = null

async function fetchManifest(base: string): Promise<void> {
    const url = manifestPath(base)
    const response = await fetch(url, { headers: { Accept: 'application/json' } })

    if (!response.ok) {
        throw new Error(`Failed to load versions manifest from ${url}`)
    }

    manifest.value = (await response.json()) as VersionManifest
}

/** Load the manifest at most once per page load. */
function loadManifest(base: string): Promise<void> {
    if (!pending) {
        pending = fetchManifest(base).catch((error) => {
            // A missing manifest is expected for an unversioned build, such as
            // local development. Both consumers degrade to rendering nothing.
            console.error(error)
        })
    }

    return pending
}

/** True for a mutable channel rather than a pinned release. */
export function isChannel(entry: VersionEntry): boolean {
    return entry.kind === 'channel' || CHANNEL_KEYS.has(entry.key)
}

/** The line a reader identifies a version by. */
export function versionTitle(entry: VersionEntry): string {
    return entry.title || entry.label || entry.key
}

/**
 * Build a cross-version link which keeps the reader on the same page.
 *
 * The page may not exist in the target version, in which case that version's
 * own 404 handling takes over. That is a better trade than always landing on
 * the target's home page, which is a certain loss of place rather than a
 * possible one.
 */
export function versionHref(
    entry: VersionEntry,
    pagePath: string
): string {
    return normalizeBase(entry.path, '/') + pagePath
}

export type NoticeKind = 'development' | 'outdated'

export interface VersionNotice {
    kind: NoticeKind
    /** The version the reader is on. */
    current: VersionEntry
    /** Where to send them instead, when there is somewhere better. */
    target: VersionEntry | null
}

export interface UseVersions {
    /** Every published version, channels before releases. */
    entries: Ref<VersionEntry[]>
    /** The version this build was published as, if it is versioned at all. */
    current: Ref<VersionEntry | null>
    channels: Ref<VersionEntry[]>
    releases: Ref<VersionEntry[]>
    /** The current page's path within its version, for cross-version links. */
    pagePath: ComputedRef<string>
    notice: Ref<VersionNotice | null>
}

export function useVersions(): UseVersions {
    const { site } = useData()
    const route = useRoute()
    const docsBase = computed(() => normalizeBase(site.value.base, '/'))

    /**
     * Taken from the route rather than read once from `window`, so cross-version
     * links keep pointing at the page the reader is actually on after a
     * client-side navigation.
     */
    const pagePath = computed(() => {
        const base = docsBase.value
        const path = route.path

        return path.startsWith(base) ? path.slice(base.length) : ''
    })

    /**
     * The version key comes from the build's own base rather than the browser
     * URL: the base is what the build was published as, so it is correct before
     * the manifest arrives and during prerendering.
     */
    const currentKey = computed(() => {
        const segments = docsBase.value.split('/').filter(Boolean)
        return segments.length < 2 ? null : segments[1]
    })

    /**
     * Stand in for the manifest so an unversioned or offline build still names
     * the version it is, rather than showing an empty control.
     */
    const fallback = computed<VersionEntry[]>(() => {
        if (!currentKey.value) return []

        return [{
            key: currentKey.value,
            label: currentKey.value,
            path: `${languageRoot(docsBase.value)}${currentKey.value}/`,
        }]
    })

    const entries = computed<VersionEntry[]>(() => {
        const published = manifest.value?.versions

        if (!published?.length) return fallback.value

        // `version_sort_key` in assemble-site.py already orders channels first
        // and then releases newest-first. Partitioning preserves that order
        // within each group, which the "newest release" checks below rely on.
        return [
            ...published.filter(isChannel),
            ...published.filter((entry) => !isChannel(entry)),
        ]
    })

    const channels = computed(() => entries.value.filter(isChannel))
    const releases = computed(() => entries.value.filter((e) => !isChannel(e)))

    const current = computed(
        () => entries.value.find((entry) => entry.key === currentKey.value) ?? null
    )

    /** The release the `stable` channel points at, when it is published. */
    const stableRelease = computed(() => {
        const key = manifest.value?.stable
        return releases.value.find((entry) => entry.key === key) ?? null
    })

    /** Where a reader on an unsuitable version should be sent instead. */
    const recommended = computed<VersionEntry | null>(() => {
        const stableChannel = channels.value.find((entry) => entry.key === 'stable')
        return stableRelease.value ?? stableChannel ?? releases.value[0] ?? null
    })

    const notice = computed<VersionNotice | null>(() => {
        const entry = current.value

        // Nothing to warn about when there is nowhere else to go. This also
        // keeps the banner off a single-channel deployment such as the beta
        // site, where every build is `latest`.
        if (!entry || entries.value.length < 2) return null

        const target = recommended.value
        const alternative = target && target.key !== entry.key ? target : null

        // `latest` tracks main, so it is worth flagging even when it is the
        // channel the site root redirects to.
        if (entry.key === 'latest' || entry.prerelease) {
            return { kind: 'development', current: entry, target: alternative }
        }

        if (isChannel(entry)) return null

        // Releases are ordered newest-first, so anything but the first is old.
        if (releases.value.indexOf(entry) > 0) {
            return { kind: 'outdated', current: entry, target: alternative }
        }

        return null
    })

    onMounted(() => {
        if (currentKey.value) void loadManifest(docsBase.value)
    })

    return { entries, current, channels, releases, pagePath, notice }
}
