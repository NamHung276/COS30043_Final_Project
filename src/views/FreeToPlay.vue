<script>
import { freeToGameApi } from "../services/api";
import SkeletonCard from "../components/SkeletonCard.vue";

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
  inject: ["toast"],

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
      wishlisted: new Set(),
    };
  },

  computed: {
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

    ftgRating(game) {
      // Mock rating based on ID for consistency since FTG API doesn't have ratings
      return (game.id % 20) / 10 + 3;
    },

    ratingStars(rating) {
      const stars = [];
      for (let i = 1; i <= 5; i++) {
        if (rating >= i) stars.push("full");
        else if (rating >= i - 0.5) stars.push("half");
        else stars.push("empty");
      }
      return stars;
    },

    ratingLabel(rating) {
      if (rating >= 4.5) return "Overwhelmingly Positive";
      if (rating >= 4.0) return "Very Positive";
      if (rating >= 3.0) return "Mostly Positive";
      return "Mixed";
    },

    addToWishlist(game, event) {
      const gameId = String(game.id);
      if (this.wishlisted.has(gameId)) {
        this.wishlisted.delete(gameId);
        this.toast?.show(`${game.title} removed from wishlist`, "info");
      } else {
        this.wishlisted.add(gameId);
        this.toast?.show(`${game.title} added to wishlist!`, "success");
      }
      this.wishlisted = new Set(this.wishlisted); // trigger reactivity
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
        let data;
        if (this.tagMode && this.selectedTags.length) {
          const params = { tag: this.selectedTags.join(".") };
          if (this.platform !== "all") params.platform = this.platform;
          if (this.sortBy !== "relevance") params.sort = this.sortBy;
          const res = await freeToGameApi.get("/filter", { params });
          data = res.data;
        } else {
          const params = {};
          if (this.platform !== "all") params.platform = this.platform;
          if (this.category) params.category = this.category;
          if (this.sortBy !== "relevance") params["sort-by"] = this.sortBy;
          const res = await freeToGameApi.get("/games", { params });
          data = res.data;
        }
        this.games = Array.isArray(data) ? data : [];
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
    // Pick up ?category= from the URL if coming from a genre tile
    const queryCat = this.$route.query.category;
    if (queryCat && typeof queryCat === "string") {
      this.category = queryCat;
    }
    this.fetchGames();
  },
};
</script>

