// src/views/Favorites.vue
<script>
import { inject } from 'vue'
import { auth, db } from '../firebase'
import { onAuthStateChanged } from 'firebase/auth'
import {
  collection,
  query,
  where,
  orderBy,
  getDocs,
  deleteDoc,
  doc
} from 'firebase/firestore'

export default {
  setup() {
    const toast = inject('toast')
    return { toast }
  },

  data() {
    return {
      favorites: [],
      loading: true,
      currentUser: null,
      searchQuery: '',
      selectedGenre: 'All',
      sortBy: 'newest',
      viewMode: 'grid'
    }
  },

  computed: {
    allGenres() {
      const genres = ['All', ...new Set(this.favorites.map(f => f.genre).filter(Boolean))]
      return genres
    },

    filteredFavorites() {
      let list = [...this.favorites]

      if (this.searchQuery.trim()) {
        const q = this.searchQuery.toLowerCase()
        list = list.filter(f => f.title?.toLowerCase().includes(q))
      }

      if (this.selectedGenre !== 'All') {
        list = list.filter(f => f.genre === this.selectedGenre)
      }

      if (this.sortBy === 'az') {
        list.sort((a, b) => (a.title || '').localeCompare(b.title || ''))
      } else if (this.sortBy === 'za') {
        list.sort((a, b) => (b.title || '').localeCompare(a.title || ''))
      }

      return list
    },

    totalCount() {
      return this.favorites.length
    },

    filteredCount() {
      return this.filteredFavorites.length
    }
  },

  methods: {
    async removeFavorite(favoriteId, title) {
      try {
        await deleteDoc(doc(db, 'favorites', favoriteId))
        this.favorites = this.favorites.filter(fav => fav.id !== favoriteId)
        this.toast.show(`Removed "${title}" from wishlist`, 'info')
      } catch (error) {
        console.error('Failed to remove from wishlist:', error)
        this.toast.show('Failed to remove. Please try again.', 'error')
      }
    },

    async loadFavorites(user) {
      this.loading = true
      const favoritesQuery = query(
        collection(db, 'favorites'),
        where('userId', '==', user.uid),
        orderBy('createdAt', 'desc')
      )
      const snapshot = await getDocs(favoritesQuery)
      this.favorites = snapshot.docs.map(docSnap => ({
        id: docSnap.id,
        ...docSnap.data()
      }))
      this.loading = false
    },

    getSourceLabel(source) {
      return source === 'freetogame' ? 'Free-to-Play' : 'Premium'
    },

    getSourceBadgeClass(source) {
      return source === 'freetogame' ? 'badge-free' : 'badge-steam'
    }
  },

  mounted() {
    onAuthStateChanged(auth, (user) => {
      if (!user) {
        this.favorites = []
        this.currentUser = null
        this.$router.push('/login')
        return
      }
      this.currentUser = user
      this.loadFavorites(user)
    })
  }
}
</script>

