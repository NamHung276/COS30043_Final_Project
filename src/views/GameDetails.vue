// src/views/GameDetails.vue
<script>
import { inject } from 'vue'
import { auth, db } from '../firebase'
import { rawgApi } from '../api'
import { onAuthStateChanged } from 'firebase/auth'
import {
  collection, query, where, getDocs, addDoc
} from 'firebase/firestore'
import ReviewSection from '../components/ReviewSection.vue'

export default {
  components: { ReviewSection },

  setup() {
    const toast = inject('toast')
    return { toast }
  },

  data() {
    return {
      game: null,
      screenshots: [],
      similarGames: [],
      loading: true,
      currentUser: null,
      activeShot: 0,
      lightboxSrc: null,
      favStatus: { visible: false, message: '', type: 'success' }
    }
  },

  computed: {
    metacriticClass() {
      const s = this.game?.metacritic
      if (!s) return 'mc-grey'
      if (s >= 75) return 'mc-green'
      if (s >= 50) return 'mc-yellow'
      return 'mc-red'
    },

    metacriticLabel() {
      const s = this.game?.metacritic
      if (!s) return null
      if (s >= 75) return 'Overwhelmingly Positive'
      if (s >= 60) return 'Mostly Positive'
      if (s >= 40) return 'Mixed'
      return 'Mostly Negative'
    },

    ratingPercent() {
      return this.game?.rating ? (this.game.rating / 5) * 100 : 0
    },

    platforms() {
      return (this.game?.platforms || []).map(p => ({
        name: p.platform.name,
        icon: this.platformIcon(p.platform.name)
      }))
    },

    developerNames() {
      return (this.game?.developers || []).map(d => d.name).join(', ') || '—'
    },

    publisherNames() {
      return (this.game?.publishers || []).map(p => p.name).join(', ') || '—'
    },

    genreNames() {
      return (this.game?.genres || []).map(g => g.name)
    },

    heroImage() {
      if (this.screenshots.length && this.screenshots[this.activeShot]) {
        return this.screenshots[this.activeShot].image
      }
      return this.game?.background_image
    }
  },

  methods: {
    platformIcon(name) {
      const n = name.toLowerCase()
      if (n.includes('pc') || n.includes('windows')) return '💻'
      if (n.includes('playstation')) return '🎮'
      if (n.includes('xbox')) return '🟩'
      if (n.includes('nintendo') || n.includes('switch')) return '🔴'
      if (n.includes('mac')) return '🍎'
      if (n.includes('linux')) return '🐧'
      if (n.includes('android') || n.includes('ios') || n.includes('mobile')) return '📱'
      return '🕹️'
    },

    showFavStatus(message, type = 'success') {
      this.favStatus = { visible: true, message, type }
      clearTimeout(this._favTimer)
      this._favTimer = setTimeout(() => { this.favStatus.visible = false }, 3000)
    },

    async addToFavorites() {
      if (!this.currentUser) {
        this.showFavStatus('Please login to add favorites.', 'warning')
        setTimeout(() => this.$router.push('/login'), 1500)
        return
      }
      try {
        const snap = await getDocs(query(
          collection(db, 'favorites'),
          where('userId', '==', this.currentUser.uid),
          where('gameId', '==', this.game.id)
        ))
        if (!snap.empty) { this.showFavStatus('⚠️ Already in your favorites!', 'warning'); return }
        await addDoc(collection(db, 'favorites'), {
          userId: this.currentUser.uid,
          gameId: this.game.id,
          title: this.game.name,
          thumbnail: this.game.background_image,
          genre: this.game.genres?.[0]?.name || ''
        })
        this.showFavStatus('⭐ Added to favorites!', 'success')
      } catch (err) {
        console.error(err)
        this.showFavStatus('Something went wrong. Please try again.', 'error')
      }
    },

    openLightbox(src) { this.lightboxSrc = src },
    closeLightbox()   { this.lightboxSrc = null },

    selectShot(i) { this.activeShot = i }
  },

  async mounted() {
    onAuthStateChanged(auth, user => { this.currentUser = user })
    try {
      const id = this.$route.params.id
      const [gameRes, ssRes, simRes] = await Promise.all([
        rawgApi.get(`/games/${id}`),
        rawgApi.get(`/games/${id}/screenshots`),
        rawgApi.get(`/games/${id}/game-series`)
      ])
      this.game = gameRes.data
      this.screenshots = ssRes.data.results || []
      this.similarGames = (simRes.data.results || []).slice(0, 6)
    } catch (err) {
      console.error(err)
    } finally {
      this.loading = false
    }
  }
}
</script>

