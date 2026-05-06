import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../lib/api";
import Layout from "../components/Layout";
import { motion } from "framer-motion";
import * as Icons from "lucide-react";
import { useAuth } from "../lib/auth";
import { toast } from "sonner";

export default function Home() {
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const { user, refreshUser } = useAuth();
  const nav = useNavigate();

  useEffect(() => {
    api.get("/subjects").then(({ data }) => setSubjects(data)).finally(() => setLoading(false));
    refreshUser();
  }, [refreshUser]);

  const dailyGoal = 30;
  const todayProgress = Math.min(dailyGoal, user?.xp ? user.xp % (dailyGoal + 1) : 0);

  const refillLives = async () => {
    try {
      await api.post("/lives/refill");
      await refreshUser();
      toast.success("Vidas recarregadas!");
    } catch {
      toast.error("Erro ao recarregar");
    }
  };

  return (
    <Layout>
      <motion.div initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="mb-5">
        <p className="text-sm uppercase tracking-widest font-extrabold text-slate-500">Olá, {user?.name?.split(" ")[0]} 👋</p>
        <h1 className="font-display font-extrabold text-3xl text-slate-900 leading-none mt-1">Escolhe uma matéria pra revisar</h1>
      </motion.div>

      {/* Daily goal card */}
      <motion.div initial={{ y: 12, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ delay: 0.1 }} className="tactile-card p-5 mb-6" data-testid="daily-goal-card">
        <div className="flex items-center justify-between mb-2">
          <div>
            <div className="text-xs uppercase tracking-widest font-extrabold text-slate-500">Meta diária</div>
            <div className="font-display font-extrabold text-xl text-slate-900">{todayProgress}/{dailyGoal} XP</div>
          </div>
          <div className="bg-yellow-100 border-2 border-yellow-500 rounded-2xl px-3 py-2 font-display font-extrabold text-yellow-700">
            {Math.round((todayProgress / dailyGoal) * 100)}%
          </div>
        </div>
        <div className="h-3 bg-slate-100 rounded-full overflow-hidden border border-slate-200">
          <div className="h-full bg-gradient-to-r from-yellow-400 to-orange-500 transition-all" style={{ width: `${Math.min(100, (todayProgress / dailyGoal) * 100)}%` }} />
        </div>
      </motion.div>

      {/* Out of lives banner */}
      {user?.lives === 0 && (
        <motion.div initial={{ scale: 0.95, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="tactile-card p-4 mb-6 bg-red-50 border-red-500" data-testid="no-lives-banner">
          <div className="font-display font-extrabold text-red-700 mb-2">Sem vidas! 💔</div>
          <p className="text-sm text-red-600 font-bold mb-3">Recarregue para continuar revisando.</p>
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
              <div className="w-14 h-14 rounded-2xl flex items-center justify-center border-2 border-slate-900 shrink-0" style={{ background: s.color + "22", color: s.color }}>
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
