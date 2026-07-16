<script>
import SkeletonCard from "../components/SkeletonCard.vue";
import { newsApi, newsDataApi } from "../services/api";

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
      const term = this.searchTerm.toLowerCase();
      if (!term) return this.tabFilteredArticles;
      return this.tabFilteredArticles.filter((article) => {
        const title = article.title || "";
        const description = article.description || "";
        const source = article.source?.name || "";
        return (
          title.toLowerCase().includes(term) ||
          description.toLowerCase().includes(term) ||
          source.toLowerCase().includes(term)
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
    editorialGridArticles() {
      if (this.filteredArticles.length === 0) return [];
      const excluded = [this.featuredStory, ...this.latestHeadlines].filter(Boolean);
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
  },

  async mounted() {
    try {
      const promises = [];

      promises.push(
        newsApi.get("/everything", {
          params: {
            q: 'gaming OR "video games"',
            language: "en",
            sortBy: "publishedAt",
            pageSize: 80,
          },
        }).then(res => {
          const articles = res.data.articles || [];
          return articles.filter(a => a.title !== "[Removed]" && a.description !== null);
        })
      );

      if (import.meta.env.VITE_NEWSDATA_API_KEY) {
        promises.push(
          newsDataApi.get("/latest", {
            params: {
              q: 'gaming OR "video games"',
              language: "en",
            },
          }).then(res => {
            const results = res.data.results || [];
            return results.map(a => ({
              title: a.title,
              description: a.description,
              url: a.link,
              urlToImage: a.image_url,
              publishedAt: a.pubDate,
              source: { name: a.source_id },
            })).filter(a => a.description && a.urlToImage);
          })
        );
      }

      const settled = await Promise.allSettled(promises);
      let combinedArticles = [];
      
      for (const result of settled) {
        if (result.status === "fulfilled" && Array.isArray(result.value)) {
          combinedArticles = combinedArticles.concat(result.value);
        }
      }

      if (combinedArticles.length === 0) {
        this.error = "Failed to load news from our providers. Please try again later.";
      } else {
        this.articles = combinedArticles.sort((a, b) => new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime());
      }
      
      this.lastUpdated = new Date().toLocaleString();
    } catch (error) {
      console.error("Critical error in mounted:", error);
      this.error = "Critical error loading news. Please try again later.";
    } finally {
      this.loading = false;
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
        <!-- ── Editorial Hero ── -->
        <section v-if="featuredStory && (currentPage === 1 || searchTerm)" class="ed-hero-section">
          <div class="ed-hero-layout">
            
            <!-- Main Featured Story -->
            <a :href="featuredStory.url" target="_blank" rel="noopener noreferrer" class="ed-featured-card">
              <div class="ed-feat-img-wrap">
                <img v-if="featuredStory.urlToImage" :src="featuredStory.urlToImage" :alt="featuredStory.title" class="ed-feat-img" />
                <div v-else class="ed-feat-img-placeholder"></div>
              </div>
              <div class="ed-feat-content">
                <div class="ed-meta">
                  <span class="ed-cat">{{ getArticleCategory(featuredStory) }}</span>
                  <span class="ed-dot">•</span>
                  <span class="ed-source">{{ featuredStory.source?.name }}</span>
                  <span class="ed-dot">•</span>
                  <span class="ed-time">{{ timeAgo(featuredStory.publishedAt) }}</span>
                </div>
                <h2 class="ed-feat-title">{{ featuredStory.title }}</h2>
                <p class="ed-feat-desc">{{ featuredStory.description }}</p>
                <div class="ed-read-btn">Read Full Story <span>&rarr;</span></div>
              </div>
            </a>

            <!-- Latest Headlines Sidebar -->
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
                </a>
              </div>
            </div>
            
          </div>
        </section>

        <!-- ── News Grid ── -->
        <section id="editorial-grid" class="ed-grid-section" v-if="paginatedArticles.length">
          <div class="ed-grid-header">
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
                <img v-if="article.urlToImage" v-lazy-img="article.urlToImage" :alt="article.title" class="ed-card-img" />
                <div v-else class="ed-card-img-placeholder">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/></svg>
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
                <div class="ed-card-footer">
                  <span class="ed-source">{{ article.source?.name }}</span>
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
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
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
  color: #ef4444;
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  margin-bottom: 8px;
}
.live-dot {
  width: 8px;
  height: 8px;
  background: #ef4444;
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
  border: 1px solid rgba(255, 255, 255, 0.1);
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
  border-top: 1px solid rgba(255,255,255,0.05);
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
.ed-dot { color: rgba(255,255,255,0.2); }

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
  background: var(--bg-surface);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 12px;
  overflow: hidden;
  text-decoration: none;
  color: inherit;
  transition: transform 0.2s, box-shadow 0.2s;
}
.ed-featured-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0,0,0,0.3);
  border-color: rgba(255,255,255,0.15);
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
  padding: 30px;
  display: flex;
  flex-direction: column;
  flex: 1;
}
.ed-feat-title {
  font-size: 1.8rem;
  font-weight: 800;
  line-height: 1.25;
  margin: 0 0 12px;
  color: var(--text-primary);
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
  border-bottom: 2px solid rgba(255,255,255,0.1);
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
  border-bottom: 1px solid rgba(255,255,255,0.05);
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
  font-size: 1.1rem;
  font-weight: 700;
  line-height: 1.4;
  color: var(--text-primary);
  margin: 0;
}

/* ── Grid Section ── */
.ed-grid-header {
  margin-bottom: 24px;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(255,255,255,0.1);
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
  background: var(--bg-surface);
  border: 1px solid rgba(255,255,255,0.05);
  border-radius: 8px;
  overflow: hidden;
  text-decoration: none;
  transition: transform 0.2s, box-shadow 0.2s;
}
.ed-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0,0,0,0.2);
  border-color: rgba(255,255,255,0.1);
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
  padding: 20px;
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
  border: 1px solid rgba(255,255,255,0.1);
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
  background: rgba(255,255,255,0.05);
}
.ed-page-num.active {
  background: var(--primary);
  border-color: var(--primary);
  color: #fff;
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
  border: 3px solid rgba(255,255,255,0.1);
  border-top-color: var(--primary);
  border-radius: 50%;
  margin: 0 auto 20px;
  animation: spin 1s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.journal-error svg {
  color: #ef4444;
  margin-bottom: 16px;
}
</style>
