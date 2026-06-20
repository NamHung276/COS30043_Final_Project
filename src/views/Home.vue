// src/views/Home.vue
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

        <div class="mt-4 d-flex justify-content-center gap-3 flex-wrap">
          <router-link
            to="/games"
            class="btn btn-primary btn-lg"
            aria-label="Browse all games"
          >
            🎮 Browse Games
          </router-link>

          <router-link
            to="/live-news"
            class="btn btn-outline-light btn-lg"
            aria-label="View latest gaming news"
          >
            📰 Latest News
          </router-link>
        </div>

      </div>
    </div>

    <div class="container py-5">

      <!-- Welcome Section -->
      <div class="section-header">
        <span class="section-icon">👋</span>
        <h2 class="mb-0">Welcome to GameHub</h2>
      </div>

      <p class="text-muted mb-4" style="max-width: 700px;">
        Your one-stop destination for free-to-play games, gaming news,
        and a community of passionate gamers. Browse hundreds of titles,
        stay up to date with the latest gaming news, and save your
        favourite games all in one place.
      </p>

      <div class="row mb-5 g-4">
        <div class="col-md-6">
          <div class="card overflow-hidden" style="border: none;">
            <img
              src="/home/game_home.jpg"
              alt="Gaming setup with PC and RGB lighting"
              class="img-fluid"
              style="width: 100%; height: 280px; object-fit: cover;"
            >
            <div class="card-body text-center">
              <p class="text-muted small mb-0">
                Level up your gaming experience
              </p>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card overflow-hidden" style="border: none;">
            <img
              src="/home/gaming_community.jpg"
              alt="Multiplayer gaming community"
              class="img-fluid"
              style="width: 100%; height: 280px; object-fit: cover;"
            >
            <div class="card-body text-center">
              <p class="text-muted small mb-0">
                Join a community of gamers
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Trending Section -->
      <div class="section-header">
        <span class="section-icon">🔥</span>
        <h2 class="mb-0">Trending Now</h2>
      </div>

      <div class="d-flex gap-3 flex-wrap mb-5">
        <div class="genre-badge">
          <span class="genre-icon">⚔️</span> MMORPG
        </div>
        <div class="genre-badge">
          <span class="genre-icon">🎯</span> Shooter
        </div>
        <div class="genre-badge">
          <span class="genre-icon">🏆</span> Battle Royale
        </div>
        <div class="genre-badge">
          <span class="genre-icon">🧙</span> MOBA
        </div>
      </div>

      <!-- Featured Games -->
      <div class="section-header">
        <span class="section-icon">⭐</span>
        <h2 class="mb-0">Featured Games</h2>
      </div>

      <!-- Skeleton Loading -->
      <div v-if="loading" class="row">
        <div
          class="col-md-4 mb-4"
          v-for="n in 3"
          :key="n"
        >
          <div class="card skeleton-card">
            <div class="skeleton skeleton-image"></div>
            <div style="padding: 16px;">
              <div class="skeleton skeleton-line" style="width: 80%;"></div>
              <div class="skeleton skeleton-line short"></div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="row">
        <div
          class="col-md-4 mb-4"
          v-for="(game, index) in featuredGames"
          :key="game.id"
        >
        <router-link
          :to="'/games/' + game.id"
          class="text-decoration-none"
        >
          <div
            class="card h-100 stagger-item"
            :style="{ animationDelay: `${index * 0.1}s` }"
          >
            <img
              :src="game.thumbnail"
              class="card-img-top"
              :alt="`${game.title} featured game thumbnail`"
              style="height: 200px; object-fit: cover;"
            >
            <div class="card-body">
              <h5 class="card-title">
                {{ game.title }}
              </h5>
              <span class="badge bg-primary">
                {{ game.genre }}
              </span>
            </div>
          </div>
        </router-link>
        </div>
      </div>
      
      <!-- Statistics -->
      <div class="card my-5">
        <div class="card-body py-4">
          <div class="row text-center">

            <div class="col-6 col-md-3 stat-card">
              <div class="stat-number">300+</div>
              <p>Free Games</p>
            </div>

            <div class="col-6 col-md-3 stat-card">
              <div class="stat-number">15</div>
              <p>GameHub Articles</p>
            </div>

            <div class="col-6 col-md-3 stat-card">
              <div class="stat-number">24/7</div>
              <p>Gaming Updates</p>
            </div>

            <div class="col-6 col-md-3 stat-card">
              <div class="stat-number">100%</div>
              <p>Free To Play</p>
            </div>

          </div>
        </div>
      </div>

      <!-- Why GameHub -->
      <div class="section-header">
        <span class="section-icon">💡</span>
        <h2 class="mb-0">Why Choose GameHub?</h2>
      </div>

      <div class="row">

        <div class="col-md-4 mb-4">
          <div class="card h-100">
            <div class="card-body">
              <div class="feature-icon">🎮</div>
              <h5 class="card-title">
                Massive Library
              </h5>
              <p class="card-text text-muted">
                Discover hundreds of free-to-play games
                across multiple genres and platforms.
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-4 mb-4">
          <div class="card h-100">
            <div class="card-body">
              <div class="feature-icon">📰</div>
              <h5 class="card-title">
                Live Updates
              </h5>
              <p class="card-text text-muted">
                Stay informed with the latest gaming
                news, releases, and industry updates.
              </p>
            </div>
          </div>
        </div>

        <div class="col-md-4 mb-4">
          <div class="card h-100">
            <div class="card-body">
              <div class="feature-icon">⭐</div>
              <h5 class="card-title">
                Personal Collection
              </h5>
              <p class="card-text text-muted">
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