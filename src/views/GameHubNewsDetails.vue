<script>
import newsData from "../data/news.json";
import LikeButton from "../components/LikeButton.vue";
import { db } from "../firebase";
import { collection, query, where, getDocs } from "firebase/firestore";

export default {
  components: { LikeButton },

  data() {
    return {
      article: null,
      relatedArticles: [],
      copyFeedback: false,
    };
  },

  computed: {
    readingTime() {
      if (!this.article?.content) return 1;
      const words = this.article.content.trim().split(/\s+/).length;
      return Math.max(1, Math.ceil(words / 200));
    },

    formattedDate() {
      if (!this.article?.date) return "";
      try {
        return new Date(this.article.date).toLocaleDateString("en-AU", {
          year: "numeric",
          month: "long",
          day: "numeric",
        });
      } catch {
        return this.article.date;
      }
    },
  },

  mounted() {
    this.loadArticle();
  },

  methods: {
    loadArticle() {
      const articleId = Number(this.$route.params.id);

      const savedNews = localStorage.getItem("gamehubNews");
      const news = savedNews ? JSON.parse(savedNews) : newsData;

      this.article = news.find((item) => item.id === articleId);

      if (this.article) {
        document.title = `${this.article.title} | GameHub`;
        this.relatedArticles = news
          .filter(
            (item) =>
              item.category === this.article.category &&
              item.id !== this.article.id,
          )
          .slice(0, 3);
      }
    },

    async copyLink() {
      try {
        await navigator.clipboard.writeText(window.location.href);
        this.copyFeedback = true;
        setTimeout(() => (this.copyFeedback = false), 2000);
      } catch {
        // Fallback for older browsers
        const el = document.createElement("textarea");
        el.value = window.location.href;
        document.body.appendChild(el);
        el.select();
        document.execCommand("copy");
        document.body.removeChild(el);
        this.copyFeedback = true;
        setTimeout(() => (this.copyFeedback = false), 2000);
      }
    },
  },
};
</script>

<template>
  <div v-if="article" class="news-detail-page">
    <!-- Hero Image -->
    <div class="news-hero" v-if="article.image">
      <img :src="article.image" :alt="article.title" class="news-hero-img" />
      <div class="news-hero-overlay"></div>
    </div>

    <div class="container news-detail-container">
      <!-- Back Button -->
      <router-link to="/gamehub-news" class="news-back-btn">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="15 18 9 12 15 6"/></svg>
        Back to News
      </router-link>

      <article class="news-article">
        <!-- Category + Meta row -->
        <div class="news-meta-row">
          <span class="news-category-badge">{{ article.category }}</span>
          <span class="news-meta-item">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
            {{ readingTime }} min read
          </span>
          <span class="news-meta-item">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/></svg>
            {{ formattedDate }}
          </span>
        </div>

        <!-- Title -->
        <h1 class="news-article-title">{{ article.title }}</h1>

        <!-- Action bar -->
        <div class="news-action-bar">
          <LikeButton :article-id="article.id" />
          <button
            class="news-share-btn"
            @click="copyLink"
            :class="{ copied: copyFeedback }"
            :title="copyFeedback ? 'Link copied!' : 'Copy link to article'"
          >
            <template v-if="copyFeedback">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" aria-hidden="true"><polyline points="20 6 9 17 4 12"/></svg>
              Copied!
            </template>
            <template v-else>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M4 12v8a2 2 0 002 2h12a2 2 0 002-2v-8"/><polyline points="16 6 12 2 8 6"/><line x1="12" y1="2" x2="12" y2="15"/></svg>
              Share
            </template>
          </button>
        </div>

        <!-- Article Body -->
        <div class="news-article-body">
          <p class="news-article-content">{{ article.content }}</p>
          <div class="news-article-footer">
            <p>This article is part of the GameHub News archive. Stay updated with the latest gaming news, reviews, esports events, and industry announcements.</p>
          </div>
        </div>
      </article>

      <!-- Related Articles -->
      <section v-if="relatedArticles.length" class="news-related">
        <h2 class="news-related-title">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
          More from {{ article.category }}
        </h2>

        <div class="news-related-grid">
          <router-link
            v-for="related in relatedArticles"
            :key="related.id"
            :to="`/gamehub-news/${related.id}`"
            class="news-related-card"
          >
            <div class="news-related-img">
              <img
                v-if="related.image"
                :src="related.image"
                :alt="related.title"
              />
              <div v-else class="news-related-img-placeholder">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/></svg>
              </div>
            </div>
            <div class="news-related-body">
              <span class="news-related-category">{{ related.category }}</span>
              <h3 class="news-related-title-text">{{ related.title }}</h3>
              <span class="news-related-date">{{ related.date }}</span>
            </div>
          </router-link>
        </div>
      </section>
    </div>
  </div>

  <div v-else class="container py-5">
    <div class="news-not-found">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" aria-hidden="true"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
      <h3>Article not found</h3>
      <p>This article may have been removed or the link is incorrect.</p>
      <router-link to="/gamehub-news" class="btn btn-primary">← Back to News</router-link>
    </div>
  </div>
