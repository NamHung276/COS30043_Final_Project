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
      recentPage: 1,
      recentPerPage: 12,
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

    featuredStories() {
      return this.tabFilteredArticles
        .filter(
          (a) => a.urlToImage && a.description && a.description.length > 50,
        )
        .slice(0, 5);
    },

    trendingStories() {
      // Pick 3 articles with images that aren’t already featured
      return this.tabFilteredArticles
        .filter((a) => a.urlToImage && !this.featuredStories.includes(a))
        .slice(0, 3);
    },

    latestHeadlines() {
      return this.tabFilteredArticles
        .filter(
          (a) =>
            !this.featuredStories.includes(a) &&
            !this.trendingStories.includes(a),
        )
        .slice(0, 8);
    },

    editorsPicks() {
      return this.tabFilteredArticles
        .filter(
          (a) =>
            a.urlToImage &&
            !this.featuredStories.includes(a) &&
            !this.trendingStories.includes(a) &&
            !this.latestHeadlines.includes(a),
        )
        .slice(0, 4);
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
        "VR",
        "Technology",
        "Releases",
        "Updates",
        "Hardware",
        "Opinion",
        "Deals",
      ];
    },

    categories() {
      // Only show categories that have at least 1 matching article
      return this.ALL_CATEGORIES.filter((cat) => {
        if (cat === "Latest") return true;
        return this.articles.some((a) => this.articleMatchesCat(a, cat));
      });
    },

    filteredArticles() {
      const term = this.searchTerm.toLowerCase();
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

    totalPages() {
      return Math.ceil(this.filteredArticles.length / this.itemsPerPage);
    },

    paginatedArticles() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      return this.filteredArticles.slice(start, start + this.itemsPerPage);
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

    displayedLatestNews() {
      const excluded = [
        ...this.featuredStories,
        ...this.trendingStories,
        ...this.editorsPicks,
      ];

      return this.tabFilteredArticles.filter((a) => !excluded.includes(a));
    },

    recentTotalPages() {
      return Math.max(
        1,
        Math.ceil(this.displayedLatestNews.length / this.recentPerPage),
      );
    },
    paginatedRecentArticles() {
      const start = (this.recentPage - 1) * this.recentPerPage;
      return this.displayedLatestNews.slice(start, start + this.recentPerPage);
    },
    recentVisiblePages() {
      const total = this.recentTotalPages;
      const cur = this.recentPage;
      const pages = [];
      if (total <= 7) {
        for (let i = 1; i <= total; i++) pages.push(i);
      } else {
        pages.push(1);
        if (cur > 4) pages.push("...");
        const s = Math.max(2, cur - 1);
        const e = Math.min(total - 1, cur + 1);
        for (let i = s; i <= e; i++) pages.push(i);
        if (cur < total - 3) pages.push("...");
        pages.push(total);
      }
      return pages;
    },
  },

  watch: {
    searchTerm() {
      this.currentPage = 1;
    },
    recentPerPage() {
      this.recentPage = 1;
    },
    activeTab() {
      this.recentPage = 1;
    },
  },

  methods: {
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    },
    goToRecentPage(page) {
      if (page >= 1 && page <= this.recentTotalPages) {
        this.recentPage = page;
        this.$nextTick(() => {
          const el = document.getElementById("latest-news-section");
          if (el) {
            const offset = el.getBoundingClientRect().top + window.scrollY - 80;
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
      this.recentPage = 1;
    },
    getReadingTime(description) {
      if (!description) return "2 min read";
      const words = description.trim().split(/\s+/).length;
      // We assume description is just an excerpt, so actual article is longer.
      // E.g. base 2 mins + 1 min per 50 words of description
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
    getCategoryColor(category) {
      const colors = {
        PlayStation: "#003791",
        Xbox: "#107C10",
        Nintendo: "#E60012",
        PC: "#171A21",
        Esports: "#f59e0b",
        Hardware: "#64748b",
        VR: "#06b6d4",
        Mobile: "#10b981",
        Reviews: "#8b5cf6",
        Deals: "#22c55e",
        Industry: "#475569",
        Releases: "#e11d48",
        News: "#3b82f6"
      };
      return colors[category] || "#3b82f6";
    },
    articleMatchesCat(a, cat) {
      const combined = (
        (a.title || "") +
        " " +
        (a.description || "")
      ).toLowerCase();
      if (cat === "Latest") return true;
      if (cat === "Breaking")
        return (
          combined.includes("break") ||
          combined.includes("urgent") ||
          combined.includes("just in")
        );
      if (cat === "Reviews")
        return (
          combined.includes("review") ||
          combined.includes("gameplay") ||
          combined.includes("rating") ||
          combined.includes("score")
        );
      if (cat === "Esports")
        return (
          combined.includes("esport") ||
          combined.includes("tournament") ||
          combined.includes("competition") ||
          combined.includes("league") ||
          combined.includes("rank")
        );
      if (cat === "Industry")
        return (
          combined.includes("developer") ||
          combined.includes("studio") ||
          combined.includes("publisher") ||
          combined.includes("acquisition") ||
          combined.includes("layoff")
        );
      if (cat === "PC")
        return (
          combined.includes("pc game") ||
          combined.includes("steam") ||
          combined.includes("pc gaming") ||
          combined.includes("windows game")
        );
      if (cat === "PlayStation")
        return (
          combined.includes("playstation") ||
          combined.includes("ps5") ||
          combined.includes("ps4") ||
          combined.includes("sony")
        );
      if (cat === "Xbox")
        return (
          combined.includes("xbox") ||
          combined.includes("game pass") ||
          combined.includes("microsoft") ||
          combined.includes("series x")
        );
      if (cat === "Nintendo")
        return (
          combined.includes("nintendo") ||
          combined.includes("switch") ||
          combined.includes("mario") ||
          combined.includes("zelda")
        );
      if (cat === "Mobile")
        return (
          combined.includes("mobile") ||
          combined.includes("ios") ||
          combined.includes("android") ||
          combined.includes("app store")
        );
      if (cat === "Indie")
        return (
          combined.includes("indie") ||
          combined.includes("small studio") ||
          combined.includes("solo dev")
        );
      if (cat === "VR")
        return (
          combined.includes("vr") ||
          combined.includes("virtual reality") ||
          combined.includes("oculus") ||
          combined.includes("meta quest")
        );
      if (cat === "Technology")
        return (
          combined.includes("graphic") ||
          combined.includes("technology") ||
          combined.includes("fps") ||
          combined.includes("ray tracing") ||
          combined.includes("engine")
        );
      if (cat === "Releases")
        return (
          combined.includes("release") ||
          combined.includes("launch") ||
          combined.includes("available now") ||
          combined.includes("out now")
        );
      if (cat === "Updates")
        return (
          combined.includes("update") ||
          combined.includes("patch") ||
          combined.includes("bug fix") ||
          combined.includes("dlc")
        );
      if (cat === "Hardware")
        return (
          combined.includes("gpu") ||
          combined.includes("cpu") ||
          combined.includes("console hardware") ||
          combined.includes("peripheral")
        );
      if (cat === "Opinion")
        return (
          combined.includes("opinion") ||
          combined.includes("editorial") ||
          combined.includes("think") ||
          combined.includes("argument")
        );
      if (cat === "Deals")
        return (
          combined.includes("deal") ||
          combined.includes("sale") ||
          combined.includes("discount") ||
          combined.includes("free game")
        );
      return false;
    },
  },

  async mounted() {
    try {
      const promises = [];

      // 1. Always fetch from NewsAPI
      promises.push(
        newsApi.get("/everything", {
          params: {
            q: 'gaming OR "video games"',
            language: "en",
            sortBy: "publishedAt",
            pageSize: 100,
          },
        }).then(res => {
          const articles = res.data.articles || [];
          return articles.filter(
            (a) => a.title !== "[Removed]" && a.description !== null,
          );
        })
      );

      // 2. If NewsData API key is present, fetch from it too
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

      // 3. Wait for all configured APIs to return
      const settled = await Promise.allSettled(promises);
      
      let combinedArticles = [];
      
      for (const result of settled) {
        if (result.status === "fulfilled" && Array.isArray(result.value)) {
          combinedArticles = combinedArticles.concat(result.value);
        } else if (result.status === "rejected") {
          console.warn("An API source failed to fetch:", result.reason);
        }
      }

      if (combinedArticles.length === 0) {
        this.error = "Failed to load live news from any source. Please try again later.";
      } else {
        // Sort combined articles by date descending
        this.articles = combinedArticles.sort((a, b) => {
          return new Date(b.publishedAt).getTime() - new Date(a.publishedAt).getTime();
        });
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
  <div class="ln-page">
    <!-- Header -->
    <div class="ln-page-header">
      <div class="container ln-header-content">
        <div class="ln-title-row">
          <div class="ln-title-col">
            <div class="ln-live-indicator" aria-hidden="true">
              <span class="ln-live-dot"></span>
              LIVE
            </div>
            <h1 class="ln-title">Gaming News</h1>
            <div class="ln-meta-row">
              <span v-if="!loading" class="ln-count-badge"
                >{{ articles.length }} stories</span
              >
              <span class="ln-last-updated">Updated {{ lastUpdated }}</span>
            </div>
          </div>
          <div class="ln-search-wrap">
            <svg
              class="ln-search-icon"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="11" cy="11" r="8" />
              <line x1="21" y1="21" x2="16.65" y2="16.65" />
            </svg>
            <input
              v-model="searchTerm"
              type="text"
              class="ln-search-input"
              placeholder="Search stories..."
              aria-label="Search"
            />
          </div>
        </div>

        <!-- Category Navigation Bar -->
        <nav class="ln-categories-section" aria-label="News categories">
          <div class="ln-categories-row">
            <button
              v-for="cat in categories"
              :key="cat"
              class="ln-category-tab"
              :class="{ active: activeTab === cat }"
              @click="setActiveTab(cat)"
              :aria-pressed="activeTab === cat"
            >
              {{ cat }}
            </button>
          </div>
        </nav>
      </div>
    </div>

    <!-- Content -->
    <div class="container ln-content">
      <div v-if="loading" class="ln-skeleton-wrapper">
        <div class="ln-skeleton-hero"></div>
        <div class="ln-skeleton-list">
          <div v-for="n in 6" :key="n" class="ln-skeleton-item"></div>
        </div>
      </div>

      <div v-else-if="error" class="ln-state">
        <svg
          width="48"
          height="48"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="1.5"
        >
          <circle cx="12" cy="12" r="10" />
          <path d="M12 8v4m0 4h.01" />
        </svg>
        <h3>Couldn't load news</h3>
        <p>{{ error }}</p>
      </div>

      <template v-else>
        <!-- SEARCH RESULTS -->
        <section v-if="searchTerm" class="ln-section">
          <div class="ln-section-title-wrap">
            <h2 class="ln-section-title">
              Search Results for "{{ searchTerm }}"
            </h2>
            <span class="ln-count-text"
              >{{ filteredArticles.length }} found</span
            >
          </div>
          <div class="ln-search-grid">
            <a
              v-for="article in paginatedArticles"
              :key="article.url"
              :href="article.url"
              target="_blank"
              rel="noopener noreferrer"
              class="ln-search-card"
            >
              <div class="ln-search-img-wrap">
                <img
                  v-if="article.urlToImage"
                  v-lazy-img="article.urlToImage"
                  :alt="article.title"
                  class="ln-search-img"
                />
                <div class="ln-search-overlay"></div>
                <div 
                  class="ln-category-badge-small" 
                  :style="{ backgroundColor: getCategoryColor(getArticleCategory(article)) }"
                >
                  {{ getArticleCategory(article) }}
                </div>
              </div>
              <div class="ln-search-card-body">
                <h4 class="ln-search-title">{{ article.title }}</h4>
                <div class="ln-search-meta">
                  <span class="ln-search-source">{{ article.source?.name }}</span>
                  <span class="ln-meta-dot">•</span>
                  <span class="ln-search-time">{{ timeAgo(article.publishedAt) }}</span>
                </div>
              </div>
            </a>
          </div>
          <nav v-if="totalPages > 1" class="ln-pagination">
            <button
              class="ln-page-btn"
              :disabled="currentPage === 1"
              @click="goToPage(currentPage - 1)"
            >
              Previous
            </button>
            <div class="ln-page-numbers">
              <template v-for="(page, i) in visiblePages" :key="i">
                <span v-if="page === '...'" class="ln-page-ellipsis"
                  >&#8230;</span
                >
                <button
                  v-else
                  class="ln-page-num"
                  :class="{ active: currentPage === page }"
                  @click="goToPage(page)"
                >
                  {{ page }}
                </button>
              </template>
            </div>
            <button
              class="ln-page-btn"
              :disabled="currentPage === totalPages"
              @click="goToPage(currentPage + 1)"
            >
              Next
            </button>
          </nav>
        </section>

        <!-- MAIN EDITORIAL LAYOUT -->
        <div v-else>
          <!-- ══ HERO: FEATURED STORY + LATEST HEADLINES ══ -->
          <section class="ln-hero-section">
            <div class="ln-hero-grid">
              <!-- Left: Big Featured Story -->
              <div class="ln-featured-col">
                <a
                  v-if="featuredStories[0]"
                  :href="featuredStories[0].url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="ln-featured-main"
                >
                  <div class="ln-featured-img-wrap">
                    <img
                      v-if="featuredStories[0].urlToImage"
                      v-lazy-img="featuredStories[0].urlToImage"
                      :alt="featuredStories[0].title"
                      class="ln-featured-img"
                    />
                    <div class="ln-featured-overlay"></div>
                    <div 
                      class="ln-category-badge" 
                      :style="{ backgroundColor: getCategoryColor(getArticleCategory(featuredStories[0])) }"
                    >
                      {{ getArticleCategory(featuredStories[0]) }}
                    </div>
                    <div class="ln-featured-text-overlay">
                      <h2 class="ln-featured-title">
                        {{ featuredStories[0].title }}
                      </h2>
                      <p class="ln-featured-desc">
                        {{ featuredStories[0].description }}
                      </p>
                      <div class="ln-featured-meta">
                        <span class="ln-meta-source">{{ featuredStories[0].source?.name }}</span>
                        <span class="ln-meta-dot">•</span>
                        <span class="ln-meta-time">{{ timeAgo(featuredStories[0].publishedAt) }}</span>
                        <span class="ln-meta-dot">•</span>
                        <span class="ln-meta-read">{{ getReadingTime(featuredStories[0].description) }}</span>
                      </div>
                    </div>
                  </div>
                </a>

                <!-- Sub-featured stories below hero -->
                <div class="ln-sub-featured-row">
                  <a
                    v-for="article in featuredStories.slice(1, 4)"
                    :key="article.url"
                    :href="article.url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="ln-sub-card"
                  >
                    <div class="ln-sub-img-wrap">
                      <img
                        v-if="article.urlToImage"
                        v-lazy-img="article.urlToImage"
                        :alt="article.title"
                        class="ln-sub-img"
                      />
                      <div 
                        class="ln-category-badge-small" 
                        :style="{ backgroundColor: getCategoryColor(getArticleCategory(article)) }"
                      >
                        {{ getArticleCategory(article) }}
                      </div>
                    </div>
                    <div class="ln-sub-body">
                      <h4 class="ln-sub-title">{{ article.title }}</h4>
                      <div class="ln-sub-meta">
                        <span class="ln-sub-time">{{ timeAgo(article.publishedAt) }}</span>
                      </div>
                    </div>
                  </a>
                </div>
              </div>

              <!-- Right: Latest Headlines list -->
              <div class="ln-headlines-col">
                <div class="ln-headlines-header">
                  <span class="ln-headlines-label">⚡ Latest</span>
                </div>
                <div class="ln-headlines-list">
                  <a
                    v-for="(article, i) in latestHeadlines"
                    :key="article.url"
                    :href="article.url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="ln-headline-item"
                  >
                    <span class="ln-headline-num">{{
                      String(i + 1).padStart(2, "0")
                    }}</span>
                    <div class="ln-headline-content">
                      <span class="ln-headline-text">{{ article.title }}</span>
                      <div class="ln-headline-meta">
                        <span class="ln-headline-source">{{
                          article.source?.name
                        }}</span>
                        <span class="ln-headline-dot">·</span>
                        <span class="ln-headline-time">{{
                          timeAgo(article.publishedAt)
                        }}</span>
                      </div>
                    </div>
                  </a>
                </div>
              </div>
            </div>
          </section>

          <!-- ══ TRENDING ══ -->
          <section v-if="trendingStories.length" class="ln-section">
            <div class="ln-section-title-wrap">
              <h2 class="ln-section-title">🔥 Trending</h2>
            </div>
            <div class="ln-trending-grid">
              <a
                v-for="article in trendingStories"
                :key="article.url"
                :href="article.url"
                target="_blank"
                rel="noopener noreferrer"
                class="ln-trending-card"
              >
                <div class="ln-trending-img-wrap">
                  <img
                    v-if="article.urlToImage"
                    v-lazy-img="article.urlToImage"
                    :alt="article.title"
                    class="ln-trending-img"
                  />
                  <div class="ln-trending-overlay"></div>
                  <div 
                    class="ln-category-badge-small" 
                    :style="{ backgroundColor: getCategoryColor(getArticleCategory(article)) }"
                  >
                    {{ getArticleCategory(article) }}
                  </div>
                </div>
                <div class="ln-trending-body">
                  <h4 class="ln-trending-title">{{ article.title }}</h4>
                  <div class="ln-trending-meta">
                    <span class="ln-trending-source">{{ article.source?.name }}</span>
                    <span class="ln-meta-dot">•</span>
                    <span class="ln-trending-time">{{ timeAgo(article.publishedAt) }}</span>
                  </div>
                </div>
              </a>
            </div>
          </section>

          <!-- ══ EDITOR'S PICKS ══ -->
          <section v-if="editorsPicks.length" class="ln-section">
            <div class="ln-section-title-wrap">
              <h2 class="ln-section-title">⭐ Editor's Picks</h2>
            </div>
            <div class="ln-picks-grid">
              <a
                v-for="article in editorsPicks"
                :key="article.url"
                :href="article.url"
                target="_blank"
                rel="noopener noreferrer"
                class="ln-pick-card"
              >
                <div class="ln-pick-img-wrap">
                  <img
                    v-if="article.urlToImage"
                    v-lazy-img="article.urlToImage"
                    :alt="article.title"
                    class="ln-pick-img"
                  />
                  <div class="ln-pick-overlay"></div>
                  <div 
                    class="ln-category-badge-small" 
                    :style="{ backgroundColor: getCategoryColor(getArticleCategory(article)) }"
                  >
                    {{ getArticleCategory(article) }}
                  </div>
                </div>
                <div class="ln-pick-body">
                  <h4 class="ln-pick-title">{{ article.title }}</h4>
                  <div class="ln-pick-meta">
                    <span class="ln-pick-source">{{ article.source?.name }}</span>
                    <span class="ln-meta-dot">•</span>
                    <span class="ln-pick-time">{{ timeAgo(article.publishedAt) }}</span>
                  </div>
                </div>
              </a>
            </div>
          </section>

          <!-- ══ LATEST / CATEGORY NEWS LIST ══ -->
          <section id="latest-news-section" class="ln-section">
            <div class="ln-section-title-wrap">
              <h2 class="ln-section-title">
                📰 {{ activeTab === "Latest" ? "Latest Stories" : activeTab }}
              </h2>
              <span class="ln-count-text"
                >{{ displayedLatestNews.length }} stories</span
              >
            </div>

            <div
              v-if="paginatedRecentArticles.length === 0"
              class="ln-empty-cat"
            >
              <p>No stories found in this category yet.</p>
            </div>

            <div class="ln-list-grid" v-else>
              <a
                v-for="article in paginatedRecentArticles"
                :key="article.url"
                :href="article.url"
                target="_blank"
                rel="noopener noreferrer"
                class="ln-list-item stagger-item"
              >
                <div class="ln-list-img-wrap">
                  <img
                    v-if="article.urlToImage"
                    v-lazy-img="article.urlToImage"
                    :alt="article.title"
                    class="ln-list-img"
                  />
                  <div v-else class="ln-list-img-placeholder">
                    <svg
                      width="24"
                      height="24"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path
                        d="M4 22h16a2 2 0 002-2V4a2 2 0 00-2-2H8L2 8v12a2 2 0 002 2z"
                      />
                    </svg>
                  </div>
                  <div 
                    class="ln-category-badge-small" 
                    :style="{ backgroundColor: getCategoryColor(getArticleCategory(article)) }"
                  >
                    {{ getArticleCategory(article) }}
                  </div>
                </div>
                <div class="ln-list-body">
                  <div class="ln-list-meta-row">
                    <span class="ln-list-source">{{ article.source?.name }}</span>
                    <span class="ln-meta-dot">•</span>
                    <span class="ln-list-time">{{ timeAgo(article.publishedAt) }}</span>
                    <span class="ln-meta-dot ln-hide-mobile">•</span>
                    <span class="ln-list-read ln-hide-mobile">{{ getReadingTime(article.description) }}</span>
                  </div>
                  <h3 class="ln-list-title">{{ article.title }}</h3>
                  <p class="ln-list-desc">
                    {{ article.description?.slice(0, 160) }}…
                  </p>
                </div>
                <div class="ln-list-read-btn">
                  Read
                  <svg
                    width="14"
                    height="14"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                </div>
              </a>
            </div>

            <nav v-if="recentTotalPages > 1" class="ln-pagination">
              <button
                class="ln-page-btn"
                :disabled="recentPage === 1"
                @click="goToRecentPage(recentPage - 1)"
              >
                Previous
              </button>
              <div class="ln-page-numbers">
                <template v-for="(page, i) in recentVisiblePages" :key="i">
                  <span v-if="page === '...'" class="ln-page-ellipsis"
                    >&#8230;</span
                  >
                  <button
                    v-else
                    class="ln-page-num"
                    :class="{ active: recentPage === page }"
                    @click="goToRecentPage(page)"
                  >
                    {{ page }}
                  </button>
                </template>
              </div>
              <button
                class="ln-page-btn"
                :disabled="recentPage === recentTotalPages"
                @click="goToRecentPage(recentPage + 1)"
              >
                Next
              </button>
            </nav>
          </section>
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
/* ── Page ── */
.ln-page {
  min-height: 100vh;
  background: var(--bg-deep);
  color: var(--text-primary);
  font-family: var(--font-family);
}
.container {
  max-width: 1300px;
  margin: 0 auto;
  padding: 0 20px;
}

/* ── Header ── */
.ln-page-header {
  background: var(--bg-base);
  padding: 20px 0 0;
  border-bottom: 1px solid var(--border-glass);
  position: sticky;
  top: 62px;
  z-index: 90;
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
}
.ln-title-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 20px;
  flex-wrap: wrap;
  padding-bottom: 14px;
}
.ln-live-indicator {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.65rem;
  font-weight: 800;
  letter-spacing: 0.1em;
  color: #ef4444;
  text-transform: uppercase;
  margin-bottom: 4px;
}
.ln-live-dot {
  width: 7px;
  height: 7px;
  background: #ef4444;
  border-radius: 50%;
  animation: pulse-dot 1.5s ease-in-out infinite;
}
@keyframes pulse-dot {
  0%,
  100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.4;
    transform: scale(0.7);
  }
}
.ln-title {
  font-size: 1.6rem;
  font-weight: 900;
  margin: 0 0 4px;
  line-height: 1;
  letter-spacing: -0.02em;
}
.ln-meta-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-top: 4px;
}
.ln-count-badge {
  font-size: 0.72rem;
  font-weight: 700;
  padding: 2px 9px;
  border-radius: 20px;
  background: rgba(6, 182, 212, 0.15);
  color: #06b6d4;
}
.ln-last-updated {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.ln-search-wrap {
  display: flex;
  align-items: center;
  position: relative;
  width: 260px;
  max-width: 100%;
  margin-top: 4px;
}
.ln-search-icon {
  position: absolute;
  left: 12px;
  color: var(--text-muted);
  pointer-events: none;
}
.ln-search-input {
  width: 100%;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 8px;
  color: var(--text-primary);
  padding: 9px 14px 9px 36px;
  font-size: 0.88rem;
  outline: none;
  transition: border-color 0.2s;
  font-family: var(--font-family);
}
.ln-search-input:focus {
  border-color: #06b6d4;
}

/* ── Category Nav ── */
.ln-categories-section {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  padding: 0;
}
.ln-categories-row {
  display: flex;
  align-items: center;
  gap: 0;
  overflow-x: auto;
  scrollbar-width: none;
}
.ln-categories-row::-webkit-scrollbar {
  display: none;
}
.ln-category-tab {
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: var(--text-secondary);
  font-size: 0.8rem;
  font-weight: 700;
  font-family: var(--font-family);
  cursor: pointer;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  white-space: nowrap;
  padding: 10px 14px;
  transition:
    color 0.2s,
    border-color 0.2s;
  position: relative;
}
.ln-category-tab:hover {
  color: var(--text-primary);
}
.ln-category-tab.active {
  color: #06b6d4;
  border-bottom-color: #06b6d4;
}

/* ── Content ── */
.ln-content {
  padding-top: 28px;
  padding-bottom: 60px;
}
.ln-section {
  margin-bottom: 44px;
}
.ln-section-title-wrap {
  margin-bottom: 18px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  padding-bottom: 10px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.ln-section-title {
  font-size: 1.1rem;
  font-weight: 800;
  margin: 0;
  color: var(--text-primary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.ln-count-text {
  font-size: 0.75rem;
  color: var(--text-muted);
}

/* ── Hero Grid ── */
.ln-hero-section {
  margin-bottom: 40px;
}
.ln-hero-grid {
  display: grid;
  grid-template-columns: 3fr 2fr;
  gap: 24px;
}
@media (max-width: 900px) {
  .ln-hero-grid {
    grid-template-columns: 1fr;
  }
}

/* Featured story — image-as-background approach */
.ln-featured-main {
  display: block;
  text-decoration: none;
  border-radius: 14px;
  overflow: hidden;
  position: relative;
  background: #0c1120;
  border: 1px solid rgba(255, 255, 255, 0.06);
  transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1), border-color 0.3s;
  margin-bottom: 14px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
}
.ln-featured-main:hover {
  transform: translateY(-4px);
  border-color: rgba(6, 182, 212, 0.4);
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.6);
}
.ln-featured-img-wrap {
  position: relative;
  aspect-ratio: 16/9;
  width: 100%;
  overflow: hidden;
}
.ln-featured-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.6s cubic-bezier(0.25, 0.8, 0.25, 1);
  display: block;
}
.ln-featured-main:hover .ln-featured-img {
  transform: scale(1.03);
}
.ln-featured-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(10, 14, 25, 1) 0%,
    rgba(10, 14, 25, 0.8) 30%,
    transparent 70%
  );
}
.ln-category-badge {
  position: absolute;
  top: 20px;
  left: 20px;
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #fff;
  padding: 4px 10px;
  border-radius: 4px;
  z-index: 10;
  box-shadow: 0 2px 8px rgba(0,0,0,0.5);
}
.ln-category-badge-small {
  position: absolute;
  top: 10px;
  left: 10px;
  font-size: 0.65rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #fff;
  padding: 3px 8px;
  border-radius: 4px;
  z-index: 10;
  box-shadow: 0 2px 6px rgba(0,0,0,0.5);
}
.ln-featured-text-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 32px;
  z-index: 10;
}
.ln-featured-title {
  font-size: clamp(1.4rem, 3vw, 2.2rem);
  font-weight: 900;
  color: #fff;
  margin: 0 0 10px;
  line-height: 1.15;
  letter-spacing: -0.02em;
  text-shadow: 0 2px 16px rgba(0, 0, 0, 0.8);
}
.ln-featured-desc {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.8);
  margin: 0 0 16px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-shadow: 0 1px 8px rgba(0, 0, 0, 0.6);
}
.ln-featured-meta {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 0.8rem;
  font-weight: 600;
}
.ln-meta-source {
  color: #06b6d4;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.ln-meta-dot {
  color: rgba(255, 255, 255, 0.3);
}
.ln-meta-time, .ln-meta-read {
  color: rgba(255, 255, 255, 0.6);
}

/* Sub-featured row below hero */
.ln-sub-featured-row {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 14px;
}
@media (max-width: 600px) {
  .ln-sub-featured-row {
    grid-template-columns: 1fr;
  }
}
.ln-sub-card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: var(--bg-surface);
  transition: transform 0.25s, border-color 0.25s;
}
.ln-sub-card:hover {
  border-color: rgba(6, 182, 212, 0.4);
  transform: translateY(-3px);
}
.ln-sub-img-wrap {
  position: relative;
  aspect-ratio: 16/9;
  width: 100%;
  overflow: hidden;
}
.ln-sub-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s ease;
}
.ln-sub-card:hover .ln-sub-img {
  transform: scale(1.05);
}
.ln-sub-body {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}
.ln-sub-title {
  font-size: 0.9rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.35;
  letter-spacing: -0.01em;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ln-sub-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: auto;
}
.ln-sub-time {
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* Latest Headlines */
.ln-headlines-col {
  display: flex;
  flex-direction: column;
}
.ln-headlines-header {
  padding: 0 0 10px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  margin-bottom: 4px;
}
.ln-headlines-label {
  font-size: 0.75rem;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-primary);
}
.ln-headlines-list {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.ln-headline-item {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 13px 0;
  text-decoration: none;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  transition: all 0.2s;
}
.ln-headline-item:hover .ln-headline-text {
  color: #06b6d4;
}
.ln-headline-num {
  font-size: 1.4rem;
  font-weight: 900;
  color: var(--text-muted);
  opacity: 0.3;
  flex-shrink: 0;
  width: 32px;
  line-height: 1;
  margin-top: 2px;
}
.ln-headline-content {
  display: flex;
  flex-direction: column;
  gap: 5px;
  flex: 1;
}
.ln-headline-text {
  font-size: 0.92rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  transition: color 0.2s;
}
.ln-headline-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}
.ln-headline-source {
  font-size: 0.7rem;
  font-weight: 700;
  color: #06b6d4;
  text-transform: uppercase;
}
.ln-headline-dot {
  color: var(--text-muted);
  opacity: 0.5;
  font-size: 0.8rem;
}
.ln-headline-time {
  font-size: 0.7rem;
  color: var(--text-muted);
}

