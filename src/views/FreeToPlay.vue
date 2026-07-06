// src/views/FreeToPlay.vue
<script>
import { freeToGameApi } from '../api'
import SkeletonCard from '../components/SkeletonCard.vue'

// All FreeToGame supported categories
const ALL_CATEGORIES = [
  'mmorpg','shooter','strategy','moba','racing','sports','social',
  'sandbox','open-world','survival','pvp','pve','pixel','voxel',
  'zombie','turn-based','first-person','third-Person','top-down',
  'tank','space','sailing','side-scroller','superhero','permadeath',
  'card','battle-royale','mmo','mmofps','mmotps','3d','2d','anime',
  'fantasy','sci-fi','fighting','action-rpg','action','military',
  'martial-arts','flight','low-spec','tower-defense','horror','mmorts'
]

export default {
  components: { SkeletonCard },

  data() {
    return {
      games: [],
      loading: false,
      error: null,

      // API-level filters
      platform: 'all',
      category: '',
      sortBy: 'relevance',

      // Multi-tag mode (uses /filter endpoint)
      selectedTags: [],
      tagMode: false,

      // Client-side search (FreeToGame has no search endpoint)
      searchTerm: '',

      // Pagination
      currentPage: 1,
      itemsPerPage: 12,

      // Constants
      allCategories: ALL_CATEGORIES
    }
  },

  computed: {
    // Apply client-side text search on top of API results
    filteredGames() {
      const term = this.searchTerm.toLowerCase().trim()
      if (!term) return this.games
      return this.games.filter(g =>
        g.title.toLowerCase().includes(term) ||
        (g.short_description || '').toLowerCase().includes(term)
      )
    },

    totalPages() {
      return Math.ceil(this.filteredGames.length / this.itemsPerPage)
    },

    paginatedGames() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      return this.filteredGames.slice(start, start + this.itemsPerPage)
    },

    visiblePages() {
      const total = this.totalPages
      const pages = []
      if (total <= 7) {
        for (let i = 1; i <= total; i++) pages.push(i)
      } else {
        pages.push(1)
        if (this.currentPage > 4) pages.push('...')
        const s = Math.max(2, this.currentPage - 1)
        const e = Math.min(total - 1, this.currentPage + 1)
        for (let i = s; i <= e; i++) pages.push(i)
        if (this.currentPage < total - 3) pages.push('...')
        pages.push(total)
      }
      return pages
    },

    // Shows the active filter summary under the panel
    activeSummary() {
      const parts = []
      if (this.tagMode && this.selectedTags.length)
        parts.push(`Tags: ${this.selectedTags.join(' + ')}`)
      else {
        if (this.platform !== 'all') parts.push(`Platform: ${this.platform}`)
        if (this.category) parts.push(`Category: ${this.category}`)
      }
      if (this.sortBy !== 'relevance') parts.push(`Sort: ${this.sortBy}`)
      return parts.length ? parts.join('  ·  ') : 'Showing all games'
    }
  },

  watch: {
    searchTerm() { this.currentPage = 1 }
  },

  methods: {
    platformIcon(platform) {
      if (!platform) return '🎮'
      if (platform.toLowerCase().includes('browser')) return '🌐'
      return '💻'
    },

    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },

    toggleTag(tag) {
      const idx = this.selectedTags.indexOf(tag)
      if (idx === -1) this.selectedTags.push(tag)
      else this.selectedTags.splice(idx, 1)
    },

    clearFilters() {
      this.platform = 'all'
      this.category = ''
      this.sortBy = 'relevance'
      this.selectedTags = []
      this.searchTerm = ''
      this.fetchGames()
    },

    async fetchGames() {
      this.loading = true
      this.error = null
      this.currentPage = 1
      try {
        let data

        if (this.tagMode && this.selectedTags.length) {
          // ── Multi-tag filter endpoint ──
          const params = { tag: this.selectedTags.join('.') }
          if (this.platform !== 'all') params.platform = this.platform
          if (this.sortBy !== 'relevance') params.sort = this.sortBy
          const res = await freeToGameApi.get('/filter', { params })
          data = res.data
        } else {
          // ── Standard games list endpoint ──
          const params = {}
          if (this.platform !== 'all') params.platform = this.platform
          if (this.category) params.category = this.category
          if (this.sortBy !== 'relevance') params['sort-by'] = this.sortBy
          const res = await freeToGameApi.get('/games', { params })
          data = res.data
        }

        this.games = Array.isArray(data) ? data : []
      } catch (err) {
        console.error(err)
        this.error = 'Failed to load games. Please try again.'
        this.games = []
      } finally {
        this.loading = false
      }
    }
  },

  mounted() {
    this.fetchGames()
  }
}
</script>

