import { createContext, useContext, useEffect, useState, useCallback } from "react";
import { api } from "./api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try { return JSON.parse(localStorage.getItem("revisa_user") || "null"); }
    catch { return null; }
  });
  // Only show loading if there's a token to validate
  const [loading, setLoading] = useState(!!localStorage.getItem("revisa_token"));

  const refreshUser = useCallback(async () => {
    try {
      const { data } = await api.get("/auth/me");
      setUser(data);
      localStorage.setItem("revisa_user", JSON.stringify(data));
      return data;
    } catch {
      // Token inválido — limpa tudo
      localStorage.removeItem("revisa_token");
      localStorage.removeItem("revisa_user");
      setUser(null);
      return null;
    }
  }, []);

  useEffect(() => {
  const token = localStorage.getItem("revisa_token");

  if (token) {
    refreshUser().finally(() => setLoading(false));
  } else {
    setLoading(false);
  }
}, [refreshUser]);

  const login = async (email, password) => {
    const { data } = await api.post("/auth/login", { email, password });
    localStorage.setItem("revisa_token", data.token);
    localStorage.setItem("revisa_user", JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  };

  const register = async (name, email, password) => {
    const { data } = await api.post("/auth/register", { name, email, password });
    localStorage.setItem("revisa_token", data.token);
    localStorage.setItem("revisa_user", JSON.stringify(data.user));
    setUser(data.user);
    return data.user;
  };

 const logout = () => {
  localStorage.removeItem("revisa_token");
  localStorage.removeItem("revisa_user");
  sessionStorage.removeItem("revisa_admin");
  setUser(null);
};
  return (
    <AuthContext.Provider value={{ user, setUser, loading, login, register, logout, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
