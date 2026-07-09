// src/views/About.vue
<script>
export default {
  data() {
    return {
      firstName: '',
      lastName: '',
      selectedScene: 'mountain',
      activeTab: 'features',
      genreIcons: [
        { name: 'MMORPG',        src: '/game_icon/mmorpg.png' },
        { name: 'Shooter',       src: '/game_icon/shooter.png' },
        { name: 'MOBA',          src: '/game_icon/moba.png' },
        { name: 'Strategy',      src: '/game_icon/strategy.png' },
        { name: 'Battle Royale', src: '/game_icon/battle_royale.png' },
        { name: 'Sci-Fi',        src: '/game_icon/sci-fi.png' },
        { name: 'Fantasy',       src: '/game_icon/fantasy.png' },
        { name: 'Sports',        src: '/game_icon/sports.png' },
        { name: 'Racing',        src: '/game_icon/racing.png' },
        { name: 'Anime',         src: '/game_icon/anime.png' },
        { name: 'Horror',        src: '/game_icon/horror.png' },
        { name: 'Survival',      src: '/game_icon/survival.png' }
      ]
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
    },

    gamerEmoji() {
      return this.selectedScene === 'mountain' ? '🏔️' : '🌊'
    }
  }
}
</script>

<template>
  <div class="about-page">

    <!-- Hero -->
    <div class="about-hero">
      <div class="about-hero-bg">
        <div class="about-hero-orb orb-1"></div>
        <div class="about-hero-orb orb-2"></div>
        <div class="about-hero-orb orb-3"></div>
      </div>
      <div class="container about-hero-content">
        <div class="about-hero-badge">
          <i class="bi bi-controller me-2"></i>COS30043 Final Project
        </div>
        <h1 class="about-hero-title">About <span class="about-gradient-text">GameHub</span></h1>
        <p class="about-hero-sub">
          A modern Vue 3 gaming platform for discovering free-to-play games,
          breaking gaming news, and building your personal collection.
        </p>

        <!-- Stat Pills -->
        <div class="about-stat-row">
          <div class="about-stat-pill">
            <i class="bi bi-controller"></i>
            <strong>300+</strong>
            <span>Games</span>
          </div>
          <div class="about-stat-pill">
            <i class="bi bi-broadcast"></i>
            <strong>24/7</strong>
            <span>Live News</span>
          </div>
          <div class="about-stat-pill">
            <i class="bi bi-link-45deg"></i>
            <strong>4</strong>
            <span>APIs</span>
          </div>
          <div class="about-stat-pill">
            <i class="bi bi-shield-lock"></i>
            <strong>Firebase</strong>
            <span>Auth & DB</span>
          </div>
        </div>
      </div>
    </div>

    <div class="container about-body">
      <div class="row g-4">

        <!-- Left / Main Column -->
        <div class="col-lg-8">

          <!-- Welcome Card -->
          <div class="about-card about-card-welcome mb-4">
            <div class="about-card-glow"></div>
            <div class="about-card-inner">
              <div class="about-section-icon" style="background: rgba(124,58,237,0.15); color: var(--primary-light);">
                <i class="bi bi-stars"></i>
              </div>
              <div>
                <h2 class="about-section-title">Welcome to GameHub</h2>
                <p class="about-section-lead">
                  Discover free-to-play games, explore gaming news,
                  and build your personal collection of favourite titles.
                </p>
                <p class="about-section-body">
                  GameHub is a full-stack web application built with Vue 3 that allows users
                  to browse free-to-play games, search for titles, filter by genre, and view
                  detailed game information — powered by FreeToGame, RAWG, CheapShark, and
                  NewsAPI, all backed by Firebase cloud storage and authentication.
                </p>
              </div>
            </div>
          </div>

          <!-- Tab Nav -->
          <div class="about-tabs mb-4">
            <button
              class="about-tab-btn"
              :class="{ active: activeTab === 'features' }"
              @click="activeTab = 'features'"
            >
              <i class="bi bi-stars me-1"></i>Features
            </button>
            <button
              class="about-tab-btn"
              :class="{ active: activeTab === 'tech' }"
              @click="activeTab = 'tech'"
            >
              <i class="bi bi-tools me-1"></i>Technologies
            </button>
            <button
              class="about-tab-btn"
              :class="{ active: activeTab === 'apis' }"
              @click="activeTab = 'apis'"
            >
              <i class="bi bi-link-45deg me-1"></i>APIs
            </button>
            <button
              class="about-tab-btn"
              :class="{ active: activeTab === 'future' }"
              @click="activeTab = 'future'"
            >
              <i class="bi bi-rocket me-1"></i>Roadmap
            </button>
          </div>

          <!-- Features Tab -->
          <div v-if="activeTab === 'features'" class="about-card mb-4 fade-tab">
            <h3 class="about-card-heading"><i class="bi bi-stars me-2 text-warning"></i>Platform Features</h3>
            <div class="about-feature-grid">
              <div class="about-feature-item">
                <div class="about-feature-icon-wrap" style="background: rgba(124,58,237,0.12);">
                  <i class="bi bi-controller" style="color: var(--primary-light);"></i>
                </div>
                <div>
                  <strong>Browse Games</strong>
                  <p>Explore 300+ free-to-play titles with genre filters</p>
                </div>
              </div>
              <div class="about-feature-item">
                <div class="about-feature-icon-wrap" style="background: rgba(6,182,212,0.12);">
                  <i class="bi bi-search" style="color: var(--accent-light);"></i>
                </div>
                <div>
                  <strong>Smart Search</strong>
                  <p>Instant title search across the full game library</p>
                </div>
              </div>
              <div class="about-feature-item">
                <div class="about-feature-icon-wrap" style="background: rgba(244,63,94,0.12);">
                  <i class="bi bi-star-fill" style="color: #f59e0b;"></i>
                </div>
                <div>
                  <strong>Favorites</strong>
                  <p>Cloud-saved personal collection via Firestore</p>
                </div>
              </div>
              <div class="about-feature-item">
                <div class="about-feature-icon-wrap" style="background: rgba(34,197,94,0.12);">
                  <i class="bi bi-broadcast" style="color: var(--success);"></i>
                </div>
                <div>
                  <strong>Live News</strong>
                  <p>Real-time gaming news powered by NewsAPI</p>
                </div>
              </div>
              <div class="about-feature-item">
                <div class="about-feature-icon-wrap" style="background: rgba(245,158,11,0.12);">
                  <i class="bi bi-shield-lock" style="color: var(--warning);"></i>
                </div>
                <div>
                  <strong>Auth System</strong>
                  <p>User registration & login with Firebase Auth</p>
                </div>
              </div>
              <div class="about-feature-item">
                <div class="about-feature-icon-wrap" style="background: rgba(124,58,237,0.12);">
                  <i class="bi bi-camera" style="color: var(--primary-light);"></i>
                </div>
                <div>
                  <strong>Screenshots</strong>
                  <p>Lazy-loaded game screenshots & media gallery</p>
                </div>
              </div>
              <div class="about-feature-item">
                <div class="about-feature-icon-wrap" style="background: rgba(6,182,212,0.12);">
                  <i class="bi bi-pencil-square" style="color: var(--accent-light);"></i>
                </div>
                <div>
                  <strong>Reviews & Ratings</strong>
                  <p>User reviews stored in Firestore</p>
                </div>
              </div>
              <div class="about-feature-item">
                <div class="about-feature-icon-wrap" style="background: rgba(34,197,94,0.12);">
                  <i class="bi bi-phone" style="color: var(--success);"></i>
                </div>
                <div>
                  <strong>Responsive Design</strong>
                  <p>Optimised for desktop, tablet &amp; mobile</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Tech Tab -->
          <div v-if="activeTab === 'tech'" class="about-card mb-4 fade-tab">
            <h3 class="about-card-heading"><i class="bi bi-tools me-2 text-info"></i>Technologies Used</h3>
            <div class="about-tech-grid">
              <div class="about-tech-chip">
                <span class="about-tech-dot" style="background:#42b883;"></span>Vue 3
              </div>
              <div class="about-tech-chip">
                <span class="about-tech-dot" style="background:#7c3aed;"></span>Vue Router
              </div>
              <div class="about-tech-chip">
                <span class="about-tech-dot" style="background:#7952b3;"></span>Bootstrap 5
              </div>
              <div class="about-tech-chip">
                <span class="about-tech-dot" style="background:#f59e0b;"></span>Firebase Auth
              </div>
              <div class="about-tech-chip">
                <span class="about-tech-dot" style="background:#ef4444;"></span>Firestore
              </div>
              <div class="about-tech-chip">
                <span class="about-tech-dot" style="background:#06b6d4;"></span>FreeToGame API
              </div>
              <div class="about-tech-chip">
                <span class="about-tech-dot" style="background:#22c55e;"></span>NewsAPI
              </div>
              <div class="about-tech-chip">
                <span class="about-tech-dot" style="background:#f59e0b;"></span>RAWG API
              </div>
              <div class="about-tech-chip">
                <span class="about-tech-dot" style="background:#34d399;"></span>CheapShark API
              </div>
              <div class="about-tech-chip">
                <span class="about-tech-dot" style="background:#a78bfa;"></span>Vite
              </div>
              <div class="about-tech-chip">
                <span class="about-tech-dot" style="background:#f0f4ff;"></span>Vanilla CSS
              </div>
              <div class="about-tech-chip">
                <span class="about-tech-dot" style="background:#fb7185;"></span>Bootstrap Icons
              </div>
            </div>

            <div class="about-purpose-block mt-4">
              <i class="bi bi-crosshair me-2" style="color: var(--accent);"></i>
              <div>
                <strong>Project Purpose</strong>
                <p>
                  GameHub was created as part of the COS30043 Full-Stack Development course.
                  It demonstrates a complete modern web application showcasing Vue 3 frontend
                  development, component-based architecture, API integration, Firebase cloud
                  services, and responsive design principles.
                </p>
              </div>
            </div>
          </div>

          <!-- APIs Tab -->
          <div v-if="activeTab === 'apis'" class="about-card mb-4 fade-tab">
            <h3 class="about-card-heading"><i class="bi bi-link-45deg me-2 text-success"></i>External APIs</h3>

            <div class="about-api-card">
              <div class="about-api-icon" style="background: rgba(34,197,94,0.12); color: #4ade80;">
                <i class="bi bi-controller"></i>
              </div>
              <div class="about-api-info">
                <strong>FreeToGame API</strong>
                <p>Provides access to 500+ free-to-play games with detailed information,
                  genres, screenshots, system requirements, and platform availability.
                  Drives the Free-to-Play section.</p>
                <span class="about-api-badge" style="border-color: rgba(34,197,94,0.4); color: #4ade80;">
                  <i class="bi bi-circle-fill me-1" style="font-size:0.4rem;"></i>Active
                </span>
              </div>
            </div>

            <div class="about-api-card">
              <div class="about-api-icon" style="background: rgba(245,158,11,0.12); color: #fbbf24;">
                <i class="bi bi-joystick"></i>
              </div>
              <div class="about-api-info">
                <strong>RAWG Video Games Database API</strong>
                <p>Powers the main Games section with a massive library of 500,000+ games,
                  rich metadata, ratings, genres, screenshots, and release information
                  spanning all major gaming platforms.</p>
                <span class="about-api-badge" style="border-color: rgba(245,158,11,0.4); color: #fbbf24;">
                  <i class="bi bi-circle-fill me-1" style="font-size:0.4rem;"></i>Active
                </span>
              </div>
            </div>

            <div class="about-api-card">
              <div class="about-api-icon" style="background: rgba(52,211,153,0.12); color: #34d399;">
                <i class="bi bi-tags"></i>
              </div>
              <div class="about-api-info">
                <strong>CheapShark Deals API</strong>
                <p>Aggregates PC game deals and price comparisons from major stores like
                  Steam, Epic, GOG, and more. Powers the Deals section to help gamers
                  find the best prices on their favourite titles.</p>
                <span class="about-api-badge" style="border-color: rgba(52,211,153,0.4); color: #34d399;">
                  <i class="bi bi-circle-fill me-1" style="font-size:0.4rem;"></i>Active
                </span>
              </div>
            </div>

            <div class="about-api-card">
              <div class="about-api-icon" style="background: rgba(6,182,212,0.12); color: var(--accent-light);">
                <i class="bi bi-newspaper"></i>
              </div>
              <div class="about-api-info">
                <strong>NewsAPI</strong>
                <p>Delivers real-time gaming news and industry updates from multiple
                  major gaming news outlets. Powers the Live News section with
                  continuously updated articles from top gaming publications.</p>
                <span class="about-api-badge" style="border-color: rgba(6,182,212,0.4); color: var(--accent-light);">
                  <i class="bi bi-circle-fill me-1" style="font-size:0.4rem;"></i>Active
                </span>
              </div>
            </div>

            <!-- Genre Icons using game_icon assets -->
            <div class="about-genre-icons">
              <h6 class="about-genre-icons-title"><i class="bi bi-grid me-1"></i>Game Genre Icons</h6>
              <div class="about-genre-icons-grid">
                <div class="about-genre-icon-item" v-for="genre in genreIcons" :key="genre.name">
                  <img :src="genre.src" :alt="genre.name" class="about-genre-img">
                  <span>{{ genre.name }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Roadmap Tab -->
          <div v-if="activeTab === 'future'" class="about-card mb-4 fade-tab">
            <h3 class="about-card-heading"><i class="bi bi-rocket me-2" style="color: var(--accent2-light);"></i>Future Roadmap</h3>
            <p class="about-section-body mb-3">GameHub is continuously evolving. Planned enhancements include:</p>
            <div class="about-roadmap">
              <div class="about-roadmap-item">
                <div class="about-roadmap-dot" style="background: var(--primary);"></div>
                <div>
                  <strong>Game Recommendation Engine</strong>
                  <p>AI-powered suggestions based on your favorites and play history</p>
                </div>
              </div>
              <div class="about-roadmap-item">
                <div class="about-roadmap-dot" style="background: var(--accent);"></div>
                <div>
                  <strong>Advanced Search &amp; Filtering</strong>
                  <p>Multi-tag filters, platform selection, and release date range</p>
                </div>
              </div>
              <div class="about-roadmap-item">
                <div class="about-roadmap-dot" style="background: #f59e0b;"></div>
                <div>
                  <strong>User-generated Reviews</strong>
                  <p>Rich text reviews with ratings, verified playtime, and helpfulness votes</p>
                </div>
              </div>
              <div class="about-roadmap-item">
                <div class="about-roadmap-dot" style="background: var(--success);"></div>
                <div>
                  <strong>Social Features</strong>
                  <p>Follow friends, share collections, and compare libraries</p>
                </div>
              </div>
              <div class="about-roadmap-item">
                <div class="about-roadmap-dot" style="background: var(--accent2);"></div>
                <div>
                  <strong>Enhanced Admin Dashboard</strong>
                  <p>Advanced news management, analytics, and moderation tools</p>
                </div>
              </div>
            </div>
          </div>

        </div>

        <!-- Right / Sidebar -->
        <div class="col-lg-4">
          <div style="position: sticky; top: 80px; display: flex; flex-direction: column; gap: 1.25rem;">

            <!-- Developer Card -->
            <div class="about-card about-dev-card">
              <div class="about-dev-avatar">
                <i class="bi bi-person-circle"></i>
              </div>
              <div class="about-dev-name">Nam Hung Truong</div>
              <div class="about-dev-role">
                <i class="bi bi-code-slash me-1"></i>Full-Stack Developer
              </div>
              <p class="about-dev-desc">
                COS30043 Full Stack Development student building modern web experiences with Vue 3 and Firebase.
              </p>
              <div class="about-dev-tags">
                <span class="about-dev-tag">Vue 3</span>
                <span class="about-dev-tag">Firebase</span>
                <span class="about-dev-tag">REST APIs</span>
              </div>
            </div>

            <!-- Gamer Profile Card -->
            <div class="about-card about-gamer-card">
              <h5 class="about-card-heading mb-0">
                <i class="bi bi-joystick me-2" style="color: var(--primary-light);"></i>Gamer Profile
              </h5>
              <p class="about-section-body mb-3" style="font-size: 0.82rem;">
                Create your gaming identity and choose your adventure.
              </p>

              <div class="about-field">
                <label for="firstName" class="about-label">First Name</label>
                <input
                  id="firstName"
                  v-model="firstName"
                  type="text"
                  class="about-input"
                  placeholder="Your first name"
                >
              </div>

              <div class="about-field">
                <label for="lastName" class="about-label">Last Name</label>
                <input
                  id="lastName"
                  v-model="lastName"
                  type="text"
                  class="about-input"
                  placeholder="Your last name"
                >
              </div>

              <!-- Welcome message -->
              <div v-if="fullName" class="about-welcome">
                <div class="about-welcome-icon">🎮</div>
                <div>
                  <strong>Welcome, {{ fullName }}!</strong>
                  <div class="about-welcome-title">{{ gamerEmoji }} {{ gamerTitle }}</div>
                </div>
              </div>

              <hr class="about-divider">

              <h6 class="about-label mb-2"><i class="bi bi-map me-1"></i>Choose Your Adventure</h6>
              <p class="about-section-body mb-3" style="font-size: 0.8rem;">Select the world you would like to explore.</p>

              <div class="about-scene-btns">
                <button
                  class="about-scene-btn"
                  :class="{ active: selectedScene === 'mountain' }"
                  @click="selectedScene = 'mountain'"
                >
                  <i class="bi bi-triangle me-1"></i>Mountain Realm
                </button>
                <button
                  class="about-scene-btn"
                  :class="{ active: selectedScene === 'ocean' }"
                  @click="selectedScene = 'ocean'"
                >
                  <i class="bi bi-water me-1"></i>Ocean Kingdom
                </button>
              </div>

              <div class="about-scene-img-wrap">
                <img
                  v-lazy-img="sceneImage"
                  :alt="selectedScene"
                  class="about-scene-img"
                >
                <div class="about-scene-label">
                  {{ selectedScene === 'mountain' ? '🏔️ You are a fearless Mountain Explorer.' : '🌊 You are an adventurous Ocean Voyager.' }}
                </div>
              </div>

            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ===== Page ===== */
.about-page {
  min-height: 100vh;
  background: var(--bg-deep);
}

/* ===== Hero ===== */
.about-hero {
  position: relative;
  padding: 4rem 0 3.5rem;
  overflow: hidden;
  border-bottom: 1px solid var(--border-subtle);
  text-align: center;
}

.about-hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.about-hero-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
}

