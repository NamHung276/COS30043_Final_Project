<script>
import SkeletonCard from "../components/SkeletonCard.vue";
import { backendApi } from "../services/api";

export default {
  components: { SkeletonCard },

  data() {
    return {
      articles: [],
      loading: true,
      error: null,
      searchTerm: "",
      currentPage: 1,
      itemsPerPage: 12,
      lastUpdated: "",
      activeTab: "Latest",

      // Market Widget Data
      trendingGames: [],
      steamDeals: [],
      upcomingReleases: [],
      marketLoading: true,
    };
  },

  computed: {
    tabFilteredArticles() {
      if (this.activeTab === "Latest") {
        return this.articles;
      }
      return this.articles.filter((a) =>
        this.articleMatchesCat(a, this.activeTab),
      );
    },

    filteredArticles() {
      const blacklist = ["casino", "slots", "betting", "gambling", "poker", "roulette", "blackjack", "lottery"];
      const baseArticles = this.tabFilteredArticles.filter(article => {
        const title = (article.title || "").toLowerCase();
        const desc = (article.description || "").toLowerCase();
        return !blacklist.some(word => title.includes(word) || desc.includes(word));
      });

      const term = this.searchTerm.toLowerCase();
      if (!term) return baseArticles;
      
      return baseArticles.filter((article) => {
        const title = (article.title || "").toLowerCase();
        const description = (article.description || "").toLowerCase();
        const source = (article.source?.name || "").toLowerCase();
        return (
          title.includes(term) ||
          description.includes(term) ||
          source.includes(term)
        );
      });
    },

    // ── Editorial Structure ──
    
    // Featured Story: Pick a robust article (has image and good description)
    featuredStory() {
      if (this.filteredArticles.length === 0) return null;
      // Prefer an article with a long description and image
      return this.filteredArticles.find(a => a.urlToImage && a.description && a.description.length > 80) || this.filteredArticles[0];
    },

    // Latest Headlines: The next 4 articles
    latestHeadlines() {
      if (this.filteredArticles.length === 0) return [];
      return this.filteredArticles.filter(a => a !== this.featuredStory).slice(0, 4);
    },

    // Grid Articles: Everything else, ready for pagination
    editorsPicks() {
      if (this.filteredArticles.length === 0) return [];
      const excluded = [this.featuredStory, ...this.latestHeadlines].filter(Boolean);
      const remaining = this.filteredArticles.filter(a => !excluded.includes(a));
      // Pick 3 articles for Editor's picks, preferably with images
      return remaining.filter(a => a.urlToImage).slice(0, 3);
    },

    editorialGridArticles() {
      if (this.filteredArticles.length === 0) return [];
      const excluded = [this.featuredStory, ...this.latestHeadlines, ...this.editorsPicks].filter(Boolean);
      return this.filteredArticles.filter(a => !excluded.includes(a));
    },

    totalPages() {
      return Math.ceil(this.editorialGridArticles.length / this.itemsPerPage);
    },

    paginatedArticles() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      return this.editorialGridArticles.slice(start, start + this.itemsPerPage);
    },

    visiblePages() {
      const total = this.totalPages;
      const pages = [];
      if (total <= 7) {
        for (let i = 1; i <= total; i++) pages.push(i);
      } else {
        pages.push(1);
        if (this.currentPage > 4) pages.push("...");
        const s = Math.max(2, this.currentPage - 1);
        const e = Math.min(total - 1, this.currentPage + 1);
        for (let i = s; i <= e; i++) pages.push(i);
        if (this.currentPage < total - 3) pages.push("...");
        pages.push(total);
      }
      return pages;
    },

    ALL_CATEGORIES() {
      return [
        "Latest",
        "Breaking",
        "Reviews",
        "Esports",
        "Industry",
        "PC",
        "PlayStation",
        "Xbox",
        "Nintendo",
        "Mobile",
        "Indie",
        "Hardware",
      ];
    },

    categories() {
      // Only show categories that have at least 1 matching article
      return this.ALL_CATEGORIES.filter((cat) => {
        if (cat === "Latest") return true;
        return this.articles.some((a) => this.articleMatchesCat(a, cat));
      });
    },
  },

  watch: {
    searchTerm() {
      this.currentPage = 1;
    },
    activeTab() {
      this.currentPage = 1;
    },
  },

  methods: {
    handleImageError(event) {
      const parent = event.target.parentElement;
      const placeholder = document.createElement("div");
      placeholder.className = "w-100 h-100 d-flex flex-column align-items-center justify-content-center bg-dark text-muted border border-secondary border-opacity-25 rounded";
      placeholder.style.minHeight = "200px";
      placeholder.innerHTML = `
        <i class="bi bi-image-fill fs-1 mb-2 opacity-50"></i>
        <div class="small fw-bold px-3 text-center">Image Unavailable</div>
        <div class="small px-3 text-center opacity-75" style="font-size: 0.7rem;">(Source Error or Copyright Restriction)</div>
      `;
      parent.replaceChild(placeholder, event.target);
    },
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        this.$nextTick(() => {
          const el = document.getElementById("editorial-grid");
          if (el) {
            const offset = el.getBoundingClientRect().top + window.scrollY - 100;
            window.scrollTo({ top: offset, behavior: "smooth" });
          }
        });
      }
    },
    formatDate(dateStr) {
      if (!dateStr) return "";
      return new Date(dateStr).toLocaleDateString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
      });
    },
    timeAgo(dateStr) {
      if (!dateStr) return "";
      const diff = Date.now() - new Date(dateStr).getTime();
      const h = Math.floor(diff / 3600000);
      if (h < 1) return "Just now";
      if (h < 24) return `${h}h ago`;
      const d = Math.floor(h / 24);
      return `${d}d ago`;
    },
    setActiveTab(tab) {
      this.activeTab = tab;
    },
    getReadingTime(description) {
      if (!description) return "2 min read";
      const words = description.trim().split(/\s+/).length;
      const mins = Math.max(2, Math.ceil(words / 50) + 1);
      return `${mins} min read`;
    },
    getArticleCategory(article) {
      const cats = this.ALL_CATEGORIES.filter((c) => c !== "Latest" && c !== "Breaking");
      for (const cat of cats) {
        if (this.articleMatchesCat(article, cat)) {
          return cat;
        }
      }
      return "News";
    },
    articleMatchesCat(a, cat) {
      const combined = ((a.title || "") + " " + (a.description || "")).toLowerCase();
      if (cat === "Latest") return true;
      if (cat === "Breaking") return combined.includes("break") || combined.includes("urgent");
      if (cat === "Reviews") return combined.includes("review") || combined.includes("gameplay") || combined.includes("score");
      if (cat === "Esports") return combined.includes("esport") || combined.includes("tournament") || combined.includes("league");
      if (cat === "Industry") return combined.includes("developer") || combined.includes("studio") || combined.includes("publisher") || combined.includes("layoff");
      if (cat === "PC") return combined.includes("pc game") || combined.includes("steam") || combined.includes("windows");
      if (cat === "PlayStation") return combined.includes("playstation") || combined.includes("ps5") || combined.includes("sony");
      if (cat === "Xbox") return combined.includes("xbox") || combined.includes("game pass") || combined.includes("microsoft");
      if (cat === "Nintendo") return combined.includes("nintendo") || combined.includes("switch");
      if (cat === "Mobile") return combined.includes("mobile") || combined.includes("ios") || combined.includes("android");
      if (cat === "Indie") return combined.includes("indie") || combined.includes("solo dev");
      if (cat === "Hardware") return combined.includes("gpu") || combined.includes("cpu") || combined.includes("console");
      return false;
    },
    
    formatNumber(num) {
      return new Intl.NumberFormat('en-US').format(num);
    },
  },

  async mounted() {
    try {
      const { data } = await backendApi.get("/news", {
        params: { page_size: 50 }
      });
      
      if (!data || !data.articles || data.articles.length === 0) {
        this.error = "Failed to load news from our providers. Please try again later.";
      } else {
        this.articles = data.articles;
      }
      
      this.lastUpdated = new Date().toLocaleString();
    } catch (error) {
      console.error("Critical error in mounted:", error);
      this.error = "Critical error loading news. Please try again later.";
    } finally {
      this.loading = false;
    }

    // ── Fetch Market Widget Data ──
    try {
      const today = new Date().toISOString().split('T')[0];
      const nextYearDate = new Date();
      nextYearDate.setFullYear(nextYearDate.getFullYear() + 1);
      const nextYear = nextYearDate.toISOString().split('T')[0];

      const [trendingRes, dealsRes, upcomingRes] = await Promise.all([
        backendApi.get("/games", { params: { ordering: "-added", page_size: 4 } }),
        backendApi.get("/deals", { params: { store_id: "1", page_size: 4 } }),
        backendApi.get("/games", { params: { dates: `${today},${nextYear}`, ordering: "-added", page_size: 4 } })
      ]);
      this.trendingGames = trendingRes.data.results || [];
      this.steamDeals = dealsRes.data.results || [];
      this.upcomingReleases = upcomingRes.data.results || [];
    } catch (err) {
      console.error("Failed to load market widget data:", err);
    } finally {
      this.marketLoading = false;
    }
  },
};
</script>

