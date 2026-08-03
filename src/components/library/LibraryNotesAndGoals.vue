<script setup>
import { ref, computed, watch } from 'vue';
import { MdEditor } from 'md-editor-v3';
import 'md-editor-v3/lib/style.css';

const props = defineProps({
  purchase: {
    type: Object,
    required: true
  }
});

const emit = defineEmits(['update-notes', 'update-goals']);

const notes = ref(props.purchase.notes || '');
const savingNotes = ref(false);

const goals = ref(props.purchase.goals || []);
const newGoal = ref('');

const completionPercentage = computed(() => {
  if (goals.value.length === 0) return 0;
  return Math.round((goals.value.filter(g => g.completed).length / goals.value.length) * 100);
});

// Auto-save notes mechanism with debounce
let saveTimeout = null;
const handleNotesChange = (val) => {
  notes.value = val;
  savingNotes.value = true;
  clearTimeout(saveTimeout);
  saveTimeout = setTimeout(() => {
    emit('update-notes', notes.value);
    setTimeout(() => { savingNotes.value = false; }, 500); // Fake delay for UI feedback
  }, 1000);
};

const addGoal = () => {
  if (newGoal.value.trim()) {
    goals.value.push({ id: Date.now(), text: newGoal.value.trim(), completed: false });
    newGoal.value = '';
    emit('update-goals', goals.value);
  }
};

const toggleGoal = (id) => {
  const goal = goals.value.find(g => g.id === id);
  if (goal) {
    goal.completed = !goal.completed;
    emit('update-goals', goals.value);
  }
};

const removeGoal = (id) => {
  if(confirm("Remove this goal?")) {
    goals.value = goals.value.filter(g => g.id !== id);
    emit('update-goals', goals.value);
  }
};
</script>

<template>
  <div class="row g-4 mb-4">
    <!-- Notes Section -->
    <div class="col-lg-7">
      <div class="bg-dark bg-opacity-25 rounded-4 p-4 border border-secondary border-opacity-25 h-100 d-flex flex-column">
        <h4 class="fw-bold mb-3 d-flex justify-content-between align-items-center text-white">
          <span><i class="bi bi-journal-richtext text-info me-2"></i> My Journal</span>
          <span v-if="savingNotes" class="badge bg-success bg-opacity-75 text-white" style="font-size: 0.75rem;"><i class="bi bi-cloud-arrow-up-fill me-1"></i> Saving</span>
        </h4>
        <div class="flex-grow-1 overflow-hidden rounded-3 border border-secondary border-opacity-25" style="min-height: 400px;">
          <MdEditor 
            v-model="notes" 
            theme="dark" 
            language="en-US" 
            @onChange="handleNotesChange"
            :preview="false"
            class="h-100"
          />
        </div>
      </div>
    </div>

    <!-- Personal Goals Section -->
    <div class="col-lg-5">
      <div class="bg-dark bg-opacity-25 rounded-4 p-4 border border-secondary border-opacity-25 h-100">
        <h4 class="fw-bold mb-4 text-white"><i class="bi bi-list-check text-warning me-2"></i> Personal Goals</h4>
        
        <div class="d-flex align-items-center justify-content-between mb-2">
          <span class="text-muted small fw-bold text-uppercase">Completion</span>
          <span class="fw-bold text-white">{{ completionPercentage }}%</span>
        </div>
        <div class="progress mb-4 bg-secondary bg-opacity-25" style="height: 6px; border-radius: 3px;">
          <div class="progress-bar bg-warning" role="progressbar" :style="{ width: completionPercentage + '%' }"></div>
        </div>

        <form @submit.prevent="addGoal" class="mb-4 d-flex gap-2">
          <input v-model="newGoal" type="text" class="form-control bg-dark text-white border-secondary" placeholder="e.g. Finish Main Story">
          <button type="submit" class="btn btn-warning fw-bold text-dark" :disabled="!newGoal">Add</button>
        </form>

        <div v-if="goals.length > 0" class="d-flex flex-column gap-2" style="max-height: 300px; overflow-y: auto;">
          <div v-for="goal in goals" :key="goal.id" class="d-flex align-items-center p-3 rounded-3 bg-black bg-opacity-25 border border-secondary border-opacity-25 transition-all hover-highlight group">
            <div class="form-check m-0 d-flex align-items-center gap-3 flex-grow-1 cursor-pointer" @click="toggleGoal(goal.id)">
              <input class="form-check-input mt-0 border-secondary" type="checkbox" :checked="goal.completed" style="width: 1.25rem; height: 1.25rem; cursor: pointer;">
              <label class="form-check-label text-white cursor-pointer" :class="{'text-decoration-line-through text-muted opacity-50': goal.completed}" style="padding-top: 2px;">
                {{ goal.text }}
              </label>
            </div>
            <button @click.stop="removeGoal(goal.id)" class="btn btn-sm btn-link text-danger p-0 opacity-0 group-hover-opacity-100 transition-all">
              <i class="bi bi-x-circle-fill fs-5"></i>
            </button>
          </div>
        </div>
        <div v-else class="text-center text-muted py-4">
          <i class="bi bi-target fs-1 mb-2 d-block opacity-50"></i>
          <p class="mb-0">Set your own goals and track your progress!</p>
        </div>

      </div>
    </div>
  </div>
</template>

<style scoped>
.hover-highlight:hover {
  background-color: rgba(255,255,255,0.05) !important;
}
.cursor-pointer {
  cursor: pointer;
}
.group:hover .group-hover-opacity-100 {
  opacity: 1 !important;
}
/* Override md-editor-v3 styles if needed to fit GameHub theme */
:deep(.md-editor) {
  --md-bk-color: rgba(15, 23, 42, 0.5) !important;
  --md-color: #f8fafc !important;
  border: none !important;
}
</style>
