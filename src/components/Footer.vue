<template>
  <footer class="gd-footer">
    <div class="gd-footer-top">
      <div class="container">
        <div class="gd-footer-grid">
          <!-- Brand Column -->
          <div class="gd-footer-brand-col">
            <div class="gd-footer-logo">
              <img src="/logo/gamepad.svg" width="22" height="22" alt="" aria-hidden="true" />
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
              <li><router-link to="/gamehub-news/create">Write an Article</router-link></li>
              <li><router-link to="/favorites">My Wishlist</router-link></li>
            </ul>
          </div>

          <!-- Account Column -->
          <div class="gd-footer-col">
            <h6 class="gd-footer-col-title">Account</h6>
            <ul class="gd-footer-links">
              <li><router-link to="/profile">My Profile</router-link></li>
              <li><router-link to="/library">My Library</router-link></li>
              <li><router-link to="/login">Sign In</router-link></li>
              <li><router-link to="/register">Create Account</router-link></li>
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

<style scoped>
.gd-footer {
  background: #0a0c12;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
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
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
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
  border-top: 1px solid rgba(255, 255, 255, 0.05);
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
</style>
