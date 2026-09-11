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
    /** Which toolchain built it. Archived pre-cutover versions are Sphinx. */
    builder?: 'vitepress' | 'sphinx'
    /**
     * Whether the picker offers it. Unlisted versions stay published and
     * reachable by URL; they are listed on the archive index page instead.
     */
    listed?: boolean
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

/**
 * True when the picker should offer this version.
 *
 * Absent means listed, so a manifest written before the flag existed still
 * renders in full rather than emptying the picker.
 */
export function isListed(entry: VersionEntry): boolean {
    return entry.listed !== false
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
 *
 * Across the Sphinx and VitePress boundary the trade reverses, so the path is
 * dropped and the link goes to the target version's root. The two builders lay
 * out URLs differently — `configuration/index.html` against `configuration/` —
 * and the docs were restructured in the rewrite, with the rules reference going
 * from one page to many. Carrying the path across is not a near miss but a
 * certain 404, which makes losing your place the cheaper of the two.
 */
export function versionHref(
    entry: VersionEntry,
    pagePath: string,
    currentBuilder?: VersionEntry['builder']
): string {
    const base = normalizeBase(entry.path, '/')

    if (entry.builder && currentBuilder && entry.builder !== currentBuilder) {
        return base
    }

    return base + pagePath
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
    /** The versions the picker offers: the listed ones, plus the current one. */
    entries: Ref<VersionEntry[]>
    /** The version this build was published as, if it is versioned at all. */
    current: Ref<VersionEntry | null>
    channels: Ref<VersionEntry[]>
    releases: Ref<VersionEntry[]>
    /** The current page's path within its version, for cross-version links. */
    pagePath: ComputedRef<string>
    notice: Ref<VersionNotice | null>
    /** A link to the same page in another version, from this one. */
    hrefFor: (entry: VersionEntry) => string
    /** The archive index page, or null when there is no manifest to index. */
    allVersionsHref: Ref<string | null>
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

    /** Every published version, channels before releases. */
    const published = computed<VersionEntry[]>(() => {
        const versions = manifest.value?.versions

        if (!versions?.length) return fallback.value

        // `version_sort_key` in assemble-site.py already orders channels first
        // and then releases newest-first. Partitioning preserves that order
        // within each group, which the "newest release" checks below rely on.
        return [
            ...versions.filter(isChannel),
            ...versions.filter((entry) => !isChannel(entry)),
        ]
    })

    const current = computed(
        () => published.value.find((entry) => entry.key === currentKey.value) ?? null
    )

    /**
     * The versions the picker offers.
     *
     * Only one release per series is listed. That is what every comparable
     * project does — Node.js hosts every patch and lists none of them — and a
     * scrolling list of a hundred patch releases is the failure mode this
     * replaces.
     *
     * The current version is added back whenever it was left out. Most readers
     * arrive on an old version from a search engine, and a control which does
     * not name the version they are reading looks broken rather than curated.
     */
    const entries = computed<VersionEntry[]>(() =>
        published.value.filter(
            (entry) => isListed(entry) || entry.key === currentKey.value
        )
    )

    const channels = computed(() => entries.value.filter(isChannel))
    const releases = computed(() => entries.value.filter((e) => !isChannel(e)))

    /**
     * Every published release, listed or not.
     *
     * The notice below asks whether the reader is on the newest release, which
     * is a question about what exists rather than about what the picker shows.
     * Asking it of the listed set would leave a reader on an unlisted patch
     * unwarned whenever nothing newer happened to be listed.
     */
    const allReleases = computed(() =>
        published.value.filter((entry) => !isChannel(entry))
    )

    /** The release the `stable` channel points at, when it is published. */
    const stableRelease = computed(() => {
        const key = manifest.value?.stable
        return allReleases.value.find((entry) => entry.key === key) ?? null
    })

    /** Where a reader on an unsuitable version should be sent instead. */
    const recommended = computed<VersionEntry | null>(() => {
        const stableChannel = published.value.find((entry) => entry.key === 'stable')
        return stableRelease.value ?? stableChannel ?? allReleases.value[0] ?? null
    })

    const notice = computed<VersionNotice | null>(() => {
        const entry = current.value

        // Nothing to warn about when there is nowhere else to go. This also
        // keeps the banner off a single-channel deployment such as the beta
        // site, where every build is `latest`.
        if (!entry || published.value.length < 2) return null

        const target = recommended.value
        const alternative = target && target.key !== entry.key ? target : null

        // `latest` tracks main, so it is worth flagging even when it is the
        // channel the site root redirects to.
        if (entry.key === 'latest' || entry.prerelease) {
            return { kind: 'development', current: entry, target: alternative }
        }

        if (isChannel(entry)) return null

        // Releases are ordered newest-first, so anything but the first is old.
        if (allReleases.value.indexOf(entry) > 0) {
            return { kind: 'outdated', current: entry, target: alternative }
        }

        return null
    })

    /**
     * A cross-version link from this page, which is always the same two
     * arguments at every call site: the page the reader is on, and the builder
     * they are on it in.
     */
    function hrefFor(entry: VersionEntry): string {
        return versionHref(entry, pagePath.value, current.value?.builder)
    }

    /**
     * Where the versions the picker leaves out stay discoverable.
     *
     * `assemble-site.py` writes this page at the language root on every publish,
     * so it exists whenever a manifest does. Without one there is nothing to
     * index, which is also the local-development case.
     */
    const allVersionsHref = computed(() =>
        manifest.value?.versions?.length
            ? `${languageRoot(docsBase.value)}versions.html`
            : null
    )

    onMounted(() => {
        if (currentKey.value) void loadManifest(docsBase.value)
    })

    return {
        entries,
        current,
        channels,
        releases,
        pagePath,
        notice,
        hrefFor,
        allVersionsHref,
    }
}
