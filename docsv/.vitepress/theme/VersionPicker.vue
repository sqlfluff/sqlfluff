<script setup lang="ts">
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useData, useRoute } from 'vitepress'
import { manifestPath, normalizeBase } from '../path-utils'

const props = withDefaults(
    defineProps<{
        showLabel?: boolean
    }>(),
    {
        showLabel: true,
    }
)

interface VersionEntry {
    key: string
    label: string
    path: string
}

interface VersionManifest {
    versions: VersionEntry[]
}

const manifest = ref<VersionManifest | null>(null)
const isOpen = ref(false)
const menuRef = ref<HTMLElement | null>(null)
const rootRef = ref<HTMLElement | null>(null)
const route = useRoute()
const { site } = useData()
const currentPath = ref(normalizeBase(route.path, '/'))

const docsBase = computed(() => normalizeBase(site.value.base, '/'))

const fallbackVersion = computed<VersionEntry[]>(() => {
    const segments = docsBase.value.split('/').filter(Boolean)

    if (segments.length < 2) {
        return []
    }

    const [language, versionKey] = segments

    return [{
        key: versionKey,
        label: versionKey,
        path: `/${language}/${versionKey}/`
    }]
})

const versions = computed(() => {
    if (manifest.value?.versions.length) {
        return manifest.value.versions
    }

    return fallbackVersion.value
})

const selectedVersion = computed(() => {
    return versions.value.find((version) => {
        const versionPath = normalizeBase(version.path, '/')
        return currentPath.value === versionPath || currentPath.value.startsWith(versionPath)
    })
})

async function loadManifest(): Promise<void> {
    if (!fallbackVersion.value.length) {
        return
    }

    const response = await fetch(manifestPath(docsBase.value), {
        headers: {
            Accept: 'application/json'
        }
    })

    if (response.ok) {
        manifest.value = await response.json() as VersionManifest
        return
    }

    throw new Error(`Failed to load versions manifest from ${manifestPath(docsBase.value)}`)
}

function navigateToVersion(version: VersionEntry): void {
    isOpen.value = false
    window.location.href = version.path
}

function toggleMenu(): void {
    isOpen.value = !isOpen.value

    if (!isOpen.value) {
        return
    }

    void nextTick(() => {
        menuRef.value
            ?.querySelector<HTMLButtonElement>('.version-picker__option[aria-checked="true"]')
            ?.focus()
    })
}

function closeMenu(): void {
    isOpen.value = false
}

function onDocumentPointerDown(event: PointerEvent): void {
    if (!rootRef.value?.contains(event.target as Node)) {
        closeMenu()
    }
}

function onDocumentKeyDown(event: KeyboardEvent): void {
    if (event.key === 'Escape') {
        closeMenu()
    }
}

function onSelect(version: VersionEntry): void {
    if (!version) {
        return
    }

    navigateToVersion(version)
}

const currentLabel = computed(() => selectedVersion.value?.label || 'Version')

watch(
    () => route.path,
    (path) => {
        currentPath.value = normalizeBase(path, '/')
        closeMenu()
    }
)

onMounted(async () => {
    currentPath.value = normalizeBase(window.location.pathname || route.path, '/')
    document.addEventListener('pointerdown', onDocumentPointerDown)
    document.addEventListener('keydown', onDocumentKeyDown)

    try {
        await loadManifest()
    } catch (error) {
        console.error(error)
    }
})

onBeforeUnmount(() => {
    document.removeEventListener('pointerdown', onDocumentPointerDown)
    document.removeEventListener('keydown', onDocumentKeyDown)
})
</script>

