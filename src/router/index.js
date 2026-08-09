import { createRouter, createWebHistory } from "vue-router";
import { auth } from "../firebase";
import { signOut } from "firebase/auth";
import { useAuthStore } from "../stores/useAuthStore";
import Home from "../views/Home.vue";
import About from "../views/About.vue";
import Games from "../views/Games.vue";

const routes = [
  {
    path: "/",
    name: "Home",
    component: Home,
  },
  {
    path: "/live-news",
    name: "LiveNews",
    component: () => import("../views/LiveNews.vue"),
  },
  {
    path: "/news",
    name: "News",
    component: () => import("../views/News.vue"),
  },
  // IMPORTANT: '/create' and '/user/:id' must come BEFORE '/:id'
  // otherwise '/:id' would match "create" as if it were an article id
  {
    path: "/news/create",
    name: "CreateNews",
    component: () => import("../views/CreateNews.vue"),
    meta: { requiresAuth: true },
  },

  {
    path: "/news/edit/:id",
    name: "EditNews",
    component: () => import("../views/EditNews.vue"),
    meta: { requiresAuth: true },
  },

  {
    path: "/news/:id",
    name: "NewsDetails",
    component: () => import("../views/NewsDetails.vue"),
  },
  {
    path: "/about",
    name: "About",
    component: About,
  },
  {
    path: "/converter",
    name: "CurrencyConverter",
    component: () => import("../views/ConverterView.vue"),
  },
  {
    path: "/games",
    name: "Games",
    component: Games,
  },
  {
    path: "/paid-games",
    name: "PaidGames",
    component: () => import("../views/PaidGames.vue"),
  },
  {
    path: "/games/:id",
    name: "GameDetails",
    component: () => import("../views/GameDetails.vue"),
  },
  {
    path: "/deals",
    name: "Deals",
    component: () => import("../views/Deals.vue"),
  },
  {
    path: "/free-to-play",
    name: "FreeToPlay",
    component: () => import("../views/FreeToPlay.vue"),
  },
  {
    path: "/free-to-play/:id",
    name: "FreeToPlayDetails",
    component: () => import("../views/FreeToPlayDetails.vue"),
  },
  {
    path: "/checkout",
    name: "Checkout",
    component: () => import("../views/Checkout.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/purchase-history",
    name: "PurchaseHistory",
    component: () => import("../views/PurchaseHistory.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/login",
    name: "Login",
    component: () => import("../views/Login.vue"),
  },
  {
    path: "/register",
    name: "Register",
    component: () => import("../views/Register.vue"),
  },
  {
    path: "/favorites",
    name: "Favorites",
    component: () => import("../views/Favorites.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/reviews",
    name: "Reviews",
    component: () => import("../views/MyReviews.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/profile",
    name: "Profile",
    component: () => import("../views/Profile.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/settings",
    name: "Settings",
    component: () => import("../views/Settings.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/library",
    name: "Library",
    component: () => import("../views/Library.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/library/:id",
    name: "LibraryDetails",
    component: () => import("../views/LibraryDetails.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/admin",
    name: "AdminDashboard",
    component: () => import("../views/AdminDashboard.vue"),
    meta: { requiresAuth: true, requiresAdmin: true },
  },
  {
    path: "/checkout/success",
    name: "CheckoutSuccess",
    component: () => import("../views/CheckoutSuccess.vue"),
    meta: { requiresAuth: true },
  },
  {
    path: "/:pathMatch(.*)*",
    name: "NotFound",
    component: () => import("../views/NotFound.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Route guard — redirect if not authenticated or not admin
router.beforeEach(async (to, from) => {
  if (to.meta.requiresAuth) {
    const authStore = useAuthStore();
    await authStore.waitForReady();

    if (!authStore.isAuthenticated) {
      return "/login";
    }

    // Check if user is banned
    if (authStore.isBanned) {
      await signOut(auth);
      return "/login?banned=true";
    }

    // Extra check: admin-only routes
    if (to.meta.requiresAdmin) {
      if (authStore.userRole !== "admin") {
        return "/"; // redirect non-admins to home
      }
    }
  }
  return true;
});

// Update document title on navigation
router.afterEach((to) => {
  if (to.name && !to.name.includes("Details")) {
    const formattedName = to.name.replace(/([A-Z])/g, " $1").trim();
    document.title = `GameHub — ${formattedName}`;
  } else if (!to.name) {
    document.title = "GameHub";
  }
  // If it's a Details page, we'll let the component update the title dynamically with the actual content title
});

export default router;