</template>

<style scoped>
.news-detail-page {
  padding-bottom: 60px;
}

/* Hero */
.news-hero {
  position: relative;
  width: 100%;
  height: 420px;
  overflow: hidden;
  margin-bottom: 0;
}

.news-hero-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.news-hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(15,17,22,0) 40%, rgba(15,17,22,0.95) 100%);
}

/* Container */
.news-detail-container {
  padding-top: 28px;
}

/* Back button */
.news-back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-decoration: none;
  padding: 7px 14px;
  border-radius: 8px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  transition: all 0.2s ease;
  margin-bottom: 28px;
}

.news-back-btn:hover {
  color: var(--primary);
  background: rgba(14,165,233,0.08);
  border-color: rgba(14,165,233,0.2);
}

/* Article layout */
.news-article {
  max-width: 780px;
  margin: 0 auto;
}

/* Meta row */
.news-meta-row {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 12px;
  margin-bottom: 16px;
}

.news-category-badge {
  display: inline-flex;
  align-items: center;
  background: rgba(14,165,233,0.15);
  border: 1px solid rgba(14,165,233,0.3);
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  padding: 4px 12px;
  border-radius: 999px;
}

.news-meta-item {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.82rem;
  color: var(--text-muted);
}

/* Title */
.news-article-title {
  font-size: 2rem;
  font-weight: 800;
  color: var(--text-primary);
  line-height: 1.3;
  margin-bottom: 20px;
}

@media (max-width: 600px) {
  .news-article-title { font-size: 1.5rem; }
  .news-hero { height: 250px; }
}

/* Action bar */
.news-action-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 14px 0;
  border-top: 1px solid var(--border-subtle);
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 32px;
}

.news-share-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  border-radius: 8px;
  color: var(--text-secondary);
  font-size: 0.83rem;
  font-weight: 600;
  padding: 7px 14px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.news-share-btn:hover {
  background: rgba(255,255,255,0.09);
  color: var(--text-primary);
}

.news-share-btn.copied {
  background: rgba(16,185,129,0.12);
  border-color: rgba(16,185,129,0.3);
  color: #10b981;
}

/* Article body */
.news-article-body {
  padding-bottom: 32px;
  border-bottom: 1px solid var(--border-subtle);
  margin-bottom: 48px;
}

.news-article-content {
  font-size: 1.05rem;
  line-height: 1.85;
  color: var(--text-secondary);
  white-space: pre-line;
}

.news-article-footer {
  margin-top: 32px;
  padding: 20px 24px;
  background: rgba(255,255,255,0.03);
  border: 1px solid rgba(255,255,255,0.06);
  border-radius: 12px;
  color: var(--text-muted);
  font-size: 0.875rem;
  line-height: 1.6;
}

.news-article-footer p { margin: 0; }

/* Related articles */
.news-related {
  max-width: 780px;
  margin: 0 auto;
}

.news-related-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 20px;
}

.news-related-title svg {
  color: var(--primary);
}

.news-related-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 16px;
}

.news-related-card {
  display: flex;
  flex-direction: column;
  background: var(--bg-glass);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  overflow: hidden;
  text-decoration: none;
  color: var(--text-primary);
  transition: all 0.25s ease;
}

.news-related-card:hover {
  transform: translateY(-4px);
  border-color: rgba(14,165,233,0.25);
  box-shadow: 0 10px 25px rgba(0,0,0,0.3);
}

.news-related-img {
  height: 130px;
  overflow: hidden;
  background: var(--bg-surface);
}

.news-related-img img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
  transition: transform 0.3s ease;
}

.news-related-card:hover .news-related-img img {
  transform: scale(1.05);
}

.news-related-img-placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-muted);
  opacity: 0.4;
}

.news-related-body {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}

.news-related-category {
  font-size: 0.7rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--primary);
}

.news-related-title-text {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.4;
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.news-related-date {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: auto;
}

/* Not found state */
.news-not-found {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-muted);
}

.news-not-found svg {
  opacity: 0.3;
  margin-bottom: 20px;
}

.news-not-found h3 {
  color: var(--text-primary);
  margin-bottom: 10px;
}

.news-not-found p {
  margin-bottom: 24px;
  font-size: 0.95rem;
}
</style>
