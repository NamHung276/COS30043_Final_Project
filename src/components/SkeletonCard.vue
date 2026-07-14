// src/components/SkeletonCard.vue
<template>
  <div class="skeleton-card-wrap" aria-hidden="true">
    <!-- Image area -->
    <div class="skeleton-img"></div>

    <!-- Body -->
    <div class="skeleton-body">
      <!-- Title lines -->
      <div class="skeleton-line" style="width: 88%;"></div>
      <div class="skeleton-line" style="width: 62%; margin-top: -2px;"></div>

      <!-- Genre tags -->
      <div class="skeleton-tags">
        <div class="skeleton-tag"></div>
        <div class="skeleton-tag" style="width: 52px;"></div>
      </div>

      <!-- Rating bar -->
      <div class="skeleton-rating-bar"></div>
      <div class="skeleton-line" style="width: 50%; height: 10px; margin-top: 4px;"></div>
    </div>
  </div>
</template>

<style scoped>
.skeleton-card-wrap {
  display: flex;
  flex-direction: column;
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(255, 255, 255, 0.06);
  border-radius: 14px;
  overflow: hidden;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

/* Shimmer keyframes */
@keyframes shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.skeleton-img {
  width: 100%;
  height: 200px;
  background: linear-gradient(
    90deg,
    rgba(30, 41, 69, 0.8) 25%,
    rgba(60, 80, 130, 0.5) 50%,
    rgba(30, 41, 69, 0.8) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.6s ease-in-out infinite;
  flex-shrink: 0;
}

.skeleton-body {
  padding: 16px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.skeleton-line {
  height: 13px;
  border-radius: 6px;
  background: linear-gradient(
    90deg,
    rgba(30, 41, 69, 0.9) 25%,
    rgba(60, 80, 130, 0.45) 50%,
    rgba(30, 41, 69, 0.9) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.6s ease-in-out infinite;
}

.skeleton-tags {
  display: flex;
  gap: 6px;
  margin-top: 4px;
}
.skeleton-tag {
  height: 22px;
  width: 68px;
  border-radius: 20px;
  background: linear-gradient(
    90deg,
    rgba(124, 58, 237, 0.12) 25%,
    rgba(124, 58, 237, 0.22) 50%,
    rgba(124, 58, 237, 0.12) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.6s ease-in-out infinite;
}

.skeleton-rating-bar {
  height: 4px;
  border-radius: 2px;
  width: 100%;
  margin-top: 6px;
  background: linear-gradient(
    90deg,
    rgba(30, 41, 69, 0.9) 25%,
    rgba(124, 58, 237, 0.3) 50%,
    rgba(30, 41, 69, 0.9) 75%
  );
  background-size: 200% 100%;
  animation: shimmer 1.6s ease-in-out infinite;
}
</style>