<template>
  <div class="journal-page">
    <!-- ── Header ── -->
    <header class="journal-header">
      <div class="container">
        <div class="jh-top">
          <div class="jh-titles">
            <div class="jh-live-tag"><span class="live-dot"></span> LIVE COVERAGE</div>
            <h1 class="jh-main-title">Gaming Hub News</h1>
            <p class="jh-subtitle">The latest stories, reviews, and industry insights, updated {{ lastUpdated }}.</p>
          </div>
          <div class="jh-search">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            <input v-model="searchTerm" type="text" placeholder="Search stories..." />
          </div>
        </div>

        <nav class="jh-nav">
          <button
            v-for="cat in categories"
            :key="cat"
            class="jh-nav-item"
            :class="{ active: activeTab === cat }"
            @click="setActiveTab(cat)"
          >
            {{ cat }}
          </button>
        </nav>
      </div>
    </header>

    <!-- ── Main Content ── -->
    <main class="container journal-content">
      <div v-if="loading" class="journal-loading">
        <div class="spinner"></div>
        <p>Fetching latest stories...</p>
      </div>

      <div v-else-if="error" class="journal-error">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><circle cx="12" cy="12" r="10"/><path d="M12 8v4m0 4h.01"/></svg>
        <h3>Couldn't load news</h3>
        <p>{{ error }}</p>
      </div>

      <template v-else>
        <!-- ── Breaking News Ticker ── -->
        <div class="breaking-ticker mb-5" v-if="latestHeadlines.length > 0">
          <div class="ticker-label">BREAKING</div>
          <div class="ticker-scroll">
            <div class="ticker-content">
              <span v-for="(article, index) in latestHeadlines" :key="'tick'+index" class="ticker-item">
                <span class="ticker-dot">•</span> {{ article.title }}
              </span>
              <!-- Duplicate for seamless scroll -->
              <span v-for="(article, index) in latestHeadlines" :key="'tick2'+index" class="ticker-item">
                <span class="ticker-dot">•</span> {{ article.title }}
              </span>
            </div>
          </div>
        </div>

        <!-- ── Editorial Hero ── -->
        <section v-if="featuredStory && (currentPage === 1 || searchTerm)" class="ed-hero-section">
          <div class="ed-hero-layout">
            
            <!-- Main Featured Story (70%) -->
            <a :href="featuredStory.url" target="_blank" rel="noopener noreferrer" class="ed-featured-card">
              <div class="ed-feat-img-wrap">
                <img v-if="featuredStory.urlToImage" :src="featuredStory.urlToImage" :alt="featuredStory.title" class="ed-feat-img" @error="handleImageError" />
                <div v-else class="ed-feat-img-placeholder"></div>
              </div>
              <div class="ed-feat-content">
                <div class="ed-meta">
                  <span class="ed-cat">{{ getArticleCategory(featuredStory) }}</span>
                  <span class="ed-dot">•</span>
                  <span class="ed-time">{{ timeAgo(featuredStory.publishedAt) }}</span>
                </div>
                <h2 class="ed-feat-title">{{ featuredStory.title }}</h2>
                <p class="ed-feat-desc">{{ featuredStory.description }}</p>
                <div class="mt-3 mb-2">
                  <button class="btn btn-primary px-4 py-2 fw-bold rounded-pill shadow-sm">Read Full Story <i class="bi bi-arrow-right ms-1"></i></button>
                </div>
                
                <div class="ed-rich-meta">
                  <div class="ed-author-block">
                    <div class="author-info" style="margin-left: 0;">
                      <span class="author-source fw-bold text-light"><i class="bi bi-building me-2"></i>{{ featuredStory.source?.name }}</span>
                    </div>
                  </div>
                  <div class="ed-stats-block">
                    <span><i class="bi bi-clock"></i> {{ getReadingTime(featuredStory.description) }}</span>
                  </div>
                </div>
              </div>
            </a>

            <!-- Latest Headlines Sidebar (30%) -->
            <div class="ed-sidebar">
              <h3 class="ed-sidebar-title">The Latest</h3>
              <div class="ed-sidebar-list">
                <a
                  v-for="article in latestHeadlines"
                  :key="article.url"
                  :href="article.url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="ed-sidebar-item"
                >
                  <div class="ed-side-meta">
                    <span class="ed-cat">{{ getArticleCategory(article) }}</span>
                    <span class="ed-time">{{ timeAgo(article.publishedAt) }}</span>
                  </div>
                  <h4 class="ed-side-title">{{ article.title }}</h4>
                  <div class="ed-side-author d-flex align-items-center">
                    {{ article.source?.name }} 
                  </div>
                </a>
              </div>
            </div>
            
          </div>
        </section>

        <!-- ── Live Market Widget (Store Integration) ── -->
        <section class="market-widget-section mb-5" v-if="!searchTerm && currentPage === 1">
          <div class="market-header d-flex justify-content-between align-items-center mb-4">
            <h3 class="ed-grid-title m-0"><i class="bi bi-shop me-2"></i> Trending Games & Deals</h3>
            <router-link to="/games" class="btn btn-outline-light btn-sm rounded-pill px-3">Store Home &rarr;</router-link>
          </div>
          
          <div v-if="marketLoading" class="text-center py-5 text-muted">
            <div class="spinner-border spinner-border-sm me-2"></div> Loading live market data...
          </div>
          
          <div v-else class="market-grid">
            <!-- Steam Deals -->
            <div class="market-col">
              <h4 class="market-col-title text-success"><i class="bi bi-tags-fill me-1"></i> Top Steam Deals</h4>
              <div class="market-list">
                <a v-for="deal in steamDeals" :key="deal.dealID" :href="`/games/${deal.gameID}`" class="market-item">
                  <img :src="deal.thumb" class="market-thumb" />
                  <div class="market-info">
                    <span class="market-name">{{ deal.title }}</span>
                    <div class="market-price-block">
                      <span class="market-discount">-{{ Math.round(deal.savings) }}%</span>
                      <span class="text-decoration-line-through text-muted small ms-1">${{ deal.normalPrice }}</span>
                      <span class="market-price ms-auto">${{ deal.salePrice }}</span>
                    </div>
                  </div>
                </a>
              </div>
            </div>

            <!-- Trending Games -->
            <div class="market-col">
              <h4 class="market-col-title text-danger"><i class="bi bi-fire me-1"></i> Trending Now</h4>
              <div class="market-list">
                <router-link v-for="game in trendingGames" :key="game.id" :to="`/games/${game.id}`" class="market-item">
                  <img :src="game.background_image" class="market-thumb" />
                  <div class="market-info">
                    <span class="market-name">{{ game.name }}</span>
                    <div class="market-meta">
                      <span class="text-warning"><i class="bi bi-star-fill"></i> {{ game.rating }}</span>
                      <span class="text-muted ms-2">{{ formatDate(game.released) }}</span>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>

            <!-- Upcoming Releases -->
            <div class="market-col">
              <h4 class="market-col-title text-primary"><i class="bi bi-calendar-star me-1"></i> Upcoming Releases</h4>
              <div class="market-list">
                <router-link v-for="game in upcomingReleases" :key="game.id" :to="`/games/${game.id}`" class="market-item">
                  <img :src="game.background_image" class="market-thumb" />
                  <div class="market-info">
                    <span class="market-name">{{ game.name }}</span>
                    <div class="market-meta d-flex justify-content-between align-items-center w-100">
                      <span class="text-muted">{{ formatDate(game.released) }}</span>
                      <button class="btn btn-sm btn-outline-secondary rounded-pill py-0 px-2" style="font-size: 0.75rem;"><i class="bi bi-heart me-1"></i> Wishlist</button>
                    </div>
                  </div>
                </router-link>
              </div>
            </div>
          </div>
        </section>

        <!-- ── Editor's Picks (Horizontal Layout) ── -->
        <section class="ed-picks-section mb-5" v-if="!searchTerm && currentPage === 1 && editorsPicks.length > 0">
          <div class="ed-grid-header mb-4">
            <h3 class="ed-grid-title m-0"><i class="bi bi-award me-2"></i> Editor's Picks</h3>
          </div>
          <div class="row g-4">
            <div class="col-12 col-lg-4" v-for="article in editorsPicks" :key="'pick-'+article.url">
              <a :href="article.url" target="_blank" rel="noopener noreferrer" class="ed-pick-card d-flex flex-column h-100 text-decoration-none">
                <div class="ed-pick-img-wrap rounded overflow-hidden mb-3" style="aspect-ratio: 16/9;">
                  <img :src="article.urlToImage" class="w-100 h-100 object-fit-cover" @error="handleImageError" />
                </div>
                <div class="ed-pick-body d-flex flex-column flex-grow-1">
                  <span class="text-primary fw-bold text-uppercase small mb-2" style="letter-spacing: 0.05em;">{{ getArticleCategory(article) }}</span>
                  <h4 class="fw-bolder text-white mb-2 fs-5" style="line-height: 1.4;">{{ article.title }}</h4>
                  <p class="text-secondary small mb-3">{{ article.description?.slice(0, 90) }}...</p>
                  <div class="mt-auto d-flex align-items-center justify-content-between pt-3 border-top border-secondary border-opacity-25">
                    <span class="text-muted small fw-bold">{{ timeAgo(article.publishedAt) }}</span>
                    <div class="d-flex gap-2">
                      <button class="btn btn-sm btn-outline-secondary rounded-circle py-0 px-1 border-0" @click.prevent><i class="bi bi-bookmark"></i></button>
                      <button class="btn btn-sm btn-outline-secondary rounded-circle py-0 px-1 border-0" @click.prevent><i class="bi bi-share"></i></button>
                    </div>
                  </div>
                </div>
              </a>
            </div>
          </div>
        </section>

        <!-- ── News Grid (More Stories) ── -->
        <section id="editorial-grid" class="ed-grid-section" v-if="paginatedArticles.length">
          <div class="ed-grid-header mb-4">
            <h3 class="ed-grid-title">{{ searchTerm ? `Results for "${searchTerm}"` : (activeTab === 'Latest' ? 'More Stories' : activeTab + ' News') }}</h3>
          </div>
          
          <div class="ed-card-grid">
            <a
              v-for="article in paginatedArticles"
              :key="article.url"
              :href="article.url"
              target="_blank"
              rel="noopener noreferrer"
              class="ed-card"
            >
              <div class="ed-card-img-wrap">
                <img v-if="article.urlToImage" v-lazy-img="article.urlToImage" :alt="article.title" class="ed-card-img" @error="handleImageError" />
                <div v-else class="ed-card-img-placeholder">
                  <i class="bi bi-newspaper fs-1 opacity-25"></i>
                </div>
              </div>
              <div class="ed-card-body">
                <div class="ed-meta">
                  <span class="ed-cat">{{ getArticleCategory(article) }}</span>
                  <span class="ed-dot">•</span>
                  <span class="ed-time">{{ timeAgo(article.publishedAt) }}</span>
                </div>
                <h4 class="ed-card-title">{{ article.title }}</h4>
                <p class="ed-card-desc">{{ article.description?.slice(0, 100) }}...</p>
                <div class="ed-card-footer mt-auto pt-3 border-top border-secondary border-opacity-25 d-flex justify-content-between align-items-center">
                  <div class="d-flex align-items-center">
                    <span class="ed-source"><i class="bi bi-building me-1"></i> {{ article.source?.name }}</span>
                  </div>
                  <div class="d-flex gap-2 align-items-center">
                    <button class="btn btn-sm btn-outline-secondary rounded-circle py-0 px-1 border-0" @click.prevent><i class="bi bi-bookmark"></i></button>
                    <button class="btn btn-sm btn-outline-secondary rounded-circle py-0 px-1 border-0" @click.prevent><i class="bi bi-share"></i></button>
                  </div>
                </div>
              </div>
            </a>
          </div>

          <!-- Pagination -->
          <nav v-if="totalPages > 1" class="ed-pagination">
            <button class="ed-page-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">&larr; Prev</button>
            <div class="ed-page-numbers">
              <template v-for="(page, i) in visiblePages" :key="i">
                <span v-if="page === '...'" class="ed-page-ellipsis">&#8230;</span>
                <button
                  v-else
                  class="ed-page-num"
                  :class="{ active: currentPage === page }"
                  @click="goToPage(page)"
                >
                  {{ page }}
                </button>
              </template>
            </div>
            <button class="ed-page-btn" :disabled="currentPage === totalPages" @click="goToPage(currentPage + 1)">Next &rarr;</button>
          </nav>
        </section>
        
        <div v-if="!paginatedArticles.length && !featuredStory" class="journal-empty">
          <p>No stories found for your current filters.</p>
        </div>

      </template>
    </main>
  </div>
