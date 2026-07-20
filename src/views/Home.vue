<script>
import { inject } from "vue";
import { rawgApi, freeToGameApi, cheapSharkApi } from "../services/api";
import { Sparkles, CalendarDays, Flame } from "@lucide/vue";

const GENRES = [
  {
    label: "MMORPG",
    icon: "/game_icon/mmorpg.png",
    color: "violet",
    cat: "mmorpg",
    link: "/games?genre=MMORPG",
  },
  {
    label: "Shooter",
    icon: "/game_icon/shooter.png",
    color: "coral",
    cat: "shooter",
    link: "/games?genre=Shooter",
  },
  {
    label: "Battle Royale",
    icon: "/game_icon/battle_royale.png",
    color: "gold",
    cat: "battle-royale",
    link: "/games?genre=Battle Royale",
  },
  {
    label: "MOBA",
    icon: "/game_icon/moba.png",
    color: "cyan",
    cat: "moba",
    link: "/games?genre=MOBA",
  },
  {
    label: "Strategy",
    icon: "/game_icon/strategy.png",
    color: "green",
    cat: "strategy",
    link: "/games?genre=Strategy",
  },
  {
    label: "Racing",
    icon: "/game_icon/racing.png",
    color: "pink",
    cat: "racing",
    link: "/games?genre=Racing",
  },
  {
    label: "Sports",
    icon: "/game_icon/sports.png",
    color: "cyan",
    cat: "sports",
    link: "/games?genre=Sports",
  },
  {
    label: "Anime",
    icon: "/game_icon/anime.png",
    color: "pink",
    cat: "anime",
    link: "/games?genre=Anime",
  },
  {
    label: "Survival",
    icon: "/game_icon/survival.png",
    color: "green",
    cat: "survival",
    link: "/games?genre=Survival",
  },
  {
    label: "Fantasy",
    icon: "/game_icon/fantasy.png",
    color: "violet",
    cat: "fantasy",
    link: "/games?genre=Fantasy",
  },
  {
    label: "Sci-Fi",
    icon: "/game_icon/sci-fi.png",
    color: "cyan",
    cat: "sci-fi",
    link: "/games?genre=Sci-Fi",
  },
  {
    label: "Horror",
    icon: "/game_icon/horror.png",
    color: "coral",
    cat: "horror",
    link: "/games?genre=Horror",
  },
];

