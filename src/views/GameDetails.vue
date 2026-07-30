<script>
import { inject } from "vue";
import { auth, db } from "../firebase";
import { backendApi } from "../services/api";
import { trackUserActivity } from "../services/tracking";
import { onAuthStateChanged } from "firebase/auth";
import { collection, query, where, getDocs, addDoc } from "firebase/firestore";
import ReviewSection from "../components/ReviewSection.vue";
import TrailerModal from "../components/TrailerModal.vue";
import { cartState } from "../services/cart";
import { getGameState } from "../services/gameState";
import { mapState } from "pinia";
import { useAuthStore } from "../stores/useAuthStore";
import { useWishlistStore } from "../stores/useWishlistStore";
import { STORE_NAMES, storeName, metacriticClass, formatDate, platformIcon } from "../composables/useGameUtils";

// STORE_NAMES is now imported from useGameUtils — single source of truth.

export default {
  components: { ReviewSection, TrailerModal },

  setup() {
    const toast = inject("toast");
    return { toast, storeName, metacriticClass, formatDate, platformIcon };
  },

  data() {
    return {
      game: null,
      screenshots: [],
      trailers: [],
      similarGames: [],
      loading: true,
      activeShot: 0,
      lightboxSrc: null,
      lightboxIndex: 0,
      favStatus: { visible: false, message: "", type: "success" },
      discoverMoreGames: [],
      recentGames: [],
      carouselInterval: null,
      showFullDescription: false,
      showTrailerModal: false,
      deals: [],
      dealsLoading: false,
      isZoomed: false,
      touchStartX: 0,
      formattedMinReq: "",
      formattedRecReq: "",
    };
  },

  computed: {
    // Auth & wishlist state from centralised stores
    ...mapState(useAuthStore, ["currentUser"]),
    ...mapState(useWishlistStore, ["wishlistedIds"]),

    metacriticLabel() {
      const s = this.game?.metacritic;
      if (!s) return null;
      if (s >= 90) return "Universal Acclaim";
      if (s >= 75) return "Generally Favorable";
      if (s >= 50) return "Mixed or Average";
      if (s >= 40) return "Generally Unfavorable";
      return "Overwhelming Dislike";
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

    gameStateInfo() {
      return getGameState(this.game);
    },

    displayPrice() {
      if (!this.game) return 0;
      return this.gameStateInfo.formattedPrice;
    },

    displayDiscount() {
      if (!this.game || this.gameStateInfo.isFree || !this.gameStateInfo.isReleased) return 0;
      const roll = this.game.id % 4;
      if (roll === 0) return 40;
      if (roll === 1) return 25;
      return 0;
    },

    discountedPrice() {
      const price = parseFloat(this.displayPrice);
      const disc = this.displayDiscount;
      if (!disc || isNaN(price)) return null;
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

    groupedPlatforms() {
      if (!this.game?.platforms?.length) return {};

      const groups = {
        PC: [],
        PlayStation: [],
        Xbox: [],
        Nintendo: [],
        Mobile: [],
        Other: [],
      };

      this.game.platforms.forEach((p) => {
        const name = p.platform?.name || "";
        if (!name) return;

        const lowerName = name.toLowerCase();
        if (
          lowerName.includes("pc") ||
          lowerName.includes("windows") ||
          lowerName.includes("mac") ||
          lowerName.includes("linux")
        ) {
          groups.PC.push(name);
        } else if (
          lowerName.includes("playstation") ||
          lowerName.includes("ps vita") ||
          lowerName.includes("psp")
        ) {
          groups.PlayStation.push(name);
        } else if (lowerName.includes("xbox")) {
          groups.Xbox.push(name);
        } else if (
          lowerName.includes("nintendo") ||
          lowerName.includes("switch") ||
          lowerName.includes("wii") ||
          lowerName.includes("gamecube") ||
          lowerName.includes("game boy") ||
          lowerName.includes("ds") ||
          lowerName.includes("nes") ||
          lowerName.match(/\bnes\b/) ||
          lowerName.match(/\bsnes\b/)
        ) {
          groups.Nintendo.push(name);
        } else if (
          lowerName.includes("ios") ||
          lowerName.includes("android") ||
          lowerName.includes("mobile")
        ) {
          groups.Mobile.push(name);
        } else {
          groups.Other.push(name);
        }
      });

      // Remove empty groups
      for (const key in groups) {
        if (groups[key].length === 0) {
          delete groups[key];
        } else {
          // Sort platforms alphabetically or keep as is? Let's sort alphabetically
          groups[key].sort((a, b) => a.localeCompare(b));
        }
      }

      return groups;
    },

    mockDLCs() {
      if (!this.game || !this.gameStateInfo.isReleased || this.gameStateInfo.isFree) return [];
      const basePrice = parseFloat(this.displayPrice) || 29.99;
      return [
        {
          id: 1,
          name: "Digital Deluxe Edition Upgrade",
          price: (basePrice * 0.4).toFixed(2),
          discount: 0
        },
        {
          id: 2,
          name: "Original Soundtrack",
          price: "9.99",
          discount: 0
        },
        {
          id: 3,
          name: "Season Pass",
          price: (basePrice * 0.8).toFixed(2),
          discount: 15
        }
      ];
    },

    mockEngine() {
      if (!this.game) return "Custom Engine";
      const id = this.game.id;
      if (id % 3 === 0) return "Unreal Engine 5";
      if (id % 5 === 0) return "Unity";
      if (id % 2 === 0) return "Decima Engine";
      return "Proprietary Engine";
    },

    hasMultiplayer() {
      return this.game?.tags?.some(t => ['multiplayer', 'co-op', 'online'].includes(t.slug));
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
      const gameId = String(this.game.id);
      if (this.wishlistedIds.has(gameId)) {
        this.showFavStatus("Already in your wishlist!", "warning");
        return;
      }
      const wishlistStore = useWishlistStore();
      const added = await wishlistStore.addToWishlist(this.game, null);
      if (added) {
        this.showFavStatus("Added to wishlist!", "success");
      } else {
        this.showFavStatus("Already in your wishlist!", "warning");
      }
    },

    openLightbox(src, index) {
      this.lightboxSrc = src;
      this.lightboxIndex = index ?? this.activeShot;
      this.isZoomed = false;
      this.stopCarousel();
    },
    closeLightbox() {
      this.lightboxSrc = null;
      this.isZoomed = false;
      this.startCarousel();
    },
    lightboxPrev() {
      if (!this.screenshots.length) return;
      this.lightboxIndex =
        (this.lightboxIndex - 1 + this.screenshots.length) %
        this.screenshots.length;
      this.lightboxSrc = this.screenshots[this.lightboxIndex].image;
      this.activeShot = this.lightboxIndex;
      this.isZoomed = false;
    },
    lightboxNext() {
      if (!this.screenshots.length) return;
      this.lightboxIndex = (this.lightboxIndex + 1) % this.screenshots.length;
      this.lightboxSrc = this.screenshots[this.lightboxIndex].image;
      this.activeShot = this.lightboxIndex;
      this.isZoomed = false;
    },
    onLightboxKey(e) {
      if (e.key === "Escape") this.closeLightbox();
      if (e.key === "ArrowLeft") this.lightboxPrev();
      if (e.key === "ArrowRight") this.lightboxNext();
    },
    toggleZoom() {
      this.isZoomed = !this.isZoomed;
    },
    onTouchStart(e) {
      this.touchStartX = e.changedTouches[0].screenX;
    },
    onTouchEnd(e) {
      const touchEndX = e.changedTouches[0].screenX;
      if (this.touchStartX - touchEndX > 50) this.lightboxNext();
      if (this.touchStartX - touchEndX < -50) this.lightboxPrev();
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
      const finalPrice = this.discountedPrice || this.displayPrice;
      cartState.add({
        id: this.game.id,
        name: this.game.name,
        price: finalPrice,
        originalPrice: this.displayPrice,
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
        const gameRes = await backendApi.get(`/games/${id}`);
        this.game = gameRes.data;
        this.screenshots = this.game.screenshots || [];
        this.trailers = this.game.trailers || [];

        const genreSlug = this.game.genres?.[0]?.slug;

        const today = new Date();
        const past = new Date(today);
        past.setMonth(past.getMonth() - 6);
        const dateStr = `${past.toISOString().split("T")[0]},${today.toISOString().split("T")[0]}`;

        const discoverPromise = genreSlug
          ? backendApi.get("/games", {
              params: { genres: genreSlug, ordering: "-added", page_size: 14 },
            })
          : Promise.resolve({ data: { results: [] } });

        const recentPromise = backendApi.get("/games", {
          params: { dates: dateStr, ordering: "-released", page_size: 6 },
        });

        const [discoverRes, recentRes] = await Promise.all([
          discoverPromise,
          recentPromise,
        ]);

        const allDiscover = (discoverRes.data.results || []).filter((g) => g.id !== Number(id));
        this.similarGames = allDiscover.slice(0, 6);
        this.discoverMoreGames = allDiscover.slice(6, 12);
        this.recentGames = recentRes.data.results || [];

        document.title = `${this.game.name} | GameHub`;
        window.scrollTo({ top: 0, behavior: "smooth" });
        this.startCarousel();

        // Fetch CheapShark deals (non-blocking) if game is released and paid
        if (this.gameStateInfo.isReleased && !this.gameStateInfo.isFree) {
          this.fetchDeals(this.game.name);
        }

        // Track user path for recommendations
        if (this.currentUser) {
          trackUserActivity("view", this.game);
        }
        
        this.processSysReqs();
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
        const res = await backendApi.get("/deals", {
          params: {
            title: title.substring(0, 30), // CheapShark title search
            page_size: 5,
            sort_by: "Price",
          },
        });
        this.deals = (res.data.results || []).filter((d) => d.title && d.salePrice);
      } catch {
        // Silently fail — not critical
      } finally {
        this.dealsLoading = false;
      }
    },

    async processSysReqs() {
      this.formattedMinReq = "";
      this.formattedRecReq = "";
      
      const reqs = this.pcRequirements;
      if (!reqs) return;

      const formatText = async (text) => {
        if (!text) return "";
        const hasNonEnglish = /[^\x00-\x7F]/.test(text);
        const hasEnglish = /[a-zA-Z]/.test(text);

        if (hasNonEnglish && !hasEnglish) {
          try {
            const res = await backendApi.post('/games/format-sysreq', { text });
            return res.data.formatted_text;
          } catch (e) {
            console.error("AI sysreq formatting failed", e);
          }
        }

        let formatted = text.replace(/(Minimum:|Recommended:|OS:|Processor:|Memory:|Graphics:|Video Card:|Storage:|Hard Drive:|Sound Card:|DirectX:|Network:|Additional Notes:|Other requirements:|Partner Requirements:)/gi, '\n$1');
        formatted = formatted.trim().replace(/\r\n/g, '\n').replace(/\n{2,}/g, '\n');
        formatted = formatted.replace(/([a-zA-Z0-9\s:.,\-+)(]+)\n([^\x00-\x7F]+)/g, '$1<br><br>$2');
        
        const lines = formatted.split('\n');
        const result = lines.map(line => {
          if (line.trim() === '') return '';
          line = line.replace(/^([A-Za-z\s]+:|[\u4e00-\u9fa5]+:|[\u0400-\u04FF]+:)/, '<strong>$1</strong>');
          return `<li style="margin-bottom: 4px;">${line}</li>`;
        });
        
        return `<ul style="list-style-type: none; padding-left: 0; margin-bottom: 0;">${result.join('')}</ul>`;
      };

      if (reqs.minimum) {
        this.formattedMinReq = await formatText(reqs.minimum);
      }
      if (reqs.recommended) {
        this.formattedRecReq = await formatText(reqs.recommended);
      }
    },
  },

  mounted() {
    document.addEventListener("keydown", this.onLightboxKey);
  },

  beforeUnmount() {
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
          <div class="d-flex justify-content-between align-items-center mb-4">
            <router-link to="/games" class="gd-back-btn d-inline-block">
              ← Back to Games
            </router-link>
            <!-- Store-like dynamic particles or badges -->
            <div v-if="game?.id" class="badge bg-primary bg-opacity-25 text-primary border border-primary border-opacity-50 rounded-pill px-3 py-2 shadow-sm d-flex align-items-center gap-2">
              <i class="bi bi-shield-check"></i> GameHub Verified
            </div>
          </div>

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
                <span v-for="g in genreNames" :key="g" class="gd-badge-genre">{{
                  g
                }}</span>
                <span v-if="game.esrb_rating" class="gd-badge-esrb">{{
                  game.esrb_rating.name
                }}</span>
                <span
                  v-if="game.released"
                  class="gd-badge-esrb"
                  style="background: rgba(255, 255, 255, 0.15)"
                  ><i class="bi bi-calendar3"></i>
                  {{ game.released.split("-")[0] }}</span
                >
              </div>

              <h1 class="gd-title display-3 fw-bold mb-3 text-primary-var">
                {{ game.name }}
              </h1>

              <!-- Rating bar & Platforms -->
              <div
                class="gd-rating-row d-flex align-items-center flex-wrap gap-4 mb-4"
              >
                <template v-if="gameStateInfo.isReleased">
                  <div v-if="game.rating" class="d-flex align-items-center gap-2">
                    <div class="gd-stars">
                      <div
                        class="gd-stars-fill"
                        :style="{ width: ratingPercent + '%' }"
                      ></div>
                    </div>
                    <span
                      class="gd-rating-text fs-5 text-primary-var fw-bold m-0"
                      style="opacity: 1"
                    >
                      {{ game.rating.toFixed(1) }}/5
                    </span>
                  </div>

                  <div
                    v-if="game.metacritic"
                    class="d-flex align-items-center gap-2"
                  >
                    <div
                      class="gd-metacritic fs-5 d-flex align-items-center justify-content-center"
                      :class="metacriticClass(game?.metacritic)"
                      style="
                        width: 44px;
                        height: 44px;
                        border-radius: 50%;
                        box-shadow: 0 0 15px rgba(0, 0, 0, 0.5);
                      "
                    >
                      {{ game.metacritic }}
                    </div>
                    <span class="text-primary-var fw-bold">Metacritic</span>
                  </div>
                </template>
                <template v-else>
                  <div class="d-flex align-items-center gap-2">
                    <span class="badge bg-secondary bg-opacity-50 text-white fs-6 py-2 px-3 border border-secondary border-opacity-25 rounded-pill">
                      Not Yet Rated
                    </span>
                  </div>
                </template>

                <!-- Platform chips -->
                <div class="d-flex flex-wrap gap-2">
                  <span
                    v-for="p in platforms.slice(0, 5)"
                    :key="p.name"
                    class="gd-platform-chip border-0 bg-surface-var bg-opacity-50 text-primary-var shadow-sm"
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
              <div v-if="gameStateInfo.state !== 'UNKNOWN'" class="d-flex flex-wrap gap-3 mt-4">
                <!-- RELEASED -->
                <template v-if="gameStateInfo.isReleased">
                  <button
                    class="gd-hero-btn-primary btn btn-primary btn-lg fw-bold px-5 shadow-sm text-primary-var"
                    @click="buyNow"
                    aria-label="Buy Now"
                  >
                    <i class="bi bi-lightning-charge-fill me-2"></i> Buy Now — ${{
                      discountedPrice || displayPrice
                    }}
                  </button>

                  <button
                    class="gd-hero-btn-secondary btn btn-lg fw-bold px-4 shadow-sm"
                    @click="addToCart"
                    aria-label="Add to Cart"
                  >
                    <i class="bi bi-cart-plus-fill me-2"></i> Add to Cart
                  </button>
                </template>

                <!-- FREE -->
                <template v-else-if="gameStateInfo.isFree">
                  <button
                    class="gd-hero-btn-primary btn btn-success btn-lg fw-bold px-5 shadow-sm text-primary-var"
                    aria-label="Play Free"
                  >
                    <i class="bi bi-play-circle-fill me-2"></i> Play Free
                  </button>
                  <button
                    class="gd-hero-btn-secondary btn btn-lg fw-bold px-4 shadow-sm"
                    aria-label="Download"
                  >
                    <i class="bi bi-download me-2"></i> Download
                  </button>
                </template>

                <!-- COMING SOON / TBA -->
                <template v-else>
                  <button
                    class="gd-hero-btn-primary btn btn-primary btn-lg fw-bold px-5 shadow-sm text-primary-var"
                    @click="addToFavorites"
                    aria-label="Add to wishlist"
                  >
                    <i class="bi bi-heart-fill me-2"></i> Wishlist
                  </button>
                  <button
                    v-if="gameStateInfo.isComingSoon"
                    class="gd-hero-btn-secondary btn btn-lg fw-bold px-4 shadow-sm"
                  >
                    <i class="bi bi-bell-fill me-2"></i> Notify Me
                  </button>
                  <button
                    v-else
                    class="gd-hero-btn-secondary btn btn-lg fw-bold px-4 shadow-sm"
                  >
                    <i class="bi bi-bookmark-plus-fill me-2"></i> Follow
                  </button>
                </template>

                <button
                  v-if="gameStateInfo.isReleased || gameStateInfo.isFree"
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
            <div
              v-if="hasTrailer"
              class="gd-section"
              style="margin-bottom: var(--section-gap)"
            >
              <h2 class="gd-section-title mb-4">
                <i class="bi bi-film me-2 text-primary"></i> Gameplay Trailer
              </h2>
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
            <div class="gd-section" style="margin-bottom: var(--section-gap)">
              <h2 class="gd-section-title mb-4">
                <i class="bi bi-card-text me-2 text-primary"></i> About this
                game
              </h2>
              <div
                class="gd-desc-container"
                :class="{ 'is-expanded': showFullDescription }"
              >
                <div
                  class="gd-description"
                  v-html="game.description || game.description_raw || game.about || 'No description available.'"
                ></div>
                <div class="gd-desc-fade" v-if="!showFullDescription"></div>
              </div>
              <button
                class="btn btn-outline-secondary w-100 mt-3 fw-bold"
                @click="showFullDescription = !showFullDescription"
              >
                {{ showFullDescription ? "Show Less" : "Read More" }}
              </button>
            </div>

            <!-- Tags -->
            <div
              v-if="game.tags?.length"
              class="gd-section"
              style="margin-bottom: var(--section-gap)"
            >
              <h2 class="gd-section-title mb-4">
                <i class="bi bi-tags-fill me-2 text-primary"></i> Tags
              </h2>
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
              class="gd-section"
              style="margin-bottom: var(--section-gap)"
            >
              <h2 class="gd-section-title mb-4">
                <i class="bi bi-pc-display me-2 text-primary"></i> System
                Requirements
              </h2>
              <div class="gd-sysreq-grid">
                <div v-if="pcRequirements.minimum" class="gd-sysreq-col">
                  <div class="gd-sysreq-label">Minimum</div>
                  <div class="gd-sysreq-text" v-html="formattedMinReq || pcRequirements.minimum"></div>
                </div>
                <div v-if="pcRequirements.recommended" class="gd-sysreq-col">
                  <div class="gd-sysreq-label">Recommended</div>
                  <div class="gd-sysreq-text" v-html="formattedRecReq || pcRequirements.recommended"></div>
                </div>
              </div>
            </div>

            <!-- Detailed Platforms -->
            <div
              v-if="Object.keys(groupedPlatforms).length"
              class="gd-section"
              style="margin-bottom: var(--section-gap)"
            >
              <h2 class="gd-section-title mb-4">
                <i class="bi bi-hdd-network-fill me-2 text-primary"></i>
                Available On
              </h2>
              <div class="d-flex flex-column gap-3">
                <div
                  v-for="(platforms, category) in groupedPlatforms"
                  :key="category"
                  class="d-flex flex-wrap align-items-baseline gap-3"
                >
                  <span
                    class="text-muted-light fw-bold"
                    style="min-width: 100px"
                    >{{ category }}</span
                  >
                  <div class="gd-tags d-flex flex-wrap gap-2">
                    <span
                      v-for="platformName in platforms"
                      :key="platformName"
                      class="gd-tag text-decoration-none bg-surface-var text-primary-var border-0 opacity-75 m-0"
                      style="cursor: default"
                    >
                      {{ platformName }}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <!-- Similar Games / Series -->
            <div
              v-if="similarGames.length"
              class="gd-section"
              style="margin-bottom: var(--section-gap)"
            >
              <h2 class="gd-section-title mb-4">
                <i class="bi bi-collection-play-fill me-2 text-primary"></i>
                More in This Series
              </h2>
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
            <div
              class="gd-section gd-review-section-tint"
              style="margin-bottom: var(--section-gap)"
            >
              <div class="gd-review-header mb-4">
                <div>
                  <h2 class="gd-section-title">
                    <i class="bi bi-chat-quote-fill me-2 text-primary"></i>
                    Community Reviews
                  </h2>
                  <p
                    v-if="gameStateInfo.isReleased"
                    class="gd-review-subtitle text-muted"
                    style="margin-top: -10px; margin-bottom: 20px"
                  >
                    Share your thoughts and help other players decide.
                  </p>
                  <p v-else class="gd-review-subtitle text-muted" style="margin-top: -10px; margin-bottom: 20px">
                    Reviews will open after release.
                  </p>
                </div>
              </div>
              <ReviewSection v-if="gameStateInfo.isReleased" :game-id="game.id" :game-title="game.name" />
              <div v-else class="text-center p-5 bg-black bg-opacity-25 rounded-4 border border-secondary border-opacity-25">
                <i class="bi bi-lock-fill text-muted fs-1 mb-3"></i>
                <h4 class="text-primary-var fw-bold">Coming after release</h4>
                <p class="text-muted mb-4">You'll be able to rate and review this game once it launches.</p>
                <div class="d-flex justify-content-center gap-3">
                  <button class="btn btn-primary fw-bold px-4" @click="addToFavorites"><i class="bi bi-heart-fill me-2"></i>Wishlist</button>
                  <button v-if="gameStateInfo.isComingSoon" class="btn btn-outline-secondary fw-bold px-4"><i class="bi bi-bell-fill me-2"></i>Notify Me</button>
                </div>
              </div>
            </div>

            <!-- Discover More -->
            <div
              v-if="discoverMoreGames.length"
              class="gd-section"
              style="margin-bottom: var(--section-gap)"
            >
              <h2 class="gd-section-title mb-4">
                <i class="bi bi-compass-fill me-2 text-primary"></i> Similar
                Games
              </h2>
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
            <div
              v-if="recentGames.length"
              class="gd-section"
              style="margin-bottom: var(--section-gap)"
            >
              <h2 class="gd-section-title mb-4">
                <i class="bi bi-fire me-2 text-primary"></i> {{ gameStateInfo.isReleased ? 'Trending This Week' : 'Most Wishlisted' }}
              </h2>
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
              <div
                v-if="game.metacritic && gameStateInfo.isReleased"
                class="gd-mc-card mb-4 profile-glass-card p-4 rounded-4 d-flex align-items-center gap-3"
                style="background: var(--bg-surface)"
              >
                <div class="gd-mc-score" :class="metacriticClass(game?.metacritic)">
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
                v-if="gameStateInfo.state !== 'UNKNOWN'"
                class="gd-actions mb-4 p-0 profile-glass-card rounded-4 border border-secondary border-opacity-25 overflow-hidden"
                style="background: var(--bg-surface)"
              >
                <!-- Price display Block -->
                <div
                  class="text-center p-4 border-bottom border-secondary border-opacity-25 bg-black bg-opacity-10"
                >
                  <template v-if="gameStateInfo.isReleased">
                    <template v-if="displayDiscount > 0">
                      <div
                        class="d-inline-block px-3 py-1 bg-danger text-primary-var fw-bold rounded-pill mb-2 shadow-sm"
                      >
                        SALE -{{ displayDiscount }}%
                      </div>
                      <div
                        class="d-flex align-items-center justify-content-center gap-3"
                      >
                        <span class="fs-1 fw-bold text-primary-var"
                          >${{ discountedPrice }}</span
                        >
                        <span class="fs-4 text-muted text-decoration-line-through"
                          >${{ displayPrice }}</span
                        >
                      </div>
                    </template>
                    <template v-else>
                      <span class="fs-1 fw-bold text-primary-var"
                        >${{ displayPrice }}</span
                      >
                    </template>
                  </template>
                  
                  <template v-else-if="gameStateInfo.isFree">
                    <span class="fs-1 fw-bold text-success">Free to Play</span>
                  </template>
                  
                  <template v-else-if="gameStateInfo.isComingSoon">
                    <span class="fs-2 fw-bold text-primary-var">Coming Soon</span>
                    <small class="d-block text-muted mt-1" v-if="gameStateInfo.releaseDate">Release: {{ formatDate(gameStateInfo.releaseDate) }}</small>
                    <small class="d-block text-info fw-bold mt-2" v-if="gameStateInfo.countdownDays > 0">Releases in {{ gameStateInfo.countdownDays }} days</small>
                    <small class="d-block text-info fw-bold mt-2" v-else-if="gameStateInfo.countdownDays === 0">Releases today!</small>
                  </template>
                  
                  <template v-else-if="gameStateInfo.isTba">
                    <span class="fs-2 fw-bold text-primary-var">Coming Soon</span>
                    <small class="d-block text-muted mt-1">Release Date: To Be Announced</small>
                  </template>
                </div>

                <!-- Sidebar Buy Actions Block -->
                <div
                  class="p-4 border-bottom border-secondary border-opacity-25"
                >
                  <template v-if="gameStateInfo.isReleased">
                    <button
                      class="gd-buy-now-btn w-100 mb-3"
                      @click="buyNow"
                      aria-label="Buy Now"
                    >
                      <i class="bi bi-lightning-charge-fill me-2"></i>
                      Buy Now — ${{ discountedPrice || displayPrice }}
                    </button>

                    <button
                      class="gd-add-cart-btn w-100 mb-3"
                      @click="addToCart"
                      aria-label="Add to Cart"
                    >
                      <i class="bi bi-cart-plus me-2"></i> Add to Cart
                    </button>
                  </template>

                  <template v-else-if="gameStateInfo.isFree">
                    <button
                      class="btn btn-success w-100 py-2 mb-3 fw-bold"
                      aria-label="Play Free"
                    >
                      <i class="bi bi-play-circle-fill me-2"></i> Play Free
                    </button>
                  </template>

                  <template v-else-if="gameStateInfo.isComingSoon">
                    <button
                      class="btn btn-outline-primary w-100 py-2 mb-3 fw-bold"
                      aria-label="Notify Me"
                    >
                      <i class="bi bi-bell-fill me-2"></i> Notify Me
                    </button>
                  </template>

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
                <div
                  class="p-3 text-center border-bottom border-secondary border-opacity-25"
                  style="background: rgba(255, 255, 255, 0.02)"
                >
                  <button
                    class="gd-wishlist-btn w-100 d-flex justify-content-between align-items-center"
                    @click="addToFavorites"
                    aria-label="Add to wishlist"
                  >
                    <span>Add to your Wishlist</span>
                    <i class="bi bi-heart fs-5"></i>
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
                <div
                  v-if="game.stores?.length"
                  class="p-4 bg-black bg-opacity-10"
                >
                  <small
                    class="text-muted d-block mb-3 fw-bold text-uppercase"
                    style="letter-spacing: 0.08em"
                    >{{ gameStateInfo.isReleased ? 'Available On' : 'Available at launch on' }}</small
                  >
                  <div class="d-flex flex-column gap-2">
                    <a
                      v-for="s in game.stores"
                      :key="s.id"
                      :href="s.url || (s.store?.domain ? 'https://' + s.store.domain : '#')"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="gd-store-link d-flex align-items-center justify-content-between p-3 rounded-3 text-decoration-none"
                      style="
                        background: var(--bg-glass);
                        border: 1px solid var(--border-glass);
                      "
                    >
                      <span
                        class="fw-semibold"
                        style="color: var(--text-primary); font-size: 0.88rem"
                        >{{ s.store.name }}</span
                      >
                      <i
                        class="bi bi-box-arrow-up-right"
                        style="color: var(--text-muted); font-size: 0.8rem"
                      ></i>
                    </a>
                  </div>
                </div>
              </div>

              <!-- Details table -->
              <div
                class="gd-details-card mb-4 profile-glass-card p-4 rounded-4"
                style="background: var(--bg-surface)"
              >
                <h5 class="gd-details-heading mb-4">
                  <i class="bi bi-info-circle-fill text-primary me-2"></i> Game
                  Info
                </h5>

                <div class="gd-meta-list">
                  <div class="gd-meta-row" v-if="developerNames !== '—'">
                    <span class="gd-meta-label">Developer</span>
                    <span class="gd-meta-value">{{ developerNames }}</span>
                  </div>
                  <div class="gd-meta-row" v-if="publisherNames !== '—'">
                    <span class="gd-meta-label">Publisher</span>
                    <span class="gd-meta-value">{{ publisherNames }}</span>
                  </div>
                  <div class="gd-meta-row" v-if="game.released">
                    <span class="gd-meta-label">Release Date</span>
                    <span class="gd-meta-value">{{
                      formatDate(game.released)
                    }}</span>
                  </div>
                  <div class="gd-meta-row" v-if="game.playtime && gameStateInfo.isReleased">
                    <span class="gd-meta-label">Avg. Playtime</span>
                    <span class="gd-meta-value">~{{ game.playtime }} hrs</span>
                  </div>
                  <div class="gd-meta-row" v-if="game.esrb_rating">
                    <span class="gd-meta-label">Age Rating</span>
                    <span class="gd-meta-value">{{
                      game.esrb_rating.name
                    }}</span>
                  </div>
                  <div class="gd-meta-row" v-if="gameStateInfo.isReleased">
                    <span class="gd-meta-label">Engine</span>
                    <span class="gd-meta-value">{{ mockEngine }} <span class="text-muted" style="cursor:help" title="Simulated Data">*</span></span>
                  </div>
                  <div class="gd-meta-row" v-if="gameStateInfo.isReleased">
                    <span class="gd-meta-label">Languages</span>
                    <span class="gd-meta-value">English, French, Spanish <span class="text-muted text-decoration-underline" style="font-size: 0.75rem; cursor: help" title="Simulated Data">+6 more</span></span>
                  </div>
                  <div class="gd-meta-row" v-if="game.ratings_count && gameStateInfo.isReleased">
                    <span class="gd-meta-label">Total Reviews</span>
                    <span class="gd-meta-value">{{
                      game.ratings_count.toLocaleString()
                    }}</span>
                  </div>
                </div>
              </div>

              <!-- Features (Trust Signals) -->
              <div
                class="gd-features-card mb-4 profile-glass-card p-4 rounded-4"
                style="background: var(--bg-surface)"
              >
                <h5 class="gd-details-heading mb-4">
                  <i class="bi bi-controller text-primary me-2"></i> Features
                </h5>
                <div class="d-flex flex-column gap-3">
                  <div class="d-flex align-items-center gap-3 gd-feature-item">
                    <i class="bi bi-person-fill text-muted fs-5"></i>
                    <span class="fw-semibold">Single-player</span>
                  </div>
                  <div class="d-flex align-items-center gap-3 gd-feature-item" v-if="hasMultiplayer">
                    <i class="bi bi-people-fill text-muted fs-5"></i>
                    <span class="fw-semibold">Multiplayer</span>
                  </div>
                  <div class="d-flex align-items-center gap-3 gd-feature-item">
                    <i class="bi bi-dpad-fill text-muted fs-5"></i>
                    <span class="fw-semibold">Full Controller Support</span>
                  </div>
                  <div class="d-flex align-items-center gap-3 gd-feature-item">
                    <i class="bi bi-cloud-check-fill text-muted fs-5"></i>
                    <span class="fw-semibold">Cloud Saves</span>
                  </div>
                  <div class="d-flex align-items-center gap-3 gd-feature-item">
                    <i class="bi bi-trophy-fill text-muted fs-5"></i>
                    <span class="fw-semibold">Achievements ({{ game ? (game.id % 50) + 20 : 0 }})</span>
                  </div>
                </div>
              </div>

              <!-- Packages and DLC -->
              <div
                v-if="mockDLCs.length"
                class="gd-dlc-card profile-glass-card p-4 rounded-4 mt-4 mb-4"
              >
                <h5 class="gd-details-heading mb-4">
                  <i class="bi bi-box-seam-fill text-primary me-2"></i> Packages & DLC
                </h5>
                <div class="d-flex flex-column gap-3">
                  <div
                    v-for="dlc in mockDLCs"
                    :key="dlc.id"
                    class="d-flex justify-content-between align-items-center p-3 rounded-3"
                    style="background: rgba(255,255,255,0.03); border: 1px solid var(--border-glass);"
                  >
                    <div>
                      <span class="fw-semibold d-block" style="font-size:0.9rem">{{ dlc.name }}</span>
                    </div>
                    <div class="d-flex align-items-center gap-2">
                      <span v-if="dlc.discount" class="badge bg-danger rounded-pill">-{{ dlc.discount }}%</span>
                      <span class="fw-bold">${{ (dlc.price * (1 - dlc.discount/100)).toFixed(2) }}</span>
                      <button class="btn btn-sm btn-outline-primary px-2 py-1 rounded-3 ms-1" title="Add to Cart">
                        <i class="bi bi-cart-plus"></i>
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <!-- CheapShark Deals -->
              <div
                class="gd-deals-card profile-glass-card p-4 rounded-4 mt-4"
                v-if="gameStateInfo.isReleased && !gameStateInfo.isFree && (deals.length || dealsLoading)"
              >
                <h5 class="gd-details-heading mb-4">
                  <i class="bi bi-tags-fill text-primary me-2"></i> Compare
                  Prices
                </h5>
                <div
                  v-if="dealsLoading"
                  class="gd-deals-loading text-center py-4 text-muted"
                >
                  <div class="spinner-border spinner-border-sm me-2"></div>
                  Searching stores…
                </div>
                <div v-else>
                  <table
                    class="table table-borderless table-hover align-middle mb-0"
                    style="color: var(--text-primary)"
                  >
                    <thead>
                      <tr
                        class="border-bottom border-secondary border-opacity-25"
                      >
                        <th class="text-muted fw-normal pb-3 px-0">Store</th>
                        <th class="text-muted fw-normal pb-3 text-end">
                          Price
                        </th>
                        <th class="pb-3 px-0"></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr
                        v-for="deal in deals"
                        :key="deal.dealID"
                        :class="{
                          'bg-success bg-opacity-10':
                            cheapestDeal?.dealID === deal.dealID,
                        }"
                      >
                        <td
                          class="fw-bold py-3 px-2 rounded-start"
                          :class="{
                            'text-success':
                              cheapestDeal?.dealID === deal.dealID,
                          }"
                        >
                          <span
                            v-if="cheapestDeal?.dealID === deal.dealID"
                            class="badge bg-success me-2"
                            >Best Deal</span
                          >
                          {{ storeName(deal.storeID) }}
                        </td>
                        <td
                          class="text-end py-3 fw-bold"
                          :class="{
                            'text-success':
                              cheapestDeal?.dealID === deal.dealID,
                          }"
                        >
                          ${{ deal.salePrice }}
                        </td>
                        <td class="text-end py-3 px-2 rounded-end">
                          <a
                            :href="`https://www.cheapshark.com/redirect?dealID=${deal.dealID}`"
                            target="_blank"
                            class="btn btn-sm rounded-pill px-3"
                            :class="
                              cheapestDeal?.dealID === deal.dealID
                                ? 'btn-success text-primary-var'
                                : 'btn-outline-secondary'
                            "
                          >
                            {{
                              cheapestDeal?.dealID === deal.dealID
                                ? "Buy"
                                : "View"
                            }}
                          </a>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <div
                class="gd-stats-card profile-glass-card p-4 rounded-4 mt-4"
                style="background: var(--bg-surface)"
              >
                <h5 class="gd-details-heading mb-4">
                  <i class="bi bi-people-fill text-primary me-2"></i> Community
                  Stats
                </h5>
                <div class="row g-4">
                  <div class="col-6" v-if="gameStateInfo.isReleased">
                    <span class="gh-meta-label"
                      ><i class="bi bi-star-fill text-warning me-1"></i>
                      Average</span
                    >
                    <span class="fw-bold" style="color: var(--text-primary)"
                      >{{ game.rating ? game.rating.toFixed(1) : "4.6" }} /
                      5</span
                    >
                  </div>
                  <div class="col-6" v-if="gameStateInfo.isReleased">
                    <span class="gh-meta-label"
                      ><i class="bi bi-chat-text-fill text-info me-1"></i>
                      Reviews</span
                    >
                    <span class="fw-bold" style="color: var(--text-primary)">{{
                      (game.ratings_count || 1254).toLocaleString()
                    }}</span>
                  </div>
                  <div class="col-6">
                    <span class="gh-meta-label"
                      ><i class="bi bi-heart-fill text-danger me-1"></i>
                      Wishlists</span
                    >
                    <span class="fw-bold" style="color: var(--text-primary)">{{
                      (game.added || 3912).toLocaleString()
                    }}</span>
                  </div>
                  <div class="col-6">
                    <span class="gh-meta-label"
                      ><i class="bi bi-collection-fill text-success me-1"></i>
                      Libraries</span
                    >
                    <span class="fw-bold" style="color: var(--text-primary)">{{
                      (game.added_by_status?.owned || 1884).toLocaleString()
                    }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <!-- You Might Also Like (Recommendations) -->
        <div class="mt-5 pt-4 mb-3" v-if="discoverMoreGames && discoverMoreGames.length">
          <h4 class="mb-4 fw-bold" style="color: var(--text-primary)">
            You Might Also Like
          </h4>
          <div class="gd-recommendation-carousel pb-3">
            <router-link
              v-for="g in discoverMoreGames"
              :key="g.id"
              :to="`/games/${g.id}`"
              class="gd-rec-card text-decoration-none"
            >
              <div class="gd-rec-img-wrapper">
                <img :src="g.background_image" :alt="g.name" class="gd-rec-img" />
              </div>
              <div class="gd-rec-info p-3">
                <h6 class="gd-rec-title fw-bold mb-1 text-truncate" :title="g.name">{{ g.name }}</h6>
                <div class="d-flex justify-content-between align-items-center mt-2">
                  <span class="gd-rec-genre text-muted small text-truncate" style="max-width: 60%">{{ g.genres?.[0]?.name || 'Game' }}</span>
                  <span class="gd-rec-price fw-bold text-success small">${{ ((g.id % 40) + 10 + 0.99).toFixed(2) }}</span>
                </div>
              </div>
            </router-link>
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
        @touchstart="onTouchStart"
        @touchend="onTouchEnd"
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
        <div class="gd-lb-img-container" :class="{'is-zoomed': isZoomed}" @click.stop="toggleZoom">
          <img
            :src="lightboxSrc"
            alt="Screenshot enlarged"
            class="gd-lb-img"
          />
        </div>
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
        <div class="gd-lb-hint">Click image to zoom</div>
      </div>
    </transition>

    <!-- Footer Transition -->
    <div class="gd-footer-transition"></div>
  </div>
</template>

<style>
.gd-lb-img-container {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 90vw;
  max-height: 90vh;
  transition: transform 0.3s ease;
  cursor: zoom-in;
}
.gd-lb-img-container.is-zoomed {
  transform: scale(1.5);
  cursor: zoom-out;
}
.gd-lb-hint {
  position: absolute;
  bottom: 60px;
  color: rgba(255,255,255,0.7);
  font-size: 0.85rem;
  pointer-events: none;
}
</style>


