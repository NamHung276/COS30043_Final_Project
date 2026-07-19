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
      const allPlatforms = (this.game?.platforms || []).map((p) => ({
        name: p.platform.name,
        icon: this.platformIcon(p.platform.name),
      }));
      const unique = [];
      const seen = new Set();
      for (const p of allPlatforms) {
        if (!seen.has(p.icon)) {
          seen.add(p.icon);
          unique.push(p);
        }
      }
      return unique;
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
      if (n.includes("pc") || n.includes("windows")) return "/game_logo/pc.svg";
      if (n.includes("playstation")) return "/game_logo/playstation_logo.png";
      if (n.includes("xbox")) return "/game_logo/xbox_logo.png";
      if (n.includes("nintendo") || n.includes("switch"))
        return "/game_logo/nintendo_logo.png";
      if (n.includes("mac")) return "/game_logo/macos.png";
      if (n.includes("linux")) return "/game_logo/linux.png";
      if (n.includes("android") || n.includes("ios") || n.includes("mobile"))
        return "/game_logo/mobile.svg";
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
        <div class="container gd-hero-content pb-5">
          <router-link to="/games" class="gd-back-btn mb-4 d-inline-block"> ← Back to Games </router-link>

          <div class="gd-hero-bottom align-items-end">
            <!-- Cover thumbnail -->
            <img
              v-if="game.background_image"
              v-lazy-img="game.background_image"
              class="gd-cover shadow-lg"
              :alt="`${game.name} cover`"
            />

            <!-- Title + meta -->
            <div class="gd-hero-info w-100">
              <div class="d-flex flex-wrap gap-2 mb-3">
                <span v-for="g in genreNames" :key="g" class="gd-badge-genre">{{ g }}</span>
                <span v-if="game.esrb_rating" class="gd-badge-esrb">{{ game.esrb_rating.name }}</span>
                <span v-if="game.released" class="gd-badge-esrb" style="background: rgba(255,255,255,0.15);"><i class="bi bi-calendar3"></i> {{ game.released.split("-")[0] }}</span>
              </div>
              
              <h1 class="gd-title display-3 fw-bold mb-3 text-white">{{ game.name }}</h1>

              <!-- Rating bar & Platforms -->
              <div class="gd-rating-row d-flex align-items-center flex-wrap gap-4 mb-4">
                <div v-if="game.rating" class="d-flex align-items-center gap-2">
                  <div class="gd-stars">
                    <div
                      class="gd-stars-fill"
                      :style="{ width: ratingPercent + '%' }"
                    ></div>
                  </div>
                  <span class="gd-rating-text fs-5 text-white fw-bold m-0" style="opacity: 1;">
                    {{ game.rating.toFixed(1) }}/5
                  </span>
                </div>
                
                <div v-if="game.metacritic" class="d-flex align-items-center gap-2">
                  <div
                    class="gd-metacritic fs-5 d-flex align-items-center justify-content-center"
                    :class="metacriticClass"
                    style="width: 44px; height: 44px; border-radius: 50%; box-shadow: 0 0 15px rgba(0,0,0,0.5);"
                  >
                    {{ game.metacritic }}
                  </div>
                  <span class="text-white fw-bold">Metacritic</span>
                </div>

                <!-- Platform chips -->
                <div class="d-flex flex-wrap gap-2">
                  <span
                    v-for="p in platforms.slice(0, 5)"
                    :key="p.name"
                    class="gd-platform-chip border-0 bg-dark bg-opacity-50 text-white shadow-sm"
                    :title="`Available on ${p.name}`"
                  >
                    <img
                      :src="p.icon"
                      :alt="`${p.name} logo`"
                      class="gd-platform-logo"
                    />
                  </span>
                </div>
              </div>
              
              <!-- Quick Actions in Hero -->
              <div class="d-flex flex-wrap gap-3 mt-4">
                <button
                  class="gd-hero-btn-primary btn btn-primary btn-lg fw-bold px-5 shadow-sm text-white"
                  @click="buyNow"
                  aria-label="Buy Now"
                >
                  <i class="bi bi-lightning-charge-fill me-2"></i> Buy Now — ${{ discountedPrice || fakePrice }}
                </button>

                <button
                  class="gd-hero-btn-secondary btn btn-lg fw-bold px-4 shadow-sm"
                  @click="addToCart"
                  aria-label="Add to Cart"
                >
                  <i class="bi bi-cart-plus-fill me-2"></i> Add to Cart
                </button>

                <button
                  class="gd-hero-btn-tertiary btn btn-lg px-4"
                  @click="addToFavorites"
                  aria-label="Add to wishlist"
                >
                  <i class="bi bi-heart me-2"></i> Wishlist
                </button>
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
            <div v-if="hasTrailer" class="gd-section" style="margin-bottom: var(--section-gap);">
              <h2 class="gd-section-title mb-4"><i class="bi bi-film me-2 text-primary"></i> Gameplay Trailer</h2>
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
            <div class="gd-section" style="margin-bottom: var(--section-gap);">
              <h2 class="gd-section-title mb-4"><i class="bi bi-card-text me-2 text-primary"></i> About this game</h2>
              <div class="gd-description" v-html="game.description || 'No description available.'"></div>
            </div>

            <!-- Tags -->
            <div v-if="game.tags?.length" class="gd-section" style="margin-bottom: var(--section-gap);">
              <h2 class="gd-section-title mb-4"><i class="bi bi-tags-fill me-2 text-primary"></i> Tags</h2>
              <div class="gd-tags d-flex flex-wrap gap-2">
                <router-link
                  v-for="tag in game.tags.slice(0, 20)"
                  :key="tag.id"
                  :to="`/games?search=${encodeURIComponent(tag.name)}`"
                  class="gd-tag text-decoration-none"
                >
                  {{ tag.name }}
                </router-link>
              </div>
            </div>

            <!-- System Requirements -->
            <div
              v-if="pcRequirements?.minimum || pcRequirements?.recommended"
              class="gd-section" style="margin-bottom: var(--section-gap);"
            >
              <h2 class="gd-section-title mb-4"><i class="bi bi-pc-display me-2 text-primary"></i> System Requirements</h2>
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
            <div v-if="similarGames.length" class="gd-section" style="margin-bottom: var(--section-gap);">
              <h2 class="gd-section-title mb-4"><i class="bi bi-collection-play-fill me-2 text-primary"></i> More in This Series</h2>
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
            <div class="gd-section gd-review-section-tint" style="margin-bottom: var(--section-gap);">
              <div class="gd-review-header mb-4">
                <div>
                  <h2 class="gd-section-title"><i class="bi bi-chat-quote-fill me-2 text-primary"></i> Community Reviews</h2>
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
            <div v-if="discoverMoreGames.length" class="gd-section" style="margin-bottom: var(--section-gap);">
              <h2 class="gd-section-title mb-4"><i class="bi bi-compass-fill me-2 text-primary"></i> 🎯 Similar Games</h2>
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
            <div v-if="recentGames.length" class="gd-section" style="margin-bottom: var(--section-gap);">
              <h2 class="gd-section-title mb-4"><i class="bi bi-fire me-2 text-primary"></i> 🔥 Trending This Week</h2>
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
              <div v-if="game.metacritic" class="gd-mc-card mb-4 profile-glass-card p-4 rounded-4 d-flex align-items-center gap-3" style="background: var(--bg-surface);">
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
                class="gd-actions mb-4 p-0 profile-glass-card rounded-4 border border-secondary border-opacity-25 overflow-hidden"
                style="background: var(--bg-surface)"
              >
                <!-- Price display Block -->
                <div class="text-center p-4 border-bottom border-secondary border-opacity-25 bg-black bg-opacity-10">
                  <template v-if="fakeDiscount > 0">
                    <div class="d-inline-block px-3 py-1 bg-danger text-white fw-bold rounded-pill mb-2 shadow-sm">
                      SALE -{{ fakeDiscount }}%
                    </div>
                    <div class="d-flex align-items-center justify-content-center gap-3">
                      <span class="fs-1 fw-bold text-primary-var">${{ discountedPrice }}</span>
                      <span class="fs-4 text-muted text-decoration-line-through">${{ fakePrice }}</span>
                    </div>
                  </template>
                  <template v-else>
                    <span class="fs-1 fw-bold text-primary-var">${{ fakePrice }}</span>
                  </template>
                </div>

                  <!-- Sidebar Buy Actions Block -->
                  <div class="p-4 border-bottom border-secondary border-opacity-25">
                    <button
                      class="gd-buy-now-btn w-100 mb-3"
                      @click="buyNow"
                      aria-label="Buy Now"
                    >
                      <i class="bi bi-lightning-charge-fill me-2"></i>
                      Buy Now — ${{ discountedPrice || fakePrice }}
                    </button>

                    <button
                      class="gd-add-cart-btn w-100 mb-3"
                      @click="addToCart"
                      aria-label="Add to Cart"
                    >
                      <i class="bi bi-cart-plus me-2"></i> Add to Cart
                    </button>

                    <button
                      v-if="hasTrailer"
                      class="btn btn-outline-secondary w-100 py-2"
                      @click="showTrailerModal = true"
                      aria-label="Watch Trailer"
                    >
                      <i class="bi bi-play-circle me-2"></i> Watch Trailer
                    </button>
                  </div>

                <!-- Wishlist Block -->
                <div class="p-3 text-center border-bottom border-secondary border-opacity-25">
                  <button
                    class="gd-wishlist-btn w-100"
                    @click="addToFavorites"
                    aria-label="Add to wishlist"
                  >
                    <i class="bi bi-heart me-2"></i> Add to Wishlist
                  </button>
                </div>
                
                <!-- Status toast -->
                <transition name="fav-fade">
                  <div
                    v-if="favStatus.visible"
                    class="fav-status-msg m-3"
                    :class="`fav-status-${favStatus.type}`"
                    role="status"
                    aria-live="polite"
                  >
                    {{ favStatus.message }}
                  </div>
                </transition>

                <!-- Store links -->
                <div v-if="game.stores?.length" class="p-4 bg-black bg-opacity-10">
                  <small class="text-muted d-block mb-3 fw-bold text-uppercase" style="letter-spacing: 0.08em;">Available On</small>
                  <div class="d-flex flex-column gap-2">
                    <a
                      v-for="s in game.stores"
                      :key="s.id"
                      :href="s.url || '#'"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="gd-store-link d-flex align-items-center justify-content-between p-3 rounded-3 text-decoration-none"
                      style="background: var(--bg-glass); border: 1px solid var(--border-glass);"
                    >
                      <span class="fw-semibold" style="color: var(--text-primary); font-size: 0.88rem;">{{ s.store.name }}</span>
                      <i class="bi bi-box-arrow-up-right" style="color: var(--text-muted); font-size: 0.8rem;"></i>
                    </a>
                  </div>
                </div>
              </div>

              <!-- Details table -->
              <div class="gd-details-card mb-4 profile-glass-card p-4 rounded-4" style="background: var(--bg-surface);">
                <h5 class="gd-details-heading mb-4"><i class="bi bi-info-circle-fill text-primary me-2"></i> Game Info</h5>

                <div class="row g-4">
                  <div class="col-6" v-if="developerNames !== '—'">
                    <span class="gh-meta-label">Developer</span>
                    <span class="fw-bold" style="color: var(--text-primary);">{{ developerNames }}</span>
                  </div>
                  <div class="col-6" v-if="publisherNames !== '—'">
                    <span class="gh-meta-label">Publisher</span>
                    <span class="fw-bold" style="color: var(--text-primary);">{{ publisherNames }}</span>
                  </div>
                  <div class="col-6" v-if="game.released">
                    <span class="gh-meta-label">Release</span>
                    <span class="fw-bold" style="color: var(--text-primary);">{{ formatDate(game.released) }}</span>
                  </div>
                  <div class="col-6" v-if="game.playtime">
                    <span class="gh-meta-label">Playtime</span>
                    <span class="fw-bold" style="color: var(--text-primary);">~{{ game.playtime }} hrs</span>
                  </div>
                  <div class="col-6" v-if="game.esrb_rating">
                    <span class="gh-meta-label">ESRB</span>
                    <span class="fw-bold" style="color: var(--text-primary);">{{ game.esrb_rating.name }}</span>
                  </div>
                  <div class="col-6" v-if="game.ratings_count">
                    <span class="gh-meta-label">Reviews</span>
                    <span class="fw-bold" style="color: var(--text-primary);">{{ game.ratings_count.toLocaleString() }}</span>
                  </div>
                </div>
              </div>

              <!-- CheapShark Deals -->
              <div class="gd-deals-card profile-glass-card p-4 rounded-4 mt-4" v-if="deals.length || dealsLoading">
                <h5 class="gd-details-heading mb-4"><i class="bi bi-tags-fill text-primary me-2"></i> Compare Prices</h5>
                <div v-if="dealsLoading" class="gd-deals-loading text-center py-4 text-muted">
                  <div class="spinner-border spinner-border-sm me-2"></div> Searching stores…
                </div>
                <div v-else>
                  <table class="table table-borderless table-hover align-middle mb-0" style="color: var(--text-primary);">
                    <thead>
                      <tr class="border-bottom border-secondary border-opacity-25">
                        <th class="text-muted fw-normal pb-3 px-0">Store</th>
                        <th class="text-muted fw-normal pb-3 text-end">Price</th>
                        <th class="pb-3 px-0"></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="deal in deals" :key="deal.dealID" :class="{ 'bg-success bg-opacity-10': cheapestDeal?.dealID === deal.dealID }">
                        <td class="fw-bold py-3 px-2 rounded-start" :class="{ 'text-success': cheapestDeal?.dealID === deal.dealID }">
                          <span v-if="cheapestDeal?.dealID === deal.dealID" class="badge bg-success me-2">Best Deal</span>
                          {{ storeName(deal.storeID) }}
                        </td>
                        <td class="text-end py-3 fw-bold" :class="{ 'text-success': cheapestDeal?.dealID === deal.dealID }">${{ deal.salePrice }}</td>
                        <td class="text-end py-3 px-2 rounded-end">
                          <a :href="`https://www.cheapshark.com/redirect?dealID=${deal.dealID}`" target="_blank" class="btn btn-sm rounded-pill px-3" :class="cheapestDeal?.dealID === deal.dealID ? 'btn-success text-white' : 'btn-outline-secondary'">
                            {{ cheapestDeal?.dealID === deal.dealID ? 'Buy' : 'View' }}
                          </a>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div class="gd-stats-card profile-glass-card p-4 rounded-4 mt-4" style="background: var(--bg-surface);">
                <h5 class="gd-details-heading mb-4">
                  <i class="bi bi-people-fill text-primary me-2"></i> Community Stats
                </h5>
                <div class="row g-4">
                  <div class="col-6">
                    <span class="gh-meta-label"><i class="bi bi-star-fill text-warning me-1"></i> Average</span>
                    <span class="fw-bold" style="color: var(--text-primary);">{{ game.rating ? game.rating.toFixed(1) : '4.6' }} / 5</span>
                  </div>
                  <div class="col-6">
                    <span class="gh-meta-label"><i class="bi bi-chat-text-fill text-info me-1"></i> Reviews</span>
                    <span class="fw-bold" style="color: var(--text-primary);">{{ (game.ratings_count || 1254).toLocaleString() }}</span>
                  </div>
                  <div class="col-6">
                    <span class="gh-meta-label"><i class="bi bi-heart-fill text-danger me-1"></i> Wishlists</span>
                    <span class="fw-bold" style="color: var(--text-primary);">{{ (game.added || 3912).toLocaleString() }}</span>
                  </div>
                  <div class="col-6">
                    <span class="gh-meta-label"><i class="bi bi-collection-fill text-success me-1"></i> Libraries</span>
                    <span class="fw-bold" style="color: var(--text-primary);">{{ (game.added_by_status?.owned || 1884).toLocaleString() }}</span>
                  </div>
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

    <!-- Footer Transition -->
    <div class="gd-footer-transition"></div>
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
  min-height: 550px;
  display: flex;
  align-items: flex-end;
  overflow: hidden;
  isolation: isolate;
  padding-top: 80px;
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
  filter: blur(8px) brightness(0.25) saturate(1.2);
  transform: scale(1.1);
  display: block;
}
.gd-hero-overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(
      to top,
      var(--bg-deep) 0%,
      rgba(5, 7, 15, 0.4) 50%,
      rgba(5, 7, 15, 0.1) 100%
    );
}
.gd-hero-content {
  position: relative;
  z-index: 2;
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
  width: 220px;
  height: 290px;
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
  height: 460px;
  object-fit: cover;
  display: block;
  transition: all 0.3s ease;
}
.gd-shot-main:hover .gd-shot-main-img {
  filter: brightness(0.85);
  transform: scale(1.03);
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

.gd-sidebar {
  position: sticky;
  top: 100px;
}

.gd-deals-card .table {
  --bs-table-bg: transparent;
  --bs-table-color: var(--text-primary);
  --bs-table-hover-bg: var(--bg-glass-hover);
  --bs-table-hover-color: var(--text-primary);
}
.gd-deals-card .table th,
.gd-deals-card .table td {
  background: transparent !important;
}
.gd-review-section-tint {
  background: rgba(124, 58, 237, 0.03);
  border: 1px solid rgba(124, 58, 237, 0.15);
}

/* ── Description ──────────────────────────── */
.gd-description {
  font-size: 1.05rem;
  line-height: 1.8;
  color: var(--text-secondary);
  max-width: 72ch;
}
.gd-description :deep(h1),
.gd-description :deep(h2),
.gd-description :deep(h3),
.gd-description :deep(h4) {
  color: var(--text-primary);
  margin-top: 1.8rem;
  margin-bottom: 0.75rem;
  font-weight: 700;
  font-size: 1.3rem;
}
.gd-description :deep(p) {
  margin-bottom: 1.25rem;
}
.gd-description :deep(ul),
.gd-description :deep(ol) {
  margin-bottom: 1.25rem;
  padding-left: 1.5rem;
}
.gd-description :deep(br) {
  content: "";
  display: block;
  margin-bottom: 0.5rem;
}

/* ── System Requirements ──────────────────── */
.gd-sysreq-text {
  max-height: 250px;
  overflow-y: auto;
  white-space: pre-wrap;
  font-size: 0.85rem;
  color: var(--text-secondary);
  background: rgba(0, 0, 0, 0.2);
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--border-glass);
}
.gd-sysreq-text::-webkit-scrollbar {
  width: 6px;
}
.gd-sysreq-text::-webkit-scrollbar-track {
  background: transparent;
}
.gd-sysreq-text::-webkit-scrollbar-thumb {
  background: var(--border-glass);
  border-radius: 10px;
}
.gd-sysreq-label {
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 8px;
  font-size: 1rem;
}
.gd-sysreq-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}
@media (min-width: 768px) {
  .gd-sysreq-grid {
    grid-template-columns: 1fr 1fr;
  }
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
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
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
  height: 140px;
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

/* ── Hero CTA Buttons ──────────────────────── */
.gd-hero-btn-primary {
  background: linear-gradient(135deg, #0ea5e9, #6366f1);
  border: none;
  border-radius: 10px;
  padding: 14px 28px;
  font-size: 1rem;
  font-weight: 700;
  letter-spacing: 0.01em;
  box-shadow: 0 4px 20px rgba(14, 165, 233, 0.4);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  color: white;
}
.gd-hero-btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(14, 165, 233, 0.55);
  filter: brightness(1.1);
  color: white;
}

.gd-hero-btn-secondary {
  background: rgba(255, 255, 255, 0.12);
  border: 1px solid rgba(255, 255, 255, 0.22);
  border-radius: 10px;
  padding: 13px 24px;
  color: white;
  backdrop-filter: blur(8px);
  transition: all 0.25s ease;
}
.gd-hero-btn-secondary:hover {
  background: rgba(255, 255, 255, 0.2);
  border-color: rgba(255, 255, 255, 0.4);
  color: white;
  transform: translateY(-2px);
}

.gd-hero-btn-tertiary {
  background: transparent;
  border: 1px solid rgba(255, 255, 255, 0.18);
  border-radius: 10px;
  padding: 13px 20px;
  color: rgba(255, 255, 255, 0.8);
  transition: all 0.25s ease;
}
.gd-hero-btn-tertiary:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.3);
  color: white;
  transform: translateY(-1px);
}

