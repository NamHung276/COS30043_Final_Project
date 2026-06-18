<script setup>
import Navbar from './components/Navbar.vue'
import Footer from './components/Footer.vue'
</script>

<template>
  <Navbar />

  <div class="container mt-4">
    <router-view />
  </div>

  <Footer />
</template>