<template>
  <div class="ftg-page">
    <!-- ══ Page Header ══ -->
    <div class="ftg-page-header">
      <div class="ftg-header-bg" aria-hidden="true"></div>
      <div class="container ftg-header-content">
        <div class="ftg-title-row">
          <span class="ftg-title-icon" aria-hidden="true">
            <img src="/logo/gamepad.svg" width="28" height="28" alt="" />
          </span>
          <div>
            <h1 class="ftg-title">Free to Play</h1>
            <p class="ftg-subtitle">
              <strong>{{ filteredGames.length.toLocaleString() }}</strong>
              browser &amp; PC titles — no cost required
              <span class="ftg-powered">· Powered by FreeToGame</span>
            </p>
          </div>
        </div>

        <!-- ══ Filter Panel ══ -->
        <div class="ftg-filter-panel">
          <!-- Row 1: Search + Platform + Sort + Clear -->
          <div class="ftg-filter-row">
            <!-- Search -->
            <div class="ftg-search-wrap">
              <img
                src="/logo/search.svg"
                class="ftg-search-icon"
                width="16"
                height="16"
                alt=""
                aria-hidden="true"
              />
              <input
                v-model="searchTerm"
                type="text"
                class="ftg-search-input"
                placeholder="Search by title or description…"
                aria-label="Search free-to-play games"
              />
            </div>

            <!-- Platform tabs -->
            <div
              class="ftg-platform-group"
              role="group"
              aria-label="Platform filter"
            >
              <button
                v-for="p in ['all', 'windows', 'browser']"
                :key="p"
                type="button"
                class="ftg-platform-btn"
                :class="{ active: platform === p }"
                @click="
                  platform = p;
                  fetchGames();
                "
              >
                <img
                  v-if="p === 'windows'"
                  src="/game_logo/pc.svg"
                  width="14"
                  height="14"
                  alt="Windows"
                  class="ftg-platform-btn-icon"
                />
                <svg
                  v-else-if="p === 'browser'"
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  class="ftg-platform-btn-icon"
                  aria-hidden="true"
                >
                  <circle cx="12" cy="12" r="10" />
                  <path
                    d="M2 12h20M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"
                  />
                </svg>
                <span>{{
                  p === "all" ? "All" : p === "windows" ? "Windows" : "Browser"
                }}</span>
              </button>
            </div>

            <!-- Sort -->
            <select
              v-model="sortBy"
              class="ftg-sort-select"
              @change="fetchGames()"
              aria-label="Sort games by"
            >
              <option value="relevance">Relevance</option>
              <option value="popularity">Popularity</option>
              <option value="release-date">Release Date</option>
              <option value="alphabetical">Alphabetical</option>
            </select>

            <!-- View toggle -->
            <div class="view-toggle" style="margin-left: auto">
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

            <!-- Clear -->
            <button
              class="ftg-clear-btn"
              @click="clearFilters"
              title="Reset all filters"
              aria-label="Clear filters"
            >
              <svg
                width="14"
                height="14"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2.5"
                stroke-linecap="round"
                aria-hidden="true"
              >
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
              Clear
            </button>
          </div>

          <!-- Row 2: Mode toggle + Category / Tag Cloud -->
          <div class="ftg-filter-row-2">
            <div class="ftg-mode-toggle">
              <span class="ftg-filter-label">Filter Mode:</span>
              <label class="ftg-switch-label">
                <input
                  type="checkbox"
                  class="ftg-switch-input"
                  id="tagModeSwitch"
                  v-model="tagMode"
                  @change="
                    selectedTags = [];
                    category = '';
                    fetchGames();
                  "
                />
                <span class="ftg-switch-track"></span>
                <span class="ftg-switch-text">{{
                  tagMode ? "Multi-tag mode" : "Category mode"
                }}</span>
              </label>
            </div>

            <!-- Category dropdown -->
            <div v-if="!tagMode" class="ftg-category-wrap">
              <span class="ftg-filter-label">Category</span>
              <select
                v-model="category"
                class="ftg-sort-select"
                @change="fetchGames()"
                aria-label="Filter by category"
              >
                <option value="">All Categories</option>
                <option v-for="cat in allCategories" :key="cat" :value="cat">
                  {{
                    cat.charAt(0).toUpperCase() +
                    cat.slice(1).replace(/-/g, " ")
                  }}
                </option>
              </select>
            </div>

            <!-- Multi-tag cloud -->
            <div v-else class="ftg-tag-wrap">
              <span class="ftg-filter-label"
                >Tags
                <small class="ftg-tag-hint">(select multiple)</small></span
              >
              <div class="ftg-tag-cloud">
                <button
                  v-for="tag in allCategories"
                  :key="tag"
                  type="button"
                  class="ftg-tag-chip"
                  :class="{ active: selectedTags.includes(tag) }"
                  @click="
                    toggleTag(tag);
                    fetchGames();
                  "
                >
                  {{ tag }}
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Active summary + result count -->
        <div class="ftg-summary-row">
          <span class="ftg-summary-text">{{ activeSummary }}</span>
          <span v-if="!loading" class="ftg-results-badge"
            >{{ filteredGames.length }} results</span
          >
        </div>
      </div>
    </div>

    <!-- ══ Content Area ══ -->
    <div class="container ftg-content">
      <!-- Skeleton Loading -->
      <div v-if="loading" class="ftg-grid">
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
      <div v-else-if="filteredGames.length === 0" class="ftg-empty">
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
        <button class="ftg-primary-btn" @click="clearFilters">
          Clear All Filters
        </button>
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
                :class="{ wishlisted: wishlisted.has(String(game.id)) }"
                @click.prevent="addToWishlist(game, $event)"
                :title="
                  wishlisted.has(String(game.id))
                    ? 'In Wishlist'
                    : 'Add to Wishlist'
                "
                :aria-label="
                  wishlisted.has(String(game.id))
                    ? 'In Wishlist'
                    : 'Add to Wishlist'
                "
              >
                {{ wishlisted.has(String(game.id)) ? "♥" : "♡" }}
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

            <!-- Star Rating -->
            <div class="game-card-stars">
              <span
                v-for="(star, si) in ratingStars(ftgRating(game))"
                :key="si"
                class="star-icon"
                :class="star"
              >
                {{ star === "full" ? "★" : star === "half" ? "⯨" : "☆" }}
              </span>
              <span class="rating-label">{{
                ratingLabel(ftgRating(game))
              }}</span>
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
        {{ filteredGames.length }} games shown
      </p>
    </div>
  </div>
