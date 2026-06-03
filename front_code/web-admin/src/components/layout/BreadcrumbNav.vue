<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const breadcrumbs = computed(() => route.meta.breadcrumb ?? ['首页'])
</script>

<template>
  <nav class="breadcrumb">
    <template v-for="(item, index) in breadcrumbs" :key="index">
      <span :class="['crumb', { current: index === breadcrumbs.length - 1 }]">{{ item }}</span>
      <span v-if="index < breadcrumbs.length - 1" class="separator">/</span>
    </template>
  </nav>
</template>

<style scoped>
.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--color-text-muted);
  margin-bottom: 16px;
}

.crumb.current {
  color: var(--color-text);
  font-weight: 500;
}

.separator {
  color: var(--color-border);
}
</style>