<template>
  <div class="fav-page">

    <!-- Hero Header -->
    <div class="fav-hero">
      <div class="fav-hero-bg"></div>
      <div class="fav-hero-content container">
        <div class="fav-hero-icon">
          <i class="bi bi-star-fill"></i>
        </div>
        <div>
          <h1 class="fav-hero-title">My Wishlist</h1>
          <p class="fav-hero-sub">Your personal gaming wishlist, all in one place</p>
        </div>
        <div class="fav-hero-stats ms-auto d-none d-md-flex">
          <div class="fav-stat">
            <span class="fav-stat-num">{{ totalCount }}</span>
            <span class="fav-stat-label">Saved</span>
          </div>
          <div class="fav-stat-divider"></div>
          <div class="fav-stat">
            <span class="fav-stat-num">{{ allGenres.length - 1 }}</span>
            <span class="fav-stat-label">Genres</span>
          </div>
        </div>
      </div>
    </div>

    <div class="container fav-body">

      <!-- Toolbar -->
      <div class="fav-toolbar" v-if="!loading && favorites.length > 0">
        <div class="fav-search-wrap">
          <i class="bi bi-search fav-search-icon"></i>
          <input
            v-model="searchQuery"
            type="text"
            class="fav-search"
            placeholder="Search your wishlist…"
            aria-label="Search wishlist"
          >
          <button
            v-if="searchQuery"
            class="fav-search-clear"
            @click="searchQuery = ''"
            aria-label="Clear search"
          >
            <i class="bi bi-x-lg"></i>
          </button>
        </div>

        <div class="fav-genre-scroll">
          <button
            v-for="genre in allGenres"
            :key="genre"
            class="fav-genre-btn"
            :class="{ active: selectedGenre === genre }"
            @click="selectedGenre = genre"
          >{{ genre }}</button>
        </div>

        <div class="fav-toolbar-right">
          <select v-model="sortBy" class="fav-select" aria-label="Sort wishlist">
            <option value="newest">Newest First</option>
            <option value="az">A → Z</option>
            <option value="za">Z → A</option>
          </select>
          <div class="fav-view-toggle">
            <button
              class="fav-view-btn"
              :class="{ active: viewMode === 'grid' }"
              @click="viewMode = 'grid'"
              aria-label="Grid view"
            ><i class="bi bi-grid-3x3-gap-fill"></i></button>
            <button
              class="fav-view-btn"
              :class="{ active: viewMode === 'list' }"
              @click="viewMode = 'list'"
              aria-label="List view"
            ><i class="bi bi-list-ul"></i></button>
          </div>
        </div>
      </div>

      <!-- Result count -->
      <div v-if="!loading && favorites.length > 0" class="fav-result-count">
        Showing <strong>{{ filteredCount }}</strong> of <strong>{{ totalCount }}</strong> games
        <span v-if="selectedGenre !== 'All'"> in <em>{{ selectedGenre }}</em></span>
      </div>

      <!-- Loading -->
      <div v-if="loading" class="fav-loading">
        <div class="fav-spinner">
          <div class="fav-spinner-ring"></div>
          <i class="bi bi-star-fill fav-spinner-icon"></i>
        </div>
        <p class="fav-loading-text">Loading your collection…</p>
      </div>

      <!-- Empty Collection -->
      <div v-else-if="favorites.length === 0" class="fav-empty">
        <div class="fav-empty-glow"></div>
        <div class="fav-empty-icon">
          <i class="bi bi-star"></i>
        </div>
        <h2 class="fav-empty-title">Your wishlist is empty</h2>
        <p class="fav-empty-desc">
          Start exploring and hit the ⭐ on any game to save it here.<br>
          Build your perfect gaming wishlist!
        </p>
        <div class="fav-empty-actions">
          <router-link to="/games" class="btn-fav-primary">
            <i class="bi bi-controller me-2"></i>Browse Games
          </router-link>
          <router-link to="/free-to-play" class="btn-fav-outline">
            <i class="bi bi-gift me-2"></i>Free To Play
          </router-link>
        </div>
      </div>

      <!-- No filter results -->
      <div v-else-if="filteredFavorites.length === 0" class="fav-empty">
        <div class="fav-empty-icon" style="background: rgba(6,182,212,0.12); color: var(--accent);">
          <i class="bi bi-funnel"></i>
        </div>
        <h2 class="fav-empty-title">No results found</h2>
        <p class="fav-empty-desc">Try a different search or genre filter.</p>
        <button class="btn-fav-outline" @click="searchQuery = ''; selectedGenre = 'All'">
          <i class="bi bi-arrow-counterclockwise me-2"></i>Clear Filters
        </button>
      </div>

      <!-- Grid View -->
      <div v-else-if="viewMode === 'grid'" class="fav-grid">
        <div
          class="fav-card stagger-item"
          v-for="(game, index) in filteredFavorites"
          :key="game.id"
          :style="{ animationDelay: `${index * 0.055}s` }"
        >
          <div class="fav-card-img-wrap">
            <img
              v-lazy-img="game.thumbnail"
              class="fav-card-img"
              :alt="`${game.title} thumbnail`"
            >
            <div class="fav-card-overlay"></div>
            <span class="fav-source-badge" :class="getSourceBadgeClass(game.source)">
              {{ getSourceLabel(game.source) }}
            </span>
            <button
              class="fav-remove-btn"
              aria-label="Remove from wishlist"
              @click="removeFavorite(game.id, game.title)"
            >
              <i class="bi bi-trash3"></i>
            </button>
          </div>
          <div class="fav-card-body">
            <h3 class="fav-card-title">{{ game.title }}</h3>
            <span class="fav-genre-tag">
              <i class="bi bi-tag me-1"></i>{{ game.genre || 'Unknown' }}
            </span>
            <router-link
              :to="game.source === 'freetogame'
                ? `/free-to-play/${game.gameId}`
                : `/games/${game.gameId}`"
              class="fav-card-btn"
            >
              View Details <i class="bi bi-arrow-right ms-1"></i>
            </router-link>
          </div>
        </div>
      </div>

      <!-- List View -->
      <div v-else class="fav-list">
        <div
          class="fav-list-item stagger-item"
          v-for="(game, index) in filteredFavorites"
          :key="game.id"
          :style="{ animationDelay: `${index * 0.04}s` }"
        >
          <img
            v-lazy-img="game.thumbnail"
            class="fav-list-thumb"
            :alt="`${game.title} thumbnail`"
          >
          <div class="fav-list-info">
            <h3 class="fav-list-title">{{ game.title }}</h3>
            <div class="fav-list-meta">
              <span class="fav-genre-tag">
                <i class="bi bi-tag me-1"></i>{{ game.genre || 'Unknown' }}
              </span>
              <span class="fav-source-badge" :class="getSourceBadgeClass(game.source)" style="position:static;font-size:0.7rem;padding:3px 8px;">
                {{ getSourceLabel(game.source) }}
              </span>
            </div>
          </div>
          <div class="fav-list-actions">
            <router-link
              :to="game.source === 'freetogame'
                ? `/free-to-play/${game.gameId}`
                : `/games/${game.gameId}`"
              class="fav-card-btn"
              style="padding: 7px 16px; font-size: 0.82rem;"
            >
              Details
            </router-link>
            <button
              class="fav-list-remove"
              aria-label="Remove from wishlist"
              @click="removeFavorite(game.id, game.title)"
            >
              <i class="bi bi-trash3"></i>
            </button>
          </div>
        </div>
      </div>

      <!-- Browse CTA at bottom -->
      <div v-if="!loading && favorites.length > 0" class="fav-cta">
        <router-link to="/games" class="btn-fav-outline">
          <i class="bi bi-plus-circle me-2"></i>Discover More Games
        </router-link>
      </div>

    </div>
  </div>