<template>
  <div class="container py-4">

    <!-- Header -->
    <div class="section-header">
      <span class="section-icon">🆓</span>
      <h1 class="mb-0">Free to Play</h1>
    </div>
    <p class="text-muted mb-4">
      {{ games.length > 0 ? filteredGames.length.toLocaleString() + ' games' : 'Loading games…' }}
      — browser &amp; PC titles, no cost required.
      <span style="opacity:0.6;">(Powered by FreeToGame)</span>
    </p>

    <!-- ══ Filter Panel ═══════════════════════════════════════════════ -->
    <div class="card ftg-filter-panel mb-3">
      <div class="card-body">

        <!-- Row 1: Search + Platform + Sort -->
        <div class="row g-3 mb-3">

          <div class="col-md-4">
            <label class="filter-label">🔍 Search</label>
            <input
              v-model="searchTerm"
              type="text"
              class="form-control"
              placeholder="Search by title or description…"
            >
          </div>

          <div class="col-md-3">
            <label class="filter-label">🖥️ Platform</label>
            <div class="btn-group w-100" role="group" aria-label="Platform filter">
              <button
                v-for="p in ['all','windows','browser']"
                :key="p"
                type="button"
                class="btn btn-sm"
                :class="platform === p ? 'btn-primary' : 'btn-outline-secondary'"
                @click="platform = p; fetchGames()"
              >
                {{ p === 'all' ? '🌍 All' : p === 'windows' ? '💻 Windows' : '🌐 Browser' }}
              </button>
            </div>
          </div>

          <div class="col-md-3">
            <label class="filter-label">📊 Sort By</label>
            <select
              v-model="sortBy"
              class="form-select"
              @change="fetchGames()"
            >
              <option value="relevance">🔥 Relevance</option>
              <option value="popularity">👥 Popularity</option>
              <option value="release-date">📅 Release Date</option>
              <option value="alphabetical">🔤 Alphabetical</option>
            </select>
          </div>

          <div class="col-md-2 d-flex flex-column justify-content-end">
            <button
              class="btn btn-outline-danger btn-sm"
              @click="clearFilters"
              title="Reset all filters"
            >
              ✕ Clear
            </button>
          </div>

        </div>

        <!-- Row 2: Category OR Multi-tag toggle -->
        <div class="row g-3 align-items-start">

          <!-- Mode toggle -->
          <div class="col-12 mb-1">
            <div class="d-flex align-items-center gap-3">
              <span class="filter-label mb-0">Filter Mode:</span>
              <div class="form-check form-switch mb-0">
                <input
                  class="form-check-input"
                  type="checkbox"
                  id="tagModeSwitch"
                  v-model="tagMode"
                  @change="selectedTags = []; category = ''; fetchGames()"
                >
                <label class="form-check-label" for="tagModeSwitch" style="font-size:0.85rem;">
                  {{ tagMode ? '🏷️ Multi-tag mode' : '📂 Category mode' }}
                </label>
              </div>
            </div>
          </div>

          <!-- Category mode -->
          <div class="col-md-5" v-if="!tagMode">
            <label class="filter-label">📂 Category</label>
            <select
              v-model="category"
              class="form-select"
              @change="fetchGames()"
            >
              <option value="">All Categories</option>
              <option
                v-for="cat in allCategories"
                :key="cat"
                :value="cat"
              >
                {{ cat.charAt(0).toUpperCase() + cat.slice(1).replace(/-/g, ' ') }}
              </option>
            </select>
          </div>

          <!-- Multi-tag mode -->
          <div class="col-12" v-else>
            <label class="filter-label">
              🏷️ Tags
              <span class="text-muted" style="font-size:0.75rem; font-weight:400;">
                (select multiple — uses FreeToGame /filter endpoint)
              </span>
            </label>
            <div class="ftg-tag-cloud">
              <button
                v-for="tag in allCategories"
                :key="tag"
                type="button"
                class="ftg-tag-chip"
                :class="{ active: selectedTags.includes(tag) }"
                @click="toggleTag(tag); fetchGames()"
              >
                {{ tag }}
              </button>
            </div>
          </div>

        </div>

      </div>
    </div>

    <!-- Active filter summary -->
    <div class="d-flex align-items-center gap-3 mb-3 flex-wrap">
      <small class="text-muted ftg-summary">{{ activeSummary }}</small>
      <span v-if="!loading" class="badge ms-auto" style="background:var(--gradient-primary);">
        {{ filteredGames.length }} results
      </span>
    </div>

    <!-- Skeleton Loading -->
    <div v-if="loading" class="row">
      <div class="col-md-4 mb-4" v-for="n in 12" :key="n">
        <SkeletonCard />
      </div>
    </div>

    <!-- Error -->
    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <!-- Empty State -->
    <div v-else-if="filteredGames.length === 0" class="empty-state">
      <div class="empty-state-icon">🔍</div>
      <h3>No games found</h3>
      <p>Try adjusting your filters or clearing the search term.</p>
      <button class="btn btn-primary" @click="clearFilters">Clear All Filters</button>
    </div>

    <!-- Games Grid -->
    <div v-else class="row">
      <div
        class="col-md-4 mb-4"
        v-for="(game, index) in paginatedGames"
        :key="game.id"
      >
        <router-link :to="`/free-to-play/${game.id}`" class="text-decoration-none">
          <div
            class="card h-100 ftg-card stagger-item"
            :style="{ animationDelay: `${(index % 12) * 0.04}s` }"
          >

            <!-- Thumbnail -->
            <div style="position:relative; overflow:hidden;">
              <img
                v-lazy-img="game.thumbnail"
                class="card-img-top"
                :alt="`${game.title} thumbnail`"
                style="height:180px; object-fit:cover;"
              >
              <span class="ftg-free-badge">FREE</span>
              <span
                class="badge"
                style="position:absolute; bottom:8px; left:8px; background:rgba(0,0,0,0.7); font-size:0.7rem;"
              >
                {{ platformIcon(game.platform) }} {{ game.platform }}
              </span>
            </div>

            <div class="card-body d-flex flex-column">
              <h5 class="card-title" style="font-size:0.95rem; line-height:1.35;">
                {{ game.title }}
              </h5>

              <p
                class="card-text text-muted mb-3"
                style="font-size:0.82rem; flex:1; display:-webkit-box; line-clamp:2; -webkit-line-clamp:2; -webkit-box-orient:vertical; overflow:hidden;"
              >
                {{ game.short_description }}
              </p>

              <div class="d-flex align-items-center justify-content-between">
                <span class="badge bg-primary" style="font-size:0.7rem;">
                  {{ game.genre }}
                </span>
                <span class="btn btn-sm ftg-play-btn" style="font-size:0.75rem; padding:3px 12px;">
                  See Details →
                </span>
              </div>
            </div>

          </div>
        </router-link>
      </div>
    </div>

    <!-- Pagination -->
    <nav v-if="!loading && totalPages > 1">
      <ul class="pagination justify-content-center">
        <li class="page-item" :class="{ disabled: currentPage === 1 }">
          <button class="page-link" @click="goToPage(currentPage - 1)">← Previous</button>
        </li>
        <li
          v-for="(page, i) in visiblePages"
          :key="i"
          class="page-item"
          :class="{ active: currentPage === page }"
        >
          <span v-if="page === '...'" class="page-link">...</span>
          <button v-else class="page-link" @click="goToPage(page)">{{ page }}</button>
        </li>
        <li class="page-item" :class="{ disabled: currentPage === totalPages }">
          <button class="page-link" @click="goToPage(currentPage + 1)">Next →</button>
        </li>
      </ul>
    </nav>

    <p v-if="!loading && totalPages > 1" class="text-center text-muted mt-2" style="font-size:0.85rem;">
      Showing {{ paginatedGames.length }} of {{ filteredGames.length }} games
    </p>

  </div>
