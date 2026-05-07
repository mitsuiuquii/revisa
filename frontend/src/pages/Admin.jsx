import { Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { useEffect, useState, useCallback } from "react";
import { api } from "../lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import {
  Users, Trophy, BookOpen, BarChart3, Search, LogOut,
  Trash2, RefreshCw, ShieldAlert, ChevronDown, ChevronUp,
  Zap, Heart, Flame, Coins, Medal, ArrowLeft, Eye, EyeOff,
} from "lucide-react";
import * as Icons from "lucide-react";

/* ─── Admin credentials ─── */
const ADMIN_EMAIL = "admin@revisa.com.br";
const ADMIN_PASSWORD = "revisa@admin2025";

/* ─── Tabs ─── */
const TABS = [
  { id: "users", label: "Usuários", icon: Users },
  { id: "stats", label: "Estatísticas", icon: BarChart3 },
  { id: "subjects", label: "Matérias", icon: BookOpen },
  { id: "ranking", label: "Ranking", icon: Trophy },
];

/* ─── Login Admin ─── */
function AdminLogin({ onLogin }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const submit = (e) => {
    e.preventDefault();

    if (email === ADMIN_EMAIL && password === ADMIN_PASSWORD) {
      sessionStorage.setItem("revisa_admin", "1");
      onLogin();
    } else {
      alert("Credenciais inválidas");
    }
  };

  return (
    <div>
      <h1>Admin Login</h1>

      <form onSubmit={submit}>
        <input
          type="email"
          placeholder="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />

        <input
          type="password"
          placeholder="senha"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit">Entrar</button>
      </form>
    </div>
  );
}

/* ─── MAIN COMPONENT ─── */
export default function Admin() {
  const { user, logout } = useAuth();
  const nav = useNavigate();

  const [authed, setAuthed] = useState(
    !!sessionStorage.getItem("revisa_admin")
  );

  const [tab, setTab] = useState("users");
  const [users, setUsers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(false);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      const [usersRes, subsRes] = await Promise.allSettled([
        api.get("/admin/users"),
        api.get("/subjects"),
      ]);

      if (usersRes.status === "fulfilled") {
        setUsers(usersRes.value.data);
      }

      if (subsRes.status === "fulfilled") {
        setSubjects(subsRes.value.data);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (authed) fetchAll();
  }, [authed, fetchAll]);

  const handleAdminLogout = () => {
    sessionStorage.removeItem("revisa_admin");
    setAuthed(false);
  };

  if (!authed) return <AdminLogin onLogin={() => setAuthed(true)} />;
  
  return (
    <div>
      {/* HEADER SIMPLES */}
      <header>
        <h2>Admin Panel</h2>

        <button onClick={handleAdminLogout}>
          Logout
        </button>
      </header>

      {/* TABS */}
      <div>
        {TABS.map((t) => (
          <button key={t.id} onClick={() => setTab(t.id)}>
            {t.label}
          </button>
        ))}
      </div>

      {/* CONTENT */}
      <main>
        {tab === "users" && (
          <div>
            <h3>Usuários</h3>
            {loading ? "Carregando..." : users.length}
          </div>
        )}

        {tab === "stats" && (
          <div>
            <h3>Stats</h3>
            <p>Total usuários: {users.length}</p>
          </div>
        )}

        {tab === "subjects" && (
          <div>
            <h3>Matérias</h3>
            {subjects.length}
          </div>
        )}

        {tab === "ranking" && (
          <div>
            <h3>Ranking</h3>
          </div>
        )}
      </main>
    </div>
  );
}