</template>

<style scoped>
/* ===== Page Layout ===== */
.fav-page {
  min-height: 100vh;
  background: var(--bg-deep);
}

/* ===== Hero Header ===== */
.fav-hero {
  position: relative;
  padding: 3rem 0 2rem;
  overflow: hidden;
  border-bottom: 1px solid var(--border-subtle);
}

.fav-hero-bg {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse 80% 60% at 20% 50%, rgba(124,58,237,0.13) 0%, transparent 70%),
              radial-gradient(ellipse 50% 80% at 80% 30%, rgba(6,182,212,0.08) 0%, transparent 70%);
  pointer-events: none;
}

.fav-hero-content {
  position: relative;
  display: flex;
  align-items: center;
  gap: 1.25rem;
  flex-wrap: wrap;
}

.fav-hero-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  background: linear-gradient(135deg, rgba(124,58,237,0.25), rgba(6,182,212,0.2));
  border: 1px solid rgba(124,58,237,0.35);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.6rem;
  color: #f59e0b;
  flex-shrink: 0;
  box-shadow: 0 0 24px rgba(124,58,237,0.2);
}

.fav-hero-title {
  font-size: clamp(1.6rem, 4vw, 2.4rem);
  font-weight: 800;
  background: linear-gradient(135deg, #f0f4ff, #a78bfa);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
  line-height: 1.2;
}

.fav-hero-sub {
  color: var(--text-secondary);
  margin: 0.25rem 0 0;
  font-size: 0.95rem;
}

.fav-hero-stats {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 14px;
  padding: 0.75rem 1.5rem;
  backdrop-filter: var(--glass-blur);
}

.fav-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.fav-stat-num {
  font-size: 1.5rem;
  font-weight: 800;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  line-height: 1;
}

.fav-stat-label {
  font-size: 0.72rem;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.fav-stat-divider {
  width: 1px;
  height: 36px;
  background: var(--border-glass);
}

/* ===== Body ===== */
.fav-body {
  padding-top: 2rem;
  padding-bottom: 4rem;
}

/* ===== Toolbar ===== */
.fav-toolbar {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}

.fav-search-wrap {
  position: relative;
  flex: 1;
  min-width: 220px;
  max-width: 340px;
}

.fav-search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 0.85rem;
  pointer-events: none;
}

.fav-search {
  width: 100%;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 10px;
  color: var(--text-primary);
  padding: 9px 36px 9px 34px;
  font-size: 0.88rem;
  backdrop-filter: var(--glass-blur);
  transition: border-color 0.2s, box-shadow 0.2s;
}

.fav-search::placeholder { color: var(--text-muted); }
.fav-search:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(124,58,237,0.18);
}

