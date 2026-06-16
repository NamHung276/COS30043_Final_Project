<script>
import newsData from '../data/news.json'

export default {
  data() {
    return {
      news: [],
      searchTerm: '',
      selectedCategory: 'All',
      currentPage: 1,
      itemsPerPage: 5
    }
  },

  mounted() {

    const savedNews =
      localStorage.getItem('gamehubNews')

    if (savedNews) {

      this.news =
        JSON.parse(savedNews)

    }
    else {

      this.news = newsData

      localStorage.setItem(
        'gamehubNews',
        JSON.stringify(newsData)
      )
    }
  },

  computed: {
    categories() {
      return [
        'All',
        ...new Set(this.news.map(item => item.category))
      ]
    },

    filteredNews() {
      const term = this.searchTerm.toLowerCase()
      return this.news.filter(item => {
        const matchesSearch =
          item.title.toLowerCase().includes(term) ||
          item.content.toLowerCase().includes(term) ||
          item.category.toLowerCase().includes(term) ||
          item.date.includes(term)

        const matchesCategory =
          this.selectedCategory === 'All' ||
          item.category === this.selectedCategory

        return matchesSearch && matchesCategory
      })
    },

    totalPages() {
      return Math.ceil(
        this.filteredNews.length / this.itemsPerPage
      )
    },

    paginatedNews() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      const end = start + this.itemsPerPage
      return this.filteredNews.slice(start, end)
    }
  },

  watch: {
    searchTerm() {
      this.currentPage = 1
    },
    selectedCategory() {
      this.currentPage = 1
    }
  },

  methods: {
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
      }
    }
  }
}
</script>

<template>
  <div class="container py-4">

    <h1 class="mb-4">Gaming News</h1>

    <!-- Search and Filter -->
    <div class="row mb-4 g-3">
      <div class="col-md-8">
        <input
          v-model="searchTerm"
          type="text"
          class="form-control"
          placeholder="Search by title, content, category or date..."
        >
      </div>
      <div class="col-md-4">
        <select
          v-model="selectedCategory"
          class="form-select"
        >
          <option
            v-for="category in categories"
            :key="category"
            :value="category"
          >
            {{ category }}
          </option>
        </select>
      </div>
    </div>

    <!-- No Results -->
    <div
      v-if="filteredNews.length === 0"
      class="alert alert-warning"
    >
      No news found matching your search.
    </div>

    <!-- News List -->
    <div
      v-for="item in paginatedNews"
      :key="item.id"
      class="card mb-4"
    >
      <div class="row g-0">
        <div class="col-md-3">
          <img
            :src="item.image"
            :alt="item.title"
            class="img-fluid rounded-start h-100 w-100"
            style="object-fit: cover;"
          >
        </div>
        <div class="col-md-9">
          <div class="card-body text-start">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <span class="badge bg-primary">
                {{ item.category }}
              </span>
              <small class="text-muted">
                {{ item.date }}
              </small>
            </div>
            <h5 class="card-title">
              {{ item.title }}
            </h5>
            <p class="card-text">
              {{ item.content }}
            </p>
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

    <!-- Page Info -->
    <p class="text-center text-muted mt-2">
      Page {{ currentPage }} of {{ totalPages }}
      ({{ filteredNews.length }} articles)
    </p>

  </div>
</template>