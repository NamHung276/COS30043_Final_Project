<script>
import newsData from '../data/news.json'
import LikeButton from '../components/LikeButton.vue'

export default {
  components: { LikeButton },

  data() {
    return {
      article: null,
      relatedArticles: []
    }
  },

  mounted() {
    this.loadArticle()
  },

  methods: {
    loadArticle() {
      const articleId = Number(this.$route.params.id)

      // Read from localStorage first (same source as the list page),
      // falling back to the original JSON if nothing's saved yet
      const savedNews = localStorage.getItem('gamehubNews')
      const news = savedNews ? JSON.parse(savedNews) : newsData

      this.article = news.find(item => item.id === articleId)

      if (this.article) {
        document.title = `${this.article.title} | GameHub`
        this.relatedArticles = news
          .filter(item =>
            item.category === this.article.category &&
            item.id !== this.article.id
          )
          .slice(0, 3)
      }
    }
  }
}
</script>

<template>
  <div class="container py-4">

    <div v-if="article">

      <img
        v-lazy-img="article.image"
        :alt="article.title"
        class="img-fluid rounded mb-4 w-100"
        style="max-height:500px;object-fit:cover;"
      >

      <div class="d-flex justify-content-between align-items-center mb-2">
        <span class="badge bg-primary">
          {{ article.category }}
        </span>

        <LikeButton :article-id="article.id" />
      </div>

      <h1 class="mb-3">
        {{ article.title }}
      </h1>

      <p class="text-muted mb-4">
        {{ article.date }}
      </p>

      <div class="card">
        <div class="card-body">

          <p class="lead">
            {{ article.content }}
          </p>

          <hr>

          <p class="mb-0">
            This article is part of the GameHub News archive.
            Stay tuned for more gaming news, updates,
            esports events, and industry announcements.
          </p>

        </div>
      </div>

      <router-link
        to="/gamehub-news"
        class="btn btn-primary mt-4"
      >
        ← Back to News
      </router-link>

      <!-- Related Articles -->
      <div
        v-if="relatedArticles.length"
        class="mt-5"
      >
        <h3 class="mb-4">Related Articles</h3>

        <div class="row">
          <div
            v-for="related in relatedArticles"
            :key="related.id"
            class="col-md-4 mb-4"
          >
            <div class="card h-100">

              <img
                v-lazy-img="related.image"
                :alt="related.title"
                class="card-img-top"
                style="height: 200px; object-fit: cover;"
              >

              <div class="card-body">
                <span class="badge bg-secondary mb-2">
                  {{ related.category }}
                </span>

                <h6>{{ related.title }}</h6>

                <p class="small text-muted">
                  {{ related.date }}
                </p>

                <router-link
                  :to="`/gamehub-news/${related.id}`"
                  class="btn btn-outline-primary btn-sm mt-2"
                >
                  Read More
                </router-link>
              </div>

            </div>
          </div>
        </div>
      </div>

    </div>

    <div
      v-else
      class="alert alert-danger"
    >
      Article not found.
    </div>

  </div>
</template>