.orb-1 {
  width: 500px; height: 500px;
  background: rgba(124,58,237,0.12);
  top: -200px; left: -100px;
}

.orb-2 {
  width: 400px; height: 400px;
  background: rgba(6,182,212,0.08);
  top: -100px; right: -50px;
}

.orb-3 {
  width: 300px; height: 300px;
  background: rgba(244,63,94,0.06);
  bottom: -100px; left: 40%;
}

.about-hero-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1.25rem;
}

.about-hero-badge {
  display: inline-flex;
  align-items: center;
  padding: 5px 16px;
  border-radius: 30px;
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  background: rgba(124,58,237,0.12);
  border: 1px solid rgba(124,58,237,0.3);
  color: var(--primary-light);
}

.about-hero-title {
  font-size: clamp(2rem, 5vw, 3.2rem);
  font-weight: 900;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.15;
}

.about-gradient-text {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.about-hero-sub {
  color: var(--text-secondary);
  font-size: 1rem;
  max-width: 600px;
  line-height: 1.7;
  margin: 0;
}

/* ===== Stat Pills ===== */
.about-stat-row {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  justify-content: center;
  margin-top: 0.5rem;
}

.about-stat-pill {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 10px 20px;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 50px;
  backdrop-filter: var(--glass-blur);
  font-size: 0.85rem;
  color: var(--text-secondary);
  transition: border-color 0.2s, transform 0.2s;
}

.about-stat-pill:hover {
  border-color: rgba(124,58,237,0.35);
  transform: translateY(-2px);
}

.about-stat-pill i { color: var(--primary-light); }
.about-stat-pill strong { color: var(--text-primary); font-weight: 700; }

/* ===== Body ===== */
.about-body {
  padding-top: 2.5rem;
  padding-bottom: 4rem;
}

/* ===== Cards ===== */
.about-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  backdrop-filter: var(--glass-blur);
  position: relative;
  overflow: hidden;
  transition: border-color 0.25s;
}

