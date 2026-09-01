import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
export const API = `${BACKEND_URL}/api`;

export const api = axios.create({ 
  baseURL: API,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json"
  }
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("revisa_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
    // Debug: log do token being enviado
    if (config.url.includes("admin")) {
      console.log(`📤 Enviando request para ${config.url} com token (primeiros 30 chars): ${token.substring(0, 30)}...`);
    }
  }
  return config;
});

api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem("revisa_token");
      localStorage.removeItem("revisa_user");
      // Não redireciona para /login se estiver em /admin (painel admin)
      const isAdminPanel = window.location.pathname.startsWith("/admin");
      if (!isAdminPanel && !window.location.pathname.startsWith("/login") && !window.location.pathname.startsWith("/register") && window.location.pathname !== "/") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(err);
  }
);