export default {
  components: {
    Sparkles,
    CalendarDays,
    Flame,
  },
  setup() {
    const toast = inject("toast");
    return { toast };
  },

  data() {
    return {
      // Featured carousel (FreeToGame)
      featuredGames: [],
      activeIndex: 0,
      autoplayTimer: null,
      isAnimating: false,
      direction: "next",
      detailCache: {},

      // New Releases strip (RAWG)
      newReleases: [],
      comingSoon: [],

      trendingFree: [],

      // Tabbed section
      activeTab: "newReleases", // 'newReleases', 'comingSoon', 'trendingFree'
      hoveredGame: null,

      // Loading states
      carouselLoading: true,
      releasesLoading: true,
      comingSoonLoading: true,
      trendingFreeLoading: true,

      // Stats counter
      statsVisible: false,
      statsObserver: null,

      // Genres
      genres: GENRES,

      // Hot Deals (CheapShark)
      hotDeals: [],
      dealsLoading: true,

      // Carousel autoplay paused by user (WCAG 2.2.2)
      isAutopaused: false,
    };
  },

  computed: {
    currentGame() {
      return this.featuredGames[this.activeIndex] || null;
    },
    currentDetail() {
      if (!this.currentGame) return null;
      return this.detailCache[this.currentGame.itemType + this.currentGame.id];
    },
    screenshots() {
      if (
        this.currentGame?.itemType === "f2p" &&
        this.currentDetail?.screenshots?.length
      ) {
        return this.currentDetail.screenshots.slice(0, 4).map((s) => s.image);
      } else if (
        this.currentGame?.itemType === "rawg" &&
        this.currentGame.short_screenshots?.length
      ) {
        return this.currentGame.short_screenshots
          .slice(1, 5)
          .map((s) => s.image);
      }
      return this.currentGame
        ? Array(4).fill(this.currentGame.displayThumb)
        : [];
    },
    shortDesc() {
      if (this.currentGame?.itemType === "f2p") {
        return (
          this.currentDetail?.short_description ||
          `A free-to-play ${this.currentGame.displayGenre || ""} experience you won't want to miss.`
        );
      } else {
        const desc =
          this.currentDetail?.description_raw ||
          `An amazing ${this.currentGame?.displayGenre || ""} game you shouldn't miss.`;
        if (desc.length <= 150) return desc;
        return desc.substring(0, 150).split(" ").slice(0, -1).join(" ") + "...";
      }
    },
    activeTabGames() {
      if (this.activeTab === "newReleases")
        return this.newReleases.slice(0, 10);
      if (this.activeTab === "comingSoon") return this.comingSoon.slice(0, 10);
      if (this.activeTab === "trendingFree")
        return this.trendingFree.slice(0, 10);
      return [];
    },
  },

  watch: {
    activeIndex(newIdx) {
      const game = this.featuredGames[newIdx];
      if (game) {
        this.fetchDetail(game);
      }
    },
  },

  async mounted() {
    // Load featured carousel + new releases in parallel
    await Promise.allSettled([
      this.loadFeatured(),
      this.loadNewReleases(),
      this.loadComingSoon(),
      this.loadHotDeals(),
    ]);

    // Setup stats intersection observer
    this.$nextTick(() => {
      const statsEl = document.getElementById("stats-section");
      if (statsEl && "IntersectionObserver" in window) {
        this.statsObserver = new IntersectionObserver(
          ([entry]) => {
            if (entry.isIntersecting) {
              this.statsVisible = true;
              this.statsObserver.disconnect();
            }
          },
          { threshold: 0.3 },
        );
        this.statsObserver.observe(statsEl);
      }
    });
  },

  beforeUnmount() {
    this.stopAutoplay();
    if (this.statsObserver) this.statsObserver.disconnect();
  },

  methods: {
    async loadFeatured() {
      try {
        const f2pReq = freeToGameApi
          .get("/games", { params: { "sort-by": "popularity" } })
          .catch(() => ({ data: [] }));
        const rawgReq = rawgApi
          .get("/games", { params: { ordering: "-added", page_size: 20 } })
          .catch(() => ({ data: { results: [] } }));

        const [f2pRes, rawgRes] = await Promise.all([f2pReq, rawgReq]);

        const f2pGames = (f2pRes.data || [])
          .sort(() => 0.5 - Math.random())
          .slice(0, 5)
          .map((g) => ({
            ...g,
            itemType: "f2p",
            displayTitle: g.title,
            displayThumb: g.thumbnail,
            displayGenre: g.genre,
            displayLink: "/free-to-play/" + g.id,
          }));

        const rawgGames = (rawgRes.data.results || [])
          .sort(() => 0.5 - Math.random())
          .slice(0, 5)
          .map((g) => ({
            ...g,
            itemType: "rawg",
            displayTitle: g.name,
            displayThumb: g.background_image,
            displayGenre: g.genres?.[0]?.name || "Action",
            displayLink: "/games/" + g.id,
          }));

        this.featuredGames = [...f2pGames, ...rawgGames].sort(
          () => 0.5 - Math.random(),
        );

        // Populate trendingFree for the tabbed section
        this.trendingFree = (f2pRes.data || []).slice(0, 10).map((g) => ({
          ...g,
          itemType: "f2p",
          name: g.title,
          background_image: g.thumbnail,
          genres: [{ name: g.genre }],
          id: g.id,
        }));

        if (this.featuredGames.length) {
          this.fetchDetail(this.featuredGames[0]);
          this.$nextTick(() => this.startAutoplay());
        }
      } catch (e) {
        console.error(e);
        this.toast?.show("Could not load featured games right now.", "error");
      } finally {
        this.carouselLoading = false;
        this.trendingFreeLoading = false;
      }
    },

    async loadNewReleases() {
      try {
        const today = new Date().toISOString().split("T")[0];
        const past = new Date();
        past.setDate(past.getDate() - 90);
        const pastStr = past.toISOString().split("T")[0];

        const { data } = await rawgApi.get("/games", {
          params: {
            ordering: "-released",
            page_size: 20,
            dates: `${pastStr},${today}`,
          },
        });
        this.newReleases = data.results || [];
      } catch (e) {
        console.error(e);
        this.toast?.show("Could not load new releases right now.", "error");
      } finally {
        this.releasesLoading = false;
      }
    },

    async loadComingSoon() {
      try {
        const today = new Date().toISOString().split("T")[0];
        const future = new Date();
        future.setFullYear(future.getFullYear() + 1);
        const futureStr = future.toISOString().split("T")[0];

        const { data } = await rawgApi.get("/games", {
          params: {
            ordering: "-added",
            page_size: 20,
            dates: `${today},${futureStr}`,
          },
        });
        this.comingSoon = data.results || [];
      } catch (e) {
        console.error(e);
        this.toast?.show("Could not load upcoming games right now.", "error");
      } finally {
        this.comingSoonLoading = false;
      }
    },

    async loadHotDeals() {
      try {
        const { data } = await cheapSharkApi.get("/deals", {
          params: {
            sortBy: "DealRating",
            pageSize: 12,
            onSale: 1,
            upperPrice: 30,
          },
        });
        const uniqueDeals = [];
        const seenTitles = new Set();
        for (const deal of data || []) {
          const key = deal.title.trim().toLowerCase();
          if (!seenTitles.has(key)) {
            uniqueDeals.push(deal);
            seenTitles.add(key);
          }
        }
        this.hotDeals = uniqueDeals.slice(0, 8);
      } catch (e) {
        console.error(e);
        this.toast?.show("Could not load special offers right now.", "error");
      } finally {
        this.dealsLoading = false;
      }
    },

    async fetchDetail(game) {
      if (!game) return;
      const cacheKey = game.itemType + game.id;
      if (this.detailCache[cacheKey]) return;
      try {
        if (game.itemType === "f2p") {
          const res = await fetch(
            `https://www.freetogame.com/api/game?id=${game.id}`,
          );
          const data = await res.json();
          this.detailCache = { ...this.detailCache, [cacheKey]: data };
        } else {
          const { data } = await rawgApi.get(`/games/${game.id}`);
          this.detailCache = { ...this.detailCache, [cacheKey]: data };
        }
      } catch {}
    },

    goTo(index, dir = "next") {
      if (this.isAnimating || index === this.activeIndex) return;
      this.direction = dir;
      this.isAnimating = true;
      this.activeIndex = index;
      setTimeout(() => {
        this.isAnimating = false;
      }, 420);
      this.resetAutoplay();
    },
    next() {
      const idx = (this.activeIndex + 1) % this.featuredGames.length;
      this.goTo(idx, "next");
    },
    prev() {
      const idx =
        (this.activeIndex - 1 + this.featuredGames.length) %
        this.featuredGames.length;
      this.goTo(idx, "prev");
    },
    startAutoplay() {
      if (this.isAutopaused) return; // respect user pause
      this.autoplayTimer = setInterval(() => this.next(), 6000);
    },
    stopAutoplay() {
      clearInterval(this.autoplayTimer);
      this.autoplayTimer = null;
    },
    resetAutoplay() {
      this.stopAutoplay();
      this.startAutoplay();
    },
    toggleAutoplay() {
      this.isAutopaused = !this.isAutopaused;
      if (this.isAutopaused) {
        this.stopAutoplay();
      } else {
        this.startAutoplay();
      }
    },

    metacriticClass(score) {
      if (!score) return "mc-grey";
      const n = parseInt(score);
      return n >= 75 ? "mc-green" : n >= 50 ? "mc-yellow" : "mc-red";
    },
    formatDate(value) {
      if (!value) return "—";
      const date = new Date(value);
      if (Number.isNaN(date.getTime())) return value;
      return new Intl.DateTimeFormat("en", {
        month: "short",
        day: "numeric",
        year: "numeric",
      }).format(date);
    },

    setTab(tabName) {
      this.activeTab = tabName;
      this.hoveredGame = null;
    },
    setHoveredGame(game) {
      this.hoveredGame = game;
    },
  },
};
</script>

