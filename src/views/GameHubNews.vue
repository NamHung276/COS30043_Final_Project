<script>
import newsData from "../data/news.json";
import LikeButton from "../components/LikeButton.vue";
import { auth, db } from "../firebase";
import { onAuthStateChanged } from "firebase/auth";
import { collection, getDocs, addDoc, query, where, Timestamp } from "firebase/firestore";

export default {
  components: { LikeButton },

  data() {
    return {
      allNews: [],
      currentUser: null,
      searchTerm: "",
      selectedCategory: "All",
      currentPage: 1,
      itemsPerPage: 6,
      loadingUserNews: true,
      expandedCategory: null,
    };
  },

  beforeUnmount() {
    if (this.unsubscribe) {
      this.unsubscribe();
    }
  },

  mounted() {
    this.unsubscribe = onAuthStateChanged(auth, (user) => {
      this.currentUser = user;
    });
    this.seedAndLoadNews();
  },

  computed: {
    scoredNews() {
      // strictly sort by date descending
      const sorted = [...this.allNews].sort((a, b) => {
        const dateA = a.createdAt?.seconds ? a.createdAt.seconds * 1000 : new Date(a.date).getTime();
        const dateB = b.createdAt?.seconds ? b.createdAt.seconds * 1000 : new Date(b.date).getTime();
        return dateB - dateA;
      });

      // Calculate trending score for each
      const now = Date.now();
      return sorted.map(item => {
        const itemDate = item.createdAt?.seconds ? item.createdAt.seconds * 1000 : new Date(item.date).getTime();
        const daysOld = Math.max(1, (now - itemDate) / (1000 * 60 * 60 * 24));
        const recencyBonus = Math.max(0, 100 - (daysOld * 2));
        const likes = item.likes || 0;
        const views = item.views || 0;
        
        return {
          ...item,
          trendingScore: (likes * 5) + (views * 1) + recencyBonus
        };
      });
    },

    // Featured story (highest score)
    featuredStory() {
      if(this.scoredNews.length === 0) return null;
      return [...this.scoredNews].sort((a, b) => b.trendingScore - a.trendingScore)[0];
    },

    // Top trending stories (top 7 scores, excluding featured)
    trendingStories() {
      if(this.scoredNews.length === 0) return [];
      const featuredId = this.featuredStory?.id;
      return [...this.scoredNews]
        .filter(item => item.id !== featuredId)
        .sort((a, b) => b.trendingScore - a.trendingScore)
        .slice(0, 7);
    },

    // All categories
    categories() {
      const cats = new Set(this.scoredNews.map((item) => item.category));
      return Array.from(cats).sort();
    },

    filteredNews() {
      const term = this.searchTerm.toLowerCase();
      return this.scoredNews.filter((item) => {
        const matchesSearch =
          (item.title && item.title.toLowerCase().includes(term)) ||
          (item.content && item.content.toLowerCase().includes(term)) ||
          (item.category && item.category.toLowerCase().includes(term));
        const matchesCategory =
          this.selectedCategory === "All" ||
          item.category === this.selectedCategory;
        return matchesSearch && matchesCategory;
      });
    },

    totalPages() {
      return Math.ceil(this.filteredNews.length / this.itemsPerPage);
    },

    paginatedNews() {
      const start = (this.currentPage - 1) * this.itemsPerPage;
      return this.filteredNews.slice(start, start + this.itemsPerPage);
    },
  },

  watch: {
    searchTerm() {
      this.currentPage = 1;
    },
    selectedCategory() {
      this.currentPage = 1;
    },
  },

  methods: {
    async seedAndLoadNews() {
      this.loadingUserNews = true;
      try {
        const q = query(collection(db, "news"), where("isOfficial", "==", true));
        const snap = await getDocs(q);
        
        // Seed official data exactly once if missing
        if (snap.empty) {
          console.log("Seeding official news to Firestore...");
          for (const item of newsData) {
            await addDoc(collection(db, "news"), {
              title: item.title,
              content: item.content,
              category: item.category,
              image: item.image,
              isOfficial: true,
              authorName: "GameHub Staff",
              date: item.date,
              createdAt: Timestamp.fromDate(new Date(item.date)),
              likes: Math.floor(Math.random() * 500),
              views: Math.floor(Math.random() * 5000),
              comments: Math.floor(Math.random() * 50)
            });
          }
        }
        
        // Load all unified news
        const allSnap = await getDocs(collection(db, "news"));
        this.allNews = allSnap.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        
      } catch (error) {
        console.error("Error seeding/loading news:", error);
      } finally {
        this.loadingUserNews = false;
      }
    },
    goToPage(page) {
      if (page >= 1 && page <= this.totalPages) {
        this.currentPage = page;
        window.scrollTo({ top: 0, behavior: "smooth" });
      }
    },
    toggleCategory(category) {
      this.expandedCategory =
        this.expandedCategory === category ? null : category;
    },
    getCategoryColor(category) {
      const map = {
        FPS: {
          bg: "rgba(239,68,68,0.15)",
          text: "#fca5a5",
          border: "rgba(239,68,68,0.3)",
        },
        MOBA: {
          bg: "rgba(16,185,129,0.15)",
          text: "#6ee7b7",
          border: "rgba(16,185,129,0.3)",
        },
        RPG: {
          bg: "rgba(245,158,11,0.15)",
          text: "#fde68a",
          border: "rgba(245,158,11,0.3)",
        },
        MMO: {
          bg: "rgba(6,182,212,0.15)",
          text: "#67e8f9",
          border: "rgba(6,182,212,0.3)",
        },
      };
      return (
        map[category] || {
          bg: "rgba(124,58,237,0.15)",
          text: "#c4b5fd",
          border: "rgba(124,58,237,0.3)",
        }
      );
    },
    getCategoryEmoji(category) {
      const map = {
        FPS: '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><circle cx="12" cy="12" r="1"/><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2z"/></svg>',
        MOBA: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.46 15.46 2 4"/><polyline points="13.46 15.46 17 19 2 4"/></svg>',
        RPG: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg>',
        MMO: '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>',
        Esports:
          '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="6 5 18 12 6 19 6 5"/></svg>',
        Strategy:
          '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 3c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3zm0 14.2c-2.5 0-4.71-1.28-6-3.22.03-1.99 4-3.08 6-3.08s5.97 1.09 6 3.08c-1.29 1.94-3.5 3.22-6 3.22z"/></svg>',
      };
      return (
        map[category] ||
        '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="1"/><circle cx="12" cy="5" r="1"/><circle cx="12" cy="19" r="1"/></svg>'
      );
    },
    detailLink(item) {
      return item.isUserPost
        ? `/gamehub-news/user/${item.id}`
        : `/gamehub-news/${item.id}`;
    },
  },
};
</script>

