import { useEffect, useState } from "react";
import { api } from "../lib/api";
import Layout from "../components/Layout";
import { motion } from "framer-motion";
import { Crown, Flame } from "lucide-react";

export default function Leaderboard() {
  const [list, setList] = useState([]);
  useEffect(() => { api.get("/leaderboard").then(({ data }) => setList(data)); }, []);

  const medalColor = (rank) => rank === 1 ? "#EAB308" : rank === 2 ? "#94A3B8" : rank === 3 ? "#F97316" : "#E2E8F0";

  return (
    <Layout>
      <h1 className="font-display font-extrabold text-3xl text-slate-900 leading-none">Ranking</h1>
      <p className="text-slate-600 font-bold mt-1">Top alunos da semana</p>

      <div className="space-y-2 mt-6">
        {list.map((u, i) => (
          <motion.div
            key={u.id}
            initial={{ x: -10, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: i * 0.03 }}
            className={`tactile-card p-3 flex items-center gap-3 ${u.is_me ? "bg-violet-50 border-violet-500" : ""}`}
            data-testid={`rank-${u.rank}`}
          >
            <div
              className="w-10 h-10 rounded-2xl flex items-center justify-center border-2 border-slate-900 font-display font-extrabold"
              style={{ background: medalColor(u.rank), color: u.rank <= 3 ? "white" : "#0F172A" }}
            >
              {u.rank <= 3 ? <Crown className="w-5 h-5" strokeWidth={3} /> : u.rank}
            </div>
            <div
              className="w-10 h-10 rounded-full flex items-center justify-center font-display font-extrabold text-white shrink-0"
              style={{ background: u.avatar_color }}
            >
              {u.name?.[0]?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-display font-extrabold text-slate-900 truncate">{u.name} {u.is_me && <span className="text-xs text-violet-600">(você)</span>}</div>
              <div className="flex items-center gap-2 text-xs font-bold text-slate-600">
                <Flame className="w-3.5 h-3.5 text-orange-500" strokeWidth={3} /> {u.streak} dias
              </div>
            </div>
            <div className="text-right">
              <div className="font-display font-extrabold text-yellow-600">{u.xp}</div>
              <div className="text-[10px] uppercase tracking-widest font-extrabold text-slate-400">XP</div>
            </div>
          </motion.div>
        ))}
        {list.length === 0 && <p className="text-center text-slate-500 font-bold py-12">Nenhum aluno no ranking ainda</p>}
      </div>
    </Layout>
  );
}
