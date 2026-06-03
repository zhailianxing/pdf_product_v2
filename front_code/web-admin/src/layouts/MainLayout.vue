<script setup>
import TopBar from '@/components/layout/TopBar.vue'
import SideBar from '@/components/layout/SideBar.vue'
import BreadcrumbNav from '@/components/layout/BreadcrumbNav.vue'
</script>

<template>
  <div class="layout">
    <TopBar />
    <div class="layout-body">
      <SideBar />
      <main class="main-content">
        <BreadcrumbNav />
        <router-view />
      </main>
    </div>
  </div>
</template>

<style scoped>
.layout {
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.layout-body {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.main-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px 20px;
}
</style>
