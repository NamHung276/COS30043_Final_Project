<script>
import { auth } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";

export default {
  name: "AboutView",
  data() {
    return {
      currentUser: null,
      unsubscribe: null,
      firstName: "",
      lastName: "",
      selectedScene: "mountain",
    };
  },
  computed: {
    fullName() {
      return `${this.firstName} ${this.lastName}`.trim();
    },
    sceneImage() {
      return this.selectedScene === "mountain"
        ? "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800&q=80"
        : "https://images.unsplash.com/photo-1505118380757-91f5f5632de0?w=800&q=80";
    },
    gamerTitle() {
      return this.selectedScene === "mountain"
        ? "Mountain Explorer"
        : "Ocean Voyager";
    },
    gamerEmoji() {
      return this.selectedScene === "mountain" ? "🏔️" : "🌊";
    },
  },
  mounted() {
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      this.currentUser = user;
    });
  },
  unmounted() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  },
};
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
        <h1 class="about-hero-title">
          Discover Your <span class="about-gradient-text">Next Adventure</span>
        </h1>
        <p class="about-hero-sub mt-3">
          GameHub helps players discover games, follow gaming news, build personal collections, and share reviews with the community.
        </p>
      </div>
    </div>

    <div class="container about-body">
      <div class="row g-5">
        <!-- Left / Main Column -->
        <div class="col-lg-8">
          
          <!-- Section 1: Why GameHub? -->
          <div class="mb-5">
            <h3 class="about-text-primary fw-bold mb-4">Why GameHub?</h3>
            <div class="row g-4">
              <!-- Cards -->
              <div class="col-md-6">
                <div class="about-feature-card h-100">
                  <div class="about-feature-icon" style="background: rgba(124, 58, 237, 0.15); color: var(--primary-light);">
                    <i class="bi bi-controller"></i>
                  </div>
                  <h5 class="about-text-primary fw-bold mt-3 mb-2">Discover Games</h5>
                  <p class="text-muted-light mb-0">Browse hundreds of free-to-play and premium games with advanced filters to find your exact match.</p>
                </div>
              </div>
              <div class="col-md-6">
                <div class="about-feature-card h-100">
                  <div class="about-feature-icon" style="background: rgba(6, 182, 212, 0.15); color: var(--accent-light);">
                    <i class="bi bi-newspaper"></i>
                  </div>
                  <h5 class="about-text-primary fw-bold mt-3 mb-2">Gaming News</h5>
                  <p class="text-muted-light mb-0">Stay updated with the latest industry news, announcements, and patch notes from top publications.</p>
                </div>
              </div>
              <div class="col-md-6">
                <div class="about-feature-card h-100">
                  <div class="about-feature-icon" style="background: rgba(245, 158, 11, 0.15); color: var(--warning);">
                    <i class="bi bi-star-fill"></i>
                  </div>
                  <h5 class="about-text-primary fw-bold mt-3 mb-2">Community Reviews</h5>
                  <p class="text-muted-light mb-0">See what other players think before you play. Share your own ratings and detailed reviews.</p>
                </div>
              </div>
              <div class="col-md-6">
                <div class="about-feature-card h-100">
                  <div class="about-feature-icon" style="background: rgba(244, 63, 94, 0.15); color: var(--danger);">
                    <i class="bi bi-heart-fill"></i>
                  </div>
                  <h5 class="about-text-primary fw-bold mt-3 mb-2">Build Your Collection</h5>
                  <p class="text-muted-light mb-0">Save your favorite titles, create custom wishlists, and track the games you want to play next.</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Section 2: Visuals -->
          <div class="mb-5">
            <h3 class="about-text-primary fw-bold mb-4">The Experience</h3>
            <div class="row g-4">
              <div class="col-12">
                <router-link to="/games" class="about-visual-card d-block text-decoration-none">
                  <div class="about-visual-img-wrap shadow mb-3 rounded-4 overflow-hidden position-relative">
                    <img src="https://images.unsplash.com/photo-1511512578047-dfb367046420?q=80&w=2071&auto=format&fit=crop" class="img-fluid w-100" alt="Browse Games">
                    <div class="about-visual-overlay">
                      <span class="fs-4 fw-bold about-text-primary"><i class="bi bi-controller me-2"></i>Browse Games</span>
                    </div>
                  </div>
                  <h5 class="about-text-primary fw-bold">Rich Game Library</h5>
                  <p class="text-muted-light mb-0">Explore a massive catalog with high-quality media, system requirements, and platform availability.</p>
                </router-link>
              </div>
              <div class="col-md-6">
                <router-link to="/live-news" class="about-visual-card d-block text-decoration-none">
                  <div class="about-visual-img-wrap shadow mb-3 rounded-4 overflow-hidden position-relative">
                    <img src="https://images.unsplash.com/photo-1542751371-adc38448a05e?q=80&w=2070&auto=format&fit=crop" class="img-fluid w-100" alt="Game Details">
                    <div class="about-visual-overlay">
                      <span class="fs-4 fw-bold about-text-primary"><i class="bi bi-people-fill me-2"></i>Community</span>
                    </div>
                  </div>
                  <h5 class="about-text-primary fw-bold">Live Community Hub</h5>
                  <p class="text-muted-light mb-0">Interact with players worldwide through reviews and community posts.</p>
                </router-link>
              </div>
              <div class="col-md-6">
                <router-link to="/profile" class="about-visual-card d-block text-decoration-none">
                  <div class="about-visual-img-wrap shadow mb-3 rounded-4 overflow-hidden position-relative">
                    <img src="https://images.unsplash.com/photo-1550745165-9bc0b252726f?q=80&w=2070&auto=format&fit=crop" class="img-fluid w-100" alt="User Collections">
                    <div class="about-visual-overlay">
                      <span class="fs-4 fw-bold about-text-primary"><i class="bi bi-person-circle me-2"></i>Profile</span>
                    </div>
                  </div>
                  <h5 class="about-text-primary fw-bold">Personalized Dashboard</h5>
                  <p class="text-muted-light mb-0">Manage your wishlist, library, and settings from a sleek unified account menu.</p>
                </router-link>
              </div>
            </div>
          </div>

          <!-- Section 3: Our Mission -->
          <div class="mb-5">
            <div class="about-card about-card-welcome">
              <div class="about-card-glow"></div>
              <div class="about-card-inner">
                <div class="about-section-icon" style="background: rgba(34, 197, 94, 0.15); color: var(--success);">
                  <i class="bi bi-bullseye"></i>
                </div>
                <div>
                  <h3 class="about-text-primary fw-bold mb-3">Our Mission</h3>
                  <p class="text-muted-light" style="font-size: 1.05rem; line-height: 1.7;">
                    We created GameHub to make discovering games simple. Instead of jumping between multiple websites for news, reviews, screenshots, and deals, GameHub brings everything together into one unified experience. Whether you're hunting for the next big free-to-play title or checking the latest patch notes, you'll find it here.
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Section 4: Meet the Developer -->
          <div class="mb-5">
            <h3 class="about-text-primary fw-bold mb-4">Meet the Developer</h3>
            <div class="about-card about-dev-card d-flex flex-column flex-md-row align-items-md-center gap-4 p-4">
              <div class="about-dev-avatar flex-shrink-0" style="width: 100px; height: 100px; font-size: 3rem;">
                <i class="bi bi-person-circle"></i>
              </div>
              <div>
                <h4 class="about-text-primary fw-bold mb-1">Nam Hung Truong</h4>
                <div class="text-primary mb-3"><i class="bi bi-code-slash me-2"></i>Full-Stack Developer</div>
                <p class="text-muted-light mb-3">
                  GameHub was built as a full-stack university project focused on creating a modern gaming platform with authentication, cloud storage, community features, and live game information.
                </p>
                <div class="d-flex gap-2 flex-wrap">
                  <span class="badge bg-secondary bg-opacity-25 text-light px-3 py-2 rounded-pill">Vue 3</span>
                  <span class="badge bg-secondary bg-opacity-25 text-light px-3 py-2 rounded-pill">Firebase</span>
                  <span class="badge bg-secondary bg-opacity-25 text-light px-3 py-2 rounded-pill">REST APIs</span>
                  <span class="badge bg-secondary bg-opacity-25 text-light px-3 py-2 rounded-pill">UI/UX Design</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Section 5: CTA -->
          <div class="about-card p-5 text-center mb-5" style="background: linear-gradient(145deg, rgba(124, 58, 237, 0.1), transparent); border-color: rgba(124, 58, 237, 0.2);">
            <h3 class="about-text-primary fw-bold mb-3">Ready to start exploring?</h3>
            <p class="text-muted-light mb-4">Jump right in and find your next favorite game or catch up on the latest announcements.</p>
            <div class="d-flex justify-content-center flex-wrap gap-3">
              <router-link to="/games" class="btn btn-primary px-4 py-2 rounded-pill fw-bold shadow-sm">
                Browse Games
              </router-link>
              <router-link to="/live-news" class="btn btn-outline-light px-4 py-2 rounded-pill fw-bold">
                Latest News
              </router-link>
            </div>
          </div>

        </div>

        <!-- Right / Sidebar -->
        <div class="col-lg-4">
          <div style="position: sticky; top: 100px; display: flex; flex-direction: column; gap: 1.5rem;">
            
            <!-- Join Promo -->
            <div v-if="!currentUser" class="about-card text-center p-5 border-primary border-opacity-50" style="background: linear-gradient(145deg, rgba(124, 58, 237, 0.1), rgba(6, 182, 212, 0.05));">
              <div class="mb-4">
                <i class="bi bi-rocket-takeoff text-primary" style="font-size: 3.5rem;"></i>
              </div>
              <h4 class="about-text-primary fw-bold mb-3">Ready to Play?</h4>
              <p class="text-muted-light mb-4">Join thousands of gamers discovering their next favorite titles today.</p>
              <router-link to="/register" class="btn btn-primary w-100 py-2 fw-bold rounded-pill shadow-sm">
                Create Free Account
              </router-link>
              <div class="mt-3">
                <small class="text-muted">Already have an account? <router-link to="/login" class="text-info text-decoration-none">Log in</router-link></small>
              </div>
            </div>

            <!-- Gamer Profile Card -->
            <div class="about-card about-gamer-card mb-4 p-4">
              <h5 class="about-text-primary fw-bold mb-0">
                <i class="bi bi-joystick me-2 text-primary"></i>Gamer Profile
              </h5>
              <p class="text-muted-light mb-3" style="font-size: 0.82rem">
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
                />
              </div>

              <div class="about-field mt-3">
                <label for="lastName" class="about-label">Last Name</label>
                <input
                  id="lastName"
                  v-model="lastName"
                  type="text"
                  class="about-input"
                  placeholder="Your last name"
                />
              </div>

              <!-- Welcome message -->
              <div v-if="fullName" class="about-welcome mt-3">
                <div class="about-welcome-icon">🎮</div>
                <div>
                  <strong class="about-text-primary">Welcome, {{ fullName }}!</strong>
                  <div class="about-welcome-title">
                    {{ gamerEmoji }} {{ gamerTitle }}
                  </div>
                </div>
              </div>

              <hr class="border-secondary opacity-25 my-4" />

              <h6 class="about-label mb-2 about-text-primary">
                <i class="bi bi-map me-1"></i>Choose Your Adventure
              </h6>
              <p class="text-muted-light mb-3" style="font-size: 0.8rem">
                Select the world you would like to explore.
              </p>

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

              <div class="about-scene-img-wrap mt-3 mb-3">
                <img
                  v-lazy-img="sceneImage"
                  :alt="selectedScene"
                  class="about-scene-img"
                />
              </div>
              <div class="text-center text-muted-light fst-italic" style="font-size: 0.9rem;">
                {{
                  selectedScene === "mountain"
                    ? "🏔️ You are a fearless Mountain Explorer."
                    : "🌊 You are an adventurous Ocean Voyager."
                }}
              </div>
            </div>

            <!-- Community Stats -->
            <div class="about-card p-4">
              <h5 class="about-text-primary fw-bold mb-4"><i class="bi bi-bar-chart-fill me-2 text-warning"></i>Platform Stats</h5>
              
              <div class="d-flex align-items-center mb-4">
                <div class="fs-1 text-primary me-3"><i class="bi bi-controller"></i></div>
                <div>
                  <div class="fs-4 fw-bold about-text-primary">300+</div>
                  <div class="text-muted-light small text-uppercase" style="letter-spacing: 1px;">Free Games</div>
                </div>
              </div>
              
              <div class="d-flex align-items-center mb-4">
                <div class="fs-1 text-success me-3"><i class="bi bi-broadcast"></i></div>
                <div>
                  <div class="fs-4 fw-bold about-text-primary">24/7</div>
                  <div class="text-muted-light small text-uppercase" style="letter-spacing: 1px;">Gaming News</div>
                </div>
              </div>

              <div class="d-flex align-items-center mb-4">
                <div class="fs-1 text-danger me-3"><i class="bi bi-plug-fill"></i></div>
                <div>
                  <div class="fs-4 fw-bold about-text-primary">4</div>
                  <div class="text-muted-light small text-uppercase" style="letter-spacing: 1px;">Integrated APIs</div>
                </div>
              </div>

              <div class="d-flex align-items-center">
                <div class="fs-1 text-info me-3"><i class="bi bi-cloud-check-fill"></i></div>
                <div>
                  <div class="fs-4 fw-bold about-text-primary">Firebase</div>
                  <div class="text-muted-light small text-uppercase" style="letter-spacing: 1px;">Cloud Sync</div>
                </div>
              </div>
            </div>

            <!-- Latest Update Card -->
            <div class="about-card p-4" style="background: rgba(34, 197, 94, 0.05); border-color: rgba(34, 197, 94, 0.2);">
              <div class="d-flex align-items-center mb-2">
                <span class="badge bg-success bg-opacity-25 text-success rounded-pill me-2">Latest Update</span>
                <span class="text-muted-light small">v1.0.0 Launched</span>
              </div>
              <h6 class="about-text-primary fw-bold mb-1">GameHub is Live!</h6>
              <p class="text-muted-light small mb-0">Featuring user authentication, personal libraries, live news integration, and community reviews.</p>
            </div>

            <!-- University Footer Note -->
            <div class="text-center mt-3 opacity-75">
              <small class="text-muted d-block mb-1 text-uppercase fw-bold" style="letter-spacing: 1px; font-size: 0.7rem;">Academic Project</small>
              <div class="badge bg-secondary bg-opacity-25 text-light px-3 py-2 rounded-pill mt-2 mb-2">
                <i class="bi bi-mortarboard-fill me-2"></i>COS30043 Full Stack Development
              </div>
              <small class="text-muted d-block mt-1">Swinburne University &copy; 2026</small>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.about-text-primary {
  color: var(--text-primary) !important;
}
.text-muted-light {
  color: var(--text-secondary) !important;
}

