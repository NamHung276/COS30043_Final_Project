<script setup>
import { ref } from 'vue';
import CurrencyConverter from '../components/CurrencyConverter.vue';
import CurrencyChart from '../components/CurrencyChart.vue';

const currentFrom = ref('USD');
const currentTo = ref('EUR');

const handleCurrencyChange = (data) => {
  if (data && data.from && data.to) {
    currentFrom.value = data.from;
    currentTo.value = data.to;
  }
};
</script>

<template>
  <div class="converter-page">
    <div class="converter-container">
      <div class="text-center mb-5">
        <h1 class="display-4 fw-bold text-white mb-3">
          Currency <span class="text-primary-var">Converter</span>
        </h1>
        <p class="text-muted fs-5 mx-auto" style="max-width: 600px;">
          Check real-time exchange rates to see exactly how much you're paying for games in different regions. 
          Powered by the European Central Bank.
        </p>
      </div>

      <div class="converter-wrapper">
        <div class="converter-col">
          <CurrencyConverter 
            :initialAmount="1.0" 
            :inline="false" 
            @currency-change="handleCurrencyChange"
          />
          <CurrencyChart 
            :from="currentFrom" 
            :to="currentTo" 
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.converter-page {
  min-height: 100vh;
  background: var(--bg-deep, #0f0f13);
  padding: 6rem 1rem;
  display: flex;
  justify-content: center;
}

.converter-container {
  width: 100%;
  max-width: 800px;
}

.text-primary-var {
  color: var(--accent, #6366f1);
}

.converter-wrapper {
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.converter-col {
  width: 100%;
  max-width: 500px;
  display: flex;
  flex-direction: column;
}

.converter-wrapper :deep(.currency-converter) {
  width: 100%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
  border: 1px solid rgba(255, 255, 255, 0.05);
}
</style>
