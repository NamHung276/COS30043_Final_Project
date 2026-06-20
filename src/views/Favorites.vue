// src/views/Favorites.vue
<script>
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
  data() {
    return {
      favorites: [],
      loading: true,
      currentUser: null
    }
  },

  methods: {
    async removeFavorite(favoriteId) {
      try {
        await deleteDoc(doc(db, 'favorites', favoriteId))
        this.favorites = this.favorites.filter(
          fav => fav.id !== favoriteId
        )
      } catch (error) {
        console.error('Failed to remove favorite:', error)
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

    <h1 class="mb-4">My Favorites</h1>

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>

    <div
      v-else-if="favorites.length === 0"
      class="alert alert-info"
    >
      No favorite games yet. Browse
      <router-link to="/games">games</router-link>
      and add some!
    </div>

    <div
      v-else
      class="row"
    >

      <div
        class="col-md-4 mb-4"
        v-for="game in favorites"
        :key="game.id"
      >

        <div class="card h-100">

          <img
            v-lazy-img="game.thumbnail"
            class="card-img-top"
            :alt="game.title"
          >

          <div class="card-body">

            <h5 class="card-title">
              {{ game.title }}
            </h5>

            <p class="card-text">
              Genre: {{ game.genre }}
            </p>

            <router-link
              :to="`/games/${game.gameId}`"
              class="btn btn-primary me-2"
            >
              Details
            </router-link>

            <button
              class="btn btn-danger"
              @click="removeFavorite(game.id)"
            >
              Remove
            </button>

          </div>

        </div>

      </div>

    </div>

  </div>
</template>