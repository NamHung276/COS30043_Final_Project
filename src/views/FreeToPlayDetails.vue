<script>
import { inject } from "vue";
import { auth, db } from "../firebase";
import { backendApi } from "../services/api";
import { onAuthStateChanged } from "firebase/auth";
import {
  collection,
  query,
  where,
  getDocs,
  addDoc,
  serverTimestamp,
} from "firebase/firestore";
import { mapState } from "pinia";
import { useLibraryStore } from "../stores/useLibraryStore";
import { useAuthStore } from "../stores/useAuthStore";
import ReviewSection from "../components/ReviewSection.vue";

export default {
  components: { ReviewSection },

  setup() {
    const toast = inject("toast");
    return { toast };
  },

  computed: {
    ...mapState(useAuthStore, ["currentUser"]),
    ...mapState(useLibraryStore, ["purchases"]),

    isClaimed() {
      if (!this.game || !this.currentUser) return false;
      return this.purchases.some(
        (p) =>
          String(p.gameId) === String(this.game.id) &&
          p.source === "freetogame",
      );
    },

    genrePills() {
      if (!this.game?.genre) return [];
      return this.game.genre
        .split(",")
        .map((g) => g.trim())
        .filter(Boolean);
    },

    heroImage() {
      if (
        this.game?.screenshots?.length &&
        this.game.screenshots[this.activeShot]
      ) {
        return this.game.screenshots[this.activeShot].image;
      }
      return this.game?.thumbnail;
    },

    platforms() {
      if (!this.game?.platform) return [];
      const parts = this.game.platform.split(",").map((s) => s.trim());
      return parts.map((p) => ({
        name: p,
        icon: this.platformIcon(p),
      }));
    },

    screenshots() {
      return this.game?.screenshots || [];
    },

    sysReqs() {
      const r = this.game?.minimum_system_requirements;
      if (!r || !Object.values(r).some((v) => v)) return null;
      return [
        { label: "OS", value: r.os },
        { label: "Processor", value: r.processor },
        { label: "Memory", value: r.memory },
        { label: "Graphics", value: r.graphics },
        { label: "Storage", value: r.storage },
      ].filter((req) => req.value && req.value !== "?");
    },
  },

  data() {
    return {
      game: null,
      loading: true,
      activeShot: 0,
      lightboxSrc: null,
      favStatus: { visible: false, message: "", type: "success" },
      discoverMoreGames: [],
      recentGames: [],
      carouselInterval: null,
      claimStatus: "idle", // idle | claiming | claimed
    };
  },

  methods: {
    platformIcon(name) {
      const n = name.toLowerCase();
      if (n.includes("pc") || n.includes("windows")) return "/game_logo/pc.svg";
      if (n.includes("browser") || n.includes("web")) return "/logo/search.svg";
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
        this.showFavStatus("Please login to add to wishlist.", "warning");
        setTimeout(() => this.$router.push("/login"), 1500);
        return;
      }
      try {
        const snap = await getDocs(
          query(
            collection(db, "favorites"),
            where("userId", "==", this.currentUser.uid),
            where("gameId", "==", this.game.id),
            where("source", "==", "freetogame"),
          ),
        );
        if (!snap.empty) {
          this.showFavStatus("⚠️ Already in your wishlist!", "warning");
          return;
        }

        await addDoc(collection(db, "favorites"), {
          userId: this.currentUser.uid,
          gameId: this.game.id,
          title: this.game.title,
          thumbnail: this.game.thumbnail,
          genre: this.game.genre,
          source: "freetogame",
          createdAt: serverTimestamp(),
        });
        this.showFavStatus("Added to wishlist!", "success");
      } catch (err) {
        console.error(err);
        this.showFavStatus("Something went wrong. Please try again.", "error");
      }
    },

    async claimFree() {
      if (!this.currentUser) {
        this.$router.push("/login");
        return;
      }
      if (this.isClaimed) {
        this.$router.push("/library");
        return;
      }
      this.claimStatus = "claiming";
      try {
        const libraryStore = useLibraryStore();
        await libraryStore.fetchPurchases();
        // Double-check to avoid duplicates from rapid clicks
        const alreadyOwned = libraryStore.purchases.some(
          (p) =>
            String(p.gameId) === String(this.game.id) &&
            p.source === "freetogame",
        );
        if (!alreadyOwned) {
          await addDoc(collection(db, "purchases"), {
            userId: this.currentUser.uid,
            gameId: String(this.game.id),
            gameName: this.game.title,
            thumbnail: this.game.thumbnail || "",
            price: 0,
            currency: "USD",
            source: "freetogame",
            gameUrl: this.game.game_url || "",
            transactionId: "FREE",
            payerName: this.currentUser.displayName || "Anonymous",
            createdAt: serverTimestamp(),
            status: "not_installed",
          });
          await libraryStore.fetchPurchases(true);
        }
        this.claimStatus = "claimed";
        this.toast?.show(`${this.game.title} added to your library!`, "success");
      } catch (err) {
        console.error("claimFree failed:", err);
        this.claimStatus = "idle";
        this.toast?.show("Something went wrong. Please try again.", "error");
      }
    },

    openLightbox(src) {
      this.lightboxSrc = src;
      this.stopCarousel();
    },
    closeLightbox() {
      this.lightboxSrc = null;
      this.startCarousel();
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

    async fetchData(id) {
      this.loading = true;
      this.game = null;
      this.activeShot = 0;

      try {
        const { data } = await backendApi.get(`/free-games/${id}`);
        this.game = data;

        const genre = this.game.genre ? this.game.genre.toLowerCase() : null;

        const discoverPromise = genre
          ? backendApi.get("/free-games", { params: { category: genre } })
          : Promise.resolve({ data: { results: [] } });

        const recentPromise = backendApi.get("/free-games", {
          params: { sort_by: "release-date" },
        });

        const [discoverRes, recentRes] = await Promise.all([
          discoverPromise,
          recentPromise,
        ]);

        const discoverAll = (discoverRes.data.results || []).filter(
          (g) => g.id !== Number(id),
        );
        this.discoverMoreGames = discoverAll
          .sort(() => 0.5 - Math.random())
          .slice(0, 6);

        this.recentGames = (recentRes.data.results || [])
          .filter((g) => g.id !== Number(id))
          .slice(0, 6);

        document.title = `${this.game.title} | GameHub`;

        window.scrollTo({ top: 0, behavior: "smooth" });
        this.startCarousel();
      } catch (err) {
        console.error(err);
      } finally {
        this.loading = false;
      }
    },
  },

  watch: {
    "$route.params.id": {
      immediate: true,
      handler(newId) {
        if (newId && this.$route.name === "FreeToPlayDetails") {
          this.fetchData(newId);
        }
      },
    },
  },

  mounted() {
    const libraryStore = useLibraryStore();
    if (this.currentUser) {
      libraryStore.fetchPurchases();
    }
  },

  beforeUnmount() {
    this.stopCarousel();
  },
};
</script>

