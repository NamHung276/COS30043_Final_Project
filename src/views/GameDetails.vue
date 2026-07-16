<script>
import { inject } from "vue";
import { auth, db } from "../firebase";
import { rawgApi, cheapSharkApi } from "../services/api";
import { onAuthStateChanged } from "firebase/auth";
import { collection, query, where, getDocs, addDoc } from "firebase/firestore";
import ReviewSection from "../components/ReviewSection.vue";
import TrailerModal from "../components/TrailerModal.vue";
import { cartState } from "../services/cart";

const STORE_NAMES = {
  1: "Steam",
  2: "GamersGate",
  3: "GreenManGaming",
  7: "GOG",
  8: "Origin",
  11: "Humble Store",
  13: "Uplay",
  15: "Fanatical",
  21: "WinGameStore",
  23: "GameBillet",
  24: "Voidu",
  25: "Epic Games",
  27: "Games Planet",
  28: "Games Tradera",
  29: "Games Republic",
  30: "Silagrastore",
  31: "Allyouplay",
  32: "DLGamer",
  33: "Noctre",
  34: "DreamGame",
};

export default {
  components: { ReviewSection, TrailerModal },

  setup() {
    const toast = inject("toast");
    return { toast };
  },

  data() {
    return {
      game: null,
      screenshots: [],
      trailers: [],
      similarGames: [],
      loading: true,
      currentUser: null,
      activeShot: 0,
      lightboxSrc: null,
      lightboxIndex: 0,
      favStatus: { visible: false, message: "", type: "success" },
      discoverMoreGames: [],
      recentGames: [],
      carouselInterval: null,
      // Trailer modal
      showTrailerModal: false,
      // CheapShark deals
      deals: [],
      dealsLoading: false,
      STORE_NAMES: {
        1: "Steam",
        7: "GOG",
        11: "Humble Store",
        15: "Fanatical",
        25: "Epic Games",
        3: "GreenManGaming",
        8: "Origin",
        13: "Uplay",
      },
    };
  },

  computed: {
    metacriticClass() {
      const s = this.game?.metacritic;
      if (!s) return "mc-grey";
      if (s >= 75) return "mc-green";
      if (s >= 50) return "mc-yellow";
      return "mc-red";
    },

    metacriticLabel() {
      const s = this.game?.metacritic;
      if (!s) return null;
      if (s >= 75) return "Overwhelmingly Positive";
      if (s >= 60) return "Mostly Positive";
      if (s >= 40) return "Mixed";
      return "Mostly Negative";
    },

    ratingPercent() {
      return this.game?.rating ? (this.game.rating / 5) * 100 : 0;
    },

    platforms() {
      return (this.game?.platforms || []).map((p) => ({
        name: p.platform.name,
        icon: this.platformIcon(p.platform.name),
      }));
    },

    developerNames() {
      return (this.game?.developers || []).map((d) => d.name).join(", ") || "—";
    },

    publisherNames() {
      return (this.game?.publishers || []).map((p) => p.name).join(", ") || "—";
    },

    genreNames() {
      return (this.game?.genres || []).map((g) => g.name);
    },

    heroImage() {
      if (this.screenshots.length && this.screenshots[this.activeShot]) {
        return this.screenshots[this.activeShot].image;
      }
      return this.game?.background_image;
    },

    fakePrice() {
      if (!this.game) return 0;
      const base = (this.game.id % 40) + 10;
      return (base + 0.99).toFixed(2);
    },

    fakeDiscount() {
      if (!this.game) return 0;
      const roll = this.game.id % 4;
      if (roll === 0) return 40;
      if (roll === 1) return 25;
      return 0;
    },

    discountedPrice() {
      const price = parseFloat(this.fakePrice);
      const disc = this.fakeDiscount;
      if (!disc) return null;
      return (price * (1 - disc / 100)).toFixed(2);
    },

    trailerYoutubeId() {
      // Try RAWG movies first (clip url)
      if (this.trailers.length > 0) {
        const t = this.trailers[0];
        if (t.data?.max) return null; // direct mp4, use videoUrl
        const m = (t.preview || "").match(
          /(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=))([\w-]{11})/,
        );
        if (m) return m[1];
      }
      // Try game.clip
      if (this.game?.clip?.video) {
        const m = this.game.clip.video.match(
          /(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=))([\w-]{11})/,
        );
        if (m) return m[1];
      }
      return null;
    },

    trailerVideoUrl() {
      if (this.trailers.length > 0 && this.trailers[0].data?.max) {
        return this.trailers[0].data.max;
      }
      return this.game?.clip?.clips?.full || this.game?.clip?.clip || null;
    },

    trailerPoster() {
      return this.trailers[0]?.preview || this.game?.background_image || null;
    },

    hasTrailer() {
      return !!(this.trailerYoutubeId || this.trailerVideoUrl);
    },

    pcRequirements() {
      const pcPlatform = (this.game?.platforms || []).find(
        (p) => p.platform.slug === "pc",
      );
      return pcPlatform?.requirements || null;
    },

    cheapestDeal() {
      if (!this.deals.length) return null;
      return this.deals.reduce((best, d) => {
        return parseFloat(d.salePrice) < parseFloat(best.salePrice) ? d : best;
      });
    },
  },

  watch: {
    "$route.params.id": {
      immediate: true,
      handler(newId) {
        if (newId) {
          this.fetchData(newId);
        }
      },
    },
  },

  methods: {
    storeName(id) {
      return STORE_NAMES[id] || `Store #${id}`;
    },

    platformIcon(name) {
      const n = name.toLowerCase();
      if (n.includes("pc") || n.includes("windows")) return "/logo/pc.svg";
      if (n.includes("playstation")) return "/logo/playstation_logo.png";
      if (n.includes("xbox")) return "/logo/xbox_logo.png";
      if (n.includes("nintendo") || n.includes("switch"))
        return "/logo/nintendo_logo.png";
      if (n.includes("mac")) return "/logo/macos.png";
      if (n.includes("linux")) return "/logo/linux.png";
      if (n.includes("android") || n.includes("ios") || n.includes("mobile"))
        return "/logo/mobile.svg";
      return "/logo/gamepad.svg";
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

    showFavStatus(message, type = "success") {
      this.favStatus = { visible: true, message, type };
      clearTimeout(this._favTimer);
      this._favTimer = setTimeout(() => {
        this.favStatus.visible = false;
      }, 3000);
    },

    async addToFavorites() {
      if (!this.currentUser) {
        this.showFavStatus("Please login to add favorites.", "warning");
        setTimeout(() => this.$router.push("/login"), 1500);
        return;
      }
      try {
        const snap = await getDocs(
          query(
            collection(db, "favorites"),
            where("userId", "==", this.currentUser.uid),
            where("gameId", "==", this.game.id),
          ),
        );
        if (!snap.empty) {
          this.showFavStatus("⚠️ Already in your wishlist!", "warning");
          return;
        }
        await addDoc(collection(db, "favorites"), {
          userId: this.currentUser.uid,
          gameId: this.game.id,
          title: this.game.name,
          thumbnail: this.game.background_image,
          genre: this.game.genres?.[0]?.name || "",
        });
        this.showFavStatus("⭐ Added to wishlist!", "success");
      } catch (err) {
        console.error(err);
        this.showFavStatus("Something went wrong. Please try again.", "error");
      }
    },

    openLightbox(src, index) {
      this.lightboxSrc = src;
      this.lightboxIndex = index ?? this.activeShot;
      this.stopCarousel();
    },
    closeLightbox() {
      this.lightboxSrc = null;
      this.startCarousel();
    },
    lightboxPrev() {
      if (!this.screenshots.length) return;
      this.lightboxIndex =
        (this.lightboxIndex - 1 + this.screenshots.length) %
        this.screenshots.length;
      this.lightboxSrc = this.screenshots[this.lightboxIndex].image;
      this.activeShot = this.lightboxIndex;
    },
    lightboxNext() {
      if (!this.screenshots.length) return;
      this.lightboxIndex = (this.lightboxIndex + 1) % this.screenshots.length;
      this.lightboxSrc = this.screenshots[this.lightboxIndex].image;
      this.activeShot = this.lightboxIndex;
    },
    onLightboxKey(e) {
      if (e.key === "Escape") this.closeLightbox();
      if (e.key === "ArrowLeft") this.lightboxPrev();
      if (e.key === "ArrowRight") this.lightboxNext();
    },

    selectShot(i) {
      this.activeShot = i;
      this.startCarousel();
    },

    startCarousel() {
      this.stopCarousel();
      this.carouselInterval = setInterval(() => {
        if (
          this.screenshots &&
          this.screenshots.length > 0 &&
          !this.lightboxSrc
        ) {
          this.activeShot = (this.activeShot + 1) % this.screenshots.length;
        }
      }, 4000);
    },

    stopCarousel() {
      if (this.carouselInterval) {
        clearInterval(this.carouselInterval);
        this.carouselInterval = null;
      }
    },

    addToCart() {
      cartState.add({
        id: this.game.id,
        name: this.game.name,
        price: this.fakePrice,
        thumbnail: this.game.background_image,
      });
      this.toast?.show(`${this.game.name} added to cart`, "success");
    },

    buyNow() {
      this.addToCart();
      this.$router.push("/checkout");
    },

    async fetchData(id) {
      this.loading = true;
      this.game = null;
      this.screenshots = [];
      this.trailers = [];
      this.similarGames = [];
      this.activeShot = 0;

      try {
        const [gameRes, ssRes, moviesRes, simRes] = await Promise.all([
          rawgApi.get(`/games/${id}`),
          rawgApi.get(`/games/${id}/screenshots`),
          rawgApi.get(`/games/${id}/movies`),
          rawgApi.get(`/games/${id}/game-series`),
        ]);
        this.game = gameRes.data;
        this.screenshots = ssRes.data.results || [];
        this.trailers = moviesRes.data.results || [];
        this.similarGames = (simRes.data.results || []).slice(0, 6);

        const genreSlug = this.game.genres?.[0]?.slug;

        const today = new Date();
        const past = new Date(today);
        past.setMonth(past.getMonth() - 6);
        const dateStr = `${past.toISOString().split("T")[0]},${today.toISOString().split("T")[0]}`;

        const discoverPromise = genreSlug
          ? rawgApi.get("/games", {
              params: { genres: genreSlug, ordering: "-added", page_size: 7 },
            })
          : Promise.resolve({ data: { results: [] } });

        const recentPromise = rawgApi.get("/games", {
          params: { dates: dateStr, ordering: "-released", page_size: 6 },
        });

        const [discoverRes, recentRes] = await Promise.all([
          discoverPromise,
          recentPromise,
        ]);

        this.discoverMoreGames = (discoverRes.data.results || [])
          .filter((g) => g.id !== Number(id))
          .slice(0, 6);
        this.recentGames = recentRes.data.results || [];

        document.title = `${this.game.name} | GameHub`;
        window.scrollTo({ top: 0, behavior: "smooth" });
        this.startCarousel();

        // Fetch CheapShark deals (non-blocking)
        this.fetchDeals(this.game.name);
      } catch (err) {
        console.error(err);
      } finally {
        this.loading = false;
      }
    },

    async fetchDeals(title) {
      this.dealsLoading = true;
      this.deals = [];
      try {
        const res = await cheapSharkApi.get("/deals", {
          params: {
            title: title.substring(0, 30), // CheapShark title search
            pageSize: 5,
            sortBy: "Price",
          },
        });
        this.deals = (res.data || []).filter((d) => d.title && d.salePrice);
      } catch {
        // Silently fail — not critical
      } finally {
        this.dealsLoading = false;
      }
    },
  },

  mounted() {
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      this.currentUser = user;
    });
    document.addEventListener("keydown", this.onLightboxKey);
  },

  beforeUnmount() {
    if (this.unsubscribe) this.unsubscribe();
    this.stopCarousel();
    document.removeEventListener("keydown", this.onLightboxKey);
  },
};
</script>