.fav-search-clear {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.75rem;
  padding: 2px;
  line-height: 1;
  transition: color 0.2s;
}
.fav-search-clear:hover { color: var(--accent2); }

.fav-genre-scroll {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
  flex: 1;
}

.fav-genre-btn {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 20px;
  color: var(--text-secondary);
  padding: 5px 14px;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.fav-genre-btn:hover {
  border-color: var(--primary-light);
  color: var(--primary-light);
}

.fav-genre-btn.active {
  background: rgba(124,58,237,0.2);
  border-color: var(--primary);
  color: var(--primary-light);
  font-weight: 600;
}

.fav-toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.fav-select {
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 10px;
  color: var(--text-primary);
  padding: 7px 12px;
  font-size: 0.82rem;
  cursor: pointer;
  backdrop-filter: var(--glass-blur);
  transition: border-color 0.2s;
}
.fav-select:focus { outline: none; border-color: var(--primary); }

.fav-view-toggle {
  display: flex;
  border: 1px solid var(--border-glass);
  border-radius: 10px;
  overflow: hidden;
}

.fav-view-btn {
  background: var(--bg-glass);
  border: none;
  color: var(--text-secondary);
  padding: 7px 11px;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.85rem;
}
.fav-view-btn:hover { color: var(--text-primary); background: var(--bg-glass-hover); }
.fav-view-btn.active {
  background: rgba(124,58,237,0.22);
  color: var(--primary-light);
}

/* Result count */
.fav-result-count {
  font-size: 0.82rem;
  color: var(--text-secondary);
  margin-bottom: 1.5rem;
}
.fav-result-count strong { color: var(--text-primary); }
.fav-result-count em { color: var(--primary-light); font-style: normal; }

/* ===== Loading ===== */
.fav-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 0;
  gap: 1.5rem;
}

.fav-spinner {
  position: relative;
  width: 64px;
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.fav-spinner-ring {
  position: absolute;
  inset: 0;
  border-radius: 50%;
  border: 2px solid transparent;
  border-top-color: var(--primary);
  border-right-color: var(--accent);
  animation: fav-spin 1s linear infinite;
}

@keyframes fav-spin {
  to { transform: rotate(360deg); }
}

.fav-spinner-icon {
  font-size: 1.4rem;
  color: #f59e0b;
}

.fav-loading-text {
  color: var(--text-secondary);
  font-size: 0.9rem;
  margin: 0;
}

/* ===== Empty State ===== */
.fav-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 5rem 1rem;
  text-align: center;
  position: relative;
}

.fav-empty-glow {
  position: absolute;
  width: 300px;
  height: 300px;
  border-radius: 50%;
  background: radial-gradient(ellipse, rgba(124,58,237,0.1) 0%, transparent 70%);
  pointer-events: none;
}