</template>

<style scoped>
/* ── Base Variables & Page ── */
.journal-page {
  min-height: 100vh;
  background: var(--bg-deep); /* Use existing dark mode background */
  color: var(--text-primary);
  font-family: var(--font-family);
  -webkit-font-smoothing: antialiased;
}
.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 20px;
}

/* ── Header ── */
.journal-header {
  background: var(--bg-surface);
  border-bottom: 1px solid var(--overlay-medium);
  padding: 40px 0 0;
}
.jh-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  margin-bottom: 24px;
  gap: 20px;
  flex-wrap: wrap;
}
.jh-titles {
  flex: 1;
}
.jh-live-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: var(--danger);
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.live-dot {
  width: 8px;
  height: 8px;
  background: var(--danger);
  border-radius: 50%;
  animation: pulse 2s infinite;
}
@keyframes pulse { 0% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(0.8); } 100% { opacity: 1; transform: scale(1); } }

.jh-main-title {
  font-size: 2.5rem;
  font-weight: 900;
  margin: 0 0 6px;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}
.jh-subtitle {
  color: var(--text-muted);
  font-size: 0.95rem;
  margin: 0;
}
.jh-search {
  display: flex;
  align-items: center;
  background: var(--bg-base);
  border: 1px solid var(--overlay-medium);
  border-radius: 6px;
  padding: 10px 16px;
  width: 300px;
  max-width: 100%;
  transition: border-color 0.2s;
}
.jh-search:focus-within {
  border-color: var(--primary);
}
.jh-search svg {
  color: var(--text-muted);
  margin-right: 10px;
}
.jh-search input {
  background: transparent;
  border: none;
  outline: none;
  color: var(--text-primary);
  width: 100%;
  font-size: 0.95rem;
}
.jh-search input::placeholder {
  color: var(--text-muted);
}

