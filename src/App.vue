// src/App.vue
<script setup>
import { ref, provide } from 'vue'
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'
import ScrollToTop from './components/ScrollToTop.vue'
import ToastNotification from './components/ToastNotification.vue'

const toastRef = ref(null)

// Provide toast globally so any child component can use it
provide('toast', {
  show(message, type = 'info', duration = 3000) {
    toastRef.value?.show(message, type, duration)
  }
})
</script>

<template>
  <Navbar />

  <div class="container mt-4" style="flex: 1;">
    <router-view v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </div>

  <Footer />
  <ScrollToTop />
  <ToastNotification ref="toastRef" />
</template>