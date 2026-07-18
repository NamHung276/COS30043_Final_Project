<template>
  <nav
    class="navbar navbar-expand-lg"
    :class="theme === 'dark' ? 'navbar-dark' : 'navbar-light'"
  >
    <div class="container">
      <router-link class="navbar-brand" to="/">
        <img
          src="/logo/gamepad.svg"
          width="20"
          height="20"
          alt=""
          aria-hidden="true"
          style="
            margin-right: 7px;
            filter: brightness(1.3);
            vertical-align: -3px;
          "
        />
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
        <!-- Left Side: Public Navigation -->
        <ul class="navbar-nav me-auto align-items-center mb-0 ps-0" style="list-style:none">
          <li class="nav-item">
            <router-link class="nav-link" to="/" @click="closeMenu">
              Home
            </router-link>
          </li>

          <!-- Games Dropdown -->
          <li class="nav-item dropdown">
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
                <router-link
                  class="dropdown-item nav-dd-item"
                  to="/games"
                  @click="closeMenu"
                >
                  <span class="nav-dd-icon nav-dd-icon-purple">
                    <img src="/logo/gamepad.svg" width="15" height="15" alt="" aria-hidden="true" />
                  </span>
                  All Games
                </router-link>
              </li>
              <li>
                <router-link
                  class="dropdown-item nav-dd-item"
                  to="/paid-games"
                  @click="closeMenu"
                >
                  <span class="nav-dd-icon nav-dd-icon-cyan">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="10" /><path d="M16 8h-6a2 2 0 100 4h4a2 2 0 110 4H8" /><path d="M12 18V6" /></svg>
                  </span>
                  Paid Games
                </router-link>
              </li>
              <li>
                <router-link
                  class="dropdown-item nav-dd-item"
                  to="/free-to-play"
                  @click="closeMenu"
                >
                  <span class="nav-dd-icon nav-dd-icon-green">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" /></svg>
                  </span>
                  Free to Play
                </router-link>
              </li>
              <li>
                <router-link
                  class="dropdown-item nav-dd-item"
                  to="/deals"
                  @click="closeMenu"
                >
                  <span class="nav-dd-icon nav-dd-icon-amber">
                    <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M20 12V22H4V12" /><path d="M22 7H2v5h20V7z" /><path d="M12 22V7" /><path d="M12 7H7.5a2.5 2.5 0 010-5C11 2 12 7 12 7z" /><path d="M12 7h4.5a2.5 2.5 0 000-5C13 2 12 7 12 7z" /></svg>
                  </span>
                  Game Deals
                </router-link>
              </li>
            </ul>
          </li>

          <li class="nav-item">
            <router-link class="nav-link" to="/live-news" @click="closeMenu">
              News
            </router-link>
          </li>

          <li class="nav-item">
            <router-link class="nav-link" to="/gamehub-news" @click="closeMenu">
              Community
            </router-link>
          </li>

          <li class="nav-item">
            <router-link class="nav-link" to="/about" @click="closeMenu">
              About
            </router-link>
          </li>
        </ul>

        <!-- Right Side: Search & User Menu -->
        <div class="navbar-nav ms-auto align-items-center">

          <!-- ── Search Bar ─────────────────────────────── -->
          <div class="nav-search-wrapper" ref="searchWrapper">
            <div class="nav-search-container" :class="{ active: searchFocused }">
              <!-- Visually hidden label associates with the input for screen readers -->
              <label for="navbar-search-input" class="visually-hidden">Search games</label>
              <svg class="nav-search-icon" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/>
              </svg>
              <input
                id="navbar-search-input"
                ref="searchInput"
                v-model="searchQuery"
                type="text"
                class="nav-search-input"
                placeholder="Search games..."
                autocomplete="off"
                @focus="searchFocused = true"
                @input="onSearchInput"
                @keydown.enter="submitSearch"
                @keydown.escape="closeSearch"
                @keydown.down.prevent="highlightNext"
                @keydown.up.prevent="highlightPrev"
              />
              <button
                v-if="searchQuery"
                class="nav-search-clear"
                @click="clearSearch"
                aria-label="Clear search"
              >
                <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
              </button>
            </div>

            <!-- Search Dropdown Results -->
            <div
              v-if="searchFocused && (searchResults.length || searchLoading || (searchQuery.length > 1 && !searchLoading))"
              class="nav-search-dropdown"
              role="listbox"
            >
              <!-- Loading skeleton -->
              <div v-if="searchLoading" class="nav-search-loading">
                <div v-for="i in 4" :key="i" class="nav-search-skeleton">
                  <div class="nss-img skeleton"></div>
                  <div class="nss-text">
                    <div class="skeleton" style="height:12px; width:80%; border-radius:4px; margin-bottom:6px"></div>
                    <div class="skeleton" style="height:10px; width:50%; border-radius:4px"></div>
                  </div>
                </div>
              </div>

              <!-- Results -->
              <template v-else-if="searchResults.length">
                <div class="nav-search-results-header">
                  <span>Games</span>
                  <button class="nav-search-view-all" @click="submitSearch">
                    View all results →
                  </button>
                </div>
                <router-link
                  v-for="(game, idx) in searchResults"
                  :key="game.id"
                  :to="`/games/${game.id}`"
                  class="nav-search-result"
                  :class="{ highlighted: idx === highlightedIndex }"
                  role="option"
                  @click="closeSearch"
                >
                  <div class="nsr-img">
                    <img
                      v-if="game.background_image"
                      :src="game.background_image"
                      :alt="game.name"
                      loading="lazy"
                    />
                    <div v-else class="nsr-img-placeholder">
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="2" y="3" width="20" height="14" rx="2"/><path d="M8 21h8M12 17v4"/></svg>
                    </div>
                  </div>
                  <div class="nsr-info">
                    <span class="nsr-title">{{ game.name }}</span>
                    <span class="nsr-meta">
                      <span v-if="game.genres?.length" class="nsr-genre">{{ game.genres[0].name }}</span>
                      <span v-if="game.metacritic" class="nsr-mc" :class="mcClass(game.metacritic)">{{ game.metacritic }}</span>
                    </span>
                  </div>
                  <div class="nsr-released" v-if="game.released">
                    {{ game.released?.substring(0, 4) }}
                  </div>
                </router-link>
              </template>

              <!-- No results -->
              <div v-else-if="searchQuery.length > 1 && !searchLoading" class="nav-search-empty">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/></svg>
                <span>No results for "<strong>{{ searchQuery }}</strong>"</span>
              </div>
            </div>
          </div>
          <!-- ── /Search Bar ─────────────────────────── -->

          <!-- Notification Bell (Placeholder) -->
          <a
            class="nav-link position-relative me-2 d-none d-lg-flex"
            href="#"
            @click.prevent
            aria-label="Notifications"
            title="Notifications"
          >
            <i class="bi bi-bell fs-5" aria-hidden="true"></i>
          </a>

          <!-- Cart Link -->
          <router-link
            class="nav-link d-flex align-items-center position-relative me-3"
            to="/checkout"
            @click="closeMenu"
          >
            <i class="bi bi-cart3 fs-5"></i>
            <span
              v-if="cartItemsCount > 0"
              class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
              style="
                font-size: 0.6rem;
                transform: translate(-30%, 10%) !important;
              "
            >
              {{ cartItemsCount }}
            </span>
            <span class="ms-2 d-lg-none">Cart</span>
          </router-link>

          <!-- Theme Toggle (Only show in navbar if logged out) -->
          <button
            v-if="!currentUser"
            class="btn btn-link nav-link theme-toggle-btn me-2"
            @click="toggleTheme"
            :title="theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'"
          >
            <svg v-if="theme === 'dark'" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5" /><line x1="12" y1="1" x2="12" y2="3" /><line x1="12" y1="21" x2="12" y2="23" /><line x1="4.22" y1="4.22" x2="5.64" y2="5.64" /><line x1="18.36" y1="18.36" x2="19.78" y2="19.78" /><line x1="1" y1="12" x2="3" y2="12" /><line x1="21" y1="12" x2="23" y2="12" /><line x1="4.22" y1="19.78" x2="5.64" y2="18.36" /><line x1="18.36" y1="5.64" x2="19.78" y2="4.22" /></svg>
            <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" /></svg>
          </button>

          <template v-if="!currentUser && authReady">
            <router-link class="nav-btn-login" to="/login" @click="closeMenu">Login</router-link>
            <router-link class="nav-btn-signup" to="/register" @click="closeMenu">Sign Up</router-link>
          </template>

          <template v-if="currentUser">
            <!-- User Menu Dropdown -->
            <li class="nav-item dropdown list-unstyled ms-1">
              <a
                class="nav-link dropdown-toggle d-flex align-items-center nav-profile-link"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
                :title="`Account: ${currentUser.email}`"
              >
                <span class="nav-user-avatar">
                  {{ userInitial }}
                </span>
                <span class="d-lg-none ms-2">{{ currentUser.displayName || currentUser.email }}</span>
              </a>
              <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0 user-dropdown-menu mt-2">
                <li class="px-3 py-2 small fw-bold text-uppercase d-flex align-items-center" style="letter-spacing: 1px; color: var(--text-primary);">
                  <span class="nav-dd-icon nav-dd-icon-blue me-2" style="background: linear-gradient(135deg, #0369a1, #0ea5e9); box-shadow: 0 2px 8px rgba(14, 165, 233, 0.4);">
                    <i class="bi bi-person-circle" style="font-size: 0.85rem;"></i>
                  </span> My Account
                </li>
                <li><hr class="dropdown-divider border-secondary opacity-25 m-0 mb-1"></li>
                <li>
                  <router-link class="dropdown-item nav-dd-item" to="/profile" @click="closeMenu">
                    <span class="nav-dd-icon nav-dd-icon-blue" style="background: linear-gradient(135deg, #0369a1, #0ea5e9); box-shadow: 0 2px 8px rgba(14, 165, 233, 0.4);">
                      <i class="bi bi-person" style="font-size: 0.85rem;"></i>
                    </span>
                    Profile
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item nav-dd-item" to="/library" @click="closeMenu">
                    <span class="nav-dd-icon nav-dd-icon-purple">
                      <i class="bi bi-controller" style="font-size: 0.85rem;"></i>
                    </span>
                    My Library
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item nav-dd-item" to="/favorites" @click="closeMenu">
                    <span class="nav-dd-icon nav-dd-icon-coral" style="background: linear-gradient(135deg, #9f1239, #f43f5e); box-shadow: 0 2px 8px rgba(244, 63, 94, 0.4);">
                      <i class="bi bi-heart-fill" style="font-size: 0.85rem;"></i>
                    </span>
                    Wishlist
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item nav-dd-item" to="/profile#reviews" @click="closeMenu">
                    <span class="nav-dd-icon nav-dd-icon-amber">
                      <i class="bi bi-star-fill" style="font-size: 0.85rem;"></i>
                    </span>
                    My Reviews
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item nav-dd-item" to="/profile#saved" @click="closeMenu">
                    <span class="nav-dd-icon nav-dd-icon-cyan">
                      <i class="bi bi-bookmark-fill" style="font-size: 0.85rem;"></i>
                    </span>
                    Saved Articles
                  </router-link>
                </li>
                <li>
                  <router-link class="dropdown-item nav-dd-item" to="/settings" @click="closeMenu">
                    <span class="nav-dd-icon nav-dd-icon-green" style="background: linear-gradient(135deg, #10b981, #059669); box-shadow: 0 2px 8px rgba(16, 185, 129, 0.4);">
                      <i class="bi bi-gear-fill" style="font-size: 0.85rem;"></i>
                    </span>
                    Settings
                  </router-link>
                </li>
                <li><hr class="dropdown-divider border-secondary opacity-25"></li>
                <li>
                  <a href="#" class="dropdown-item nav-dd-item" @click.prevent.stop="toggleTheme">
                    <span class="nav-dd-icon" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12);">
                      <i :class="theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill'" style="font-size: 0.85rem; color: var(--warning);"></i>
                    </span>
                    {{ theme === 'dark' ? 'Light Mode' : 'Dark Mode' }}
                  </a>
                </li>
                <li>
                  <router-link class="dropdown-item nav-dd-item" to="/profile#settings" @click="closeMenu">
                    <span class="nav-dd-icon" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12);">
                      <i class="bi bi-gear-fill" style="font-size: 0.85rem; color: var(--text-muted);"></i>
                    </span>
                    Settings
                  </router-link>
                </li>
                <template v-if="isAdmin">
                  <li><hr class="dropdown-divider border-secondary opacity-25"></li>
                  <li>
                    <router-link class="dropdown-item nav-dd-item" to="/admin" @click="closeMenu" style="color: var(--accent-light);">
                      <span class="nav-dd-icon nav-dd-icon-violet">
                        <i class="bi bi-shield-lock-fill" style="font-size: 0.85rem;"></i>
                      </span>
                      Admin Dashboard
                    </router-link>
                  </li>
                </template>
                <li><hr class="dropdown-divider border-secondary opacity-25"></li>
                <li>
                  <button class="dropdown-item nav-dd-item text-danger" @click="logout">
                    <span class="nav-dd-icon" style="background: rgba(244, 63, 94, 0.15); border: 1px solid rgba(244, 63, 94, 0.25);">
                      <i class="bi bi-box-arrow-right" style="font-size: 0.85rem;"></i>
                    </span>
                    Logout
                  </button>
                </li>
              </ul>
            </li>
          </template>