<template>
  <div>
    <!-- ══════════════════════════════════════
         HERO V2 — Welcome Banner
         ══════════════════════════════════════ -->

    <!-- ══════════════════════════════════════
         HERO V2 — Full-Bleed Carousel
         ══════════════════════════════════════ -->
    <div
      class="steam-hero-fullbleed"
      :key="currentGame?.id"
      :style="{ backgroundImage: `url(${currentGame?.displayThumb || ''})` }"
    >
      <div class="steam-hero-blur-overlay"></div>
      <div class="container py-5" style="position: relative; z-index: 2">
        <div class="hero-heading mb-4">
          <h1 class="hero-title">Find Your Next Favorite Game</h1>

          <p class="hero-subtitle">
            Explore curated games, read community reviews, discover the latest
            gaming news, and find the best deals—all in one place.
          </p>
        </div>

        <!-- Skeleton -->
        <div v-if="carouselLoading" class="steam-carousel-skeleton">
          <div class="scs-main skeleton"></div>
          <div class="scs-side">
            <div
              class="skeleton"
              style="
                height: 28px;
                border-radius: 6px;
                width: 75%;
                margin-bottom: 10px;
              "
            ></div>
            <div
              class="skeleton"
              style="
                height: 14px;
                border-radius: 4px;
                width: 45%;
                margin-bottom: 20px;
              "
            ></div>
            <div class="scs-thumb-grid">
              <div
                v-for="n in 4"
                :key="n"
                class="skeleton scs-thumb-item"
              ></div>
            </div>
            <div style="margin-top: auto; padding-top: 16px">
              <div
                class="skeleton"
                style="height: 44px; border-radius: 8px"
              ></div>
            </div>
          </div>
        </div>

        <!-- Carousel -->
        <div
          v-else-if="featuredGames.length && currentGame"
          class="steam-carousel mb-5"
          @mouseenter="stopAutoplay"
          @mouseleave="!isAutopaused && startAutoplay()"
          role="region"
          aria-label="Featured games carousel"
        >
          <!-- aria-live region: announces slide changes to screen readers (WCAG 1.3.1) -->
          <div aria-live="polite" aria-atomic="true" class="visually-hidden">
            {{
              currentGame
                ? `${activeIndex + 1} of ${featuredGames.length}: ${currentGame.displayTitle}`
                : ""
            }}
          </div>

          <button
            class="steam-arrow steam-arrow-left"
            @click="prev"
            aria-label="Previous game"
          >
            ‹
          </button>

          <div class="steam-main-panel">
            <transition
              :name="direction === 'next' ? 'slide-left' : 'slide-right'"
              mode="out-in"
            >
              <router-link
                :key="currentGame.itemType + currentGame.id"
                :to="currentGame.displayLink"
                class="steam-hero-link"
              >
                <img
                  :src="currentGame.displayThumb"
                  :alt="currentGame.displayTitle"
                  class="steam-hero-img"
                />
                <div class="steam-hero-overlay"></div>
              </router-link>
            </transition>
          </div>

          <transition
            :name="direction === 'next' ? 'fade-up' : 'fade-down'"
            mode="out-in"
          >
            <div
              class="steam-info-panel"
              :key="'info-' + currentGame.itemType + currentGame.id"
            >
              <div class="steam-info-top">
                <h3 class="steam-title">{{ currentGame.displayTitle }}</h3>
                <div class="steam-meta-row">
                  <span class="steam-badge-genre">
                    {{ currentGame.displayGenre }}
                  </span>

                  <span
                    v-if="currentGame.itemType === 'f2p'"
                    class="steam-badge-free"
                  >
                    Free to Play
                  </span>

                  <span v-else class="steam-badge-premium"> Premium </span>

                  <span
                    v-if="currentDetail?.platform"
                    class="steam-badge-platform"
                  >
                    {{ currentDetail.platform }}
                  </span>
                </div>
                <p class="steam-desc">
                  {{ shortDesc }}
                </p>

                <p v-if="currentDetail?.publisher" class="steam-publisher">
                  Published by
                  <strong>{{ currentDetail.publisher }}</strong>
                </p>
              </div>

              <div class="steam-screenshots-grid">
                <template v-if="screenshots.length">
                  <div
                    v-for="(src, i) in screenshots"
                    :key="i"
                    class="steam-screenshot"
                  >
                    <img
                      :src="src"
                      :alt="`${currentGame.displayTitle} screenshot ${i + 1}`"
                    />
                  </div>
                </template>
                <template v-else>
                  <div
                    v-for="n in 4"
                    :key="n"
                    class="steam-screenshot skeleton"
                  ></div>
                </template>
              </div>

              <div class="steam-info-bottom">
                <div
                  class="steam-dev-info"
                  v-if="
                    currentDetail?.developer ||
                    currentDetail?.developers?.length
                  "
                >
                  <span class="steam-dev-label">Developer</span>
                  <span class="steam-dev-value">{{
                    currentDetail?.developer ||
                    currentDetail?.developers[0]?.name
                  }}</span>
                </div>
                <router-link
                  :to="currentGame.displayLink"
                  class="btn steam-play-btn"
                >
                  View Game →
                </router-link>
              </div>
            </div>
          </transition>

          <button
            class="steam-arrow steam-arrow-right"
            @click="next"
            aria-label="Next game"
          >
            ›
          </button>

          <div class="steam-counter">
            {{ activeIndex + 1 }}
            <span>/</span>
            {{ featuredGames.length }}
          </div>

          <!-- Pause / Play toggle button (WCAG 2.2.2 — user control over auto-moving content) -->
          <button
            class="steam-carousel-pause-btn"
            @click="toggleAutoplay"
            :aria-label="
              isAutopaused
                ? 'Play carousel autoplay'
                : 'Pause carousel autoplay'
            "
            :title="isAutopaused ? 'Resume autoplay' : 'Pause autoplay'"
          >
            <svg
              v-if="isAutopaused"
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="currentColor"
              aria-hidden="true"
            >
              <path d="M8 5v14l11-7z" />
            </svg>
            <svg
              v-else
              width="12"
              height="12"
              viewBox="0 0 24 24"
              fill="currentColor"
              aria-hidden="true"
            >
              <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z" />
            </svg>
          </button>

          <div class="steam-dots">
            <button
              v-for="(game, i) in featuredGames"
              :key="game.itemType + game.id"
              class="steam-dot"
              :class="{ active: i === activeIndex }"
              @click="goTo(i, i > activeIndex ? 'next' : 'prev')"
              :aria-label="`Go to ${game.displayTitle}`"
            ></button>
          </div>
        </div>
      </div>
    </div>
    <!-- /steam-hero-fullbleed -->

    <!-- Quick Navigation Shortcuts -->
    <section class="hero-shortcuts">
      <div class="container">
        <router-link to="/games" class="hero-shortcut-card">
          <span class="shortcut-icon">
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              aria-hidden="true"
            >
              <rect x="2" y="3" width="20" height="14" rx="2" />
              <path d="M8 21h8M12 17v4" />
            </svg>
          </span>
          <span class="shortcut-title">Browse Games</span>
          <small>RAWG database</small>
        </router-link>

        <router-link to="/live-news" class="hero-shortcut-card">
          <span class="shortcut-icon">
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              aria-hidden="true"
            >
              <path
                d="M5 12.55a11 11 0 0114.08 0M1.42 9a16 16 0 0121.16 0M8.53 16.11a6 6 0 016.95 0M12 20h.01"
              />
            </svg>
          </span>
          <span class="shortcut-title">Gaming News</span>
          <small>Live updates</small>
        </router-link>

        <router-link to="/free-to-play" class="hero-shortcut-card">
          <span class="shortcut-icon">
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              aria-hidden="true"
            >
              <path d="M12 2L2 7l10 5 10-5-10-5z" />
              <path d="M2 17l10 5 10-5" />
              <path d="M2 12l10 5 10-5" />
            </svg>
          </span>
          <span class="shortcut-title">Free to Play</span>
          <small>400+ titles</small>
        </router-link>

        <router-link to="/deals" class="hero-shortcut-card">
          <span class="shortcut-icon">
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              aria-hidden="true"
            >
              <path d="M20 12V22H4V12" />
              <path d="M22 7H2v5h20V7z" />
              <path d="M12 22V7" />
              <path d="M12 7H7.5a2.5 2.5 0 010-5C11 2 12 7 12 7z" />
              <path d="M12 7h4.5a2.5 2.5 0 000-5C13 2 12 7 12 7z" />
            </svg>
          </span>
          <span class="shortcut-title">Game Deals</span>
          <small>CheapShark prices</small>
        </router-link>

        <router-link to="/library" class="hero-shortcut-card">
          <span class="shortcut-icon">
            <svg
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              aria-hidden="true"
            >
              <path d="M4 19.5A2.5 2.5 0 016.5 17H20" />
              <path
                d="M6.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15A2.5 2.5 0 016.5 2z"
              />
            </svg>
          </span>
          <span class="shortcut-title">My Library</span>
          <small>Your games</small>
        </router-link>
      </div>
    </section>
    <div class="container steam-main-container pb-5">
      <!-- ══════════════════════════════════════
           TABBED DISCOVERY
           ══════════════════════════════════════ -->
      <div
        class="steam-tabs-container"
        style="margin-bottom: var(--section-gap)"
      >
        <!-- Tabs -->
        <div
          class="steam-tabs-header"
          role="tablist"
          aria-label="Game discovery categories"
        >
          <button
            id="tab-newReleases"
            class="steam-tab-btn"
            role="tab"
            :class="{ active: activeTab === 'newReleases' }"
            :aria-selected="activeTab === 'newReleases'"
            aria-controls="tabpanel-newReleases"
            @click="setTab('newReleases')"
          >
            <Sparkles size="18" class="me-2" /> Popular New Releases
          </button>
          <button
            id="tab-comingSoon"
            class="steam-tab-btn"
            role="tab"
            :class="{ active: activeTab === 'comingSoon' }"
            :aria-selected="activeTab === 'comingSoon'"
            aria-controls="tabpanel-comingSoon"
            @click="setTab('comingSoon')"
          >
            <CalendarDays size="18" class="me-2" /> Popular Upcoming
          </button>
          <button
            id="tab-trendingFree"
            class="steam-tab-btn"
            role="tab"
            :class="{ active: activeTab === 'trendingFree' }"
            :aria-selected="activeTab === 'trendingFree'"
            aria-controls="tabpanel-trendingFree"
            @click="setTab('trendingFree')"
          >
            <Flame size="18" class="me-2" /> Trending Free
          </button>
        </div>

        <!-- Tab Content -->
        <div
          :id="'tabpanel-' + activeTab"
          class="steam-tab-content"
          role="tabpanel"
          :aria-labelledby="'tab-' + activeTab"
          tabindex="0"
        >
          <div class="row g-0">
            <!-- Left List -->
            <div class="col-md-7 col-lg-8 steam-tab-list">
              <template v-if="activeTab === 'newReleases' && releasesLoading">
                <div
                  v-for="n in 5"
                  :key="n"
                  class="skeleton steam-tab-item-skeleton"
                ></div>
              </template>
              <template
                v-else-if="activeTab === 'comingSoon' && comingSoonLoading"
              >
                <div
                  v-for="n in 5"
                  :key="n"
                  class="skeleton steam-tab-item-skeleton"
                ></div>
              </template>
              <template
                v-else-if="activeTab === 'trendingFree' && trendingFreeLoading"
              >
                <div
                  v-for="n in 5"
                  :key="n"
                  class="skeleton steam-tab-item-skeleton"
                ></div>
              </template>
              <template v-else>
                <router-link
                  v-for="(game, index) in activeTabGames"
                  :key="game.id"
                  :to="
                    game.itemType === 'f2p'
                      ? `/free-to-play/${game.id}`
                      : `/games/${game.id}`
                  "
                  class="steam-tab-item"
                  @mouseenter="setHoveredGame(game)"
                >
                  <div class="steam-tab-item-img">
                    <img :src="game.background_image" :alt="game.name" />
                  </div>
                  <div class="steam-tab-item-info">
                    <div class="steam-tab-item-title">{{ game.name }}</div>
                    <div class="steam-tab-item-tags">
                      <span
                        v-for="(genre, i) in (game.genres || []).slice(0, 3)"
                        :key="i"
                        class="steam-tab-tag"
                        >{{ genre.name }}</span
                      >
                    </div>
                  </div>
                  <div class="steam-tab-item-meta d-none d-sm-flex">
                    <span v-if="game.itemType === 'f2p'" class="steam-tab-free"
                      >Free to Play</span
                    >
                    <span v-else-if="game.price" class="steam-tab-price"
                      >${{ game.price }}</span
                    >
                  </div>
                </router-link>
              </template>
            </div>

            <!-- Right Preview Panel (only visible on hover and md+ screens) -->
            <div
              class="col-md-5 col-lg-4 d-none d-md-block steam-tab-preview-col"
            >
              <div class="steam-tab-preview" v-if="hoveredGame">
                <h4 class="steam-preview-title">{{ hoveredGame.name }}</h4>
                <div
                  class="steam-preview-reviews"
                  v-if="hoveredGame.metacritic"
                >
                  <span
                    class="preview-mc"
                    :class="metacriticClass(hoveredGame.metacritic)"
                    >{{ hoveredGame.metacritic }}</span
                  >
                  <span style="color: var(--text-secondary); font-size: 0.75rem"
                    >Metacritic</span
                  >
                </div>
                <div class="steam-preview-screenshots">
                  <img
                    v-if="hoveredGame.background_image"
                    :src="hoveredGame.background_image"
                    alt=""
                    class="preview-img-main"
                  />
                  <div class="preview-tags mt-2">
                    <span
                      v-for="(genre, i) in (hoveredGame.genres || []).slice(
                        0,
                        4,
                      )"
                      :key="i"
                      class="steam-tab-tag"
                      >{{ genre.name }}</span
                    >
                  </div>
                </div>
              </div>
              <div
                class="steam-tab-preview"
                style="
                  display: flex;
                  align-items: center;
                  justify-content: center;
                  opacity: 0.5;
                  height: 100%;
                "
                v-else
              >
                <div style="text-align: center">
                  <i
                    class="bi bi-controller"
                    style="font-size: 2rem; display: block; margin-bottom: 10px"
                  ></i>
                  <span>Hover over a game for details</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ══════════════════════════════════════
           GENRE EXPLORER
           ══════════════════════════════════════ -->
      <div class="mb-5">
        <div class="section-header mb-4">
          <span class="section-icon">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <rect x="3" y="3" width="7" height="7" />
              <rect x="14" y="3" width="7" height="7" />
              <rect x="14" y="14" width="7" height="7" />
              <rect x="3" y="14" width="7" height="7" />
            </svg>
          </span>
          <h2 class="mb-0">Explore by Genre</h2>
        </div>

        <div class="steam-genre-explorer">
          <router-link
            v-for="(g, i) in genres"
            :key="g.label"
            :to="g.link"
            :class="['steam-genre-card', `sgc-${g.color}`, 'stagger-item']"
            :style="{ animationDelay: `${i * 0.04}s` }"
            :aria-label="`Browse ${g.label} games`"
          >
            <div class="sgc-bg"></div>
            <div class="sgc-content">
              <span class="sgc-label">{{ g.label }}</span>
            </div>
            <img :src="g.icon" :alt="g.label" class="sgc-icon" />
          </router-link>
        </div>
      </div>

      <!-- ══════════════════════════════════════
           HOT DEALS — Horizontal Scroll Strip
           ══════════════════════════════════════ -->
      <div style="margin-bottom: var(--section-gap)">
        <div class="section-header mb-4">
          <span
            class="section-icon"
            style="
              background: linear-gradient(135deg, #92400e, #f59e0b);
              box-shadow: 0 4px 16px rgba(245, 158, 11, 0.4);
            "
          >
            <i
              class="bi bi-tags-fill"
              style="color: white; font-size: 1.1rem"
            ></i>
          </span>
          <h2 class="mb-0">Best Deals Right Now</h2>
          <router-link
            to="/deals"
            class="ms-auto btn btn-sm"
            style="
              background: rgba(245, 158, 11, 0.12);
              border: 1px solid rgba(245, 158, 11, 0.3);
              color: #fbbf24;
              font-size: 0.8rem;
              border-radius: 20px;
              padding: 4px 16px;
            "
          >
            View All
            <span class="visually-hidden"> game deals</span>
            →
          </router-link>
        </div>

        <!-- Skeleton -->
        <div v-if="dealsLoading" class="h-scroll-strip">
          <div
            v-for="n in 8"
            :key="n"
            class="steam-special-offer-card"
            style="background: var(--bg-glass)"
          >
            <div class="skeleton" style="height: 120px; width: 100%"></div>
            <div class="sso-body">
              <div
                class="skeleton"
                style="height: 12px; width: 85%; margin-bottom: 6px"
              ></div>
              <div class="skeleton" style="height: 24px; width: 100%"></div>
            </div>
          </div>
        </div>

        <!-- Deals strip -->
        <div v-else class="h-scroll-strip">
          <a
            v-for="deal in hotDeals"
            :key="deal.dealID"
            :href="`https://www.cheapshark.com/redirect?dealID=${deal.dealID}`"
            target="_blank"
            rel="noopener noreferrer"
            class="steam-special-offer-card stagger-item"
            :aria-label="`${deal.title} — ${deal.salePrice === '0.00' ? 'Free' : '$' + deal.salePrice}`"
          >
            <div class="sso-img-wrap">
              <img :src="deal.thumb" :alt="deal.title" loading="lazy" />
            </div>
            <div class="sso-body">
              <p class="sso-title">{{ deal.title }}</p>
              <div class="sso-price-row">
                <div class="sso-discount">
                  -{{ Math.round(parseFloat(deal.savings)) }}%
                </div>
                <div class="sso-prices">
                  <span class="sso-orig">${{ deal.normalPrice }}</span>
                  <span class="sso-sale">{{
                    deal.salePrice === "0.00" ? "FREE" : `$${deal.salePrice}`
                  }}</span>
                </div>
              </div>
            </div>
          </a>
        </div>
      </div>

      <!-- ══════════════════════════════════════
           STATS COUNTER
           ══════════════════════════════════════ -->
      <div class="stats-section" id="stats-section">
        <div class="row text-center">
          <div class="col-6 col-md-3">
            <div class="stat-item">
              <span class="stat-number">500K+</span>
              <span class="stat-label">Games via RAWG</span>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="stat-item">
              <span class="stat-number">400+</span>
              <span class="stat-label">Free-to-Play Titles</span>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="stat-item">
              <span class="stat-number">Live</span>
              <span class="stat-label">NewsAPI Headlines</span>
            </div>
          </div>
          <div class="col-6 col-md-3">
            <div class="stat-item">
              <span class="stat-number">30+</span>
              <span class="stat-label">Game Stores Tracked</span>
            </div>
          </div>
        </div>
      </div>

      <!-- ══════════════════════════════════════
           WHY GAMEHUB — Premium Feature Cards
           ══════════════════════════════════════ -->
      <div style="margin-bottom: var(--section-gap)">
        <div class="section-header mb-5">
          <span class="section-icon">
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="10" />
              <path d="M12 8v4M12 16h.01" />
            </svg>
          </span>
          <h2 class="mb-0">
            Why Choose <span class="gradient-text">GameHub?</span>
          </h2>
        </div>

        <div class="row g-4">
          <div class="col-md-4">
            <div class="feature-card fc-violet">
              <span class="feature-card-icon"
                ><i class="bi bi-joystick"></i
              ></span>
              <h5>Massive Library</h5>
              <p>
                Discover 500,000+ titles from RAWG's database plus 400+
                free-to-play games across every genre and platform imaginable.
              </p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card fc-cyan">
              <span class="feature-card-icon"
                ><i class="bi bi-broadcast"></i
              ></span>
              <h5>Live Gaming News</h5>
              <p>
                Stay ahead with real-time gaming news from NewsAPI alongside our
                own curated GameHub articles and community posts.
              </p>
            </div>
          </div>
          <div class="col-md-4">
            <div class="feature-card fc-coral">
              <span class="feature-card-icon"><i class="bi bi-tag"></i></span>
              <h5>Best Deals Finder</h5>
              <p>
                Never overpay again. Our CheapShark-powered Deals page tracks
                the lowest prices on Steam, Epic, GOG &amp; more.
              </p>
            </div>
          </div>
          <div class="col-md-4">
            <div
              class="feature-card fc-violet"
              style="
                --fc-gradient: linear-gradient(
                  135deg,
                  rgba(6, 182, 212, 0.12),
                  transparent
                );
                --fc-glow: rgba(6, 182, 212, 0.6);
              "
            >
              <span class="feature-card-icon"
                ><i class="bi bi-bookmark-heart"></i
              ></span>
              <h5>Personal Collection</h5>
              <p>
                Save any game to your wishlist. Your collection is synced to the
                cloud and accessible from any device.
              </p>
            </div>
          </div>
          <div class="col-md-4">
            <div
              class="feature-card fc-cyan"
              style="
                --fc-gradient: linear-gradient(
                  135deg,
                  rgba(244, 63, 94, 0.12),
                  transparent
                );
                --fc-glow: rgba(244, 63, 94, 0.6);
              "
            >
              <span class="feature-card-icon"
                ><i class="bi bi-pencil-square"></i
              ></span>
              <h5>Write Reviews</h5>
              <p>
                Share your thoughts. Leave star-rated reviews on any game and
                read what other players have to say.
              </p>
            </div>
          </div>
          <div class="col-md-4">
            <div
              class="feature-card fc-coral"
              style="
                --fc-gradient: linear-gradient(
                  135deg,
                  rgba(124, 58, 237, 0.12),
                  transparent
                );
                --fc-glow: rgba(124, 58, 237, 0.6);
              "
            >
              <span class="feature-card-icon"><i class="bi bi-globe"></i></span>
              <h5>100% Free</h5>
              <p>
                No subscriptions, no paywalls, no ads. GameHub is a
                community-first platform built to be free for everyone.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.mc-green {
  background: #15803d !important;
  color: #fff !important;
}
.mc-yellow {
  background: #a16207 !important;
  color: #fff !important;
}
.mc-red {
  background: #b91c1c !important;
  color: #fff !important;
}
.mc-grey {
  background: var(--bg-glass) !important;
  color: var(--text-muted) !important;
}

/* ---- Carousel Pause/Play button (WCAG 2.2.2) ---- */
.steam-carousel-pause-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 10;
  width: 32px;
  height: 32px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: rgba(0, 0, 0, 0.55);
  color: rgba(255, 255, 255, 0.75);
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition:
    background 0.2s,
    color 0.2s,
    border-color 0.2s;
  backdrop-filter: blur(6px);
}
.steam-carousel-pause-btn:hover {
  background: rgba(14, 165, 233, 0.4);
  border-color: rgba(14, 165, 233, 0.6);
  color: #fff;
}
.steam-carousel-pause-btn:focus-visible {
  outline: 3px solid var(--primary-light);
  outline-offset: 2px;
}