/* ===== Page ===== */
.about-page {
  min-height: 100vh;
  background: var(--bg-deep);
}

/* ===== Hero ===== */
.about-hero {
  position: relative;
  padding: 5rem 0 4.5rem;
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
  width: 500px;
  height: 500px;
  background: rgba(124, 58, 237, 0.12);
  top: -200px;
  left: -100px;
}

.orb-2 {
  width: 400px;
  height: 400px;
  background: rgba(6, 182, 212, 0.08);
  top: -100px;
  right: -50px;
}

.orb-3 {
  width: 300px;
  height: 300px;
  background: rgba(244, 63, 94, 0.06);
  bottom: -100px;
  left: 40%;
}

.about-hero-content {
  position: relative;
  display: flex;
  flex-direction: column;
  align-items: center;
  z-index: 1;
}

.about-hero-title {
  font-size: clamp(2.5rem, 6vw, 4rem);
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
  font-size: 1.15rem;
  max-width: 650px;
  line-height: 1.7;
  margin: 0;
}

/* ===== Body ===== */
.about-body {
  padding-top: 4rem;
  padding-bottom: 5rem;
}

/* ===== Cards ===== */
.about-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  backdrop-filter: var(--glass-blur);
  position: relative;
  overflow: hidden;
  transition: border-color 0.25s;
}