</div>
      </div>
    </div>
  </nav>
</template>

<script>
import { auth, db } from "../firebase";
import { onAuthStateChanged, signOut } from "firebase/auth";
import { doc, getDoc } from "firebase/firestore";
import { cartState } from "../services/cart";
import { rawgApi } from "../services/api";

export default {
  data() {
    return {
      currentUser: null,
      authReady: false,
      isAdmin: false,
      unsubscribe: null,
      theme: "dark",
      // Search state
      searchQuery: "",
      searchFocused: false,
      searchResults: [],
      searchLoading: false,
      searchDebounce: null,
      highlightedIndex: -1,
    };
  },

  computed: {
    userInitial() {
      if (!this.currentUser) return "";
      const name = this.currentUser.displayName || this.currentUser.email;
      return name.charAt(0).toUpperCase();
    },
    cartItemsCount() {
      return cartState.totalItems;
    },
  },

  mounted() {
    // Theme initialization
    const savedTheme = localStorage.getItem("gamehub-theme") || "dark";
    this.theme = savedTheme;
    document.documentElement.setAttribute("data-theme", savedTheme);

    // Firebase listener — fires automatically on login/logout/page load
    this.unsubscribe = onAuthStateChanged(auth, async (user) => {
      this.currentUser = user;
      this.authReady = true;
      if (user) {
        try {
          const snap = await getDoc(doc(db, "users", user.uid));
          this.isAdmin = snap.exists() && snap.data().role === "admin";
        } catch {
          this.isAdmin = false;
        }
      } else {
        this.isAdmin = false;
      }
    });

    // Close search when clicking outside
    document.addEventListener("click", this.handleOutsideClick);
  },

  beforeUnmount() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
    document.removeEventListener("click", this.handleOutsideClick);
    clearTimeout(this.searchDebounce);
  },

  methods: {
    toggleTheme() {
      this.theme = this.theme === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", this.theme);
      localStorage.setItem("gamehub-theme", this.theme);
    },

    async logout() {
      try {
        await signOut(auth);
        this.closeMenu();
        this.$router.push("/");
      } catch (error) {
        console.error("Logout failed:", error);
      }
    },

    closeMenu() {
      // Close mobile navbar on navigation
      const navCollapse = document.getElementById("navbarNav");
      if (navCollapse && navCollapse.classList.contains("show")) {
        if (window.bootstrap?.Collapse) {
          const bsCollapse = window.bootstrap.Collapse.getInstance(navCollapse);
          if (bsCollapse) bsCollapse.hide();
        } else {
          navCollapse.classList.remove("show");
        }
      }
    },

    // ── Search methods ──────────────────────────────────
    onSearchInput() {
      this.highlightedIndex = -1;
      clearTimeout(this.searchDebounce);

      if (this.searchQuery.length < 2) {
        this.searchResults = [];
        this.searchLoading = false;
        return;
      }

      this.searchLoading = true;
      this.searchDebounce = setTimeout(() => {
        this.fetchSearchResults();
      }, 320);
    },

    async fetchSearchResults() {
      if (!this.searchQuery.trim() || this.searchQuery.length < 2) {
        this.searchLoading = false;
        return;
      }
      try {
        const { data } = await rawgApi.get("/games", {
          params: {
            search: this.searchQuery.trim(),
            page_size: 6,
            ordering: "-rating",
          },
        });
        this.searchResults = data.results || [];
      } catch {
        this.searchResults = [];
      } finally {
        this.searchLoading = false;
      }
    },

    submitSearch() {
      if (this.highlightedIndex >= 0 && this.searchResults[this.highlightedIndex]) {
        const game = this.searchResults[this.highlightedIndex];
        this.$router.push(`/games/${game.id}`);
        this.closeSearch();
        return;
      }
      if (this.searchQuery.trim()) {
        this.$router.push(`/games?search=${encodeURIComponent(this.searchQuery.trim())}`);
        this.closeSearch();
      }
    },

    closeSearch() {
      this.searchFocused = false;
      this.searchResults = [];
      this.searchQuery = "";
      this.highlightedIndex = -1;
      this.$refs.searchInput?.blur();
    },

    clearSearch() {
      this.searchQuery = "";
      this.searchResults = [];
      this.highlightedIndex = -1;
      this.$refs.searchInput?.focus();
    },

    highlightNext() {
      if (this.highlightedIndex < this.searchResults.length - 1) {
        this.highlightedIndex++;
      }
    },

    highlightPrev() {
      if (this.highlightedIndex > -1) {
        this.highlightedIndex--;
      }
    },

    handleOutsideClick(e) {
      if (this.$refs.searchWrapper && !this.$refs.searchWrapper.contains(e.target)) {
        this.searchFocused = false;
      }
    },

    mcClass(score) {
      if (!score) return "";
      const n = parseInt(score);
      return n >= 75 ? "mc-green" : n >= 50 ? "mc-yellow" : "mc-red";
    },
  },
};
</script>