.h-scroll-strip {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
  scroll-snap-type: x mandatory;
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}
.h-scroll-strip::-webkit-scrollbar {
  display: none;
}
.h-scroll-card {
  width: 220px;
  flex: 0 0 220px;
  border-radius: 12px;
  overflow: hidden;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  text-decoration: none;
  color: inherit;
  scroll-snap-align: start;
}
.h-scroll-img-wrap {
  position: relative;
  height: 120px;
  overflow: hidden;
}
.h-scroll-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.h-card-badges {
  position: absolute;
  left: 8px;
  top: 8px;
  display: flex;
  gap: 8px;
}
.h-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  padding: 6px 8px;
  border-radius: 999px;
  color: #fff;
  font-weight: 700;
  backdrop-filter: blur(6px);
}
.h-badge img {
  width: 14px;
  height: 14px;
  object-fit: contain;
}
.h-badge-verified {
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
  box-shadow: 0 6px 20px rgba(251, 191, 36, 0.12);
}
.h-badge-official {
  background: rgba(59, 130, 246, 0.95);
}
.h-scroll-card-body {
  padding: 12px 14px;
}
.h-scroll-card-title {
  font-size: 0.88rem;
  font-weight: 700;
  margin: 0 0 6px 0;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.h-scroll-card-meta {
  display: flex;
  gap: 8px;
  align-items: center;
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* Deal scroll cards */
.deal-scroll-card {
  width: 220px;
  flex: 0 0 220px;
  border-radius: 12px;
  overflow: hidden;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  text-decoration: none;
  color: inherit;
  transition:
    transform 0.22s ease,
    box-shadow 0.22s ease,
    border-color 0.22s ease;
}
.deal-scroll-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 32px rgba(245, 158, 11, 0.18);
  border-color: rgba(245, 158, 11, 0.3);
}
.deal-scroll-img-wrap {
  position: relative;
  height: 120px;
  overflow: hidden;
}
.deal-scroll-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
}
.deal-scroll-card:hover .deal-scroll-img-wrap img {
  transform: scale(1.06);
}
.deal-scroll-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(10, 15, 30, 0.7) 0%,
    transparent 55%
  );
  pointer-events: none;
}
.deal-scroll-savings {
  position: absolute;
  top: 8px;
  right: 8px;
  background: linear-gradient(135deg, #15803d, #4ade80);
  color: #fff;
  font-weight: 800;
  font-size: 0.68rem;
  padding: 3px 8px;
  border-radius: 20px;
  letter-spacing: 0.4px;
}
.deal-scroll-price {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 4px;
}
.deal-scroll-orig {
  text-decoration: line-through;
  color: var(--text-muted);
  font-size: 0.75rem;
}
.deal-scroll-sale {
  font-weight: 800;
  font-size: 0.95rem;
  color: #fbbf24;
}
/* --- SUMMER SALE HERO --- */
.summer-sale-hero {
  position: relative;
  width: 100%;
  height: 500px;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  overflow: hidden;
  margin-top: -70px;
  margin-bottom: 0;
}
.summer-sale-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at center, #0070d1, #002b66 80%);
  z-index: 1;
}
.summer-sale-bg::after {
  content: "";
  position: absolute;
  inset: 0;
  background: url("https://gmedia.playstation.com/is/image/SIEPDC/ps-store-hero-bg-light")
    center/cover;
  opacity: 0.1;
  mix-blend-mode: overlay;
}
.summer-sale-content {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}
.summer-sale-title-container {
  text-transform: uppercase;
  letter-spacing: 2px;
}
.ss-steam {
  font-size: 1.5rem;
  font-weight: 800;
  color: #bae6fd;
  display: block;
  margin-bottom: -10px;
}
.summer-sale-title {
  font-size: 5.5rem;
  font-weight: 900;
  color: #fff;
  text-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
  margin: 0;
  line-height: 1.1;
}
.summer-sale-subtitle {
  font-size: 1.1rem;
  color: #e0f2fe;
  letter-spacing: 4px;
  font-weight: 600;
  margin-top: 1rem;
}