</template>

<style scoped>
/* ── Page ─────────────────────────────────────────── */
.ftg-page {
  min-height: 100vh;
  background: var(--bg-deep);
}

/* ── Header ───────────────────────────────────────── */
.ftg-page-header {
  position: relative;
  padding: 0;
  overflow: hidden;
  background: var(--bg-base);
  border-bottom: 1px solid var(--border-glass);
}
.ftg-header-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(
      ellipse 70% 120% at 90% 50%,
      rgba(16, 185, 129, 0.07) 0%,
      transparent 65%
    ),
    radial-gradient(
      ellipse 50% 80% at 10% 80%,
      rgba(124, 58, 237, 0.08) 0%,
      transparent 60%
    );
  pointer-events: none;
}
.ftg-header-content {
  position: relative;
  z-index: 1;
  padding-top: 40px;
  padding-bottom: 0;
}

/* Title row */
.ftg-title-row {
  display: flex;
  align-items: center;
  gap: 18px;
  margin-bottom: 20px;
}
.ftg-title-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 54px;
  height: 54px;
  border-radius: 16px;
  background: linear-gradient(135deg, #059669, #10b981);
  flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
}
.ftg-title {
  font-size: 2.1rem;
  font-weight: 800;
  color: var(--text-primary) !important;
  margin: 0 0 4px;
  line-height: 1;
}
.ftg-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary) !important;
  margin: 0;
}
.ftg-subtitle strong {
  color: var(--text-primary) !important;
}
.ftg-powered {
  opacity: 0.55;
}

/* ── Filter Panel ─────────────────────────────────── */
.ftg-filter-panel {
  background: var(--bg-surface);
  border: 1px solid var(--border-glass);
  border-bottom: none;
  border-radius: 14px 14px 0 0;
  padding: 20px 24px 16px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  margin-bottom: 0;
}

.ftg-filter-row {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}
.ftg-filter-row-2 {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  flex-wrap: wrap;
}
.ftg-filter-label {
  display: block;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.6px;
  color: var(--text-muted) !important;
  margin-bottom: 8px;
}

/* Search */
.ftg-search-wrap {
  flex: 1;
  min-width: 200px;
  position: relative;
}
.ftg-search-icon {
  position: absolute;
  left: 13px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  opacity: 0.6;
}
.ftg-search-input {
  width: 100%;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  color: var(--text-primary) !important;
  padding: 10px 14px 10px 38px;
  font-size: 0.88rem;
  font-family: var(--font-family);
  outline: none;
  transition: border-color 0.2s;
}
.ftg-search-input::placeholder {
  color: var(--text-muted);
}
.ftg-search-input:focus {
  border-color: var(--primary-light);
}

/* Platform buttons */
.ftg-platform-group {
  display: flex;
  gap: 6px;
}
.ftg-platform-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 14px;
  border-radius: 8px;
  border: 1px solid var(--border-glass);
  background: var(--bg-surface);
  color: var(--text-secondary) !important;
  font-size: 0.82rem;
  font-weight: 600;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.ftg-platform-btn:hover {
  border-color: rgba(16, 185, 129, 0.4);
  color: #6ee7b7 !important;
}
.ftg-platform-btn.active {
  background: linear-gradient(135deg, #059669, #10b981);
  border-color: transparent;
  color: #fff !important;
  box-shadow: 0 2px 14px rgba(16, 185, 129, 0.35);
}
.ftg-platform-btn-icon {
  filter: brightness(0.7);
  transition: filter 0.2s;
}
.ftg-platform-btn:hover .ftg-platform-btn-icon,
.ftg-platform-btn.active .ftg-platform-btn-icon {
  filter: brightness(1.2);
}

/* Sort select */
.ftg-sort-select {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  color: var(--text-primary) !important;
  padding: 9px 14px;
  font-size: 0.88rem;
  font-family: var(--font-family);
  outline: none;
  cursor: pointer;
  min-width: 150px;
  transition: border-color 0.2s;
}
.ftg-sort-select:focus {
  border-color: var(--primary-light);
}

/* Clear button */
.ftg-clear-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 16px;
  border-radius: 8px;
  border: 1px solid rgba(239, 68, 68, 0.3);
  background: rgba(239, 68, 68, 0.08);
  color: #f87171 !important;
  font-size: 0.82rem;
  font-weight: 600;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}