<template>
  <div class="ghn-page">
    <!-- ══ Header ══ -->
    <div class="ghn-page-header">
      <div class="ghn-header-bg" aria-hidden="true"></div>
      <div class="container ghn-header-content">
        <div class="ghn-title-row">
          <span class="ghn-title-icon" aria-hidden="true">
            <svg
              width="26"
              height="26"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
              <polyline points="14,2 14,8 20,8" />
              <line x1="16" y1="13" x2="8" y2="13" />
              <line x1="16" y1="17" x2="8" y2="17" />
              <polyline points="10,9 9,9 8,9" />
            </svg>
          </span>
          <div style="flex: 1">
            <h1 class="ghn-title">GameHub News</h1>
            <p class="ghn-subtitle">
              Gaming updates, esports stories, launches &amp; industry news
            </p>
          </div>
          <router-link
            to="/gamehub-news/create"
            class="ghn-post-btn"
            aria-label="Post a new article"
          >
            <svg
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2.5"
              stroke-linecap="round"
            >
              <path d="M12 5v14M5 12h14" />
            </svg>
            Post Article
          </router-link>
        </div>

        <!-- Search Bar -->
        <div class="ghn-filter-panel">
          <div class="ghn-categories-bar">
            <button 
              class="ghn-cat-tab" 
              :class="{ active: selectedCategory === 'All' }"
              @click="selectedCategory = 'All'"
            >
              All News
            </button>
            <button 
              v-for="cat in categories" 
              :key="cat"
              class="ghn-cat-tab" 
              :class="{ active: selectedCategory === cat }"
              @click="selectedCategory = cat"
            >
              {{ cat }}
            </button>
          </div>
          <div class="ghn-search-wrap">
            <img
              src="/logo/search.svg"
              class="ghn-search-icon"
              width="16"
              height="16"
              alt=""
              aria-hidden="true"
            />
            <input
              v-model="searchTerm"
              type="text"
              class="ghn-search-input"
              placeholder="Search by title, content, category or date…"
              aria-label="Search GameHub news"
            />
          </div>
        </div>
      </div>
    </div>

    <!-- ══ Content ══ -->
    <div class="container ghn-content">
      <!-- TOP STORIES FEATURED CARD -->
      <section v-if="featuredStory" class="ghn-featured-section">
        <router-link
          :to="detailLink(featuredStory)"
          class="ghn-featured-card"
          :aria-label="`Read featured: ${featuredStory.title}`"
        >
          <div class="ghn-featured-img-wrap">
            <img
              v-lazy-img="featuredStory.image"
              :alt="featuredStory.title"
              class="ghn-featured-img"
            />
            <div class="ghn-featured-overlay"></div>
          </div>
          <div class="ghn-featured-content">
            <div class="ghn-featured-badges">
              <span class="ghn-featured-label">
                <svg
                  width="12"
                  height="12"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <polygon
                    points="12,2 15.09,8.26 22,9.27 17,14.14 18.18,21.02 12,17.77 5.82,21.02 7,14.14 2,9.27 8.91,8.26"
                  />
                </svg>
                Top Story
              </span>
              <span v-if="!featuredStory.isOfficial" class="ghn-community-badge">
                <svg
                  width="11"
                  height="11"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2"
                >
                  <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
                Community
              </span>
              <span v-else class="ghn-official-badge">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                </svg>
                Official
              </span>
              <span
                class="ghn-cat-pill"
                :style="{
                  background: getCategoryColor(featuredStory.category).bg,
                  color: getCategoryColor(featuredStory.category).text,
                  border: `1px solid ${getCategoryColor(featuredStory.category).border}`,
                }"
              >
                <span
                  v-html="getCategoryEmoji(featuredStory.category)"
                  style="display: inline-block; margin-right: 6px"
                ></span
                >{{ featuredStory.category }}
              </span>
            </div>
            <h2 class="ghn-featured-title">{{ featuredStory.title }}</h2>
            <p class="ghn-featured-excerpt">
              {{ featuredStory.content.substring(0, 200) }}…
            </p>
            <div class="ghn-featured-footer">
              <span class="ghn-featured-date">{{ featuredStory.date }}</span>
              <span class="ghn-read-cta">
                Read Full Story
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  stroke-width="2.5"
                  stroke-linecap="round"
                >
                  <path d="M5 12h14M12 5l7 7-7 7" />
                </svg>
              </span>
            </div>
          </div>
        </router-link>
        <div class="ghn-featured-like">
          <LikeButton :article-id="featuredStory.id" />
        </div>
      </section>

      <!-- SEARCH/FILTER RESULTS -->
      <section
        v-if="searchTerm || selectedCategory !== 'All'"
        class="ghn-section"
      >
        <div class="ghn-section-header">
          <h2 class="ghn-section-title">
            <span v-if="searchTerm" class="ghn-section-label"
              >Search Results: "{{ searchTerm }}"</span
            >
            <span v-else class="ghn-section-label"
              >{{ selectedCategory }} News</span
            >
          </h2>
          <span class="ghn-section-count"
            >{{ filteredNews.length }} articles</span
          >
        </div>

        <div v-if="filteredNews.length === 0" class="ghn-state">
          <svg
            width="52"
            height="52"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.2"
            style="opacity: 0.3"
          >
            <path
              d="M4 22h16a2 2 0 002-2V4a2 2 0 00-2-2H8L2 8v12a2 2 0 002 2z"
            />
            <path d="M8 2v6H2" />
            <line x1="12" y1="11" x2="16" y2="11" />
          </svg>
          <h3>No articles found</h3>
          <p>Try adjusting your search or category filter.</p>
        </div>

        <div v-else class="ghn-list">
          <div
            v-for="(item, idx) in paginatedNews"
            :key="item.id"
            class="ghn-list-card stagger-item"
            :style="{ animationDelay: `${idx * 0.05}s` }"
          >
            <router-link
              :to="detailLink(item)"
              class="ghn-list-img-link"
              :aria-label="`Read: ${item.title}`"
            >
              <div class="ghn-list-img-wrap">
                <img
                  v-lazy-img="item.image"
                  :alt="item.title"
                  class="ghn-list-img"
                />
                <div class="ghn-list-img-overlay"></div>
              </div>
            </router-link>
            <div class="ghn-list-content">
              <div class="ghn-list-meta">
                <span
                  class="ghn-cat-pill"
                  :style="{
                    background: getCategoryColor(item.category).bg,
                    color: getCategoryColor(item.category).text,
                    border: `1px solid ${getCategoryColor(item.category).border}`,
                  }"
                >
                  <span
                    v-html="getCategoryEmoji(item.category)"
                    style="display: inline-block; margin-right: 6px"
                  ></span
                  >{{ item.category }}
                </span>
                <span v-if="!item.isOfficial" class="ghn-community-badge">
                  <svg
                    width="11"
                    height="11"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2"
                  >
                    <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                    <circle cx="12" cy="7" r="4" />
                  </svg>
                  Community
                </span>
                <span v-else class="ghn-official-badge list-badge">
                  <svg width="11" height="11" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
                  </svg>
                  Official
                </span>
                <span class="ghn-list-date">{{ item.date }}</span>
              </div>
              <router-link :to="detailLink(item)" class="ghn-list-title-link">
                <h3 class="ghn-list-title">{{ item.title }}</h3>
              </router-link>
              <p class="ghn-list-excerpt">
                {{ item.content.substring(0, 160) }}…
              </p>
              <div class="ghn-list-footer">
                <router-link
                  :to="detailLink(item)"
                  class="ghn-read-btn"
                  :aria-label="`Read more: ${item.title}`"
                >
                  Read More
                  <svg
                    width="12"
                    height="12"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    stroke-width="2.5"
                    stroke-linecap="round"
                  >
                    <path d="M5 12h14M12 5l7 7-7 7" />
                  </svg>
                </router-link>
                <LikeButton :article-id="item.id" />
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <nav
          v-if="totalPages > 1"
          class="ghn-pagination"
          aria-label="GameHub news pagination"
        >
          <button
            class="ghn-page-btn"
            :disabled="currentPage === 1"
            @click="goToPage(currentPage - 1)"
          >
            <img
              src="/logo/arrow-left.svg"
              width="15"
              height="15"
              alt=""
              aria-hidden="true"
            />
            Previous
          </button>
          <div class="ghn-page-numbers">
            <button
              v-for="page in totalPages"
              :key="page"
              class="ghn-page-num"
              :class="{ active: currentPage === page }"
              @click="goToPage(page)"
            >
              {{ page }}
            </button>
          </div>
          <button
            class="ghn-page-btn"
            :disabled="currentPage === totalPages"
            @click="goToPage(currentPage + 1)"
          >
            Next
            <img
              src="/logo/arrow-right.svg"
              width="15"
              height="15"
              alt=""
              aria-hidden="true"
            />
          </button>
        </nav>
      </section>

      <!-- TRENDING STORIES -->
      <section
        v-if="
          !searchTerm && selectedCategory === 'All' && trendingStories.length
        "
        class="ghn-section"
      >
        <div class="ghn-section-header">
          <h2 class="ghn-section-title">
            <span class="ghn-section-icon"
              ><svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="currentColor"
              >
                <path d="M13 2L3 14h8l-1 8 10-12h-8l1-8z" /></svg
            ></span>
            Trending Now
          </h2>
          <span class="ghn-section-count"
            >{{ trendingStories.length }} stories</span
          >
        </div>
        <div class="ghn-trending-list">
          <router-link
            v-for="(article, idx) in trendingStories.slice(0, 7)"
            :key="article.id"
            :to="detailLink(article)"
            class="ghn-trending-item stagger-item"
            :style="{ animationDelay: `${idx * 0.04}s` }"
          >
            <div class="ghn-trending-num">{{ idx + 1 }}</div>
            <div class="ghn-trending-body">
              <div class="ghn-trending-category">
                <span
                  v-html="getCategoryEmoji(article.category)"
                  style="display: inline-block; margin-right: 6px"
                ></span
                >{{ article.category }}
              </div>
              <h4 class="ghn-trending-title">{{ article.title }}</h4>
              <div class="ghn-trending-meta">
                <span class="ghn-trending-date">{{ article.date }}</span>
                <span v-if="!article.isOfficial" class="ghn-trending-community"
                  >Community</span
                >
                <span v-else class="ghn-trending-official"
                  >Official</span
                >
              </div>
            </div>
            <svg
              class="ghn-trending-arrow"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            >
              <path d="M5 12h14M12 5l7 7-7 7" />
            </svg>
          </router-link>
        </div>
      </section>

      <!-- CATEGORIES BROWSER -->
      <section
        v-if="!searchTerm && selectedCategory === 'All' && categories.length"
        class="ghn-section"
      >
        <div class="ghn-section-header">
          <h2 class="ghn-section-title">
            <span class="ghn-section-icon"
              ><svg
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                stroke-width="2"
                stroke-linecap="round"
                stroke-linejoin="round"
              >
                <rect x="3" y="3" width="7" height="7" />
                <rect x="14" y="3" width="7" height="7" />
                <rect x="14" y="14" width="7" height="7" />
                <rect x="3" y="14" width="7" height="7" /></svg
            ></span>
            Browse by Category
          </h2>
        </div>
        <div class="ghn-categories-grid">
          <button
            v-for="cat in categories"
            :key="cat"
            type="button"
            class="ghn-category-btn"
            :class="{ expanded: expandedCategory === cat }"
            @click="toggleCategory(cat)"
          >
            <span class="ghn-cat-icon" v-html="getCategoryEmoji(cat)"></span>
            <span class="ghn-cat-title">{{ cat }}</span>
            <span class="ghn-cat-count">{{
              newsByCategory[cat]?.length || 0
            }}</span>
            <svg
              class="ghn-cat-chevron"
              width="16"
              height="16"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            >
              <polyline points="6 9 12 15 18 9" />
            </svg>
          </button>
        </div>

        <!-- Expanded Category -->
        <div
          v-if="expandedCategory && newsByCategory[expandedCategory]"
          class="ghn-category-expanded"
        >
          <div class="ghn-expanded-header">
            <h3 class="ghn-expanded-title">
              <span
                v-html="getCategoryEmoji(expandedCategory)"
                style="display: inline-block; margin-right: 8px"
              ></span
              >{{ expandedCategory }} Stories
            </h3>
            <span class="ghn-expanded-count"
              >{{ newsByCategory[expandedCategory].length }} stories</span
            >
          </div>
          <div class="ghn-expanded-cards">
            <div
              v-for="(item, idx) in newsByCategory[expandedCategory]"
              :key="item.id"
              class="ghn-list-card stagger-item"
              :style="{ animationDelay: `${(idx % 20) * 0.02}s` }"
            >
              <router-link
                :to="detailLink(item)"
                class="ghn-list-img-link"
                :aria-label="`Read: ${item.title}`"
              >
                <div class="ghn-list-img-wrap">
                  <img
                    v-lazy-img="item.image"
                    :alt="item.title"
                    class="ghn-list-img"
                  />
                  <div class="ghn-list-img-overlay"></div>
                </div>
              </router-link>
              <div class="ghn-list-content">
                <div class="ghn-list-meta">
                  <span
                    class="ghn-cat-pill"
                    :style="{
                      background: getCategoryColor(item.category).bg,
                      color: getCategoryColor(item.category).text,
                      border: `1px solid ${getCategoryColor(item.category).border}`,
                    }"
                  >
                    {{ item.category }}
                  </span>
                  <span v-if="item.isUserPost" class="ghn-community-badge">
                    <svg
                      width="11"
                      height="11"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2"
                    >
                      <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
                      <circle cx="12" cy="7" r="4" />
                    </svg>
                    Community
                  </span>
                  <span class="ghn-list-date">{{ item.date }}</span>
                </div>
                <router-link :to="detailLink(item)" class="ghn-list-title-link">
                  <h3 class="ghn-list-title">{{ item.title }}</h3>
                </router-link>
                <p class="ghn-list-excerpt">
                  {{ item.content.substring(0, 160) }}…
                </p>
                <div class="ghn-list-footer">
                  <router-link
                    :to="detailLink(item)"
                    class="ghn-read-btn"
                    :aria-label="`Read more: ${item.title}`"
                  >
                    Read More
                    <svg
                      width="12"
                      height="12"
                      viewBox="0 0 24 24"
                      fill="none"
                      stroke="currentColor"
                      stroke-width="2.5"
                      stroke-linecap="round"
                    >
                      <path d="M5 12h14M12 5l7 7-7 7" />
                    </svg>
                  </router-link>
                  <LikeButton :article-id="item.id" />
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
/* ── Page ─────────────────────────────────────────── */
.ghn-page {
  min-height: 100vh;
  background: var(--bg-deep);
}