<template>
  <div>

    <!-- ── Loading ───────────────────────────────── -->
    <!-- ── Loading ───────────────────────────────── -->
    <div v-if="loading" class="gd-loader">
      <div class="gd-loader-inner">
        <div class="gd-spinner"></div>
        <p class="text-muted mt-3" style="font-size:0.9rem;">Loading game data…</p>
      </div>
    </div>

    <!-- ── Not Found ─────────────────────────────── -->
    <div v-else-if="!game" class="container mt-4">
      <div class="alert alert-danger">Game not found.</div>
      <router-link to="/games" class="btn btn-outline-secondary">← Back to Games</router-link>
    </div>

    <!-- ── Game Page ─────────────────────────────── -->
    <div v-else>

      <!-- ══════════ CINEMATIC HERO ══════════ -->
      <div class="gd-hero">
        <!-- Blurred background art -->
        <div class="gd-hero-bg" aria-hidden="true">
          <img :src="heroImage || game.background_image" alt="">
        </div>

        <!-- Gradient overlay -->
        <div class="gd-hero-overlay" aria-hidden="true"></div>

        <!-- Content -->
        <div class="container gd-hero-content">
          <router-link to="/games" class="gd-back-btn">
            ← Games
          </router-link>

          <div class="gd-hero-bottom">
            <!-- Cover thumbnail -->
            <img
              v-if="game.background_image"
              v-lazy-img="game.background_image"
              class="gd-cover"
              :alt="`${game.name} cover`"
            >

            <!-- Title + meta -->
            <div class="gd-hero-info">
              <div class="d-flex flex-wrap gap-2 mb-2">
                <span v-for="g in genreNames" :key="g" class="gd-badge-genre">{{ g }}</span>
                <span v-if="game.esrb_rating" class="gd-badge-esrb">{{ game.esrb_rating.name }}</span>
              </div>
              <h1 class="gd-title">{{ game.name }}</h1>

              <!-- Rating bar -->
              <div v-if="game.rating" class="gd-rating-row">
                <div class="gd-stars">
                  <div class="gd-stars-fill" :style="{ width: ratingPercent + '%' }"></div>
                </div>
                <span class="gd-rating-text">
                  {{ game.rating.toFixed(1) }}/5
                  <span class="gd-rating-count">({{ (game.ratings_count || 0).toLocaleString() }} ratings)</span>
                </span>
                <span v-if="game.metacritic" class="gd-metacritic" :class="metacriticClass">
                  {{ game.metacritic }}
                </span>
              </div>

              <!-- Platform chips -->
              <div class="d-flex flex-wrap gap-2 mt-2">
                <span v-for="p in platforms.slice(0, 6)" :key="p.name" class="gd-platform-chip">
                  {{ p.icon }} {{ p.name }}
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
              <div class="gd-shot-main" @click="openLightbox(screenshots[activeShot].image)">
                <img
                  v-lazy-img="screenshots[activeShot].image"
                  :alt="`${game.name} screenshot`"
                  class="gd-shot-main-img"
                >
                <div class="gd-shot-zoom-hint">🔍 Click to enlarge</div>
              </div>
              <!-- Thumbnail strip -->
              <div class="gd-shot-strip">
                <div
                  v-for="(shot, i) in screenshots"
                  :key="shot.id"
                  class="gd-shot-thumb"
                  :class="{ active: i === activeShot }"
                  @click="selectShot(i)"
                >
                  <img v-lazy-img="shot.image" :alt="`Screenshot ${i + 1}`">
                </div>
              </div>
            </div>

            <!-- About -->
            <div class="gd-section mb-4">
              <h2 class="gd-section-title">About this game</h2>
              <div class="gd-description">
                {{ game.description_raw || 'No description available.' }}
              </div>
            </div>

            <!-- Tags -->
            <div v-if="game.tags?.length" class="gd-section mb-4">
              <h2 class="gd-section-title">Tags</h2>
              <div class="gd-tags">
                <span v-for="tag in game.tags.slice(0, 20)" :key="tag.id" class="gd-tag">
                  {{ tag.name }}
                </span>
              </div>
            </div>

            <!-- Similar Games / Series -->
            <div v-if="similarGames.length" class="gd-section mb-4">
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
                  >
                  <div class="gd-similar-body">
                    <p class="gd-similar-title">{{ g.name }}</p>
                    <span v-if="g.metacritic" class="gd-similar-mc" :class="g.metacritic >= 75 ? 'mc-green' : g.metacritic >= 50 ? 'mc-yellow' : 'mc-red'">
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
                <div class="gd-mc-score" :class="metacriticClass">{{ game.metacritic }}</div>
                <div class="gd-mc-info">
                  <strong>Metacritic Score</strong>
                  <small class="d-block text-muted">{{ metacriticLabel }}</small>
                </div>
              </div>

              <!-- Actions -->
              <div class="gd-actions mb-4">
                <a
                  v-if="game.website"
                  :href="game.website"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-primary w-100 mb-2"
                >
                  🌐 Official Website
                </a>
                <button
                  class="btn btn-success w-100 mb-2"
                  @click="addToFavorites"
                  aria-label="Add to favorites"
                >
                  ⭐ Add to Favorites
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

                <!-- Store links -->
                <div v-if="game.stores?.length" class="gd-stores mt-2">
                  <small class="text-muted d-block mb-2" style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.5px;">Available On</small>
                  <div class="d-flex flex-wrap gap-2">
                    <a
                      v-for="s in game.stores"
                      :key="s.id"
                      :href="s.url || '#'"
                      target="_blank"
                      rel="noopener noreferrer"
                      class="gd-store-btn"
                    >
                      {{ s.store.name }}
                    </a>
                  </div>
                </div>
              </div>

              <!-- Details table -->
              <div class="gd-details-card">
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
                  <span class="gd-detail-value">{{ game.released }}</span>
                </div>
                <div class="gd-detail-row" v-if="game.playtime">
                  <span class="gd-detail-label">Avg Playtime</span>
                  <span class="gd-detail-value">{{ game.playtime }}h</span>
                </div>
                <div class="gd-detail-row" v-if="game.esrb_rating">
                  <span class="gd-detail-label">ESRB</span>
                  <span class="gd-detail-value">{{ game.esrb_rating.name }}</span>
                </div>
                <div class="gd-detail-row" v-if="game.ratings_count">
                  <span class="gd-detail-label">Total Votes</span>
                  <span class="gd-detail-value">{{ (game.ratings_count).toLocaleString() }}</span>
                </div>
              </div>

            </div>
          </div>

        </div>

        <!-- ══════════ REVIEWS ══════════ -->
        <div class="gd-reviews-section">
          <ReviewSection :game-id="game.id" />
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
        <button class="gd-lb-close" @click.stop="closeLightbox" aria-label="Close">✕</button>
        <img :src="lightboxSrc" alt="Screenshot enlarged" class="gd-lb-img" @click.stop>
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
.gd-loader-inner { text-align: center; }
.gd-spinner {
  width: 48px; height: 48px;
  border: 3px solid rgba(124,58,237,0.2);
  border-top-color: #7c3aed;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

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
}
.gd-hero-bg img {
  width: 100%; height: 100%;
  object-fit: cover;
  filter: blur(2px) brightness(0.35) saturate(0.7);
  transform: scale(1.05);
  display: block;
}
.gd-hero-overlay {
  position: absolute;
  inset: 0;
  background:
    linear-gradient(to top, var(--bg-deep) 0%, rgba(5,7,15,0.6) 50%, rgba(5,7,15,0.2) 100%),
    linear-gradient(to right, rgba(5,7,15,0.7) 0%, transparent 60%);
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
  color: rgba(255,255,255,0.75);
  text-decoration: none;
  font-size: 0.88rem;
  font-weight: 600;
  padding: 8px 14px;
  border-radius: 8px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  margin-bottom: 28px;
  transition: all 0.2s;
  margin-top: 20px;
  backdrop-filter: blur(8px);
}
.gd-back-btn:hover {
  color: #fff;
  background: rgba(255,255,255,0.14);
  border-color: rgba(255,255,255,0.25);
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
  box-shadow: 0 12px 40px rgba(0,0,0,0.7);
  flex-shrink: 0;
  border: 2px solid rgba(255,255,255,0.1);
}
.gd-hero-info { flex: 1; min-width: 240px; }
.gd-title {
  font-size: clamp(1.6rem, 4vw, 2.8rem);
  font-weight: 900;
  color: #fff;
  margin-bottom: 12px;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 20px rgba(0,0,0,0.8);
  line-height: 1.1;
}

