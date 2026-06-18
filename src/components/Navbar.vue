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

          <template v-if="!currentUser && authReady">
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
              👤 {{ currentUser.displayName || currentUser.email }}
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
import { auth } from '../firebase'
import { onAuthStateChanged, signOut } from 'firebase/auth'

export default {
  data() {
    return {
      currentUser: null,
      authReady: false,
      unsubscribe: null
    }
  },

  mounted() {
    // Firebase listener — fires automatically on login/logout/page load
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      this.currentUser = user
      this.authReady = true
    })
  },

  beforeUnmount() {
    if (this.unsubscribe) {
      this.unsubscribe()
    }
  },

  methods: {
    async logout() {
      try {
        await signOut(auth)
        localStorage.removeItem('favorites')
        this.$router.push('/')
      } catch (error) {
        console.error('Logout failed:', error)
      }
    }
  }
}
</script>