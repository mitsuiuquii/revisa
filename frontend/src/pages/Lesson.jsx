import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { X, Check, Heart } from "lucide-react";
import confetti from "canvas-confetti";
import { useAuth } from "../lib/auth";
import { toast } from "sonner";

export default function Lesson() {
  const { lessonId } = useParams();
  const nav = useNavigate();
  const { refreshUser } = useAuth();
  const [data, setData] = useState(null);
  const [idx, setIdx] = useState(0);
  const [selected, setSelected] = useState(null);
  const [answered, setAnswered] = useState(false);
  const [answers, setAnswers] = useState([]);
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const cardRef = useRef(null);

  useEffect(() => {
    api.get(`/lessons/${lessonId}`).then(({ data }) => setData(data));
  }, [lessonId]);

  if (!data) return <div className="min-h-screen flex items-center justify-center text-slate-500 font-bold">Carregando…</div>;
  const { lesson, questions } = data;

  if (questions.length === 0) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-6">
        <p className="font-display text-2xl text-slate-900 mb-4">Em breve! 🚧</p>
        <button onClick={() => nav(-1)} className="btn-tactile btn-primary-revisa">Voltar</button>
      </div>
    );
  }

  const q = questions[idx];
  const isCorrect = answered && selected === q.correct_index;
  const progressPct = ((idx + (answered ? 1 : 0)) / questions.length) * 100;

  const onCheck = () => {
    if (selected == null) return;
    setAnswered(true);
    if (selected === q.correct_index) {
      // small pop
      confetti({ particleCount: 25, spread: 60, origin: { y: 0.7 }, colors: ["#22C55E", "#EAB308", "#8B5CF6"] });
    } else {
      cardRef.current?.classList.add("shake");
      setTimeout(() => cardRef.current?.classList.remove("shake"), 450);
    }
  };

  const onNext = async () => {
    const newAnswers = [...answers, { question_id: q.id, selected_index: selected }];
    setAnswers(newAnswers);
    if (idx + 1 < questions.length) {
      setIdx(idx + 1);
      setSelected(null);
      setAnswered(false);
    } else {
      // submit
      setSubmitting(true);
      try {
        const { data: res } = await api.post("/lessons/complete", { lesson_id: lessonId, answers: newAnswers });
        setResult(res);
        await refreshUser();
        confetti({ particleCount: 180, spread: 90, origin: { y: 0.5 }, colors: ["#8B5CF6", "#F97316", "#EAB308", "#22C55E", "#EF4444"] });
      } catch (err) {
        toast.error(err.response?.data?.detail || "Erro ao enviar");
      } finally {
        setSubmitting(false);
      }
    }
  };

  if (result) {
    return (
      <div className="min-h-screen bg-[#FAFAFA] flex flex-col items-center justify-center p-6">
        <div className="max-w-md w-full text-center">
          <motion.div initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ type: "spring", stiffness: 300 }}>
            <div className="text-6xl mb-2">{result.perfect ? "🏆" : result.correct >= result.total / 2 ? "🎉" : "💪"}</div>
            <h1 className="font-display font-extrabold text-4xl text-slate-900 leading-none mb-2">
              {result.perfect ? "Perfeito!" : result.correct >= result.total / 2 ? "Mandou bem!" : "Continua tentando!"}
            </h1>
            <p className="text-slate-600 font-bold mb-8">Acertou {result.correct} de {result.total} questões</p>
          </motion.div>

          <div className="grid grid-cols-2 gap-3 mb-8">
            <div className="tactile-card p-4 bg-yellow-50">
              <div className="text-xs uppercase font-extrabold text-yellow-700 tracking-widest">XP ganho</div>
              <div className="font-display font-extrabold text-3xl text-yellow-700">+{result.xp_earned}</div>
            </div>
            <div className="tactile-card p-4 bg-orange-50">
              <div className="text-xs uppercase font-extrabold text-orange-700 tracking-widest">Ofensiva</div>
              <div className="font-display font-extrabold text-3xl text-orange-700">{result.new_streak}🔥</div>
            </div>
          </div>

          {result.new_achievements?.length > 0 && (
            <div className="mb-6">
              <p className="text-sm uppercase font-extrabold text-slate-500 mb-2 tracking-widest">Novas conquistas!</p>
              <div className="space-y-2">
                {result.new_achievements.map((a) => (
                  <div key={a.id} className="tactile-card p-3 flex items-center gap-3 text-left" style={{ background: a.color + "11" }}>
                    <div className="w-10 h-10 rounded-2xl flex items-center justify-center border-2 border-slate-900" style={{ background: a.color, color: "white" }}>
                      <Check className="w-5 h-5" strokeWidth={3} />
                    </div>
                    <div>
                      <div className="font-display font-extrabold text-slate-900">{a.name}</div>
                      <div className="text-xs text-slate-600 font-bold">{a.description}</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          <button onClick={() => nav("/home")} className="btn-tactile btn-primary-revisa w-full text-lg" data-testid="lesson-result-continue">
            Continuar
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#FAFAFA] flex flex-col">
      {/* Header w/ progress */}
      <header className="px-5 py-4 flex items-center gap-3 max-w-md mx-auto w-full">
        <button onClick={() => nav(-1)} data-testid="lesson-close" className="p-2 hover:bg-slate-100 rounded-full">
          <X className="w-6 h-6 text-slate-500" strokeWidth={3} />
        </button>
        <div className="flex-1 h-3 bg-slate-200 rounded-full overflow-hidden border border-slate-300">
          <motion.div className="h-full bg-gradient-to-r from-violet-500 to-violet-600" initial={false} animate={{ width: `${progressPct}%` }} />
        </div>
      </header>

      <main className="flex-1 max-w-md mx-auto w-full px-5 pb-32">
        <AnimatePresence mode="wait">
          <motion.div
            ref={cardRef}
            key={q.id}
            initial={{ x: 30, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -30, opacity: 0 }}
            className="mt-4"
          >
            <p className="text-xs uppercase tracking-widest font-extrabold text-slate-500 mb-1">{lesson.title} · {idx + 1}/{questions.length}</p>
            <h2 className="font-display font-extrabold text-2xl text-slate-900 leading-tight mb-6" data-testid="question-prompt">{q.prompt}</h2>

            <div className="space-y-3">
              {q.options.map((opt, i) => {
                const sel = selected === i;
                let style = "bg-white border-slate-300";
                if (answered) {
                  if (i === q.correct_index) style = "bg-green-100 border-green-500 text-green-800";
                  else if (sel) style = "bg-red-100 border-red-500 text-red-800";
                  else style = "bg-white border-slate-200 opacity-60";
                } else if (sel) {
                  style = "bg-violet-100 border-violet-500 text-violet-800";
                }
                return (
                  <button
                    key={`${q.id}-${i}`}
                    onClick={() => !answered && setSelected(i)}
                    disabled={answered}
                    data-testid={`option-${i}`}
                    className={`w-full text-left px-4 py-4 rounded-2xl border-2 font-bold text-base transition-all ${style}`}
                  >
                    {opt}
                  </button>
                );
              })}
            </div>
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Sticky footer */}
      <div className={`fixed bottom-0 left-0 right-0 border-t-2 ${answered ? (isCorrect ? "border-green-500 bg-green-50" : "border-red-500 bg-red-50") : "border-slate-900 bg-white"}`}>
        <div className="max-w-md mx-auto p-4">
          {answered && (
            <motion.div initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="mb-3">
              <div className={`flex items-center gap-2 font-display font-extrabold text-xl ${isCorrect ? "text-green-700" : "text-red-700"}`}>
                {isCorrect ? <Check className="w-6 h-6" strokeWidth={4} /> : <Heart className="w-6 h-6" strokeWidth={3} fill="currentColor" />}
                {isCorrect ? "Boa! Acertou." : "Não foi dessa vez."}
              </div>
              {q.explanation && <p className="text-sm text-slate-700 font-bold mt-1">{q.explanation}</p>}
            </motion.div>
          )}
          {!answered ? (
            <button
              onClick={onCheck}
              disabled={selected == null}
              className="btn-tactile btn-primary-revisa w-full text-lg"
              data-testid="lesson-check-btn"
            >
              Verificar
            </button>
          ) : (
            <button
              onClick={onNext}
              disabled={submitting}
              className={`btn-tactile w-full text-lg ${isCorrect ? "btn-primary-revisa" : "btn-secondary-revisa"}`}
              style={!isCorrect ? { background: "#EF4444", color: "white", borderColor: "#0F172A" } : {}}
              data-testid="lesson-next-btn"
            >
              {submitting ? "Enviando…" : (idx + 1 < questions.length ? "Continuar" : "Finalizar")}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
