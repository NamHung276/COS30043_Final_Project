<script setup>
import { ref, computed, onMounted, watch } from 'vue';
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

const activeDropdown = ref(null);
const fromSearchQuery = ref('');
const toSearchQuery = ref('');

const formatCurrencyName = (code, name) => {
  if (!name) return code;
  return `${code} - ${name}`;
};

const filteredFromCurrencies = computed(() => {
  const query = fromSearchQuery.value.toLowerCase().trim();
  const currentText = formatCurrencyName(fromCurrency.value, currencies.value[fromCurrency.value] || '').toLowerCase();
  
  if (!query || query === currentText) return currencies.value;
  
  const result = {};
  for (const [code, name] of Object.entries(currencies.value)) {
    if (code.toLowerCase().includes(query) || name.toLowerCase().includes(query)) {
      result[code] = name;
    }
  }
  return result;
});

const filteredToCurrencies = computed(() => {
  const query = toSearchQuery.value.toLowerCase().trim();
  const currentText = formatCurrencyName(toCurrency.value, currencies.value[toCurrency.value] || '').toLowerCase();
  
  if (!query || query === currentText) return currencies.value;
  
  const result = {};
  for (const [code, name] of Object.entries(currencies.value)) {
    if (code.toLowerCase().includes(query) || name.toLowerCase().includes(query)) {
      result[code] = name;
    }
  }
  return result;
});

const openDropdown = (type) => {
  if (type === 'from' && props.fixedFrom) return;
  activeDropdown.value = type;
};

const selectCurrency = (type, code) => {
  if (type === 'from') {
    fromCurrency.value = code;
    fromSearchQuery.value = formatCurrencyName(code, currencies.value[code]);
  } else {
    toCurrency.value = code;
    toSearchQuery.value = formatCurrencyName(code, currencies.value[code]);
  }
  activeDropdown.value = null;
  convert();
};

watch(activeDropdown, (newVal, oldVal) => {
  if (!newVal && oldVal) {
    // Reset to selected currency text if clicked away without selecting
    if (oldVal === 'from') {
      fromSearchQuery.value = formatCurrencyName(fromCurrency.value, currencies.value[fromCurrency.value]);
    } else if (oldVal === 'to') {
      toSearchQuery.value = formatCurrencyName(toCurrency.value, currencies.value[toCurrency.value]);
    }
  }
});

const emit = defineEmits(['close', 'currency-change']);

const fetchCurrencies = async () => {
  try {
    const res = await backendApi.get('/currency/list');
    currencies.value = res.data;
    
    fromSearchQuery.value = formatCurrencyName(fromCurrency.value, currencies.value[fromCurrency.value]);
    toSearchQuery.value = formatCurrencyName(toCurrency.value, currencies.value[toCurrency.value]);
    
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
  
  fromSearchQuery.value = formatCurrencyName(fromCurrency.value, currencies.value[fromCurrency.value]);
  toSearchQuery.value = formatCurrencyName(toCurrency.value, currencies.value[toCurrency.value]);
  
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
        
        <!-- From Currency -->
        <div class="select-group">
          <label>From</label>
          <div class="custom-select-container">
            <div class="combobox-wrapper" :class="{ disabled: fixedFrom }">
              <input 
                type="text" 
                v-model="fromSearchQuery" 
                class="combobox-input" 
                @focus="openDropdown('from')"
                :disabled="fixedFrom"
                placeholder="Search currency..."
              />
              <svg class="combobox-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <div v-if="activeDropdown === 'from'" class="custom-select-dropdown">
              <div class="custom-select-options">
                <div 
                  v-for="(name, code) in filteredFromCurrencies" 
                  :key="code" 
                  class="custom-select-option"
                  :class="{ active: fromCurrency === code }"
                  @click="selectCurrency('from', code)"
                >
                  {{ code }} - {{ name }}
                </div>
                <div v-if="Object.keys(filteredFromCurrencies).length === 0" class="custom-select-empty">
                  No currencies found
                </div>
              </div>
            </div>
          </div>
        </div>

        <button v-if="!fixedFrom" class="swap-btn" @click="swapCurrencies" title="Swap currencies" :disabled="loading">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="16 3 21 3 21 8"></polyline>
            <line x1="4" y1="14" x2="21" y2="3"></line>
            <polyline points="8 21 3 21 3 16"></polyline>
            <line x1="20" y1="10" x2="3" y2="21"></line>
          </svg>
        </button>

        <!-- To Currency -->
        <div class="select-group">
          <label>To</label>
          <div class="custom-select-container">
            <div class="combobox-wrapper">
              <input 
                type="text" 
                v-model="toSearchQuery" 
                class="combobox-input" 
                @focus="openDropdown('to')"
                placeholder="Search currency..."
              />
              <svg class="combobox-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <div v-if="activeDropdown === 'to'" class="custom-select-dropdown">
              <div class="custom-select-options">
                <div 
                  v-for="(name, code) in filteredToCurrencies" 
                  :key="code" 
                  class="custom-select-option"
                  :class="{ active: toCurrency === code }"
                  @click="selectCurrency('to', code)"
                >
                  {{ code }} - {{ name }}
                </div>
                <div v-if="Object.keys(filteredToCurrencies).length === 0" class="custom-select-empty">
                  No currencies found
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <p v-if="error" class="error-text">{{ error }}</p>

      <div v-if="activeDropdown" class="dropdown-overlay-capture" @click="activeDropdown = null"></div>

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

.select-group select:focus,
.combobox-wrapper:focus-within {
  outline: none;
  border-color: rgba(124, 58, 237, 0.5);
  box-shadow: 0 0 0 3px rgba(124, 58, 237, 0.15);
}
.select-group select:disabled,
.combobox-wrapper.disabled {
  opacity: 0.5;
  cursor: not-allowed;
  background: var(--bg-surface-lighter, #191c28);
}

/* Custom Select Dropdown */
.custom-select-container {
  position: relative;
  width: 100%;
}
.combobox-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--bg-surface, #1e2130);
  border: 1px solid var(--border-glass, rgba(255, 255, 255, 0.1));
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s ease;
}
.combobox-input {
  flex: 1;
  width: 100%;
  background: transparent;
  border: none;
  color: var(--text-primary, #ffffff);
  padding: 12px 16px;
  font-size: 0.95rem;
  font-family: inherit;
  outline: none;
}
.combobox-input:disabled {
  cursor: not-allowed;
}
.combobox-icon {
  position: absolute;
  right: 16px;
  pointer-events: none;
  color: var(--text-secondary);
}
.dropdown-overlay-capture {
  position: fixed;
  inset: 0;
  z-index: 9998;
}
.custom-select-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  width: 100%;
  background: #111422;
  border: 1px solid var(--border-glass, rgba(255, 255, 255, 0.1));
  border-radius: 8px;
  z-index: 9999;
  box-shadow: 0 10px 30px rgba(0,0,0,0.8);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.custom-select-options {
  max-height: 240px;
  overflow-y: auto;
}
.custom-select-option {
  padding: 10px 16px;
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--text-secondary);
  transition: all 0.15s ease;
}
.custom-select-option:hover {
  background: rgba(255, 255, 255, 0.05);
  color: white;
}
.custom-select-option.active {
  background: rgba(124, 58, 237, 0.2);
  color: var(--primary-light);
  font-weight: 600;
}
.custom-select-empty {
  padding: 1rem;
  text-align: center;
  color: var(--text-muted);
  font-size: 0.9rem;
}
.dropdown-overlay-capture {
  position: fixed;
  inset: 0;
  z-index: 9998;
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
