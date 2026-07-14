// src/components/Navbar.vue
<template>
  <nav class="navbar navbar-expand-lg" :class="theme === 'dark' ? 'navbar-dark' : 'navbar-light'">
    <div class="container">

      <router-link
        class="navbar-brand"
        to="/"
      >
        <img src="/logo/gamepad.svg" width="20" height="20" alt="" aria-hidden="true" style="margin-right:7px; filter:brightness(1.3); vertical-align:-3px;">
        GameHub
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
            <ul class="dropdown-menu shadow-sm border-0">
              <li>
                <router-link class="dropdown-item nav-dd-item" to="/games" @click="closeMenu">
                  <span class="nav-dd-icon nav-dd-icon-purple">
                    <img src="/logo/gamepad.svg" width="15" height="15" alt="" aria-hidden="true">
                  </span>
                  All Games
                </router-link>
              </li>
              <li>
                <router-link class="dropdown-item nav-dd-item" to="/paid-games" @click="closeMenu">
                  <span class="nav-dd-icon nav-dd-icon-cyan">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10"/><path d="M16 8h-6a2 2 0 100 4h4a2 2 0 110 4H8"/><path d="M12 18V6"/></svg>
                  </span>
                  Paid Games
                </router-link>
              </li>
              <li>
                <router-link class="dropdown-item nav-dd-item" to="/free-to-play" @click="closeMenu">
                  <span class="nav-dd-icon nav-dd-icon-green">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>
                  </span>
                  Free to Play
                </router-link>
              </li>
              <li>
                <router-link class="dropdown-item nav-dd-item" to="/deals" @click="closeMenu">
                  <span class="nav-dd-icon nav-dd-icon-amber">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 12V22H4V12"/><path d="M22 7H2v5h20V7z"/><path d="M12 22V7"/><path d="M12 7H7.5a2.5 2.5 0 010-5C11 2 12 7 12 7z"/><path d="M12 7h4.5a2.5 2.5 0 000-5C13 2 12 7 12 7z"/></svg>
                  </span>
                  Game Deals
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
            <ul class="dropdown-menu shadow-sm border-0">
              <li>
                <router-link class="dropdown-item nav-dd-item" to="/live-news" @click="closeMenu">
                  <span class="nav-dd-icon nav-dd-icon-cyan">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M5 12.55a11 11 0 0114.08 0M1.42 9a16 16 0 0121.16 0M8.53 16.11a6 6 0 016.95 0M12 20h.01"/>
                    </svg>
                  </span>
                  Live News
                </router-link>
              </li>
              <li>
                <router-link class="dropdown-item nav-dd-item" to="/gamehub-news" @click="closeMenu">
                  <span class="nav-dd-icon nav-dd-icon-violet">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                      <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/>
                      <polyline points="14,2 14,8 20,8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10,9 9,9 8,9"/>
                    </svg>
                  </span>
                  GameHub News
                </router-link>
              </li>
            </ul>
          </li>

          <router-link
            class="nav-link"
            to="/favorites"
            @click="closeMenu"
          >
            Wishlist
          </router-link>

          <router-link
            class="nav-link"
            to="/about"
            @click="closeMenu"
          >
            About
          </router-link>

          <!-- Cart Link -->
          <router-link
            class="nav-link d-flex align-items-center position-relative me-2"
            to="/checkout"
            @click="closeMenu"
          >
            <i class="bi bi-cart3 fs-5"></i>
            <span v-if="cartItemsCount > 0" class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger" style="font-size: 0.6rem; transform: translate(-30%, 10%) !important;">
              {{ cartItemsCount }}
            </span>
            <span class="ms-2 d-lg-none">Cart</span>
          </router-link>

          <!-- Admin link (only visible to admins) -->
          <router-link
            v-if="isAdmin"
            class="nav-link nav-admin-link"
            to="/admin"
            @click="closeMenu"
          >
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right:5px; vertical-align:-1px;" aria-hidden="true"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
            Admin
          </router-link>

          <!-- Theme Toggle -->
          <button 
            class="btn btn-link nav-link theme-toggle-btn"
            @click="toggleTheme"
            :title="theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
          >
            <svg v-if="theme === 'dark'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
            </svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          </button>

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
import { cartState } from '../services/cart'

export default {
  data() {
    return {
      currentUser: null,
      authReady: false,
      isAdmin: false,
      unsubscribe: null,
      theme: 'dark'
    }
  },

  computed: {
    userInitial() {
      if (!this.currentUser) return ''
      const name = this.currentUser.displayName || this.currentUser.email
      return name.charAt(0).toUpperCase()
    },
    cartItemsCount() {
      return cartState.totalItems
    }
  },

  mounted() {
    // Theme initialization
    const savedTheme = localStorage.getItem('gamehub-theme') || 'dark'
    this.theme = savedTheme
    document.documentElement.setAttribute('data-theme', savedTheme)

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
    toggleTheme() {
      this.theme = this.theme === 'dark' ? 'light' : 'dark'
      document.documentElement.setAttribute('data-theme', this.theme)
      localStorage.setItem('gamehub-theme', this.theme)
    },

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
        if (window.bootstrap?.Collapse) {
          const bsCollapse = window.bootstrap.Collapse.getInstance(navCollapse)
          if (bsCollapse) bsCollapse.hide()
        } else {
          // Fallback: manually collapse if Bootstrap JS isn't on window
          navCollapse.classList.remove('show')
        }
      }
    }
  }
}
</script>

<style scoped>
.theme-toggle-btn {
  color: var(--text-secondary);
  border: none;
  background: transparent;
  padding: 0.5rem;
  margin: 0 10px;
  transition: color 0.2s, transform 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.theme-toggle-btn:hover {
  color: var(--primary);
  transform: scale(1.15);
}
</style>