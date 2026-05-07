// REMINDER: DO NOT HARDCODE THE URL, OR ADD ANY FALLBACKS OR REDIRECT URLS, THIS BREAKS THE AUTH
import { useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import { useAuth } from "../lib/auth";
import { toast } from "sonner";

export default function AuthCallback() {
  const nav = useNavigate();
  const { setUser } = useAuth();
  const hasProcessed = useRef(false);
  const [msg, setMsg] = useState("Finalizando seu login…");

  useEffect(() => {
    if (hasProcessed.current) return;
    hasProcessed.current = true;

    const hash = window.location.hash || "";
    const match = hash.match(/session_id=([^&]+)/);
    if (!match) {
      toast.error("Sessão não encontrada");
      nav("/login", { replace: true });
      return;
    }
    const sessionId = decodeURIComponent(match[1]);

    (async () => {
      try {
        const { data } = await api.post("/auth/google/session", { session_id: sessionId });
        localStorage.setItem("revisa_token", data.token);
        localStorage.setItem("revisa_user", JSON.stringify(data.user));
        setUser(data.user);
        // Clear the hash and go home
        window.history.replaceState(null, "", window.location.pathname);
        toast.success("Bem-vindo ao REVISA! 🎉");
        nav("/home", { replace: true });
      } catch (err) {
        setMsg("Falhou. Redirecionando…");
        toast.error(err.response?.data?.detail || "Erro no login com Google");
        nav("/login", { replace: true });
      }
    })();
  }, [nav, setUser]);

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6">
      <div className="w-16 h-16 rounded-3xl border-4 border-slate-900 bg-violet-500 flex items-center justify-center mb-4 animate-pulse">
        <svg className="w-8 h-8 text-white animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
        </svg>
      </div>
      <p className="font-display font-extrabold text-xl text-slate-900">{msg}</p>
    </div>
  );
}