<template>
  <div>
    <!-- ── Loading ───────────────────────────────── -->
    <!-- ── Loading ───────────────────────────────── -->
    <div v-if="loading" class="gd-loader">
      <div class="gd-loader-inner">
        <div class="gd-spinner"></div>
        <p class="text-muted mt-3" style="font-size: 0.9rem">
          Loading game data…
        </p>
      </div>
    </div>

    <!-- ── Not Found ─────────────────────────────── -->
    <div v-else-if="!game" class="container mt-4">
      <div class="alert alert-danger">Game not found.</div>
      <router-link to="/games" class="btn btn-outline-secondary"
        >← Back to Games</router-link
      >
    </div>

    <!-- ── Game Page ─────────────────────────────── -->
    <div v-else>
      <!-- ══════════ CINEMATIC HERO ══════════ -->
      <div class="gd-hero">
        <!-- Blurred background art -->
        <div class="gd-hero-bg" aria-hidden="true">
          <img :src="heroImage || game.background_image" alt="" />
        </div>

        <!-- Gradient overlay -->
        <div class="gd-hero-overlay" aria-hidden="true"></div>

        <!-- Content -->
        <div class="container gd-hero-content">
          <router-link to="/games" class="gd-back-btn"> ← Games </router-link>

          <div class="gd-hero-bottom">
            <!-- Cover thumbnail -->
            <img
              v-if="game.background_image"
              v-lazy-img="game.background_image"
              class="gd-cover"
              :alt="`${game.name} cover`"
            />

            <!-- Title + meta -->
            <div class="gd-hero-info">
              <div class="d-flex flex-wrap gap-2 mb-2">
                <span v-for="g in genreNames" :key="g" class="gd-badge-genre">{{
                  g
                }}</span>
                <span v-if="game.esrb_rating" class="gd-badge-esrb">{{
                  game.esrb_rating.name
                }}</span>
              </div>
              <h1 class="gd-title">{{ game.name }}</h1>

              <!-- Rating bar -->
              <div v-if="game.rating" class="gd-rating-row">
                <div class="gd-stars">
                  <div
                    class="gd-stars-fill"
                    :style="{ width: ratingPercent + '%' }"
                  ></div>
                </div>
                <span class="gd-rating-text">
                  {{ game.rating.toFixed(1) }}/5
                  <span class="gd-rating-count"
                    >Based on
                    {{
                      (game.ratings_count || 0).toLocaleString()
                    }}
                    ratings</span
                  >
                </span>
                <span
                  v-if="game.metacritic"
                  class="gd-metacritic"
                  :class="metacriticClass"
                >
                  {{ game.metacritic }}
                </span>
              </div>

              <!-- Platform chips -->
              <div class="d-flex flex-wrap gap-2 mt-2">
                <span
                  v-for="p in platforms.slice(0, 6)"
                  :key="p.name"
                  class="gd-platform-chip"
                >
                  <img
                    :src="p.icon"
                    :alt="`${p.name} logo`"
                    class="gd-platform-logo"
                  />
                  <span>{{ p.name }}</span>
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ══════════ MAIN BODY ══════════ -->
      <div class="container gd-body">
        <div class="row g-4">
          <!-- ── LEFT: Screenshots + About + Tags ── -->
          <div class="col-lg-8">
            <!-- Gameplay Trailer -->
            <div v-if="hasTrailer" class="gd-section mb-4">
              <h2 class="gd-section-title mb-3">Gameplay Trailer</h2>
              <div
                class="gd-trailer-thumb"
                @click="showTrailerModal = true"
                role="button"
                tabindex="0"
                aria-label="Play trailer"
              >
                <img
                  :src="trailerPoster || game.background_image"
                  :alt="`${game.name} trailer thumbnail`"
                  class="gd-trailer-thumb-img"
                />
                <div class="gd-trailer-play-btn" aria-hidden="true">
                  <span class="gd-play-icon">▶</span>
                  <span>Watch Trailer</span>
                </div>
              </div>

              <TrailerModal
                :show="showTrailerModal"
                :youtube-id="trailerYoutubeId"
                :video-url="trailerVideoUrl"
                :poster-url="trailerPoster"
                :title="game.name"
                @close="showTrailerModal = false"
              />
            </div>

            <!-- Screenshot Viewer -->
            <div v-if="screenshots.length" class="gd-screenshots-block mb-4">
              <!-- Main featured shot -->
              <div
                class="gd-shot-main"
                @click="openLightbox(screenshots[activeShot].image, activeShot)"
              >
                <img
                  v-lazy-img="screenshots[activeShot].image"
                  :alt="`${game.name} screenshot ${activeShot + 1}`"
                  class="gd-shot-main-img"
                />
                <div class="gd-shot-zoom-hint">
                  <span>🔍 Click to enlarge</span>
                  <span class="gd-shot-counter"
                    >{{ activeShot + 1 }} / {{ screenshots.length }}</span
                  >
                </div>
              </div>
              <!-- Thumbnail strip -->
              <div class="gd-shot-strip" role="tablist">
                <button
                  v-for="(shot, i) in screenshots"
                  :key="shot.id"
                  class="gd-shot-thumb"
                  :class="{ active: i === activeShot }"
                  @click="selectShot(i)"
                  :aria-label="`View screenshot ${i + 1}`"
                  role="tab"
                  :aria-selected="i === activeShot"
                >
                  <img v-lazy-img="shot.image" :alt="`Screenshot ${i + 1}`" />
                </button>
              </div>
            </div>

            <!-- About -->
            <div class="gd-section mb-5">
              <h2 class="gd-section-title" style="font-size: 2rem">
                About this game
              </h2>
              <div class="gd-description">
                {{ game.description_raw || "No description available." }}
              </div>
            </div>

            <!-- Tags -->
            <div v-if="game.tags?.length" class="gd-section mb-5">
              <h2 class="gd-section-title">Tags</h2>
              <div class="gd-tags">
                <span
                  v-for="tag in game.tags.slice(0, 20)"
                  :key="tag.id"
                  class="gd-tag"
                >
                  {{ tag.name }}
                </span>
              </div>
            </div>

            <!-- System Requirements -->
            <div
              v-if="pcRequirements?.minimum || pcRequirements?.recommended"
              class="gd-section mb-5"
            >
              <h2 class="gd-section-title">System Requirements</h2>
              <div class="gd-sysreq-grid">
                <div v-if="pcRequirements.minimum" class="gd-sysreq-col">
                  <div class="gd-sysreq-label">Minimum</div>
                  <pre class="gd-sysreq-text">{{ pcRequirements.minimum }}</pre>
                </div>
                <div v-if="pcRequirements.recommended" class="gd-sysreq-col">
                  <div class="gd-sysreq-label">Recommended</div>
                  <pre class="gd-sysreq-text">{{
                    pcRequirements.recommended
                  }}</pre>
                </div>
              </div>
            </div>

            <!-- Similar Games / Series -->
            <div v-if="similarGames.length" class="gd-section mb-5">
              <h2 class="gd-section-title">More in This Series</h2>
              <div class="gd-similar-grid">
                <router-link
                  v-for="g in similarGames"
                  :key="g.id"
                  :to="`/games/${g.id}`"
                  class="gd-similar-card"
                >
                  <img
                    v-lazy-img="g.background_image"
                    :alt="g.name"
                    class="gd-similar-img"
                  />
                  <div class="gd-similar-body">
                    <div class="gd-similar-info">
                      <p class="gd-similar-title">{{ g.name }}</p>
                      <small class="gd-similar-meta">
                        <span v-if="g.genres?.[0]">{{ g.genres[0].name }}</span>
                        <span v-if="g.genres?.[0] && g.released"> • </span>
                        <span v-if="g.released">{{
                          g.released.split("-")[0]
                        }}</span>
                      </small>
                    </div>
                    <span
                      v-if="g.metacritic"
                      class="gd-similar-mc"
                      :class="
                        g.metacritic >= 75
                          ? 'mc-green'
                          : g.metacritic >= 50
                            ? 'mc-yellow'
                            : 'mc-red'
                      "
                    >
                      {{ g.metacritic }}
                    </span>
                  </div>
                </router-link>
              </div>
            </div>

            <!-- REVIEWS (Moved Above Discover) -->
            <div class="gd-section mb-5">
              <div class="gd-review-header">
                <div>
                  <h2 class="gd-section-title" style="font-size: 2rem">
                    Community Reviews
                  </h2>
                  <p
                    class="gd-review-subtitle text-muted"
                    style="margin-top: -10px; margin-bottom: 20px"
                  >
                    Share your thoughts and help other players decide.
                  </p>
                </div>
              </div>
              <ReviewSection :game-id="game.id" :game-title="game.name" />
            </div>

            <!-- Discover More -->
            <div v-if="discoverMoreGames.length" class="gd-section mb-5">
              <h2 class="gd-section-title">More Games to Discover</h2>
              <div class="gd-similar-grid">
                <router-link
                  v-for="g in discoverMoreGames"
                  :key="g.id"
                  :to="`/games/${g.id}`"
                  class="gd-similar-card"
                >
                  <img
                    v-lazy-img="g.background_image"
                    :alt="g.name"
                    class="gd-similar-img"
                  />
                  <div class="gd-similar-body">
                    <div class="gd-similar-info">
                      <p class="gd-similar-title">{{ g.name }}</p>
                      <small class="gd-similar-meta">
                        <span v-if="g.genres?.[0]">{{ g.genres[0].name }}</span>
                        <span v-if="g.genres?.[0] && g.released"> • </span>
                        <span v-if="g.released">{{
                          g.released.split("-")[0]
                        }}</span>
                      </small>
                    </div>
                    <span
                      v-if="g.metacritic"
                      class="gd-similar-mc"
                      :class="
                        g.metacritic >= 75
                          ? 'mc-green'
                          : g.metacritic >= 50
                            ? 'mc-yellow'
                            : 'mc-red'
                      "
                    >
                      {{ g.metacritic }}
                    </span>
                  </div>
                </router-link>
              </div>
            </div>

            <!-- Recent Releases -->
            <div v-if="recentGames.length" class="gd-section mb-5">
              <h2 class="gd-section-title">Recent Releases</h2>
              <div class="gd-similar-grid">
                <router-link
                  v-for="g in recentGames"
                  :key="g.id"
                  :to="`/games/${g.id}`"
                  class="gd-similar-card"
                >
                  <img
                    v-lazy-img="g.background_image"
                    :alt="g.name"
                    class="gd-similar-img"
                  />
                  <div class="gd-similar-body">
                    <div class="gd-similar-info">
                      <p class="gd-similar-title">{{ g.name }}</p>
                      <small class="gd-similar-meta">
                        <span v-if="g.genres?.[0]">{{ g.genres[0].name }}</span>
                        <span v-if="g.genres?.[0] && g.released"> • </span>
                        <span v-if="g.released">{{
                          g.released.split("-")[0]
                        }}</span>
                      </small>
                    </div>
                    <span
                      v-if="g.metacritic"
                      class="gd-similar-mc"
                      :class="
                        g.metacritic >= 75
                          ? 'mc-green'
                          : g.metacritic >= 50
                            ? 'mc-yellow'
                            : 'mc-red'
                      "
                    >
                      {{ g.metacritic }}
                    </span>
                  </div>
                </router-link>
              </div>
            </div>
          </div>

          <!-- ── RIGHT: Sidebar ── -->
          <div class="col-lg-4">
            <div class="gd-sidebar">
              <!-- Metacritic Score -->
              <div v-if="game.metacritic" class="gd-mc-card mb-3">
                <div class="gd-mc-score" :class="metacriticClass">
                  {{ game.metacritic }}
                </div>
                <div class="gd-mc-info">
                  <strong>Metacritic Score</strong>
                  <small class="d-block text-muted">{{
                    metacriticLabel
                  }}</small>
                </div>
              </div>

              <!-- Actions -->
              <div
                class="gd-actions mb-4 p-3 profile-glass-card rounded-4 border border-secondary border-opacity-25"
                style="background: var(--bg-surface)"
              >
                <!-- Price display -->
                <div class="text-center mb-3">
                  <template v-if="fakeDiscount > 0">
                    <div
                      class="d-flex align-items-center justify-content-center gap-2 mb-1"
                    >
                      <span class="gd-discount-badge"
                        >-{{ fakeDiscount }}%</span
                      >
                      <span class="gd-original-price">${{ fakePrice }}</span>
                    </div>
                    <span class="fs-2 fw-bold" style="color: var(--text-primary);"
                      >${{ discountedPrice }}</span
                    >
                  </template>
                  <template v-else>
                    <span class="fs-2 fw-bold" style="color: var(--text-primary);"
                      >${{ fakePrice }}</span
                    >
                  </template>
                </div>

                <button
                  class="btn btn-primary text-white w-100 mb-2 py-2 fw-bold"
                  @click="buyNow"
                  aria-label="Buy Now"
                >
                  <i class="bi bi-credit-card-fill me-2"></i> Buy Now
                </button>

                <button
                  class="btn w-100 mb-3 py-2 fw-bold"
                  style="border: 1px solid var(--border-glass); color: var(--text-primary);"
                  @click="addToCart"
                  aria-label="Add to Cart"
                >
                  <i class="bi bi-cart-plus-fill me-2"></i> Add to Cart
                </button>

                <!-- Trailer button -->
                <button
                  v-if="hasTrailer"
                  class="btn btn-outline-secondary w-100 mb-3 py-2"
                  @click="showTrailerModal = true"
                  aria-label="Watch Trailer"
                >
                  ▶ Watch Trailer
                </button>

                <div class="d-flex gap-2">
                  <a
                    v-if="game.website"
                    :href="game.website"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="btn btn-sm btn-dark flex-grow-1 gd-action-btn border-secondary"
                    aria-label="Official Website"
                  >
                    <i class="bi bi-globe me-1"></i> Website
                  </a>
                  <button
                    class="btn btn-sm btn-dark flex-grow-1 gd-action-btn border-secondary"
                    @click="addToFavorites"
                    aria-label="Add to wishlist"
                  >
                    <i class="bi bi-star-fill text-warning me-1"></i> Wishlist
                  </button>
                </div>

                <!-- Status toast -->
                <transition name="fav-fade">
                  <div
                    v-if="favStatus.visible"
                    class="fav-status-msg mt-3"
                    :class="`fav-status-${favStatus.type}`"
                    role="status"
                    aria-live="polite"
                  >
                    {{ favStatus.message }}
                  </div>
                </transition>

                <!-- Store links -->
                <div v-if="game.stores?.length" class="gd-stores mt-2">
                  <small
                    class="text-muted d-block mb-2"
                    style="
                      font-size: 0.75rem;
                      text-transform: uppercase;
                      letter-spacing: 0.5px;
                    "
                    >Available On</small
                  >
                  <div class="d-flex flex-wrap gap-2">
                    <a
                      v-for="s in game.stores"
                      :key="s.id"
                      :href="s.url || '#'"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="gd-store-btn"
                      :aria-label="`Buy on ${s.store.name}`"
                    >
                      {{ s.store.name }}
                    </a>
                  </div>
                </div>
              </div>

              <!-- Details table -->
              <div class="gd-details-card mb-3">
                <h5 class="gd-details-heading">Game Info</h5>

                <div class="gd-detail-row" v-if="developerNames !== '—'">
                  <span class="gd-detail-label">Developer</span>
                  <span class="gd-detail-value">{{ developerNames }}</span>
                </div>
                <div class="gd-detail-row" v-if="publisherNames !== '—'">
                  <span class="gd-detail-label">Publisher</span>
                  <span class="gd-detail-value">{{ publisherNames }}</span>
                </div>
                <div class="gd-detail-row" v-if="game.released">
                  <span class="gd-detail-label">Release</span>
                  <span class="gd-detail-value">{{
                    formatDate(game.released)
                  }}</span>
                </div>
                <div class="gd-detail-row" v-if="game.playtime">
                  <span class="gd-detail-label">Avg Playtime</span>
                  <span class="gd-detail-value">{{ game.playtime }}h</span>
                </div>
                <div class="gd-detail-row" v-if="game.esrb_rating">
                  <span class="gd-detail-label">ESRB</span>
                  <span class="gd-detail-value">{{
                    game.esrb_rating.name
                  }}</span>
                </div>
                <div class="gd-detail-row" v-if="game.ratings_count">
                  <span class="gd-detail-label">Total Votes</span>
                  <span class="gd-detail-value">{{
                    game.ratings_count.toLocaleString()
                  }}</span>
                </div>
              </div>

              <!-- CheapShark Deals -->
              <div class="gd-deals-card" v-if="deals.length || dealsLoading">
                <h5 class="gd-details-heading">Compare Prices</h5>
                <div v-if="dealsLoading" class="gd-deals-loading">
                  Searching stores…
                </div>
                <div v-else>
                  <a
                    v-for="deal in deals"
                    :key="deal.dealID"
                    :href="`https://www.cheapshark.com/redirect?dealID=${deal.dealID}`"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="gd-deal-row"
                    :class="{ cheapest: cheapestDeal?.dealID === deal.dealID }"
                  >
                    <div class="gd-deal-store">
                      <span
                        class="gd-deal-cheapest-badge"
                        v-if="cheapestDeal?.dealID === deal.dealID"
                        >BEST</span
                      >
                      {{ storeName(deal.storeID) }}
                    </div>
                    <div class="gd-deal-prices">
                      <span
                        v-if="
                          parseFloat(deal.normalPrice) >
                          parseFloat(deal.salePrice)
                        "
                        class="gd-deal-original"
                        >${{ parseFloat(deal.normalPrice).toFixed(2) }}</span
                      >
                      <span class="gd-deal-sale"
                        >${{ parseFloat(deal.salePrice).toFixed(2) }}</span
                      >
                      <span
                        v-if="parseFloat(deal.savings) > 0"
                        class="gd-deal-savings"
                        >-{{ Math.round(deal.savings) }}%</span
                      >
                    </div>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Lightbox with prev/next navigation -->
    <transition name="lb">
      <div
        v-if="lightboxSrc"
        class="gd-lightbox"
        @click.self="closeLightbox"
        role="dialog"
        aria-modal="true"
        aria-label="Screenshot preview"
      >
        <button
          class="gd-lb-close"
          @click.stop="closeLightbox"
          aria-label="Close"
        >
          ✕
        </button>
        <button
          class="gd-lb-nav gd-lb-prev"
          @click.stop="lightboxPrev"
          aria-label="Previous screenshot"
        >
          ‹
        </button>
        <img
          :src="lightboxSrc"
          alt="Screenshot enlarged"
          class="gd-lb-img"
          @click.stop
        />
        <button
          class="gd-lb-nav gd-lb-next"
          @click.stop="lightboxNext"
          aria-label="Next screenshot"
        >
          ›
        </button>
        <div class="gd-lb-counter" aria-live="polite">
          {{ lightboxIndex + 1 }} / {{ screenshots.length }}
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* ── Loading ──────────────────────────────── */
.gd-loader {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
.gd-loader-inner {
  text-align: center;
}
.gd-spinner {
  width: 48px;
  height: 48px;
  border: 3px solid rgba(124, 58, 237, 0.2);
  border-top-color: #7c3aed;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* ── Hero ──────────────────────────────────── */
.gd-hero {
  position: relative;
  min-height: 380px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  isolation: isolate;
}
.gd-hero-bg {
  position: absolute;
  inset: 0;
  overflow: hidden;
  animation: gdFadeIn 1s ease-out forwards;
}
.gd-hero-bg img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  filter: blur(2px) brightness(0.35) saturate(0.7);
  transform: scale(1.05);
  display: block;
}
.gd-hero-overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      to top,
      var(--bg-deep) 0%,
      rgba(5, 7, 15, 0.6) 50%,
      rgba(5, 7, 15, 0.2) 100%
    ),
    linear-gradient(to right, rgba(5, 7, 15, 0.7) 0%, transparent 60%);
}
.gd-hero-content {
  position: relative;
  z-index: 2;
  padding-bottom: 32px;
  width: 100%;
}
.gd-back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.75);
  text-decoration: none;
  font-size: 0.88rem;
  font-weight: 600;
  padding: 8px 14px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.12);
  margin-bottom: 28px;
  transition: all 0.2s;
  margin-top: 20px;
  backdrop-filter: blur(8px);
}
.gd-back-btn:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.14);
  border-color: rgba(255, 255, 255, 0.25);
}