<template>
  <div>
    <!-- ── Loading Skeleton ──────────────────────── -->
    <div v-if="loading" class="gd-skeleton-loader">
      <div class="gd-skeleton-hero"></div>
      <div class="container mt-4">
        <div class="row g-4">
          <div class="col-lg-8">
            <div
              class="gd-skeleton-box"
              style="height: 380px; margin-bottom: 32px"
            ></div>
            <div
              class="gd-skeleton-box"
              style="height: 150px; margin-bottom: 32px"
            ></div>
            <div
              class="gd-skeleton-box"
              style="height: 100px; margin-bottom: 32px"
            ></div>
          </div>
          <div class="col-lg-4">
            <div class="gd-skeleton-box" style="height: 250px"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- ── Not Found ─────────────────────────────── -->
    <div v-else-if="!game" class="container mt-4">
      <div class="alert alert-danger">Game not found.</div>
      <router-link to="/free-to-play" class="btn btn-outline-secondary"
        >← Back to Free to Play</router-link
      >
    </div>

    <!-- ── Game Page ─────────────────────────────── -->
    <div v-else>
      <!-- ══════════ CINEMATIC HERO ══════════ -->
      <div class="gd-hero">
        <!-- Blurred background art -->
        <div class="gd-hero-bg" aria-hidden="true">
          <img :src="heroImage || game.thumbnail" alt="" />
        </div>

        <!-- Gradient overlay -->
        <div class="gd-hero-overlay" aria-hidden="true"></div>

        <!-- Content -->
        <div class="container gd-hero-content pb-5">
          <router-link to="/free-to-play" class="gd-back-btn mb-4 d-inline-block">
            ← Back to Free to Play
          </router-link>

          <div class="gd-hero-bottom align-items-end">
            <!-- Cover thumbnail -->
            <img
              v-if="game.thumbnail"
              v-lazy-img="game.thumbnail"
              class="gd-cover shadow-lg"
              :alt="`${game.title} cover`"
            />

            <!-- Title + meta -->
            <div class="gd-hero-info w-100">
              <div class="d-flex flex-wrap gap-2 mb-3">
                <span class="gd-badge-genre">{{ game.genre }}</span>
                <span
                  class="gd-badge-esrb"
                  style="
                    background: rgba(74, 222, 128, 0.25);
                    color: #4ade80;
                    border-color: rgba(74, 222, 128, 0.4);
                  "
                >
                  <i class="bi bi-gift me-1"></i>Free to Play
                </span>
              </div>
              
              <h1 class="gd-title display-3 fw-bold mb-3 text-primary-var">{{ game.title }}</h1>

              <!-- Platform chips -->
              <div class="d-flex flex-wrap gap-2 mb-4">
                <span
                  v-for="p in platforms"
                  :key="p.name"
                  class="gd-platform-chip border-0 bg-surface-var bg-opacity-50 text-primary-var shadow-sm"
                  :title="`Available on ${p.name}`"
                >
                  <img
                    :src="p.icon"
                    :alt="`${p.name} logo`"
                    class="gd-platform-logo"
                  />
                  <span>{{ p.name }}</span>
                </span>
                <span
                  v-if="game.status"
                  class="gd-platform-chip border-0 shadow-sm"
                  style="
                    background: rgba(34, 197, 94, 0.15);
                    color: #86efac;
                  "
                >
                  {{ game.status }}
                </span>
              </div>

              <!-- Quick Actions in Hero -->
              <div class="d-flex flex-wrap gap-3 mt-4 align-items-center">
                <!-- State: Already Claimed → Download -->
                <button
                  v-if="isClaimed || claimStatus === 'claimed'"
                  class="ftg-claim-btn ftg-claim-btn--download btn btn-lg fw-bold px-5 shadow"
                  @click="$router.push('/library')"
                  aria-label="Go to library to download"
                >
                  <i class="bi bi-download me-2"></i> Download
                </button>

                <!-- State: Claiming in progress -->
                <button
                  v-else-if="claimStatus === 'claiming'"
                  class="ftg-claim-btn ftg-claim-btn--loading btn btn-lg fw-bold px-5"
                  disabled
                  aria-label="Claiming"
                >
                  <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Claiming...
                </button>

                <!-- State: Not yet claimed → Claim Free -->
                <button
                  v-else
                  class="ftg-claim-btn ftg-claim-btn--free btn btn-lg fw-bold px-5 shadow"
                  @click="claimFree"
                  aria-label="Claim this game for free"
                >
                  <i class="bi bi-gift-fill me-2"></i>
                  {{ currentUser ? 'Claim Free' : 'Sign In to Claim' }}
                </button>

                <button
                  class="gd-hero-btn-tertiary btn btn-lg px-4"
                  @click="addToFavorites"
                  aria-label="Add to wishlist"
                >
                  <i class="bi bi-heart me-2"></i> Wishlist
                </button>

                <a
                  v-if="game.game_url"
                  :href="game.game_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-outline-secondary btn-lg px-4 text-decoration-none"
                  aria-label="Open official page"
                >
                  <i class="bi bi-box-arrow-up-right me-1"></i> Official Site
                </a>
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
            <!-- Screenshot Viewer -->
            <div v-if="screenshots.length" class="gd-screenshots-block mb-4">
              <!-- Main featured shot -->
              <div
                class="gd-shot-main"
                @click="openLightbox(screenshots[activeShot].image)"
              >
                <img
                  v-lazy-img="screenshots[activeShot].image"
                  :alt="`${game.title} screenshot`"
                  class="gd-shot-main-img"
                />
                <div class="gd-shot-zoom-hint">
                  <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="11" cy="11" r="8"/><path d="M21 21l-4.35-4.35"/><line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/></svg>
                  <span>Enlarge</span>
                  <span class="gd-shot-counter">{{ activeShot + 1 }} / {{ screenshots.length }}</span>
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
              <div class="gd-description">
                <span v-html="game.description || 'No description available.'"></span>
              </div>
            </div>

            <!-- Tags -->
            <div v-if="genrePills.length" class="gd-section" style="margin-bottom: var(--section-gap);">
              <h2 class="gd-section-title mb-4"><i class="bi bi-tags-fill me-2 text-primary"></i> Tags</h2>
              <div class="gd-tags d-flex flex-wrap gap-2">
                <span
                  v-for="pill in genrePills"
                  :key="pill"
                  class="gd-tag text-decoration-none bg-surface-var text-primary-var border-0 opacity-75"
                  style="cursor: default;"
                >{{ pill }}</span>
              </div>
            </div>


            <!-- System Requirements -->
            <div class="gd-section" style="margin-bottom: var(--section-gap);">
              <h2 class="gd-section-title mb-4"><i class="bi bi-pc-display me-2 text-primary"></i> Minimum System Requirements</h2>
              <div class="table-responsive" v-if="sysReqs">
                <table class="table table-striped mb-0 gd-table" style="font-size: 0.85rem">
                  <tbody>
                    <tr v-for="req in sysReqs" :key="req.label">
                      <th
                        scope="row"
                        style="
                          width: 120px;
                          color: var(--text-muted);
                          font-weight: 600;
                        "
                      >
                        {{ req.label }}
                      </th>
                      <td style="color: var(--text-secondary)">
                        {{ req.value }}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
              <div v-else class="text-muted" style="font-size: 0.9rem;">
                Not specified by the developer.
              </div>
            </div>

            <!-- REVIEWS (Moved Above Discover) -->
            <div class="gd-section gd-review-section-tint" style="margin-bottom: var(--section-gap);">
              <div class="gd-review-header mb-4">
                <div>
                  <h2 class="gd-section-title"><i class="bi bi-chat-left-text me-2 text-primary"></i> Community Reviews</h2>
                  <p class="gd-review-subtitle text-muted mt-2 mb-0">
                    Share your thoughts and help other players decide.
                  </p>
                </div>
              </div>
              <ReviewSection
                :game-id="String(game.id)"
                :game-title="game.title"
              />
            </div>

            <!-- Discover More -->
            <div v-if="discoverMoreGames.length" class="gd-section" style="margin-bottom: var(--section-gap);">
              <h2 class="gd-section-title mb-4"><i class="bi bi-compass-fill me-2 text-primary"></i> Similar Games</h2>
              <div class="gd-similar-grid">
                <router-link
                  v-for="g in discoverMoreGames"
                  :key="g.id"
                  :to="`/free-to-play/${g.id}`"
                  class="gd-similar-card"
                >
                  <img
                    v-lazy-img="g.thumbnail"
                    :alt="g.title"
                    class="gd-similar-img"
                  />
                  <div class="gd-similar-body">
                    <div class="gd-similar-info">
                      <p class="gd-similar-title">{{ g.title }}</p>
                      <small class="gd-similar-meta">
                        <span v-if="g.genre">{{ g.genre }}</span>
                        <span v-if="g.genre && g.release_date"> • </span>
                        <span v-if="g.release_date">{{
                          g.release_date.split("-")[0]
                        }}</span>
                      </small>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>

            <!-- Recent Releases -->
            <div v-if="recentGames.length" class="gd-section" style="margin-bottom: var(--section-gap);">
              <h2 class="gd-section-title mb-4"><i class="bi bi-fire me-2 text-primary"></i> Trending This Week</h2>
              <div class="gd-similar-grid">
                <router-link
                  v-for="g in recentGames"
                  :key="g.id"
                  :to="`/free-to-play/${g.id}`"
                  class="gd-similar-card"
                >
                  <img
                    v-lazy-img="g.thumbnail"
                    :alt="g.title"
                    class="gd-similar-img"
                  />
                  <div class="gd-similar-body">
                    <div class="gd-similar-info">
                      <p class="gd-similar-title">{{ g.title }}</p>
                      <small class="gd-similar-meta">
                        <span v-if="g.genre">{{ g.genre }}</span>
                        <span v-if="g.genre && g.release_date"> • </span>
                        <span v-if="g.release_date">{{
                          g.release_date.split("-")[0]
                        }}</span>
                      </small>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
          </div>

          <!-- ── RIGHT: Sidebar ── -->
          <div class="col-lg-4">
            <div class="gd-sidebar">
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

              <!-- ── FREE Pricing Panel ── -->
              <div class="ftg-price-panel gd-details-card mb-4">
                <div class="ftg-price-free-label">FREE</div>
                <p class="ftg-price-subtitle">No purchase required</p>

                <!-- Claim / Download CTA (mirrored in sidebar) -->
                <button
                  v-if="isClaimed || claimStatus === 'claimed'"
                  class="ftg-claim-btn ftg-claim-btn--download btn btn-lg fw-bold w-100 shadow mb-3"
                  @click="$router.push('/library')"
                >
                  <i class="bi bi-download me-2"></i> Download
                </button>
                <button
                  v-else-if="claimStatus === 'claiming'"
                  class="ftg-claim-btn ftg-claim-btn--loading btn btn-lg fw-bold w-100 mb-3"
                  disabled
                >
                  <span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                  Claiming...
                </button>
                <button
                  v-else
                  class="ftg-claim-btn ftg-claim-btn--free btn btn-lg fw-bold w-100 shadow mb-3"
                  @click="claimFree"
                >
                  <i class="bi bi-gift-fill me-2"></i>
                  {{ currentUser ? 'Claim Free' : 'Sign In to Claim' }}
                </button>

                <div class="ftg-price-trust d-flex flex-column gap-2 mt-1">
                  <span class="ftg-trust-item"><i class="bi bi-shield-check-fill text-success me-2"></i>No credit card required</span>
                  <span class="ftg-trust-item"><i class="bi bi-infinity text-primary me-2"></i>Free to keep forever</span>
                  <span v-if="game.platform" class="ftg-trust-item">
                    <i class="bi bi-display text-muted me-2"></i>{{ game.platform }}
                  </span>
                </div>
              </div>

              <!-- Details table -->
              <div class="gd-details-card">
                <h5 class="gd-details-heading">Game Info</h5>

                <div class="gd-detail-row" v-if="game.developer">
                  <span class="gd-detail-label">Developer</span>
                  <span class="gd-detail-value">{{ game.developer }}</span>
                </div>
                <div class="gd-detail-row" v-if="game.publisher">
                  <span class="gd-detail-label">Publisher</span>
                  <span class="gd-detail-value">{{ game.publisher }}</span>
                </div>
                <div class="gd-detail-row" v-if="game.release_date">
                  <span class="gd-detail-label">Release</span>
                  <span class="gd-detail-value">{{
                    formatDate(game.release_date)
                  }}</span>
                </div>
                <div class="gd-detail-row">
                  <span class="gd-detail-label">Genre</span>
                  <span class="gd-detail-value">{{ game.genre || '—' }}</span>
                </div>
                <div class="gd-detail-row">
                  <span class="gd-detail-label">Platform</span>
                  <span class="gd-detail-value">{{ game.platform }}</span>
                </div>
                <div class="gd-detail-row" v-if="game.status">
                  <span class="gd-detail-label">Status</span>
                  <span class="gd-detail-value" style="color: #4ade80;">{{ game.status }}</span>
                </div>
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>

    <!-- ── Lightbox ───────────────────────────── -->
    <transition name="lb">
      <div
        v-if="lightboxSrc"
        class="gd-lightbox"
        @click="closeLightbox"
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
        <img
          :src="lightboxSrc"
          alt="Screenshot enlarged"
          class="gd-lb-img"
          @click.stop
        />
      </div>
    </transition>
  </div>
