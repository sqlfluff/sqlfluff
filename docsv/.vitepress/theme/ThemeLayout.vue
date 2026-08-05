<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'
import NotFound from './NotFound.vue'
import VersionPicker from './VersionPicker.vue'
</script>

<template>
  <DefaultTheme.Layout>
    <template #nav-bar-content-before>
      <VersionPicker class="version-picker--desktop" :show-label="false" />
    </template>

    <template #nav-screen-content-before>
      <VersionPicker class="version-picker--mobile" />
    </template>

    <template #not-found>
      <NotFound />
    </template>
  </DefaultTheme.Layout>
</template>

<style scoped>
.version-picker--desktop {
  display: none;
  margin-right: auto;
  margin-left: 0.75rem;
}

.version-picker--mobile {
  display: flex;
  padding: 0 0 1rem;
}

@media (min-width: 768px) {
  .version-picker--desktop {
    display: flex;
  }

  .version-picker--mobile {
    display: none;
  }
}
</style>