.ftg-clear-btn:hover {
  background: rgba(239, 68, 68, 0.18);
  border-color: rgba(239, 68, 68, 0.5);
}

/* Mode toggle (custom switch) */
.ftg-mode-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-top: 4px;
}
.ftg-switch-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
}
.ftg-switch-input {
  display: none;
}
.ftg-switch-track {
  width: 38px;
  height: 20px;
  border-radius: 10px;
  background: var(--border-glass);
  border: 1px solid var(--border-glass);
  position: relative;
  transition: background 0.2s;
  flex-shrink: 0;
}
.ftg-switch-track::after {
  content: "";
  position: absolute;
  top: 2px;
  left: 2px;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--text-muted);
  transition:
    transform 0.2s,
    background 0.2s;
}
.ftg-switch-input:checked + .ftg-switch-track {
  background: linear-gradient(135deg, #059669, #10b981);
  border-color: transparent;
}
.ftg-switch-input:checked + .ftg-switch-track::after {
  transform: translateX(18px);
  background: #fff;
}
.ftg-switch-text {
  font-size: 0.82rem;
  color: var(--text-secondary) !important;
  font-weight: 500;
}

/* Category wrap */
.ftg-category-wrap {
  display: flex;
  flex-direction: column;
}

/* Tag cloud */
.ftg-tag-wrap {
  flex: 1;
  display: flex;
  flex-direction: column;
}
.ftg-tag-hint {
  color: var(--text-muted) !important;
  font-size: 0.72rem;
  font-weight: 400;
}
.ftg-tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-height: 110px;
  overflow-y: auto;
  padding: 4px 0;
  scrollbar-width: thin;
  scrollbar-color: rgba(16, 185, 129, 0.3) transparent;
}
.ftg-tag-chip {
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 0.74rem;
  border: 1px solid var(--border-glass);
  background: var(--bg-surface);
  color: var(--text-secondary) !important;
  cursor: pointer;
  transition: all 0.15s;
  white-space: nowrap;
  font-family: var(--font-family);
}
.ftg-tag-chip:hover {
  border-color: rgba(16, 185, 129, 0.4);
  color: #6ee7b7 !important;
}
.ftg-tag-chip.active {
  background: linear-gradient(135deg, #059669, #10b981);
  border-color: transparent;
  color: #fff !important;
  font-weight: 600;
}

/* Summary row */
.ftg-summary-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 10px 24px;
  background: var(--bg-surface);
  border: 1px solid var(--border-glass);
  border-top: none;
  border-radius: 0 0 0 0;
  margin-bottom: 0;
}
.ftg-summary-text {
  font-size: 0.78rem;
  color: var(--text-muted) !important;
  font-style: italic;
}
.ftg-results-badge {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 3px 12px;
  border-radius: 20px;
  background: var(--gradient-primary);
  color: #fff !important;
  letter-spacing: 0.3px;
}

/* ── Content ──────────────────────────────────────── */
.ftg-content {
  padding-top: 28px;
  padding-bottom: 60px;
}

/* ── GRID ── */
.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
  padding-top: 10px;
}

.game-card {
  display: flex;
  flex-direction: column;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  overflow: hidden;
  text-decoration: none;
  transition: all 0.3s ease;
  position: relative;
}
.game-card:hover {
  transform: translateY(-5px);
  box-shadow:
    0 12px 30px rgba(0, 0, 0, 0.4),
    0 0 0 1px rgba(16, 185, 129, 0.3);
}

/* Image */
.game-card-img-wrap {
  position: relative;
  overflow: hidden;
  height: 180px;
  flex-shrink: 0;
  background: rgba(10, 15, 30, 0.5);
}
.game-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s ease;
}
.game-card:hover .game-card-img {
  transform: scale(1.05);
}
.game-card-img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-glass);
  color: var(--text-muted);
}
.game-card-img-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to bottom,
    transparent 40%,
    rgba(5, 7, 15, 0.65) 75%,
    rgba(5, 7, 15, 0.95) 100%
  );
  pointer-events: none;
}

