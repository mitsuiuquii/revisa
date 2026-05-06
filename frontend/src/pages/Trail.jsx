import { useEffect, useState } from "react";
import { useNavigate, useParams, Link } from "react-router-dom";
import { api } from "../lib/api";
import Layout from "../components/Layout";
import { motion } from "framer-motion";
import * as Icons from "lucide-react";
import { Check, Lock, Star, ArrowLeft } from "lucide-react";

export default function Trail() {
  const { subjectId } = useParams();
  const [data, setData] = useState(null);
  const nav = useNavigate();

  useEffect(() => {
    api.get(`/subjects/${subjectId}/lessons`).then(({ data }) => setData(data));
  }, [subjectId]);

  if (!data) return <Layout><div className="text-center py-12 text-slate-500 font-bold">Carregando…</div></Layout>;
  const { subject, lessons } = data;
  const Icon = Icons[subject.icon] || Icons.BookOpen;

  return (
    <Layout>
      <Link to="/home" className="inline-flex items-center gap-1 text-slate-700 font-extrabold mb-4 hover:text-violet-600" data-testid="trail-back">
        <ArrowLeft className="w-4 h-4" strokeWidth={3} /> Voltar
      </Link>

      <div className="tactile-card p-5 mb-8 flex items-center gap-4" style={{ background: subject.color + "11" }}>
        <div className="w-16 h-16 rounded-3xl flex items-center justify-center border-2 border-slate-900" style={{ background: subject.color, color: "white" }}>
          <Icon className="w-8 h-8" strokeWidth={3} />
        </div>
        <div>
          <div className="text-[11px] uppercase tracking-widest font-extrabold text-slate-500">Matéria</div>
          <div className="font-display font-extrabold text-2xl text-slate-900 leading-none">{subject.name}</div>
          <div className="text-sm text-slate-600 font-bold mt-1">{subject.description}</div>
        </div>
      </div>

      <div className="flex flex-col items-center">
        {lessons.length === 0 && (
          <div className="text-center text-slate-500 font-bold py-12">Em breve mais lições nesta matéria 🚀</div>
        )}
        {lessons.map((l, i) => {
          const isCompleted = l.completed;
          const isCurrent = !isCompleted && l.unlocked;
          const isLocked = !l.unlocked;
          // zig-zag offset
          const offset = i % 4;
          const offsets = ["translate-x-0", "translate-x-12", "translate-x-0", "-translate-x-12"];

          return (
            <div key={l.id} className="flex flex-col items-center w-full">
              {i > 0 && <div className="trail-connector" />}
              <motion.button
                initial={{ scale: 0.6, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ delay: i * 0.06, type: "spring", stiffness: 320, damping: 14 }}
                onClick={() => !isLocked && nav(`/lesson/${l.id}`)}
                disabled={isLocked}
                data-testid={`lesson-node-${i}`}
                className={`relative ${offsets[offset]} group`}
              >
                <div className={`w-20 h-20 rounded-full flex items-center justify-center border-4 border-slate-900 transition-all
                  ${isCompleted ? "bg-green-400" : isCurrent ? "bg-violet-500 node-current" : "bg-slate-200"}
                  ${isLocked ? "opacity-60" : "shadow-[0_4px_0_0_#0F172A] hover:translate-y-0.5 hover:shadow-[0_2px_0_0_#0F172A]"}
                `}>
                  {isCompleted ? (
                    <Check className="w-10 h-10 text-white" strokeWidth={4} />
                  ) : isLocked ? (
                    <Lock className="w-8 h-8 text-slate-500" strokeWidth={3} />
                  ) : (
                    <Star className="w-9 h-9 text-white" strokeWidth={3} fill="white" />
                  )}
                </div>
                <div className="mt-2 text-center font-extrabold text-sm text-slate-700 max-w-[140px] mx-auto leading-tight">
                  {l.title}
                </div>
              </motion.button>
            </div>
          );
        })}
      </div>
    </Layout>
  );
}
