<script>
export default {
  data() {
    return {
      game: null,
      loading: true
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

    <div v-else>

      <h1>{{ game.title }}</h1>

      <img
        :src="game.thumbnail"
        class="img-fluid mb-3"
        :alt="game.title"
      >

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
        {{ game.description }}
      </p>

    </div>

  </div>
</template>