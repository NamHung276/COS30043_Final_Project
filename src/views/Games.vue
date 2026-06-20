// src/views/Games.vue
<script>
import SkeletonCard from '../components/SkeletonCard.vue'

export default {
  components: { SkeletonCard },

  data() {
    return {
      games: [],
      loading: true,
      error: null,
      searchTerm: '',
      selectedGenre: 'All',
      currentPage: 1,
      itemsPerPage: 12
    }
  },

  computed: {
    filteredGames() {
      return this.games.filter(game => {

        const matchesSearch =
          game.title
            .toLowerCase()
            .includes(this.searchTerm.toLowerCase())

        const matchesGenre =
          this.selectedGenre === 'All' ||
          game.genre === this.selectedGenre

        return matchesSearch && matchesGenre
      })
    },

    genres() {
      return [
        'All',
        ...new Set(
          this.games.map(game => game.genre)
        )
      ]
    },

    totalPages() {
      return Math.ceil(
        this.filteredGames.length / this.itemsPerPage
      )
    },

    paginatedGames() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredGames.slice(start, end)
    },

    visiblePages() {
      const pages = []

      if (this.totalPages <= 7) {
        for (let i = 1; i <= this.totalPages; i++) {
          pages.push(i)
        }
      }
      else {
        pages.push(1)

        if (this.currentPage > 4) {
          pages.push('...')
        }

        const start = Math.max(2, this.currentPage - 1)
        const end = Math.min(
          this.totalPages - 1,
          this.currentPage + 1
        )

        for (let i = start; i <= end; i++) {
          pages.push(i)
        }

        if (this.currentPage < this.totalPages - 3) {
          pages.push('...')
        }

        pages.push(this.totalPages)
      }

      return pages
    }
  },

  watch: {
    searchTerm() {
      this.currentPage = 1
    },
    selectedGenre() {
      this.currentPage = 1
    }
  },

  methods: {
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },

    platformIcon(platform) {
      if (!platform) return '🎮'
      if (platform.toLowerCase().includes('browser')) return '🌐'
      return '💻'
    }
  },

  async mounted() {
    try {
      const response = await fetch(
        'https://www.freetogame.com/api/games'
      )

      this.games = await response.json()
    }
    catch (error) {
      console.error(error)
      this.error = 'Failed to load games. Please try again later.'
    }
    finally {
      this.loading = false
    }
  }
}
</script>

<template>
  <div class="container py-4">

    <div class="section-header">
      <span class="section-icon">🎮</span>
      <h1 class="mb-0">Games</h1>
    </div>

    <!-- Search & Filter -->
    <div class="row mb-4 g-3">
      <div class="col-md-8">
        <div class="position-relative">
          <input
            type="text"
            class="form-control"
            placeholder="🔍 Search games..."
            aria-label="Search games"
            v-model="searchTerm"
            style="padding-left: 14px;"
          >
        </div>
      </div>
      <div class="col-md-4">
        <select
          class="form-select"
          aria-label="Filter games by genre"
          v-model="selectedGenre"
        >
          <option
            v-for="genre in genres"
            :key="genre"
            :value="genre"
          >
            {{ genre }}
          </option>
        </select>
      </div>
    </div>

    <!-- Skeleton Loading -->
    <div v-if="loading" class="row">
      <div
        class="col-md-4 mb-4"
        v-for="n in 12"
        :key="n"
      >
        <SkeletonCard />
      </div>
    </div>

    <div
      v-else-if="error"
      class="alert alert-danger"
    >
      {{ error }}
    </div>

    <!-- Empty State -->
    <div
      v-else-if="filteredGames.length === 0"
      class="empty-state"
    >
      <div class="empty-state-icon">🔍</div>
      <h3>No games found</h3>
      <p>Try a different search term or genre filter.</p>
    </div>

    <div v-else class="row">

      <div
        class="col-md-4 mb-4"
        v-for="(game, index) in paginatedGames"
        :key="game.id"
      >

        <router-link
          :to="`/games/${game.id}`"
          class="text-decoration-none"
        >

          <div
            class="card h-100 stagger-item"
            :style="{ animationDelay: `${(index % 12) * 0.04}s` }"
          >

            <img
              v-lazy-img="game.thumbnail"
              class="card-img-top"
              :alt="`${game.title} game thumbnail`"
              style="height: 180px; object-fit: cover;"
            >

            <div class="card-body">

              <h5 class="card-title" style="font-size: 1rem;">
                {{ game.title }}
              </h5>

              <div class="d-flex gap-2 flex-wrap">
                <span class="badge bg-primary">
                  {{ game.genre }}
                </span>
                <span class="badge" style="background: var(--bg-glass-hover); color: var(--text-secondary);">
                  {{ platformIcon(game.platform) }} {{ game.platform }}
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

        <li
          class="page-item"
          :class="{ disabled: currentPage === 1 }"
        >
          <button
            class="page-link"
            @click="goToPage(currentPage - 1)"
          >
            ← Previous
          </button>
        </li>

        <li
          v-for="(page, index) in visiblePages"
          :key="index"
          class="page-item"
          :class="{ active: currentPage === page }"
        >

          <span
            v-if="page === '...'"
            class="page-link"
          >
            ...
          </span>

          <button
            v-else
            class="page-link"
            @click="goToPage(page)"
          >
            {{ page }}
          </button>

        </li>

        <li
          class="page-item"
          :class="{ disabled: currentPage === totalPages }"
        >
          <button
            class="page-link"
            @click="goToPage(currentPage + 1)"
          >
            Next →
          </button>
        </li>

      </ul>
    </nav>

    <p v-if="!loading" class="text-center text-muted mt-2" style="font-size: 0.85rem;">
      Page {{ currentPage }} of {{ totalPages }}
      · {{ filteredGames.length }} games
    </p>

  </div>
</template>