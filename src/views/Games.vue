<script>
import SkeletonCard from "../components/SkeletonCard.vue";
import TrailerModal from "../components/TrailerModal.vue";
import { inject } from "vue";
import { backendApi } from "../services/api";
import { mapState } from "pinia";
import { useAuthStore } from "../stores/useAuthStore";
import { useWishlistStore } from "../stores/useWishlistStore";
import {
  metacriticClass,
  ratingStars,
  ratingLabel,
  platformIcons,
  gamePrice,
  gameDiscount,
  discountedPrice,
} from "../composables/useGameUtils";

// RAWG parent_platform IDs
const PLATFORMS = [
  { key: "all", label: "All Platforms", icon: null, id: null },
  { key: "pc", label: "PC", icon: "/game_logo/pc.svg", id: 1 },
  { key: "ps", label: "PlayStation", icon: "/game_logo/playstation_logo.png", id: 2 },
  { key: "xbox", label: "Xbox", icon: "/game_logo/xbox_logo.png", id: 3 },
  { key: "nintendo", label: "Nintendo", icon: "/game_logo/nintendo_logo.png", id: 7 },
  { key: "mobile", label: "Mobile", icon: "/game_logo/mobile.svg", id: "4,8" },
];

const ALL_GENRES = [
  "All", "Action", "Adventure", "Anime", "Arcade", "Battle Royale", "Card",
  "Casual", "Fantasy", "Fighting", "Horror", "Indie", "MMORPG", "MOBA",
  "Platformer", "Puzzle", "Racing", "RPG", "Sci-Fi", "Shooter", "Simulation",
  "Sports", "Strategy", "Survival",
];