<style scoped>
.theme-toggle-btn {
  color: var(--text-secondary);
  border: none;
  background: transparent;
  padding: 0.5rem;
  margin: 0 4px;
  transition:
    color 0.2s,
    transform 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.theme-toggle-btn:hover {
  color: var(--primary);
  transform: scale(1.15);
}

/* ── Search Bar ─────────────────────────────────── */
.nav-search-wrapper {
  position: relative;
  margin: 0 6px;
}

.nav-search-container {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.09);
  border-radius: 10px;
  padding: 6px 12px;
  width: 200px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: text;
}

.nav-search-container.active,
.nav-search-container:focus-within {
  width: 280px;
  background: rgba(255, 255, 255, 0.09);
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(14, 165, 233, 0.12);
}

.nav-search-icon {
  color: var(--text-muted);
  flex-shrink: 0;
  transition: color 0.2s;
}

.nav-search-container.active .nav-search-icon,
.nav-search-container:focus-within .nav-search-icon {
  color: var(--primary);
}

.nav-search-input {
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 0.85rem;
  font-family: var(--font-family);
  width: 100%;
  min-width: 0;
}

.nav-search-input::placeholder {
  color: var(--text-muted);
  font-size: 0.83rem;
}

.nav-search-clear {
  background: transparent;
  border: none;
  padding: 0;
  color: var(--text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  flex-shrink: 0;
  transition: color 0.2s;
}

.nav-search-clear:hover {
  color: var(--text-primary);
}

/* Search Dropdown */
.nav-search-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 360px;
  background: var(--bg-surface);
  border: 1px solid var(--border-glass);
  border-radius: 14px;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255,255,255,0.04);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  overflow: hidden;
  z-index: 9999;
  animation: searchDropIn 0.18s cubic-bezier(0.4, 0, 0.2, 1);
}

