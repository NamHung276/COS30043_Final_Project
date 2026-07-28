<script setup>
import { ref, provide, onMounted, watch } from "vue";
import Navbar from "./components/Navbar.vue";
import Footer from "./components/Footer.vue";
import ScrollToTop from "./components/ScrollToTop.vue";
import ToastNotification from "./components/ToastNotification.vue";
import ChatbotWidget from "./components/ChatbotWidget.vue";
import { useAuthStore } from "./stores/useAuthStore";
import { useWishlistStore } from "./stores/useWishlistStore";

const toastRef = ref(null);

// Provide toast globally so any child component can use it
provide("toast", {
  show(message, type = "info", duration = 3000) {
    toastRef.value?.show(message, type, duration);
  },
});

// ── Single global auth listener ──────────────────────────────────────────────
// Previously every authenticated view registered its own onAuthStateChanged.
// Now we register exactly ONE listener here for the entire application lifetime.
const authStore = useAuthStore();
const wishlistStore = useWishlistStore();

onMounted(() => {
  authStore.init();
});

// When auth state resolves, load the wishlist once for the session.
// When the user signs out, reset the wishlist.
watch(
  () => authStore.currentUser,
  async (user) => {
    if (user) {
      await wishlistStore.loadWishlist(user.uid);
    } else {
      wishlistStore.reset();
    }
  },
);
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
