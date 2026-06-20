// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import { auth } from '../firebase'
import { onAuthStateChanged } from 'firebase/auth'
import Home from '../views/Home.vue'
import About from '../views/About.vue'
import Games from '../views/Games.vue'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home
  },
  {
    path: '/live-news',
    name: 'LiveNews',
    component: () => import('../views/LiveNews.vue')
  },
  {
    path: '/gamehub-news',
    name: 'GameHubNews',
    component: () => import('../views/GameHubNews.vue')
  },
  {
    path: '/gamehub-news/:id',
    name: 'GameHubNewsDetails',
    component: () => import('../views/GameHubNewsDetails.vue')
  },
  {
    path: '/about',
    name: 'About',
    component: About
  },
  {
    path: '/games',
    name: 'Games',
    component: Games
  },
  {
    path: '/games/:id',
    name: 'GameDetails',
    component: () => import('../views/GameDetails.vue')
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue')
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('../views/Register.vue')
  },
  {
    path: '/favorites',
    name: 'Favorites',
    component: () => import('../views/Favorites.vue'),
    meta: { requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Helper — waits for Firebase to confirm the current auth state
// (onAuthStateChanged fires once immediately with the current user, then again on changes)
function getCurrentUser() {
  return new Promise((resolve) => {
    const unsubscribe = onAuthStateChanged(auth, (user) => {
      unsubscribe()
      resolve(user)
    })
  })
}

// Route guard — redirect to login if not authenticated
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    const user = await getCurrentUser()
    if (!user) {
      next('/login')
      return
    }
  }
  next()
})

export default router