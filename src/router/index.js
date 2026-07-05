import { createRouter, createWebHistory } from 'vue-router'
import { auth, db } from '../firebase'
import { onAuthStateChanged } from 'firebase/auth'
import { doc, getDoc } from 'firebase/firestore'
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
  // IMPORTANT: '/create' and '/user/:id' must come BEFORE '/:id'
  // otherwise '/:id' would match "create" as if it were an article id
  {
    path: '/gamehub-news/create',
    name: 'CreateNews',
    component: () => import('../views/CreateNews.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/gamehub-news/user/:id',
    name: 'UserNewsDetails',
    component: () => import('../views/UserNewsDetails.vue')
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
    path: '/deals',
    name: 'Deals',
    component: () => import('../views/Deals.vue')
  },
  {
    path: '/free-to-play',
    name: 'FreeToPlay',
    component: () => import('../views/FreeToPlay.vue')
  },
  {
    path: '/free-to-play/:id',
    name: 'FreeToPlayDetails',
    component: () => import('../views/FreeToPlayDetails.vue')
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
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('../views/Profile.vue'),
    meta: { requiresAuth: true }
  },
  {
    path: '/admin',
    name: 'AdminDashboard',
    component: () => import('../views/AdminDashboard.vue'),
    meta: { requiresAuth: true, requiresAdmin: true }
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

// Route guard — redirect if not authenticated or not admin
router.beforeEach(async (to, from, next) => {
  if (to.meta.requiresAuth) {
    const user = await getCurrentUser()
    if (!user) {
      next('/login')
      return
    }

    // Extra check: admin-only routes
    if (to.meta.requiresAdmin) {
      try {
        const snap = await getDoc(doc(db, 'users', user.uid))
        const role = snap.exists() ? snap.data().role : 'user'
        if (role !== 'admin') {
          next('/')   // redirect non-admins to home
          return
        }
      } catch {
        next('/')
        return
      }
    }
  }
  next()
})

export default router