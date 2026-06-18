<script>
export default {
  data() {
    return {
      firstName: '',
      lastName: '',
      selectedScene: 'mountain'
    }
  },

  computed: {
    fullName() {
      return `${this.firstName} ${this.lastName}`.trim()
    },

    sceneImage() {
      return this.selectedScene === 'mountain'
        ? 'https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80'
        : 'https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=800&q=80'
    },

    gamerTitle() {
      return this.selectedScene === 'mountain'
        ? '🏔️ Mountain Explorer'
        : '🌊 Ocean Voyager'
    }
  }
}
</script>

<template>
  <div class="container py-4">

    <h1 class="mb-4">About GameHub</h1>

    <div class="row g-4">

      <!-- Left Column: Main Content -->
      <div class="col-md-8">

        <div class="card mb-4">
          <div class="card-body text-start">
            <h3>🎮 Welcome to GameHub</h3>
            <p class="lead">
              Discover free-to-play games, explore gaming news,
              and build your personal collection of favourite titles.
            </p>
            <hr>
            <p>
              GameHub is a web application built with Vue 3 that allows users
              to browse free-to-play games, search for titles, filter games by
              genre, and view detailed information about individual games.
            </p>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-start">
            <h3>Technologies Used</h3>
            <ul>
              <li>Vue 3</li>
              <li>Vue Router</li>
              <li>Bootstrap 5</li>
              <li>JavaScript</li>
              <li>FreeToGame API</li>
              <li>NewsAPI</li>
            </ul>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-center">
            <div class="row">
              <div class="col-4">
                <h3 class="text-primary">300+</h3>
                <p>Games</p>
              </div>
              <div class="col-4">
                <h3 class="text-primary">15</h3>
                <p>Articles</p>
              </div>
              <div class="col-4">
                <h3 class="text-primary">2</h3>
                <p>APIs</p>
              </div>
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-start">
            <h3>Features</h3>
            <ul>
              <li>Browse free-to-play games</li>
              <li>Search games by title</li>
              <li>Filter games by genre</li>
              <li>View detailed game information</li>
              <li>View screenshots and game details</li>
              <li>Live gaming news via NewsAPI</li>
              <li>GameHub archived news</li>
              <li>Save favourite games</li>
              <li>User registration and login</li>
              <li>Responsive Bootstrap interface</li>
            </ul>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-start">
            <h3>Project Purpose</h3>
            <p>
              GameHub was created as part of the COS30043 Full-Stack Development course.
              The project demonstrates a complete modern web application showcasing Vue 3 frontend
              development, component-based architecture, API integration, and responsive design principles.
              It serves as a portfolio piece demonstrating full-stack web development capabilities.
            </p>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-start">
            <h3>APIs Used</h3>
            <ul>
              <li><strong>FreeToGame API</strong> - Provides access to 500+ free-to-play games with detailed information, genres, screenshots, and platform availability</li>
              <li><strong>NewsAPI</strong> - Delivers real-time gaming news and industry updates from multiple gaming news sources</li>
            </ul>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-start">
            <h3>Future Development</h3>
            <p>
              GameHub is continuously evolving.
              Future enhancements may include:
            </p>
            <ul>
              <li>User-generated reviews</li>
              <li>Game recommendation system</li>
              <li>Cloud-based favourites</li>
              <li>Admin news management</li>
              <li>Advanced search and filtering</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="col-md-4">

        <div class="card mb-4 sticky-top" style="top: 80px;">
          <div class="card-body text-start">

            <h5 class="card-title mb-3">🎮 Gamer Profile</h5>
            <p class="text-muted small mb-3">
              Create your gaming identity and choose your adventure.
            </p>

            <!-- Name Inputs -->
            <div class="mb-3">
              <label
                for="firstName"
                class="form-label"
              >
                First Name
              </label>
              <input
                id="firstName"
                v-model="firstName"
                type="text"
                class="form-control form-control-sm"
                placeholder="Your first name"
              >
            </div>

            <div class="mb-3">
              <label
                for="lastName"
                class="form-label"
              >
                Last Name
              </label>
              <input
                id="lastName"
                v-model="lastName"
                type="text"
                class="form-control form-control-sm"
                placeholder="Your last name"
              >
            </div>

            <!-- Welcome Message -->
            <div
              v-if="fullName"
              class="alert alert-success py-2 small"
            >
              🎮 Welcome, {{ fullName }}!

              <br>

              <strong>
                {{ gamerTitle }}
              </strong>
            </div>

            <hr>

            <!-- Scene Picker -->
            <h6 class="mb-2">🌄🗺️ Choose Your Adventure</h6>
            <p class="text-muted small mb-2">
              Select the world you would like to explore.
            </p>

            <div class="d-flex gap-3 mb-3">
              <div class="form-check">
                <input
                  id="mountain"
                  v-model="selectedScene"
                  class="form-check-input"
                  type="radio"
                  value="mountain"
                >
                <label
                  class="form-check-label"
                  for="mountain"
                >
                  🏔️ Mountain Realm
                </label>
              </div>

              <div class="form-check">
                <input
                  id="ocean"
                  v-model="selectedScene"
                  class="form-check-input"
                  type="radio"
                  value="ocean"
                >
                <label
                  class="form-check-label"
                  for="ocean"
                >
                  🌊 Ocean Kingdom
                </label>
              </div>
            </div>

            <img
              :src="sceneImage"
              :alt="selectedScene"
              class="img-fluid rounded"
              style="width: 100%; height: 160px; object-fit: cover;"
            >

            <p class="text-muted small mt-2 text-center">
              {{
                selectedScene === 'mountain'
                  ? 'You are a fearless Mountain Explorer.'
                  : 'You are an adventurous Ocean Voyager.'
              }}
            </p>

          </div>
        </div>

      </div>

    </div>

  </div>
</template>