@keyframes searchDropIn {
  from { opacity: 0; transform: translateY(-8px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}

.nav-search-results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 14px 6px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  border-bottom: 1px solid var(--border-subtle);
}

.nav-search-view-all {
  background: transparent;
  border: none;
  color: var(--primary);
  font-size: 0.72rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
  transition: color 0.2s;
}

.nav-search-view-all:hover {
  color: var(--primary-light);
}

.nav-search-result {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 14px;
  text-decoration: none;
  color: var(--text-primary);
  transition: background 0.15s ease;
  cursor: pointer;
}

.nav-search-result:hover,
.nav-search-result.highlighted {
  background: rgba(14, 165, 233, 0.08);
}

.nsr-img {
  width: 48px;
  height: 30px;
  border-radius: 5px;
  overflow: hidden;
  flex-shrink: 0;
  background: var(--bg-glass);
}

.nsr-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.nsr-img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}

.nsr-info {
  flex: 1;
  min-width: 0;
}

.nsr-title {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 2px;
}

.nsr-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}

.nsr-genre {
  font-size: 0.72rem;
  color: var(--text-muted);
}

.nsr-mc {
  font-size: 0.68rem;
  font-weight: 700;
  padding: 1px 6px;
  border-radius: 3px;
  color: #fff;
}