.about-card:hover {
  border-color: rgba(124,58,237,0.25);
}

.about-card-welcome {
  border-color: rgba(124,58,237,0.2);
}

.about-card-glow {
  position: absolute;
  top: -80px; right: -80px;
  width: 250px; height: 250px;
  border-radius: 50%;
  background: radial-gradient(ellipse, rgba(124,58,237,0.1) 0%, transparent 70%);
  pointer-events: none;
}

.about-card-inner {
  display: flex;
  gap: 1.25rem;
  position: relative;
}

.about-section-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
  flex-shrink: 0;
}

.about-section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem;
}

.about-section-lead {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin-bottom: 0.75rem;
  font-style: italic;
}

.about-section-body {
  color: var(--text-secondary);
  font-size: 0.88rem;
  line-height: 1.7;
  margin: 0;
}

.about-card-heading {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 1.25rem;
}

/* ===== Tabs ===== */
.about-tabs {
  display: flex;
  gap: 4px;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 14px;
  padding: 5px;
  backdrop-filter: var(--glass-blur);
  flex-wrap: wrap;
}

.about-tab-btn {
  flex: 1;
  min-width: 100px;
  padding: 8px 12px;
  border-radius: 10px;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 0.82rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.about-tab-btn:hover {
  color: var(--text-primary);
  background: var(--bg-glass-hover);
}

.about-tab-btn.active {
  background: rgba(124,58,237,0.22);
  color: var(--primary-light);
  font-weight: 700;
}

/* ===== Feature Grid ===== */
.about-feature-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.about-feature-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem;
  border-radius: 12px;
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border-subtle);
  transition: border-color 0.2s, background 0.2s;
}

