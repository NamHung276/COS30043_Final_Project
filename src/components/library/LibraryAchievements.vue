<script setup>
import { computed } from 'vue';

const props = defineProps({
  achievements: {
    type: Array,
    required: true
  }
});

const unlockedCount = computed(() => props.achievements.filter(a => a.unlocked).length);
const totalCount = computed(() => props.achievements.length);
const completionPercentage = computed(() => totalCount.value ? Math.round((unlockedCount.value / totalCount.value) * 100) : 0);

</script>

<template>
  <div class="library-achievements bg-dark bg-opacity-50 rounded-4 p-4 border border-secondary border-opacity-25 h-100">
    <h5 class="fw-bold mb-4"><i class="bi bi-trophy-fill text-warning me-2"></i>Achievements</h5>
    
    <div class="d-flex align-items-center justify-content-between mb-3">
      <span class="text-muted fw-bold text-uppercase" style="letter-spacing: 1px; font-size: 0.85rem;">Completion</span>
      <span class="fs-4 fw-bold text-white">{{ completionPercentage }}%</span>
    </div>
    
    <div class="progress mb-4 bg-secondary bg-opacity-25" style="height: 12px; border-radius: 6px;">
      <div class="progress-bar bg-warning progress-bar-striped progress-bar-animated" role="progressbar" :style="{ width: completionPercentage + '%' }"></div>
    </div>
    
    <h6 class="fw-bold mb-3 mt-4 text-muted d-flex justify-content-between">
      <span>Unlocked</span>
      <span>{{ unlockedCount }} / {{ totalCount }}</span>
    </h6>
    
    <div class="ld-achievements-list d-flex flex-column gap-2" style="max-height: 400px; overflow-y: auto;">
      <div v-for="ach in achievements" :key="ach.id" class="achievement-card d-flex align-items-center gap-3 p-3 rounded-4 bg-black bg-opacity-25 border border-secondary border-opacity-10 position-relative overflow-hidden" :class="{'locked': !ach.unlocked}">
        <!-- Glow effect for unlocked -->
        <div v-if="ach.unlocked" class="position-absolute top-0 start-0 w-100 h-100 bg-warning pointer-events-none" style="opacity: 0.1;"></div>
        
        <div class="achievement-icon rounded-circle d-flex align-items-center justify-content-center" :class="ach.unlocked ? 'bg-warning bg-opacity-25 border border-warning' : 'bg-secondary bg-opacity-25 border border-secondary'">
          <i class="bi fs-4" :class="ach.unlocked ? 'bi-trophy-fill text-warning' : 'bi-lock-fill text-secondary'"></i>
        </div>
        
        <div class="flex-grow-1">
          <h6 class="mb-1 fw-bold text-white" :class="{'text-muted': !ach.unlocked}">{{ ach.title }}</h6>
          <p class="mb-0 small text-muted">{{ ach.unlocked ? 'Unlocked just now' : 'Locked achievement' }}</p>
        </div>
        
        <div v-if="ach.unlocked" class="badge bg-warning text-dark px-2 py-1 rounded-3 fw-bold">+50 XP</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.achievement-card {
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.achievement-card:not(.locked):hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(255, 193, 7, 0.1) !important;
}
.achievement-card.locked {
  filter: grayscale(100%);
  opacity: 0.7;
}
.achievement-icon {
  width: 48px;
  height: 48px;
}
</style>
