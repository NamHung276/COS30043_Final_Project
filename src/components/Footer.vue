<template>
  <footer class="gd-footer">
    <div class="gd-footer-top">
      <div class="container">
        <div class="gd-footer-grid">
          <div class="gd-footer-brand-col">
            <div class="gd-footer-logo">
              <img src="/logo/gamepad.svg" width="24" height="24" alt="GameHub Logo" class="logo-img me-2" style="filter: brightness(1.3)" />
              <span>GameHub</span>
            </div>
            <p class="gd-footer-tagline">
              Discover games, read reviews, track deals, and stay on top of gaming news — all in one place.
            </p>
            <div class="gd-footer-badges">
              <span class="gd-footer-badge">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                RAWG Database
              </span>
              <span class="gd-footer-badge">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                Firebase Auth
              </span>
              <span class="gd-footer-badge">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
                Live News API
              </span>
            </div>
            <!-- Mobile App Teaser -->
            <div class="gd-footer-app-badges">
              <div class="gd-app-badge" style="opacity: 0.5; cursor: default;" aria-label="Mobile app coming soon">
                <svg class="gd-app-badge-icon" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true"><path d="M18.71 19.5c-.83 1.24-1.71 2.45-3.05 2.47-1.34.03-1.77-.79-3.29-.79-1.53 0-2 .77-3.27.82-1.31.05-2.3-1.32-3.14-2.53C4.25 17 2.94 12.45 4.7 9.39c.87-1.52 2.43-2.48 4.12-2.51 1.28-.02 2.5.87 3.29.87.78 0 2.26-1.07 3.8-.91.65.03 2.47.26 3.64 1.98l-.09.06c-.22.15-2.18 1.27-2.16 3.79.03 3.02 2.65 4.03 2.68 4.04-.03.07-.42 1.44-1.38 2.84M13 3.5c.73-.83 1.94-1.46 2.94-1.5.13 1.17-.34 2.35-1.04 3.19-.69.85-1.83 1.51-2.95 1.42-.15-1.15.41-2.35 1.05-3.11z"/></svg>
                <span class="gd-app-badge-text">
                  <small>Coming soon on</small>
                  <strong>Mobile</strong>
                </span>
              </div>
            </div>
          </div>

          <!-- Store Column -->
          <div class="gd-footer-col">
            <h6 class="gd-footer-col-title">Store</h6>
            <ul class="gd-footer-links">
              <li><router-link to="/games">All Games</router-link></li>
              <li><router-link to="/free-to-play">Free to Play</router-link></li>
              <li><router-link to="/paid-games">Paid Games</router-link></li>
              <li><router-link to="/deals">Game Deals</router-link></li>
              <li><router-link to="/checkout">Cart</router-link></li>
            </ul>
          </div>

          <!-- Community Column -->
          <div class="gd-footer-col">
            <h6 class="gd-footer-col-title">Community</h6>
            <ul class="gd-footer-links">
              <li><router-link to="/live-news">Live Gaming News</router-link></li>
              <li><router-link to="/gamehub-news">GameHub Articles</router-link></li>
              <li v-if="currentUser"><router-link to="/gamehub-news/create">Write an Article</router-link></li>
              <li v-else><router-link to="/login">Sign In to Write</router-link></li>
              <li><router-link to="/favorites">My Wishlist</router-link></li>
            </ul>
          </div>

          <!-- Account Column -->
          <div class="gd-footer-col">
            <h6 class="gd-footer-col-title">Account</h6>
            <ul class="gd-footer-links">
              <li><router-link to="/profile">My Profile</router-link></li>
              <li><router-link to="/library">My Library</router-link></li>
              <template v-if="!currentUser">
                <li><router-link to="/login">Sign In</router-link></li>
                <li><router-link to="/register">Create Account</router-link></li>
              </template>
              <li><router-link to="/about">About GameHub</router-link></li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <div class="gd-footer-bottom">
      <div class="container">
        <div class="gd-footer-bottom-inner">
          <span class="gd-footer-copy">© 2026 GameHub — COS30043 Full-Stack Project</span>
          <span class="gd-footer-apis">
            Powered by
            <a href="https://rawg.io" target="_blank" rel="noopener">RAWG</a>,
            <a href="https://www.freetogame.com" target="_blank" rel="noopener">FreeToGame</a>,
            <a href="https://newsapi.org" target="_blank" rel="noopener">NewsAPI</a> &amp;
            <a href="https://www.cheapshark.com" target="_blank" rel="noopener">CheapShark</a>
          </span>
        </div>
      </div>
    </div>
  </footer>
