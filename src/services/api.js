// Centralized Axios instances for all external API calls.

import axios from "axios";

// ── Internal Backend API ──────────────────────────────────────────────────────
// Dev: uses Vite proxy (/api → http://localhost:8000/api)
// Prod: calls Render backend directly
const BACKEND_BASE_URL = import.meta.env.PROD
  ? `${import.meta.env.VITE_API_BASE_URL || "https://gamehub-api-er30.onrender.com"}/api`
  : "/api";

export const backendApi = axios.create({
  baseURL: BACKEND_BASE_URL,
  timeout: 60000,
});

const cache = new Map();
const CACHE_TTL = 3 * 60 * 1000; // 3 minutes

// ── Shared Interceptors & Caching ─────────────────────────
[backendApi].forEach((instance) => {
  // Simple GET Cache to prevent duplicate API calls
  const originalGet = instance.get;
  instance.get = async function (url, config) {
    const key = `${instance.defaults.baseURL}${url}?${new URLSearchParams(
      config?.params || {}
    ).toString()}`;
    
    const cached = cache.get(key);
    if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
      return Promise.resolve({ data: cached.data, status: 200, statusText: "OK", headers: {}, config });
    }
    
    const response = await originalGet.call(this, url, config);
    cache.set(key, { timestamp: Date.now(), data: response.data });
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