/* ── Header ───────────────────────────────────────── */
.ghn-page-header {
  position: relative;
  background: var(--bg-base);
  border-bottom: 1px solid var(--border-glass);
  overflow: hidden;
}
.ghn-header-bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(
      ellipse 65% 120% at 90% 50%,
      rgba(139, 92, 246, 0.07) 0%,
      transparent 60%
    ),
    radial-gradient(
      ellipse 50% 80% at 10% 80%,
      rgba(6, 182, 212, 0.05) 0%,
      transparent 60%
    );
  pointer-events: none;
}
.ghn-header-content {
  position: relative;
  z-index: 1;
  padding-top: 40px;
  padding-bottom: 0;
}

/* Title */
.ghn-title-row {
  display: flex;
  align-items: flex-start;
  gap: 18px;
  margin-bottom: 20px;
}
.ghn-title-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 54px;
  height: 54px;
  border-radius: 16px;
  flex-shrink: 0;
  margin-top: 2px;
  background: linear-gradient(135deg, #4c1d95, #7c3aed);
  color: #fff;
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
}
.ghn-title {
  font-size: 2.1rem;
  font-weight: 800;
  color: var(--text-primary) !important;
  margin: 0 0 6px;
  line-height: 1;
}
.ghn-subtitle {
  font-size: 0.85rem;
  color: var(--text-secondary) !important;
  margin: 0;
}