</template>

<style scoped>
/* Filter panel */
.ftg-filter-panel {
  border: 1px solid var(--border-glass, rgba(255,255,255,0.1));
}
.filter-label {
  display: block;
  font-size: 0.78rem;
  color: var(--text-muted, #94a3b8);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

/* Tag cloud */
.ftg-tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  max-height: 140px;
  overflow-y: auto;
  padding: 4px 0;
}
.ftg-tag-chip {
  padding: 3px 12px;
  border-radius: 20px;
  font-size: 0.75rem;
  border: 1px solid var(--border-glass, rgba(255,255,255,0.15));
  background: var(--bg-glass, rgba(255,255,255,0.05));
  color: var(--text-muted, #94a3b8);
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}
.ftg-tag-chip:hover {
  border-color: var(--accent-primary, #6366f1);
  color: #fff;
}
.ftg-tag-chip.active {
  background: var(--gradient-primary, linear-gradient(135deg, #6366f1, #8b5cf6));
  border-color: transparent;
  color: #fff;
  font-weight: 600;
}

/* Active summary */
.ftg-summary {
  font-size: 0.8rem;
  opacity: 0.75;
  font-style: italic;
}

/* Cards */
.ftg-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.ftg-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.35);
}

.ftg-free-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  background: linear-gradient(135deg, #4ade80, #16a34a);
  color: #fff;
  font-weight: 700;
  font-size: 0.72rem;
  padding: 3px 9px;
  border-radius: 20px;
  letter-spacing: 0.8px;
  box-shadow: 0 2px 8px rgba(74,222,128,0.45);
}

.ftg-play-btn {
  background: var(--gradient-primary, linear-gradient(135deg, #6366f1, #8b5cf6));
  color: #fff;
  border: none;
  border-radius: 20px;
  transition: opacity 0.2s;
}
.ftg-play-btn:hover { opacity: 0.85; color: #fff; }
</style>
