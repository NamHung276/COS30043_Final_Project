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

      <img
        v-lazy-img="article.image"
        :alt="article.title"
        class="img-fluid rounded mb-4"
        style="width:100%;max-height:500px;object-fit:cover;"
      >

      <div class="d-flex justify-content-between align-items-center mb-2">
        <span class="badge bg-primary">
          {{ article.category }}
        </span>

        <LikeButton :article-id="article.id" />
      </div>

      <h1>
        {{ article.title }}
      </h1>

      <p class="text-muted">
        {{ article.date }}
      </p>

      <hr>

      <p class="fs-5">
        {{ article.content }}
      </p>

      <router-link
        to="/gamehub-news"
        class="btn btn-secondary mt-4"
      >
        Back to News
      </router-link>

    </div>

    <div
      v-else
      class="alert alert-danger"
    >
      Article not found.
    </div>

  </div>

</template>