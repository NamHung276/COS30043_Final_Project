// src/views/GameHubNewsDetails.vue
<script>
import newsData from '../data/news.json'
import LikeButton from '../components/LikeButton.vue'

export default {

  components: { LikeButton },

  data() {
    return {
      article: null
    }
  },

  mounted() {

    const articleId =
      Number(this.$route.params.id)

    // Read from localStorage first (same source as the list page),
    // falling back to the original JSON if nothing's saved yet
    const savedNews =
      localStorage.getItem('gamehubNews')

    const news =
      savedNews
        ? JSON.parse(savedNews)
        : newsData

    this.article =
      news.find(
        item => item.id === articleId
      )

  }

}
</script>

<template>

  <div class="container py-4">

    <div v-if="article">

      <!-- Hero Image -->
      <div class="card overflow-hidden mb-4" style="border: none;">
        <div style="position: relative;">
          <img
            v-lazy-img="article.image"
            :alt="article.title"
            style="width:100%;max-height:500px;object-fit:cover;"
          >
          <div
            style="position: absolute; bottom: 0; left: 0; right: 0; padding: 24px 24px 20px; background: linear-gradient(transparent, rgba(7,11,20,0.9));"
          >
            <span class="badge bg-primary">
              {{ article.category }}
            </span>
          </div>
        </div>
      </div>

      <div class="d-flex justify-content-between align-items-center mb-2">
        <h1>
          {{ article.title }}
        </h1>

        <LikeButton :article-id="article.id" />
      </div>

      <p class="text-muted">
        {{ article.date }}
      </p>

      <hr style="border-color: var(--border-glass);">

      <div class="card">
        <div class="card-body">
          <p class="fs-5" style="line-height: 1.8;">
            {{ article.content }}
          </p>
        </div>
      </div>

      <router-link
        to="/gamehub-news"
        class="btn btn-outline-secondary mt-4"
      >
        ← Back to News
      </router-link>

    </div>

    <div
      v-else
      class="empty-state"
    >
      <div class="empty-state-icon">📰</div>
      <h3>Article not found</h3>
      <p>The article you're looking for doesn't exist or has been removed.</p>
      <router-link to="/gamehub-news" class="btn btn-primary">
        ← Back to News
      </router-link>
    </div>

  </div>

</template>