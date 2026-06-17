<template>
  <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container">

      <router-link
        class="navbar-brand"
        to="/"
      >
        🎮 GameHub
      </router-link>

      <!-- Hamburger toggle for mobile -->
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarNav">
        <div class="navbar-nav ms-auto">

          <router-link
            class="nav-link"
            to="/"
          >
            Home
          </router-link>

          <router-link
            class="nav-link"
            to="/games"
          >
            Games
          </router-link>

          <!-- News Dropdown -->
          <li class="nav-item dropdown list-unstyled">
            <a
              class="nav-link dropdown-toggle"
              href="#"
              role="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              News
            </a>
            <ul class="dropdown-menu dropdown-menu-dark">
              <li>
                <router-link
                  class="dropdown-item"
                  to="/live-news"
                >
                  📡 Live News
                </router-link>
              </li>
              <li>
                <router-link
                  class="dropdown-item"
                  to="/gamehub-news"
                >
                  🗂️ GameHub News
                </router-link>
              </li>
            </ul>
          </li>

          <router-link
            class="nav-link"
            to="/favorites"
          >
            Favorites
          </router-link>

          <router-link
            class="nav-link"
            to="/about"
          >
            About
          </router-link>

          <template v-if="!currentUser">
            <router-link
              class="nav-link btn btn-primary"
              to="/login"
              style="margin-left: 10px; padding: 6px 16px; border-radius: 4px;"
            >
              Login
            </router-link>

            <router-link
              class="nav-link btn btn-primary"
              to="/register"
              style="margin-left: 10px; padding: 6px 16px; border-radius: 4px;"
            >
              Sign Up
            </router-link>
          </template>

          <template v-if="currentUser">
            <span class="nav-link">
              👤 {{ currentUser.name }}
            </span>

            <button
              class="nav-link btn btn-link"
              @click="logout"
            >
              Logout
            </button>
          </template>

        </div>
      </div>

    </div>
  </nav>
</template>

<script>
export default {
  data() {
    return {
      currentUser: null
    }
  },

  mounted() {
    this.currentUser =
      JSON.parse(localStorage.getItem('currentUser'))

    // Listen for login/logout events from other pages
    window.addEventListener('auth-updated', this.refreshUser)
  },

  beforeUnmount() {
    window.removeEventListener('auth-updated', this.refreshUser)
  },

  methods: {
    refreshUser() {
      this.currentUser =
        JSON.parse(localStorage.getItem('currentUser'))
    },

    logout() {
      localStorage.removeItem('currentUser')
      localStorage.removeItem('favorites')
      this.currentUser = null
      this.$router.push('/')
    }
  }
}
</script>