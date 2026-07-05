// src/views/FreeToPlayDetails.vue
<script>
import { inject } from 'vue'
import { auth, db } from '../firebase'
import { freeToGameApi } from '../api'
import { onAuthStateChanged } from 'firebase/auth'
import {
  collection,
  query,
  where,
  getDocs,
  addDoc
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
      loading: true,
      currentUser: null,
      activeScreenshot: null,
      favStatus: { visible: false, message: '', type: 'success' }
    }
  },

  computed: {
    hasSystemReqs() {
      const r = this.game?.minimum_system_requirements
      return r && Object.values(r).some(v => v)
    }
  },

  methods: {
    showFavStatus(message, type = 'success') {
      this.favStatus = { visible: true, message, type }
      clearTimeout(this._favTimer)
      this._favTimer = setTimeout(() => {
        this.favStatus.visible = false
      }, 3000)
    },

    async addToFavorites() {
      if (!this.currentUser) {
        this.showFavStatus('Please login to add favorites.', 'warning')
        setTimeout(() => this.$router.push('/login'), 1500)
        return
      }

      try {
        const existingQuery = query(
          collection(db, 'favorites'),
          where('userId', '==', this.currentUser.uid),
          where('gameId', '==', this.game.id),
          where('source', '==', 'freetogame')
        )
        const existingSnapshot = await getDocs(existingQuery)

        if (!existingSnapshot.empty) {
          this.showFavStatus('⚠️ Already in your favorites!', 'warning')
          return
        }

        await addDoc(collection(db, 'favorites'), {
          userId: this.currentUser.uid,
          gameId: this.game.id,
          title: this.game.title,
          thumbnail: this.game.thumbnail,
          genre: this.game.genre,
          source: 'freetogame'           // ← distinguishes from RAWG favorites
        })

        this.showFavStatus('⭐ Added to favorites!', 'success')
      } catch (error) {
        console.error('Failed to add favorite:', error)
        this.showFavStatus('Something went wrong. Please try again.', 'error')
      }
    },

    openScreenshot(img) {
      this.activeScreenshot = img
    },

    closeScreenshot() {
      this.activeScreenshot = null
    }
  },

  async mounted() {
    onAuthStateChanged(auth, (user) => {
      this.currentUser = user
    })

    try {
      const id = this.$route.params.id
      const { data } = await freeToGameApi.get('/game', { params: { id } })
      this.game = data
    } catch (error) {
      console.error(error)
    } finally {
      this.loading = false
    }
  }
}
</script>

