<script setup lang="ts">
/**
 * The shared three-state theme control from the design package.
 *
 * This renders the markup documented in the package's INTEGRATION.md and
 * nothing else: the shared `theme.js` bootstrap owns the preference, delegates
 * clicks from the document, and stores the choice in a cookie which follows the
 * reader across SQLFluff subdomains. VitePress's own appearance handling is
 * disabled in config so there is a single owner of the theme.
 *
 * The only piece not handled by delegation is `aria-pressed` on controls
 * rendered after the last theme change, which is what the subscription below
 * keeps in sync.
 */
import { onMounted, onUnmounted, ref, useId } from 'vue'

type Preference = 'auto' | 'light' | 'dark'

interface SqlfluffTheme {
  get(): Preference
  subscribe(listener: (preference: Preference) => void): () => void
}

// `icon` is listed rather than derived from `value`: the shared stylesheet names
// the automatic state's icon `system` while the stored preference is `auto`.
const OPTIONS: { value: Preference; icon: string; label: string; title: string }[] = [
  { value: 'auto', icon: 'system', label: 'Use system theme', title: 'System theme' },
  { value: 'light', icon: 'light', label: 'Use light theme', title: 'Light theme' },
  { value: 'dark', icon: 'dark', label: 'Use dark theme', title: 'Dark theme' },
]

const preference = ref<Preference>('auto')
// The control renders in both the nav bar and the mobile nav screen, so the
// label needs a unique id per instance rather than the fixed one in the docs.
const labelId = useId()
let unsubscribe: (() => void) | undefined

onMounted(() => {
  const theme = (window as unknown as { sqlfluffTheme?: SqlfluffTheme }).sqlfluffTheme
  if (!theme) return

  unsubscribe = theme.subscribe((next) => {
    preference.value = next
  })
})

onUnmounted(() => unsubscribe?.())
</script>

<template>
  <div class="sqlfluff-theme-control">
    <span :id="labelId" class="sqlfluff-visually-hidden">Colour theme</span>
    <div
      class="sqlfluff-theme-switcher"
      role="group"
      :aria-labelledby="labelId"
    >
      <button
        v-for="option in OPTIONS"
        :key="option.value"
        type="button"
        :data-sqlfluff-theme-value="option.value"
        :aria-label="option.label"
        :title="option.title"
        :aria-pressed="String(preference === option.value)"
      >
        <span
          class="sqlfluff-theme-icon"
          :class="`sqlfluff-theme-icon-${option.icon}`"
          aria-hidden="true"
        ></span>
      </button>
    </div>
  </div>
</template>
