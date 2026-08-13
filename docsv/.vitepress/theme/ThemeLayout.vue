<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'
import NotFound from './NotFound.vue'
import ThemeSwitcher from './ThemeSwitcher.vue'
import VersionBanner from './VersionBanner.vue'
import VersionPicker from './VersionPicker.vue'
</script>

<template>
  <DefaultTheme.Layout>
    <!-- Above the nav bar rather than inside the article, so the notice reaches
         the home page and the 404 page as well as prose, and so it does not
         narrow to the reading column. -->
    <template #layout-top>
      <VersionBanner />
    </template>

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