.mc-green { background: #15803d; }
.mc-yellow { background: #a16207; }
.mc-red { background: #b91c1c; }

.nsr-released {
  font-size: 0.72rem;
  color: var(--text-muted);
  flex-shrink: 0;
}

/* Loading skeleton */
.nav-search-loading {
  padding: 8px 0;
}

.nav-search-skeleton {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 9px 14px;
}

.nss-img {
  width: 48px;
  height: 30px;
  border-radius: 5px;
  flex-shrink: 0;
}

.nss-text {
  flex: 1;
}

/* No results state */
.nav-search-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  padding: 28px 20px;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.85rem;
}

.nav-search-empty svg {
  opacity: 0.4;
}

/* Skeleton animation */
.skeleton {
  background: linear-gradient(90deg, var(--bg-glass) 25%, rgba(255,255,255,0.06) 50%, var(--bg-glass) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Light theme adjustments */
[data-theme="light"] .nav-search-container {
  background: rgba(0, 0, 0, 0.05);
  border-color: rgba(0, 0, 0, 0.1);
}
[data-theme="light"] .nav-search-container.active,
[data-theme="light"] .nav-search-container:focus-within {
  background: rgba(0, 0, 0, 0.07);
}
[data-theme="light"] .nav-search-dropdown {
  background: #ffffff;
  border-color: rgba(0,0,0,0.1);
  box-shadow: 0 20px 50px rgba(0,0,0,0.15);
}
[data-theme="light"] .nav-search-input {
  color: var(--text-primary);
}
[data-theme="light"] .navbar {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  border-bottom: 1px solid rgba(0, 0, 0, 0.03);
}

/* User Dropdown styling */
.user-dropdown-menu {
  min-width: 240px;
  background: rgba(10, 14, 26, 0.97);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--border-glass) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 24px 60px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255,255,255,0.04) !important;
  padding: 8px !important;
}

/* Dropdown item with icon badge */
.nav-dd-item {
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
  padding: 9px 12px !important;
  border-radius: 8px !important;
  font-size: 0.88rem !important;
  font-weight: 500 !important;
  color: var(--text-secondary) !important;
  transition: all 0.18s ease !important;
  background: transparent !important;
  border: none;
  cursor: pointer;
  width: 100%;
  text-align: left;
}

.nav-dd-item:hover,
.nav-dd-item:focus {
  color: var(--text-primary) !important;
  background: rgba(255, 255, 255, 0.06) !important;
  transform: translateX(2px);
}

.nav-dd-item.router-link-active {
  color: var(--primary-light) !important;
  background: rgba(14, 165, 233, 0.08) !important;
}

/* Icon badge shared base */
.nav-dd-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 7px;
  font-size: 0.8rem;
  flex-shrink: 0;
  color: white;
}

/* Color variants */
.nav-dd-icon-blue {
  background: linear-gradient(135deg, #0369a1, #0ea5e9);
  box-shadow: 0 2px 8px rgba(14, 165, 233, 0.4);
}
.nav-dd-icon-purple {
  background: linear-gradient(135deg, #6d28d9, #8b5cf6);
  box-shadow: 0 2px 8px rgba(139, 92, 246, 0.4);
}
.nav-dd-icon-coral {
  background: linear-gradient(135deg, #9f1239, #f43f5e);
  box-shadow: 0 2px 8px rgba(244, 63, 94, 0.4);
}
.nav-dd-icon-amber {
  background: linear-gradient(135deg, #92400e, #f59e0b);
  box-shadow: 0 2px 8px rgba(245, 158, 11, 0.4);
}
.nav-dd-icon-cyan {
  background: linear-gradient(135deg, #0e7490, #06b6d4);
  box-shadow: 0 2px 8px rgba(6, 182, 212, 0.4);
}
.nav-dd-icon-green {
  background: linear-gradient(135deg, #065f46, #10b981);
  box-shadow: 0 2px 8px rgba(16, 185, 129, 0.4);
}
.nav-dd-icon-violet {
  background: linear-gradient(135deg, #4c1d95, #7c3aed);
  box-shadow: 0 2px 8px rgba(124, 58, 237, 0.4);
}
</style>