.about-feature-item:hover {
  border-color: rgba(124,58,237,0.25);
  background: rgba(124,58,237,0.04);
}

.about-feature-icon-wrap {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.95rem;
  flex-shrink: 0;
}

.about-feature-item strong {
  display: block;
  font-size: 0.85rem;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.about-feature-item p {
  font-size: 0.78rem;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.4;
}

/* ===== Tech Grid ===== */
.about-tech-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.about-tech-chip {
  display: flex;
  align-items: center;
  gap: 7px;
  padding: 7px 14px;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-glass);
  border-radius: 30px;
  font-size: 0.82rem;
  color: var(--text-primary);
  transition: border-color 0.2s, transform 0.2s;
}
.about-tech-chip:hover {
  border-color: rgba(124,58,237,0.3);
  transform: translateY(-1px);
}

.about-tech-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.about-purpose-block {
  display: flex;
  gap: 0.75rem;
  align-items: flex-start;
  padding: 1rem;
  border-radius: 12px;
  background: rgba(6,182,212,0.05);
  border: 1px solid rgba(6,182,212,0.15);
}
.about-purpose-block strong { display: block; color: var(--text-primary); margin-bottom: 4px; font-size: 0.9rem; }
.about-purpose-block p { margin: 0; color: var(--text-secondary); font-size: 0.82rem; line-height: 1.6; }

