// src/views/Games.vue
<script>
export default {
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
      }
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

    <h1 class="mb-4">Games</h1>

    <div class="row mb-4 g-3">
      <div class="col-md-8">
        <input
          type="text"
          class="form-control"
          placeholder="Search games..."
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

    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading games...</p>
    </div>

    <div
      v-else-if="error"
      class="alert alert-danger"
    >
      {{ error }}
    </div>

    <div
      v-else-if="filteredGames.length === 0"
      class="alert alert-warning"
    >
      No games found matching your search.
    </div>

    <div v-else class="row">

      <div
        class="col-md-4 mb-4"
        v-for="game in paginatedGames"
        :key="game.id"
      >

        <router-link
          :to="`/games/${game.id}`"
          class="text-decoration-none text-dark"
        >

          <div class="card h-100 shadow-sm">

            <img
              v-lazy-img="game.thumbnail"
              class="card-img-top"
              :alt="`${game.title} game thumbnail`"
            >

            <div class="card-body">

              <h5 class="card-title">
                {{ game.title }}
              </h5>

              <p class="card-text">
                Genre: {{ game.genre }}
              </p>

              <p class="card-text">
                Platform: {{ game.platform }}
              </p>

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
            Previous
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
            Next
          </button>
        </li>

      </ul>
    </nav>

    <p v-if="!loading" class="text-center text-muted mt-2">
      Page {{ currentPage }} of {{ totalPages }}
      ({{ filteredGames.length }} games)
    </p>

  </div>
</template>