/* ── Nav Tabs ── */
.jh-nav {
  display: flex;
  gap: 24px;
  overflow-x: auto;
  scrollbar-width: none;
  border-top: 1px solid var(--overlay-light);
}
.jh-nav::-webkit-scrollbar { display: none; }
.jh-nav-item {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 600;
  padding: 16px 0;
  cursor: pointer;
  position: relative;
  white-space: nowrap;
  transition: color 0.2s;
}
.jh-nav-item:hover {
  color: var(--text-primary);
}
.jh-nav-item.active {
  color: var(--primary);
}
.jh-nav-item.active::after {
  content: "";
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--primary);
  border-radius: 3px 3px 0 0;
}

/* ── Content Area ── */
.journal-content {
  padding-top: 40px;
  padding-bottom: 80px;
}

/* ── Shared Meta Styling ── */
.ed-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 10px;
}
.ed-cat { color: var(--primary); }
.ed-source { color: var(--text-secondary); }
.ed-time { color: var(--text-muted); }
.ed-dot { color: var(--overlay-heavy); }

/* ── Editorial Hero Section ── */
.ed-hero-section {
  margin-bottom: 60px;
}
.ed-hero-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 30px;
}
@media (max-width: 900px) {
  .ed-hero-layout { grid-template-columns: 1fr; }
}