</template>

<style scoped>
/* ── FREE Pricing Panel ────────────────────────────────────────── */
.ftg-price-panel {
  text-align: center;
  padding: 1.75rem 1.5rem 1.5rem;
}

.ftg-price-free-label {
  font-size: 3rem;
  font-weight: 900;
  line-height: 1;
  letter-spacing: -1px;
  background: linear-gradient(135deg, #4ade80 0%, #22d3ee 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.25rem;
}

.ftg-price-subtitle {
  color: var(--text-muted, #94a3b8);
  font-size: 0.85rem;
  margin-bottom: 1.25rem;
}

.ftg-trust-item {
  font-size: 0.82rem;
  color: var(--text-secondary, #cbd5e1);
}

/* ── Claim Button States ───────────────────────────────────────── */
.ftg-claim-btn {
  border: none;
  transition: transform 0.15s ease, box-shadow 0.15s ease, opacity 0.2s;
}
.ftg-claim-btn:not(:disabled):hover {
  transform: translateY(-2px);
}
.ftg-claim-btn:not(:disabled):active {
  transform: translateY(0);
}

/* Green gradient — "Claim Free" */
.ftg-claim-btn--free {
  background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%);
  color: #fff;
  box-shadow: 0 4px 20px rgba(34, 197, 94, 0.35);
}
.ftg-claim-btn--free:hover {
  box-shadow: 0 6px 28px rgba(34, 197, 94, 0.55);
  color: #fff;
}

/* Teal gradient — "Download" */
.ftg-claim-btn--download {
  background: linear-gradient(135deg, #06b6d4 0%, #0284c7 100%);
  color: #fff;
  box-shadow: 0 4px 20px rgba(6, 182, 212, 0.35);
}
.ftg-claim-btn--download:hover {
  box-shadow: 0 6px 28px rgba(6, 182, 212, 0.55);
  color: #fff;
}

/* Muted — "Claiming..." spinner */
.ftg-claim-btn--loading {
  background: rgba(255,255,255,0.08);
  color: var(--text-muted, #94a3b8);
  cursor: not-allowed;
}
</style>
