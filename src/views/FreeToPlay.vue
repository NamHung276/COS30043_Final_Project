<script>
import { backendApi } from "../services/api";
import SkeletonCard from "../components/SkeletonCard.vue";
import { inject } from "vue";
import { mapState } from "pinia";
import { useAuthStore } from "../stores/useAuthStore";
import { useWishlistStore } from "../stores/useWishlistStore";

const ALL_CATEGORIES = [
  "mmorpg",
  "shooter",
  "strategy",
  "moba",
  "racing",
  "sports",
  "social",
  "sandbox",
  "open-world",
  "survival",
  "pvp",
  "pve",
  "pixel",
  "voxel",
  "zombie",
  "turn-based",
  "first-person",
  "third-Person",
  "top-down",
  "tank",
  "space",
  "sailing",
  "side-scroller",
  "superhero",
  "permadeath",
  "card",
  "battle-royale",
  "mmo",
  "mmofps",
  "mmotps",
  "3d",
  "2d",
  "anime",
  "fantasy",
  "sci-fi",
  "fighting",
  "action-rpg",
  "action",
  "military",
  "martial-arts",
  "flight",
  "low-spec",
  "tower-defense",
  "horror",
  "mmorts",
];

export default {
  components: { SkeletonCard },
  setup() {
    const toast = inject("toast");
    return { toast };
  },

  data() {
    return {
      games: [],
      loading: false,
      error: null,
      platform: "all",
      category: "",
      sortBy: "relevance",
      viewMode: "grid",
      selectedTags: [],
      tagMode: false,
      searchTerm: "",
      currentPage: 1,
      itemsPerPage: 12,
      allCategories: ALL_CATEGORIES,
    };
  },

  computed: {
    // Auth & wishlist state from centralised stores
    ...mapState(useAuthStore, ["currentUser"]),
    ...mapState(useWishlistStore, ["wishlistedIds"]),

    filteredGames() {
      const term = this.searchTerm.toLowerCase().trim();
      if (!term) return this.games;
      return this.games.filter(
        (g) =>
          g.title.toLowerCase().includes(term) ||
          (g.short_description || "").toLowerCase().includes(term),
      );
    },
    totalPages() {
      return Math.ceil(this.filteredGames.length / this.itemsPerPage);
    },
    paginatedGames() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      return this.filteredGames.slice(start, start + this.itemsPerPage);
    },
    visiblePages() {
      const total = this.totalPages;
      const pages = [];
      if (total <= 7) {
        for (let i = 1; i <= total; i++) pages.push(i);
      } else {
        pages.push(1);
        if (this.currentPage > 4) pages.push("...");
        const s = Math.max(2, this.currentPage - 1);
        const e = Math.min(total - 1, this.currentPage + 1);
        for (let i = s; i <= e; i++) pages.push(i);
        if (this.currentPage < total - 3) pages.push("...");
        pages.push(total);
      }
      return pages;
    },
    activeSummary() {
      const parts = [];
      if (this.tagMode && this.selectedTags.length)
        parts.push(`Tags: ${this.selectedTags.join(" + ")}`);
      else {
        if (this.platform !== "all") parts.push(`Platform: ${this.platform}`);
        if (this.category) parts.push(`Category: ${this.category}`);
      }
      if (this.sortBy !== "relevance") parts.push(`Sort: ${this.sortBy}`);
      return parts.length ? parts.join("  ·  ") : "Showing all games";
    },
  },

  watch: {
    searchTerm() {
      this.currentPage = 1;
    },

    // React when navigating between genre tiles (query param changes)
    "$route.query.category"(newCat) {
      const cat = newCat || "";
      if (cat !== this.category) {
        this.category = cat;
        this.fetchGames();
      }
    },
  },

  methods: {
    platformIcon(platform) {
      if (!platform) return "/game_logo/pc.svg";
      if (platform.toLowerCase().includes("browser")) return null; // use inline SVG
      return "/game_logo/pc.svg";
    },

    isBrowser(platform) {
      return platform && platform.toLowerCase().includes("browser");
    },

    platformLabel(platform) {
      if (!platform) return "PC";
      if (platform.toLowerCase().includes("browser")) return "Browser";
      return "PC (Windows)";
    },

    async toggleWishlist(game, event) {
      event.stopPropagation();
      if (!this.currentUser) {
        this.toast?.show("Please log in to add to wishlist", "warning");
        this.$router.push("/login");
        return;
      }
      // Pass itemType so the store sets source: 'freetogame' correctly
      const wishlistStore = useWishlistStore();
      await wishlistStore.toggleWishlist({ ...game, itemType: "f2p" }, this.toast);
    },

    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    },

    toggleTag(tag) {
      const idx = this.selectedTags.indexOf(tag);
      if (idx === -1) this.selectedTags.push(tag);
      else this.selectedTags.splice(idx, 1);
    },

    clearFilters() {
      this.platform = "all";
      this.category = "";
      this.sortBy = "relevance";
      this.selectedTags = [];
      this.searchTerm = "";
      this.fetchGames();
    },

    async fetchGames() {
      this.loading = true;
      this.error = null;
      this.currentPage = 1;
      try {
        const params = {};
        if (this.platform !== "all") params.platform = this.platform;
        if (this.sortBy !== "relevance") params.sort_by = this.sortBy;
        if (this.tagMode && this.selectedTags.length) {
          params.tag = this.selectedTags.join(".");
        } else if (this.category) {
          params.category = this.category;
        }
        const res = await backendApi.get("/free-games", { params });
        this.games = res.data.results || [];
      } catch (err) {
        console.error(err);
        this.error = "Failed to load games. Please try again.";
        this.games = [];
      } finally {
        this.loading = false;
      }
    },
  },

  mounted() {
    const queryCat = this.$route.query.category;
    if (queryCat && typeof queryCat === "string") {
      this.category = queryCat;
    }
    this.fetchGames();
  },
};
</script>

