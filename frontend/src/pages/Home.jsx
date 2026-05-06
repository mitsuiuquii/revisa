import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import Layout from "../components/Layout";
import Tutorial from "../components/Tutorial";
import { motion } from "framer-motion";
import * as Icons from "lucide-react";
import { useAuth } from "../lib/auth";
import { toast } from "sonner";
import { HelpCircle } from "lucide-react";

export default function Home() {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showTutorial, setShowTutorial] = useState(false);
  const { user, refreshUser } = useAuth();
  const nav = useNavigate();

  useEffect(() => {
    api.get("/subjects").then(({ data }) => setSubjects(data)).finally(() => setLoading(false));
    refreshUser();
  }, [refreshUser]);

  const refillLives = async () => {
    try {
      await api.post("/lives/refill");
      await refreshUser();
      toast.success("Vidas recarregadas!");
    } catch { toast.error("Erro"); }
  };

  // Find next rank threshold
  const nextRank = (() => {
    if (!user?.rank) return null;
    const tiers = [
      { name: "Bronze", min: 0 },{ name: "Prata", min: 200 },{ name: "Ouro", min: 600 },
      { name: "Platina", min: 1500 },{ name: "Diamante", min: 3500 },{ name: "Sábio", min: 7000 }
    ];
    return tiers.find(t => t.min > user.xp);
  })();
  const xpToNext = nextRank ? nextRank.min - (user?.xp || 0) : 0;

  return (
    <Layout>
      <Tutorial forceFirstTime open={showTutorial} onClose={() => setShowTutorial(false)} />

      <motion.div initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="mb-5 flex items-start justify-between gap-2">
        <div>
          <p className="text-sm uppercase tracking-widest font-extrabold text-slate-500">Olá, {user?.name?.split(" ")[0]} 👋</p>
          <h1 className="font-display font-extrabold text-3xl text-slate-900 leading-none mt-1">Trilhas</h1>
        </div>
        <button onClick={() => setShowTutorial(true)} className="flex items-center gap-1 text-xs font-extrabold text-violet-600 bg-violet-50 px-3 py-1.5 rounded-full border-2 border-violet-200" data-testid="home-help">
          <HelpCircle className="w-4 h-4" strokeWidth={3} /> Como funciona?
        </button>
      </motion.div>

      {/* Rank progress card */}
      {user && (
        <motion.div initial={{ y: 12, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.1 }}
          className="tactile-card p-4 mb-5"
          style={{ background: (user.rank?.color || "#8B5CF6") + "11" }}
          data-testid="rank-progress-card"
        >
          <div className="flex items-center justify-between">
            <div>
              <div className="text-[10px] uppercase tracking-widest font-extrabold text-slate-500">Patente atual</div>
              <div className="font-display font-extrabold text-2xl leading-none" style={{ color: user.rank?.color }}>{user.rank?.name}</div>
            </div>
            {nextRank ? (
              <div className="text-right">
                <div className="text-[10px] uppercase tracking-widest font-extrabold text-slate-500">Faltam pra {nextRank.name}</div>
                <div className="font-display font-extrabold text-xl text-slate-900">{xpToNext} XP</div>
              </div>
            ) : (
              <div className="text-right">
                <div className="text-[10px] uppercase tracking-widest font-extrabold text-violet-600">Patente máxima</div>
                <div className="font-display font-extrabold text-xl text-violet-600">Sábio 🧠</div>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {user?.lives === 0 && (
        <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="tactile-card p-4 mb-5 bg-red-50 border-red-500" data-testid="no-lives-banner">
          <div className="font-display font-extrabold text-red-700 mb-2">Sem vidas! 💔</div>
          <button onClick={refillLives} className="btn-tactile btn-primary-revisa w-full" data-testid="refill-lives-btn">Recarregar vidas</button>
        </motion.div>
      )}

      <div className="space-y-3">
        {loading && <div className="text-center text-slate-500 font-bold py-12">Carregando matérias…</div>}
        {!loading && subjects.map((s, i) => {
          const Icon = Icons[s.icon] || Icons.BookOpen;
          return (
            <motion.button
              key={s.id}
              data-testid={`subject-${s.name}`}
              onClick={() => nav(`/trail/${s.id}`)}
              initial={{ x: -20, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              transition={{ delay: i * 0.04 }}
              className="tactile-card w-full p-4 flex items-center gap-4 text-left hover:translate-y-0.5 hover:shadow-[3px_3px_0_0_#0F172A] transition-all"
            >
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center border-2 border-slate-900 shrink-0" style={{ background: s.color, color: "white" }}>
                <Icon className="w-7 h-7" strokeWidth={2.8} />
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-display font-extrabold text-lg text-slate-900 leading-tight">{s.name}</div>
                <div className="text-xs text-slate-500 font-bold truncate">{s.description}</div>
                <div className="mt-2 h-2 bg-slate-100 rounded-full overflow-hidden">
                  <div className="h-full transition-all" style={{ width: `${s.progress}%`, background: s.color }} />
                </div>
              </div>
              <div className="text-right shrink-0">
                <div className="font-display font-extrabold text-lg" style={{ color: s.color }}>{s.completed_lessons}/{s.total_lessons}</div>
                <div className="text-[10px] uppercase tracking-widest font-extrabold text-slate-400">lições</div>
              </div>
            </motion.button>
          );
        })}
      </div>
    </Layout>
  );
}
