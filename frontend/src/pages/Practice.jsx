import { useState } from "react";
import Layout from "../components/Layout";
import { api } from "../lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { Sparkles, Loader2, Check, X } from "lucide-react";
import { toast } from "sonner";

const SUBJECTS = ["Matemática", "Português", "História", "Geografia", "Biologia", "Química", "Física", "Literatura", "Inglês", "Redação"];
const DIFFICULTIES = [{ id: "facil", label: "Fácil" }, { id: "medio", label: "Médio" }, { id: "dificil", label: "Difícil" }];

export default function Practice() {
  const [subject, setSubject] = useState(SUBJECTS[0]);
  const [difficulty, setDifficulty] = useState("medio");
  const [busy, setBusy] = useState(false);
  const [q, setQ] = useState(null);
  const [selected, setSelected] = useState(null);
  const [answered, setAnswered] = useState(false);

  const generate = async () => {
    setBusy(true); setQ(null); setSelected(null); setAnswered(false);
    try {
      const { data } = await api.post("/practice/ai", { subject, difficulty });
      setQ(data);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erro ao gerar questão");
    } finally {
      setBusy(false);
    }
  };

  return (
    <Layout>
      <div className="flex items-center gap-2 mb-2">
        <Sparkles className="w-6 h-6 text-violet-500" strokeWidth={3} />
        <h1 className="font-display font-extrabold text-3xl text-slate-900 leading-none">Pratique com IA</h1>
      </div>
      <p className="text-slate-600 font-bold mt-1">Questão nova geradinha pra você 🚀</p>

      <div className="mt-6 space-y-3">
        <div>
          <label className="text-xs font-extrabold uppercase tracking-widest text-slate-700">Matéria</label>
          <div className="flex flex-wrap gap-2 mt-2">
            {SUBJECTS.map((s) => (
              <button
                key={s}
                onClick={() => setSubject(s)}
                data-testid={`practice-subj-${s}`}
                className={`px-3 py-1.5 rounded-full text-sm font-extrabold border-2 transition-all ${subject === s ? "bg-violet-500 text-white border-slate-900" : "bg-white text-slate-700 border-slate-300 hover:border-violet-400"}`}
              >
                {s}
              </button>
            ))}
          </div>
        </div>
        <div>
          <label className="text-xs font-extrabold uppercase tracking-widest text-slate-700">Dificuldade</label>
          <div className="flex gap-2 mt-2">
            {DIFFICULTIES.map((d) => (
              <button
                key={d.id}
                onClick={() => setDifficulty(d.id)}
                data-testid={`practice-diff-${d.id}`}
                className={`flex-1 py-2 rounded-2xl text-sm font-extrabold border-2 transition-all ${difficulty === d.id ? "bg-orange-500 text-white border-slate-900" : "bg-white text-slate-700 border-slate-300"}`}
              >
                {d.label}
              </button>
            ))}
          </div>
        </div>
        <button onClick={generate} disabled={busy} className="btn-tactile btn-primary-revisa w-full flex items-center justify-center gap-2" data-testid="practice-generate">
          {busy ? <><Loader2 className="w-5 h-5 animate-spin" /> Gerando…</> : <><Sparkles className="w-5 h-5" strokeWidth={3} /> Gerar questão</>}
        </button>
      </div>

      <AnimatePresence>
        {q && (
          <motion.div
            initial={{ y: 20, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ opacity: 0 }}
            className="mt-6 tactile-card p-5"
          >
            <p className="text-xs uppercase tracking-widest font-extrabold text-violet-600 mb-2">{subject} · {difficulty}</p>
            <h2 className="font-display font-extrabold text-xl text-slate-900 mb-4">{q.prompt}</h2>
            <div className="space-y-2">
              {q.options.map((opt, i) => {
                let style = "bg-white border-slate-300";
                if (answered) {
                  if (i === q.correct_index) style = "bg-green-100 border-green-500 text-green-800";
                  else if (selected === i) style = "bg-red-100 border-red-500 text-red-800";
                  else style = "bg-white border-slate-200 opacity-60";
                } else if (selected === i) style = "bg-violet-100 border-violet-500";
                return (
                  <button
                    key={`${q.id}-${i}`}
                    disabled={answered}
                    onClick={() => setSelected(i)}
                    className={`w-full text-left px-3 py-3 rounded-2xl border-2 font-bold transition-all ${style}`}
                    data-testid={`practice-opt-${i}`}
                  >
                    {opt}
                  </button>
                );
              })}
            </div>
            {!answered ? (
              <button onClick={() => selected != null && setAnswered(true)} disabled={selected == null} className="btn-tactile btn-primary-revisa w-full mt-4" data-testid="practice-check">
                Verificar
              </button>
            ) : (
              <div className="mt-4">
                <div className={`flex items-center gap-2 font-display font-extrabold text-lg mb-2 ${selected === q.correct_index ? "text-green-700" : "text-red-700"}`}>
                  {selected === q.correct_index ? <><Check className="w-5 h-5" strokeWidth={4} /> Acertou!</> : <><X className="w-5 h-5" strokeWidth={4} /> Errou</>}
                </div>
                {q.explanation && <p className="text-sm text-slate-700 font-bold">{q.explanation}</p>}
                <button onClick={generate} className="btn-tactile btn-primary-revisa w-full mt-4" data-testid="practice-another">Outra questão</button>
              </div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </Layout>
  );
}