<template>
  <div class="games-page">
    <!-- ══ Page Header ══ -->
    <div class="games-page-header">
      <div class="games-page-header-bg" aria-hidden="true"></div>
      <div class="container games-header-content">
        <div class="games-title-row">
          <span class="games-title-icon" aria-hidden="true">
            <img src="/logo/gamepad.svg" width="28" height="28" alt="" />
          </span>
          <div>
            <h1 class="games-title">Free to Play</h1>
            <p class="games-subtitle">
              <strong>{{ filteredGames.length.toLocaleString() }}</strong>
              browser &amp; PC titles — no cost required
              <span class="text-muted ms-2">· Powered by FreeToGame</span>
            </p>
          </div>
        </div>

        <!-- ══ Filter Panel ══ -->
        <div class="games-filters mt-4">
          <!-- Search -->
          <div class="games-search-wrap flex-grow-1">
            <img
              src="/logo/search.svg"
              class="games-search-icon"
              width="17"
              height="17"
              alt=""
              aria-hidden="true"
            />
            <input
              v-model="searchTerm"
              type="text"
              class="games-search-input w-100"
              placeholder="Search by title or description…"
              aria-label="Search free-to-play games"
            />
          </div>

          <!-- Category dropdown (if not tag mode) -->
          <select
            v-if="!tagMode"
            v-model="category"
            class="games-genre-select"
            @change="fetchGames()"
            aria-label="Filter by category"
          >
            <option value="">All Categories</option>
            <option v-for="cat in allCategories" :key="cat" :value="cat">
              {{ cat.charAt(0).toUpperCase() + cat.slice(1).replace(/-/g, " ") }}
            </option>
          </select>

          <!-- Sort -->
          <select
            v-model="sortBy"
            class="games-genre-select"
            @change="fetchGames()"
            aria-label="Sort games by"
          >
            <option value="relevance">Sort: Relevance</option>
            <option value="popularity">Sort: Popularity</option>
            <option value="release-date">Sort: Release Date</option>
            <option value="alphabetical">Sort: Alphabetical</option>
          </select>

          <!-- View toggle -->
          <div class="view-toggle">
            <button
              class="view-btn"
              :class="{ active: viewMode === 'grid' }"
              @click="viewMode = 'grid'"
              aria-label="Grid view"
              title="Grid view"
            >
              ⊞
            </button>
            <button
              class="view-btn"
              :class="{ active: viewMode === 'list' }"
              @click="viewMode = 'list'"
              aria-label="List view"
              title="List view"
            >
              ≡
            </button>
          </div>
          
          <button
            class="btn btn-outline-secondary d-flex align-items-center gap-2 px-3"
            @click="clearFilters"
            title="Reset all filters"
            aria-label="Clear filters"
            style="border-color: var(--border-subtle); color: var(--text-secondary);"
          >
            <i class="bi bi-x-circle"></i> Clear
          </button>
        </div>

        <!-- Platform Tabs & Tag Mode -->
        <div class="d-flex flex-wrap align-items-center justify-content-between mt-3 mb-2 gap-3">
          <div class="platform-tabs m-0">
            <button
              v-for="p in ['all', 'windows', 'browser']"
              :key="p"
              type="button"
              class="platform-tab"
              :class="{ active: platform === p }"
              @click="platform = p; fetchGames();"
            >
              <img
                v-if="p === 'windows'"
                src="/game_logo/pc.svg"
                width="16"
                height="16"
                alt="Windows"
              />
              <svg
                v-else-if="p === 'browser'"
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
                aria-hidden="true"
              >
                <circle cx="12" cy="12" r="10" />
                <path d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z" />
              </svg>
              {{ p === "all" ? "All Platforms" : p === "windows" ? "Windows" : "Browser" }}
            </button>
          </div>

          <div class="ftg-mode-toggle d-flex align-items-center gap-2">
            <label class="ftg-switch-label d-flex align-items-center gap-2 m-0" style="cursor: pointer;">
              <span class="ftg-switch-text text-muted small">{{ tagMode ? "Multi-tag mode ON" : "Multi-tag mode OFF" }}</span>
              <div class="form-check form-switch m-0" style="font-size: 1.25rem;">
                <input
                  class="form-check-input"
                  type="checkbox"
                  role="switch"
                  id="tagModeSwitch"
                  v-model="tagMode"
                  @change="selectedTags = []; category = ''; fetchGames();"
                  style="cursor: pointer;"
                />
              </div>
            </label>
          </div>
        </div>

        <!-- Multi-tag cloud -->
        <div v-if="tagMode" class="mt-3 mb-4 p-3 bg-surface-var bg-opacity-25 rounded-3 border border-secondary border-opacity-25">
          <span class="d-block text-muted small mb-2"><i class="bi bi-tags-fill me-1"></i> Select multiple tags:</span>
          <div class="d-flex flex-wrap gap-2">
            <button
              v-for="tag in allCategories"
              :key="tag"
              type="button"
              class="btn btn-sm rounded-pill transition-all"
              :class="selectedTags.includes(tag) ? 'btn-primary shadow-sm' : 'btn-outline-secondary bg-surface-var bg-opacity-50 text-primary-var border-0'"
              @click="toggleTag(tag); fetchGames();"
            >
              {{ tag }}
            </button>
          </div>
        </div>

        <!-- Active summary + result count -->
        <div class="ftg-summary-row d-flex align-items-center gap-2">
          <span class="ftg-summary-text">{{ activeSummary }}</span>
          <span v-if="!loading" class="ftg-results-badge badge bg-secondary bg-opacity-25 text-light"
            >{{ filteredGames.length }} results</span
          >
        </div>
      </div>
    </div>

    <!-- ══ Content Area ══ -->
    <div class="container pb-5">
      <!-- ══════════════════════════════════════
           FEATURED GAMES (RECOMMENDATIONS)
           ══════════════════════════════════════ -->
      <div v-if="!searchTerm && currentPage === 1 && games.length" class="mb-5">
        <div class="d-flex align-items-center mb-4">
          <span class="section-icon me-3" style="background: linear-gradient(135deg, #10b981, #047857); box-shadow: 0 4px 16px rgba(16, 185, 129, 0.4); border-radius: 12px; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center;">
            <i class="bi bi-star-fill" style="color: white; font-size: 1.1rem"></i>
          </span>
          <h2 class="mb-0 fw-bold" style="color: var(--text-primary)">Featured Games</h2>
        </div>
        <div class="gd-recommendation-carousel pb-3">
          <router-link
            v-for="g in games.slice(0, 8)"
            :key="g.id"
            :to="`/free-to-play/${g.id}`"
            class="gd-rec-card text-decoration-none"
          >
            <div class="gd-rec-img-wrapper">
              <img :src="g.thumbnail" :alt="g.title" class="gd-rec-img" />
            </div>
            <div class="gd-rec-info p-3">
              <h6 class="gd-rec-title fw-bold mb-1 text-truncate" :title="g.title">{{ g.title }}</h6>
              <div class="d-flex justify-content-between align-items-center mt-2">
                <span class="gd-rec-genre text-muted small text-truncate" style="max-width: 60%">{{ g.genre || 'Game' }}</span>
                <span class="gd-rec-price fw-bold text-success small">Free</span>
              </div>
            </div>
          </router-link>
        </div>
      </div>
      <!-- Skeleton Loading -->
      <div v-if="loading" class="games-grid">
        <SkeletonCard v-for="n in 12" :key="n" />
      </div>

      <!-- Error -->
      <div v-else-if="error" class="ftg-error">
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
          aria-hidden="true"
        >
          <circle cx="12" cy="12" r="10" />
          <path d="M12 8v4m0 4h.01" />
        </svg>
        <h3>Something went wrong</h3>
        <p>{{ error }}</p>
        <button class="ftg-primary-btn" @click="fetchGames()">Try Again</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredGames.length === 0" class="games-empty-state">
        <img
          src="/logo/search.svg"
          width="60"
          height="60"
          alt=""
          aria-hidden="true"
          style="opacity: 0.35"
        />
        <h3>No games found</h3>
        <p>Try adjusting your filters or clearing the search term.</p>
      </div>

      <!-- Games Grid -->
      <div v-else-if="viewMode === 'grid'" class="games-grid">
        <router-link
          v-for="(game, index) in paginatedGames"
          :key="game.id"
          :to="`/free-to-play/${game.id}`"
          class="game-card stagger-item"
          :style="{ animationDelay: `${(index % 12) * 0.04}s` }"
          :aria-label="`View details for ${game.title}`"
        >
          <!-- Cover Image -->
          <div class="game-card-img-wrap">
            <img
              v-if="game.thumbnail"
              v-lazy-img="game.thumbnail"
              class="game-card-img"
              :alt="`${game.title} cover art`"
            />
            <div v-else class="game-card-img-placeholder">
              <img
                src="/logo/gamepad.svg"
                width="36"
                height="36"
                alt=""
                aria-hidden="true"
                style="opacity: 0.4"
              />
            </div>
            <div class="game-card-img-overlay" aria-hidden="true"></div>

            <div class="game-card-hover" aria-hidden="true">
              <div class="hover-content">
                <span class="hover-action">View Details</span>
              </div>
            </div>

            <!-- Floating action buttons -->
            <div class="card-float-actions">
              <!-- Wishlist button -->
              <button
                class="card-float-btn wishlist-btn"
                :class="{ wishlisted: wishlistedIds.has(String(game.id)) }"
                @click.prevent="toggleWishlist(game, $event)"
                :title="
                  wishlistedIds.has(String(game.id))
                    ? 'In Wishlist'
                    : 'Add to Wishlist'
                "
                :aria-label="
                  wishlistedIds.has(String(game.id))
                    ? 'In Wishlist'
                    : 'Add to Wishlist'
                "
              >
                {{ wishlistedIds.has(String(game.id)) ? "♥" : "♡" }}
              </button>
            </div>

            <!-- Genre Ribbon -->
            <div class="genre-ribbon" v-if="game.genre">
              {{ game.genre }}
            </div>

            <!-- Platform icons -->
            <div class="game-card-platforms">
              <span class="platform-icon" :title="platformLabel(game.platform)">
                <svg
                  v-if="isBrowser(game.platform)"
                  width="13"
                  height="13"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="10" />
                  <path
                    d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"
                  />
                </svg>
                <img
                  v-else
                  :src="platformIcon(game.platform)"
                  width="13"
                  height="13"
                  :alt="platformLabel(game.platform)"
                />
              </span>
            </div>
          </div>

          <!-- Card Body -->
          <div class="game-card-body">
            <div class="game-card-header">
              <h3 class="game-card-title">{{ game.title }}</h3>
              <span class="game-type free">FREE</span>
            </div>

            <!-- Genre tags -->
            <div class="game-card-genres">
              <span class="game-genre-tag">{{ game.genre }}</span>
            </div>



            <!-- Price row -->
            <div class="game-card-price-row">
              <span class="price-current">Free to Play</span>
              <span class="game-source-pill">FreeToGame</span>
            </div>
          </div>
        </router-link>
      </div>

      <!-- Games List -->
      <div v-else class="games-list">
        <router-link
          v-for="(game, index) in paginatedGames"
          :key="game.id"
          :to="`/free-to-play/${game.id}`"
          class="game-list-row stagger-item"
          :style="{ animationDelay: `${(index % 12) * 0.03}s` }"
        >
          <div class="glr-thumb-wrap">
            <img
              v-lazy-img="game.thumbnail"
              :alt="game.title"
              class="glr-thumb"
            />
          </div>
          <div class="glr-info">
            <div class="glr-title">{{ game.title }}</div>
            <div class="glr-meta">
              <span class="game-genre-tag">{{ game.genre }}</span>
              <span class="glr-year">{{ platformLabel(game.platform) }}</span>
            </div>
          </div>
          <div class="glr-right">
            <div class="glr-price">
              <span class="price-free">Free to Play</span>
            </div>
          </div>
        </router-link>
      </div>

      <!-- Pagination -->
      <nav
        v-if="!loading && totalPages > 1"
        class="ftg-pagination"
        aria-label="Free-to-play games pagination"
      >
        <button
          class="ftg-page-btn"
          :disabled="currentPage === 1"
          @click="goToPage(currentPage - 1)"
        >
          <img
            src="/logo/arrow-left.svg"
            width="15"
            height="15"
            alt=""
            aria-hidden="true"
          />
          Previous
        </button>
        <div class="ftg-page-numbers">
          <template v-for="(page, index) in visiblePages" :key="index">
            <span v-if="page === '...'" class="ftg-page-ellipsis">&#8230;</span>
            <button
              v-else
              class="ftg-page-num-btn"
              :class="{ active: currentPage === page }"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
          </template>
        </div>
        <button
          class="ftg-page-btn"
          :disabled="currentPage === totalPages"
          @click="goToPage(currentPage + 1)"
        >
          Next
          <img
            src="/logo/arrow-right.svg"
            width="15"
            height="15"
            alt=""
            aria-hidden="true"
          />
        </button>
      </nav>

      <p v-if="!loading && totalPages > 1" class="ftg-page-info">
        Page {{ currentPage }} of {{ totalPages }} ·
        {{ filteredGames.length }} {{ filteredGames.length === 1 ? 'game' : 'games' }} shown
      </p>
    </div>
  </div>
</template>

<style scoped>
/* ── Free-To-Play Specific Styles ── */

.ftg-primary-btn {
  background: var(--bg-surface);
  color: var(--text-primary);
  border: 1px solid var(--border-glass);
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}
.ftg-primary-btn:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-2px);
}

.ftg-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 2rem;
  padding: 1rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
}
.ftg-page-btn {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-glass);
  padding: 8px 16px;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 8px;
}
.ftg-page-btn:hover:not(:disabled) {
  background: rgba(255,255,255,0.05);
}
.ftg-page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.ftg-page-numbers {
  display: flex;
  gap: 6px;
}
.ftg-page-num-btn {
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid transparent;
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  transition: all 0.2s;
}
.ftg-page-num-btn:hover:not(.active) {
  background: rgba(255,255,255,0.05);
}
.ftg-page-num-btn.active {
  background: var(--accent);
  color: #fff;
  box-shadow: 0 4px 12px rgba(109, 40, 217, 0.4);
}
.ftg-page-ellipsis {
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
}
.ftg-page-info {
  text-align: center;
  margin-top: 1rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}
</style>