@media (max-width: 768px) {
  .summer-sale-title {
    font-size: 3.5rem;
  }
  .summer-sale-subtitle {
    font-size: 0.9rem;
    letter-spacing: 2px;
  }
}

/* --- STEAM TABBED DISCOVERY --- */
.steam-tabs-container {
  background: var(--bg-surface);
  border-radius: 8px;
  border: 1px solid var(--border-subtle);
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
}
.steam-tabs-header {
  display: flex;
  background: var(--bg-deep);
  border-bottom: 1px solid var(--border-subtle);
}
.steam-tab-btn {
  flex: 1;
  background: transparent;
  border: none;
  color: var(--text-muted);
  font-weight: 600;
  font-size: 0.95rem;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  border-bottom: 2px solid transparent;
  text-align: center;
}
.steam-tab-btn:hover {
  color: var(--text-primary);
  background: var(--bg-surface);
}
.steam-tab-btn.active {
  color: var(--text-primary);
  border-bottom-color: #00439c;
  background: var(--bg-surface);
}
.steam-tab-content {
  background: var(--bg-surface);
  min-height: 400px;
}
.steam-tab-list {
  max-height: 500px;
  overflow-y: auto;
}
.steam-tab-list::-webkit-scrollbar {
  width: 8px;
}
.steam-tab-list::-webkit-scrollbar-track {
  background: var(--bg-deep);
}
.steam-tab-list::-webkit-scrollbar-thumb {
  background: var(--border-subtle);
  border-radius: 4px;
}
.steam-tab-list::-webkit-scrollbar-thumb:hover {
  background: var(--text-muted);
}
.steam-tab-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  text-decoration: none;
  border-bottom: 1px solid var(--border-subtle);
  transition: background 0.15s ease;
  color: inherit;
}
.steam-tab-item:hover {
  background: var(--bg-deep);
  cursor: pointer;
}
.steam-tab-item-img {
  width: 140px;
  height: 65px;
  flex-shrink: 0;
  overflow: hidden;
  border-radius: 4px;
  background: var(--bg-deep);
}
.steam-tab-item-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.steam-tab-item-info {
  flex: 1;
  min-width: 0;
  padding: 0 16px;
}
.steam-tab-item-title {
  color: var(--text-primary);
  font-weight: 600;
  font-size: 1.05rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}
