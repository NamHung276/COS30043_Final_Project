<script setup>
import { ref, computed } from 'vue';

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

const emit = defineEmits(['add-screenshot', 'remove-screenshot']);

const newScreenshotUrl = ref('');
const lightboxImage = ref(null);

const apiScreenshots = computed(() => {
  if (!props.game.screenshots) return [];
  // FreeToGame uses 'image', RAWG might use 'image' or 'url'
  return props.game.screenshots.map(s => s.image || s.url || s).filter(s => typeof s === 'string');
});

const userScreenshots = computed(() => {
  return props.purchase.screenshots || [];
});

const allScreenshots = computed(() => {
  return [...userScreenshots.value, ...apiScreenshots.value];
});

const handleAdd = () => {
  if (newScreenshotUrl.value.trim()) {
    emit('add-screenshot', newScreenshotUrl.value.trim());
    newScreenshotUrl.value = '';
  }
};

const handleRemove = (url) => {
  if(confirm("Remove this screenshot?")) {
    emit('remove-screenshot', url);
  }
};

const openLightbox = (url) => {
  lightboxImage.value = url;
};
const closeLightbox = () => {
  lightboxImage.value = null;
};
</script>

<template>
  <div class="library-gallery mb-5">
    <div class="d-flex justify-content-between align-items-end mb-4">
      <h4 class="fw-bold mb-0"><i class="bi bi-images text-info me-2"></i> Screenshot Gallery</h4>
      
      <div class="d-flex gap-2">
        <input v-model="newScreenshotUrl" type="url" class="form-control form-control-sm bg-dark text-white border-secondary" placeholder="Paste image URL..." style="width: 250px;">
        <button @click="handleAdd" class="btn btn-sm btn-outline-info rounded-3" :disabled="!newScreenshotUrl">Add</button>
      </div>
    </div>
    
    <div v-if="allScreenshots.length > 0" class="row g-3">
      <div v-for="(img, idx) in allScreenshots" :key="idx" class="col-md-4 col-sm-6">
        <div class="gallery-item position-relative rounded-4 overflow-hidden shadow-sm border border-secondary border-opacity-25 group">
          <img :src="img" class="w-100 object-fit-cover" style="height: 200px; cursor: pointer;" @click="openLightbox(img)" alt="Screenshot" />
          
          <!-- Delete overlay only for user screenshots -->
          <div v-if="userScreenshots.includes(img)" class="position-absolute top-0 end-0 p-2 opacity-0 group-hover-opacity-100 transition-all">
            <button @click.stop="handleRemove(img)" class="btn btn-danger btn-sm rounded-circle p-1 shadow" style="width: 28px; height: 28px; line-height: 1;"><i class="bi bi-trash"></i></button>
          </div>
          
          <div class="position-absolute bottom-0 start-0 w-100 p-2 bg-dark bg-opacity-75 backdrop-blur opacity-0 group-hover-opacity-100 transition-all text-center" style="pointer-events: none;">
            <i class="bi bi-arrows-fullscreen text-white"></i>
          </div>
        </div>
      </div>
    </div>
    
    <div v-else class="bg-dark bg-opacity-25 rounded-4 p-5 text-center border border-secondary border-opacity-25">
      <img src="https://illustrations.popsy.co/amber/digital-nomad.svg" alt="Empty Gallery" style="height: 150px; opacity: 0.5; filter: grayscale(100%);" class="mb-3">
      <h5 class="text-white mb-2">No Screenshots Yet</h5>
      <p class="text-muted mb-0">Capture your favorite moments and paste the URLs here to build your personal gallery.</p>
    </div>

    <!-- Lightbox -->
    <div v-if="lightboxImage" class="lightbox-overlay position-fixed top-0 start-0 w-100 h-100 z-3 d-flex align-items-center justify-content-center bg-black bg-opacity-75 backdrop-blur" @click="closeLightbox">
      <button class="btn btn-dark position-absolute top-0 end-0 m-4 rounded-circle p-2 border-secondary shadow-lg" @click="closeLightbox">
        <i class="bi bi-x-lg"></i>
      </button>
      <img :src="lightboxImage" class="img-fluid rounded-4 shadow-lg border border-secondary" style="max-height: 90vh; max-width: 90vw; object-fit: contain;" @click.stop />
    </div>
  </div>
</template>

<style scoped>
.gallery-item {
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}
.gallery-item:hover {
  transform: translateY(-5px);
  box-shadow: 0 10px 25px rgba(0,0,0,0.5) !important;
  z-index: 2;
}
.group:hover .group-hover-opacity-100 {
  opacity: 1 !important;
}
.backdrop-blur {
  backdrop-filter: blur(5px);
}
.lightbox-overlay {
  z-index: 1050;
  animation: fadeIn 0.2s ease-out;
}
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>
