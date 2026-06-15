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
                <select
                        id="version-picker-select"
                        class="version-picker__select"
                        :value="selectedVersion?.key"
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

.version-picker__select {
    min-width: 7rem;
    padding: 0.35rem 2rem 0.35rem 0.65rem;
    border: 1px solid var(--vp-c-divider);
    border-radius: 999px;
    background: var(--vp-c-bg-soft);
    color: var(--vp-c-text-1);
    font-size: 0.875rem;
}

.version-picker--inline .version-picker__select {
    min-width: 5.5rem;
    padding-right: 1.5rem;
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
