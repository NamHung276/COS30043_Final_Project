<template>
  <div class="navbar-wrapper">
    <!-- Email Verification Banner -->
    <div v-if="currentUser && !currentUser.emailVerified" class="alert alert-warning text-center rounded-0 mb-0 py-2 border-0" style="z-index: 1050; position: relative;">
      <small>
        <strong>Action Required:</strong> Please verify your email address ({{ currentUser.email }}) to unlock purchasing. 
        <button @click="resendVerification" class="btn btn-sm btn-link p-0 fw-bold ms-2 text-dark" :disabled="resendingEmail">
          {{ resendingEmail ? 'Sending...' : 'Resend Email' }}
        </button>
      </small>
    </div>
  <nav
    class="navbar navbar-expand-lg"
    :class="theme === 'dark' ? 'navbar-dark' : 'navbar-light'"
  >
    <div class="container">
      <router-link class="navbar-brand" to="/" aria-label="GameHub Home">
        <img
          src="/logo/gamepad.svg"
          width="20"
          height="20"
          alt=""
          aria-hidden="true"
          class="logo-img"
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
            <router-link class="nav-link" to="/" @click="closeMenu" :exact-active-class="'nav-link-active'" active-class="">
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
            <router-link class="nav-link" to="/live-news" @click="closeMenu" active-class="nav-link-active">
              News
            </router-link>
          </li>

          <li class="nav-item">
            <router-link class="nav-link" to="/gamehub-news" @click="closeMenu" active-class="nav-link-active">
              Community
            </router-link>
          </li>

          <li class="nav-item">
            <router-link class="nav-link" to="/converter" @click="closeMenu" :exact-active-class="'nav-link-active'" active-class="">
              Converter
            </router-link>
          </li>

          <li class="nav-item">
            <router-link class="nav-link" to="/about" @click="closeMenu" :exact-active-class="'nav-link-active'" active-class="">
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

          <!-- Notification Bell -->
          <li class="nav-item dropdown d-none d-lg-flex me-2">
            <a
              class="nav-link position-relative d-flex align-items-center"
              href="#"
              role="button"
              data-bs-toggle="dropdown"
              aria-expanded="false"
              @click="onBellClick"
            >
              <i class="bi bi-bell fs-5" aria-hidden="true"></i>
              <span
                v-if="notificationStore?.unreadCount > 0"
                class="position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger"
                style="font-size: 0.6rem; transform: translate(-30%, 10%) !important;"
              >
                {{ notificationStore.unreadCount }}
              </span>
            </a>
            <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0 notification-dropdown-menu mt-2 p-0">
              <li class="px-3 py-2 d-flex justify-content-between align-items-center border-bottom border-secondary border-opacity-25 bg-dark text-white rounded-top">
                <span class="fw-bold">Notifications</span>
                <button v-if="notificationStore?.unreadCount > 0" class="btn btn-sm btn-link text-decoration-none p-0 text-info" @click.stop="notificationStore.markAllAsRead()">Mark all as read</button>
              </li>
              <div class="notification-list custom-scrollbar">
                <div v-if="!notificationStore?.sortedNotifications.length" class="p-4 text-center text-muted">
                  <i class="bi bi-bell-slash fs-1 d-block mb-2"></i>
                  No notifications yet.
                </div>
                <template v-else>
                  <li v-for="notif in notificationStore.sortedNotifications" :key="notif.id" class="notification-item border-bottom border-secondary border-opacity-25" :class="{ 'unread': !notif.read }">
                    <div class="p-3 d-flex gap-3 align-items-start" @click="handleNotificationClick(notif)">
                      <div class="notif-icon mt-1" :class="getNotifIconClass(notif.type)">
                        <i class="bi" :class="getNotifIcon(notif.type)"></i>
                      </div>
                      <div class="notif-content flex-grow-1">
                        <div class="d-flex justify-content-between align-items-center mb-1">
                          <strong class="notif-title" :class="{'text-white': !notif.read, 'text-muted-light': notif.read}">{{ notif.title }}</strong>
                          <small class="text-muted" style="font-size:0.7rem;">{{ formatTimeAgo(notif.createdAt) }}</small>
                        </div>
                        <p class="mb-0 notif-message" :class="{'text-white-50': !notif.read, 'text-muted': notif.read}">{{ notif.message }}</p>
                      </div>
                      <div class="notif-actions d-flex flex-column gap-2">
                        <button v-if="!notif.read" class="btn btn-sm btn-link p-0 text-success" @click.stop="notificationStore.markAsRead(notif.id)" title="Mark as read">
                          <i class="bi bi-check-circle-fill"></i>
                        </button>
                        <button class="btn btn-sm btn-link p-0 text-danger" @click.stop="notificationStore.deleteNotification(notif.id)" title="Delete">
                          <i class="bi bi-trash-fill"></i>
                        </button>
                      </div>
                    </div>
                  </li>
                </template>
              </div>
            </ul>
          </li>

          <!-- Cart Link -->
          <router-link
            class="nav-link d-flex align-items-center position-relative me-3"
            to="/checkout"
            @click="closeMenu"
            aria-label="Shopping Cart"
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



          <template v-if="!currentUser && authReady">
            <!-- Settings for Logged-Out Users -->
            <li class="nav-item dropdown list-unstyled ms-0 ms-lg-1 me-2">
              <a
                class="nav-link dropdown-toggle d-flex align-items-center"
                href="#"
                role="button"
                data-bs-toggle="dropdown"
                aria-expanded="false"
                title="Settings"
              >
                <i class="bi bi-gear-fill"></i>
              </a>
              <ul class="dropdown-menu dropdown-menu-end shadow-sm border-0 user-dropdown-menu mt-2">
                <li>
                  <button class="dropdown-item nav-dd-item" @click.stop="toggleTheme">
                    <span class="nav-dd-icon" style="background: rgba(148, 163, 184, 0.15); box-shadow: 0 2px 8px rgba(148, 163, 184, 0.2);">
                      <i v-if="theme === 'dark'" class="bi bi-moon-fill" style="font-size: 0.85rem; color: #94a3b8"></i>
                      <i v-else class="bi bi-sun-fill" style="font-size: 0.85rem; color: #f59e0b"></i>
                    </span>
                    Theme: {{ theme === 'dark' ? 'Dark' : 'Light' }}
                  </button>
                </li>
              </ul>
            </li>

            <router-link class="nav-btn-login" to="/login" @click="closeMenu">Login</router-link>
            <router-link class="nav-btn-signup" to="/register" @click="closeMenu">Sign Up</router-link>
          </template>

          <template v-if="currentUser">
            <!-- User Menu Dropdown -->
            <li class="nav-item dropdown list-unstyled ms-0 ms-lg-1">
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
                  <router-link class="dropdown-item nav-dd-item" to="/reviews" @click="closeMenu">
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
                <li>
                  <button class="dropdown-item nav-dd-item" @click.stop="toggleTheme">
                    <span class="nav-dd-icon" style="background: rgba(148, 163, 184, 0.15); box-shadow: 0 2px 8px rgba(148, 163, 184, 0.2);">
                      <i v-if="theme === 'dark'" class="bi bi-moon-fill" style="font-size: 0.85rem; color: #94a3b8"></i>
                      <i v-else class="bi bi-sun-fill" style="font-size: 0.85rem; color: #f59e0b"></i>
                    </span>
                    Theme: {{ theme === 'dark' ? 'Dark' : 'Light' }}
                  </button>
                </li>
                <li><hr class="dropdown-divider border-secondary opacity-25"></li>

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
  </div>