/* Featured Card */
.ed-featured-card {
  display: flex;
  flex-direction: column;
  background: transparent;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
}
.ed-featured-card:hover .ed-feat-title {
  text-decoration: underline;
  text-decoration-color: var(--primary);
  text-underline-offset: 4px;
}
.ed-feat-img-wrap {
  width: 100%;
  aspect-ratio: 16/9;
  overflow: hidden;
}
.ed-feat-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.ed-featured-card:hover .ed-feat-img {
  transform: scale(1.02);
}
.ed-feat-img-placeholder {
  width: 100%;
  height: 100%;
  background: var(--bg-base);
}
.ed-feat-content {
  padding: 24px 0 0 0;
  display: flex;
  flex-direction: column;
  flex: 1;
}
.ed-feat-title {
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 900;
  line-height: 1.1;
  margin: 0 0 16px;
  color: var(--text-primary);
  letter-spacing: -0.02em;
}
.ed-feat-desc {
  font-size: 1.05rem;
  color: var(--text-secondary);
  line-height: 1.6;
  margin: 0 0 20px;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ed-read-btn {
  margin-top: auto;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--primary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.ed-read-btn span {
  transition: transform 0.2s;
}
.ed-featured-card:hover .ed-read-btn span {
  transform: translateX(4px);
}

/* Sidebar List */
.ed-sidebar {
  display: flex;
  flex-direction: column;
}
.ed-sidebar-title {
  font-size: 1.1rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-primary);
  margin: 0 0 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--overlay-medium);
}
.ed-sidebar-list {
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.ed-sidebar-item {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  padding-bottom: 20px;
  border-bottom: 1px solid var(--overlay-light);
  transition: opacity 0.2s;
}
.ed-sidebar-item:hover {
  opacity: 0.8;
}
.ed-sidebar-item:last-child {
  border-bottom: none;
}
.ed-side-meta {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 8px;
}
.ed-side-title {
  font-size: 1.15rem;
  font-weight: 800;
  line-height: 1.3;
  color: var(--text-primary);
  margin: 0;
  transition: color 0.2s;
}
.ed-sidebar-item:hover .ed-side-title {
  color: var(--primary);
  text-decoration: underline;
  text-underline-offset: 2px;
}

/* ── Grid Section ── */
.ed-grid-header {
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--overlay-medium);
}
.ed-grid-title {
  font-size: 1.3rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-primary);
  margin: 0;
}

