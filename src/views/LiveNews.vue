// src/views/LiveNews.vue
<script>
import SkeletonCard from '../components/SkeletonCard.vue'

export default {
  components: { SkeletonCard },

  data() {
    return {
      articles: [],
      loading: true,
      error: null,

      searchTerm: '',
      currentPage: 1,
      itemsPerPage: 9,
      
      sortOption: 'newest',
      selectedSource: '',
      lastUpdated: ''
    }
  },

  computed: {
    filteredArticles() {
      const term = this.searchTerm.toLowerCase()

      let filtered = this.articles.filter(article => {
        const title = article.title || ''
        const description = article.description || ''
        const source = article.source?.name || ''

        return (
          title.toLowerCase().includes(term) ||
          description.toLowerCase().includes(term) ||
          source.toLowerCase().includes(term)
        )
      })

      if (this.selectedSource) {
        filtered = filtered.filter(
          article =>
            article.source?.name === this.selectedSource
        )
      }

      if (this.sortOption === 'newest') {
        filtered.sort(
          (a, b) =>
            new Date(b.publishedAt) -
            new Date(a.publishedAt)
        )
      }

      if (this.sortOption === 'oldest') {
        filtered.sort(
          (a, b) =>
            new Date(a.publishedAt) -
            new Date(b.publishedAt)
        )
      }

      return filtered
    },

    availableSources() {
      return [
        ...new Set(
          this.articles.map(
            article => article.source?.name
          )
        )
      ].filter(Boolean)
    },

    totalPages() {
      return Math.ceil(
        this.filteredArticles.length / this.itemsPerPage
      )
    },

    paginatedArticles() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredArticles.slice(start, end)
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

        const start =
          Math.max(2, this.currentPage - 1)

        const end =
          Math.min(
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
    }
  },

  methods: {
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },

    formatDate(dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString('en-AU', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      })
    }
  },

  async mounted() {
    try {
      // Using Vite proxy — /newsapi routes to https://newsapi.org
      const response = await fetch(
        '/newsapi/v2/everything?q=gaming OR "video games"&language=en&sortBy=publishedAt&pageSize=100&apiKey=a125829a83b64ea99e6889447f348dc8'
      )

      const data = await response.json()

      if (data.status === 'error') {
        this.error = data.message
        return
      }

      // Filter out articles with removed/null content
      this.articles = (data.articles || []).filter(
        article =>
          article.title !== '[Removed]' &&
          article.description !== null
      )

      this.lastUpdated = new Date().toLocaleString()

    } catch (error) {
      console.error(error)
      this.error = 'Failed to load live news. Please try again later.'
    } finally {
      this.loading = false
    }
  }
}
</script>

<template>
  <div class="container py-4">

    <div class="section-header">
      <span class="section-icon">📡</span>
      <h1 class="mb-0">Live Gaming News</h1>
    </div>

    <div class="d-flex align-items-center gap-3 mb-2 flex-wrap">
      <p class="text-muted mb-0" style="font-size: 0.85rem;">
        Last Updated: {{ lastUpdated }}
      </p>
      <span
        v-if="!loading"
        class="badge"
        style="background: var(--gradient-primary);"
      >
        {{ filteredArticles.length }} articles
      </span>
    </div>
    
    <p class="text-muted mb-4">
      Latest gaming news from trusted sources around the world.
      <span style="opacity: 0.6;">(Powered by NewsAPI)</span>
    </p>

    <!-- Search & Filter -->
    <div class="row mb-4 g-3">

      <div class="col-md-8">
        <input
          v-model="searchTerm"
          type="text"
          class="form-control"
          placeholder="🔍 Search live news..."
        >
      </div>

      <div class="col-md-2">
        <select
          v-model="sortOption"
          class="form-select"
        >
          <option value="newest">
            Newest First
          </option>

          <option value="oldest">
            Oldest First
          </option>
        </select>
      </div>

      <div class="col-md-2">
        <select
          v-model="selectedSource"
          class="form-select"
        >
          <option value="">
            All Sources
          </option>

          <option
            v-for="source in availableSources"
            :key="source"
            :value="source"
          >
            {{ source }}
          </option>
        </select>
      </div>

    </div>

    <!-- Skeleton Loading -->
    <div v-if="loading" class="row">
      <div
        class="col-md-4 mb-4"
        v-for="n in 9"
        :key="n"
      >
        <SkeletonCard />
      </div>
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="alert alert-danger"
    >
      {{ error }}
    </div>

    <!-- Empty State -->
    <div
      v-else-if="filteredArticles.length === 0"
      class="empty-state"
    >
      <div class="empty-state-icon">📰</div>
      <h3>No articles found</h3>
      <p>Try adjusting your search or filter settings.</p>
    </div>

    <!-- Articles Grid -->
    <div v-else class="row">
      <div
        class="col-md-4 mb-4"
        v-for="(article, index) in paginatedArticles"
        :key="article.url"
      >
        <div
          class="card h-100 stagger-item"
          :style="{ animationDelay: `${(index % 9) * 0.04}s` }"
        >

          <div style="position: relative; overflow: hidden;">
            <img
              v-if="article.urlToImage"
              v-lazy-img="article.urlToImage"
              class="card-img-top"
              :alt="article.title"
              style="height: 200px; object-fit: cover;"
            >
            <div
              v-else
              class="d-flex align-items-center justify-content-center"
              style="height: 200px; background: var(--bg-glass);"
            >
              <span class="text-muted" style="font-size: 2rem;">📰</span>
            </div>
            <!-- Source badge overlay -->
            <a
              :href="article.url"
              target="_blank"
              class="badge text-decoration-none"
              style="position: absolute; top: 10px; left: 10px; background: var(--gradient-primary); font-size: 0.72rem;"
            >
              {{ article.source.name }}
            </a>
          </div>

          <div class="card-body text-start d-flex flex-column">
            <small class="text-muted mb-2">
              {{ formatDate(article.publishedAt) }}
              <span v-if="article.author"> · {{ article.author }}</span>
            </small>

            <h5 class="card-title" style="font-size: 0.95rem; line-height: 1.4;">
              {{ article.title }}
            </h5>

            <p class="card-text text-muted" style="font-size: 0.85rem; flex: 1;">
              {{
                article.description
                  ? article.description.slice(0, 120) + '...'
                  : 'No description available.'
              }}
            </p>

            <a
              :href="article.url"
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn-outline-primary btn-sm mt-auto"
            >
              Read More →
            </a>
          </div>

        </div>
      </div>
    </div>

    <!-- Pagination -->
    <nav v-if="totalPages > 1">
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

    <p class="text-center text-muted mt-2" style="font-size: 0.85rem;">
      Page {{ currentPage }} of {{ totalPages }}
      · {{ filteredArticles.length }} articles
    </p>

  </div>
</template>