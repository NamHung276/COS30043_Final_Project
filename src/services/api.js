// Centralized Axios instances for all external API calls.

import axios from "axios";

// ── FreeToGame API ────────────────────────────────────────────────────────────
export const freeToGameApi = axios.create({
  baseURL: "https://www.freetogame.com/api",
  timeout: 10000,
});

// ── NewsAPI (via Vite proxy: /newsapi → https://newsapi.org) ──────────────────
export const newsApi = axios.create({
  baseURL: "/newsapi/v2",
  timeout: 10000,
  params: {
    apiKey: import.meta.env.VITE_NEWS_API_KEY,
  },
});

// ── NewsData.io API ────────────────────────────────────────────────────────
export const newsDataApi = axios.create({
  baseURL: "https://newsdata.io/api/1",
  timeout: 10000,
  params: {
    apikey: import.meta.env.VITE_NEWSDATA_API_KEY,
  },
});

// ── CheapShark Deals API (via Vite proxy: /cheapshark → https://www.cheapshark.com) ──
export const cheapSharkApi = axios.create({
  baseURL: "/cheapshark/api/1.0",
  timeout: 10000,
});

// ── RAWG Video Games Database API ────────────────────────────────────────────
export const rawgApi = axios.create({
  baseURL: "https://api.rawg.io/api",
  timeout: 10000,
  params: {
    key: import.meta.env.VITE_RAWG_API_KEY,
  },
});

const cache = new Map();
const CACHE_TTL = 3 * 60 * 1000; // 3 minutes

// ── Shared Interceptors & Caching ─────────────────────────
[freeToGameApi, newsApi, newsDataApi, cheapSharkApi, rawgApi].forEach((instance) => {
  // Simple GET Cache to prevent duplicate API calls
  const originalGet = instance.get;
  instance.get = async function (url, config) {
    const key = `${instance.defaults.baseURL}${url}?${new URLSearchParams(
      config?.params || {}
    ).toString()}`;
    
    const cached = cache.get(key);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      return Promise.resolve(cached.data);
    }
    
    const response = await originalGet.call(this, url, config);
    cache.set(key, { timestamp: Date.now(), data: response });
    return response;
  };

  // Request Interceptor (Logging)
  instance.interceptors.request.use((config) => {
    // console.log(`[${config.baseURL}]`, config.url); // Removed for cleanliness
    return config;
  });

  // Response Interceptor (Error Handling)
  instance.interceptors.response.use(
    (response) => response,
    (error) => {
      console.error(
        `[API ERROR] ${error.config?.baseURL}`,
        error.response?.status,
        error.response?.data,
      );

      const message =
        error.response?.data?.error ||
        error.response?.data?.message ||
        error.message ||
        "Unknown API error";

      return Promise.reject(new Error(message));
    },
  );
});