.fav-empty-icon {
  width: 88px;
  height: 88px;
  border-radius: 24px;
  background: rgba(124,58,237,0.12);
  border: 1px solid rgba(124,58,237,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2.2rem;
  color: var(--primary-light);
  margin-bottom: 1.5rem;
}

.fav-empty-title {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 0.75rem;
}

.fav-empty-desc {
  color: var(--text-secondary);
  font-size: 0.95rem;
  max-width: 420px;
  line-height: 1.7;
  margin-bottom: 2rem;
}

.fav-empty-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  justify-content: center;
}

/* ===== Buttons ===== */
.btn-fav-primary {
  display: inline-flex;
  align-items: center;
  padding: 11px 24px;
  background: var(--gradient-primary);
  border-radius: 12px;
  color: #fff;
  font-weight: 600;
  font-size: 0.9rem;
  text-decoration: none;
  box-shadow: 0 4px 20px rgba(124,58,237,0.35);
  transition: transform 0.2s, box-shadow 0.2s;
}
.btn-fav-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 30px rgba(124,58,237,0.45);
  color: #fff;
}

.btn-fav-outline {
  display: inline-flex;
  align-items: center;
  padding: 10px 22px;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  color: var(--text-secondary);
  font-weight: 500;
  font-size: 0.88rem;
  text-decoration: none;
  backdrop-filter: var(--glass-blur);
  transition: all 0.2s;
  cursor: pointer;
}
.btn-fav-outline:hover {
  border-color: var(--primary-light);
  color: var(--primary-light);
  transform: translateY(-1px);
}

/* ===== Grid ===== */
.fav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 1.5rem;
}

/* ===== Card ===== */
.fav-card {
  background: var(--bg-glass);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  backdrop-filter: var(--glass-blur);
  transition: transform 0.25s, box-shadow 0.25s, border-color 0.25s;
}

.fav-card:hover {
  transform: translateY(-5px);
  border-color: rgba(124,58,237,0.4);
  box-shadow: 0 12px 40px rgba(124,58,237,0.18), 0 0 0 1px rgba(124,58,237,0.15);
}

.fav-card-img-wrap {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.fav-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s;
}

.fav-card:hover .fav-card-img {
  transform: scale(1.06);
}

.fav-card-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, transparent 40%, rgba(5,7,15,0.85) 100%);
  pointer-events: none;
}

.fav-source-badge {
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  padding: 3px 9px;
  border-radius: 20px;
  text-transform: uppercase;
}

.badge-free {
  background: rgba(34,197,94,0.2);
  border: 1px solid rgba(34,197,94,0.4);
  color: #4ade80;
}

.badge-steam {
  background: rgba(6,182,212,0.2);
  border: 1px solid rgba(6,182,212,0.4);
  color: var(--accent-light);
}

.fav-remove-btn {
  position: absolute;
  top: 10px;
  right: 10px;
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: rgba(244,63,94,0.15);
  border: 1px solid rgba(244,63,94,0.3);
  color: #fb7185;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s, transform 0.2s, background 0.2s;
}

.fav-card:hover .fav-remove-btn {
  opacity: 1;
}

.fav-remove-btn:hover {
  background: rgba(244,63,94,0.3);
  transform: scale(1.12);
}

.fav-card-body {
  padding: 1rem 1.1rem 1.2rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
  flex: 1;
}

.fav-card-title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.fav-genre-tag {
  display: inline-flex;
  align-items: center;
  font-size: 0.75rem;
  color: var(--primary-light);
  background: rgba(124,58,237,0.12);
  border: 1px solid rgba(124,58,237,0.2);
  border-radius: 20px;
  padding: 3px 10px;
  width: fit-content;
}

.fav-card-btn {
  display: inline-flex;
  align-items: center;
  margin-top: auto;
  padding: 8px 16px;
  background: rgba(124,58,237,0.15);
  border: 1px solid rgba(124,58,237,0.3);
  border-radius: 10px;
  color: var(--primary-light);
  font-size: 0.82rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.2s;
  width: fit-content;
}

