// src/directives/lazyImg.js
/**
 * v-lazy-img
 *
 * Custom directive that lazy-loads images using the IntersectionObserver API.
 * Instead of loading every image immediately, the real image only loads
 * once it scrolls into the viewport — improving initial page load speed.
 * Once loaded, the image fades in smoothly.
 *
 * Usage:
 *   <img v-lazy-img="game.thumbnail" alt="...">
 *
 * Instead of:
 *   <img :src="game.thumbnail" alt="...">
 */

const PLACEHOLDER =
  'data:image/svg+xml;charset=UTF-8,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="100%25" height="100%25" fill="%23333"/%3E%3C/svg%3E'

export default {
  mounted(el, binding) {
    // Start with a placeholder + transition styles
    el.src = PLACEHOLDER
    el.style.transition = 'opacity 0.4s ease-in-out'
    el.style.opacity = '0'

    const realSrc = binding.value

    const loadImage = () => {
      const tempImg = new Image()
      tempImg.src = realSrc

      tempImg.onload = () => {
        el.src = realSrc
        el.style.opacity = '1'
      }

      tempImg.onerror = () => {
        // Keep placeholder visible if the real image fails
        el.style.opacity = '1'
      }
    }

    // Observe when the element enters the viewport
    const observer = new IntersectionObserver((entries, obs) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          loadImage()
          obs.unobserve(el)
        }
      })
    }, {
      rootMargin: '50px' // start loading slightly before it's visible
    })

    observer.observe(el)

    // Store observer on the element so we can clean it up later
    el._lazyObserver = observer
  },

  updated(el, binding) {
    // If the bound value changes (e.g. different game selected), reload
    if (binding.value !== binding.oldValue) {
      el.style.opacity = '0'
      const tempImg = new Image()
      tempImg.src = binding.value
      tempImg.onload = () => {
        el.src = binding.value
        el.style.opacity = '1'
      }
    }
  },

  unmounted(el) {
    if (el._lazyObserver) {
      el._lazyObserver.disconnect()
    }
  }
}