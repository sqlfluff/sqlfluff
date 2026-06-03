<script setup lang="ts">
import DefaultTheme from 'vitepress/theme'
import NotFound from './NotFound.vue'
import VersionPicker from './VersionPicker.vue'
</script>

<template>
  <DefaultTheme.Layout>
    <template #layout-top>
      <VersionPicker />
    </template>

    <template #not-found>
      <NotFound />
    </template>
  </DefaultTheme.Layout>
</template>