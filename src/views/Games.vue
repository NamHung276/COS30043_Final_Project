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
      this.fetchGames();
    },
    selectedPlatform() {
      this.currentPage = 1;
      this.fetchGames();
    },
    sortBy() {
      this.currentPage = 1;
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

    async addToWishlist(game, e) {
      e.preventDefault();
      e.stopPropagation();
      if (!this.currentUser) {
        this.toast?.show("Please log in to add to wishlist", "warning");
        this.$router.push("/login");
        return;
      }
      const gameId = String(game.id ?? game.gameId);
      if (this.wishlistedIds.has(gameId)) {
        this.toast?.show("Already in your wishlist!", "info");
        return;
      }
      const wishlistStore = useWishlistStore();
      await wishlistStore.addToWishlist(game, this.toast);
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
      this.error = null;
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

      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

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
              <img :src="g.background_image || g.thumbnail || '/placeholder.png'" :alt="g.name" class="gd-rec-img" />
            </div>
            <div class="gd-rec-info p-3">
              <h6 class="gd-rec-title fw-bold mb-1 text-truncate" :title="g.name">{{ g.name }}</h6>
              <div class="d-flex justify-content-between align-items-center mt-2">
                <span class="gd-rec-genre text-muted small text-truncate" style="max-width: 60%">{{ g.genres?.[0]?.name || 'Game' }}</span>
                <span class="gd-rec-price fw-bold text-success small" v-if="gamePrice(g)">${{ gamePrice(g) }}</span>
              </div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- ══ GRID VIEW ══ -->
      <div v-if="viewMode === 'grid'" class="games-grid">
        <router-link
          v-for="(game, index) in paginatedGames"
          :key="game.itemType + game.id"
          :to="
            game.itemType === 'f2p'
              ? `/free-to-play/${game.id}`
              : `/games/${game.id}`
          "
          class="game-card stagger-item"
          :style="{ animationDelay: `${(index % 24) * 0.04}s` }"
          :aria-label="`View details for ${game.name}`"
        >
          <!-- Cover Image -->
          <div class="game-card-img-wrap">
            <img
              v-if="game.background_image"
              v-lazy-img="game.background_image"
              class="game-card-img"
              :alt="`${game.name} cover art`"
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

            <!-- Floating action buttons -->
            <div class="card-float-actions">
              <!-- Trailer button -->
              <button
                v-if="hasTrailer(game)"
                class="card-float-btn trailer-btn"
                @click="openTrailer(game, $event)"
                title="Watch Trailer"
                aria-label="Watch trailer"
              >
                ▶ Trailer
              </button>
              <!-- Wishlist button -->
              <button
                class="card-float-btn wishlist-btn"
                :class="{ wishlisted: wishlistedIds.has(String(game.id)) }"
                @click="addToWishlist(game, $event)"
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
            <div class="genre-ribbon" v-if="game.genres?.length">
              {{ game.genres[0].name }}
            </div>

            <!-- Metacritic badge -->
            <span
              v-if="game.metacritic"
              class="mc-badge"
              :class="metacriticClass(game.metacritic)"
              :title="`Metacritic: ${game.metacritic}`"
            >
              {{ game.metacritic }}
            </span>

            <!-- Platform icons -->
            <div
              class="game-card-platforms"
              v-if="platformIcons(game.platforms).length"
            >
              <span
                v-for="p in platformIcons(game.platforms).slice(0, 4)"
                :key="p.key"
                class="platform-icon"
                :title="p.label"
              >
                <img
                  v-if="p.key === 'pc'"
                  src="/game_logo/pc.svg"
                  width="13"
                  height="13"
                  alt="PC"
                />
                <img
                  v-else-if="p.key === 'ps'"
                  src="/game_logo/playstation_logo.png"
                  width="13"
                  height="13"
                  alt="PlayStation"
                />
                <img
                  v-else-if="p.key === 'xbox'"
                  src="/game_logo/xbox_logo.png"
                  width="13"
                  height="13"
                  alt="Xbox"
                />
                <img
                  v-else-if="p.key === 'nintendo'"
                  src="/game_logo/nintendo_logo.png"
                  width="13"
                  height="13"
                  alt="Nintendo"
                />
                <img
                  v-else-if="p.key === 'mobile'"
                  src="/game_logo/mobile.svg"
                  width="13"
                  height="13"
                  alt="Mobile"
                />
              </span>
              <span v-if="platformIcons(game.platforms).length > 4" class="platform-icon-more" style="font-size: 0.65rem; color: var(--text-muted); font-weight: bold; margin-left: 2px;">
                +{{ platformIcons(game.platforms).length - 4 }}
              </span>
            </div>
          </div>

          <!-- Card Body -->
          <div class="game-card-body">
            <div class="game-card-header">
              <h3 class="game-card-title">{{ game.name }}</h3>
              <span v-if="game.itemType === 'f2p'" class="game-type free"
                >FREE</span
              >
              <span v-else class="game-type premium">PREMIUM</span>
            </div>

            <!-- Genre tags -->
            <div class="game-card-genres" v-if="(game.genres || []).length">
              <span
                v-for="genre in (game.genres || []).slice(0, 2)"
                :key="genre.id"
                class="game-genre-tag text-muted"
                style="background: transparent; border: 1px solid var(--border-glass);"
              >
                {{ genre.name }}
              </span>
              <span v-if="(game.genres || []).length > 2" class="game-genre-tag text-muted" style="background: transparent; border: 1px solid var(--border-glass);">
                +{{ game.genres.length - 2 }}
              </span>
            </div>
            <!-- Star Rating -->
            <div class="game-card-stars" v-if="game.rating">
              <span
                v-for="(star, si) in ratingStars(game.rating)"
                :key="si"
                class="star-icon"
                :class="star"
              >
                {{ star === "full" ? "★" : star === "half" ? "⯨" : "☆" }}
              </span>
              <span class="rating-label">{{ ratingLabel(game.rating) }}</span>
            </div>

            <!-- Price row -->
            <div class="game-card-price-row">
              <!-- Free badge -->
              <template v-if="game.itemType === 'f2p'">
                <span class="price-free">Free to Play</span>
              </template>
              <!-- Discounted -->
              <template v-else-if="gameDiscount(game) > 0">
                <span class="price-discount-badge"
                  >-{{ gameDiscount(game) }}%</span
                >
                <span class="price-original">${{ gamePrice(game) }}</span>
                <span class="price-current">${{ discountedPrice(game) }}</span>
              </template>
              <!-- Full price -->
              <template v-else-if="gamePrice(game)">
                <span class="price-current">${{ gamePrice(game) }}</span>
              </template>

              <span class="game-source-pill">{{
                game.itemType === "f2p" ? "FreeToGame" : "RAWG"
              }}</span>
            </div>
          </div>
        </router-link>
      </div>

      <!-- ══ LIST VIEW ══ -->
      <div v-else class="games-list">
        <router-link
          v-for="(game, index) in paginatedGames"
          :key="game.itemType + game.id"
          :to="
            game.itemType === 'f2p'
              ? `/free-to-play/${game.id}`
              : `/games/${game.id}`
          "
          class="game-list-row stagger-item"
          :style="{ animationDelay: `${(index % 24) * 0.03}s` }"
        >
          <div class="glr-thumb-wrap">
            <img
              v-if="game.background_image"
              v-lazy-img="game.background_image"
              :alt="game.name"
              class="glr-thumb"
            />
            <div v-else class="glr-thumb-placeholder"></div>
            <span
              v-if="game.metacritic"
              class="glr-mc"
              :class="metacriticClass(game.metacritic)"
              >{{ game.metacritic }}</span
            >
          </div>
          <div class="glr-info">
            <div class="glr-title">{{ game.name }}</div>
            <div class="glr-meta">
              <span
                v-for="g in (game.genres || []).slice(0, 2)"
                :key="g.id"
                class="game-genre-tag text-muted"
                style="background: transparent; border: 1px solid var(--border-glass);"
                >{{ g.name }}</span
              >
              <span v-if="(game.genres || []).length > 2" class="game-genre-tag text-muted" style="background: transparent; border: 1px solid var(--border-glass);">
                +{{ game.genres.length - 2 }}
              </span>
              <span v-if="game.released" class="glr-year">{{
                game.released.split("-")[0]
              }}</span>
            </div>
            <div class="glr-stars" v-if="game.rating">
              <span
                v-for="(s, si) in ratingStars(game.rating)"
                :key="si"
                class="star-icon"
                :class="s"
              >
                {{ s === "full" ? "★" : s === "half" ? "⯨" : "☆" }}
              </span>
              <span class="rating-label">{{ game.rating.toFixed(1) }}</span>
            </div>
          </div>
          <div class="glr-right">
            <div class="glr-price">
              <template v-if="game.itemType === 'f2p'"
                ><span class="price-free">Free</span></template
              >
              <template v-else-if="gameDiscount(game) > 0">
                <span class="price-discount-badge"
                  >-{{ gameDiscount(game) }}%</span
                >
                <span class="price-current">${{ discountedPrice(game) }}</span>
              </template>
              <template v-else-if="gamePrice(game)"
                ><span class="price-current"
                  >${{ gamePrice(game) }}</span
                ></template
              >
            </div>
            <div class="glr-actions">
              <button
                v-if="hasTrailer(game)"
                class="glr-btn trailer"
                @click="openTrailer(game, $event)"
                aria-label="Watch trailer"
              >
                ▶
              </button>
              <button
                class="glr-btn wishlist"
                :class="{ active: wishlistedIds.has(String(game.id)) }"
                @click="addToWishlist(game, $event)"
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


