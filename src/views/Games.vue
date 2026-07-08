// src/views/Games.vue
<script>
import SkeletonCard from '../components/SkeletonCard.vue'
import { rawgApi } from '../api'

// RAWG parent_platform IDs
const PLATFORMS = [
  { key: 'all',         label: 'All Platforms', icon: null,                       id: null },
  { key: 'pc',         label: 'PC',            icon: '/logo/pc.svg',              id: 1    },
  { key: 'ps',         label: 'PlayStation',   icon: '/logo/playstation_logo.png', id: 2   },
  { key: 'xbox',       label: 'Xbox',          icon: '/logo/xbox_logo.png',       id: 3    },
  { key: 'nintendo',   label: 'Nintendo',      icon: '/logo/nintendo_logo.png',   id: 7    },
  { key: 'mobile',     label: 'Mobile',        icon: '/logo/mobile.svg',          id: '4,8' },
]

export default {
  components: { SkeletonCard },

  data() {
    return {
      games: [],
      loading: true,
      error: null,
      searchTerm: '',
      selectedGenre: 'All',
      selectedPlatform: 'all',
      genres: ['All'],
      platforms: PLATFORMS,
      currentPage: 1,
      itemsPerPage: 12,
      totalCount: 0,
      searchTimeout: null
    }
  },

  computed: {
    filteredGames() {
      let list = this.games
      if (this.selectedGenre !== 'All') {
        list = list.filter(g => g.genres?.some(genre => genre.name === this.selectedGenre))
      }
      return list
    },

    totalPages() {
      return Math.ceil(this.filteredGames.length / this.itemsPerPage)
    },

    paginatedGames() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      return this.filteredGames.slice(start, start + this.itemsPerPage)
    },

    visiblePages() {
      const pages = []
      if (this.totalPages <= 7) {
        for (let i = 1; i <= this.totalPages; i++) pages.push(i)
      } else {
        pages.push(1)
        if (this.currentPage > 4) pages.push('...')
        const start = Math.max(2, this.currentPage - 1)
        const end = Math.min(this.totalPages - 1, this.currentPage + 1)
        for (let i = start; i <= end; i++) pages.push(i)
        if (this.currentPage < this.totalPages - 3) pages.push('...')
        pages.push(this.totalPages)
      }
      return pages
    },

    activePlatform() {
      return this.platforms.find(p => p.key === this.selectedPlatform)
    }
  },

  watch: {
    searchTerm() {
      this.currentPage = 1
      clearTimeout(this.searchTimeout)
      this.searchTimeout = setTimeout(() => {
        this.fetchGames()
      }, 400)
    },
    selectedGenre() {
      this.currentPage = 1
    },
    selectedPlatform() {
      this.currentPage = 1
      this.fetchGames()
    }
  },

  methods: {
    metacriticClass(score) {
      if (!score) return 'mc-none'
      if (score >= 75) return 'mc-green'
      if (score >= 50) return 'mc-yellow'
      return 'mc-red'
    },

    platformIcons(platforms) {
      if (!platforms?.length) return []
      const icons = []
      const ids = platforms.map(p => p.platform.id)
      // PC = 4
      if (ids.includes(4)) icons.push({ key: 'pc', label: 'PC' })
      // PlayStation = 16,18,27,187,19 etc
      if (platforms.some(p => p.platform.slug?.includes('playstation'))) icons.push({ key: 'ps', label: 'PlayStation' })
      // Xbox
      if (platforms.some(p => p.platform.slug?.includes('xbox'))) icons.push({ key: 'xbox', label: 'Xbox' })
      // Nintendo
      if (platforms.some(p => p.platform.slug?.includes('nintendo') || p.platform.slug?.includes('switch') || p.platform.slug?.includes('wii') || p.platform.slug?.includes('3ds') || p.platform.slug?.includes('nes') || p.platform.slug?.includes('snes'))) icons.push({ key: 'nintendo', label: 'Nintendo' })
      // Mobile
      if (platforms.some(p => p.platform.slug?.includes('ios') || p.platform.slug?.includes('android'))) icons.push({ key: 'mobile', label: 'Mobile' })
      return icons
    },

    selectPlatform(key) {
      this.selectedPlatform = key
    },

    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },

    async fetchGames() {
      this.loading = true
      this.error = null
      try {
        const params = {
          page_size: 100,
          ordering: this.searchTerm ? '-rating' : '-metacritic',
          // Exclude DLCs, editions, add-ons — only show main games
          exclude_additions: true,
          // Minimum metacritic score to filter out obscure / unofficial games
          metacritic: '30,100',
          // Must have at least 3 ratings
          ratings_count: 3,
        }

        if (this.searchTerm) params.search = this.searchTerm

        // Server-side platform filter using RAWG parent_platforms
        const plat = this.platforms.find(p => p.key === this.selectedPlatform)
        if (plat && plat.id !== null) {
          params.parent_platforms = plat.id
        }

        const { data } = await rawgApi.get('/games', { params })
        this.games = data.results || []
        this.totalCount = data.count || 0

        // Build genre list from results
        const genreSet = new Set()
        this.games.forEach(g => g.genres?.forEach(genre => genreSet.add(genre.name)))
        this.genres = ['All', ...Array.from(genreSet).sort()]
        // Reset genre if no longer available
        if (!this.genres.includes(this.selectedGenre)) this.selectedGenre = 'All'
      } catch (err) {
        console.error(err)
        this.error = 'Failed to load games. Please try again later.'
      } finally {
        this.loading = false
      }
    }
  },

  async mounted() {
    await this.fetchGames()
  }
}
</script>