/* Post button */
.ghn-post-btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  padding: 10px 20px;
  border-radius: 10px;
  border: none;
  background: var(--gradient-primary);
  color: #fff !important;
  font-size: 0.88rem;
  font-weight: 700;
  font-family: var(--font-family);
  text-decoration: none;
  cursor: pointer;
  transition:
    opacity 0.2s,
    transform 0.2s;
  box-shadow: 0 4px 16px rgba(124, 58, 237, 0.4);
  align-self: center;
}
.ghn-post-btn:hover {
  opacity: 0.88;
  transform: translateY(-1px);
  color: #fff !important;
}

/* Filter panel */
.ghn-filter-panel {
  background: var(--bg-surface);
  border: 1px solid var(--border-glass);
  border-bottom: none;
  border-radius: 14px 14px 0 0;
  padding: 18px 24px;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}
.ghn-search-wrap {
  position: relative;
  width: 100%;
}
.ghn-search-icon {
  position: absolute;
  left: 13px;
  top: 50%;
  transform: translateY(-50%);
  pointer-events: none;
  opacity: 0.6;
}
.ghn-search-input {
  width: 100%;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: var(--radius-sm);
  color: var(--text-primary) !important;
  padding: 10px 14px 10px 38px;
  font-size: 0.88rem;
  font-family: var(--font-family);
  outline: none;
  transition: border-color 0.2s;
}
.ghn-search-input::placeholder {
  color: var(--text-muted);
}
.ghn-search-input:focus {
  border-color: var(--primary-light);
}

