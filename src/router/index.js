import { createRouter, createWebHistory } from 'vue-router'
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
    name: 'NewsDetails',
    component: () => import('../views/NewsDetails.vue')
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

// Route guard — redirect to login if not authenticated
router.beforeEach((to, from, next) => {
  const user = localStorage.getItem('currentUser')
  if (to.meta.requiresAuth && !user) {
    next('/login')
  } else {
    next()
  }
})

export default router