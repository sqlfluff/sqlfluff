<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useData, useRoute } from 'vitepress'
import { manifestPath, normalizeBase } from '../path-utils'

const props = withDefaults(
    defineProps<{
        inline?: boolean
        showLabel?: boolean
    }>(),
    {
        inline: false,
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
const route = useRoute()
const { site } = useData()
const currentPath = ref('/')

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

function onChange(event: Event): void {
    const target = event.target as HTMLSelectElement
    const version = versions.value.find((entry) => entry.key === target.value)

    if (!version) {
        return
    }

    window.location.href = version.path
}

const currentLabel = computed(() => selectedVersion.value?.label || 'Version')

onMounted(async () => {
    currentPath.value = normalizeBase(window.location.pathname || route.path, '/')

    try {
        await loadManifest()
    } catch (error) {
        console.error(error)
    }
})
</script>

<template>
    <div v-if="versions.length" :class="['version-picker', { 'version-picker--inline': props.inline }]">
        <label v-if="props.showLabel" class="version-picker__label" for="version-picker-select">Version</label>
        <div class="version-picker__control">
            <span v-if="props.inline" class="version-picker__current">{{ currentLabel }}</span>
            <select
                id="version-picker-select"
                class="version-picker__select"
                :value="selectedVersion?.key"
                :aria-label="props.showLabel ? undefined : 'Version'"
                @change="onChange"
            >
                <option
                    v-for="version in versions"
                    :key="version.key"
                    :value="version.key"
                >
                    {{ version.label }}
                </option>
            </select>
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

.version-picker--inline {
    padding: 0;
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

.version-picker__control::after {
    position: absolute;
    right: 0.7rem;
    width: 0.45rem;
    height: 0.45rem;
    border-right: 1.5px solid var(--vp-c-text-2);
    border-bottom: 1.5px solid var(--vp-c-text-2);
    content: "";
    pointer-events: none;
    transform: translateY(-0.15rem) rotate(45deg);
}

.version-picker__current {
    position: absolute;
    left: 0.7rem;
    color: var(--vp-c-text-1);
    font-size: 0.875rem;
    font-weight: 600;
    pointer-events: none;
}

.version-picker__select {
    min-width: 7.5rem;
    height: 2rem;
    padding: 0.35rem 2rem 0.35rem 0.7rem;
    border: 1px solid var(--vp-c-divider);
    border-radius: 6px;
    appearance: none;
    background: var(--vp-c-bg-soft);
    color: var(--vp-c-text-1);
    font-size: 0.875rem;
    line-height: 1.25rem;
}

.version-picker--inline .version-picker__select {
    min-width: 6.5rem;
    color: transparent;
    background: transparent;
}

.version-picker__select:focus {
    outline: 2px solid var(--vp-c-brand-1);
    outline-offset: 2px;
}

@media (max-width: 960px) {
    .version-picker {
        justify-content: space-between;
    }
}
</style>