/* ── Content ──────────────────────────────────────── */
.ghn-content {
  padding-top: 24px;
  padding-bottom: 60px;
}

/* ── Section ──────────────────────────────────────── */
.ghn-section {
  margin-bottom: 52px;
}
.ghn-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid rgba(124, 58, 237, 0.2);
}
.ghn-section-title {
  font-size: 1.6rem;
  font-weight: 800;
  color: var(--text-primary) !important;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 10px;
}
.ghn-section-label {
  font-size: 1rem;
  font-weight: 600;
}
.ghn-section-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  color: #7c3aed;
}
.ghn-section-icon svg {
  width: 28px;
  height: 28px;
  stroke-width: 2;
}
.ghn-section-count {
  font-size: 0.8rem;
  padding: 4px 12px;
  border-radius: 20px;
  background: rgba(124, 58, 237, 0.15);
  color: var(--accent-light) !important;
  font-weight: 600;
}

/* ── FEATURED SECTION ─────────────────────────────── */
.ghn-featured-section {
  position: relative;
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(124, 58, 237, 0.25);
  margin-bottom: 48px;
  transition:
    box-shadow 0.3s ease,
    border-color 0.3s ease;
}
.ghn-featured-section:hover {
  box-shadow: 0 20px 60px rgba(124, 58, 237, 0.2);
  border-color: rgba(124, 58, 237, 0.45);
}

