// src/directives/lazyImg.js
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
 *
 * Instead of:
 *   <img :src="game.thumbnail" alt="...">
 */

const PLACEHOLDER =
  'data:image/svg+xml;charset=UTF-8,%3Csvg xmlns="http://www.w3.org/2000/svg" width="400" height="300"%3E%3Crect width="100%25" height="100%25" fill="%231e293b"/%3E%3C/svg%3E'

export default {
  mounted(el, binding) {
    // Start with a placeholder + shimmer style
    el.src = PLACEHOLDER
    el.style.transition = 'opacity 0.5s ease, transform 0.5s ease'
    el.style.opacity = '0'
    el.style.transform = 'scale(1.02)'

    // Add shimmer class for loading animation
    el.classList.add('skeleton')

    const realSrc = binding.value

    const loadImage = () => {
      const tempImg = new Image()
      tempImg.src = realSrc

      tempImg.onload = () => {
        el.src = realSrc
        el.style.opacity = '1'
        el.style.transform = 'scale(1)'
        el.classList.remove('skeleton')
      }

      tempImg.onerror = () => {
        // Keep placeholder visible if the real image fails
        el.style.opacity = '1'
        el.style.transform = 'scale(1)'
        el.classList.remove('skeleton')
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
      rootMargin: '100px' // start loading slightly before it's visible
    })

    observer.observe(el)

    // Store observer on the element so we can clean it up later
    el._lazyObserver = observer
  },

  updated(el, binding) {
    // If the bound value changes (e.g. different game selected), reload
    if (binding.value !== binding.oldValue) {
      el.style.opacity = '0'
      el.style.transform = 'scale(1.02)'
      el.classList.add('skeleton')

      const tempImg = new Image()
      tempImg.src = binding.value
      tempImg.onload = () => {
        el.src = binding.value
        el.style.opacity = '1'
        el.style.transform = 'scale(1)'
        el.classList.remove('skeleton')
      }
      tempImg.onerror = () => {
        el.style.opacity = '1'
        el.style.transform = 'scale(1)'
        el.classList.remove('skeleton')
      }
    }
  },

  unmounted(el) {
    if (el._lazyObserver) {
      el._lazyObserver.disconnect()
    }
  }
}