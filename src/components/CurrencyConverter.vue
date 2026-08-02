<script setup>
import { ref, onMounted, watch } from 'vue';
import { backendApi } from '../services/api';

const props = defineProps({
  initialAmount: {
    type: Number,
    default: 1.0
  },
  initialFrom: {
    type: String,
    default: 'USD'
  },
  inline: {
    type: Boolean,
    default: false
  },
  asModal: {
    type: Boolean,
    default: false
  },
  fixedFrom: {
    type: Boolean,
    default: false
  }
});

const currencies = ref({});
const fromCurrency = ref(props.initialFrom);
const toCurrency = ref('EUR');
const amount = ref(props.initialAmount);
const convertedResult = ref(null);
const loading = ref(false);
const error = ref(null);

const emit = defineEmits(['close', 'currency-change']);

const fetchCurrencies = async () => {
  try {
    const res = await backendApi.get('/currency/list');
    currencies.value = res.data;
    emit('currency-change', { from: fromCurrency.value, to: toCurrency.value });
  } catch (err) {
    console.error(err);
    error.value = "Unable to load currency list.";
  }
};

const convert = async () => {
  if (!amount.value || amount.value <= 0) return;
  
  loading.value = true;
  error.value = null;
  
  try {
    const res = await backendApi.get('/currency/convert', {
      params: {
        from_curr: fromCurrency.value,
        to_curr: toCurrency.value,
        amount: amount.value
      }
    });
    
    convertedResult.value = res.data;
    emit('currency-change', { from: fromCurrency.value, to: toCurrency.value });
  } catch (err) {
    console.error(err);
    error.value = "Failed to convert currency.";
    convertedResult.value = null;
  } finally {
    loading.value = false;
  }
};

const swapCurrencies = () => {
  const temp = fromCurrency.value;
  fromCurrency.value = toCurrency.value;
  toCurrency.value = temp;
  convert();
};

watch(() => props.initialAmount, (newVal) => {
  if (newVal !== amount.value) {
    amount.value = newVal;
    convert();
  }
});

onMounted(() => {
  fetchCurrencies();
  convert();
});
</script>

<template>
  <teleport to="body" :disabled="!asModal">
    <div :class="{ 'converter-backdrop': asModal }" @click.self="asModal && emit('close')">
      <div class="currency-converter" :class="{ 'is-inline': inline }">
        <div v-if="!inline" class="converter-header">
      <div style="display: flex; align-items: center; gap: 0.75rem; flex: 1;">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="12" y1="1" x2="12" y2="23"></line>
          <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
        </svg>
        <h2>Currency Converter</h2>
      </div>
      <button class="close-btn" @click="emit('close')" aria-label="Close">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
    </div>

    <div class="converter-body">
      <div class="input-group">
        <label>Amount</label>
        <input type="number" v-model="amount" min="0" step="0.01" @change="convert" />
      </div>

      <div class="currency-controls">
        <div class="select-group">
          <label>From</label>
          <select v-model="fromCurrency" @change="convert" :disabled="fixedFrom">
            <option v-for="(name, code) in currencies" :key="code" :value="code">
              {{ code }} - {{ name }}
            </option>
          </select>
        </div>

        <button v-if="!fixedFrom" class="swap-btn" @click="swapCurrencies" title="Swap currencies" :disabled="loading">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="16 3 21 3 21 8"></polyline>
            <line x1="4" y1="14" x2="21" y2="3"></line>
            <polyline points="8 21 3 21 3 16"></polyline>
            <line x1="20" y1="10" x2="3" y2="21"></line>
          </svg>
        </button>

        <div class="select-group">
          <label>To</label>
          <select v-model="toCurrency" @change="convert">
            <option v-for="(name, code) in currencies" :key="code" :value="code">
              {{ code }} - {{ name }}
            </option>
          </select>
        </div>
      </div>
      
      <p v-if="error" class="error-text">{{ error }}</p>

      <div class="result-box" :class="{ loading: loading }">
        <div class="result-label">Converted Amount</div>
        <div class="result-value">
          <span v-if="loading" class="spinner"></span>
          <span v-else-if="convertedResult">
            {{ new Intl.NumberFormat('en-US', { style: 'currency', currency: toCurrency }).format(convertedResult.converted_amount) }}
          </span>
          <span v-else>---</span>
        </div>
        <div v-if="convertedResult && !loading" class="exchange-rate">
          1 {{ fromCurrency }} = {{ convertedResult.rates[toCurrency] }} {{ toCurrency }}
        </div>
      </div>
    </div>
      </div>
    </div>
  </teleport>
</template>

<style scoped>
.converter-backdrop {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  backdrop-filter: blur(8px);
}

.currency-converter {
  background: var(--bg-surface, #1e1e24);
  border: 1px solid var(--border-color, #333);
  border-radius: 12px;
  padding: 1.5rem;
  color: var(--text-primary, #fff);
  font-family: inherit;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  width: 100%;
  max-width: 480px;
}

.currency-converter.is-inline {
  background: transparent;
  border: none;
  box-shadow: none;
  padding: 0;
}

.converter-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  color: var(--accent, #6366f1);
}

.converter-header h2 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary, #fff);
}

.close-btn {
  background: transparent;
  border: none;
  color: var(--text-secondary, #aaa);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.close-btn:hover {
  background: var(--overlay-light, rgba(255, 255, 255, 0.1));
  color: var(--text-primary, #fff);
}

.converter-body {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.input-group, .select-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  width: 100%;
}

label {
  font-size: 0.85rem;
  color: var(--text-secondary, #aaa);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
}

input, select {
  background: var(--overlay-light, rgba(255, 255, 255, 0.05));
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  border-radius: 8px;
  padding: 0.75rem 1rem;
  color: var(--text-primary, #fff);
  font-size: 1rem;
  transition: all 0.2s ease;
  outline: none;
}

select option {
  background: var(--bg-surface, #1e1e24);
  color: var(--text-primary, #fff);
}

select:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  background: var(--overlay-medium, rgba(255, 255, 255, 0.08));
}

input:focus, select:focus {
  border-color: var(--accent, #6366f1);
  background: var(--overlay-medium, rgba(255, 255, 255, 0.08));
}

.currency-controls {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.swap-btn {
  background: var(--overlay-light, rgba(255, 255, 255, 0.05));
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.1));
  color: var(--text-primary, #fff);
  border-radius: 50%;
  width: 42px;
  height: 42px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s ease;
  transform: rotate(90deg);
}

.swap-btn:hover {
  background: var(--accent, #6366f1);
  border-color: var(--accent, #6366f1);
  color: #fff;
  transform: rotate(270deg);
}

.swap-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.result-box {
  background: var(--overlay-light, rgba(255, 255, 255, 0.03));
  border-radius: 8px;
  padding: 1.25rem;
  text-align: center;
  border: 1px solid var(--border-color, rgba(255, 255, 255, 0.05));
  transition: opacity 0.2s;
}

.result-box.loading {
  opacity: 0.6;
}

.result-label {
  font-size: 0.9rem;
  color: var(--text-secondary, #aaa);
  margin-bottom: 0.5rem;
}

.result-value {
  font-size: 2rem;
  font-weight: 700;
  color: var(--accent, #6366f1);
  margin-bottom: 0.5rem;
  min-height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.exchange-rate {
  font-size: 0.85rem;
  color: var(--text-secondary, #888);
}

.error-text {
  color: #ef4444;
  font-size: 0.9rem;
  margin: 0;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--overlay-medium, rgba(255, 255, 255, 0.1));
  border-top-color: var(--accent, #6366f1);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