export default {
  components: { SkeletonCard, TrailerModal },

  setup() {
    const toast = inject("toast");
    // Expose shared utility functions to the template
    return {
      toast,
      metacriticClass,
      ratingStars,
      ratingLabel,
      platformIcons,
      gamePrice,
      gameDiscount,
      discountedPrice,
    };
  },

  data() {
    return {
      games: [],
      loading: true,
      loadTimedOut: false,
      loadingTimer: null,
      error: null,
      searchTerm: "",
      selectedGenre: "All",
      selectedPlatform: "all",
      sortBy: "rating",
      viewMode: "grid",
      genres: ALL_GENRES,
      platforms: PLATFORMS,
      currentPage: 1,
      itemsPerPage: 24,
      totalCount: 0,
      searchTimeout: null,
      filterTimeout: null,
      // Trailer modal
      trailerGame: null,
      showTrailer: false,
      // Recommendations (auth-gated)
      recommendedGames: [],
      loadingRecommendations: false,
    };
  },

  computed: {
    // Auth & wishlist state from centralised stores
    ...mapState(useAuthStore, ["currentUser"]),
    ...mapState(useWishlistStore, ["wishlistedIds"]),

    sortedGames() {
      const list = [...this.games];
      if (this.sortBy === "rating") list.sort((a, b) => (b.rating || 0) - (a.rating || 0));
      else if (this.sortBy === "metacritic") list.sort((a, b) => (b.metacritic || 0) - (a.metacritic || 0));
      else if (this.sortBy === "release") list.sort((a, b) => new Date(b.released || 0) - new Date(a.released || 0));
      else if (this.sortBy === "az") list.sort((a, b) => (a.name || "").localeCompare(b.name || ""));
      return list;
    },

    filteredGames() {
      return this.sortedGames;
    },

    totalPages() {
      return Math.ceil(this.filteredGames.length / this.itemsPerPage);
    },

    paginatedGames() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      return this.filteredGames.slice(start, start + this.itemsPerPage);
    },

    visiblePages() {
      const pages = [];
      if (this.totalPages <= 7) {
        for (let i = 1; i <= this.totalPages; i++) pages.push(i);
      } else {
        pages.push(1);
        if (this.currentPage > 4) pages.push("...");
        const start = Math.max(2, this.currentPage - 1);
        const end = Math.min(this.totalPages - 1, this.currentPage + 1);
        for (let i = start; i <= end; i++) pages.push(i);
        if (this.currentPage < this.totalPages - 3) pages.push("...");
        pages.push(this.totalPages);
      }
      return pages;
    },

    activePlatform() {
      return this.platforms.find((p) => p.key === this.selectedPlatform);
    },
  },

  watch: {
    "$route.query.genre": {
      immediate: true,
      handler(newVal) {
        if (newVal) this.selectedGenre = newVal;
      },
    },
    "$route.query.search": {
      immediate: true,
      handler(newVal) {
        if (newVal !== undefined && newVal !== this.searchTerm) {
          this.searchTerm = newVal || "";
        }
      },
    },
    searchTerm() {
      this.currentPage = 1;
      clearTimeout(this.searchTimeout);
      this.searchTimeout = setTimeout(() => {
        this.fetchGames();
      }, 400);
    },
    selectedGenre() {
      this.currentPage = 1;
      clearTimeout(this.filterTimeout);
      this.filterTimeout = setTimeout(() => {
        this.fetchGames();
      }, 200);
    },
    selectedPlatform() {
      this.currentPage = 1;
      clearTimeout(this.filterTimeout);
      this.filterTimeout = setTimeout(() => {
        this.fetchGames();
      }, 200);
    },
    sortBy() {
      this.currentPage = 1;
      clearTimeout(this.filterTimeout);
      this.filterTimeout = setTimeout(() => {
        this.fetchGames();
      }, 200);
    },
    // React to auth state changes via the centralised store
    currentUser: {
      immediate: true,
      async handler(user) {
        if (user) {
          await this.fetchRecommendations();
        } else {
          this.recommendedGames = [];
        }
      },
    },
  },

  methods: {
    openTrailer(game, e) {
      e.preventDefault();
      e.stopPropagation();
      this.trailerGame = game;
      this.showTrailer = true;
    },

    closeTrailer() {
      this.showTrailer = false;
      this.trailerGame = null;
    },

    trailerYoutubeId(game) {
      if (game.clip?.video) {
        const m = game.clip.video.match(
          /(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=))([\w-]{11})/,
        );
        if (m) return m[1];
      }
      return null;
    },

    trailerVideoUrl(game) {
      return game.clip?.clips?.full || game.clip?.clip || null;
    },

    hasTrailer(game) {
      return !!(this.trailerYoutubeId(game) || this.trailerVideoUrl(game));
    },

    async toggleWishlist(game, e) {
      e.preventDefault();
      e.stopPropagation();
      if (!this.currentUser) {
        this.toast?.show("Please log in to add to wishlist", "warning");
        this.$router.push("/login");
        return;
      }
      const wishlistStore = useWishlistStore();
      await wishlistStore.toggleWishlist(game, this.toast);
    },

    selectPlatform(key) {
      this.selectedPlatform = key;
    },

    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    },

    async fetchGames() {
      this.loading = true;
      this.loadTimedOut = false;
      this.error = null;

      // Hard timeout: stop skeleton and show retry after 20s
      if (this.loadingTimer) clearTimeout(this.loadingTimer);
      this.loadingTimer = setTimeout(() => {
        if (this.loading) {
          this.loading = false;
          this.loadTimedOut = true;
          this.error = "Games are taking too long to load. Please check your connection and try again.";
        }
      }, 20_000);

      try {
        const params = {
          page_size: 40,
          ordering: this.searchTerm ? "-rating" : "-metacritic",
          exclude_additions: true,
          metacritic: "30,100",
          ratings_count: 3,
        };

        if (this.searchTerm) params.search = this.searchTerm;

        const plat = this.platforms.find((p) => p.key === this.selectedPlatform);
        if (plat && plat.id !== null) {
          params.parent_platforms = plat.id;
        }

        let ftgParams = { "sort-by": "popularity" };
        if (plat && plat.key === "pc") ftgParams.platform = "pc";
        if (plat && plat.key === "mobile") ftgParams.platform = "browser";

        if (this.selectedGenre !== "All") {
          ftgParams.category = this.selectedGenre.toLowerCase().replace(" ", "-");

          const rawgGenreMap = {
            Shooter: "shooter", Strategy: "strategy", Racing: "racing",
            Sports: "sports", Action: "action", RPG: "role-playing-games-rpg",
            Adventure: "adventure", Simulation: "simulation", Puzzle: "puzzle",
            Arcade: "arcade", Platformer: "platformer", Fighting: "fighting",
            MMORPG: "massively-multiplayer", Indie: "indie", Casual: "casual", Card: "card",
          };
          const rawgTagMap = {
            Anime: "anime", "Battle Royale": "battle-royale", MOBA: "moba",
            Survival: "survival", Fantasy: "fantasy", "Sci-Fi": "sci-fi", Horror: "horror",
          };

          if (rawgGenreMap[this.selectedGenre]) {
            params.genres = rawgGenreMap[this.selectedGenre];
          } else if (rawgTagMap[this.selectedGenre]) {
            params.tags = rawgTagMap[this.selectedGenre];
          }
        }

        const rawgReq = backendApi
          .get("/games", { params })
          .catch(() => ({ data: { results: [], count: 0 } }));
        const ftgReq = backendApi
          .get("/free-games", { params: ftgParams })
          .catch(() => ({ data: { results: [] } }));

        const [rawgRes, ftgRes] = await Promise.all([rawgReq, ftgReq]);

        let rawgList = (rawgRes.data.results || []).map((g) => ({
          ...g,
          itemType: "rawg",
        }));

        let ftgList = (ftgRes.data?.results || []).map((g) => ({
          ...g,
          itemType: "f2p",
          name: g.title,
          background_image: g.thumbnail,
          genres: [{ name: g.genre }],
          platforms: [{ platform: { id: 4, name: "PC", slug: "pc" } }],
          metacritic: null,
          rating: 0,
        }));

        if (this.searchTerm) {
          const lowerSearch = this.searchTerm.toLowerCase();
          ftgList = ftgList.filter((g) =>
            g.name.toLowerCase().includes(lowerSearch),
          );
        }

        // Interleave: 2 premium for every 1 free
        let combined = [];
        let rIdx = 0, fIdx = 0;
        while (rIdx < rawgList.length || fIdx < ftgList.length) {
          if (rIdx < rawgList.length) combined.push(rawgList[rIdx++]);
          if (rIdx < rawgList.length) combined.push(rawgList[rIdx++]);
          if (fIdx < ftgList.length) combined.push(ftgList[fIdx++]);
        }

        this.games = combined;
        this.totalCount = (rawgRes.data.count || 0) + (ftgRes.data?.results?.length || 0);
      } catch (err) {
        console.error(err);
        this.error = "Failed to load games. Please try again.";
      } finally {
        clearTimeout(this.loadingTimer);
        this.loading = false;
      }
    },

    async fetchRecommendations() {
      if (!this.currentUser) return;
      this.loadingRecommendations = true;
      try {
        const res = await backendApi.get("/games/recommendations", {
          params: { user_id: this.currentUser.uid },
        });
        if (res.data?.results) {
          this.recommendedGames = res.data.results.map((g) => ({
            ...g,
            itemType: "rawg",
          }));
        }
      } catch (error) {
        console.error("Failed to load recommendations", error);
      } finally {
        this.loadingRecommendations = false;
      }
    },
  },

  beforeUnmount() {
    clearTimeout(this.searchTimeout);
    clearTimeout(this.loadingTimer);
  },

  async mounted() {
    await this.fetchGames();
  },
};
</script>