.steam-tab-item-tags {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}
.steam-tab-tag {
  font-size: 0.65rem;
  background: var(--bg-deep);
  color: var(--text-secondary);
  padding: 2px 6px;
  border-radius: 4px;
}
.steam-tab-item-meta {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  width: 100px;
}
.steam-tab-free {
  color: #00439c;
  font-weight: 700;
  font-size: 0.9rem;
}
.steam-tab-price {
  color: var(--text-primary);
  font-weight: 700;
  font-size: 0.9rem;
  background: var(--bg-deep);
  padding: 4px 8px;
  border-radius: 4px;
}
.steam-tab-preview-col {
  background: var(--bg-deep);
  border-left: 1px solid var(--border-subtle);
}
.steam-tab-preview {
  padding: 24px;
  position: sticky;
  top: 0;
}
.steam-preview-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 12px;
}
.steam-preview-reviews {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}
.preview-mc {
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: 700;
  font-size: 0.85rem;
}
.preview-img-main {
  width: 100%;
  aspect-ratio: 16/9;
  object-fit: cover;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 12px;
}

/* --- STEAM SPECIAL OFFERS --- */
.steam-special-offer-card {
  width: 280px;
  flex: 0 0 280px;
  background: var(--bg-surface);
  display: flex;
  flex-direction: column;
  text-decoration: none;
  color: inherit;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid var(--border-subtle);
}
.steam-special-offer-card:hover {
  transform: scale(1.03);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}
