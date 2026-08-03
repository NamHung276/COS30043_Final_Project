<script setup>
import { computed } from 'vue';

const props = defineProps({
  game: {
    type: Object,
    required: true
  },
  purchase: {
    type: Object,
    required: true
  }
});

const simulatedLivePlayers = computed(() => {
  if (props.game.added) {
    return (props.game.added * 1.5).toFixed(0).replace(/\B(?=(\d{3})+(?!\d))/g, ",");
  }
  return "8,321";
});
</script>

<template>
  <div class="row g-4 mb-4">
    <!-- Community Stats -->
    <div class="col-lg-5">
      <div class="ld-stats-card bg-dark bg-opacity-50 rounded-4 p-4 border border-secondary border-opacity-25 h-100">
        <h5 class="fw-bold mb-4 text-white"><i class="bi bi-people-fill text-primary me-2"></i>Community Overview</h5>
        
        <div class="d-flex flex-column gap-3">
          <div class="d-flex justify-content-between align-items-center">
            <span class="text-muted"><i class="bi bi-broadcast text-danger me-2"></i>Live Players</span>
            <span class="text-white fw-bold fs-5">{{ simulatedLivePlayers }}</span>
          </div>
          
          <hr class="border-secondary opacity-25 my-1">
          
          <div class="d-flex justify-content-between align-items-center">
            <span class="text-muted">Metacritic</span>
            <span class="badge" :class="game.metacritic >= 75 ? 'bg-success' : (game.metacritic >= 50 ? 'bg-warning' : 'bg-danger')" v-if="game.metacritic">
              {{ game.metacritic }}
            </span>
            <span v-else class="text-muted fw-bold">N/A</span>
          </div>
          
          <div class="d-flex justify-content-between align-items-center">
            <span class="text-muted">Community Rating</span>
            <span class="text-white fw-bold"><i class="bi bi-star-fill text-warning me-1"></i> {{ game.rating || 'N/A' }} / 5</span>
          </div>
          
          <div class="d-flex justify-content-between align-items-center">
            <span class="text-muted">Total Reviews</span>
            <span class="text-white fw-bold">{{ game.ratings_count ? game.ratings_count.toLocaleString() : 0 }}</span>
          </div>

          <div class="mt-2 p-3 bg-primary bg-opacity-10 rounded-3 border border-primary border-opacity-25 text-center">
            <span class="text-primary fw-bold"><i class="bi bi-graph-up-arrow me-2"></i> Trending in Top 100</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Friends Activity -->
    <div class="col-lg-7">
      <div class="bg-dark bg-opacity-25 rounded-4 p-4 border border-secondary border-opacity-25 h-100 d-flex flex-column">
        <h5 class="fw-bold mb-4 text-white"><i class="bi bi-person-lines-fill text-success me-2"></i>Friends Activity</h5>
        
        <div class="flex-grow-1 d-flex flex-column align-items-center justify-content-center text-center text-muted" style="min-height: 200px;">
          <div class="position-relative mb-3">
            <i class="bi bi-people fs-1 opacity-50"></i>
            <i class="bi bi-search position-absolute text-success" style="bottom: 0; right: -5px; font-size: 1rem;"></i>
          </div>
          <h6 class="text-white mb-2">No friends own this game yet.</h6>
          <p class="small mb-4" style="max-width: 300px;">Share this game with your friends to compare achievements and play together!</p>
          <button class="btn btn-outline-success rounded-pill px-4" @click="$emit('share')"><i class="bi bi-share-fill me-2"></i>Share Link</button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.ld-stats-card {
  transition: transform 0.2s ease, background-color 0.2s ease;
}
.ld-stats-card:hover {
  transform: translateY(-2px);
  background-color: rgba(255,255,255,0.05) !important;
}
</style>
