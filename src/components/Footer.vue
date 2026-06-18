<template>
  <footer class="footer mt-5 py-4">
    <div class="container text-center">

      <h5>GameHub</h5>

      <p class="text-muted">
        Discover free-to-play games and stay updated with gaming news.
      </p>

      <div class="mb-3">
        <router-link to="/" class="footer-link">Home</router-link>
        <router-link to="/games" class="footer-link">Games</router-link>
        <router-link to="/live-news" class="footer-link">News</router-link>
        <router-link to="/about" class="footer-link">About</router-link>
      </div>

      <small class="text-muted">
        © 2026 GameHub | COS30043 Full-Stack Project
      </small>

    </div>
  </footer>
</template>

<style scoped>
.footer {
  background: #161b22;
  border-top: 1px solid #2d333b;
}

.footer-link {
  color: #8b949e;
  text-decoration: none;
  margin: 0 12px;
}

.footer-link:hover {
  color: white;
}
</style>