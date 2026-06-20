// src/views/Favorites.vue
<script>
import { inject } from 'vue'
import { auth, db } from '../firebase'
import { onAuthStateChanged } from 'firebase/auth'
import {
  collection,
  query,
  where,
  getDocs,
  deleteDoc,
  doc
} from 'firebase/firestore'

export default {
  setup() {
    const toast = inject('toast')
    return { toast }
  },

  data() {
    return {
      favorites: [],
      loading: true,
      currentUser: null
    }
  },

  methods: {
    async removeFavorite(favoriteId, title) {
      try {
        await deleteDoc(doc(db, 'favorites', favoriteId))
        this.favorites = this.favorites.filter(
          fav => fav.id !== favoriteId
        )
        this.toast.show(`Removed "${title}" from favorites`, 'info')
      } catch (error) {
        console.error('Failed to remove favorite:', error)
        this.toast.show('Failed to remove. Please try again.', 'error')
      }
    },

    async loadFavorites(user) {
      this.loading = true

      const favoritesQuery = query(
        collection(db, 'favorites'),
        where('userId', '==', user.uid)
      )

      const snapshot = await getDocs(favoritesQuery)

      this.favorites = snapshot.docs.map(docSnap => ({
        id: docSnap.id,
        ...docSnap.data()
      }))

      this.loading = false
    }
  },

  mounted() {
    onAuthStateChanged(auth, (user) => {
      if (!user) {
        this.favorites = []
        this.currentUser = null
        this.$router.push('/login')
        return
      }

      this.currentUser = user
      this.loadFavorites(user)
    })
  }
}
</script>

<template>
  <div class="container py-4">

    <div class="section-header">
      <span class="section-icon">⭐</span>
      <h1 class="mb-0">My Favorites</h1>
    </div>

    <router-link
      to="/games"
      class="btn btn-outline-secondary mb-4"
    >
      ← Browse More Games
    </router-link>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <!-- Empty State -->
    <div
      v-else-if="favorites.length === 0"
      class="empty-state"
    >
      <div class="empty-state-icon">⭐</div>
      <h3>No favorites yet</h3>
      <p>
        Browse games and add your favorites to build your personal collection!
      </p>
      <router-link to="/games" class="btn btn-primary">
        🎮 Browse Games
      </router-link>
    </div>

    <div
      v-else
      class="row"
    >

      <div
        class="col-md-4 mb-4"
        v-for="(game, index) in favorites"
        :key="game.id"
      >

        <div
          class="card h-100 stagger-item"
          :style="{ animationDelay: `${index * 0.06}s` }"
        >

          <img
            v-lazy-img="game.thumbnail"
            class="card-img-top"
            :alt="`${game.title} favorite game thumbnail`"
            style="height: 180px; object-fit: cover;"
          >

          <div class="card-body">

            <h5 class="card-title" style="font-size: 1rem;">
              {{ game.title }}
            </h5>

            <span class="badge bg-primary mb-3">
              {{ game.genre }}
            </span>

            <div class="d-flex gap-2">
              <router-link
                :to="`/games/${game.gameId}`"
                class="btn btn-primary btn-sm"
              >
                Details
              </router-link>

              <button
                class="btn btn-outline-danger btn-sm"
                aria-label="Remove game from favorites"
                @click="removeFavorite(game.id, game.title)"
              >
                Remove
              </button>
            </div>

          </div>

        </div>

      </div>

    </div>

  </div>
</template>