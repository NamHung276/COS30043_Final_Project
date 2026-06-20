// src/views/GameHubNews.vue
<script>
import newsData from '../data/news.json'
import LikeButton from '../components/LikeButton.vue'

export default {
  components: { LikeButton },

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
    },

    getCategoryColor(category) {
      switch(category) {
        case 'FPS':
          return 'bg-danger'
        case 'MOBA':
          return 'bg-success'
        case 'RPG':
          return 'bg-warning text-dark'
        case 'MMO':
          return 'bg-info text-dark'
        default:
          return 'bg-primary'
      }
    }
  }
}
</script>

<template>
  <div class="container py-4">

    <h1 class="mb-4">📰 GameHub News</h1>

    <p class="lead text-muted">
      Discover gaming updates, esports stories,
      game launches, and industry news.
    </p>

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

    <!-- Total Results -->
    <p class="text-muted mb-4">
      Showing {{ filteredNews.length }}
      articles
    </p>

    <!-- News List or Featured Article -->
    <div
      v-if="news.length"
      class="card mb-5 featured-news overflow-hidden"
    >
      <img
        v-lazy-img="news[0].image"
        :alt="news[0].title"
        class="card-img-top"
        style="height:400px;object-fit:cover;"
      >

      <div class="card-body">
        <span class="badge bg-danger mb-2">
          Featured Story
        </span>

        <h2>{{ news[0].title }}</h2>

        <p>
          {{ news[0].content.substring(0, 200) }}...
        </p>

        <router-link
          :to="`/gamehub-news/${news[0].id}`"
          class="btn btn-primary me-2"
        >
          Read Full Story
        </router-link>

        <LikeButton :article-id="news[0].id" />
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
      class="card mb-4 news-card"
    >
      <div class="row g-0">
        <div class="col-md-3">
          <img
            v-lazy-img="item.image"
            :alt="item.title"
            class="img-fluid rounded-start h-100 w-100"
            style="object-fit: cover;"
          >
        </div>
        <div class="col-md-9">
          <div class="card-body text-start">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <span
                class="badge"
                :class="getCategoryColor(item.category)"
              >
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
              {{ item.content.substring(0, 120) }}...</p>
            <router-link
              :to="`/gamehub-news/${item.id}`"
              class="btn btn-outline-primary btn-sm me-2"
            >
              Read More
            </router-link>

            <LikeButton :article-id="item.id" />
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