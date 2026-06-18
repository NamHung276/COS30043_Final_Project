<script>
import newsData from '../data/news.json'

export default {
  data() {
    return {
      article: null
    }
  },

  mounted() {

    const id =
      parseInt(this.$route.params.id)

    this.article =
      newsData.find(
        item => item.id === id
      )
  }
}
</script>

<template>

  <div class="container py-4">

    <div
      v-if="article"
      class="card"
    >

      <img
        :src="article.image"
        :alt="article.title"
        class="card-img-top"
        style="
          max-height: 500px;
          object-fit: cover;
        "
      >

      <div class="card-body text-start">

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

        <p>
          {{ article.content }}
        </p>

        <router-link
          to="/gamehub-news"
          class="btn btn-secondary mt-3"
        >
          ← Back to News
        </router-link>

      </div>

    </div>

  </div>

</template>