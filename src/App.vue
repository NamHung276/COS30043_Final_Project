<script setup>
import { ref, provide } from "vue";
import Navbar from "./components/Navbar.vue";
import Footer from "./components/Footer.vue";
import ScrollToTop from "./components/ScrollToTop.vue";
import ToastNotification from "./components/ToastNotification.vue";
import ChatbotWidget from "./components/ChatbotWidget.vue";

const toastRef = ref(null);

// Provide toast globally so any child component can use it
provide("toast", {
  show(message, type = "info", duration = 3000) {
    toastRef.value?.show(message, type, duration);
  },
});
</script>

<template>
  <!-- Skip Navigation Link (WCAG 2.4.1) -->
  <a href="#main-content" class="skip-link">Skip to main content</a>

  <Navbar />

  <main id="main-content" style="flex: 1; min-width: 0">
    <router-view v-slot="{ Component }">
      <transition name="page" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>
  </main>

  <Footer />
  <ScrollToTop />
  <ToastNotification ref="toastRef" />
  <ChatbotWidget />
</template>