<template>
  <div class="games-page">

    <!-- Page Header -->
    <div class="games-page-header">
      <div class="games-page-header-bg" aria-hidden="true"></div>
      <div class="container games-header-content">
        <div class="games-title-row">
          <span class="games-title-icon" aria-hidden="true">
            <img src="/logo/gamepad.svg" width="28" height="28" alt="" aria-hidden="true">
          </span>
          <div>
            <h1 class="games-title">Games</h1>
            <p class="games-subtitle">
              Powered by <a href="https://rawg.io" target="_blank" rel="noopener noreferrer">RAWG</a>
              &nbsp;&middot;&nbsp;
              <strong>{{ totalCount.toLocaleString() }}</strong> games in database
            </p>
          </div>
        </div>

        <!-- Search & Genre Filter -->
        <div class="games-filters">
          <div class="games-search-wrap">
            <img src="/logo/search.svg" class="games-search-icon" width="17" height="17" alt="" aria-hidden="true">
            <input
              type="text"
              class="games-search-input"
              placeholder="Search games..."
              aria-label="Search games"
              v-model="searchTerm"
            >
          </div>
          <select
            class="games-genre-select"
            aria-label="Filter games by genre"
            v-model="selectedGenre"
          >
            <option v-for="genre in genres" :key="genre" :value="genre">{{ genre }}</option>
          </select>
        </div>

        <!-- Platform Filter Tabs -->
        <div class="platform-tabs">
          <button
            v-for="plat in platforms"
            :key="plat.key"
            class="platform-tab"
            :class="{ active: selectedPlatform === plat.key }"
            @click="selectPlatform(plat.key)"
            :aria-pressed="selectedPlatform === plat.key"
          >
            <img v-if="plat.icon" :src="plat.icon" width="18" height="18" :alt="plat.label" class="platform-tab-icon">
            <span>{{ plat.label }}</span>
          </button>
        </div>
      </div>
    </div>

    <div class="container pb-5">

      <!-- Skeleton -->
      <div v-if="loading" class="games-grid">
        <SkeletonCard v-for="n in 12" :key="n" />
      </div>

      <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

      <!-- Empty State -->
      <div v-else-if="filteredGames.length === 0" class="games-empty-state">
        <img src="/logo/search.svg" width="60" height="60" alt="" aria-hidden="true" style="opacity:0.4;">
        <h3>No games found</h3>
        <p>Try adjusting your search term, genre, or platform filter.</p>
      </div>

      <!-- Games Grid -->
      <div v-else class="games-grid">
        <router-link
          v-for="(game, index) in paginatedGames"
          :key="game.id"
          :to="`/games/${game.id}`"
          class="game-card stagger-item"
          :style="{ animationDelay: `${(index % 12) * 0.05}s` }"
          :aria-label="`View details for ${game.name}`"
        >
          <!-- Cover Image -->
          <div class="game-card-img-wrap">
            <img
              v-if="game.background_image"
              v-lazy-img="game.background_image"
              class="game-card-img"
              :alt="`${game.name} cover art`"
            >
            <div v-else class="game-card-img-placeholder">
              <img src="/logo/gamepad.svg" width="36" height="36" alt="" aria-hidden="true" style="opacity:0.4;">
            </div>
            <div class="game-card-img-overlay" aria-hidden="true"></div>

            <!-- Metacritic badge -->
            <span v-if="game.metacritic" class="mc-badge" :class="metacriticClass(game.metacritic)" :title="`Metacritic: ${game.metacritic}`">
              {{ game.metacritic }}
            </span>

            <!-- Platform icons -->
            <div class="game-card-platforms" v-if="platformIcons(game.platforms).length">
              <span v-for="p in platformIcons(game.platforms)" :key="p.key" class="platform-icon" :title="p.label">
                <img v-if="p.key === 'pc'"        src="/logo/pc.svg"               width="13" height="13" alt="PC">
                <img v-else-if="p.key === 'ps'"   src="/logo/playstation_logo.png" width="13" height="13" alt="PlayStation">
                <img v-else-if="p.key === 'xbox'" src="/logo/xbox_logo.png"        width="13" height="13" alt="Xbox">
                <img v-else-if="p.key === 'nintendo'" src="/logo/nintendo_logo.png" width="13" height="13" alt="Nintendo">
                <img v-else-if="p.key === 'mobile'"   src="/logo/mobile.svg"        width="13" height="13" alt="Mobile">
              </span>
            </div>
          </div>

          <!-- Card Body -->
          <div class="game-card-body">
            <h3 class="game-card-title">{{ game.name }}</h3>
            <div class="game-card-genres" v-if="(game.genres || []).length">
              <span v-for="genre in (game.genres || []).slice(0, 2)" :key="genre.id" class="game-genre-tag">
                {{ genre.name }}
              </span>
            </div>
            <div class="game-card-rating" v-if="game.rating">
              <div class="game-rating-bar-track">
                <div class="game-rating-bar-fill" :style="{ width: `${(game.rating / 5) * 100}%` }"></div>
              </div>
              <div class="game-rating-text">
                <img src="/logo/star.svg" width="11" height="11" alt="" aria-hidden="true">
                <span>{{ game.rating.toFixed(1) }} / 5</span>
                <span class="game-rating-count">&middot; {{ (game.ratings_count || 0).toLocaleString() }} ratings</span>
              </div>
            </div>
          </div>
        </router-link>
      </div>

      <!-- Pagination -->
      <nav v-if="!loading && totalPages > 1" class="games-pagination" aria-label="Games pagination">
        <button class="page-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
          <img src="/logo/arrow-left.svg" width="15" height="15" alt="" aria-hidden="true">
          Previous
        </button>
        <div class="page-numbers">
          <template v-for="(page, index) in visiblePages" :key="index">
            <span v-if="page === '...'" class="page-ellipsis">&#8230;</span>
            <button v-else class="page-num-btn" :class="{ active: currentPage === page }" @click="goToPage(page)">{{ page }}</button>
          </template>
        </div>
        <button class="page-btn" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">
          Next
          <img src="/logo/arrow-right.svg" width="15" height="15" alt="" aria-hidden="true">
        </button>
      </nav>

      <p v-if="!loading" class="games-page-info">
        Page {{ currentPage }} of {{ totalPages }} &middot; {{ filteredGames.length }} games shown
      </p>

    </div>
  </div>
