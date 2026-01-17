<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import redirects from '../redirects.json'

const router = useRouter()

onMounted(() => {
  // Check if the current path matches any redirect
  const currentPath = window.location.pathname.replace(/^\//, '').replace(/\/$/, '')
  const redirectMap = redirects as Record<string, string>

  if (redirectMap[currentPath]) {
    const target = redirectMap[currentPath]

    // Redirect to the target page
    if (target.includes('#')) {
      window.location.href = `/${target}`
    } else {
      router.go(`/${target}`)
    }
  }
})
</script>

<template>
  <DefaultTheme.Layout />
</template>
