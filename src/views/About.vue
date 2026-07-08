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
        ? 'Mountain Explorer'
        : 'Ocean Voyager'
    }
  }
}
</script>

<template>
  <div class="container py-4">

    <div class="section-header">
      <span class="section-icon"><i class="bi bi-info-circle-fill"></i></span>
      <h1 class="mb-0">About GameHub</h1>
    </div>

    <div class="row g-4">

      <!-- Left Column: Main Content -->
      <div class="col-md-8">

        <div class="card mb-4">
          <div class="card-body text-start">
            <div class="feature-icon"><i class="bi bi-controller"></i></div>
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
            <div class="feature-icon"><i class="bi bi-tools"></i></div>
            <h3>Technologies Used</h3>
            <div class="row mt-3">
              <div class="col-6">
                <ul class="list-unstyled">
                  <li class="mb-2"><i class="bi bi-circle-fill text-success me-2" style="font-size:0.5rem;vertical-align:middle;"></i>Vue 3</li>
                  <li class="mb-2"><i class="bi bi-arrow-left-right me-2 text-primary"></i>Vue Router</li>
                  <li class="mb-2"><i class="bi bi-palette me-2 text-info"></i>Bootstrap 5</li>
                  <li class="mb-2"><i class="bi bi-shield-lock me-2 text-warning"></i>Firebase Auth</li>
                </ul>
              </div>
              <div class="col-6">
                <ul class="list-unstyled">
                  <li class="mb-2"><i class="bi bi-database me-2 text-danger"></i>Firebase Firestore</li>
                  <li class="mb-2"><i class="bi bi-controller me-2 text-success"></i>FreeToGame API</li>
                  <li class="mb-2"><i class="bi bi-newspaper me-2 text-primary"></i>NewsAPI</li>
                  <li class="mb-2"><i class="bi bi-lightning me-2 text-warning"></i>Vite</li>
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
            <div class="feature-icon"><i class="bi bi-stars"></i></div>
            <h3>Features</h3>
            <div class="row mt-3">
              <div class="col-md-6">
                <ul class="list-unstyled">
                  <li class="mb-2"><i class="bi bi-controller me-2"></i>Browse free-to-play games</li>
                  <li class="mb-2"><i class="bi bi-search me-2"></i>Search games by title</li>
                  <li class="mb-2"><i class="bi bi-tags me-2"></i>Filter games by genre</li>
                  <li class="mb-2"><i class="bi bi-list-ul me-2"></i>View detailed game information</li>
                  <li class="mb-2"><i class="bi bi-camera me-2"></i>View screenshots</li>
                  <li class="mb-2"><i class="bi bi-broadcast me-2"></i>Live gaming news via NewsAPI</li>
                  <li class="mb-2"><i class="bi bi-newspaper me-2"></i>GameHub archived news</li>
                </ul>
              </div>
              <div class="col-md-6">
                <ul class="list-unstyled">
                  <li class="mb-2"><i class="bi bi-star me-2"></i>Save favourite games</li>
                  <li class="mb-2"><i class="bi bi-person me-2"></i>User registration and login</li>
                  <li class="mb-2"><i class="bi bi-cloud me-2"></i>Cloud-saved favourites</li>
                  <li class="mb-2"><i class="bi bi-pencil-square me-2"></i>User reviews and ratings</li>
                  <li class="mb-2"><i class="bi bi-shield-lock me-2"></i>Firebase Authentication</li>
                  <li class="mb-2"><i class="bi bi-image me-2"></i>Lazy-loaded images</li>
                  <li class="mb-2"><i class="bi bi-phone me-2"></i>Responsive interface</li>
                </ul>
              </div>
            </div>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-start">
            <div class="feature-icon"><i class="bi bi-crosshair"></i></div>
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
            <div class="feature-icon"><i class="bi bi-code-slash"></i></div>
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
            <div class="feature-icon"><i class="bi bi-link-45deg"></i></div>
            <h3>APIs Used</h3>
            <ul style="list-style: none; padding: 0;">
              <li class="mb-3">
                <strong class="d-block"><i class="bi bi-controller me-1"></i>FreeToGame API</strong>
                <span class="text-muted" style="font-size: 0.9rem;">
                  Provides access to 500+ free-to-play games with detailed information, genres, screenshots, and platform availability
                </span>
              </li>
              <li>
                <strong class="d-block"><i class="bi bi-newspaper me-1"></i>NewsAPI</strong>
                <span class="text-muted" style="font-size: 0.9rem;">
                  Delivers real-time gaming news and industry updates from multiple gaming news sources
                </span>
              </li>
            </ul>
          </div>
        </div>

        <div class="card mb-4">
          <div class="card-body text-start">
            <div class="feature-icon"><i class="bi bi-rocket"></i></div>
            <h3>Future Development</h3>
            <p class="text-muted">
              GameHub is continuously evolving.
              Future enhancements may include:
            </p>
            <ul class="list-unstyled">
              <li class="mb-2"><i class="bi bi-chat-left-text me-2"></i>User-generated reviews</li>
              <li class="mb-2"><i class="bi bi-cpu me-2"></i>Game recommendation system</li>
              <li class="mb-2"><i class="bi bi-cloud me-2"></i>Cloud-based favourites</li>
              <li class="mb-2"><i class="bi bi-wrench me-2"></i>Admin news management</li>
              <li class="mb-2"><i class="bi bi-funnel me-2"></i>Advanced search and filtering</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="col-md-4">

        <div style="position: sticky; top: 80px;">
          <div class="card mb-4">
            <div class="card-body text-start">

            <h5 class="card-title mb-3"><i class="bi bi-controller me-2"></i>Gamer Profile</h5>
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
              <i class="bi bi-controller me-1"></i>Welcome, {{ fullName }}!

              <br>

              <strong>
                {{ gamerTitle }}
              </strong>
            </div>

            <hr style="border-color: var(--border-glass);">

            <!-- Scene Picker -->
            <h6 class="mb-2"><i class="bi bi-map me-1"></i>Choose Your Adventure</h6>
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
                  <i class="bi bi-triangle me-1"></i>Mountain Realm
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
                  <i class="bi bi-water me-1"></i>Ocean Kingdom
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

  </div>
</template>