</template>

<style scoped>
.games-page { min-height: 100vh; background: var(--bg-deep); }

/* Header */
.games-page-header {
  position: relative;
  padding: 48px 0 0;
  overflow: hidden;
  background: var(--bg-base);
}
.games-page-header-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 70% 120% at 10% 50%, rgba(124,58,237,0.14), transparent),
    radial-gradient(ellipse 50% 100% at 90% 50%, rgba(6,182,212,0.10), transparent);
  pointer-events: none;
}
.games-header-content { position: relative; z-index: 1; }
.games-title-row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 28px;
}
.games-title-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 54px;
  height: 54px;
  border-radius: 16px;
  background: var(--gradient-primary);
  color: white;
  flex-shrink: 0;
  box-shadow: 0 4px 20px rgba(124,58,237,0.4);
}
.games-title {
  font-size: 2.1rem;
  font-weight: 800;
  color: #f0f4ff !important;
  margin: 0 0 4px;
  line-height: 1;
}
.games-subtitle { font-size: 0.85rem; color: #8b9cc8 !important; margin: 0; }
.games-subtitle a { color: var(--accent-light); text-decoration: none; }
.games-subtitle strong { color: #f0f4ff !important; }

/* Filters */
.games-filters {
  display: flex;
  gap: 14px;
  padding-bottom: 16px;
}
.games-search-wrap { flex: 1; position: relative; }
.games-search-icon {
  position: absolute;
  left: 14px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-muted);
  pointer-events: none;
}
.games-search-input {
  width: 100%;
  background: rgba(15,23,42,0.6);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  padding: 11px 14px 11px 42px;
  font-size: 0.92rem;
  font-family: var(--font-family);
  transition: border-color 0.25s, box-shadow 0.25s;
  outline: none;
}
.games-search-input::placeholder { color: var(--text-muted); }
.games-search-input:focus {
  border-color: var(--primary-light);
  box-shadow: 0 0 0 3px rgba(124,58,237,0.15);
  background: rgba(15,23,42,0.85);
}
.games-genre-select {
  width: 200px;
  flex-shrink: 0;
  background: rgba(15,23,42,0.6);
  border: 1px solid var(--border-glass);
  color: var(--text-primary);
  border-radius: var(--radius-sm);
  padding: 11px 14px;
  font-size: 0.92rem;
  font-family: var(--font-family);
  outline: none;
  cursor: pointer;
}
.games-genre-select:focus {
  border-color: var(--primary-light);
  box-shadow: 0 0 0 3px rgba(124,58,237,0.15);
}

/* Platform Tabs */
.platform-tabs {
  display: flex;
  align-items: center;
  gap: 8px;
  padding-bottom: 24px;
  overflow-x: auto;
  scrollbar-width: none;
  -ms-overflow-style: none;
  flex-wrap: wrap;
}
.platform-tabs::-webkit-scrollbar { display: none; }

.platform-tab {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 30px;
  border: 1px solid var(--border-glass);
  background: rgba(15,23,42,0.5);
  color: #8b9cc8 !important;
  font-size: 0.83rem;
  font-weight: 600;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all 0.22s ease;
  white-space: nowrap;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.platform-tab:hover {
  border-color: rgba(124,58,237,0.4);
  background: rgba(124,58,237,0.1);
  color: var(--primary-light) !important;
}
.platform-tab.active {
  background: var(--gradient-primary);
  border-color: transparent;
  color: #fff !important;
  box-shadow: 0 2px 16px rgba(124,58,237,0.45);
}
.platform-tab-icon {
  width: 18px;
  height: 18px;
  object-fit: contain;
  filter: brightness(0.75);
  transition: filter 0.2s;
}
.platform-tab:hover .platform-tab-icon,
.platform-tab.active .platform-tab-icon {
  filter: brightness(1.2);
}

/* Grid */
.games-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(270px, 1fr));
  gap: 22px;
  padding-top: 8px;
}

