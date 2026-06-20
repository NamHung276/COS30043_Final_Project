// src/views/LiveNews.vue
<script>
export default {
  data() {
    return {
      articles: [],
      loading: true,
      error: null,
      searchTerm: '',
      currentPage: 1,
      itemsPerPage: 6
    }
  },

  computed: {
    filteredArticles() {
      const term = this.searchTerm.toLowerCase()
      return this.articles.filter(article => {
        const title = article.title || ''
        const description = article.description || ''
        const source = article.source?.name || ''
        return (
          title.toLowerCase().includes(term) ||
          description.toLowerCase().includes(term) ||
          source.toLowerCase().includes(term)
        )
      })
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
        '/newsapi/v2/everything?q="video games"&language=en&sortBy=publishedAt&pageSize=30&apiKey=a125829a83b64ea99e6889447f348dc8'
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

    <h1 class="mb-2">Live Gaming News</h1>
    <p class="text-muted mb-4">
      Latest gaming news powered by NewsAPI
    </p>

    <!-- Search -->
    <div class="mb-4">
      <input
        v-model="searchTerm"
        type="text"
        class="form-control"
        placeholder="Search live news by title, description or source..."
      >
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading live news...</p>
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="alert alert-danger"
    >
      {{ error }}
    </div>

    <!-- No Results -->
    <div
      v-else-if="filteredArticles.length === 0"
      class="alert alert-warning"
    >
      No articles found matching your search.
    </div>

    <!-- Articles Grid -->
    <div v-else class="row">
      <div
        class="col-md-4 mb-4"
        v-for="article in paginatedArticles"
        :key="article.url"
      >
        <div class="card h-100">

          <img
            v-if="article.urlToImage"
            v-lazy-img="article.urlToImage"
            class="card-img-top"
            :alt="article.title"
            style="height: 200px; object-fit: cover;"
          >
          <div
            v-else
            class="card-img-top bg-secondary d-flex align-items-center justify-content-center"
            style="height: 200px;"
          >
            <span class="text-white">No Image</span>
          </div>

          <div class="card-body text-start">
            <div class="d-flex justify-content-between mb-2">
              <span class="badge bg-primary">
                {{ article.source.name }}
              </span>
              <small class="text-muted">
                {{ formatDate(article.publishedAt) }}
              </small>
            </div>

            <h5 class="card-title">
              {{ article.title }}
            </h5>

            <p class="card-text">
              {{
                article.description
                  ? article.description.slice(0, 120) + '...'
                  : 'No description available.'
              }}
            </p>
          </div>

          <div class="card-footer">
            <a
              :href="article.url"
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn-primary w-100"
            >
              Read More
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
            Previous
          </button>
        </li>

        <li
          v-for="page in totalPages"
          :key="page"
          class="page-item"
          :class="{ active: currentPage === page }"
        >
          <button
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

    <p class="text-center text-muted mt-2">
      Page {{ currentPage }} of {{ totalPages }}
      ({{ filteredArticles.length }} articles)
    </p>

  </div>
</template>