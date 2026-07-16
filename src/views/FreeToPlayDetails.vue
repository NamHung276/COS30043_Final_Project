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
      if (n.includes("pc") || n.includes("windows")) return "/logo/pc.svg";
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
        this.showFavStatus("⭐ Added to wishlist!", "success");
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
        <div class="container gd-hero-content">
          <router-link to="/free-to-play" class="gd-back-btn">
            ← Free to Play
          </router-link>

          <div class="gd-hero-bottom">
            <!-- Cover thumbnail -->
            <img
              v-if="game.thumbnail"
              v-lazy-img="game.thumbnail"
              class="gd-cover"
              :alt="`${game.title} cover`"
            />

            <!-- Title + meta -->
            <div class="gd-hero-info">
              <div class="d-flex flex-wrap gap-2 mb-2">
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
              <h1 class="gd-title">{{ game.title }}</h1>

              <!-- Platform chips -->
              <div class="d-flex flex-wrap gap-2 mt-2">
                <span
                  v-for="p in platforms"
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
                <span
                  v-if="game.status"
                  class="gd-platform-chip"
                  style="
                    background: rgba(34, 197, 94, 0.15);
                    border-color: rgba(34, 197, 94, 0.3);
                    color: #86efac;
                  "
                >
                  {{ game.status }}
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
                <div class="gd-shot-zoom-hint">Click to enlarge</div>
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
                {{ game.description || "No description available." }}
              </div>
            </div>

            <!-- Tags -->
            <div v-if="game.genre" class="gd-section mb-5">
              <h2 class="gd-section-title">Tags</h2>
              <div class="gd-tags">
                <span class="gd-tag">{{ game.genre }}</span>
              </div>
            </div>

            <!-- System Requirements -->
            <div class="gd-section mb-5">
              <h2 class="gd-section-title">Minimum System Requirements</h2>
              <div class="table-responsive" v-if="sysReqs">
                  <table
                    class="table table-striped mb-0 gd-table"
                    style="font-size: 0.85rem"
                  >
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
              <ReviewSection
                :game-id="String(game.id)"
                :game-title="game.title"
              />
            </div>

            <!-- Discover More -->
            <div v-if="discoverMoreGames.length" class="gd-section mb-5">
              <h2 class="gd-section-title">More Games to Discover</h2>
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
            <div v-if="recentGames.length" class="gd-section mb-5">
              <h2 class="gd-section-title">Recent Releases</h2>
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
              <!-- Actions -->
              <div class="gd-actions mb-4">
                <a
                  v-if="game.game_url"
                  :href="game.game_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-primary w-100 mb-2 gd-action-btn"
                  aria-label="Official Website"
                >
                  <img src="/logo/pc.svg" alt="" class="gd-action-icon" />
                  <span>Play Now (FreeToGame)</span>
                </a>
                <button
                  class="btn btn-success w-100 mb-2 gd-action-btn"
                  @click="addToFavorites"
                  aria-label="Add to wishlist"
                >
                  <img src="/logo/star.svg" alt="" class="gd-action-icon" />
                  <span>Add to Wishlist</span>
                </button>

                <!-- Status toast -->
                <transition name="fav-fade">
                  <div
                    v-if="favStatus.visible"
                    class="fav-status-msg"
                    :class="`fav-status-${favStatus.type}`"
                    role="status"
                    aria-live="polite"
                  >
                    {{ favStatus.message }}
                  </div>
                </transition>
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

<style scoped>
/* ── Loading Skeleton ─────────────────────── */
.gd-skeleton-loader {
  animation: pulse 1.5s infinite;
}
.gd-skeleton-hero {
  height: 380px;
  background: rgba(255, 255, 255, 0.05);
  border-radius: 0 0 20px 20px;
}
.gd-skeleton-box {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 16px;
}
@keyframes pulse {
  0% {
    opacity: 0.6;
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0.6;
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
  padding: 4px 10px;
  border-radius: 20px;
  backdrop-filter: blur(4px);
  opacity: 0;
  transition: opacity 0.2s;
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

/* ── Sidebar ──────────────────────────────── */
.gd-sidebar {
  position: sticky;
  top: 80px;
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

/* Transitions */
.lb-enter-active,
.lb-leave-active {
  transition: opacity 0.2s ease;
}
.lb-enter-from,
.lb-leave-to {
  opacity: 0;
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
  .gd-sidebar {
    position: static;
  }
}
</style>
