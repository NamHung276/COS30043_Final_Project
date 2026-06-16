<script>
export default {
  data() {
    return {
      game: null,
      loading: true
    }
  },

  methods: {
    addToFavorites() {

      const currentUser =
        JSON.parse(
          localStorage.getItem('currentUser')
        )

      if (!currentUser) {

        alert(
          'Please login to add favorites.'
        )

        this.$router.push('/login')

        return
      }

      const favorites =
        JSON.parse(
          localStorage.getItem('favorites')
        ) || []

      const exists =
        favorites.find(
          game => game.id === this.game.id
        )

      if (exists) {

        alert(
          'Game already in favorites.'
        )

        return
      }

      favorites.push({
        id: this.game.id,
        title: this.game.title,
        thumbnail: this.game.thumbnail,
        genre: this.game.genre
      })

      localStorage.setItem(
        'favorites',
        JSON.stringify(favorites)
      )

      alert(
        'Added to favorites!'
      )
    }
  },

  async mounted() {
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

    <div v-if="loading">
      Loading...
    </div>

    <div v-else class="container mt-4">

      <h1>{{ game.title }}</h1>

      <div class="row mb-4">
        <div class="col-md-4">
          <img
            :src="game.thumbnail"
            class="img-fluid rounded"
            :alt="game.title"
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
                  class="btn btn-primary me-2"
                >
                  Play Game
                </a>
                <button
                  class="btn btn-success"
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
              :src="screenshot.image"
              :alt="game.title"
              class="img-thumbnail w-100"
            >
          </div>
        </div>
      </div>

    </div>
  </div>
</template>