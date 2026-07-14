// src/services/api.js
// Centralized Axios instances for all external API calls.

import axios from 'axios'

// ── FreeToGame API ────────────────────────────────────────────────────────────
export const freeToGameApi = axios.create({
  baseURL: 'https://www.freetogame.com/api',
  timeout: 10000
})

// ── NewsAPI (via Vite proxy: /newsapi → https://newsapi.org) ──────────────────
export const newsApi = axios.create({
  baseURL: '/newsapi/v2',
  timeout: 10000,
  params: {
    apiKey: import.meta.env.VITE_NEWS_API_KEY
  }
})

// ── CheapShark Deals API (via Vite proxy: /cheapshark → https://www.cheapshark.com) ──
export const cheapSharkApi = axios.create({
  baseURL: '/cheapshark/api/1.0',
  timeout: 10000,
  headers: {
    'User-Agent': 'GameHub/1.0 (student-project)'
  }
})

// ── RAWG Video Games Database API ────────────────────────────────────────────
export const rawgApi = axios.create({
  baseURL: 'https://api.rawg.io/api',
  timeout: 10000,
  params: {
    key: import.meta.env.VITE_RAWG_API_KEY
  }
})

// ── Shared Interceptors ─────────────────────────
;[freeToGameApi, newsApi, cheapSharkApi, rawgApi].forEach(instance => {
  // Request Interceptor (Logging)
  instance.interceptors.request.use(config => {
    console.log(`[${config.baseURL}]`, config.url)
    return config
  })

  // Response Interceptor (Error Handling)
  instance.interceptors.response.use(
    response => response,
    error => {
      console.error(
        `[API ERROR] ${error.config?.baseURL}`,
        error.response?.status,
        error.response?.data
      )

      const message =
        error.response?.data?.error ||
        error.response?.data?.message ||
        error.message ||
        'Unknown API error'
        
      return Promise.reject(new Error(message))
    }
  )
})