.sso-img-wrap {
  width: 100%;
  height: 130px;
}
.sso-img-wrap img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.sso-body {
  padding: 12px;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}
.sso-title {
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 12px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.sso-price-row {
  display: flex;
  align-items: stretch;
  height: 34px;
  background: var(--bg-deep);
  border-radius: 4px;
  overflow: hidden;
  width: fit-content;
}
.sso-discount {
  background: #facc15;
  color: #111827;
  font-weight: 700;
  font-size: 0.95rem;
  padding: 0 8px;
  display: flex;
  align-items: center;
}
.sso-prices {
  background: transparent;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0 8px;
}
.sso-orig {
  color: var(--text-muted);
  text-decoration: line-through;
  font-size: 0.65rem;
  line-height: 1;
  margin-bottom: 2px;
}
.sso-sale {
  color: var(--text-primary);
  font-size: 0.85rem;
  font-weight: 700;
  line-height: 1;
}

/* --- STEAM GENRE CARDS --- */
.steam-genre-explorer {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}
.steam-genre-card {
  position: relative;
  height: 140px;
  border-radius: 8px;
  overflow: hidden;
  text-decoration: none;
  color: #fff;
  transition:
    transform 0.2s,
    box-shadow 0.2s;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}
.steam-genre-card:hover {
  transform: scale(1.05);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.2);
  z-index: 2;
}
.sgc-bg {
  position: absolute;
  inset: 0;
  background: linear-gradient(135deg, #00439c, #002b66);
  z-index: 1;
  transition: opacity 0.3s;
}
.sgc-content {
  position: absolute;
  inset: 0;
  z-index: 3;
  display: flex;
  align-items: flex-end;
  padding: 16px;
  background: linear-gradient(to top, rgba(0, 0, 0, 0.6) 0%, transparent 60%);
}
.sgc-label {
  font-size: 1.25rem;
  font-weight: 800;
  letter-spacing: 1px;
  text-transform: uppercase;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.5);
}
.sgc-icon {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 64px;
  height: 64px;
  object-fit: contain;
  z-index: 2;
  opacity: 0.5;
  transition:
    transform 0.3s,
    opacity 0.3s;
  filter: brightness(0) invert(1);
}
.steam-genre-card:hover .sgc-icon {
  transform: scale(1.1) rotate(5deg);
  opacity: 0.9;
}

.sgc-violet .sgc-bg {
  background: linear-gradient(135deg, #6366f1, #4338ca);
}
.sgc-coral .sgc-bg {
  background: linear-gradient(135deg, #f43f5e, #be123c);
}
.sgc-gold .sgc-bg {
  background: linear-gradient(135deg, #f59e0b, #b45309);
}
.sgc-cyan .sgc-bg {
  background: linear-gradient(135deg, #06b6d4, #0e7490);
}
.sgc-green .sgc-bg {
  background: linear-gradient(135deg, #10b981, #047857);
}
.sgc-pink .sgc-bg {
  background: linear-gradient(135deg, #ec4899, #be185d);
}

.h-scroll-strip {
  padding-bottom: 16px;
}
</style>
