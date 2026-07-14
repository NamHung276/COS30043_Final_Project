<script>
import SkeletonCard from '../components/SkeletonCard.vue'
import { newsApi } from '../services/api'

export default {
  components: { SkeletonCard },

  data() {
    return {
      articles: [],
      loading: true,
      error: null,
      searchTerm: '',
      currentPage: 1,
      itemsPerPage: 12,
      sortOption: 'newest',
      selectedCategory: '',
      selectedSource: '',
      lastUpdated: '',
      expandedCategory: null,
      // Recent & More News pagination
      recentPage: 1,
      recentPerPage: 8
    }
  },

  computed: {
    // Top stories (newest, with image, from trusted sources)
    topStories() {
      return this.articles
        .filter(a => a.urlToImage && a.description && a.description.length > 50)
        .slice(0, 6)
    },

    // Popular/trending stories (most recent from various sources)
    trendingStories() {
      return this.articles
        .filter(a => a.urlToImage && !this.topStories.includes(a))
        .slice(0, 12)
    },

    // All unique categories with better detection
    categories() {
      const cats = new Set()
      this.articles.forEach(a => {
        const title = a.title.toLowerCase()
        const desc = (a.description || '').toLowerCase()
        const combined = title + ' ' + desc
        
        if (combined.includes('esport') || combined.includes('tournament') || combined.includes('competition') || combined.includes('rank') || combined.includes('league')) cats.add('Esports')
        if (combined.includes('release') || combined.includes('launch') || combined.includes('new game') || combined.includes('available')) cats.add('Releases')
        if (combined.includes('developer') || combined.includes('studio') || combined.includes('publisher') || combined.includes('company')) cats.add('Industry')
        if (combined.includes('review') || combined.includes('gameplay') || combined.includes('rating')) cats.add('Reviews')
        if (combined.includes('playstation') || combined.includes('xbox') || combined.includes('switch') || combined.includes('pc gaming') || combined.includes('console')) cats.add('Platforms')
        if (combined.includes('update') || combined.includes('patch') || combined.includes('bug fix')) cats.add('Updates')
        if (combined.includes('graphic') || combined.includes('technology') || combined.includes('fps') || combined.includes('ray tracing') || combined.includes('engine')) cats.add('Tech')
      })
      return Array.from(cats).sort()
    },

    // Articles by category with better filtering
    articlesByCategory() {
      const result = {}
      this.categories.forEach(cat => {
        result[cat] = this.articles.filter(a => {
          const title = a.title.toLowerCase()
          const desc = (a.description || '').toLowerCase()
          const combined = title + ' ' + desc
          
          if (cat === 'Esports') return combined.includes('esport') || combined.includes('tournament') || combined.includes('competition') || combined.includes('rank') || combined.includes('league')
          if (cat === 'Releases') return combined.includes('release') || combined.includes('launch') || combined.includes('new game') || combined.includes('available')
          if (cat === 'Industry') return combined.includes('developer') || combined.includes('studio') || combined.includes('publisher') || combined.includes('company')
          if (cat === 'Reviews') return combined.includes('review') || combined.includes('gameplay') || combined.includes('rating')
          if (cat === 'Platforms') return combined.includes('playstation') || combined.includes('xbox') || combined.includes('switch') || combined.includes('pc gaming') || combined.includes('console')
          if (cat === 'Updates') return combined.includes('update') || combined.includes('patch') || combined.includes('bug fix')
          if (cat === 'Tech') return combined.includes('graphic') || combined.includes('technology') || combined.includes('fps') || combined.includes('ray tracing') || combined.includes('engine')
          return false
        })
      })
      return result
    },

    // Uncategorized articles
    uncategorizedArticles() {
      const categorizedSet = new Set()
      Object.values(this.articlesByCategory).forEach(cats => {
        cats.forEach(a => categorizedSet.add(a.url))
      })
      return this.articles.filter(a => !categorizedSet.has(a.url))
    },

    // Filtered articles for search
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
        filtered = filtered.filter(a => a.source?.name === this.selectedSource)
      }
      if (this.sortOption === 'newest') {
        filtered.sort((a, b) => new Date(b.publishedAt) - new Date(a.publishedAt))
      } else if (this.sortOption === 'oldest') {
        filtered.sort((a, b) => new Date(a.publishedAt) - new Date(b.publishedAt))
      }
      return filtered
    },

    availableSources() {
      return [...new Set(this.articles.map(a => a.source?.name))].filter(Boolean).sort()
    },

    totalPages() {
      return Math.ceil(this.filteredArticles.length / this.itemsPerPage)
    },

    paginatedArticles() {
      const start = (this.currentPage - 1) * this.itemsPerPage
      return this.filteredArticles.slice(start, start + this.itemsPerPage)
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

    // ── Recent & More News pagination ────────────────
    recentTotalPages() {
      return Math.max(1, Math.ceil(this.uncategorizedArticles.length / this.recentPerPage))
    },
    paginatedRecentArticles() {
      const start = (this.recentPage - 1) * this.recentPerPage
      return this.uncategorizedArticles.slice(start, start + this.recentPerPage)
    },
    recentVisiblePages() {
      const total = this.recentTotalPages
      const cur = this.recentPage
      const pages = []
      if (total <= 7) {
        for (let i = 1; i <= total; i++) pages.push(i)
      } else {
        pages.push(1)
        if (cur > 4) pages.push('...')
        const s = Math.max(2, cur - 1)
        const e = Math.min(total - 1, cur + 1)
        for (let i = s; i <= e; i++) pages.push(i)
        if (cur < total - 3) pages.push('...')
        pages.push(total)
      }
      return pages
    },
    recentStartItem() {
      return this.uncategorizedArticles.length === 0 ? 0 : (this.recentPage - 1) * this.recentPerPage + 1
    },
    recentEndItem() {
      return Math.min(this.recentPage * this.recentPerPage, this.uncategorizedArticles.length)
    }
  },

  watch: {
    searchTerm() { this.currentPage = 1 },
    selectedSource() { this.currentPage = 1 },
    recentPerPage() { this.recentPage = 1 }
  },

  methods: {
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page
        window.scrollTo({ top: 0, behavior: 'smooth' })
      }
    },
    goToRecentPage(page) {
      if (page >= 1 && page <= this.recentTotalPages) {
        this.recentPage = page
        this.$nextTick(() => {
          const el = document.getElementById('recent-news-section')
          if (el) {
            const offset = el.getBoundingClientRect().top + window.scrollY - 80
            window.scrollTo({ top: offset, behavior: 'smooth' })
          }
        })
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return ''
      return new Date(dateStr).toLocaleDateString('en-AU', {
        year: 'numeric', month: 'short', day: 'numeric'
      })
    },
    timeAgo(dateStr) {
      if (!dateStr) return ''
      const diff = Date.now() - new Date(dateStr).getTime()
      const h = Math.floor(diff / 3600000)
      if (h < 1) return 'Just now'
      if (h < 24) return `${h}h ago`
      const d = Math.floor(h / 24)
      return `${d}d ago`
    },
    getCategoryIcon(category) {
      const icons = {
        'Esports': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="6 5 18 12 6 19 6 5"/></svg>',
        'Releases': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9"/><polyline points="12 7 12 12 16 14"/></svg>',
        'Industry': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
        'Reviews': '<svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>',
        'Platforms': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2"/><line x1="2" y1="20" x2="22" y2="20"/></svg>',
        'Updates': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 4 23 10 17 10"/><polyline points="1 20 1 14 7 14"/><path d="M3.51 9a9 9 0 0 1 14.85-3.36M20.49 15a9 9 0 0 1-14.85 3.36"/></svg>',
        'Tech': '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>'
      }
      return icons[category] || '<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3H7a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V9"/><polyline points="9 12 11 14 15 10"/></svg>'
    },
    toggleCategory(category) {
      this.expandedCategory = this.expandedCategory === category ? null : category
    }
  },

  async mounted() {
    try {
      const { data } = await newsApi.get('/everything', {
        params: { q: 'gaming OR "video games"', language: 'en', sortBy: 'publishedAt', pageSize: 100 }
      })
      if (data.status === 'error') { this.error = data.message; return }
      this.articles = (data.articles || []).filter(
        a => a.title !== '[Removed]' && a.description !== null
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
  <div class="ln-page">
    <!-- ══ Header ══ -->
    <div class="ln-page-header">
      <div class="ln-header-bg" aria-hidden="true"></div>
      <div class="container ln-header-content">
        <div class="ln-title-row">
          <span class="ln-title-icon" aria-hidden="true">
            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12.55a11 11 0 0114.08 0M1.42 9a16 16 0 0121.16 0M8.53 16.11a6 6 0 016.95 0M12 20h.01"/></svg>
          </span>
          <div>
            <h1 class="ln-title">Live Gaming News</h1>
            <div class="ln-meta-row">
              <span class="ln-last-updated">Updated {{ lastUpdated }}</span>
              <span v-if="!loading" class="ln-count-badge">{{ articles.length }} articles</span>
            </div>
            <p class="ln-subtitle">
              Breaking stories, trending topics &amp; hot gaming news
              <span class="ln-powered">· Powered by NewsAPI</span>
            </p>
          </div>
        </div>

        <!-- Search & Filter Bar -->
        <div class="ln-filter-panel">
          <div class="ln-search-wrap">
            <img src="/logo/search.svg" class="ln-search-icon" width="16" height="16" alt="" aria-hidden="true">
            <input v-model="searchTerm" type="text" class="ln-search-input" placeholder="Search news, sources…" aria-label="Search live gaming news">
          </div>
          <div class="ln-filter-controls">
            <select v-model="sortOption" class="ln-select" aria-label="Sort news">
              <option value="newest">Newest</option>
              <option value="oldest">Oldest</option>
            </select>
            <select v-model="selectedSource" class="ln-select" aria-label="Filter by source">
              <option value="">All Sources</option>
              <option v-for="src in availableSources" :key="src" :value="src">{{ src }}</option>
            </select>
          </div>
        </div>
      </div>
    </div>

    <!-- ══ Content ══ -->
    <div class="container ln-content">
      <!-- Skeleton Loading -->
      <div v-if="loading" class="ln-skeleton-wrapper">
        <SkeletonCard v-for="n in 12" :key="n" />
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="ln-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
        <h3>Couldn't load news</h3>
        <p>{{ error }}</p>
      </div>

      <!-- Main Content -->
      <template v-else>
        <!-- TOP STORIES SECTION -->
        <section v-if="topStories.length" class="ln-section">
          <div class="ln-section-header">
            <h2 class="ln-section-title">
              <span class="ln-section-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zm9 7h-6v13c0 .55-.45 1-1 1s-1-.45-1-1v-3H9v3c0 .55-.45 1-1 1s-1-.45-1-1V9H1c-.55 0-1-.45-1-1s.45-1 1-1h6V4c0-.55.45-1 1-1s1 .45 1 1v3h6V4c0-.55.45-1 1-1s1 .45 1 1v3h6c.55 0 1 .45 1 1s-.45 1-1 1z"/></svg></span> Top Stories
            </h2>
            <span class="ln-section-count">{{ topStories.length }} stories</span>
          </div>
          <div class="ln-top-grid">
            <!-- Featured Main Card -->
            <a
              v-if="topStories[0]"
              :href="topStories[0].url"
              target="_blank"
              rel="noopener noreferrer"
              class="ln-featured-card"
              :aria-label="`Read: ${topStories[0].title}`"
            >
              <div class="ln-featured-img-wrap">
                <img
                  v-if="topStories[0].urlToImage"
                  v-lazy-img="topStories[0].urlToImage"
                  :alt="topStories[0].title"
                  class="ln-featured-img"
                >
                <div v-else class="ln-featured-img-placeholder">
                  <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 22h16a2 2 0 002-2V4a2 2 0 00-2-2H8L2 8v12a2 2 0 002 2z"/><path d="M8 2v6H2"/></svg>
                </div>
                <div class="ln-featured-overlay"></div>
                <span class="ln-featured-badge">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor"><polygon points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"/></svg>
                  Breaking
                </span>
              </div>
              <div class="ln-featured-body">
                <div class="ln-featured-meta">
                  <span class="ln-featured-source">{{ topStories[0].source?.name }}</span>
                  <span class="ln-featured-time">{{ timeAgo(topStories[0].publishedAt) }}</span>
                </div>
                <h3 class="ln-featured-title">{{ topStories[0].title }}</h3>
                <p class="ln-featured-desc">{{ topStories[0].description?.slice(0, 150) }}…</p>
              </div>
            </a>

            <!-- Side Cards -->
            <div class="ln-top-side">
              <a
                v-for="(article, idx) in topStories.slice(1, 4)"
                :key="article.url"
                :href="article.url"
                target="_blank"
                rel="noopener noreferrer"
                class="ln-side-card"
                :aria-label="`Read: ${article.title}`"
              >
                <div class="ln-side-card-img">
                  <img
                    v-if="article.urlToImage"
                    v-lazy-img="article.urlToImage"
                    :alt="article.title"
                    class="ln-side-img"
                  >
                  <div v-else class="ln-side-img-placeholder">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 22h16a2 2 0 002-2V4a2 2 0 00-2-2H8L2 8v12a2 2 0 002 2z"/></svg>
                  </div>
                </div>
                <div class="ln-side-card-body">
                  <div class="ln-side-meta">
                    <span class="ln-side-source">{{ article.source?.name }}</span>
                  </div>
                  <h4 class="ln-side-title">{{ article.title }}</h4>
                  <span class="ln-side-time">{{ timeAgo(article.publishedAt) }}</span>
                </div>
              </a>
            </div>
          </div>
        </section>

        <!-- SEARCH/FILTER RESULTS -->
        <section v-if="searchTerm || selectedSource" class="ln-section">
          <div class="ln-section-header">
            <h2 class="ln-section-title">
              <span v-if="searchTerm" class="ln-section-subtitle">Search Results for "{{ searchTerm }}"</span>
              <span v-else class="ln-section-subtitle">From {{ selectedSource }}</span>
            </h2>
            <span class="ln-section-count">{{ filteredArticles.length }} results</span>
          </div>
          <div class="ln-search-grid">
            <a
              v-for="(article, idx) in paginatedArticles"
              :key="article.url"
              :href="article.url"
              target="_blank"
              rel="noopener noreferrer"
              class="ln-card stagger-item"
              :style="{ animationDelay: `${(idx % 12) * 0.03}s` }"
              :aria-label="`Read: ${article.title}`"
            >
              <div class="ln-card-img-wrap">
                <img
                  v-if="article.urlToImage"
                  v-lazy-img="article.urlToImage"
                  class="ln-card-img"
                  :alt="article.title"
                >
                <div v-else class="ln-card-img-placeholder"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 22h16a2 2 0 002-2V4a2 2 0 00-2-2H8L2 8v12a2 2 0 002 2z"/></svg></div>
                <div class="ln-card-img-overlay"></div>
                <span class="ln-source-badge">{{ article.source?.name }}</span>
              </div>
              <div class="ln-card-body">
                <div class="ln-card-meta">
                  <span class="ln-card-date">{{ formatDate(article.publishedAt) }}</span>
                  <span class="ln-card-time-ago">{{ timeAgo(article.publishedAt) }}</span>
                </div>
                <h3 class="ln-card-title">{{ article.title }}</h3>
                <p class="ln-card-desc">{{ article.description?.slice(0, 110) }}…</p>
                <div class="ln-card-cta">
                  Read More
                  <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                </div>
              </div>
            </a>
          </div>

          <!-- Search Pagination -->
          <nav v-if="totalPages > 1" class="ln-pagination" aria-label="News pagination">
            <button class="ln-page-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
              <img src="/logo/arrow-left.svg" width="15" height="15" alt="" aria-hidden="true">
              Previous
            </button>
            <div class="ln-page-numbers">
              <template v-for="(page, i) in visiblePages" :key="i">
                <span v-if="page === '...'" class="ln-page-ellipsis">&#8230;</span>
                <button v-else class="ln-page-num" :class="{ active: currentPage === page }" @click="goToPage(page)">{{ page }}</button>
              </template>
            </div>
            <button class="ln-page-btn" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">
              Next
              <img src="/logo/arrow-right.svg" width="15" height="15" alt="" aria-hidden="true">
            </button>
          </nav>
        </section>

        <!-- TRENDING STORIES SECTION -->
        <section v-if="!searchTerm && !selectedSource && trendingStories.length" class="ln-section">
          <div class="ln-section-header">
            <h2 class="ln-section-title">
              <span class="ln-section-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor"><path d="M13 2L3 14h8l-1 8 10-12h-8l1-8z"/></svg></span> Trending Now
            </h2>
            <span class="ln-section-count">{{ trendingStories.length }} stories</span>
          </div>
          <div class="ln-trending-list">
            <a
              v-for="(article, idx) in trendingStories.slice(0, 8)"
              :key="article.url"
              :href="article.url"
              target="_blank"
              rel="noopener noreferrer"
              class="ln-trending-item stagger-item"
              :style="{ animationDelay: `${idx * 0.04}s` }"
              :aria-label="`Read: ${article.title}`"
            >
              <div class="ln-trending-num">{{ idx + 1 }}</div>
              <div class="ln-trending-body">
                <h4 class="ln-trending-title">{{ article.title }}</h4>
                <div class="ln-trending-meta">
                  <span class="ln-trending-source">{{ article.source?.name }}</span>
                  <span class="ln-trending-time">{{ timeAgo(article.publishedAt) }}</span>
                </div>
              </div>
              <svg class="ln-trending-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            </a>
          </div>
        </section>

        <!-- CATEGORY SECTIONS -->
        <section v-if="!searchTerm && !selectedSource && categories.length" class="ln-section">
          <div class="ln-section-header">
            <h2 class="ln-section-title">
              <span class="ln-section-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg></span> Browse by Category
            </h2>
          </div>
          <div class="ln-categories-grid">
            <button
              v-for="cat in categories"
              :key="cat"
              class="ln-category-btn"
              :class="{ expanded: expandedCategory === cat }"
              @click="toggleCategory(cat)"
              :aria-label="`${expandedCategory === cat ? 'Collapse' : 'Expand'} ${cat} stories`"
            >
              <span class="ln-cat-emoji" v-html="getCategoryIcon(cat)"></span>
              <span class="ln-cat-name">{{ cat }}</span>
              <span class="ln-cat-count">{{ articlesByCategory[cat]?.length || 0 }}</span>
              <svg class="ln-cat-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
          </div>

          <!-- Expanded Category Content -->
          <div v-if="expandedCategory && articlesByCategory[expandedCategory]" class="ln-category-expanded">
            <div class="ln-category-title">{{ expandedCategory }} Stories ({{ articlesByCategory[expandedCategory].length }})</div>
            <div class="ln-category-cards">
              <a
                v-for="(article, idx) in articlesByCategory[expandedCategory]"
                :key="article.url"
                :href="article.url"
                target="_blank"
                rel="noopener noreferrer"
                class="ln-card stagger-item"
                :style="{ animationDelay: `${(idx % 24) * 0.02}s` }"
                :aria-label="`Read: ${article.title}`"
              >
                <div class="ln-card-img-wrap">
                  <img
                    v-if="article.urlToImage"
                    v-lazy-img="article.urlToImage"
                    class="ln-card-img"
                    :alt="article.title"
                  >
                  <div v-else class="ln-card-img-placeholder"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 22h16a2 2 0 002-2V4a2 2 0 00-2-2H8L2 8v12a2 2 0 002 2z"/></svg></div>
                  <div class="ln-card-img-overlay"></div>
                  <span class="ln-source-badge">{{ article.source?.name }}</span>
                </div>
                <div class="ln-card-body">
                  <div class="ln-card-meta">
                    <span class="ln-card-date">{{ formatDate(article.publishedAt) }}</span>
                    <span class="ln-card-time-ago">{{ timeAgo(article.publishedAt) }}</span>
                  </div>
                  <h3 class="ln-card-title">{{ article.title }}</h3>
                  <p class="ln-card-desc">{{ article.description?.slice(0, 110) }}…</p>
                </div>
              </a>
            </div>
          </div>
        </section>

        <!-- RECENT NEWS SECTION (Uncategorized, paginated) -->
        <section
          v-if="!searchTerm && !selectedSource && uncategorizedArticles.length"
          id="recent-news-section"
          class="ln-section"
        >
          <!-- Section header with per-page control -->
          <div class="ln-section-header ln-recent-header">
            <h2 class="ln-section-title">
              <span class="ln-section-icon"><svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2z"/><line x1="4" y1="9" x2="20" y2="9"/><line x1="4" y1="14" x2="12" y2="14"/></svg></span>
              Recent &amp; More News
            </h2>
            <div class="ln-recent-controls">
              <span class="ln-section-count">{{ uncategorizedArticles.length }} articles</span>
              <!-- Per-page selector -->
              <div class="ln-perpage-wrap">
                <label class="ln-perpage-label">Show</label>
                <select v-model.number="recentPerPage" class="ln-perpage-select" aria-label="Articles per page">
                  <option :value="4">4</option>
                  <option :value="6">6</option>
                  <option :value="8">8</option>
                </select>
                <label class="ln-perpage-label">per page</label>
              </div>
            </div>
          </div>

          <!-- Page info -->
          <div class="ln-page-info ln-recent-info">
            Page {{ recentPage }} of {{ recentTotalPages }}
            &nbsp;·&nbsp;
            Showing {{ recentStartItem }}–{{ recentEndItem }} of {{ uncategorizedArticles.length }} articles
          </div>

          <!-- Paginated grid with fade transition -->
          <Transition name="page-fade" mode="out-in">
            <div :key="recentPage" class="ln-search-grid">
              <a
                v-for="(article, idx) in paginatedRecentArticles"
                :key="article.url"
                :href="article.url"
                target="_blank"
                rel="noopener noreferrer"
                class="ln-card stagger-item"
                :style="{ animationDelay: `${idx * 0.05}s` }"
                :aria-label="`Read: ${article.title}`"
              >
                <div class="ln-card-img-wrap">
                  <img
                    v-if="article.urlToImage"
                    v-lazy-img="article.urlToImage"
                    class="ln-card-img"
                    :alt="article.title"
                  >
                  <div v-else class="ln-card-img-placeholder"><svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M4 22h16a2 2 0 002-2V4a2 2 0 00-2-2H8L2 8v12a2 2 0 002 2z"/></svg></div>
                  <div class="ln-card-img-overlay"></div>
                  <span class="ln-source-badge">{{ article.source?.name }}</span>
                </div>
                <div class="ln-card-body">
                  <div class="ln-card-meta">
                    <span class="ln-card-date">{{ formatDate(article.publishedAt) }}</span>
                    <span class="ln-card-time-ago">{{ timeAgo(article.publishedAt) }}</span>
                  </div>
                  <h3 class="ln-card-title">{{ article.title }}</h3>
                  <p class="ln-card-desc">{{ article.description?.slice(0, 110) }}…</p>
                  <div class="ln-card-cta">
                    Read More
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
                  </div>
                </div>
              </a>
            </div>
          </Transition>

          <!-- Pagination nav -->
          <nav v-if="recentTotalPages > 1" class="ln-pagination" aria-label="Recent news pagination">
            <button
              class="ln-page-btn"
              :disabled="recentPage === 1"
              @click="goToRecentPage(recentPage - 1)"
            >
              <i class="bi bi-chevron-left" style="font-size:0.85rem;"></i>
              Previous
            </button>
            <div class="ln-page-numbers">
              <template v-for="(page, i) in recentVisiblePages" :key="i">
                <span v-if="page === '...'" class="ln-page-ellipsis">&#8230;</span>
                <button
                  v-else
                  class="ln-page-num"
                  :class="{ active: recentPage === page }"
                  :aria-label="`Go to page ${page}`"
                  :aria-current="recentPage === page ? 'page' : undefined"
                  @click="goToRecentPage(page)"
                >{{ page }}</button>
              </template>
            </div>
            <button
              class="ln-page-btn"
              :disabled="recentPage === recentTotalPages"
              @click="goToRecentPage(recentPage + 1)"
            >
              Next
              <i class="bi bi-chevron-right" style="font-size:0.85rem;"></i>
            </button>
          </nav>
        </section>
      </template>
    </div>
  </div>
</template>

<style scoped>
/* ── Page ─────────────────────────────────────────── */
.ln-page { min-height: 100vh; background: var(--bg-deep); }

/* ── Header ───────────────────────────────────────── */
.ln-page-header {
  position: relative; background: var(--bg-base);
  border-bottom: 1px solid var(--border-glass); overflow: hidden;
}
.ln-header-bg {
  position: absolute; inset: 0;
  background:
    radial-gradient(ellipse 65% 120% at 90% 50%, rgba(6,182,212,0.07) 0%, transparent 60%),
    radial-gradient(ellipse 50% 80% at 10% 80%, rgba(124,58,237,0.06) 0%, transparent 60%);
  pointer-events: none;
}
.ln-header-content { position: relative; z-index: 1; padding-top: 40px; padding-bottom: 0; }

/* Title */
.ln-title-row { display: flex; align-items: flex-start; gap: 18px; margin-bottom: 20px; }
.ln-title-icon {
  display: flex; align-items: center; justify-content: center;
  width: 54px; height: 54px; border-radius: 16px; flex-shrink: 0; margin-top: 2px;
  background: linear-gradient(135deg, #0e7490, #06b6d4);
  color: #fff; box-shadow: 0 4px 20px rgba(6,182,212,0.4);
}
.ln-title { font-size: 2.1rem; font-weight: 800; color: var(--text-primary) !important; margin: 0 0 4px; line-height: 1; }
.ln-meta-row { display: flex; align-items: center; gap: 10px; margin-bottom: 4px; }
.ln-last-updated { font-size: 0.78rem; color: #4a5580 !important; }
.ln-count-badge { font-size: 0.7rem; font-weight: 700; padding: 2px 10px; border-radius: 20px; background: var(--gradient-primary); color: #fff !important; }
.ln-subtitle { font-size: 0.85rem; color: #8b9cc8 !important; margin: 0; }
.ln-powered { opacity: 0.55; }

/* Filter panel */
.ln-filter-panel {
  background: rgba(15,23,42,0.6); border: 1px solid var(--border-glass); border-bottom: none;
  border-radius: 14px 14px 0 0; padding: 18px 24px;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}
.ln-filter-row { display: flex; align-items: center; gap: 12px; flex-wrap: wrap; }
.ln-search-wrap { flex: 1; min-width: 200px; position: relative; }
.ln-search-icon { position: absolute; left: 13px; top: 50%; transform: translateY(-50%); pointer-events: none; opacity: 0.6; }
.ln-search-input {
  width: 100%; background: rgba(15,23,42,0.7); border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm); color: var(--text-primary) !important; padding: 10px 14px 10px 38px;
  font-size: 0.88rem; font-family: var(--font-family); outline: none; transition: border-color 0.2s;
}
.ln-search-input::placeholder { color: #4a5580; }
.ln-search-input:focus { border-color: #06b6d4; }
.ln-select {
  background: rgba(15,23,42,0.7); border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm); color: var(--text-primary) !important; padding: 9px 14px;
  font-size: 0.88rem; font-family: var(--font-family); outline: none; cursor: pointer; min-width: 140px;
}
.ln-select:focus { border-color: #06b6d4; }

/* Summary row */
.ln-summary-row {
  display: flex; align-items: center; justify-content: space-between; padding: 10px 24px;
  background: rgba(15,23,42,0.4); border: 1px solid var(--border-glass); border-top: none;
}
.ln-summary-text { font-size: 0.78rem; color: #4a5580 !important; font-style: italic; }
.ln-results-badge {
  font-size: 0.72rem; font-weight: 700; padding: 3px 12px; border-radius: 20px;
  background: linear-gradient(135deg, #0e7490, #06b6d4); color: #fff !important;
}

/* ── Content ──────────────────────────────────────── */
.ln-content { padding-top: 24px; padding-bottom: 60px; }

/* ── Skeleton Wrapper ─────────────────────────────── */
.ln-skeleton-wrapper { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 18px; }

/* ── Section ──────────────────────────────────────── */
.ln-section { margin-bottom: 52px; }
.ln-section-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 20px; padding-bottom: 12px; border-bottom: 2px solid rgba(6,182,212,0.2);
}
.ln-section-title {
  font-size: 1.6rem; font-weight: 800; color: var(--text-primary) !important; margin: 0;
  display: flex; align-items: center; gap: 10px;
}
.ln-section-subtitle { font-size: 1rem; font-weight: 600; }
.ln-section-icon { display: inline-flex; align-items: center; justify-content: center; width: 32px; height: 32px; color: #06b6d4; }
.ln-section-icon svg { width: 28px; height: 28px; stroke-width: 2; }
.ln-section-count {
  font-size: 0.8rem; padding: 4px 12px; border-radius: 20px;
  background: rgba(6,182,212,0.15); color: #67e8f9 !important;
  font-weight: 600;
}

/* ── TOP STORIES ──────────────────────────────────── */
.ln-top-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 20px;
  @media (max-width: 900px) { grid-template-columns: 1fr; }
}

/* Featured Card */
.ln-featured-card {
  display: flex; flex-direction: column; text-decoration: none;
  border-radius: 16px; overflow: hidden;
  background: rgba(15,23,42,0.55); border: 1px solid rgba(255,255,255,0.07);
  transition: transform 0.3s ease, box-shadow 0.3s ease, border-color 0.3s ease;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}
.ln-featured-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 60px rgba(6,182,212,0.2), 0 4px 24px rgba(0,0,0,0.5);
  border-color: rgba(6,182,212,0.3);
}

.ln-featured-img-wrap {
  position: relative; overflow: hidden; height: 280px; flex-shrink: 0;
}
.ln-featured-img {
  width: 100%; height: 100%; object-fit: cover; display: block;
  transition: transform 0.4s ease;
}
.ln-featured-card:hover .ln-featured-img { transform: scale(1.05); }
.ln-featured-img-placeholder {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
  background: rgba(15,23,42,0.8); color: rgba(255,255,255,0.2);
}
.ln-featured-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(10,15,30,0.7) 0%, transparent 60%);
  pointer-events: none;
}
.ln-featured-badge {
  position: absolute; top: 12px; left: 12px;
  display: inline-flex; align-items: center; gap: 5px;
  background: #ef4444; color: #fff !important; font-size: 0.7rem; font-weight: 800;
  padding: 5px 12px; border-radius: 20px; letter-spacing: 0.5px;
  box-shadow: 0 4px 12px rgba(239,68,68,0.5);
  text-transform: uppercase;
}

.ln-featured-body { padding: 20px; display: flex; flex-direction: column; flex: 1; gap: 10px; }
.ln-featured-meta {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.ln-featured-source {
  font-size: 0.75rem; font-weight: 700; color: #67e8f9 !important; text-transform: uppercase;
  letter-spacing: 0.3px;
}
.ln-featured-time {
  font-size: 0.74rem; color: #4a5580 !important;
}
.ln-featured-title {
  font-size: 1.32rem; font-weight: 800; color: var(--text-primary) !important; margin: 0;
  line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}
.ln-featured-desc {
  font-size: 0.87rem; color: #8b9cc8 !important; line-height: 1.6; margin: 0;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
}

/* Side Cards */
.ln-top-side {
  display: flex; flex-direction: column; gap: 14px;
}
.ln-side-card {
  display: flex; gap: 14px; text-decoration: none;
  padding: 12px; border-radius: 12px; transition: all 0.2s;
  background: rgba(15,23,42,0.4); border: 1px solid rgba(255,255,255,0.05);
}
.ln-side-card:hover {
  background: rgba(15,23,42,0.6); border-color: rgba(6,182,212,0.2);
  transform: translateX(4px);
}
.ln-side-card-img {
  width: 100px; height: 80px; flex-shrink: 0; border-radius: 8px; overflow: hidden;
  background: rgba(15,23,42,0.8);
}
.ln-side-img {
  width: 100%; height: 100%; object-fit: cover; display: block;
}
.ln-side-img-placeholder {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
  color: rgba(255,255,255,0.2);
}
.ln-side-card-body { flex: 1; display: flex; flex-direction: column; justify-content: space-between; }
.ln-side-meta {
  display: flex; align-items: center; gap: 6px;
}
.ln-side-source {
  font-size: 0.68rem; font-weight: 700; color: #67e8f9 !important; text-transform: uppercase;
}
.ln-side-title {
  font-size: 0.95rem; font-weight: 700; color: var(--text-primary) !important; margin: 0 0 6px;
  line-height: 1.35; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}
.ln-side-time {
  font-size: 0.7rem; color: #4a5580 !important;
}

/* ── SEARCH GRID ──────────────────────────────────── */
.ln-search-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }

/* ── Filter Controls ──────────────────────────────── */
.ln-filter-controls { display: flex; gap: 12px; }

/* ── TRENDING LIST ────────────────────────────────── */
.ln-trending-list { display: flex; flex-direction: column; gap: 12px; }
.ln-trending-item {
  display: flex; align-items: center; gap: 14px; padding: 14px; text-decoration: none;
  border-radius: 10px; transition: all 0.2s; border: 1px solid rgba(255,255,255,0.06);
  background: rgba(15,23,42,0.4);
}
.ln-trending-item:hover {
  background: rgba(15,23,42,0.6); border-color: rgba(6,182,212,0.2); transform: translateX(6px);
}
.ln-trending-num {
  font-size: 1.4rem; font-weight: 900; color: #06b6d4 !important; min-width: 30px; text-align: center;
}
.ln-trending-body { flex: 1; min-width: 0; }
.ln-trending-title {
  font-size: 0.98rem; font-weight: 700; color: var(--text-primary) !important; margin: 0 0 6px;
  line-height: 1.4; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden;
}
.ln-trending-meta {
  display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
}
.ln-trending-source {
  font-size: 0.68rem; font-weight: 700; color: #67e8f9 !important; text-transform: uppercase;
}
.ln-trending-time {
  font-size: 0.7rem; color: #4a5580 !important;
}
.ln-trending-arrow {
  color: #67e8f9; opacity: 0; transition: opacity 0.2s; flex-shrink: 0;
}
.ln-trending-item:hover .ln-trending-arrow { opacity: 1; }

/* ── CATEGORIES ───────────────────────────────────– */
.ln-categories-grid {
  display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 10px;
}
.ln-category-btn {
  display: flex; align-items: center; justify-content: center; gap: 8px; flex-wrap: wrap;
  padding: 12px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.08);
  background: rgba(15,23,42,0.5); color: #8b9cc8 !important;
  font-size: 0.85rem; font-weight: 600; font-family: var(--font-family); cursor: pointer;
  transition: all 0.2s;
}
.ln-category-btn:hover {
  background: rgba(15,23,42,0.8); border-color: rgba(6,182,212,0.2);
}
.ln-category-btn.expanded {
  background: rgba(6,182,212,0.15); border-color: rgba(6,182,212,0.4); color: #67e8f9 !important;
}
.ln-cat-emoji { display: inline-flex; align-items: center; justify-content: center; width: 24px; height: 24px; color: currentColor; }
.ln-cat-emoji svg { width: 20px; height: 20px; stroke-width: 2; }
.ln-cat-name { flex: 1; text-align: left; }
.ln-cat-count {
  font-size: 0.72rem; padding: 2px 6px; border-radius: 4px;
  background: rgba(6,182,212,0.15); color: #67e8f9 !important;
}
.ln-cat-chevron {
  transition: transform 0.2s; flex-shrink: 0;
}
.ln-category-btn.expanded .ln-cat-chevron { transform: scaleY(-1); }

/* Expanded Category */
.ln-category-expanded {
  margin-top: 28px; padding: 20px; border-radius: 12px;
  background: rgba(15,23,42,0.4); border: 1px solid rgba(6,182,212,0.15);
  animation: slideDown 0.3s ease;
}
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}
.ln-category-title {
  font-size: 1.1rem; font-weight: 700; color: var(--text-primary) !important; margin: 0 0 16px;
}
.ln-category-cards { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 18px; }

/* ── Card Generic ─────────────────────────────────── */
.ln-card {
  display: flex; flex-direction: column;
  background: rgba(15,23,42,0.55); border: 1px solid rgba(255,255,255,0.07);
  border-radius: 14px; overflow: hidden; text-decoration: none;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
}
.ln-card:hover {
  transform: translateY(-6px) scale(1.01);
  box-shadow: 0 16px 48px rgba(6,182,212,0.15), 0 4px 20px rgba(0,0,0,0.4);
  border-color: rgba(6,182,212,0.3);
}

/* Image */
.ln-card-img-wrap { position: relative; overflow: hidden; height: 195px; flex-shrink: 0; }
.ln-card-img { width: 100%; height: 100%; object-fit: cover; display: block; transition: transform 0.35s ease; }
.ln-card:hover .ln-card-img { transform: scale(1.06); }
.ln-card-img-placeholder {
  width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;
  background: rgba(15,23,42,0.8); color: rgba(255,255,255,0.2);
}
.ln-card-img-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(to top, rgba(10,15,30,0.78) 0%, transparent 55%);
  pointer-events: none;
}
.ln-source-badge {
  position: absolute; top: 10px; left: 10px;
  background: linear-gradient(135deg, #0e7490, #06b6d4);
  color: #fff !important; font-size: 0.67rem; font-weight: 700; padding: 3px 10px;
  border-radius: 20px; letter-spacing: 0.3px; max-width: 160px;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
  box-shadow: 0 2px 8px rgba(6,182,212,0.4);
}

/* Body */
.ln-card-body { padding: 14px 16px 16px; display: flex; flex-direction: column; flex: 1; gap: 8px; }
.ln-card-meta { display: flex; align-items: center; gap: 6px; flex-wrap: wrap; }
.ln-card-date { font-size: 0.72rem; color: #4a5580 !important; }
.ln-card-time-ago { font-size: 0.7rem; font-weight: 600; color: #06b6d4 !important; }
.ln-card-title {
  font-size: 0.95rem; font-weight: 700; color: var(--text-primary) !important; margin: 0;
  line-height: 1.45; display: -webkit-box; -webkit-line-clamp: 3; -webkit-box-orient: vertical; overflow: hidden;
}
.ln-card-desc {
  font-size: 0.79rem; color: #6b7fa8 !important; line-height: 1.6; flex: 1;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden; margin-bottom: 4px;
}
.ln-card-cta {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 0.77rem; font-weight: 700; color: #8b9cc8 !important; transition: color 0.2s;
  margin-top: auto;
}
.ln-card:hover .ln-card-cta { color: #67e8f9 !important; }

/* ── State ────────────────────────────────────────── */
.ln-state {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  text-align: center; min-height: 320px; gap: 12px; color: #6b7fa8 !important;
}
.ln-state h3 { color: var(--text-primary) !important; font-size: 1.2rem; margin: 0; }
.ln-state p { color: #6b7fa8 !important; font-size: 0.88rem; margin: 0; }

/* ── Pagination ───────────────────────────────────── */
.ln-pagination { display: flex; align-items: center; justify-content: center; gap: 8px; padding: 32px 0 8px; flex-wrap: wrap; }
.ln-page-btn {
  display: inline-flex; align-items: center; gap: 6px; padding: 9px 18px;
  border-radius: 8px; border: 1px solid var(--border-glass);
  background: rgba(15,23,42,0.6); color: #8b9cc8 !important;
  font-size: 0.83rem; font-weight: 600; font-family: var(--font-family); cursor: pointer; transition: all 0.2s;
}
.ln-page-btn:disabled { opacity: 0.35; cursor: not-allowed; }
.ln-page-btn:not(:disabled):hover { border-color: rgba(6,182,212,0.4); color: #67e8f9 !important; }
.ln-page-numbers { display: flex; align-items: center; gap: 4px; }
.ln-page-num {
  width: 36px; height: 36px; border-radius: 8px; border: 1px solid var(--border-glass);
  background: rgba(15,23,42,0.5); color: #8b9cc8 !important;
  font-size: 0.83rem; font-weight: 600; font-family: var(--font-family); cursor: pointer; transition: all 0.18s;
}
.ln-page-num:hover { border-color: rgba(6,182,212,0.35); color: #67e8f9 !important; }
.ln-page-num.active {
  background: linear-gradient(135deg, #0e7490, #06b6d4);
  border-color: transparent; color: #fff !important;
  box-shadow: 0 2px 12px rgba(6,182,212,0.4);
}
.ln-page-ellipsis { color: #4a5580 !important; padding: 0 4px; font-size: 0.88rem; }
.ln-page-info { text-align: center; font-size: 0.78rem; color: #4a5580 !important; margin: 8px 0 0; }

/* ── Stagger Animation ────────────────────────────── */
.stagger-item {
  animation: fadeInUp 0.5s ease both;
}
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* ── Recent section header overrides ─────────────── */
.ln-recent-header {
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 12px;
}
.ln-recent-controls {
  display: flex;
  align-items: center;
  gap: 14px;
  flex-wrap: wrap;
}
.ln-perpage-wrap {
  display: flex;
  align-items: center;
  gap: 6px;
}
.ln-perpage-label {
  font-size: 0.78rem;
  color: #6b7fa8 !important;
  white-space: nowrap;
  cursor: default;
}
.ln-perpage-select {
  background: rgba(15,23,42,0.7);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  color: var(--text-primary) !important;
  padding: 5px 10px;
  font-size: 0.82rem;
  font-family: var(--font-family);
  outline: none;
  cursor: pointer;
  transition: border-color 0.2s;
}
.ln-perpage-select:focus { border-color: #06b6d4; }

/* ── Recent page info bar ─────────────────────────── */
.ln-recent-info {
  margin-bottom: 18px !important;
  margin-top: -8px;
  font-size: 0.78rem;
  color: #4a5580 !important;
  font-style: italic;
}

/* ── Page-fade transition ─────────────────────────── */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}
.page-fade-enter-from {
  opacity: 0;
  transform: translateY(14px);
}
.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>