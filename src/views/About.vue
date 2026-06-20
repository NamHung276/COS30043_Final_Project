// src/views/About.vue
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

    <div class="section-header">
      <span class="section-icon">ℹ️</span>
      <h1 class="mb-0">About GameHub</h1>
    </div>

    <div class="row g-4">

      <!-- Left Column: Main Content -->
      <div class="col-md-8">

        <div class="card mb-4">
          <div class="card-body text-start">
            <div class="feature-icon">🎮</div>
            <h3>Welcome to GameHub</h3>
            <p class="lead text-muted">
              Discover free-to-play games, explore gaming news,
              and build your personal collection of favourite titles.
            </p>
            <hr style="border-color: var(--border-glass);">
            <p class="text-muted">
              GameHub is a web application built with Vue 3 that allows users
              to browse free-to-play games, search for titles, filter games by
              genre, and view detailed information about individual games.
            </p>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-start">
            <div class="feature-icon">🛠️</div>
            <h3>Technologies Used</h3>
            <div class="row mt-3">
              <div class="col-6">
                <ul class="list-unstyled">
                  <li class="mb-2">🟢 Vue 3</li>
                  <li class="mb-2">🔀 Vue Router</li>
                  <li class="mb-2">🎨 Bootstrap 5</li>
                  <li class="mb-2">🔐 Firebase Auth</li>
                </ul>
              </div>
              <div class="col-6">
                <ul class="list-unstyled">
                  <li class="mb-2">🗄️ Firebase Firestore</li>
                  <li class="mb-2">🎮 FreeToGame API</li>
                  <li class="mb-2">📰 NewsAPI</li>
                  <li class="mb-2">⚡ Vite</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-center">
            <div class="row">
              <div class="col-4 stat-card">
                <div class="stat-number">300+</div>
                <p>Games</p>
              </div>
              <div class="col-4 stat-card">
                <div class="stat-number">24/7</div>
                <p>News Updates</p>
              </div>
              <div class="col-4 stat-card">
                <div class="stat-number">2</div>
                <p>External APIs</p>
              </div>           
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-start">
            <div class="feature-icon">✨</div>
            <h3>Features</h3>
            <div class="row mt-3">
              <div class="col-md-6">
                <ul class="list-unstyled">
                  <li class="mb-2">🎮 Browse free-to-play games</li>
                  <li class="mb-2">🔍 Search games by title</li>
                  <li class="mb-2">🏷️ Filter games by genre</li>
                  <li class="mb-2">📋 View detailed game information</li>
                  <li class="mb-2">📸 View screenshots</li>
                  <li class="mb-2">📡 Live gaming news via NewsAPI</li>
                  <li class="mb-2">📰 GameHub archived news</li>
                </ul>
              </div>
              <div class="col-md-6">
                <ul class="list-unstyled">
                  <li class="mb-2">⭐ Save favourite games</li>
                  <li class="mb-2">👤 User registration and login</li>
                  <li class="mb-2">☁️ Cloud-saved favourites</li>
                  <li class="mb-2">📝 User reviews and ratings</li>
                  <li class="mb-2">🔐 Firebase Authentication</li>
                  <li class="mb-2">🖼️ Lazy-loaded images</li>
                  <li class="mb-2">📱 Responsive interface</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-start">
            <div class="feature-icon">🎯</div>
            <h3>Project Purpose</h3>
            <p class="text-muted">
              GameHub was created as part of the COS30043 Full-Stack Development course.
              The project demonstrates a complete modern web application showcasing Vue 3 frontend
              development, component-based architecture, API integration, and responsive design principles.
              It serves as a portfolio piece demonstrating full-stack web development capabilities.
            </p>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-start">
            <div class="feature-icon">👨‍💻</div>
            <h3>Developer</h3>

            <p class="text-muted">
              Developed by Nam Hung Truong
              as part of COS30043 Full Stack Development.
            </p>

            <p class="text-muted">
              The project demonstrates modern web development
              using Vue 3, Firebase, REST APIs,
              component-based architecture,
              and responsive design.
            </p>

          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-start">
            <div class="feature-icon">🔗</div>
            <h3>APIs Used</h3>
            <ul style="list-style: none; padding: 0;">
              <li class="mb-3">
                <strong class="d-block">🎮 FreeToGame API</strong>
                <span class="text-muted" style="font-size: 0.9rem;">
                  Provides access to 500+ free-to-play games with detailed information, genres, screenshots, and platform availability
                </span>
              </li>
              <li>
                <strong class="d-block">📰 NewsAPI</strong>
                <span class="text-muted" style="font-size: 0.9rem;">
                  Delivers real-time gaming news and industry updates from multiple gaming news sources
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-start">
            <div class="feature-icon">🚀</div>
            <h3>Future Development</h3>
            <p class="text-muted">
              GameHub is continuously evolving.
              Future enhancements may include:
            </p>
            <ul class="list-unstyled">
              <li class="mb-2">💬 User-generated reviews</li>
              <li class="mb-2">🤖 Game recommendation system</li>
              <li class="mb-2">☁️ Cloud-based favourites</li>
              <li class="mb-2">🔧 Admin news management</li>
              <li class="mb-2">🔍 Advanced search and filtering</li>
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

            <hr style="border-color: var(--border-glass);">

            <!-- Scene Picker -->
            <h6 class="mb-2">🗺️ Choose Your Adventure</h6>
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
              v-lazy-img="sceneImage"
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