.ghn-featured-card {
  display: block;
  text-decoration: none;
  position: relative;
}
.ghn-featured-img-wrap {
  height: 420px;
  overflow: hidden;
}
.ghn-featured-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.4s ease;
}
.ghn-featured-section:hover .ghn-featured-img {
  transform: scale(1.04);
}
.ghn-featured-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to top,
    rgba(5, 8, 20, 0.95) 0%,
    rgba(5, 8, 20, 0.3) 50%,
    transparent 80%
  );
}

.ghn-featured-content {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 32px 36px 28px;
}
.ghn-featured-badges {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}
.ghn-featured-label {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: var(--gradient-primary);
  color: #fff !important;
  font-size: 0.72rem;
  font-weight: 700;
  padding: 4px 12px;
  border-radius: 20px;
  letter-spacing: 0.3px;
}
.ghn-community-badge {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  background: rgba(100, 116, 139, 0.25);
  border: 1px solid rgba(100, 116, 139, 0.4);
  color: var(--text-secondary) !important;
  font-size: 0.7rem;
  font-weight: 600;
  padding: 3px 10px;
  border-radius: 20px;
}
.ghn-cat-pill {
  display: inline-block;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 3px 10px;
  border-radius: 20px;
  letter-spacing: 0.3px;
}
.ghn-featured-title {
  font-size: 1.85rem;
  font-weight: 800;
  color: #fff !important;
  margin: 0 0 12px;
  line-height: 1.25;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ghn-featured-excerpt {
  font-size: 0.88rem;
  color: rgba(255, 255, 255, 0.65) !important;
  line-height: 1.6;
  margin: 0 0 16px;
  max-width: 680px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ghn-featured-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}
.ghn-featured-date {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.45) !important;
}
.ghn-read-cta {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 700;
  color: #fff !important;
  padding: 8px 20px;
  border-radius: 30px;
  background: var(--gradient-primary);
  box-shadow: 0 4px 16px rgba(124, 58, 237, 0.4);
  transition: opacity 0.2s;
}
.ghn-featured-section:hover .ghn-read-cta {
  opacity: 0.88;
}
.ghn-featured-like {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 2;
}