<template>
  <div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Not found -->
    <div v-else-if="!game" class="container mt-4">
      <div class="alert alert-danger">Game not found.</div>
      <router-link to="/free-to-play" class="btn btn-outline-secondary">
        ← Back to Free to Play
      </router-link>
    </div>

    <div v-else class="container mt-4">

      <router-link to="/free-to-play" class="btn btn-outline-secondary mb-3">
        ← Back to Free to Play
      </router-link>

      <!-- Hero banner -->
      <div
        class="mb-4 rounded"
        style="position:relative; height:320px; overflow:hidden; isolation:isolate; contain:layout;"
      >
        <!-- Blurred background -->
        <div style="position:absolute; inset:0; overflow:hidden; contain:strict;">
          <img
            v-if="game.thumbnail"
            :src="game.thumbnail"
            alt=""
            aria-hidden="true"
            style="width:100%; height:100%; object-fit:cover; filter:blur(20px) brightness(0.3); transform:scale(1.1); display:block;"
          >
        </div>

        <!-- Foreground content -->
        <div style="position:absolute; inset:0; display:flex; align-items:center; padding:32px;">
          <div class="d-flex align-items-start gap-4 flex-wrap">
            <img
              v-if="game.thumbnail"
              v-lazy-img="game.thumbnail"
              class="rounded"
              :alt="`${game.title} thumbnail`"
              style="width:200px; height:130px; object-fit:cover; box-shadow:0 8px 30px rgba(0,0,0,0.6); position:relative; z-index:1;"
            >
            <div style="position:relative; z-index:1;">
              <h1 class="mb-2" style="color:#fff; text-shadow:0 2px 16px rgba(0,0,0,0.9);">
                {{ game.title }}
              </h1>
              <div class="d-flex gap-2 flex-wrap mb-2">
                <span class="badge bg-primary">{{ game.genre }}</span>
                <span class="badge" style="background:rgba(74,222,128,0.25); color:#4ade80;">
                  🆓 Free to Play
                </span>
                <span class="badge" style="background:rgba(255,255,255,0.15);">
                  {{ game.platform }}
                </span>
                <span
                  v-if="game.status"
                  class="badge"
                  style="background:rgba(34,197,94,0.2); color:#86efac;"
                >
                  {{ game.status }}
                </span>
              </div>
              <small style="color:rgba(255,255,255,0.7);">
                Released: {{ game.release_date }} · by {{ game.developer }}
              </small>
            </div>
          </div>
        </div>
      </div>

      <!-- Main content row -->
      <div class="row mb-4">

        <!-- Description -->
        <div class="col-md-8">
          <div class="card">
            <div class="card-body text-start">
              <h3 class="mb-3">About</h3>
              <p style="line-height:1.8; white-space:pre-line;">
                {{ game.description || game.short_description || 'No description available.' }}
              </p>
            </div>
          </div>
        </div>

        <!-- Sidebar -->
        <div class="col-md-4">
          <div class="card">
            <div class="card-body text-start">
              <h5 class="mb-3">Details</h5>

              <div class="mb-2">
                <small class="text-muted d-block">Developer</small>
                <strong>{{ game.developer || '—' }}</strong>
              </div>
              <div class="mb-2">
                <small class="text-muted d-block">Publisher</small>
                <strong>{{ game.publisher || '—' }}</strong>
              </div>
              <div class="mb-2">
                <small class="text-muted d-block">Release Date</small>
                <strong>{{ game.release_date || '—' }}</strong>
              </div>
              <div class="mb-2">
                <small class="text-muted d-block">Platform</small>
                <strong>{{ game.platform || '—' }}</strong>
              </div>
              <div class="mb-3">
                <small class="text-muted d-block">Genre</small>
                <strong>{{ game.genre || '—' }}</strong>
              </div>

              <hr style="border-color:var(--border-glass);">

              <div class="d-grid gap-2">
                <!-- Play / Download button -->
                <a
                  v-if="game.game_url"
                  :href="game.game_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-primary"
                >
                  🎮 {{ game.platform && game.platform.toLowerCase().includes('browser') ? 'Play in Browser' : 'Download Free' }}
                </a>

                <!-- Add to Favorites -->
                <button
                  class="btn btn-success"
                  aria-label="Add game to favorites"
                  @click="addToFavorites"
                >
                  ⭐ Add to Favorites
                </button>

                <!-- Inline status message -->
                <transition name="fav-status">
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

                <!-- FreeToGame profile link -->
                <a
                  v-if="game.freetogame_profile_url"
                  :href="game.freetogame_profile_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-sm"
                  style="background:var(--bg-glass); border:1px solid var(--border-glass); font-size:0.78rem;"
                >
                  🔗 View on FreeToGame
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Minimum System Requirements -->
      <div v-if="hasSystemReqs" class="mt-4">
        <div class="section-header">
          <span class="section-icon">🖥️</span>
          <h3 class="mb-0">Minimum System Requirements</h3>
        </div>
        <div class="card">
          <div class="card-body p-0">
            <table
              class="table table-bordered mb-0"
              :aria-label="`Minimum system requirements for ${game.title}`"
              style="border-color:var(--border-glass);"
            >
              <caption class="visually-hidden">
                Minimum system requirements for {{ game.title }}
              </caption>
              <thead>
                <tr>
                  <th scope="col" style="width:35%;">Component</th>
                  <th scope="col">Requirement</th>
                </tr>
              </thead>
              <tbody>
                <tr v-if="game.minimum_system_requirements.os">
                  <th scope="row">Operating System</th>
                  <td>{{ game.minimum_system_requirements.os }}</td>
                </tr>
                <tr v-if="game.minimum_system_requirements.processor">
                  <th scope="row">Processor</th>
                  <td>{{ game.minimum_system_requirements.processor }}</td>
                </tr>
                <tr v-if="game.minimum_system_requirements.memory">
                  <th scope="row">Memory</th>
                  <td>{{ game.minimum_system_requirements.memory }}</td>
                </tr>
                <tr v-if="game.minimum_system_requirements.graphics">
                  <th scope="row">Graphics</th>
                  <td>{{ game.minimum_system_requirements.graphics }}</td>
                </tr>
                <tr v-if="game.minimum_system_requirements.storage">
                  <th scope="row">Storage</th>
                  <td>{{ game.minimum_system_requirements.storage }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Screenshots -->
      <div v-if="game.screenshots && game.screenshots.length" class="mt-5">
        <div class="section-header">
          <span class="section-icon">📸</span>
          <h3 class="mb-0">Screenshots</h3>
        </div>
        <div class="row g-3">
          <div
            v-for="shot in game.screenshots"
            :key="shot.id"
            class="col-md-4"
          >
            <img
              v-lazy-img="shot.image"
              :alt="`${game.title} screenshot`"
              class="img-thumbnail w-100 ftg-screenshot"
              style="height:200px; object-fit:cover; cursor:pointer;"
              @click="openScreenshot(shot.image)"
            >
          </div>
        </div>
      </div>

      <hr class="my-5" style="border-color:var(--border-glass);">

      <ReviewSection :game-id="game.id" />

    </div>

    <!-- Lightbox overlay -->
    <transition name="lightbox">
      <div
        v-if="activeScreenshot"
        class="ftg-lightbox"
        @click="closeScreenshot"
        role="dialog"
        aria-modal="true"
        aria-label="Screenshot preview"
      >
        <button
          class="ftg-lightbox-close"
          @click.stop="closeScreenshot"
          aria-label="Close screenshot"
        >✕</button>
        <img
          :src="activeScreenshot"
          alt="Screenshot enlarged"
          class="ftg-lightbox-img"
          @click.stop
        >
      </div>
    </transition>

  </div>
</template>

<style scoped>
.ftg-screenshot {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.ftg-screenshot:hover {
  transform: scale(1.02);
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}

/* Lightbox */
.ftg-lightbox {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.88);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
  padding: 24px;
  cursor: zoom-out;
}
.ftg-lightbox-img {
  max-width: 90vw;
  max-height: 85vh;
  border-radius: 10px;
  box-shadow: 0 24px 80px rgba(0,0,0,0.7);
  cursor: default;
}
.ftg-lightbox-close {
  position: absolute;
  top: 20px;
  right: 24px;
  background: rgba(255,255,255,0.1);
  border: 1px solid rgba(255,255,255,0.2);
  color: #fff;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.ftg-lightbox-close:hover { background: rgba(255,255,255,0.25); }

/* Transitions */
.lightbox-enter-active, .lightbox-leave-active { transition: opacity 0.2s ease; }
.lightbox-enter-from, .lightbox-leave-to       { opacity: 0; }

.fav-status-enter-active, .fav-status-leave-active { transition: all 0.3s ease; }
.fav-status-enter-from, .fav-status-leave-to       { opacity: 0; transform: translateY(-6px); }
</style>