/* Genre/ESRB badges */
.gd-badge-genre {
  padding: 3px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(124,58,237,0.3);
  border: 1px solid rgba(124,58,237,0.4);
  color: #c4b5fd;
}
.gd-badge-esrb {
  padding: 3px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.15);
  color: rgba(255,255,255,0.7);
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
  background: rgba(255,255,255,0.15);
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
  color: rgba(255,255,255,0.8);
  font-weight: 600;
}
.gd-rating-count {
  font-size: 0.75rem;
  color: rgba(255,255,255,0.5);
  font-weight: 400;
  margin-left: 4px;
}

/* Metacritic score badge */
.gd-metacritic {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 44px; height: 44px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 900;
  flex-shrink: 0;
}
.mc-green  { background: #15803d; color: #fff; }
.mc-yellow { background: #a16207; color: #fff; }
.mc-red    { background: #b91c1c; color: #fff; }
.mc-grey   { background: #374151; color: #9ca3af; }

/* Platform chips */
.gd-platform-chip {
  font-size: 0.72rem;
  padding: 3px 10px;
  border-radius: 20px;
  background: rgba(255,255,255,0.08);
  border: 1px solid rgba(255,255,255,0.12);
  color: rgba(255,255,255,0.7);
  white-space: nowrap;
}

/* ── Body Layout ──────────────────────────── */
.gd-body {
  padding-top: 32px;
  padding-bottom: 60px;
}

/* ── Screenshots ──────────────────────────── */
.gd-screenshots-block {}
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
.gd-shot-main:hover .gd-shot-main-img { filter: brightness(0.85); }
.gd-shot-zoom-hint {
  position: absolute;
  bottom: 14px;
  right: 14px;
  background: rgba(0,0,0,0.6);
  color: rgba(255,255,255,0.8);
  font-size: 0.72rem;
  padding: 4px 10px;
  border-radius: 20px;
  backdrop-filter: blur(4px);
  opacity: 0;
  transition: opacity 0.2s;
}
.gd-shot-main:hover .gd-shot-zoom-hint { opacity: 1; }

.gd-shot-strip {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  scrollbar-width: thin;
  scrollbar-color: rgba(124,58,237,0.3) transparent;
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
.gd-shot-thumb:hover { opacity: 0.85; }
.gd-shot-thumb.active {
  border-color: var(--primary);
  opacity: 1;
  box-shadow: 0 0 12px rgba(124,58,237,0.5);
}
.gd-shot-thumb img {
  width: 100%; height: 100%;
  object-fit: cover; display: block;
}

/* ── Section headings ─────────────────────── */
.gd-section-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 16px;
  padding-bottom: 10px;
  border-bottom: 1px solid var(--border-glass);
  letter-spacing: 0.02em;
  text-transform: uppercase;
  font-size: 0.82rem;
  color: var(--text-muted);
}

/* ── Description ──────────────────────────── */
.gd-description {
  font-size: 0.93rem;
  line-height: 1.9;
  color: var(--text-secondary);
  white-space: pre-wrap;
}

/* ── Tags ─────────────────────────────────── */
.gd-tags { display: flex; flex-wrap: wrap; gap: 8px; }
.gd-tag {
  padding: 4px 14px;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
  background: rgba(124,58,237,0.1);
  border: 1px solid rgba(124,58,237,0.2);
  color: var(--text-secondary);
  transition: all 0.2s ease;
  cursor: default;
}
.gd-tag:hover {
  background: rgba(124,58,237,0.22);
  border-color: rgba(124,58,237,0.4);
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
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: block;
}
.gd-similar-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(124,58,237,0.35);
  border-color: rgba(124,58,237,0.4);
}
.gd-similar-img { width: 100%; height: 80px; object-fit: cover; display: block; }
.gd-similar-body { padding: 8px; display: flex; justify-content: space-between; align-items: center; gap: 6px; }
.gd-similar-title {
  font-size: 0.72rem; font-weight: 600;
  color: var(--text-primary); margin: 0;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  flex: 1;
}
.gd-similar-mc {
  font-size: 0.65rem; font-weight: 800;
  padding: 2px 6px; border-radius: 4px; flex-shrink: 0;
}

/* ── Sidebar ──────────────────────────────── */
.gd-sidebar { position: sticky; top: 80px; }

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
  width: 60px; height: 60px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

/* Actions */
.gd-actions {}

.gd-store-btn {
  display: inline-block;
  padding: 4px 12px;
  font-size: 0.72rem;
  border-radius: 20px;
  background: rgba(255,255,255,0.05);
  border: 1px solid var(--border-glass);
  color: var(--text-secondary);
  text-decoration: none;
  transition: all 0.2s ease;
}
.gd-store-btn:hover {
  background: rgba(124,58,237,0.15);
  border-color: rgba(124,58,237,0.35);
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
.gd-detail-row:last-child { border-bottom: none; }
.gd-detail-label { color: var(--text-muted); flex-shrink: 0; }
.gd-detail-value { color: var(--text-primary); font-weight: 600; text-align: right; }

/* ── Reviews ──────────────────────────────── */
.gd-reviews-section { margin-top: 48px; padding-top: 32px; border-top: 1px solid var(--border-glass); }

/* ── Lightbox ─────────────────────────────── */
.gd-lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.92);
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
  box-shadow: 0 32px 80px rgba(0,0,0,0.8);
  cursor: default;
}
.gd-lb-close {
  position: absolute;
  top: 20px; right: 24px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  border-radius: 50%;
  width: 40px; height: 40px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
  display: flex; align-items: center; justify-content: center;
}
.gd-lb-close:hover { background: rgba(255,255,255,0.25); }

/* Transitions */
.lb-enter-active, .lb-leave-active { transition: opacity 0.2s ease; }
.lb-enter-from, .lb-leave-to       { opacity: 0; }

.fav-fade-enter-active, .fav-fade-leave-active { transition: all 0.3s ease; }
.fav-fade-enter-from, .fav-fade-leave-to       { opacity: 0; transform: translateY(-6px); }

/* Responsive */
@media (max-width: 768px) {
  .gd-hero { min-height: 280px; }
  .gd-cover { width: 120px; height: 80px; }
  .gd-title { font-size: 1.4rem; }
  .gd-shot-main-img { height: 220px; }
  .gd-similar-grid { grid-template-columns: repeat(2, 1fr); }
  .gd-sidebar { position: static; }
}
</style>