/* ── Sidebar Purchase Buttons ──────────────── */
.gd-buy-now-btn {
  display: block;
  width: 100%;
  padding: 14px 20px;
  background: linear-gradient(135deg, #0ea5e9, #6366f1);
  border: none;
  border-radius: 10px;
  color: white;
  font-weight: 700;
  font-size: 1rem;
  letter-spacing: 0.01em;
  box-shadow: 0 4px 16px rgba(14, 165, 233, 0.35);
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
}
.gd-buy-now-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(14, 165, 233, 0.5);
  filter: brightness(1.08);
}

.gd-add-cart-btn {
  display: block;
  width: 100%;
  padding: 11px 20px;
  background: var(--bg-glass-hover);
  border: 1px solid var(--border-glass);
  border-radius: 10px;
  color: var(--text-primary);
  font-weight: 600;
  font-size: 0.92rem;
  transition: all 0.2s ease;
  cursor: pointer;
}
.gd-add-cart-btn:hover {
  border-color: var(--primary);
  background: rgba(14, 165, 233, 0.08);
  color: var(--primary-light);
  transform: translateY(-1px);
}

.gd-wishlist-btn {
  display: block;
  width: 100%;
  padding: 10px 20px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-weight: 600;
  font-size: 0.88rem;
  cursor: pointer;
  transition: all 0.2s ease;
}
.gd-wishlist-btn:hover {
  color: var(--danger);
}

/* ── Screenshot zoom hint ──────────────────── */
.gd-shot-zoom-hint {
  position: absolute;
  bottom: 14px;
  right: 14px;
  background: rgba(0, 0, 0, 0.65);
  color: var(--text-primary);
  font-size: 0.72rem;
  padding: 5px 12px;
  border-radius: 20px;
  backdrop-filter: blur(8px);
  opacity: 0;
  transition: opacity 0.2s;
  display: flex;
  gap: 10px;
  align-items: center;
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
    grid-template-columns: 1fr;
  }
  .gd-sidebar {
    position: static;
  }
}

.gd-footer-transition {
  height: 100px;
  background: linear-gradient(to bottom, var(--bg-deep) 0%, transparent 100%);
  margin-top: -60px;
  margin-bottom: 80px;
  pointer-events: none;
}
</style>
