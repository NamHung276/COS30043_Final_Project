// src/views/GameDetails.vue
<script>
import { inject } from 'vue'
import { auth, db } from '../firebase'
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
      currentUser: null
    }
  },

  methods: {
    async addToFavorites() {
      if (!this.currentUser) {
        this.toast.show('Please login to add favorites.', 'warning')
        setTimeout(() => this.$router.push('/login'), 1500)
        return
      }

      try {
        // Check if already favorited
        const existingQuery = query(
          collection(db, 'favorites'),
          where('userId', '==', this.currentUser.uid),
          where('gameId', '==', this.game.id)
        )

        const existingSnapshot = await getDocs(existingQuery)

        if (!existingSnapshot.empty) {
          this.toast.show('Game already in favorites.', 'warning')
          return
        }

        await addDoc(collection(db, 'favorites'), {
          userId: this.currentUser.uid,
          gameId: this.game.id,
          title: this.game.title,
          thumbnail: this.game.thumbnail,
          genre: this.game.genre
        })

        this.toast.show('Added to favorites! ⭐', 'success')

      } catch (error) {
        console.error('Failed to add favorite:', error)
        this.toast.show('Something went wrong. Please try again.', 'error')
      }
    }
  },

  async mounted() {
    onAuthStateChanged(auth, (user) => {
      this.currentUser = user
    })

    try {
      const id = this.$route.params.id

      const response = await fetch(
        `https://www.freetogame.com/api/game?id=${id}`
      )

      this.game = await response.json()
    }
    catch (error) {
      console.error(error)
    }
    finally {
      this.loading = false
    }
  }
}
</script>

<template>
  <div>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div v-else class="container mt-4">

      <router-link
        to="/games"
        class="btn btn-outline-secondary mb-3"
      >
        ← Back to Games
      </router-link>

      <!-- Game Hero Area -->
      <div class="card mb-4 overflow-hidden" style="border: none;">
        <div style="position: relative;">
          <img
            v-if="game.thumbnail"
            :src="game.thumbnail"
            :alt="`${game.title} banner`"
            style="width: 100%; height: 300px; object-fit: cover; filter: blur(20px) brightness(0.3); transform: scale(1.1);"
          >
          <div style="position: absolute; inset: 0; display: flex; align-items: center; padding: 32px;">
            <div class="d-flex align-items-start gap-4 flex-wrap">
              <img
                v-lazy-img="game.thumbnail"
                class="rounded"
                :alt="`${game.title} game thumbnail`"
                style="width: 200px; height: 120px; object-fit: cover; box-shadow: 0 8px 30px rgba(0,0,0,0.5);"
              >
              <div>
                <h1 class="mb-2" style="text-shadow: 0 2px 10px rgba(0,0,0,0.5);">{{ game.title }}</h1>
                <div class="d-flex gap-2 flex-wrap">
                  <span class="badge bg-primary">{{ game.genre }}</span>
                  <span class="badge" style="background: rgba(255,255,255,0.15);">{{ game.platform }}</span>
                  <span class="badge" style="background: rgba(34,197,94,0.2); color: #86efac;">{{ game.status }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Game Info -->
      <div class="row mb-4">
        <div class="col-md-8">
          <div class="card">
            <div class="card-body text-start">
              <h3 class="mb-3">About</h3>
              <p style="line-height: 1.8;">
                {{ game.description }}
              </p>
            </div>
          </div>
        </div>
        <div class="col-md-4">
          <div class="card">
            <div class="card-body text-start">
              <h5 class="mb-3">Details</h5>
              <div class="mb-2">
                <small class="text-muted d-block">Publisher</small>
                <strong>{{ game.publisher }}</strong>
              </div>
              <div class="mb-2">
                <small class="text-muted d-block">Developer</small>
                <strong>{{ game.developer }}</strong>
              </div>
              <div class="mb-2">
                <small class="text-muted d-block">Release Date</small>
                <strong>{{ game.release_date }}</strong>
              </div>
              <hr style="border-color: var(--border-glass);">
              <div class="d-grid gap-2">
                <a
                  v-if="game.game_url"
                  :href="game.game_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-primary"
                >
                  🎮 Play Game
                </a>
                <button
                  class="btn btn-success"
                  aria-label="Add game to favorites"
                  @click="addToFavorites"
                >
                  ⭐ Add to Favorites
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="game.screenshots && game.screenshots.length" class="mt-5">
        <div class="section-header">
          <span class="section-icon">📸</span>
          <h3 class="mb-0">Screenshots</h3>
        </div>
        <div class="row g-3">
          <div
            v-for="screenshot in game.screenshots"
            :key="screenshot.id"
            class="col-md-4"
          >
            <img
              v-lazy-img="screenshot.image"
              :alt="`${game.title} screenshot`"
              class="img-thumbnail w-100"
              style="height: 200px; object-fit: cover;"
            >
          </div>
        </div>
      </div>

      <hr class="my-5" style="border-color: var(--border-glass);">

      <ReviewSection :game-id="game.id" />

    </div>
  </div>
</template>