.ed-card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}
.ed-card {
  display: flex;
  flex-direction: column;
  background: transparent;
  overflow: hidden;
  text-decoration: none;
}
.ed-card:hover .ed-card-title {
  color: var(--primary);
}
.ed-card:hover .ed-card-img {
  transform: scale(1.05);
}
.ed-card-img-wrap {
  width: 100%;
  aspect-ratio: 16/9;
  background: var(--bg-base);
  position: relative;
}
.ed-card-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.ed-card-img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
}
.ed-card-body {
  padding: 16px 0 0 0;
  display: flex;
  flex-direction: column;
  flex: 1;
}
.ed-card-title {
  font-size: 1.1rem;
  font-weight: 700;
  line-height: 1.4;
  margin: 0 0 10px;
  color: var(--text-primary);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ed-card-desc {
  font-size: 0.9rem;
  color: var(--text-secondary);
  line-height: 1.5;
  margin: 0 0 16px;
}
.ed-card-footer {
  margin-top: auto;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--text-muted);
}

/* ── Pagination ── */
.ed-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 50px;
}
.ed-page-btn, .ed-page-num {
  background: transparent;
  border: 1px solid var(--overlay-medium);
  color: var(--text-primary);
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 600;
  transition: background 0.2s;
}
.ed-page-numbers {
  display: flex;
  gap: 8px;
}
.ed-page-num {
  padding: 8px 12px;
}
.ed-page-btn:hover:not(:disabled), .ed-page-num:hover:not(.active) {
  background: var(--overlay-light);
}
.ed-page-num.active {
  background: var(--primary);
  border-color: var(--primary);
  color: var(--text-primary);
}
.ed-page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}
.ed-page-ellipsis {
  color: var(--text-muted);
  padding: 0 8px;
  align-self: flex-end;
}

