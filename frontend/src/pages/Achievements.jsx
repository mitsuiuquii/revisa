import { useEffect, useState } from "react";
import { api } from "../lib/api";
import Layout from "../components/Layout";
import { motion } from "framer-motion";
import * as Icons from "lucide-react";
import { Lock } from "lucide-react";

export default function Achievements() {
  const [list, setList] = useState([]);
  useEffect(() => { api.get("/achievements").then(({ data }) => setList(data)); }, []);

  const unlocked = list.filter(a => a.unlocked).length;

  return (
    <Layout>
      <h1 className="font-display font-extrabold text-3xl text-slate-900 leading-none">Conquistas</h1>
      <p className="text-slate-600 font-bold mt-1">{unlocked} de {list.length} desbloqueadas</p>

      <div className="grid grid-cols-2 gap-3 mt-6">
        {list.map((a, i) => {
          const Icon = Icons[a.icon] || Icons.Award;
          return (
            <motion.div
              key={a.id}
              initial={{ y: 12, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: i * 0.04 }}
              className={`tactile-card p-4 text-center ${a.unlocked ? "" : "opacity-60"}`}
              data-testid={`achievement-${a.name}`}
            >
              <div
                className="w-14 h-14 rounded-3xl mx-auto flex items-center justify-center border-2 border-slate-900 mb-2"
                style={{ background: a.unlocked ? a.color : "#E2E8F0", color: a.unlocked ? "white" : "#94A3B8" }}
              >
                {a.unlocked ? <Icon className="w-7 h-7" strokeWidth={3} /> : <Lock className="w-6 h-6" strokeWidth={3} />}
              </div>
              <div className="font-display font-extrabold text-sm text-slate-900 leading-tight">{a.name}</div>
              <div className="text-xs text-slate-500 font-bold mt-1">{a.description}</div>
            </motion.div>
          );
        })}
      </div>
    </Layout>
  );
}