.gd-hero-bottom {
  display: flex;
  align-items: flex-end;
  gap: 28px;
  flex-wrap: wrap;
}
.gd-cover {
  width: 180px;
  height: 120px;
  object-fit: cover;
  border-radius: 10px;
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.7);
  flex-shrink: 0;
  border: 2px solid rgba(255, 255, 255, 0.1);
  animation: gdSlideUp 0.6s ease-out forwards;
  animation-delay: 0.1s;
  opacity: 0;
  transform: translateY(20px);
}
.gd-hero-info {
  flex: 1;
  min-width: 240px;
  animation: gdFadeIn 0.8s ease-out forwards;
  animation-delay: 0.3s;
  opacity: 0;
}
.gd-title {
  font-size: clamp(1.6rem, 4vw, 2.8rem);
  font-weight: 900;
  color: #fff;
  margin-bottom: 12px;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 20px rgba(0, 0, 0, 0.8);
  line-height: 1.1;
}

@keyframes gdFadeIn {
  to {
    opacity: 1;
  }
}
@keyframes gdSlideUp {
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Genre/ESRB badges */
.gd-badge-genre {
  padding: 3px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(124, 58, 237, 0.3);
  border: 1px solid rgba(124, 58, 237, 0.4);
  color: #c4b5fd;
}
.gd-badge-esrb {
  padding: 3px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  background: var(--border-glass);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
}

/* Star rating bar */
.gd-rating-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  flex-wrap: wrap;
}
.gd-stars {
  width: 120px;
  height: 8px;
  background: var(--border-glass);
  border-radius: 4px;
  overflow: hidden;
}
.gd-stars-fill {
  height: 100%;
  background: linear-gradient(90deg, #f59e0b, #fbbf24);
  border-radius: 4px;
  transition: width 0.6s ease;
}
.gd-rating-text {
  font-size: 0.85rem;
  color: var(--text-primary);
  font-weight: 600;
}
.gd-rating-count {
  font-size: 0.75rem;
  color: var(--text-muted);
  font-weight: 400;
  margin-left: 4px;
}

/* Metacritic score badge */
.gd-metacritic {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 900;
  flex-shrink: 0;
}
.mc-green {
  background: #15803d;
  color: #fff;
}
.mc-yellow {
  background: #a16207;
  color: #fff;
}
.mc-red {
  background: #b91c1c;
  color: #fff;
}
.mc-grey {
  background: #374151;
  color: #9ca3af;
}

/* Platform chips */
.gd-platform-chip {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  padding: 4px 10px;
  border-radius: 20px;
  background: var(--border-glass);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  white-space: nowrap;
}
.gd-platform-logo {
  width: 16px;
  height: 16px;
  object-fit: contain;
  flex-shrink: 0;
}

/* ── Body Layout ──────────────────────────── */
.gd-body {
  padding-top: 32px;
  padding-bottom: 60px;
}

/* ── Screenshots ──────────────────────────── */
.gd-shot-main {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  cursor: zoom-in;
  background: var(--bg-glass);
  margin-bottom: 10px;
}
.gd-shot-main-img {
  width: 100%;
  height: 380px;
  object-fit: cover;
  display: block;
  transition: filter 0.2s ease;
}
.gd-shot-main:hover .gd-shot-main-img {
  filter: brightness(0.85);
}
.gd-shot-zoom-hint {
  position: absolute;
  bottom: 14px;
  right: 14px;
  background: rgba(0, 0, 0, 0.6);
  color: var(--text-primary);
  font-size: 0.72rem;
  padding: 4px 12px;
  border-radius: 20px;
  backdrop-filter: blur(4px);
  opacity: 0;
  transition: opacity 0.2s;
  display: flex;
  gap: 12px;
  align-items: center;
}
.gd-shot-counter {
  color: var(--text-muted);
}
.gd-shot-main:hover .gd-shot-zoom-hint {
  opacity: 1;
}

.gd-shot-strip {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: thin;
  scrollbar-color: rgba(124, 58, 237, 0.3) transparent;
}
.gd-shot-thumb {
  flex: 0 0 100px;
  height: 64px;
  border-radius: 6px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s ease;
  opacity: 0.6;
}
.gd-shot-thumb:hover {
  opacity: 0.85;
}
.gd-shot-thumb.active {
  border-color: var(--primary);
  opacity: 1;
  box-shadow: 0 0 12px rgba(124, 58, 237, 0.5);
}
.gd-shot-thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

/* ── Section blocks ──────────────────────── */
.gd-section {
  background: var(--bg-surface);
  border: 1px solid var(--border-glass);
  border-radius: 16px;
  padding: 32px;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}
.gd-section-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-glass);
  letter-spacing: 0.02em;
}