.game-card-hover {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(5, 8, 18, 0.72);
  opacity: 0;
  transition: 0.28s ease;
  z-index: 3;
}
.game-card:hover .game-card-hover {
  opacity: 1;
}
.hover-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}
.hover-action {
  padding: 12px 26px;
  background: var(--gradient-primary);
  border-radius: 999px;
  font-weight: 700;
  transition: 0.25s;
}
.game-card:hover .hover-action {
  transform: translateY(0);
  color: #fff;
}

.genre-ribbon {
  position: absolute;
  left: 12px;
  top: 12px;
  z-index: 3;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(12, 17, 29, 0.82);
  backdrop-filter: blur(10px);
  font-size: 0.72rem;
  font-weight: 700;
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.08);
}

/* Platform icons */
.game-card-platforms {
  position: absolute;
  bottom: 10px;
  right: 10px;
  display: flex;
  gap: 5px;
  z-index: 2;
}
.platform-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 6px;
  background: var(--bg-glass);
  color: var(--text-primary);
  backdrop-filter: blur(6px);
  border: 1px solid var(--border-glass);
  transition:
    background 0.2s,
    color 0.2s;
}
.game-card:hover .platform-icon {
  background: var(--primary);
  color: #fff;
}

/* Card body */
.game-card-body {
  padding: 16px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}
.game-card-title {
  font-size: 0.97rem;
  font-weight: 700;
  line-height: 1.4;
  color: var(--text-primary) !important;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.game-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 10px;
}
.game-type {
  font-size: 0.65rem;
  font-weight: 800;
  padding: 5px 8px;
  border-radius: 999px;
  letter-spacing: 0.08em;
  flex-shrink: 0;
}
.game-type.free {
  background: #16a34a;
  color: white;
}
.game-type.premium {
  background: #f59e0b;
  color: #111;
}

/* Genre tags */
.game-card-genres {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.game-genre-tag {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  background: rgba(14, 165, 233, 0.15);
  color: var(--primary-light);
  border: 1px solid rgba(14, 165, 233, 0.28);
  letter-spacing: 0.02em;
  transition: background 0.2s;
}
.game-card:hover .game-genre-tag {
  background: rgba(14, 165, 233, 0.3);
  color: #fff;
}

/* Float action buttons on card image */
.card-float-actions {
  position: absolute;
  bottom: 45px;
  right: 10px;
  z-index: 5;
  display: flex;
  flex-direction: row;
  gap: 6px;
  opacity: 0;
  transform: translateY(6px);
  transition:
    opacity 0.25s,
    transform 0.25s;
}
.game-card:hover .card-float-actions {
  opacity: 1;
  transform: translateY(0);
}
.card-float-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  font-size: 0.85rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  backdrop-filter: blur(6px);
}
.wishlist-btn {
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  border: 1px solid rgba(255, 255, 255, 0.1);
}
.wishlist-btn.wishlisted {
  background: rgba(239, 68, 68, 0.8);
  border-color: transparent;
}
.wishlist-btn:hover {
  background: rgba(239, 68, 68, 0.9);
  border-color: transparent;
}

/* Stars */
.game-card-stars {
  display: flex;
  align-items: center;
  gap: 3px;
  margin-top: auto;
}
.star-icon {
  font-size: 0.85rem;
  line-height: 1;
}
.star-icon.full {
  color: #f59e0b;
}
.star-icon.half {
  color: #f59e0b;
  opacity: 0.7;
}
.star-icon.empty {
  color: rgba(255, 255, 255, 0.15);
}
.rating-label {
  font-size: 0.68rem;
  color: var(--text-muted);
  margin-left: 5px;
}

/* Price row */
.game-card-price-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 2px;
  padding-top: 10px;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}
.price-current {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--text-primary);
}
.game-source-pill {
  margin-left: auto;
  font-size: 0.62rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--text-secondary);
  opacity: 0.7;
}

/* ── Error ────────────────────────────────────────── */
.ftg-error,
.ftg-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-height: 300px;
  gap: 12px;
  color: var(--text-muted) !important;
}
.ftg-error svg,
.ftg-empty img {
  opacity: 0.4;
}
.ftg-error h3,
.ftg-empty h3 {
  color: var(--text-primary) !important;
  font-size: 1.2rem;
  margin: 0;
}
.ftg-error p,
.ftg-empty p {
  color: var(--text-muted) !important;
  font-size: 0.88rem;
  margin: 0;
}