/* ── TRENDING LIST ────────────────────────────────── */
.ghn-trending-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
.ghn-trending-item {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  text-decoration: none;
  border-radius: 10px;
  transition: all 0.2s;
  border: 1px solid var(--border-glass);
  background: var(--bg-surface);
}
.ghn-trending-item:hover {
  background: var(--bg-glass-hover);
  border-color: rgba(124, 58, 237, 0.2);
  transform: translateX(6px);
}
.ghn-trending-num {
  font-size: 1.4rem;
  font-weight: 900;
  color: var(--primary) !important;
  min-width: 30px;
  text-align: center;
}
.ghn-trending-body {
  flex: 1;
  min-width: 0;
}
.ghn-trending-category {
  font-size: 0.68rem;
  font-weight: 700;
  color: var(--primary) !important;
  text-transform: uppercase;
  letter-spacing: 0.3px;
  margin-bottom: 3px;
}
.ghn-trending-title {
  font-size: 0.98rem;
  font-weight: 700;
  color: var(--text-primary) !important;
  margin: 0 0 6px;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ghn-trending-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.ghn-trending-date {
  font-size: 0.7rem;
  color: var(--text-muted) !important;
}
.ghn-trending-community {
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--text-secondary) !important;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(100, 116, 139, 0.2);
}
.ghn-trending-arrow {
  color: #7c3aed;
  opacity: 0;
  transition: opacity 0.2s;
  flex-shrink: 0;
}
.ghn-trending-item:hover .ghn-trending-arrow {
  opacity: 1;
}

/* ── CATEGORIES ───────────────────────────────────── */
.ghn-categories-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 10px;
}
.ghn-category-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  padding: 12px 14px;
  border-radius: 10px;
  border: 1px solid var(--border-glass);
  background: var(--bg-surface);
  color: var(--text-secondary) !important;
  font-size: 0.85rem;
  font-weight: 600;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all 0.2s;
}
.ghn-category-btn:hover {
  background: var(--bg-glass-hover);
  border-color: rgba(124, 58, 237, 0.2);
}
.ghn-category-btn.expanded {
  background: rgba(124, 58, 237, 0.15);
  border-color: rgba(124, 58, 237, 0.4);
  color: var(--accent-light) !important;
}
.ghn-cat-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  color: currentColor;
}
.ghn-cat-icon svg {
  width: 20px;
  height: 20px;
  stroke-width: 2;
}
.ghn-cat-title {
  flex: 1;
  text-align: left;
}
.ghn-cat-count {
  font-size: 0.72rem;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(124, 58, 237, 0.15);
  color: var(--accent-light) !important;
}
.ghn-cat-chevron {
  transition: transform 0.2s;
  flex-shrink: 0;
}
.ghn-category-btn.expanded .ghn-cat-chevron {
  transform: scaleY(-1);
}

/* Expanded Category */
.ghn-category-expanded {
  margin-top: 28px;
  padding: 20px;
  border-radius: 12px;
  background: var(--bg-surface);
  border: 1px solid rgba(124, 58, 237, 0.15);
  animation: slideDown 0.3s ease;
}
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
.ghn-expanded-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid rgba(124, 58, 237, 0.2);
}
.ghn-expanded-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-primary) !important;
  margin: 0;
}
.ghn-expanded-count {
  font-size: 0.75rem;
  padding: 3px 10px;
  border-radius: 20px;
  background: rgba(124, 58, 237, 0.15);
  color: var(--accent-light) !important;
  font-weight: 600;
}
.ghn-expanded-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 18px;
}

/* ── State ────────────────────────────────────────── */
.ghn-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-height: 200px;
  gap: 12px;
  color: var(--text-muted) !important;
}
.ghn-state h3 {
  color: var(--text-primary) !important;
  font-size: 1.2rem;
  margin: 0;
}
.ghn-state p {
  color: var(--text-muted) !important;
  font-size: 0.88rem;
  margin: 0;
}

/* ── LIST ─────────────────────────────────────────── */
.ghn-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.ghn-list-card {
  display: flex;
  gap: 0;
  border-radius: 14px;
  overflow: hidden;
  background: var(--bg-surface);
  border: 1px solid var(--border-glass);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  transition:
    transform 0.22s ease,
    box-shadow 0.22s ease,
    border-color 0.22s ease;
}
.ghn-list-card:hover {
  transform: translateY(-3px);
  box-shadow:
    0 12px 36px rgba(124, 58, 237, 0.15),
    0 4px 16px rgba(0, 0, 0, 0.3);
  border-color: rgba(124, 58, 237, 0.25);
}