/* Game Card */
.game-card {
  display: flex;
  flex-direction: column;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-md);
  overflow: hidden;
  text-decoration: none;
  color: var(--text-primary);
  transition: transform 0.3s cubic-bezier(0.22,1,0.36,1), box-shadow 0.3s cubic-bezier(0.22,1,0.36,1), border-color 0.3s ease;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.game-card:hover {
  transform: translateY(-8px) scale(1.015);
  box-shadow: 0 24px 60px rgba(0,0,0,0.5), 0 0 40px rgba(124,58,237,0.18);
  border-color: rgba(124,58,237,0.4);
  color: var(--text-primary);
}

/* Image */
.game-card-img-wrap {
  position: relative;
  overflow: hidden;
  height: 200px;
  flex-shrink: 0;
}
.game-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.5s ease;
  display: block;
}
.game-card:hover .game-card-img { transform: scale(1.07); }
.game-card-img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-glass);
  color: var(--text-muted);
}
.game-card-img-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, transparent 40%, rgba(5,7,15,0.65) 75%, rgba(5,7,15,0.95) 100%);
  pointer-events: none;
}

/* Metacritic */
.mc-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 0.78rem;
  font-weight: 800;
  padding: 4px 9px;
  border-radius: 7px;
  min-width: 38px;
  text-align: center;
  box-shadow: 0 2px 10px rgba(0,0,0,0.5);
  letter-spacing: 0.02em;
  z-index: 2;
}
.mc-green  { background: #15803d; color: #d1fae5; border: 1px solid rgba(21,128,61,0.4); }
.mc-yellow { background: #92400e; color: #fde68a; border: 1px solid rgba(146,64,14,0.4); }
.mc-red    { background: #991b1b; color: #fee2e2; border: 1px solid rgba(153,27,27,0.4); }
.mc-none   { display: none; }

/* Platform icons */
.game-card-platforms {
  position: absolute;
  bottom: 10px;
  right: 10px;
  display: flex;
  gap: 5px;
  z-index: 2;
}
.platform-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  border-radius: 6px;
  background: rgba(5,7,15,0.72);
  color: rgba(255,255,255,0.8);
  backdrop-filter: blur(6px);
  border: 1px solid rgba(255,255,255,0.1);
  transition: background 0.2s, color 0.2s;
}
.game-card:hover .platform-icon {
  background: rgba(124,58,237,0.55);
  color: #fff;
}

/* Card body */
.game-card-body {
  padding: 16px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  flex: 1;
}
.game-card-title {
  font-size: 0.97rem;
  font-weight: 700;
  line-height: 1.4;
  color: #f0f4ff !important;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* Genre tags */
.game-card-genres { display: flex; flex-wrap: wrap; gap: 6px; }
.game-genre-tag {
  font-size: 0.68rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
  background: rgba(124,58,237,0.15);
  color: var(--primary-light);
  border: 1px solid rgba(124,58,237,0.28);
  letter-spacing: 0.02em;
  transition: background 0.2s;
}
.game-card:hover .game-genre-tag {
  background: rgba(124,58,237,0.3);
  color: #ddd4ff;
}

/* Rating */
.game-card-rating { margin-top: auto; display: flex; flex-direction: column; gap: 6px; }
.game-rating-bar-track {
  height: 4px;
  border-radius: 2px;
  background: rgba(255,255,255,0.08);
  overflow: hidden;
}
.game-rating-bar-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--gradient-primary);
}
.game-rating-text {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.75rem;
  color: #8b9cc8 !important;
}
.game-rating-count { color: #4a5580 !important; font-size: 0.7rem; }

/* Empty state */
.games-empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 80px 20px;
  color: var(--text-muted);
  text-align: center;
}
.games-empty-state h3 { color: var(--text-secondary); margin: 0; }
.games-empty-state p { color: var(--text-muted); margin: 0; font-size: 0.9rem; }

/* Pagination */
.games-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  margin-top: 48px;
  flex-wrap: wrap;
}
.page-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  border-radius: var(--radius-sm);
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  color: var(--text-secondary);
  font-size: 0.88rem;
  font-weight: 600;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all 0.2s ease;
}
.page-btn:hover:not(:disabled) {
  background: var(--bg-glass-hover);
  color: var(--primary-light);
  border-color: rgba(124,58,237,0.35);
}
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-numbers { display: flex; align-items: center; gap: 6px; }
.page-num-btn {
  width: 38px;
  height: 38px;
  border-radius: var(--radius-sm);
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  color: var(--text-secondary);
  font-size: 0.88rem;
  font-weight: 600;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}
.page-num-btn:hover {
  background: var(--bg-glass-hover);
  color: var(--primary-light);
  border-color: rgba(124,58,237,0.35);
}
.page-num-btn.active {
  background: var(--gradient-primary);
  border-color: transparent;
  color: white;
  box-shadow: 0 2px 12px rgba(124,58,237,0.45);
}
.page-ellipsis { color: var(--text-muted); padding: 0 4px; }
.games-page-info { text-align: center; color: var(--text-muted); font-size: 0.82rem; margin-top: 16px; }
</style>
