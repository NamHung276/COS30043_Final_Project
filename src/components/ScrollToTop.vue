<script>
export default {
  data() {
    return {
      visible: false,
    };
  },

  mounted() {
    // Set initial visibility in case the page mounts already scrolled down
    // (e.g. browser back/forward navigation, or a route that doesn't reset scroll)
    this.handleScroll();
    window.addEventListener("scroll", this.handleScroll);
  },

  beforeUnmount() {
    window.removeEventListener("scroll", this.handleScroll);
  },

  methods: {
    handleScroll() {
      this.visible = window.scrollY > 300;
    },

    scrollToTop() {
      window.scrollTo({ top: 0, behavior: "smooth" });
    },
  },
};
</script>

<template>
  <button
    class="scroll-to-top"
    :class="{ visible }"
    aria-label="Scroll to top"
    @click="scrollToTop"
  >
    ↑
  </button>
</template>