/* Image */
.ghn-list-img-link {
  flex-shrink: 0;
  width: 240px;
}
.ghn-list-img-wrap {
  position: relative;
  height: 100%;
  min-height: 180px;
  overflow: hidden;
}
.ghn-list-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
}
.ghn-list-card:hover .ghn-list-img {
  transform: scale(1.05);
}
.ghn-list-img-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(
    to right,
    transparent 60%,
    rgba(10, 15, 30, 0.5) 100%
  );
  pointer-events: none;
}

/* Content */
.ghn-list-content {
  flex: 1;
  padding: 20px 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.ghn-list-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}
.ghn-list-date {
  font-size: 0.72rem;
  color: var(--text-muted) !important;
  margin-left: auto;
}
.ghn-list-title-link {
  text-decoration: none;
}
.ghn-list-title {
  font-size: 1.08rem;
  font-weight: 700;
  color: var(--text-primary) !important;
  margin: 0;
  line-height: 1.4;
  transition: color 0.2s;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ghn-list-title-link:hover .ghn-list-title {
  color: var(--primary-light) !important;
}
.ghn-list-excerpt {
  font-size: 0.83rem;
  color: var(--text-muted) !important;
  line-height: 1.65;
  flex: 1;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.ghn-list-footer {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: auto;
}
.ghn-read-btn {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--text-secondary) !important;
  text-decoration: none;
  transition: color 0.2s;
  padding: 0;
}
.ghn-list-card:hover .ghn-read-btn {
  color: var(--primary-light) !important;
}

/* ── Pagination ───────────────────────────────────── */
.ghn-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 32px 0 8px;
  flex-wrap: wrap;
}
.ghn-page-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 9px 18px;
  border-radius: 8px;
  border: 1px solid var(--border-glass);
  background: var(--bg-surface);
  color: var(--text-secondary) !important;
  font-size: 0.83rem;
  font-weight: 600;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all 0.2s;
}
.ghn-page-btn:disabled {
  opacity: 0.35;
  cursor: not-allowed;
}
.ghn-page-btn:not(:disabled):hover {
  border-color: rgba(124, 58, 237, 0.4);
  color: var(--primary-light) !important;
}
.ghn-page-numbers {
  display: flex;
  align-items: center;
  gap: 4px;
}
.ghn-page-num {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid var(--border-glass);
  background: var(--bg-surface);
  color: var(--text-secondary) !important;
  font-size: 0.83rem;
  font-weight: 600;
  font-family: var(--font-family);
  cursor: pointer;
  transition: all 0.18s;
}
.ghn-page-num:hover {
  border-color: rgba(124, 58, 237, 0.35);
  color: var(--primary-light) !important;
}
.ghn-page-num.active {
  background: var(--gradient-primary);
  border-color: transparent;
  color: #fff !important;
  box-shadow: 0 2px 12px rgba(124, 58, 237, 0.4);
}
.ghn-page-info {
  text-align: center;
  font-size: 0.78rem;
  color: var(--text-muted) !important;
  margin: 8px 0 0;
}

/* ── Stagger Animation ────────────────────────────── */
.stagger-item {
  animation: fadeInUp 0.5s ease both;
}
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Responsive */
@media (max-width: 640px) {
  .ghn-list-img-link {
    width: 140px;
  }
  .ghn-featured-title {
    font-size: 1.4rem;
  }
  .ghn-featured-img-wrap {
    height: 280px;
  }
  .ghn-post-btn span {
    display: none;
  }
}

/* === NEW UI ELEMENTS: Categories & Official Badges === */
.ghn-categories-bar {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
}
.ghn-categories-bar::-webkit-scrollbar {
  height: 4px;
}
.ghn-categories-bar::-webkit-scrollbar-thumb {
  background: var(--border-glass);
  border-radius: 4px;
}
.ghn-cat-tab {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--border-glass);
  color: var(--text-secondary);
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}
.ghn-cat-tab:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}
.ghn-cat-tab.active {
  background: var(--primary);
  border-color: var(--primary-light);
  color: #fff;
  box-shadow: 0 0 10px rgba(124, 58, 237, 0.3);
}

.ghn-official-badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(16, 185, 129, 0.15); /* Emerald */
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #10b981;
  padding: 4px 10px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.ghn-trending-official {
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: #10b981;
  background: rgba(16, 185, 129, 0.1);
  padding: 2px 6px;
  border-radius: 4px;
  margin-left: 6px;
}

.list-badge {
  padding: 3px 8px;
  font-size: 0.68rem;
}
</style>