<template>
    <div v-if="versions.length" ref="rootRef" class="version-picker">
        <span v-if="props.showLabel" class="version-picker__label">Version</span>
        <div class="version-picker__control">
            <button
                class="version-picker__trigger"
                type="button"
                aria-haspopup="menu"
                :aria-expanded="isOpen"
                :aria-label="props.showLabel ? undefined : 'Version'"
                @click="toggleMenu"
                @keydown.down.prevent="toggleMenu"
            >
                <span class="version-picker__current">{{ currentLabel }}</span>
                <span class="version-picker__chevron" :class="{ 'version-picker__chevron--open': isOpen }" aria-hidden="true"></span>
            </button>

            <div
                v-if="isOpen"
                ref="menuRef"
                class="version-picker__menu"
                role="menu"
                aria-label="Available versions"
            >
                <button
                    v-for="version in versions"
                    :key="version.key"
                    class="version-picker__option"
                    type="button"
                    role="menuitemradio"
                    :aria-checked="selectedVersion?.key === version.key"
                    @click="onSelect(version)"
                >
                    <span>{{ version.label }}</span>
                </button>
            </div>
        </div>
    </div>
</template>

<style scoped>
.version-picker {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.5rem 0;
}

.version-picker__label {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--vp-c-text-2);
}

.version-picker__control {
    position: relative;
    display: inline-flex;
    align-items: center;
}

.version-picker__current {
    color: var(--vp-c-text-1);
    font-size: 0.875rem;
    font-weight: 600;
}

.version-picker__trigger {
    display: inline-flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    min-width: 7.5rem;
    height: 2rem;
    padding: 0 0.75rem;
    border: 0;
    border-radius: 999px;
    background: color-mix(in srgb, var(--vp-c-default-soft) 78%, transparent);
    color: var(--vp-c-text-1);
    cursor: pointer;
    transition: background-color 0.2s ease, color 0.2s ease, box-shadow 0.2s ease;
    box-shadow: inset 0 0 0 1px color-mix(in srgb, var(--vp-c-divider) 88%, transparent);
}

.version-picker__trigger:hover {
    background: color-mix(in srgb, var(--vp-c-default-soft) 94%, var(--vp-c-brand-soft));
}

.version-picker__trigger:focus-visible,
.version-picker__option:focus-visible {
    outline: none;
    box-shadow: inset 0 0 0 2px var(--vp-c-brand-1);
}

.version-picker__chevron {
    width: 0.5rem;
    height: 0.5rem;
    border-right: 1.5px solid currentColor;
    border-bottom: 1.5px solid currentColor;
    transform: translateY(-0.1rem) rotate(45deg);
    transition: transform 0.2s ease;
}

.version-picker__chevron--open {
    transform: translateY(0.1rem) rotate(-135deg);
}

.version-picker__menu {
    position: absolute;
    top: calc(100% + 0.125rem);
    left: 0;
    z-index: 30;
    display: flex;
    flex-direction: column;
    min-width: 9rem;
    padding: 0.25rem;
    border-radius: 14px;
    background: color-mix(in srgb, var(--vp-c-bg-elv) 92%, var(--vp-c-bg));
    box-shadow: 0 16px 40px rgba(15, 23, 42, 0.16);
    border: 1px solid color-mix(in srgb, var(--vp-c-divider) 85%, transparent);
}

.version-picker__option {
    display: flex;
    align-items: center;
    width: 100%;
    padding: 0.45rem 0.625rem;
    border: 0;
    border-radius: 10px;
    background: transparent;
    color: var(--vp-c-text-1);
    font-size: 0.875rem;
    font-weight: 600;
    line-height: 1.25rem;
    text-align: left;
    cursor: pointer;
}

.version-picker__option:hover {
    background: color-mix(in srgb, var(--vp-c-brand-soft) 68%, transparent);
}

.version-picker__option[aria-checked="true"] {
    background: color-mix(in srgb, var(--vp-c-brand-soft) 88%, transparent);
    color: var(--vp-c-brand-1);
}

@media (max-width: 960px) {
    .version-picker {
        justify-content: space-between;
    }

    .version-picker__menu {
        left: auto;
        right: 0;
    }
}
</style>