</template>

<script>
import { auth } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";

export default {
  name: "Footer",
  data() {
    return {
      currentUser: null,
      unsubscribe: null,
    };
  },
  mounted() {
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      this.currentUser = user;
    });
  },
  beforeUnmount() {
    if (this.unsubscribe) this.unsubscribe();
  },
};
</script>

<style scoped>
.gd-footer {
  background: var(--bg-deep);
  border-top: 1px solid var(--overlay-medium);
  margin-top: auto;
}

.gd-footer-top {
  padding: 56px 0 40px;
}

.gd-footer-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 40px;
}

@media (max-width: 768px) {
  .gd-footer-grid {
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }
  .gd-footer-brand-col {
    grid-column: 1 / -1;
  }
}

@media (max-width: 480px) {
  .gd-footer-grid {
    grid-template-columns: 1fr;
  }
}

.gd-footer-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  font-family: var(--font-display);
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--primary);
  margin-bottom: 14px;
  text-decoration: none;
}

.gd-footer-logo img {
  filter: brightness(1.3);
  opacity: 0.9;
}

.gd-footer-tagline {
  font-size: 0.85rem;
  color: var(--text-muted);
  line-height: 1.65;
  max-width: 300px;
  margin-bottom: 18px;
}

.gd-footer-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.gd-footer-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.72rem;
  font-weight: 600;
  color: var(--text-secondary);
  background: var(--overlay-light);
  border: 1px solid var(--overlay-medium);
  border-radius: 999px;
  padding: 4px 10px;
}

.gd-footer-badge svg {
  color: var(--accent2);
  flex-shrink: 0;
}

.gd-footer-col-title {
  font-family: var(--font-display);
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.1em;
  margin-bottom: 16px;
}

.gd-footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.gd-footer-links a {
  font-size: 0.875rem;
  color: var(--text-muted);
  text-decoration: none;
  transition: color 0.2s ease, transform 0.2s ease;
  display: inline-block;
}

.gd-footer-links a:hover {
  color: var(--primary-light);
  transform: translateX(3px);
}

.gd-footer-bottom {
  border-top: 1px solid var(--overlay-light);
  padding: 18px 0;
}

.gd-footer-bottom-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}

.gd-footer-copy {
  font-size: 0.78rem;
  color: var(--text-muted);
}

.gd-footer-apis {
  font-size: 0.78rem;
  color: var(--text-muted);
}

.gd-footer-apis a {
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.gd-footer-apis a:hover {
  color: var(--primary-light);
}

/* ── Mobile App Badges ── */
.gd-footer-app-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin-top: 20px;
}

.gd-app-badge {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  background: var(--overlay-medium);
  border: 1px solid var(--overlay-heavy);
  border-radius: 10px;
  padding: 8px 14px;
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.2s ease;
  min-width: 140px;
}

.gd-app-badge:hover {
  background: var(--overlay-heavy);
  border-color: var(--primary);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(14, 165, 233, 0.2);
  color: var(--text-primary);
}

.gd-app-badge-icon {
  width: 22px;
  height: 22px;
  flex-shrink: 0;
  color: var(--text-primary);
}

.gd-app-badge-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}

.gd-app-badge-text small {
  font-size: 0.6rem;
  color: var(--text-muted);
  letter-spacing: 0.02em;
}

.gd-app-badge-text strong {
  font-size: 0.78rem;
  font-weight: 700;
  font-family: var(--font-display);
  color: var(--text-primary);
}
</style>
