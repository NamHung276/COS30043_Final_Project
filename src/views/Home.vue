<script>
export default {
  data() {
    return {
      featuredGames: [],
      loading: true
    }
  },

  async mounted() {
    try {
      const response = await fetch(
        'https://www.freetogame.com/api/games'
      )

      const games = await response.json()

      this.featuredGames =
        games
          .sort(() => 0.5 - Math.random())
          .slice(0, 3)

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

    <!-- Hero Banner -->
    <div class="hero-banner">
      <div class="hero-content">

        <h1>Discover Your Next Adventure</h1>

        <p class="lead">
          Explore free-to-play games,
          stay updated with gaming news,
          and build your favorite collection.
        </p>

        <div class="mt-4">
          <router-link
            to="/games"
            class="btn btn-primary me-2"
          >
            Browse Games
          </router-link>

          <router-link
            to="/live-news"
            class="btn btn-outline-light"
          >
            Latest News
          </router-link>
        </div>

      </div>
    </div>

    <div class="container py-4">

      <!-- Stage 1: Two Static Images -->
      <h2 class="mb-4">Welcome to GameHub</h2>
      <p class="text-muted mb-4">
        Your one-stop destination for free-to-play games, gaming news,
        and a community of passionate gamers. Browse hundreds of titles,
        stay up to date with the latest gaming news, and save your
        favourite games all in one place.
      </p>

      <div class="row mb-5 g-4">
        <div class="col-md-6">
          <img
            src="/home/game_home.jpg"
            alt="Gaming setup with PC and RGB lighting"
            class="img-fluid rounded shadow"
            style="width: 100%; height: 280px; object-fit: cover;"
          >
          <p class="text-muted small mt-2 text-center">
            Level up your gaming experience
          </p>
        </div>
        <div class="col-md-6">
          <img
            src="/home/gaming_community.jpg"
            alt="Multiplayer gaming community"
            class="img-fluid rounded shadow"
            style="width: 100%; height: 280px; object-fit: cover;"
          >
          <p class="text-muted small mt-2 text-center">
            Join a community of gamers
          </p>
        </div>
      </div>

      <!-- Trending Section -->

      <h2 class="mb-3">
        🔥 Trending Now
      </h2>

      <div class="card mb-5">
        <div class="card-body">

          <div class="row text-center">

            <div class="col-md-3">
              <h5>MMORPG</h5>
            </div>

            <div class="col-md-3">
              <h5>Shooter</h5>
            </div>

            <div class="col-md-3">
              <h5>Battle Royale</h5>
            </div>

            <div class="col-md-3">
              <h5>MOBA</h5>
            </div>

          </div>

        </div>
      </div>

      <!-- Featured Games -->
      <h2 class="mb-4">Featured Games</h2>

      <div v-if="loading" class="text-center py-4">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <div v-else class="row">
        <div
          class="col-md-4 mb-4"
          v-for="game in featuredGames"
          :key="game.title"
        >
        <router-link
          :to="'/games/' + game.id"
          class="text-decoration-none"
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
      
      <!-- Statistics -->
      <div class="row text-center my-5">
        <div class="col-md-3">
          <h2>300+</h2>
          <p>Free Games</p>
        </div>
        <div class="col-md-3">
          <h2>15</h2>
          <p>GameHub Articles</p>
        </div>
        <div class="col-md-3">
          <h2>24/7</h2>
          <p>Gaming Updates</p>
        </div>
        <div class="col-md-3">
          <h2>100%</h2>
          <p>Free To Play</p>
        </div>
      </div>

      <!-- Why GameHub -->
      <h2 class="mb-4">Why Choose GameHub?</h2>

      <div class="row">

        <div class="col-md-4 mb-4">
          <div class="card h-100">
            <div class="card-body">

              <h5 class="card-title">
                🎮 Massive Library
              </h5>

              <p class="card-text">
                Discover hundreds of free-to-play games
                across multiple genres and platforms.
              </p>

            </div>
          </div>
        </div>

        <div class="col-md-4 mb-4">
          <div class="card h-100">
            <div class="card-body">

              <h5 class="card-title">
                📰 Live Updates
              </h5>

              <p class="card-text">
                Stay informed with the latest gaming
                news, releases, and industry updates.
              </p>

            </div>
          </div>
        </div>

        <div class="col-md-4 mb-4">
          <div class="card h-100">
            <div class="card-body">

              <h5 class="card-title">
                ⭐ Personal Collection
              </h5>

              <p class="card-text">
                Save your favorite games and
                access them anytime.
              </p>

            </div>
          </div>
        </div>

      </div>

    </div>

  </div>
</template>