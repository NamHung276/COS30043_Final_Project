// src/views/GameHubNews.vue
<script>
import newsData from '../data/news.json'
import LikeButton from '../components/LikeButton.vue'
import { auth, db } from '../firebase'
import { onAuthStateChanged } from 'firebase/auth'
import { collection, getDocs } from 'firebase/firestore'

export default {
  components: { LikeButton },

  data() {
    return {
      staticNews: [],     // read-only articles from news.json
      userNews: [],       // user-submitted articles from Firestore
      currentUser: null,
      searchTerm: '',
      selectedCategory: 'All',
      currentPage: 1,
      itemsPerPage: 5,
      loadingUserNews: true
    }
  },

  mounted() {
    onAuthStateChanged(auth, (user) => {
      this.currentUser = user
    })

    this.loadStaticNews()
    this.loadUserNews()
  },

  computed: {
    // Combine both sources into one list for display
    allNews() {
      return [...this.userNews, ...this.staticNews]
    },

    categories() {
      return [
        'All',
        ...new Set(this.allNews.map(item => item.category))
      ]
    },

    filteredNews() {
      const term = this.searchTerm.toLowerCase()
      return this.allNews.filter(item => {
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
    loadStaticNews() {
      const savedNews = localStorage.getItem('gamehubNews')

      if (savedNews) {
        this.staticNews = JSON.parse(savedNews)
      } else {
        this.staticNews = newsData
        localStorage.setItem('gamehubNews', JSON.stringify(newsData))
      }
    },

    async loadUserNews() {
      this.loadingUserNews = true

      try {
        const snapshot = await getDocs(collection(db, 'news'))

        this.userNews = snapshot.docs.map(docSnap => ({
          id: docSnap.id,
          isUserPost: true,
          ...docSnap.data()
        }))
      } catch (error) {
        console.error('Failed to load user news:', error)
      } finally {
        this.loadingUserNews = false
      }
    },

    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        window.scrollTo({ top: 0, behavior: 'smooth' })
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
    },

    // Builds the correct detail link depending on article source
    detailLink(item) {
      return item.isUserPost
        ? `/gamehub-news/user/${item.id}`
        : `/gamehub-news/${item.id}`
    }
  }
}
</script>

<template>
  <div class="container py-4">

    <div class="d-flex justify-content-between align-items-start mb-2 flex-wrap gap-2">
      <div>
        <div class="section-header mb-1">
          <span class="section-icon">📰</span>
          <h1 class="mb-0">GameHub News</h1>
        </div>
      </div>

      <router-link
        to="/gamehub-news/create"
        class="btn btn-primary"
      >
        ✏️ Post Article
      </router-link>
    </div>

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
          placeholder="🔍 Search by title, content, category or date..."
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
    <p class="text-muted mb-4" style="font-size: 0.85rem;">
      Showing {{ filteredNews.length }} articles
    </p>

    <!-- Featured Article -->
    <div
      v-if="allNews.length"
      class="card mb-5 featured-news overflow-hidden"
    >
      <div style="position: relative;">
        <img
          v-lazy-img="allNews[0].image"
          :alt="allNews[0].title"
          class="card-img-top"
          style="height:400px;object-fit:cover;"
        >
        <div
          style="position: absolute; bottom: 0; left: 0; right: 0; padding: 32px; background: linear-gradient(transparent, rgba(7,11,20,0.9));"
        >
          <div class="d-flex gap-2 mb-2 flex-wrap">
            <span class="badge" style="background: var(--danger);">
              ⚡ Featured Story
            </span>
            <span
              v-if="allNews[0].isUserPost"
              class="badge bg-secondary"
            >
              👤 Community Post
            </span>
          </div>

          <h2 class="mb-2" style="text-shadow: 0 2px 8px rgba(0,0,0,0.5);">
            {{ allNews[0].title }}
          </h2>

          <p class="mb-3 text-muted" style="max-width: 600px;">
            {{ allNews[0].content.substring(0, 200) }}...
          </p>

          <div class="d-flex align-items-center gap-2 flex-wrap">
            <router-link
              :to="detailLink(allNews[0])"
              class="btn btn-primary"
            >
              Read Full Story →
            </router-link>

            <LikeButton :article-id="allNews[0].id" />
          </div>
        </div>
      </div>
    </div>

    <!-- No Results -->
    <div
      v-if="filteredNews.length === 0"
      class="empty-state"
    >
      <div class="empty-state-icon">📰</div>
      <h3>No news found</h3>
      <p>Try adjusting your search or category filter.</p>
    </div>

    <!-- News List -->
    <div
      v-for="(item, index) in paginatedNews"
      :key="item.id"
      class="card mb-4 news-card stagger-item"
      :style="{ animationDelay: `${index * 0.06}s` }"
    >
      <div class="row g-0">
        <div class="col-md-3">
          <img
            v-lazy-img="item.image"
            :alt="item.title"
            class="img-fluid rounded-start h-100 w-100"
            style="object-fit: cover; min-height: 180px;"
          >
        </div>
        <div class="col-md-9">
          <div class="card-body text-start">
            <div class="d-flex justify-content-between align-items-start mb-2">
              <div class="d-flex gap-2 flex-wrap">
                <span
                  class="badge"
                  :class="getCategoryColor(item.category)"
                >
                  {{ item.category }}
                </span>
                <span
                  v-if="item.isUserPost"
                  class="badge bg-secondary"
                >
                  👤 Community
                </span>
              </div>
              <small class="text-muted">
                {{ item.date }}
              </small>
            </div>
            <h5 class="card-title">
              {{ item.title }}
            </h5>
            <p class="card-text text-muted" style="font-size: 0.9rem;">
              {{ item.content.substring(0, 120) }}...
            </p>

            <div class="d-flex align-items-center gap-2 flex-wrap">
              <router-link
                :to="detailLink(item)"
                class="btn btn-outline-primary btn-sm"
              >
                Read More →
              </router-link>

              <LikeButton :article-id="item.id" />
            </div>
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
            Next →
          </button>
        </li>

      </ul>
    </nav>

    <!-- Page Info -->
    <p class="text-center text-muted mt-2" style="font-size: 0.85rem;">
      Page {{ currentPage }} of {{ totalPages }}
      · {{ filteredNews.length }} articles
    </p>

  </div>
</template>