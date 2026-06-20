// src/views/GameDetails.vue
<script>
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

  data() {
    return {
      game: null,
      loading: true,
      currentUser: null,
      favoriteMessage: '',
      favoriteMessageType: 'success'
    }
  },

  methods: {
    async addToFavorites() {
      if (!this.currentUser) {
        this.favoriteMessage = 'Please login to add favorites.'
        this.favoriteMessageType = 'danger'
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
          this.favoriteMessage = 'Game already in favorites.'
          this.favoriteMessageType = 'warning'
          return
        }

        await addDoc(collection(db, 'favorites'), {
          userId: this.currentUser.uid,
          gameId: this.game.id,
          title: this.game.title,
          thumbnail: this.game.thumbnail,
          genre: this.game.genre
        })

        this.favoriteMessage = 'Added to favorites!'
        this.favoriteMessageType = 'success'

      } catch (error) {
        console.error('Failed to add favorite:', error)
        this.favoriteMessage = 'Something went wrong. Please try again.'
        this.favoriteMessageType = 'danger'
      }

      setTimeout(() => {
        this.favoriteMessage = ''
      }, 3000)
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

      <h1>{{ game.title }}</h1>

      <div
        v-if="favoriteMessage"
        class="alert"
        :class="`alert-${favoriteMessageType}`"
      >
        {{ favoriteMessage }}
      </div>

      <div class="row mb-4">
        <div class="col-md-4">
          <img
            v-lazy-img="game.thumbnail"
            class="img-fluid rounded"
            :alt="`${game.title} game thumbnail`"
          >
        </div>
        <div class="col-md-8">
          <div class="card">
            <div class="card-body text-start">
              <p>
                <strong>Genre:</strong>
                {{ game.genre }}
              </p>
              <p>
                <strong>Platform:</strong>
                {{ game.platform }}
              </p>
              <p>
                <strong>Publisher:</strong>
                {{ game.publisher }}
              </p>
              <p>
                <strong>Developer:</strong>
                {{ game.developer }}
              </p>
              <p>
                <strong>Release Date:</strong>
                {{ game.release_date }}
              </p>
              <p>
                <strong>Status:</strong>
                {{ game.status }}
              </p>
              <div class="mt-3 d-flex justify-content-end">
                <a
                  v-if="game.game_url"
                  :href="game.game_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn btn-primary me-2"
                >
                  Play Game
                </a>
                <button
                  class="btn btn-success"
                  aria-label="Add game to favorites"
                  @click="addToFavorites"
                >
                  Add to Favorites
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <h3 class="mb-3">Description</h3>
      <p>
        {{ game.description }}
      </p>

      <div v-if="game.screenshots && game.screenshots.length" class="mt-5">
        <h3 class="mb-3">Screenshots</h3>
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
            >
          </div>
        </div>
      </div>

      <hr class="my-5">

      <ReviewSection :game-id="game.id" />

    </div>
  </div>
</template>