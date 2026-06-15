<script>
export default {
  data() {
    return {
      featuredGames: [
        {
          title: 'Minecraft',
          genre: 'Sandbox'
        },
        {
          title: 'Valorant',
          genre: 'FPS'
        },
        {
          title: 'League of Legends',
          genre: 'MOBA'
        }
      ]
    }
  }
}
</script>

<template>
  <div class="text-center mb-5">
    <h1>Welcome to GameHub</h1>
    <p class="lead">
      Discover games, read news, and join the community.
    </p>
  </div>

  <h2 class="mb-4">Featured Games</h2>

  <div class="row">
    <div
      class="col-md-4 mb-4"
      v-for="game in featuredGames"
      :key="game.title"
    >
      <div class="card h-100">
        <div class="card-body">
          <h5 class="card-title">
            {{ game.title }}
          </h5>

          <p class="card-text">
            Genre: {{ game.genre }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>