/* ── Description ──────────────────────────── */
.gd-description {
  font-size: 0.98rem;
  line-height: 1.9;
  color: var(--text-secondary);
  white-space: pre-wrap;
  max-width: 72ch;
}

/* ── Tags ─────────────────────────────────── */
.gd-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.gd-tag {
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
  background: rgba(124, 58, 237, 0.1);
  border: 1px solid rgba(124, 58, 237, 0.2);
  color: var(--text-secondary);
  transition: all 0.2s ease;
  cursor: default;
}
.gd-tag:hover {
  background: rgba(124, 58, 237, 0.22);
  border-color: rgba(124, 58, 237, 0.4);
  color: var(--text-primary);
}

/* ── Similar games grid ───────────────────── */
.gd-similar-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 10px;
}
.gd-similar-card {
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--border-glass);
  text-decoration: none;
  background: var(--bg-glass);
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  display: block;
}
.gd-similar-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(124, 58, 237, 0.35);
  border-color: rgba(124, 58, 237, 0.4);
}
.gd-similar-img {
  width: 100%;
  height: 80px;
  object-fit: cover;
  display: block;
}
.gd-similar-body {
  padding: 8px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 6px;
}
.gd-similar-title {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 2px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.gd-similar-meta {
  font-size: 0.7rem;
  color: var(--text-muted);
}
.gd-similar-info {
  flex: 1;
  overflow: hidden;
}
.gd-similar-mc {
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}

/* ── Sidebar ──────────────────────────────── */
.gd-sidebar {
  position: sticky;
  top: 80px;
}

/* Metacritic card */
.gd-mc-card {
  display: flex;
  align-items: center;
  gap: 16px;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  padding: 16px 20px;
}
.gd-mc-score {
  font-size: 2rem;
  font-weight: 900;
  width: 60px;
  height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Actions */
.gd-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  transition: all 0.25s ease;
}
.gd-action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
}
.gd-action-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
  flex-shrink: 0;
}

