// src/components/Navbar.vue
<template>
  <nav class="navbar navbar-expand-lg navbar-dark">
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
        <div class="navbar-nav ms-auto align-items-center">

          <router-link
            class="nav-link"
            to="/"
            @click="closeMenu"
          >
            Home
          </router-link>

          <!-- Games Dropdown -->
          <li class="nav-item dropdown list-unstyled">
            <a
              class="nav-link dropdown-toggle"
              href="#"
              role="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
            >
              Games
            </a>
            <ul class="dropdown-menu dropdown-menu-dark">
              <li>
                <router-link
                  class="dropdown-item"
                  to="/games"
                  @click="closeMenu"
                >
                  🎮 All Games
                </router-link>
              </li>
              <li>
                <router-link
                  class="dropdown-item"
                  to="/free-to-play"
                  @click="closeMenu"
                >
                  🆓 Free to Play
                </router-link>
              </li>
            </ul>
          </li>

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
                  @click="closeMenu"
                >
                  📡 Live News
                </router-link>
              </li>
              <li>
                <router-link
                  class="dropdown-item"
                  to="/gamehub-news"
                  @click="closeMenu"
                >
                  🗂️ GameHub News
                </router-link>
              </li>
            </ul>
          </li>

          <router-link
            class="nav-link"
            to="/favorites"
            @click="closeMenu"
          >
            Favorites
          </router-link>

          <router-link
            class="nav-link"
            to="/about"
            @click="closeMenu"
          >
            About
          </router-link>

          <!-- Admin link (only visible to admins) -->
          <router-link
            v-if="isAdmin"
            class="nav-link nav-admin-link"
            to="/admin"
            @click="closeMenu"
          >
            🛡️ Admin
          </router-link>

          <template v-if="!currentUser && authReady">
            <router-link
              class="nav-btn-login"
              to="/login"
              @click="closeMenu"
            >
              Login
            </router-link>

            <router-link
              class="nav-btn-signup"
              to="/register"
              @click="closeMenu"
            >
              Sign Up
            </router-link>
          </template>

          <template v-if="currentUser">
            <router-link
              class="nav-link d-flex align-items-center nav-profile-link"
              to="/profile"
              :title="`Account: ${currentUser.email}`"
              @click="closeMenu"
            >
              <span class="nav-user-avatar">
                {{ userInitial }}
              </span>
              {{ currentUser.displayName || currentUser.email }}
            </router-link>

            <button
              class="btn btn-outline-danger btn-sm ms-2"
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
import { auth, db } from '../firebase'
import { onAuthStateChanged, signOut } from 'firebase/auth'
import { doc, getDoc } from 'firebase/firestore'

export default {
  data() {
    return {
      currentUser: null,
      authReady: false,
      isAdmin: false,
      unsubscribe: null
    }
  },

  computed: {
    userInitial() {
      if (!this.currentUser) return ''
      const name = this.currentUser.displayName || this.currentUser.email
      return name.charAt(0).toUpperCase()
    }
  },

  mounted() {
    // Firebase listener — fires automatically on login/logout/page load
    this.unsubscribe = onAuthStateChanged(auth, async (user) => {
      this.currentUser = user
      this.authReady = true
      if (user) {
        try {
          const snap = await getDoc(doc(db, 'users', user.uid))
          this.isAdmin = snap.exists() && snap.data().role === 'admin'
        } catch {
          this.isAdmin = false
        }
      } else {
        this.isAdmin = false
      }
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
        this.closeMenu()
        this.$router.push('/')
      } catch (error) {
        console.error('Logout failed:', error)
      }
    },

    closeMenu() {
      // Close mobile navbar on navigation
      const navCollapse = document.getElementById('navbarNav')
      if (navCollapse && navCollapse.classList.contains('show')) {
        const bsCollapse = bootstrap.Collapse.getInstance(navCollapse)
        if (bsCollapse) bsCollapse.hide()
      }
    }
  }
}
</script>