/* ── Loading / Error ── */
.journal-loading, .journal-error, .journal-empty {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}
.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--overlay-medium);
  border-top-color: var(--primary);
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.journal-error svg {
  color: var(--danger);
  margin-bottom: 16px;
}
/* ── Breaking Ticker ── */
.breaking-ticker {
  display: flex;
  background: var(--bg-surface);
  border-left: 4px solid var(--primary);
  border-radius: 4px;
  overflow: hidden;
  height: 40px;
  align-items: center;
}
.ticker-label {
  background: var(--primary);
  color: var(--text-primary);
  font-weight: 800;
  font-size: 0.8rem;
  padding: 0 16px;
  height: 100%;
  display: flex;
  align-items: center;
  z-index: 2;
  letter-spacing: 0.05em;
}
.ticker-scroll {
  flex: 1;
  overflow: hidden;
  position: relative;
  height: 100%;
}
.ticker-content {
  display: flex;
  white-space: nowrap;
  animation: scroll-ticker 30s linear infinite;
  height: 100%;
  align-items: center;
}
.ticker-item {
  padding: 0 30px;
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--text-primary);
}
.ticker-dot {
  color: var(--primary);
  margin-right: 8px;
}
@keyframes scroll-ticker {
  0% { transform: translateX(0); }
  100% { transform: translateX(-50%); }
}

