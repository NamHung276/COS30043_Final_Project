// src/views/Games.vue
<script>
import SkeletonCard from '../components/SkeletonCard.vue'
import { rawgApi } from '../api'

export default {
  components: { SkeletonCard },

  data() {
    return {
      games: [],
      loading: true,
      error: null,
      searchTerm: '',
      selectedGenre: 'All',
      genres: ['All'],
      currentPage: 1,
      itemsPerPage: 12,
      totalCount: 0,
      searchTimeout: null
    }
  },

  computed: {
    filteredGames() {
      if (this.selectedGenre === 'All') return this.games
      return this.games.filter(g =>
        g.genres?.some(genre => genre.name === this.selectedGenre)
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
      const names = platforms.map(p => p.platform.slug)
      if (names.some(n => n.includes('pc'))) icons.push({ icon: '🖥️', label: 'PC' })
      if (names.some(n => n.includes('playstation'))) icons.push({ icon: '🎮', label: 'PlayStation' })
      if (names.some(n => n.includes('xbox'))) icons.push({ icon: '🟩', label: 'Xbox' })
      if (names.some(n => n.includes('nintendo') || n.includes('switch'))) icons.push({ icon: '🕹️', label: 'Nintendo' })
      if (names.some(n => n.includes('ios') || n.includes('android'))) icons.push({ icon: '📱', label: 'Mobile' })
      return icons
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
          page_size: 40,
          ordering: '-rating',
        }
        if (this.searchTerm) params.search = this.searchTerm

        const { data } = await rawgApi.get('/games', { params })
        this.games = data.results || []
        this.totalCount = data.count || 0

        // Build genre list from results
        const genreSet = new Set()
        this.games.forEach(g => g.genres?.forEach(genre => genreSet.add(genre.name)))
        this.genres = ['All', ...Array.from(genreSet).sort()]
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
  <div class="container py-4">

    <div class="section-header">
      <span class="section-icon">🎮</span>
      <h1 class="mb-0">Games</h1>
    </div>
    <p class="text-muted mb-4" style="font-size:0.85rem;">
      Powered by <a href="https://rawg.io" target="_blank" rel="noopener noreferrer" style="color:var(--accent-primary);">RAWG</a>
      · {{ totalCount.toLocaleString() }} games in database
    </p>

    <!-- Search & Filter -->
    <div class="row mb-4 g-3">
      <div class="col-md-8">
        <input
          type="text"
          class="form-control"
          placeholder="🔍 Search games..."
          aria-label="Search games"
          v-model="searchTerm"
        >
      </div>
      <div class="col-md-4">
        <select
          class="form-select"
          aria-label="Filter games by genre"
          v-model="selectedGenre"
        >
          <option v-for="genre in genres" :key="genre" :value="genre">
            {{ genre }}
          </option>
        </select>
      </div>
    </div>

    <!-- Skeleton Loading -->
    <div v-if="loading" class="row">
      <div class="col-md-4 mb-4" v-for="n in 12" :key="n">
        <SkeletonCard />
      </div>
    </div>

    <div v-else-if="error" class="alert alert-danger">{{ error }}</div>

    <!-- Empty State -->
    <div v-else-if="filteredGames.length === 0" class="empty-state">
      <div class="empty-state-icon">🔍</div>
      <h3>No games found</h3>
      <p>Try a different search term or genre filter.</p>
    </div>

    <!-- Games Grid -->
    <div v-else class="row">
      <div
        class="col-md-4 mb-4"
        v-for="(game, index) in paginatedGames"
        :key="game.id"
      >
        <router-link :to="`/games/${game.id}`" class="text-decoration-none">
          <div
            class="card h-100 game-card stagger-item"
            :style="{ animationDelay: `${(index % 12) * 0.04}s` }"
          >

            <!-- Cover Image -->
            <div style="position:relative; overflow:hidden;">
              <img
                v-if="game.background_image"
                v-lazy-img="game.background_image"
                class="card-img-top"
                :alt="`${game.name} cover art`"
                style="height:180px; object-fit:cover;"
              >
              <div
                v-else
                class="d-flex align-items-center justify-content-center"
                style="height:180px; background:var(--bg-glass);"
              >
                <span style="font-size:2.5rem;">🎮</span>
              </div>

              <!-- Metacritic badge -->
              <span
                v-if="game.metacritic"
                class="mc-badge"
                :class="metacriticClass(game.metacritic)"
              >
                {{ game.metacritic }}
              </span>
            </div>

            <div class="card-body">
              <h5 class="card-title" style="font-size:0.95rem; line-height:1.35;">
                {{ game.name }}
              </h5>

              <div class="d-flex gap-2 flex-wrap align-items-center">
                <!-- Genre tags -->
                <span
                  v-for="genre in (game.genres || []).slice(0, 2)"
                  :key="genre.id"
                  class="badge bg-primary"
                  style="font-size:0.7rem;"
                >
                  {{ genre.name }}
                </span>

                <!-- Platform icons -->
                <span class="ms-auto d-flex gap-1">
                  <span
                    v-for="p in platformIcons(game.platforms)"
                    :key="p.label"
                    :title="p.label"
                    style="font-size:0.85rem;"
                  >
                    {{ p.icon }}
                  </span>
                </span>
              </div>

              <!-- Rating bar -->
              <div class="mt-2" v-if="game.rating">
                <div
                  style="height:3px; border-radius:2px; background:var(--bg-glass); overflow:hidden;"
                >
                  <div
                    :style="{
                      width: `${(game.rating / 5) * 100}%`,
                      height: '100%',
                      background: 'var(--gradient-primary)',
                      borderRadius: '2px'
                    }"
                  ></div>
                </div>
                <small class="text-muted" style="font-size:0.72rem;">
                  ★ {{ game.rating.toFixed(1) }} / 5 · {{ (game.ratings_count || 0).toLocaleString() }} ratings
                </small>
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
          v-for="(page, index) in visiblePages"
          :key="index"
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

    <p v-if="!loading" class="text-center text-muted mt-2" style="font-size:0.85rem;">
      Page {{ currentPage }} of {{ totalPages }}
      · {{ filteredGames.length }} games shown
    </p>

  </div>
</template>

<style scoped>
.game-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.game-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 40px rgba(0,0,0,0.35);
}

.mc-badge {
  position: absolute;
  top: 10px;
  right: 10px;
  font-size: 0.8rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
  min-width: 36px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0,0,0,0.4);
}
.mc-green  { background: #15803d; color: #fff; }
.mc-yellow { background: #a16207; color: #fff; }
.mc-red    { background: #b91c1c; color: #fff; }
.mc-none   { display: none; }
</style>