.about-card:hover {
  border-color: rgba(124, 58, 237, 0.25);
}

.about-card-welcome {
  border-color: rgba(34, 197, 94, 0.2);
}

.about-card-glow {
  position: absolute;
  top: -80px;
  right: -80px;
  width: 250px;
  height: 250px;
  border-radius: 50%;
  background: radial-gradient(
    ellipse,
    rgba(34, 197, 94, 0.1) 0%,
    transparent 70%
  );
  pointer-events: none;
}

.about-card-inner {
  display: flex;
  gap: 1.25rem;
  position: relative;
  padding: 2rem;
}

.about-section-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  flex-shrink: 0;
}

.about-feature-card {
  background: rgba(25, 27, 35, 0.5);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 1.5rem;
  transition: transform 0.3s, box-shadow 0.3s, border-color 0.3s;
}

.about-feature-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
  border-color: rgba(124, 58, 237, 0.4);
}

.about-feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.3rem;
}

.about-visual-card {
  transition: transform 0.3s;
}

.about-visual-card:hover {
  transform: translateY(-5px);
}

.about-visual-img-wrap {
  aspect-ratio: 16/9;
}
.col-12 > .about-visual-card .about-visual-img-wrap {
  aspect-ratio: 21/9;
}

.about-visual-img-wrap img {
  border: 1px solid rgba(255, 255, 255, 0.05);
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
}