/* ── Rich Meta ── */
.ed-rich-meta {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--overlay-medium);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.ed-author-block {
  display: flex;
  align-items: center;
  gap: 12px;
}
.author-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--overlay-heavy);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.2rem;
  color: var(--text-secondary);
}
.author-info {
  display: flex;
  flex-direction: column;
}
.author-name {
  font-weight: 700;
  font-size: 0.9rem;
  color: var(--text-primary);
}
.author-source {
  font-size: 0.8rem;
  color: var(--text-muted);
}
.ed-stats-block {
  display: flex;
  gap: 16px;
  font-size: 0.85rem;
  color: var(--text-muted);
  font-weight: 600;
}
.ed-side-author {
  font-size: 0.8rem;
  color: var(--text-muted);
  margin-top: 8px;
  font-weight: 600;
}

/* ── Live Market Widget ── */
.market-widget-section {
  background: var(--bg-surface);
  border-radius: 8px;
  padding: 30px;
  border: 1px solid var(--overlay-medium);
}
.market-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 30px;
}
@media (max-width: 992px) {
  .market-grid { grid-template-columns: 1fr; }
}
.market-col-title {
  font-size: 1.1rem;
  font-weight: 800;
  text-transform: uppercase;
  margin-bottom: 20px;
  letter-spacing: 0.05em;
  padding-bottom: 12px;
  border-bottom: 2px solid var(--overlay-light);
}
.market-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.market-item {
  display: flex;
  gap: 16px;
  text-decoration: none;
  background: var(--bg-base);
  border-radius: 6px;
  padding: 12px;
  transition: transform 0.2s, background 0.2s;
  border: 1px solid transparent;
}
.market-item:hover {
  transform: translateY(-2px);
  background: var(--overlay-light);
  border-color: var(--overlay-medium);
}
.market-thumb {
  width: 70px;
  height: 90px;
  object-fit: cover;
  border-radius: 4px;
}
.market-info {
  display: flex;
  flex-direction: column;
  justify-content: center;
  flex: 1;
}
.market-name {
  font-weight: 700;
  font-size: 0.95rem;
  color: var(--text-primary);
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.market-meta {
  font-size: 0.85rem;
  font-weight: 600;
}
.market-price-block {
  display: flex;
  align-items: center;
  gap: 8px;
}
.market-discount {
  background: var(--success);
  color: white;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 800;
}
.market-price {
  color: var(--success);
  font-weight: 700;
  font-size: 0.9rem;
}

/* ── Editor's Picks ── */
.ed-picks-section {
  padding-top: 30px;
  border-top: 1px solid var(--overlay-medium);
}
.ed-pick-card {
  background: var(--bg-surface);
  border: 1px solid var(--overlay-light);
  border-radius: 8px;
  padding: 16px;
  transition: transform 0.2s, box-shadow 0.2s;
}
.ed-pick-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
}
.ed-pick-card:hover .ed-pick-title {
  color: var(--primary);
  text-decoration: underline;
  text-underline-offset: 2px;
}
.ed-pick-card:hover .ed-pick-img-wrap img {
  transform: scale(1.05);
}
.ed-pick-img-wrap {
  position: relative;
  background: var(--bg-base);
}
.ed-pick-img-wrap img {
  transition: transform 0.3s ease;
}
.ed-pick-img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: var(--overlay-heavy);
  background: var(--bg-base);
}
</style>
