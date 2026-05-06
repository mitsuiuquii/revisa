import Layout from "../components/Layout";
import { useAuth } from "../lib/auth";
import { motion } from "framer-motion";
import { LogOut, Heart, Flame, Zap, BookOpen, Medal } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Profile() {
  const { user, logout } = useAuth();
  const nav = useNavigate();
  if (!user) return null;

  const stats = [
    { label: "XP total", value: user.xp, icon: Zap, color: "#EAB308" },
    { label: "Ofensiva", value: `${user.streak}🔥`, icon: Flame, color: "#F97316" },
    { label: "Vidas", value: user.lives, icon: Heart, color: "#EF4444" },
    { label: "Lições", value: user.completed_lessons.length, icon: BookOpen, color: "#3B82F6" },
    { label: "Conquistas", value: user.achievements.length, icon: Medal, color: "#8B5CF6" },
  ];

  return (
    <Layout>
      <motion.div initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="tactile-card p-6 text-center">
        <div className="w-20 h-20 rounded-full mx-auto flex items-center justify-center border-2 border-slate-900 font-display font-extrabold text-3xl text-white" style={{ background: user.avatar_color }}>
          {user.name?.[0]?.toUpperCase()}
        </div>
        <h1 className="font-display font-extrabold text-2xl text-slate-900 mt-3 leading-none" data-testid="profile-name">{user.name}</h1>
        <p className="text-slate-500 font-bold text-sm mt-1">{user.email}</p>
      </motion.div>

      <div className="grid grid-cols-2 gap-3 mt-6">
        {stats.map((s, i) => (
          <motion.div
            key={s.label}
            initial={{ y: 12, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            transition={{ delay: 0.05 + i * 0.04 }}
            className="tactile-card p-4"
            data-testid={`profile-stat-${s.label}`}
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

      <button
        onClick={() => { logout(); nav("/"); }}
        className="btn-tactile btn-secondary-revisa w-full mt-8 flex items-center justify-center gap-2"
        data-testid="profile-logout"
      >
        <LogOut className="w-5 h-5" strokeWidth={3} /> Sair
      </button>
    </Layout>
  );
}