<template>
  <div class="games-page">
    <!-- Trailer Modal -->
    <TrailerModal
      :show="showTrailer"
      :youtube-id="trailerGame ? trailerYoutubeId(trailerGame) : null"
      :video-url="trailerGame ? trailerVideoUrl(trailerGame) : null"
      :poster-url="trailerGame?.background_image"
      :title="trailerGame?.name"
      @close="closeTrailer"
    />

    <!-- Page Header -->
    <div class="games-page-header">
      <div class="games-page-header-bg" aria-hidden="true"></div>
      <div class="container games-header-content">
        <div class="games-title-row">
          <span class="games-title-icon" aria-hidden="true">
            <img
              src="/logo/gamepad.svg"
              width="28"
              height="28"
              alt=""
              aria-hidden="true"
            />
          </span>
          <div>
            <h1 class="games-title">All Games</h1>
            <p class="games-subtitle">
              Premium &amp; Free-To-Play &nbsp;&middot;&nbsp;
              <strong>{{ totalCount.toLocaleString() }}</strong> titles
            </p>
          </div>
        </div>

        <!-- Search & Genre Filter -->
        <div class="games-filters">
          <div class="games-search-wrap">
            <img
              src="/logo/search.svg"
              class="games-search-icon"
              width="17"
              height="17"
              alt=""
              aria-hidden="true"
            />
            <input
              type="text"
              class="games-search-input"
              placeholder="Search games..."
              aria-label="Search games"
              v-model="searchTerm"
            />
          </div>
          <select
            class="games-genre-select"
            aria-label="Filter by genre"
            v-model="selectedGenre"
          >
            <option v-for="genre in genres" :key="genre" :value="genre">
              {{ genre }}
            </option>
          </select>
          <select
            class="games-genre-select"
            aria-label="Sort games"
            v-model="sortBy"
          >
            <option value="rating">Sort: Top Rated</option>
            <option value="metacritic">Sort: Metacritic</option>
            <option value="release">Sort: Latest Release</option>
            <option value="az">Sort: A–Z</option>
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
        </div>

        <!-- Platform Filter Tabs -->
        <div class="platform-tabs">
          <button
            v-for="plat in platforms"
            :key="plat.key"
            class="platform-tab"
            :class="{ active: selectedPlatform === plat.key }"
            @click="selectPlatform(plat.key)"
            :aria-pressed="selectedPlatform === plat.key"
          >
            <img
              v-if="plat.icon"
              :src="plat.icon"
              width="18"
              height="18"
              :alt="plat.label"
              class="platform-tab-icon"
            />
            <span>{{ plat.label }}</span>
          </button>
        </div>
      </div>
    </div>

    <div class="container pb-5">
      <!-- Skeleton -->
      <div v-if="loading" class="games-grid">
        <SkeletonCard v-for="n in 12" :key="n" />
      </div>

      <div v-else-if="error" class="games-empty-state py-5">
        <svg width="56" height="56" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="opacity:0.5; color: var(--accent-coral);" aria-hidden="true">
          <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>
        </svg>
        <h3 class="mt-3">Could not load games</h3>
        <p class="text-muted mb-4">{{ error }}</p>
        <button class="btn btn-primary px-4 py-2 rounded-pill" @click="fetchGames">
          <i class="bi bi-arrow-clockwise me-2"></i>Try Again
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredGames.length === 0" class="games-empty-state">
        <img
          src="/logo/search.svg"
          width="60"
          height="60"
          alt=""
          aria-hidden="true"
          style="opacity: 0.4"
        />
        <h3>No games found</h3>
        <p>Try adjusting your search term, genre, or platform filter.</p>
      </div>

      <template v-else>
        <!-- Recommended for You -->
        <div v-if="recommendedGames.length > 0 && !searchTerm && selectedGenre === 'All' && selectedPlatform === 'all'" class="mb-5">
        <h2 class="gd-section-title mb-4">
          <i class="bi bi-stars text-warning me-2"></i> Recommended by our community
        </h2>
        <div class="gd-recommendation-carousel pb-3">
          <router-link
            v-for="g in recommendedGames.slice(0, 8)"
            :key="'rec-' + g.id"
            :to="`/games/${g.id}`"
            class="gd-rec-card text-decoration-none"
          >
            <div class="gd-rec-img-wrapper">
              >
                ▶
              </button>
              <button
                class="glr-btn wishlist"
                :class="{ active: wishlistedIds.has(String(game.id)) }"
                @click="toggleWishlist(game, $event)"
                :aria-label="
                  wishlistedIds.has(String(game.id)) ? 'In Wishlist' : 'Wishlist'
                "
              >
                {{ wishlistedIds.has(String(game.id)) ? "♥" : "♡" }}
              </button>
            </div>
          </div>
        </router-link>
      </div>
      </template>

      <!-- Pagination -->
      <nav
        v-if="!loading && totalPages > 1"
        class="games-pagination"
        aria-label="Games pagination"
      >
        <button
          class="page-btn"
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
        <div class="page-numbers">
          <template v-for="(page, index) in visiblePages" :key="index">
            <span v-if="page === '...'" class="page-ellipsis">&#8230;</span>
            <button
              v-else
              class="page-num-btn"
              :class="{ active: currentPage === page }"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
          </template>
        </div>
        <button
          class="page-btn"
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

      <p v-if="!loading" class="games-page-info">
        Page {{ currentPage }} of {{ totalPages }} &middot;
        {{ filteredGames.length }} {{ filteredGames.length === 1 ? 'game' : 'games' }} shown
      </p>
    </div>
  </div>
</template>

<style scoped>
/* ── Pagination ── */
.games-pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 2rem;
  padding: 1rem;
  background: var(--bg-surface);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
}
.page-btn {
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
.page-btn:hover:not(:disabled) {
  background: rgba(255,255,255,0.05);
}
.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.page-numbers {
  display: flex;
  gap: 6px;
}
.page-num-btn {
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
.page-num-btn:hover:not(.active) {
  background: rgba(255,255,255,0.05);
}
.page-num-btn.active {
  background: var(--accent);
  color: #fff;
  box-shadow: 0 4px 12px rgba(109, 40, 217, 0.4);
}
.page-ellipsis {
  color: var(--text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
}
.games-page-info {
  text-align: center;
  margin-top: 1rem;
  color: var(--text-muted);
  font-size: 0.9rem;
}
</style>
