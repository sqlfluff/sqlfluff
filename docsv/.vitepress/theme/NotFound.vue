<script setup lang="ts">
import { onMounted } from 'vue'
import { useData, useRouter } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import redirects from '../redirects.json'
import { normalizeBase, normalizePath, toRedirectPath } from '../path-utils'

const router = useRouter()
const { site } = useData()

onMounted(() => {
  // Check if the current path matches any redirect
  const docsBase = normalizeBase(site.value.base)
  const currentPath = normalizePath(window.location.pathname, docsBase)
  const redirectMap = redirects as Record<string, string>

  if (redirectMap[currentPath]) {
    router.go(toRedirectPath(redirectMap[currentPath], docsBase))
  }
})
</script>

<template>
  <DefaultTheme.Layout />
</template>