/* ── Trending ── */
.ln-trending-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
@media (max-width: 700px) {
  .ln-trending-grid {
    grid-template-columns: 1fr;
  }
}
.ln-trending-card {
  border-radius: 12px;
  overflow: hidden;
  text-decoration: none;
  background: var(--bg-surface);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: transform 0.25s, border-color 0.25s;
  display: flex;
  flex-direction: column;
}
.ln-trending-card:hover {
  transform: translateY(-4px);
  border-color: rgba(6, 182, 212, 0.4);
}
.ln-trending-img-wrap {
  position: relative;
  aspect-ratio: 16/9;
  width: 100%;
  overflow: hidden;
}
.ln-trending-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s ease;
}
.ln-trending-card:hover .ln-trending-img {
  transform: scale(1.05);
}
.ln-trending-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(5, 7, 15, 0.4), transparent 60%);
}
.ln-trending-body {
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
}
.ln-trending-title {
  font-size: 1.05rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.35;
  letter-spacing: -0.01em;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ln-trending-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: auto;
}
.ln-trending-source {
  font-size: 0.72rem;
  font-weight: 700;
  color: #06b6d4;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.ln-trending-time {
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* ── Editor's Picks ── */
.ln-picks-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
}
@media (max-width: 1000px) {
  .ln-picks-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
@media (max-width: 600px) {
  .ln-picks-grid {
    grid-template-columns: 1fr;
  }
}
.ln-pick-card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-surface);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: transform 0.22s, border-color 0.22s;
}
.ln-pick-card:hover {
  transform: translateY(-3px);
  border-color: rgba(6, 182, 212, 0.4);
}
.ln-pick-img-wrap {
  position: relative;
  overflow: hidden;
  aspect-ratio: 16/9;
  width: 100%;
}
.ln-pick-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s ease;
}
.ln-pick-card:hover .ln-pick-img {
  transform: scale(1.05);
}
.ln-pick-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(5, 7, 15, 0.4), transparent);
}
.ln-pick-body {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  justify-content: space-between;
}
.ln-pick-title {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.35;
  letter-spacing: -0.01em;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ln-pick-meta {
  display: flex;
  align-items: center;
  gap: 6px;
}
.ln-pick-source {
  font-size: 0.68rem;
  font-weight: 700;
  color: #06b6d4;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}
.ln-pick-time {
  font-size: 0.72rem;
  color: var(--text-muted);
}

/* ── Latest News List ── */
.ln-list-grid {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.ln-empty-cat {
  padding: 40px 0;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.9rem;
}
.ln-list-item {
  display: flex;
  gap: 20px;
  padding: 16px;
  text-decoration: none;
  background: var(--bg-surface);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.04);
  transition: all 0.2s ease;
  align-items: flex-start;
}
.ln-list-item:hover {
  background: var(--bg-glass-hover);
  border-color: rgba(6, 182, 212, 0.3);
  transform: translateX(4px);
}
@media (max-width: 600px) {
  .ln-list-item {
    flex-direction: column;
    align-items: stretch;
  }
}
.ln-list-img-wrap {
  width: 240px;
  aspect-ratio: 16/9;
  flex-shrink: 0;
  border-radius: 8px;
  overflow: hidden;
  background: #0f172a;
  position: relative;
}
@media (max-width: 600px) {
  .ln-list-img-wrap {
    width: 100%;
    aspect-ratio: 16/9;
  }
}
.ln-list-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.ln-list-item:hover .ln-list-img {
  transform: scale(1.05);
}
.ln-list-img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--border-glass);
}
.ln-list-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
  min-width: 0;
}
.ln-list-meta-row {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.ln-list-source {
  font-size: 0.72rem;
  font-weight: 800;
  color: #06b6d4;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.ln-list-time, .ln-list-read {
  font-size: 0.75rem;
  color: var(--text-muted);
}
@media (max-width: 480px) {
  .ln-hide-mobile {
    display: none;
  }
}
.ln-list-title {
  font-size: 1.25rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.35;
  letter-spacing: -0.01em;
}
.ln-list-desc {
  font-size: 0.95rem;
  color: var(--text-secondary);
  margin: 0;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ln-list-read-btn {
  font-size: 0.85rem;
  font-weight: 700;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  gap: 4px;
  transition: color 0.2s;
  flex-shrink: 0;
  margin-top: 10px;
}
.ln-list-item:hover .ln-list-read-btn {
  color: #06b6d4;
}

/* ── Skeleton ── */
.ln-skeleton-wrapper {
  display: flex;
  flex-direction: column;
  gap: 24px;
  padding-top: 20px;
}
.ln-skeleton-hero {
  height: 440px;
  border-radius: 14px;
  background: linear-gradient(
    90deg,
    var(--bg-glass) 25%,
    rgba(255, 255, 255, 0.05) 50%,
    var(--bg-glass) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
.ln-skeleton-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.ln-skeleton-item {
  height: 120px;
  border-radius: 12px;
  background: linear-gradient(
    90deg,
    var(--bg-glass) 25%,
    rgba(255, 255, 255, 0.05) 50%,
    var(--bg-glass) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.4s infinite;
}
@keyframes shimmer {
  to {
    background-position: -200% 0;
  }
}

/* ── Search Results ── */
.ln-search-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 16px;
}
.ln-search-card {
  display: flex;
  flex-direction: column;
  text-decoration: none;
  border-radius: 10px;
  overflow: hidden;
  background: var(--bg-surface);
  border: 1px solid rgba(255, 255, 255, 0.05);
  transition: transform 0.2s, border-color 0.2s;
}
.ln-search-card:hover {
  transform: translateY(-4px);
  border-color: rgba(6, 182, 212, 0.4);
}
.ln-search-img-wrap {
  position: relative;
  aspect-ratio: 16/9;
  width: 100%;
  overflow: hidden;
}
.ln-search-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.ln-search-card:hover .ln-search-img {
  transform: scale(1.05);
}
.ln-search-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, rgba(5, 7, 15, 0.3), transparent);
}
.ln-search-card-body {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  flex: 1;
  justify-content: space-between;
}
.ln-search-title {
  font-size: 0.95rem;
  font-weight: 800;
  color: var(--text-primary);
  margin: 0;
  line-height: 1.35;
  letter-spacing: -0.01em;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ln-search-meta {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 0.72rem;
  color: var(--text-muted);
}
.ln-search-source {
  color: #06b6d4;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* ── Error State ── */
.ln-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 80px 0;
  color: var(--text-muted);
  text-align: center;
}
.ln-state h3 {
  color: var(--text-secondary);
  margin: 0;
}
.ln-state p {
  margin: 0;
  font-size: 0.9rem;
}

/* ── Pagination ── */
.ln-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  margin-top: 36px;
  flex-wrap: wrap;
}
.ln-page-btn {
  padding: 7px 16px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: var(--bg-surface);
  color: var(--text-primary);
  font-size: 0.88rem;
  font-weight: 600;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all 0.2s;
}
.ln-page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
.ln-page-btn:not(:disabled):hover {
  border-color: #06b6d4;
  color: #06b6d4;
}
.ln-page-numbers {
  display: flex;
  gap: 5px;
}
.ln-page-num {
  width: 34px;
  height: 34px;
  border-radius: 6px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: var(--bg-surface);
  color: var(--text-secondary);
  font-size: 0.88rem;
  font-weight: 600;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all 0.2s;
}
.ln-page-num:hover {
  border-color: #06b6d4;
  color: #06b6d4;
}
.ln-page-num.active {
  background: #06b6d4;
  color: #fff;
  border-color: #06b6d4;
}
.ln-page-ellipsis {
  color: var(--text-muted);
  padding: 0 4px;
}

/* ── Animations ── */
.stagger-item {
  animation: fadeInUp 0.4s ease forwards;
  opacity: 0; /* Base state to ensure it starts hidden before animation */
}
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.ln-list-item:nth-child(1) {
  animation-delay: 0.04s;
}
.ln-list-item:nth-child(2) {
  animation-delay: 0.08s;
}
.ln-list-item:nth-child(3) {
  animation-delay: 0.12s;
}
.ln-list-item:nth-child(4) {
  animation-delay: 0.16s;
}
.ln-list-item:nth-child(5) {
  animation-delay: 0.2s;
}
.ln-list-item:nth-child(n + 6) {
  animation-delay: 0.24s;
}
</style>