</template>

<script>
import { auth, db } from "../firebase";
import { onAuthStateChanged, signOut, sendEmailVerification } from "firebase/auth";
import { doc, getDoc } from "firebase/firestore";
import { cartState } from "../services/cart";
import { backendApi } from "../services/api";
import { useNotificationStore } from "../stores/useNotificationStore";
import { useLibraryStore } from "../stores/useLibraryStore";
import { useWishlistStore } from "../stores/useWishlistStore";

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
      notificationStore: null,
      resendingEmail: false,
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
      
      if (!this.notificationStore) {
        this.notificationStore = useNotificationStore();
      }
      
      if (user) {
        this.notificationStore.init();
        try {
          const snap = await getDoc(doc(db, "users", user.uid));
          this.isAdmin = snap.exists() && snap.data().role === "admin";
        } catch {
          this.isAdmin = false;
        }
      } else {
        this.notificationStore.stopListening();
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
    async resendVerification() {
      if (!this.currentUser || this.resendingEmail) return;
      this.resendingEmail = true;
      try {
        await sendEmailVerification(this.currentUser);
        alert("Verification email sent! Please check your inbox.");
      } catch (err) {
        console.error("Error resending email:", err);
        alert("Failed to send verification email. Please try again later.");
      } finally {
        this.resendingEmail = false;
      }
    },
    toggleTheme() {
      this.theme = this.theme === "dark" ? "light" : "dark";
      document.documentElement.setAttribute("data-theme", this.theme);
      localStorage.setItem("gamehub-theme", this.theme);
    },

    async logout() {
      try {
        // Clear user-specific stores BEFORE signing out so they are
        // wiped regardless of whether signOut() succeeds.
        cartState.clear();
        useLibraryStore().clearStore();
        useWishlistStore().reset();

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
        const { data } = await backendApi.get("/games", {
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

    // ── Notifications ───────────────────────────────────
    onBellClick() {
      // Optional: Logic when bell is clicked
    },
    
    handleNotificationClick(notif) {
      if (!notif.read) {
        this.notificationStore.markAsRead(notif.id);
      }
      if (notif.link) {
        this.$router.push(notif.link);
      }
    },
    
    getNotifIcon(type) {
      switch (type) {
        case 'wishlist': return 'bi-heart-fill';
        case 'social': return 'bi-people-fill';
        case 'system': return 'bi-info-circle-fill';
        default: return 'bi-bell-fill';
      }
    },
    
    getNotifIconClass(type) {
      switch (type) {
        case 'wishlist': return 'text-danger bg-danger bg-opacity-10';
        case 'social': return 'text-primary bg-primary bg-opacity-10';
        case 'system': return 'text-info bg-info bg-opacity-10';
        default: return 'text-secondary bg-secondary bg-opacity-10';
      }
    },
    
    formatTimeAgo(timestamp) {
      if (!timestamp?.seconds) return 'Just now';
      const seconds = Math.floor(Date.now() / 1000 - timestamp.seconds);
      if (seconds < 60) return 'Just now';
      const minutes = Math.floor(seconds / 60);
      if (minutes < 60) return `${minutes}m ago`;
      const hours = Math.floor(minutes / 60);
      if (hours < 24) return `${hours}h ago`;
      const days = Math.floor(hours / 24);
      return `${days}d ago`;
    }
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
  background: var(--overlay-medium);
  border: 1px solid var(--overlay-medium);
  border-radius: 10px;
  padding: 6px 12px;
  width: 200px;
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: text;
}

.nav-search-container.active,
.nav-search-container:focus-within {
  width: 280px;
  background: var(--overlay-medium);
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

/* ── Notifications Dropdown ─────────────────────────── */
.notification-dropdown-menu {
  width: 320px;
  background: var(--bg-surface);
  border: 1px solid var(--border-glass);
  border-radius: 14px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4), 0 0 0 1px var(--overlay-light);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  overflow: hidden;
  animation: searchDropIn 0.18s cubic-bezier(0.4, 0, 0.2, 1);
}

.notification-list {
  max-height: 350px;
  overflow-y: auto;
}

.notification-item {
  transition: background 0.15s ease;
  cursor: pointer;
}

.notification-item:hover {
  background: rgba(14, 165, 233, 0.08);
}

.notification-item.unread {
  background: rgba(14, 165, 233, 0.04);
}
.notification-item.unread:hover {
  background: rgba(14, 165, 233, 0.12);
}

.notif-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 1.1rem;
}

.notif-message {
  font-size: 0.82rem;
  line-height: 1.3;
}

[data-theme="light"] .notification-dropdown-menu {
  background: #ffffff;
  border-color: rgba(0,0,0,0.1);
  box-shadow: 0 10px 40px rgba(0,0,0,0.1);
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
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5), 0 0 0 1px var(--overlay-light);
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
  color: var(--text-primary);
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
  background: linear-gradient(90deg, var(--bg-glass) 25%, var(--overlay-medium) 50%, var(--bg-glass) 75%);
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
  background: var(--bg-surface) !important;
  border: 1px solid var(--overlay-border) !important;
  border-radius: var(--radius-md) !important;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3) !important;
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
  background: var(--overlay-medium) !important;
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

@media (max-width: 991px) {
  .user-dropdown-menu {
    min-width: 100% !important;
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 10px !important;
    position: relative !important;
    float: none !important;
    margin-top: 0 !important;
  }
  .dropdown-menu.show {
    display: block;
  }
}
</style>