.gd-store-btn {
  display: inline-block;
  padding: 4px 12px;
  font-size: 0.72rem;
  border-radius: 20px;
  background: var(--border-glass);
  border: 1px solid var(--border-glass);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s ease;
}
.gd-store-btn:hover {
  background: rgba(124, 58, 237, 0.15);
  border-color: rgba(124, 58, 237, 0.35);
  color: var(--primary-light);
}

/* Details card */
.gd-details-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  overflow: hidden;
}
.gd-details-heading {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--text-muted);
  padding: 14px 18px 10px;
  margin: 0;
  border-bottom: 1px solid var(--border-glass);
}
.gd-detail-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  padding: 10px 18px;
  border-bottom: 1px solid var(--border-subtle);
  font-size: 0.85rem;
}
.gd-detail-row:last-child {
  border-bottom: none;
}
.gd-detail-label {
  color: var(--text-muted);
  flex-shrink: 0;
}
.gd-detail-value {
  color: var(--text-primary);
  font-weight: 600;
  text-align: right;
}

/* ── Lightbox ─────────────────────────────── */
.gd-lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 24px;
  cursor: zoom-out;
}
.gd-lb-img {
  max-width: 92vw;
  max-height: 88vh;
  border-radius: 12px;
  box-shadow: 0 32px 80px rgba(0, 0, 0, 0.8);
  cursor: default;
}
.gd-lb-close {
  position: absolute;
  top: 20px;
  right: 24px;
  background: var(--border-glass);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.gd-lb-close:hover {
  background: var(--border-subtle);
}

/* Lightbox nav */
.gd-lb-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  background: var(--border-glass);
  border: 1px solid var(--border-subtle);
  color: var(--text-primary);
  border-radius: 50%;
  width: 48px;
  height: 48px;
  font-size: 1.8rem;
  cursor: pointer;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 1;
}
.gd-lb-nav:hover {
  background: var(--border-subtle);
}
.gd-lb-prev {
  left: 16px;
}
.gd-lb-next {
  right: 16px;
}
.gd-lb-counter {
  position: absolute;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.6);
  color: var(--text-primary);
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 0.82rem;
  backdrop-filter: blur(4px);
}

