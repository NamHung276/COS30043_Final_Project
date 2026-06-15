<script>
export default {
  data() {
    return {
      games: [],
      loading: true,
      searchTerm: '',
      selectedGenre: 'All'
    }
  },

  computed: {
    filteredGames() {
      return this.games.filter(game => {

        const matchesSearch =
          game.title
            .toLowerCase()
            .includes(this.searchTerm.toLowerCase())

        const matchesGenre =
          this.selectedGenre === 'All' ||
          game.genre === this.selectedGenre

        return matchesSearch && matchesGenre
      })
    },

    genres() {
      return [
        'All',
        ...new Set(
          this.games.map(game => game.genre)
        )
      ]
    }
  },

  async mounted() {
    try {
      const response = await fetch(
        'https://www.freetogame.com/api/games'
      )

      this.games = await response.json()
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

    <h1 class="mb-4">Games</h1>

    <div class="mb-4">
      <input
        type="text"
        class="form-control"
        placeholder="Search games..."
        v-model="searchTerm"
      >
    </div>

    <div class="mb-4">
      <select
        class="form-select"
        v-model="selectedGenre"
      >
        <option
          v-for="genre in genres"
          :key="genre"
          :value="genre"
        >
          {{ genre }}
        </option>
      </select>
    </div>

    <div v-if="loading">
      Loading games...
    </div>

    <div v-else class="row">

        <div
            class="col-md-4 mb-4"
            v-for="game in filteredGames.slice(0, 12)"
            :key="game.id"
        >

        <router-link
            :to="`/games/${game.id}`"
            class="text-decoration-none text-dark"
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

            </div>

            </div>

        </router-link>

        </div>

    </div>

  </div>
</template>