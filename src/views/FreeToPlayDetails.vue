<script>
import { inject } from "vue";
import { auth, db } from "../firebase";
import { freeToGameApi } from "../services/api";
import { onAuthStateChanged } from "firebase/auth";
import {
  collection,
  query,
  where,
  getDocs,
  addDoc,
  serverTimestamp,
} from "firebase/firestore";
import ReviewSection from "../components/ReviewSection.vue";

export default {
  components: { ReviewSection },

  setup() {
    const toast = inject("toast");
    return { toast };
  },

  data() {
    return {
      game: null,
      loading: true,
      currentUser: null,
      activeShot: 0,
      lightboxSrc: null,
      favStatus: { visible: false, message: "", type: "success" },
      discoverMoreGames: [],
      recentGames: [],
      carouselInterval: null,
    };
  },

  computed: {
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
        const { data } = await freeToGameApi.get("/game", { params: { id } });
        this.game = data;

        const genre = this.game.genre ? this.game.genre.toLowerCase() : null;

        const discoverPromise = genre
          ? freeToGameApi.get("/games", { params: { category: genre } })
          : Promise.resolve({ data: [] });

        const recentPromise = freeToGameApi.get("/games", {
          params: { "sort-by": "release-date" },
        });

        const [discoverRes, recentRes] = await Promise.all([
          discoverPromise,
          recentPromise,
        ]);

        const discoverAll = (discoverRes.data || []).filter(
          (g) => g.id !== Number(id),
        );
        this.discoverMoreGames = discoverAll
          .sort(() => 0.5 - Math.random())
          .slice(0, 6);

        this.recentGames = (recentRes.data || [])
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
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      this.currentUser = user;
    });
  },

  beforeUnmount() {
    if (this.unsubscribe) this.unsubscribe();
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
              
              <h1 class="gd-title display-3 fw-bold mb-3 text-white">{{ game.title }}</h1>

              <!-- Platform chips -->
              <div class="d-flex flex-wrap gap-2 mb-4">
                <span
                  v-for="p in platforms"
                  :key="p.name"
                  class="gd-platform-chip border-0 bg-dark bg-opacity-50 text-white shadow-sm"
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
              <div class="d-flex flex-wrap gap-3 mt-4">
                <a
                  v-if="game.game_url"
                  :href="game.game_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="gd-hero-btn-primary btn btn-primary btn-lg fw-bold px-5 shadow-sm text-white text-decoration-none"
                  aria-label="Play Now"
                >
                  <i class="bi bi-controller me-2"></i> Play Now (FreeToGame)
                </a>

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
            <div v-if="game.genre" class="gd-section" style="margin-bottom: var(--section-gap);">
              <h2 class="gd-section-title mb-4"><i class="bi bi-tags-fill me-2 text-primary"></i> Tags</h2>
              <div class="gd-tags d-flex flex-wrap gap-2">
                <span class="gd-tag text-decoration-none bg-dark text-white border-0 opacity-75" style="cursor: default;">{{ game.genre }}</span>
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
                  <span class="gd-detail-label">Platform</span>
                  <span class="gd-detail-value">{{ game.platform }}</span>
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


