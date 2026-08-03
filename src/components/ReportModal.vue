<script setup>
import { ref } from 'vue';

const props = defineProps({
  show: Boolean,
  targetName: String,
  targetType: String
});

const emit = defineEmits(['close', 'submit']);

const reason = ref('');
const isSubmitting = ref(false);
const error = ref('');

const close = () => {
  reason.value = '';
  error.value = '';
  emit('close');
};

const submit = async () => {
  if (!reason.value.trim()) {
    error.value = "Please provide a reason for the report.";
    return;
  }
  
  isSubmitting.value = true;
  error.value = '';
  
  try {
    emit('submit', reason.value.trim());
    reason.value = '';
  } catch (err) {
    error.value = "Failed to submit report. Please try again later.";
  } finally {
    isSubmitting.value = false;
  }
};
</script>

<template>
  <div v-if="show" class="report-modal-overlay" @click.self="close">
    <div class="report-modal">
      <button class="close-btn" @click="close" aria-label="Close modal">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>

      <div class="modal-header">
        <div class="modal-icon text-danger">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M4 15s1-1 4-1 5 2 8 2 4-1 4-1V3s-1 1-4 1-5-2-8-2-4 1-4 1z"></path>
            <line x1="4" y1="22" x2="4" y2="15"></line>
          </svg>
        </div>
        <h2>Report {{ targetType }}</h2>
        <p class="modal-subtitle">You are reporting: <strong>{{ targetName }}</strong></p>
      </div>

      <div class="modal-body">
        <label for="report-reason" class="form-label">Reason for reporting</label>
        <textarea 
          id="report-reason" 
          v-model="reason" 
          placeholder="Please describe why you are reporting this content..."
          class="form-textarea"
          rows="4"
        ></textarea>
        <p v-if="error" class="error-msg">{{ error }}</p>
      </div>

      <div class="modal-footer">
        <button class="btn btn-secondary" @click="close" :disabled="isSubmitting">Cancel</button>
        <button class="btn btn-danger" @click="submit" :disabled="isSubmitting">
          <span v-if="isSubmitting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
          Submit Report
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.report-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.75);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1050;
  animation: fadeIn 0.2s ease;
  padding: 1rem;
}

.report-modal {
  background: var(--bg-surface);
  border: 1px solid var(--border-glass);
  border-radius: 12px;
  width: 100%;
  max-width: 500px;
  position: relative;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  animation: slideUp 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: transparent;
  border: none;
  color: var(--text-muted);
  cursor: pointer;
  transition: color 0.2s;
  padding: 0;
  display: flex;
}
.close-btn:hover {
  color: var(--text-primary);
}

.modal-header {
  padding: 2rem 2rem 1rem;
  text-align: center;
}
.modal-icon {
  margin-bottom: 1rem;
}
.modal-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
}
.modal-subtitle {
  color: var(--text-secondary);
  font-size: 0.95rem;
  margin: 0;
}

.modal-body {
  padding: 0 2rem 1.5rem;
}
.form-label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
  font-size: 0.9rem;
}
.form-textarea {
  width: 100%;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-glass);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: var(--text-primary);
  font-family: inherit;
  font-size: 0.95rem;
  resize: vertical;
  transition: border-color 0.2s;
}
.form-textarea:focus {
  outline: none;
  border-color: rgba(220, 53, 69, 0.5);
  background: rgba(0, 0, 0, 0.3);
}
.error-msg {
  color: #dc3545;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.modal-footer {
  padding: 1.5rem 2rem;
  border-top: 1px solid var(--border-glass);
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  background: rgba(0, 0, 0, 0.1);
  border-bottom-left-radius: 12px;
  border-bottom-right-radius: 12px;
}
.btn {
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.95rem;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}
.btn-secondary {
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--border-glass);
}
.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.05);
}
.btn-danger {
  background: #dc3545;
  color: white;
}
.btn-danger:hover {
  background: #c82333;
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
@keyframes slideUp {
  from { opacity: 0; transform: translateY(20px) scale(0.95); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
</style>
