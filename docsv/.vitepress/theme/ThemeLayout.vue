<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'
import NotFound from './NotFound.vue'
import VersionPicker from './VersionPicker.vue'
</script>

<template>
  <DefaultTheme.Layout>
    <template #nav-bar-content-after>
      <VersionPicker :show-label="false" :inline="true" />
    </template>

    <template #nav-screen-content-after>
      <VersionPicker class="version-picker--mobile" />
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
</style>
