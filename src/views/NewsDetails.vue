// src/views/NewsDetails.vue
<script>
import newsData from '../data/news.json'

export default {
  data() {
    return {
      article: null,
      relatedArticles: []
    }
  },

    mounted() {
        const id = parseInt(this.$route.params.id)

        this.article =
            newsData.find(item => item.id === id)

        if (this.article) {

            this.relatedArticles =
            newsData
                .filter(item =>
                item.category === this.article.category &&
                item.id !== this.article.id
                )
                .slice(0, 3)

        }
    }
}
</script>

<template>
  <div class="container py-5">

    <div v-if="article">

      <img
        :src="article.image"
        :alt="article.title"
        class="img-fluid rounded mb-4 w-100"
        style="max-height:500px; object-fit:cover;"
      >

      <span class="badge bg-primary mb-3">
        {{ article.category }}
      </span>

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

          <p>
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
      <div
        v-if="relatedArticles.length"
        class="mt-5"
        >

        <h3 class="mb-4">
            Related Articles
        </h3>

        <div class="row">

            <div
            v-for="related in relatedArticles"
            :key="related.id"
            class="col-md-4 mb-4"
            >

            <div class="card h-100">

                <img
                :src="related.image"
                :alt="related.title"
                class="card-img-top"
                style="height: 200px; object-fit: cover;"
                >

                <div class="card-body">

                <span class="badge bg-secondary mb-2">
                    {{ related.category }}
                </span>

                <h6>
                    {{ related.title }}
                </h6>

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

    <div v-else>

      <div class="alert alert-danger">
        Article not found.
      </div>

    </div>

  </div>
</template>