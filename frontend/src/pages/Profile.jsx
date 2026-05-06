import { useEffect, useState } from "react";
import Layout from "../components/Layout";
import { useAuth } from "../lib/auth";
import { motion } from "framer-motion";
import { LogOut, Heart, Flame, Zap, BookOpen, Medal, Coins, Trophy } from "lucide-react";
import * as Icons from "lucide-react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";

export default function Profile() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  const [meta, setMeta] = useState(null);

  useEffect(() => { api.get("/meta/ranks").then(({ data }) => setMeta(data)); }, []);

  if (!user) return null;

  const stats = [
    { label: "XP total", value: user.xp, icon: Zap, color: "#EAB308" },
    { label: "Moedas", value: user.coins, icon: Coins, color: "#D97706" },
    { label: "Ofensiva", value: `${user.streak}🔥`, icon: Flame, color: "#F97316" },
    { label: "Vidas", value: user.lives, icon: Heart, color: "#EF4444" },
    { label: "Lições", value: user.completed_lessons.length, icon: BookOpen, color: "#3B82F6" },
    { label: "Medalhas", value: user.achievements.length, icon: Medal, color: "#8B5CF6" },
  ];

  return (
    <Layout>
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="tactile-card p-6 text-center" data-testid="profile-card">
        <div className="w-20 h-20 rounded-full mx-auto flex items-center justify-center border-2 border-slate-900 font-display font-extrabold text-3xl text-white" style={{ background: user.avatar_color }}>
          {user.name?.[0]?.toUpperCase()}
        </div>
        <h1 className="font-display font-extrabold text-2xl text-slate-900 mt-3 leading-none" data-testid="profile-name">{user.name}</h1>
        <p className="text-slate-500 font-bold text-sm mt-1">{user.email}</p>
        <div className="inline-flex items-center gap-2 mt-3 px-3 py-1 rounded-full border-2 border-slate-900 font-display font-extrabold"
             style={{ background: user.rank?.color + "22", color: user.rank?.color }}>
          <Trophy className="w-4 h-4" strokeWidth={3} />
          {user.rank?.name}
        </div>
      </motion.div>

      <div className="grid grid-cols-2 gap-3 mt-6">
        {stats.map((s, i) => (
          <motion.div key={s.label}
            initial={{ y: 12, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.05 + i * 0.04 }}
            className="tactile-card p-4" data-testid={`profile-stat-${s.label}`}
          >
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: s.color + "22", color: s.color }}>
                <s.icon className="w-4 h-4" strokeWidth={3} />
              </div>
              <div className="text-xs uppercase tracking-widest font-extrabold text-slate-500">{s.label}</div>
            </div>
            <div className="font-display font-extrabold text-2xl text-slate-900">{s.value}</div>
          </motion.div>
        ))}
      </div>

      {/* Patentes ladder */}
      {meta && (
        <div className="mt-8">
          <h2 className="font-display font-extrabold text-xl text-slate-900 mb-3">Patentes</h2>
          <div className="space-y-2">
            {meta.ranks.map((r) => {
              const Icon = Icons[r.icon] || Trophy;
              const reached = user.xp >= r.min_xp;
              const isCurrent = user.rank?.id === r.id;
              return (
                <div key={r.id}
                  className={`tactile-card p-3 flex items-center gap-3 transition-all ${isCurrent ? "ring-2 ring-offset-2" : reached ? "" : "opacity-60"}`}
                  style={isCurrent ? { background: r.color + "22", borderColor: r.color, "--tw-ring-color": r.color } : {}}
                  data-testid={`rank-${r.id}`}
                >
                  <div className="w-12 h-12 rounded-2xl flex items-center justify-center border-2 border-slate-900"
                       style={{ background: reached ? r.color : "#E2E8F0", color: reached ? "white" : "#94A3B8" }}>
                    <Icon className="w-6 h-6" strokeWidth={3} />
                  </div>
                  <div className="flex-1">
                    <div className="font-display font-extrabold text-slate-900">{r.name} {isCurrent && <span className="text-xs text-violet-600">(atual)</span>}</div>
                    <div className="text-xs font-bold text-slate-500">A partir de {r.min_xp} XP</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <button onClick={() => { logout(); nav("/"); }}
        className="btn-tactile btn-secondary-revisa w-full mt-8 flex items-center justify-center gap-2" data-testid="profile-logout">
        <LogOut className="w-5 h-5" strokeWidth={3} /> Sair
      </button>
    </Layout>
  );
}