.fav-card-btn:hover {
  background: rgba(124,58,237,0.28);
  border-color: var(--primary);
  color: #fff;
}

/* ===== List View ===== */
.fav-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.fav-list-item {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: var(--bg-glass);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-md);
  padding: 0.75rem 1rem;
  backdrop-filter: var(--glass-blur);
  transition: border-color 0.2s, transform 0.2s;
}

.fav-list-item:hover {
  border-color: rgba(124,58,237,0.35);
  transform: translateX(3px);
}

.fav-list-thumb {
  width: 72px;
  height: 50px;
  border-radius: 8px;
  object-fit: cover;
  flex-shrink: 0;
}

.fav-list-info {
  flex: 1;
  min-width: 0;
}

.fav-list-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.3rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.fav-list-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  flex-wrap: wrap;
}

.fav-list-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}

.fav-list-remove {
  width: 34px;
  height: 34px;
  border-radius: 8px;
  background: rgba(244,63,94,0.1);
  border: 1px solid rgba(244,63,94,0.25);
  color: #fb7185;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}
.fav-list-remove:hover {
  background: rgba(244,63,94,0.25);
  transform: scale(1.08);
}

/* ===== CTA ===== */
.fav-cta {
  display: flex;
  justify-content: center;
  margin-top: 3rem;
}

/* ===== Stagger animation ===== */
.stagger-item {
  opacity: 0;
  animation: fav-fade-in 0.45s ease forwards;
}

@keyframes fav-fade-in {
  from { opacity: 0; transform: translateY(16px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* ===== Responsive ===== */
/* Tablet (iPad, 768px–1023px) */
@media (max-width: 1023px) {
  .fav-hero { padding: 2.5rem 0 1.75rem; }
  .fav-hero-title { font-size: 2rem; }
  .fav-genre-scroll { overflow-x: auto; flex-wrap: nowrap; -webkit-overflow-scrolling: touch; scrollbar-width: none; }
  .fav-genre-scroll::-webkit-scrollbar { display: none; }
  .fav-genre-btn { flex-shrink: 0; }
  .fav-grid { grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }
}

/* Mobile (≤767px) */
@media (max-width: 767px) {
  .fav-hero { padding: 1.75rem 0 1.25rem; }
  .fav-hero-title { font-size: 1.5rem; }
  .fav-hero-sub { font-size: 0.85rem; }
  .fav-hero-content { gap: 0.875rem; }
  .fav-toolbar {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }
  .fav-search-wrap { max-width: 100%; }
  .fav-genre-scroll {
    overflow-x: auto;
    flex-wrap: nowrap;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    padding-bottom: 2px;
  }
  .fav-genre-scroll::-webkit-scrollbar { display: none; }
  .fav-genre-btn { flex-shrink: 0; }
  .fav-toolbar-right { justify-content: flex-end; }
  .fav-grid { grid-template-columns: repeat(auto-fill, minmax(155px, 1fr)); gap: 0.875rem; }
  .fav-card-img-wrap { height: 125px; }
  .fav-card-body { padding: 0.75rem 0.875rem 1rem; }
  .fav-card-title { font-size: 0.85rem; }
  .fav-list-thumb { width: 60px; height: 44px; }
  .fav-list-title { font-size: 0.82rem; }
  .fav-list-item { padding: 0.625rem 0.75rem; gap: 0.75rem; }
  .fav-empty { padding: 3.5rem 1rem; }
  .fav-cta { margin-top: 2rem; }
}

/* Small mobile (≤479px) */
@media (max-width: 479px) {
  .fav-grid { grid-template-columns: repeat(2, 1fr); gap: 0.75rem; }
  .fav-card-img-wrap { height: 110px; }
  .fav-card-title { font-size: 0.8rem; }
  .fav-genre-tag { font-size: 0.7rem; padding: 2px 8px; }
  .fav-card-btn { font-size: 0.75rem; padding: 6px 12px; }
  .fav-list-actions { flex-direction: column; gap: 4px; }
  .fav-list-remove { width: 28px; height: 28px; font-size: 0.72rem; }
}

</style>