/* ===== API Cards ===== */
.about-api-card {
  display: flex;
  gap: 1rem;
  padding: 1.1rem;
  border-radius: 14px;
  background: rgba(255,255,255,0.02);
  border: 1px solid var(--border-subtle);
  margin-bottom: 1rem;
  transition: border-color 0.2s;
}
.about-api-card:hover { border-color: rgba(124,58,237,0.25); }
.about-api-card:last-child { margin-bottom: 0; }

.about-api-icon {
  width: 44px; height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  flex-shrink: 0;
}

.about-api-info strong {
  display: block;
  font-size: 0.92rem;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.about-api-info p {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin: 0 0 0.6rem;
  line-height: 1.5;
}

.about-api-badge {
  display: inline-flex;
  align-items: center;
  font-size: 0.72rem;
  font-weight: 600;
  padding: 2px 10px;
  border-radius: 20px;
  border: 1px solid;
  background: transparent;
}

/* ===== Roadmap ===== */
.about-roadmap {
  display: flex;
  flex-direction: column;
  gap: 0;
  position: relative;
}

.about-roadmap::before {
  content: '';
  position: absolute;
  left: 7px;
  top: 12px;
  bottom: 12px;
  width: 2px;
  background: linear-gradient(180deg, var(--primary), var(--accent), #f59e0b, var(--success), var(--accent2));
  opacity: 0.3;
}

.about-roadmap-item {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
  padding: 0.75rem 0 0.75rem 0;
  position: relative;
}

.about-roadmap-dot {
  width: 16px; height: 16px;
  border-radius: 50%;
  flex-shrink: 0;
  margin-top: 2px;
  position: relative;
  z-index: 1;
  box-shadow: 0 0 8px currentColor;
}

.about-roadmap-item strong {
  display: block;
  font-size: 0.88rem;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.about-roadmap-item p {
  font-size: 0.8rem;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.4;
}

/* ===== Developer Card ===== */
.about-dev-card {
  text-align: center;
  background: linear-gradient(135deg, rgba(124,58,237,0.1), rgba(6,182,212,0.06));
  border-color: rgba(124,58,237,0.2);
}

.about-dev-avatar {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(6,182,212,0.2));
  border: 2px solid rgba(124,58,237,0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: var(--primary-light);
  margin: 0 auto 1rem;
}

.about-dev-name {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--text-primary);
  margin-bottom: 0.25rem;
}

.about-dev-role {
  font-size: 0.8rem;
  color: var(--primary-light);
  margin-bottom: 0.75rem;
}

.about-dev-desc {
  font-size: 0.82rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.about-dev-tags {
  display: flex;
  gap: 6px;
  justify-content: center;
  flex-wrap: wrap;
}

.about-dev-tag {
  font-size: 0.72rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  background: rgba(124,58,237,0.12);
  border: 1px solid rgba(124,58,237,0.25);
  color: var(--primary-light);
}

/* ===== Gamer Profile Card ===== */
.about-gamer-card {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.about-field {
  margin-bottom: 0.875rem;
}

.about-label {
  display: block;
  font-size: 0.78rem;
  color: var(--text-secondary);
  margin-bottom: 5px;
  font-weight: 500;
}

.about-input {
  width: 100%;
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border-glass);
  border-radius: 9px;
  color: var(--text-primary);
  padding: 8px 12px;
  font-size: 0.85rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}
.about-input::placeholder { color: var(--text-muted); }
.about-input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(124,58,237,0.15);
}

.about-welcome {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem;
  border-radius: 12px;
  background: rgba(34,197,94,0.08);
  border: 1px solid rgba(34,197,94,0.2);
  margin-bottom: 0.875rem;
}

.about-welcome-icon { font-size: 1.5rem; flex-shrink: 0; }
.about-welcome strong { display: block; color: var(--text-primary); font-size: 0.88rem; }
.about-welcome-title { font-size: 0.78rem; color: var(--success); margin-top: 2px; }

.about-divider {
  border: none;
  border-top: 1px solid var(--border-subtle);
  margin: 0.75rem 0;
}

/* Scene buttons */
.about-scene-btns {
  display: flex;
  gap: 8px;
  margin-bottom: 1rem;
}

.about-scene-btn {
  flex: 1;
  padding: 8px 10px;
  border-radius: 10px;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  color: var(--text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}

.about-scene-btn:hover {
  border-color: var(--primary-light);
  color: var(--primary-light);
}

.about-scene-btn.active {
  background: rgba(124,58,237,0.2);
  border-color: var(--primary);
  color: var(--primary-light);
  font-weight: 600;
}

.about-scene-img-wrap {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
}

.about-scene-img {
  width: 100%;
  height: 150px;
  object-fit: cover;
  display: block;
  transition: transform 0.4s;
}

.about-scene-img-wrap:hover .about-scene-img {
  transform: scale(1.04);
}

.about-scene-label {
  position: absolute;
  bottom: 0; left: 0; right: 0;
  background: linear-gradient(transparent, rgba(5,7,15,0.85));
  color: var(--text-secondary);
  font-size: 0.75rem;
  padding: 1.5rem 0.75rem 0.6rem;
  text-align: center;
}

/* ===== Tab fade animation ===== */
.fade-tab {
  animation: tab-in 0.3s ease;
}

@keyframes tab-in {
  from { opacity: 0; transform: translateY(8px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ===== Genre Icons Section ===== */
.about-genre-icons {
  margin-top: 1.5rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-subtle);
}

.about-genre-icons-title {
  font-size: 0.82rem;
  color: var(--text-secondary);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 0.875rem;
}

.about-genre-icons-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.about-genre-icon-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 10px;
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  transition: border-color 0.2s, transform 0.2s, background 0.2s;
  cursor: default;
  min-width: 70px;
}

.about-genre-icon-item:hover {
  border-color: rgba(124,58,237,0.3);
  background: rgba(124,58,237,0.06);
  transform: translateY(-2px);
}

.about-genre-img {
  width: 36px;
  height: 36px;
  object-fit: contain;
}

.about-genre-icon-item span {
  font-size: 0.68rem;
  color: var(--text-secondary);
  text-align: center;
  text-transform: capitalize;
  line-height: 1.2;
}

/* ===== Responsive ===== */
/* Tablet (iPad, 768px–1023px) */
@media (max-width: 1023px) {
  .about-hero { padding: 3rem 0 2.5rem; }
  .about-stat-pill { padding: 8px 14px; font-size: 0.8rem; }
  .about-genre-icons-grid { gap: 0.5rem; }
  .about-genre-icon-item { min-width: 60px; padding: 6px 8px; }
  .about-genre-img { width: 28px; height: 28px; }
}

/* Mobile (≤767px) */
@media (max-width: 767px) {
  .about-hero { padding: 2rem 0 1.5rem; }
  .about-hero-sub { font-size: 0.88rem; }
  .about-stat-row { gap: 0.5rem; }
  .about-stat-pill { padding: 7px 12px; font-size: 0.78rem; gap: 0.35rem; }
  .about-card-inner { flex-direction: column; }
  .about-feature-grid { grid-template-columns: 1fr; }
  .about-tabs {
    gap: 2px;
    padding: 4px;
    overflow-x: auto;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }
  .about-tabs::-webkit-scrollbar { display: none; }
  .about-tab-btn { font-size: 0.75rem; padding: 7px 10px; white-space: nowrap; flex-shrink: 0; }
  .about-api-card { flex-direction: column; gap: 0.75rem; }
  .about-api-icon { width: 36px; height: 36px; font-size: 0.9rem; }
  .about-roadmap::before { left: 6px; }
  .about-roadmap-dot { width: 14px; height: 14px; }
  .about-body { padding-top: 1.5rem; padding-bottom: 2.5rem; }
  .about-genre-icons-grid { gap: 0.4rem; }
  .about-genre-icon-item { min-width: 55px; padding: 5px 6px; }
  .about-genre-img { width: 24px; height: 24px; }
}
</style>