/* Trailer thumbnail button */
.gd-trailer-thumb {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  cursor: pointer;
  background: #000;
}
.gd-trailer-thumb-img {
  width: 100%;
  height: 360px;
  object-fit: cover;
  display: block;
  filter: brightness(0.6);
  transition: filter 0.3s;
}
.gd-trailer-thumb:hover .gd-trailer-thumb-img {
  filter: brightness(0.4);
}
.gd-trailer-play-btn {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  color: #fff;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  transition: all 0.2s;
}
.gd-play-icon {
  width: 72px;
  height: 72px;
  background: rgba(124, 58, 237, 0.85);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.8rem;
  box-shadow: 0 8px 32px rgba(124, 58, 237, 0.5);
  transition:
    transform 0.25s,
    box-shadow 0.25s;
}
.gd-trailer-thumb:hover .gd-play-icon {
  transform: scale(1.1);
  box-shadow: 0 12px 40px rgba(124, 58, 237, 0.7);
}

/* Discount badge in sidebar */
.gd-discount-badge {
  display: inline-block;
  background: #22c55e;
  color: #fff;
  font-size: 0.75rem;
  font-weight: 800;
  padding: 3px 8px;
  border-radius: 6px;
}
.gd-original-price {
  font-size: 0.9rem;
  color: var(--text-muted);
  text-decoration: line-through;
}

