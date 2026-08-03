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

const emit = defineEmits(['launch', 'verify', 'reinstall', 'hide', 'archive', 'export-notes']);

const simulatedInstallSize = computed(() => {
  if (props.game.name) {
    const hash = props.game.name.length * 14;
    return `${hash > 150 ? hash : hash + 20} GB`;
  }
  return '60 GB';
});

const installFolder = computed(() => {
  const slug = props.game.slug || props.game.name?.toLowerCase().replace(/\s+/g, '-') || 'game';
  return `C:\\GameHub\\Games\\${slug}`;
});

const copyInstallPath = () => {
  navigator.clipboard.writeText(installFolder.value);
  alert("Install path copied to clipboard!");
};
</script>

<template>
  <div class="library-sidebar d-flex flex-column gap-4">
    
    <!-- Game Information -->
    <div v-if="purchase.status === 'installed' || purchase.status === 'playing' || purchase.status === 'completed'" class="bg-dark bg-opacity-50 rounded-4 p-4 border border-secondary border-opacity-25 shadow-sm">
      <h5 class="fw-bold mb-4 text-white"><i class="bi bi-hdd-fill text-info me-2"></i>Installation Info</h5>
      
      <div class="d-flex flex-column gap-3">
        <div class="d-flex justify-content-between">
          <span class="text-muted small text-uppercase fw-bold">Install Size</span>
          <span class="text-white fw-bold">{{ simulatedInstallSize }}</span>
        </div>
        <div class="d-flex justify-content-between">
          <span class="text-muted small text-uppercase fw-bold">Cloud Save</span>
          <span class="text-success fw-bold"><i class="bi bi-cloud-check-fill me-1"></i> Synced</span>
        </div>
        <div class="d-flex justify-content-between">
          <span class="text-muted small text-uppercase fw-bold">Version</span>
          <span class="text-white fw-bold">v1.0.4.2</span>
        </div>
        <div class="d-flex justify-content-between" v-if="game.id">
          <span class="text-muted small text-uppercase fw-bold">App ID</span>
          <span class="text-white fw-bold">{{ game.id }}</span>
        </div>
        <div class="d-flex justify-content-between">
          <span class="text-muted small text-uppercase fw-bold">Controller</span>
          <span class="text-white fw-bold"><i class="bi bi-controller me-1"></i> Full Support</span>
        </div>
        
        <hr class="border-secondary opacity-25 my-2">
        
        <div>
          <div class="d-flex justify-content-between align-items-center mb-1">
            <span class="text-muted small text-uppercase fw-bold">Install Folder</span>
            <button @click="copyInstallPath" class="btn btn-sm btn-link text-info p-0 text-decoration-none"><i class="bi bi-copy"></i> Copy</button>
          </div>
          <code class="d-block p-2 bg-black bg-opacity-50 rounded-3 text-info text-truncate border border-secondary border-opacity-25" style="font-size: 0.8rem;">
            {{ installFolder }}
          </code>
        </div>
      </div>
    </div>

    <!-- Manage Game Actions -->
    <div class="bg-dark bg-opacity-50 rounded-4 p-4 border border-secondary border-opacity-25 shadow-sm">
      <h5 class="fw-bold mb-4 text-white"><i class="bi bi-gear-fill text-secondary me-2"></i>Manage Game</h5>
      
      <div class="d-flex flex-column gap-2">
        <button v-if="purchase.status === 'installed' || purchase.status === 'completed'" @click="$emit('launch')" class="btn btn-success fw-bold py-2 mb-2">
          <i class="bi bi-play-fill me-1"></i> Launch Game
        </button>
        
        <button v-if="purchase.status === 'installed' || purchase.status === 'completed'" @click="$emit('verify')" class="btn btn-dark border-secondary text-start hover-highlight py-2">
          <i class="bi bi-shield-check me-2 text-info"></i> Verify File Integrity
        </button>
        
        <button v-if="purchase.notes" @click="$emit('export-notes')" class="btn btn-dark border-secondary text-start hover-highlight py-2">
          <i class="bi bi-download me-2 text-warning"></i> Export Journal (MD)
        </button>
        
        <button @click="$emit('hide')" class="btn btn-dark border-secondary text-start hover-highlight py-2">
          <i class="bi bi-eye-slash me-2 text-muted"></i> Hide from Library
        </button>
        
        <button v-if="purchase.status === 'installed' || purchase.status === 'completed'" @click="$emit('reinstall')" class="btn btn-dark border-secondary text-start text-danger hover-highlight py-2 mt-2">
          <i class="bi bi-arrow-clockwise me-2"></i> Force Reinstall
        </button>
      </div>
    </div>

  </div>
</template>

<style scoped>
.hover-highlight {
  transition: background-color 0.2s ease, transform 0.2s ease;
}
.hover-highlight:hover {
  background-color: rgba(255,255,255,0.05) !important;
  transform: translateX(2px);
}
</style>
