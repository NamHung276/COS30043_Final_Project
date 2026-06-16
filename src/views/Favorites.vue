<script>
export default {
  data() {
    return {
      favorites: []
    }
  },

  methods: {
    removeFavorite(id) {

      this.favorites =
        this.favorites.filter(
          game => game.id !== id
        )

      localStorage.setItem(
        'favorites',
        JSON.stringify(this.favorites)
      )
    }
  },

  mounted() {

    const currentUser =
      JSON.parse(
        localStorage.getItem('currentUser')
      )

    if (!currentUser) {
        this.$router.push('/login')
        return
    }
      
    this.favorites =
      JSON.parse(
        localStorage.getItem('favorites')
      ) || []
  }
}
</script>

<template>
  <div>

    <h1 class="mb-4">
      My Favorites
    </h1>

    <div
      v-if="favorites.length === 0"
      class="alert alert-info"
    >
      No favorite games yet.
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
            :src="game.thumbnail"
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
              :to="`/games/${game.id}`"
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