/* Primary action button */
.ftg-primary-btn {
  margin-top: 8px;
  padding: 10px 24px;
  border-radius: 30px;
  border: none;
  background: var(--gradient-primary);
  color: #fff !important;
  font-size: 0.88rem;
  font-weight: 700;
  font-family: var(--font-family);
  cursor: pointer;
  transition: opacity 0.2s;
}
.ftg-primary-btn:hover {
  opacity: 0.85;
}

/* ── Pagination ───────────────────────────────────── */
.ftg-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 32px 0 8px;
  flex-wrap: wrap;
}
.ftg-page-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  border-radius: 8px;
  border: 1px solid var(--border-glass);
  background: var(--bg-surface);
  color: var(--text-secondary) !important;
  font-size: 0.83rem;
  font-weight: 600;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all 0.2s;
}
.ftg-page-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.ftg-page-btn:not(:disabled):hover {
  border-color: rgba(16, 185, 129, 0.4);
  color: #6ee7b7 !important;
}
.ftg-page-numbers {
  display: flex;
  align-items: center;
  gap: 4px;
}
.ftg-page-num-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid var(--border-glass);
  background: var(--bg-surface);
  color: var(--text-secondary) !important;
  font-size: 0.83rem;
  font-weight: 600;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all 0.18s;
}
.ftg-page-num-btn:hover {
  border-color: rgba(16, 185, 129, 0.35);
  color: #6ee7b7 !important;
}
.ftg-page-num-btn.active {
  background: linear-gradient(135deg, #059669, #10b981);
  border-color: transparent;
  color: #fff !important;
  box-shadow: 0 2px 12px rgba(16, 185, 129, 0.4);
}
.ftg-page-ellipsis {
  color: var(--text-muted) !important;
  padding: 0 4px;
  font-size: 0.88rem;
}
.ftg-page-info {
  text-align: center;
  font-size: 0.78rem;
  color: var(--text-muted) !important;
  margin: 8px 0 0;
}

.ftg-star.empty {
  color: var(--border-glass);
}
.ftg-rating-label {
  font-size: 0.65rem;
  color: var(--text-muted);
  margin-left: 4px;
  white-space: nowrap;
}

/* ── List view additions ── */
.games-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding-top: 8px;
}
.game-list-row {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  padding: 12px 16px;
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.2s;
}
.game-list-row:hover {
  border-color: rgba(16, 185, 129, 0.35);
  background: var(--bg-glass-hover);
  transform: translateX(4px);
  color: var(--text-primary);
}
.glr-thumb-wrap {
  position: relative;
  flex-shrink: 0;
}
.glr-thumb {
  width: 100px;
  height: 60px;
  object-fit: cover;
  border-radius: 8px;
  display: block;
}
.glr-info {
  flex: 1;
  min-width: 0;
}
.glr-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 5px;
}
.glr-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 5px;
}
.game-genre-tag {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(255, 255, 255, 0.08);
  color: var(--text-secondary);
}
.glr-year {
  font-size: 0.72rem;
  color: var(--text-muted);
}
.glr-stars {
  display: flex;
  align-items: center;
  gap: 3px;
}
.star-icon {
  font-size: 0.8rem;
  line-height: 1;
}
.star-icon.full {
  color: #f59e0b;
}
.star-icon.half {
  color: #f59e0b;
  opacity: 0.7;
}
.star-icon.empty {
  color: rgba(255, 255, 255, 0.2);
}
.rating-label {
  font-size: 0.65rem;
  color: #6b7fa8;
  margin-left: 4px;
  white-space: nowrap;
}
.glr-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  flex-shrink: 0;
}
.glr-price {
  display: flex;
  align-items: center;
  gap: 6px;
}
.price-free {
  font-size: 0.88rem;
  font-weight: 700;
  color: #34d399;
}
.glr-actions {
  display: flex;
  gap: 6px;
}
.glr-btn {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.glr-btn.wishlist {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-muted);
  border: 1px solid var(--border-glass);
}
.glr-btn.wishlist:hover,
.glr-btn.wishlist.active {
  color: #f43f5e;
  border-color: #f43f5e;
  background: rgba(244, 63, 94, 0.12);
}

/* View toggle */
.view-toggle {
  display: flex;
  border: 1px solid var(--border-glass);
  border-radius: 8px;
  overflow: hidden;
}
.view-btn {
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--text-muted);
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}
.view-btn.active {
  background: rgba(16, 185, 129, 0.3);
  color: #34d399;
}
.view-btn:hover:not(.active) {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-secondary);
}
</style>
