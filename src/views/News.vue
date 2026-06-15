<script>
export default {
  data() {
    return {
      articles: [],
      loading: true,
      searchTerm: ''
    }
  },

  computed: {
    filteredArticles() {
      return this.articles.filter(article => {

        const title =
          article.title || ''

        return title
          .toLowerCase()
          .includes(
            this.searchTerm.toLowerCase()
          )
      })
    }
  },

  async mounted() {
    try {

      const response = await fetch(
        'https://newsapi.org/v2/everything?q="video games"&language=en&sortBy=publishedAt&apiKey=a125829a83b64ea99e6889447f348dc8'
      )

      const data =
        await response.json()

      this.articles =
        data.articles || []

    }
    catch (error) {
      console.error(error)
    }
    finally {
      this.loading = false
    }
  }
}
</script>

<template>
  <div class="container py-4">

    <h1 class="mb-4">
      Gaming News
    </h1>

    <div class="mb-4">

      <input
        type="text"
        class="form-control"
        placeholder="Search news..."
        v-model="searchTerm"
      >

    </div>

    <div v-if="loading">
      Loading news...
    </div>

    <div
      v-else
      class="row"
    >

      <div
        class="col-md-4 mb-4"
        v-for="article in filteredArticles"
        :key="article.url"
      >

        <div class="card h-100">

          <img
            v-if="article.urlToImage"
            :src="article.urlToImage"
            class="card-img-top"
            :alt="article.title"
          >

          <div class="card-body">

            <p class="text-muted small mb-2">
              {{ article.source.name }}
            </p>

            <h5 class="card-title">
              {{ article.title }}
            </h5>

            <p class="card-text">
              {{ article.description
                  ? article.description.slice(0, 120) + '...'
                  : 'No description available.'
              }}
            </p>

          </div>

          <div class="card-footer">

            <a
              :href="article.url"
              target="_blank"
              rel="noopener noreferrer"
              class="btn btn-primary"
            >
              Read More
            </a>

          </div>

        </div>

      </div>

    </div>

  </div>
</template>