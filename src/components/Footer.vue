// src/components/Footer.vue
<template>
  <footer class="footer mt-5 py-4 gd-footer-transition">
    <div class="container text-center">

      <h5><i class="bi bi-controller me-2"></i>GameHub</h5>

      <p class="mb-3" style="max-width: 480px; margin: 0 auto 16px; color: var(--text-secondary);">
        Discover free-to-play games and stay updated with gaming news.
      </p>

      <div class="mb-3">

        <router-link to="/" class="footer-link">
          Home
        </router-link>

        <router-link to="/games" class="footer-link">
          Games
        </router-link>

        <router-link to="/live-news" class="footer-link">
          Live News
        </router-link>

        <router-link to="/gamehub-news" class="footer-link">
          GameHub News
        </router-link>

        <router-link to="/favorites" class="footer-link">
          Favorites
        </router-link>

        <router-link to="/about" class="footer-link">
          About
        </router-link>

      </div>

      <hr class="footer-divider" />

      <div class="d-flex justify-content-center align-items-center gap-3 flex-wrap">
        <small style="color: var(--text-secondary);">
          Built with Vue 3, Firebase, FreeToGame API and NewsAPI
        </small>
      </div>

      <small class="d-block mt-2" style="color: var(--text-secondary);">
        © 2026 GameHub | COS30043 Full-Stack Project
      </small>

    </div>
  </footer>
</template>

<style scoped>
.gd-footer-transition {
    background: linear-gradient(var(--bg-deep), var(--border-subtle));
}
</style>