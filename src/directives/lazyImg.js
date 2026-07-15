/**
 * v-lazy-img
 *
 * Custom directive that lazy-loads images using the IntersectionObserver API.
 * Instead of loading every image immediately, the real image only loads
 * once it scrolls into the viewport — improving initial page load speed.
 * Shows a shimmer placeholder, then fades in smoothly.
 *
 * Usage:
 *   <img v-lazy-img="game.thumbnail" alt="...">
 */

const PLACEHOLDER =
  'data:image/svg+xml;charset=UTF-8,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="100%25" height="100%25" fill="%231e293b"/%3E%3C/svg%3E';

function applyImage(el, src) {
  // Prevent duplicate loading
  if (el.dataset.loaded === src) return;

  // Avoid loading empty URLs
  if (!src) {
    el.src = PLACEHOLDER;
    el.style.opacity = "1";
    el.classList.remove("skeleton");
    return;
  }

  // Start with a placeholder + shimmer style
  el.src = PLACEHOLDER;
  el.style.transition = "opacity 0.5s ease, transform 0.5s ease";
  el.style.opacity = "0";
  el.style.transform = "scale(1.02)";
  el.classList.add("skeleton");

  // Skeleton timeout: stop shimmer after 8 seconds if internet is slow
  const shimmerTimeout = setTimeout(() => {
    el.classList.remove("skeleton");
  }, 8000);

  const tempImg = new Image();
  tempImg.src = src;

  const renderImage = () => {
    clearTimeout(shimmerTimeout);
    el.dataset.loaded = src;

    // Fade in AFTER src changes for a smoother animation
    requestAnimationFrame(() => {
      el.src = src;
      requestAnimationFrame(() => {
        el.style.opacity = "1";
        el.style.transform = "scale(1)";
        el.classList.remove("skeleton");
      });
    });
  };

  const handleError = () => {
    clearTimeout(shimmerTimeout);
    // Keep placeholder visible if the real image fails
    el.style.opacity = "1";
    el.style.transform = "scale(1)";
    el.classList.remove("skeleton");
  };

  // Handle cached images immediately
  if (tempImg.complete) {
    renderImage();
    return;
  }

  // Use decode() before displaying for smoother loading without flickering
  if ("decode" in tempImg) {
    tempImg.decode().then(renderImage).catch(handleError);
  } else {
    tempImg.onload = renderImage;
    tempImg.onerror = handleError;
  }
}

export default {
  mounted(el, binding) {
    // Native lazy loading attributes
    el.loading = "lazy";
    el.decoding = "async";
    el.setAttribute("draggable", "false");

    const src = binding.value;

    // Don't create an observer if browser doesn't support it
    if (!("IntersectionObserver" in window)) {
      applyImage(el, src);
      return;
    }

    // Observe when the element enters the viewport
    const observer = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            applyImage(el, src);
            obs.unobserve(el);
          }
        });
      },
      {
        rootMargin: "250px", // Increase preload distance
      },
    );

    observer.observe(el);

    // Store observer on the element so we can clean it up later
    el._lazyObserver = observer;
  },

  updated(el, binding) {
    // If the bound value changes (e.g. different game selected), reload
    if (binding.value !== binding.oldValue) {
      applyImage(el, binding.value);
    }
  },

  unmounted(el) {
    if (el._lazyObserver) {
      el._lazyObserver.disconnect();
    }
  },
};
