<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'
import NotFound from './NotFound.vue'
import ThemeSwitcher from './ThemeSwitcher.vue'
import VersionPicker from './VersionPicker.vue'
</script>

<template>
  <DefaultTheme.Layout>
    <template #nav-bar-content-after>
      <VersionPicker />
      <ThemeSwitcher />
    </template>

    <template #nav-screen-content-after>
      <VersionPicker variant="list" :show-label="true" class="version-picker--mobile" />
      <ThemeSwitcher class="theme-switcher--mobile" />
    </template>

    <template #not-found>
      <NotFound />
    </template>
  </DefaultTheme.Layout>
</template>

<style scoped>
.version-picker--mobile {
  padding: 0.75rem 0 0;
}

.theme-switcher--mobile {
  padding: 0.75rem 0 0;
}
</style>
