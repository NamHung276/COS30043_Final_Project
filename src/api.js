// src/api.js
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
    apiKey: 'a125829a83b64ea99e6889447f348dc8'
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
    key: 'ac1924ebac0a443b83a78f401f8ee01b'
  }
})

  // ── Shared response interceptor (auto-handle errors) ─────────────────────────
  ;[freeToGameApi, newsApi, cheapSharkApi, rawgApi].forEach(instance => {
    instance.interceptors.response.use(
      response => response,
      error => {
        const message =
          error.response?.data?.message ||
          error.message ||
          'An unknown error occurred.'
        return Promise.reject(new Error(message))
      }
    )
  })
