<script>
import newsData from '../data/news.json'

export default {

  data() {
    return {
      article: null
    }
  },

  mounted() {

    const articleId =
      Number(this.$route.params.id)

    this.article =
      newsData.find(
        news => news.id === articleId
      )

  }

}
</script>

<template>

  <div class="container py-4">

    <div v-if="article">

      <img
        :src="article.image"
        :alt="article.title"
        class="img-fluid rounded mb-4"
        style="width:100%;max-height:500px;object-fit:cover;"
      >

      <span class="badge bg-primary mb-2">
        {{ article.category }}
      </span>

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