/* System Requirements */
.gd-sysreq-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
}
@media (max-width: 640px) {
  .gd-sysreq-grid {
    grid-template-columns: 1fr;
  }
}
.gd-sysreq-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  margin-bottom: 10px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border-glass);
}
.gd-sysreq-text {
  font-size: 0.78rem;
  line-height: 1.7;
  color: var(--text-secondary);
  white-space: pre-wrap;
  font-family: var(--font-family);
  margin: 0;
  word-break: break-word;
}

/* CheapShark Deals */
.gd-deals-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  overflow: hidden;
}
.gd-deals-loading {
  padding: 16px 18px;
  font-size: 0.82rem;
  color: var(--text-muted);
  font-style: italic;
}
.gd-deal-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 18px;
  border-bottom: 1px solid var(--border-subtle);
  text-decoration: none;
  transition: background 0.15s;
  gap: 8px;
}
.gd-deal-row:last-child {
  border-bottom: none;
}
.gd-deal-row:hover {
  background: rgba(124, 58, 237, 0.08);
}
.gd-deal-row.cheapest {
  background: rgba(34, 197, 94, 0.06);
}
.gd-deal-store {
  font-size: 0.83rem;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 7px;
}
.gd-deal-cheapest-badge {
  font-size: 0.58rem;
  font-weight: 800;
  background: #22c55e;
  color: #fff;
  padding: 2px 6px;
  border-radius: 4px;
  letter-spacing: 0.06em;
}
.gd-deal-prices {
  display: flex;
  align-items: center;
  gap: 6px;
}
.gd-deal-original {
  font-size: 0.75rem;
  color: var(--text-muted);
  text-decoration: line-through;
}
.gd-deal-sale {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-primary);
}
.gd-deal-savings {
  font-size: 0.65rem;
  font-weight: 800;
  background: #22c55e;
  color: #fff;
  padding: 1px 5px;
  border-radius: 4px;
}

.fav-fade-enter-active,
.fav-fade-leave-active {
  transition: all 0.3s ease;
}
.fav-fade-enter-from,
.fav-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

/* Responsive */
@media (max-width: 768px) {
  .gd-hero {
    min-height: 280px;
  }
  .gd-cover {
    width: 120px;
    height: 80px;
  }
  .gd-title {
    font-size: 1.4rem;
  }
  .gd-shot-main-img {
    height: 220px;
  }
  .gd-similar-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  .gd-sidebar {
    position: static;
  }
}
</style>
