// What does this component do? It displays a carousel of games. It takes a
title and a list of games as props. // When a user clicks on a game, it
navigates to the game detail page. It also has left and right buttons to scroll
through the games. // The image uses v-lazy-img to lazy load the image. // How
does this code work? // 1. It uses the ref() function to create a reference to
the carousel element. // 2. It uses the defineProps() function to define the
props. // 3. It uses the computed() function to create a computed property. //
4. It uses the watch() function to watch for changes in the props. // 5. It uses
the onMounted() function to run code when the component is mounted. // 6. It
uses the onUnmounted() function to run code when the component is unmounted. //
7. It uses the scrollCarousel() function to scroll the carousel. // 8. It uses
the imageLoaded() function to handle image loading. // 9. It uses the v-lazy-img
directive to lazy load the image. // 10. It uses the card-hover class to add a
hover effect to the cards. // 11. It uses the gd-section class to add a section
style to the carousel. // 12. It uses the gd-carousel class to add a carousel
style to the carousel. // 13. It uses the gd-carousel-card class to add a card
style to the cards. // 14. It uses the gd-carousel-img class to add an image
style to the images. // 15. It uses the gd-carousel-body class to add a body
style to the cards. // 16. It uses the gd-carousel-btn class to add a button
style to the buttons. // 17. It uses the gd-carousel-wrapper class to add a
wrapper style to the carousel. // 18. It uses the gd-section-title class to add
a title style to the title. // 19. It uses the mc-green, mc-yellow, and mc-red
classes to add a color style to the metacritic scores.

<script setup>
import { ref } from "vue";

const props = defineProps({
  title: {
    type: String,
    required: true,
  },
  games: {
    type: Array,
    required: true,
  },
});

const carouselRef = ref(null);

const scrollCarousel = (direction) => {
  if (!carouselRef.value) return;
  const amount = 320;
  carouselRef.value.scrollBy({
    left: direction * amount,
    behavior: "smooth",
  });
};

const imageLoaded = (event) => {
  event.target.classList.add("loaded");
};
</script>

<template>
  <div v-if="games.length" class="gd-section">
    <h2 class="gd-section-title">{{ title }}</h2>
    <div class="gd-carousel-wrapper">
      <button class="gd-carousel-btn left" @click="scrollCarousel(-1)">
        ❮
      </button>
      <div class="gd-carousel" ref="carouselRef">
        <router-link
          v-for="g in games"
          :key="g.id"
          :to="`/games/${g.id}`"
          class="gd-carousel-card card-hover"
        >
          <img
            v-lazy-img="g.background_image"
            :alt="g.name"
            class="gd-carousel-img"
            @load="imageLoaded"
          />
          <div class="gd-carousel-body">
            <h6>{{ g.name }}</h6>
            <span
              v-if="g.metacritic"
              class="gd-similar-mc"
              :class="
                g.metacritic >= 75
                  ? 'mc-green'
                  : g.metacritic >= 50
                    ? 'mc-yellow'
                    : 'mc-red'
              "
            >
              {{ g.metacritic }}
            </span>
          </div>
        </router-link>
      </div>
      <button class="gd-carousel-btn right" @click="scrollCarousel(1)">
        ❯
      </button>
    </div>
  </div>
</template>

<style scoped>
.gd-section {
  background: linear-gradient(
    180deg,
    var(--overlay-light),
    rgba(255, 255, 255, 0.01)
  );
  border: 1px solid var(--border-subtle);
  border-radius: 24px;
  padding: 30px;
  margin: 45px 0;
  box-shadow: inset 0 1px 0 var(--border-subtle);
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.08);
  animation: fadeUp 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}
.gd-section:first-child {
  margin-top: 40px;
}
.gd-section:last-child {
  margin-bottom: 100px;
}
.gd-section-title {
  font-size: 2rem;
  font-weight: 800;
  letter-spacing: 1px;
  margin-bottom: 25px;
  display: flex;
  align-items: center;
  gap: 12px;
  color: var(--text-primary);
}
.gd-section-title::before {
  content: "";
  width: 6px;
  height: 34px;
  border-radius: 20px;
  background: linear-gradient(180deg, #6f5cff, #4aa3ff);
  box-shadow:
    0 0 12px rgba(111, 92, 255, 0.7),
    0 0 24px rgba(74, 163, 255, 0.5);
}

.gd-carousel-wrapper {
  position: relative;
}
.gd-carousel {
  display: flex;
  gap: 18px;
  overflow-x: auto;
  scroll-behavior: smooth;
  scrollbar-width: none;
  padding: 4px;
}
.gd-carousel::-webkit-scrollbar {
  display: none;
}
.gd-carousel-card {
  flex: 0 0 270px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.08);
  border-radius: 16px;
  overflow: hidden;
  background: var(--overlay-light);
  border: 1px solid var(--border-subtle);
  text-decoration: none;
  transition:
    transform 0.25s,
    box-shadow 0.25s,
    border-color 0.25s;
}
.gd-carousel-card:hover {
  transform: translateY(-8px) scale(1.02);
  border-color: #7c3aed;
  box-shadow: 0 18px 45px rgba(0, 0, 0, 0.18);
}
.gd-carousel-img {
  width: 100%;
  height: 170px;
  object-fit: cover;
  opacity: 0;
  transform: scale(0.96);
  transition:
    opacity 0.35s ease,
    transform 0.35s ease;
}
.gd-carousel-img.loaded {
  opacity: 1;
  transform: scale(1);
}
.gd-carousel-body {
  padding: 14px;
}
.gd-carousel-body h6 {
  color: var(--text-primary);
  font-size: 0.95rem;
  line-height: 1.5;
  min-height: 42px;
  font-weight: 700;
  margin: 0 0 8px;
}
.gd-similar-mc {
  font-size: 0.65rem;
  font-weight: 800;
  padding: 2px 6px;
  border-radius: 4px;
  flex-shrink: 0;
}
.mc-green {
  background: #15803d;
  color: var(--text-primary);
}
.mc-yellow {
  background: #a16207;
  color: var(--text-primary);
}
.mc-red {
  background: #b91c1c;
  color: var(--text-primary);
}

.gd-carousel-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 44px;
  height: 44px;
  border: none;
  border-radius: 50%;
  background: var(--overlay-heavy);
  color: var(--text-primary);
  z-index: 5;
  opacity: 0;
  transition: 0.25s;
  cursor: pointer;
}
.gd-carousel-wrapper:hover .gd-carousel-btn {
  opacity: 1;
}
.gd-carousel-btn.left {
  left: -20px;
}
.gd-carousel-btn.right {
  right: -20px;
}
.gd-carousel-btn:hover {
  background: #7c3aed;
}

.card-hover {
  transition:
    transform 0.35s ease,
    box-shadow 0.35s ease;
}
.card-hover:hover {
  transform: translateY(-10px) scale(1.03);
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.45);
}

@keyframes fadeUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