.about-visual-card:hover .about-visual-img-wrap img {
  transform: scale(1.05);
}

.about-visual-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.about-visual-card:hover .about-visual-overlay {
  opacity: 1;
}

.about-dev-avatar {
  background: linear-gradient(135deg, #7c3aed, #06b6d4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  border-radius: 20px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
}

@media (max-width: 768px) {
  .about-hero {
    padding: 3rem 1rem;
  }
  .about-card-inner {
    flex-direction: column;
  }
}

/* Gamer Profile */
.about-gamer-card {
  border-color: rgba(6, 182, 212, 0.2);
}

.about-field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.about-label {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.about-input {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-sm);
  padding: 0.6rem 1rem;
  color: var(--text-primary);
  font-size: 0.95rem;
  transition: all 0.2s;
}

.about-input:focus {
  outline: none;
  border-color: var(--primary-light);
  background: rgba(124, 58, 237, 0.1);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}

.about-input::placeholder {
  color: var(--text-muted);
}

.about-welcome {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem;
  background: rgba(124, 58, 237, 0.15);
  border: 1px solid rgba(124, 58, 237, 0.3);
  border-radius: var(--radius-sm);
  animation: slideUp 0.3s ease forwards;
}

.about-welcome-icon {
  font-size: 1.8rem;
}

.about-welcome-title {
  font-size: 0.85rem;
  color: var(--primary-light);
  font-weight: 600;
}

.about-scene-btns {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.about-scene-btn {
  flex: 1;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-subtle);
  color: var(--text-secondary);
  padding: 0.6rem;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  font-weight: 600;
  transition: all 0.2s;
}

.about-scene-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
}

.about-scene-btn.active {
  background: rgba(6, 182, 212, 0.15);
  border-color: rgba(6, 182, 212, 0.4);
  color: var(--accent-light);
}

.about-scene-img-wrap {
  position: relative;
  border-radius: var(--radius-md);
  overflow: hidden;
  aspect-ratio: 16 / 9;
}

.about-scene-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s;
}

.about-scene-img-wrap:hover .about-scene-img {
  transform: scale(1.05);
}

.about-scene-label {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.9));
  padding: 2rem 1rem 1rem;
  color: var(--text-primary);
  font-size: 0.85rem;
  font-weight: 500;
  text-align: center;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
