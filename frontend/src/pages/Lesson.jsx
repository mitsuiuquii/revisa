import { useEffect, useRef, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { api } from "../lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { X, Check, Heart, Coins, Users, SkipForward, BarChart3, Zap, Trophy } from "lucide-react";
import confetti from "canvas-confetti";
import { useAuth } from "../lib/auth";
import { toast } from "sonner";

const POWERS = [
  { id: "fifty_fifty", name: "50/50", icon: Users, color: "#1800AD" },
  { id: "skip",        name: "Pular", icon: SkipForward, color: "#FF751F" },
  { id: "audience",    name: "Plateia", icon: BarChart3, color: "#00BF63" },
];
const POWER_COST = 15;

export default function Lesson() {
  const { lessonId } = useParams();
  const nav = useNavigate();
  const { user, refreshUser, setUser } = useAuth();
  const [data, setData] = useState(null);
  const [idx, setIdx] = useState(0);
  const [selected, setSelected] = useState(null);
  const [answered, setAnswered] = useState(false);
  const [answers, setAnswers] = useState([]);
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [powerUsed, setPowerUsed] = useState(null); // string id once used
  const [eliminated, setEliminated] = useState([]); // indexes hidden by 50/50
  const [audienceStats, setAudienceStats] = useState(null);
  const cardRef = useRef(null);

  useEffect(() => {
    api.get(`/lessons/${lessonId}`).then(({ data }) => setData(data)).catch((err) => {
      toast.error(err.response?.data?.detail || "Erro ao carregar");
      nav(-1);
    });
  }, [lessonId, nav]);

  if (!data) return <div className="min-h-screen flex items-center justify-center text-slate-500 font-bold">Carregando…</div>;
  const { lesson, questions } = data;
  if (questions.length === 0) {
    return <div className="min-h-screen flex flex-col items-center justify-center p-6">
      <p className="font-display text-2xl text-slate-900 mb-4">Em breve! 🚧</p>
      <button onClick={() => nav(-1)} className="btn-tactile btn-primary-revisa">Voltar</button>
    </div>;
  }

  const q = questions[idx];
  const isCorrect = answered && selected === q.correct_index;
  const progressPct = ((idx + (answered ? 1 : 0)) / questions.length) * 100;

  const handleUsePower = async (powerId) => {
    if (powerUsed) { toast.error("Você já usou uma habilidade nesta lição"); return; }
    if ((user?.coins || 0) < POWER_COST) { toast.error("Moedas insuficientes"); return; }
    try {
      const { data: res } = await api.post("/powers/use", { power_id: powerId });
      setUser({ ...user, coins: res.new_coins });
      setPowerUsed(powerId);

      if (powerId === "fifty_fifty") {
        const wrong = q.options.map((_, i) => i).filter(i => i !== q.correct_index);
        const toRemove = wrong.sort(() => Math.random() - 0.5).slice(0, 2);
        setEliminated(toRemove);
      } else if (powerId === "audience") {
        const { data: aud } = await api.get(`/powers/audience/${q.id}`);
        setAudienceStats(aud.percentages);
      } else if (powerId === "skip") {
        // Auto-advance, count as skipped (-1 index = skip)
        const newAnswers = [...answers, { question_id: q.id, selected_index: -1 }];
        setAnswers(newAnswers);
        if (idx + 1 < questions.length) {
          setIdx(idx + 1); setSelected(null); setAnswered(false);
          setEliminated([]); setAudienceStats(null);
        } else {
          submitLesson(newAnswers);
        }
      }
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erro");
    }
  };

  const onCheck = () => {
    if (selected == null) return;
    setAnswered(true);
    if (selected === q.correct_index) {
      confetti({ particleCount: 25, spread: 60, origin: { y: 0.7 }, colors: ["#00BF63", "#FFDE59", "#8000FF"] });
    } else {
      cardRef.current?.classList.add("shake");
      setTimeout(() => cardRef.current?.classList.remove("shake"), 450);
    }
  };

  const submitLesson = async (allAnswers) => {
    setSubmitting(true);
    try {
      const { data: res } = await api.post("/lessons/complete", {
        lesson_id: lessonId, answers: allAnswers, power_used: powerUsed,
      });
      setResult(res);
      await refreshUser();
      confetti({ particleCount: 180, spread: 90, origin: { y: 0.5 }, colors: ["#8000FF", "#FF751F", "#FFDE59", "#00BF63", "#FF3131"] });
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erro");
    } finally { setSubmitting(false); }
  };

  const onNext = async () => {
    const newAnswers = [...answers, { question_id: q.id, selected_index: selected }];
    setAnswers(newAnswers);
    if (idx + 1 < questions.length) {
      setIdx(idx + 1); setSelected(null); setAnswered(false);
      setEliminated([]); setAudienceStats(null);
    } else {
      submitLesson(newAnswers);
    }
  };

  if (result) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-6">
        <div className="max-w-md w-full text-center">
          <motion.div initial={{ scale: 0.5, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ type: "spring", stiffness: 300 }}>
            <div className="text-6xl mb-2">{result.perfect ? "🏆" : result.correct >= result.total / 2 ? "🎉" : "💪"}</div>
            <h1 className="font-display font-extrabold text-4xl text-slate-900 leading-none mb-1">
              {result.perfect ? "Perfeito!" : result.correct >= result.total / 2 ? "Mandou bem!" : "Continua tentando!"}
            </h1>
            <p className="text-slate-600 font-bold mb-6">Acertou {result.correct} de {result.total} ({result.accuracy}%)</p>
          </motion.div>

          {result.rank_up && (
            <motion.div initial={{ scale: 0.5 }} animate={{ scale: 1 }} className="tactile-card p-4 mb-4" style={{ background: result.new_rank.color + "22", borderColor: result.new_rank.color }} data-testid="rank-up-banner">
              <div className="text-xs uppercase font-extrabold tracking-widest" style={{ color: result.new_rank.color }}>SUBIU DE PATENTE!</div>
              <div className="font-display font-extrabold text-2xl mt-1" style={{ color: result.new_rank.color }}>
                {result.old_rank.name} → {result.new_rank.name}
              </div>
            </motion.div>
          )}

          <div className="grid grid-cols-3 gap-2 mb-6">
            <div className="tactile-card p-3 bg-blue-50">
              <Zap className="w-5 h-5 mx-auto text-blue-600" strokeWidth={3} fill="currentColor" />
              <div className="font-display font-extrabold text-2xl text-blue-700 mt-1">+{result.xp_earned}</div>
              <div className="text-[9px] uppercase font-extrabold tracking-widest text-blue-700">XP</div>
            </div>
            <div className="tactile-card p-3 bg-yellow-50">
              <Coins className="w-5 h-5 mx-auto text-yellow-600" strokeWidth={3} fill="currentColor" />
              <div className="font-display font-extrabold text-2xl text-yellow-700 mt-1">+{result.coins_earned}</div>
              <div className="text-[9px] uppercase font-extrabold tracking-widest text-yellow-700">moedas</div>
            </div>
            <div className="tactile-card p-3 bg-red-50">
              <Trophy className="w-5 h-5 mx-auto text-red-600" strokeWidth={3} />
              <div className="font-display font-extrabold text-2xl text-red-700 mt-1">{result.new_streak}</div>
              <div className="text-[9px] uppercase font-extrabold tracking-widest text-red-700">ofensiva</div>
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
    <div className="min-h-screen flex flex-col">
      <header className="px-4 py-3 flex items-center gap-3 max-w-md mx-auto w-full">
        <button onClick={() => nav(-1)} data-testid="lesson-close" className="p-2 hover:bg-slate-100 rounded-full">
          <X className="w-5 h-5 text-slate-500" strokeWidth={3} />
        </button>
        <div className="flex-1 h-3 bg-slate-200 rounded-full overflow-hidden border border-slate-300">
          <motion.div className="h-full bg-gradient-to-r from-blue-500 to-purple-600" initial={false} animate={{ width: `${progressPct}%` }} />
        </div>
        <div className="flex items-center gap-1 text-yellow-600 font-extrabold" data-testid="lesson-coins">
          <Coins className="w-4 h-4" strokeWidth={3} fill="currentColor" />
          <span>{user?.coins || 0}</span>
        </div>
      </header>

      <main className="flex-1 max-w-md mx-auto w-full px-5 pb-40">
        <AnimatePresence mode="wait">
          <motion.div ref={cardRef} key={q.id}
            initial={{ x: 30, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: -30, opacity: 0 }}
            className="mt-2"
          >
            <div className="flex items-center gap-2 mb-1 flex-wrap">
              <p className="text-[10px] uppercase tracking-widest font-extrabold text-slate-500">{lesson.title} · {idx + 1}/{questions.length}</p>
              <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full"
                style={{ background: q.difficulty === "facil" ? "#DCFCE7" : q.difficulty === "medio" ? "#FEF3C7" : "#FEE2E2",
                         color: q.difficulty === "facil" ? "#15803D" : q.difficulty === "medio" ? "#A16207" : "#B91C1C" }}>
                {q.difficulty}
              </span>
              {q.source && (
                <span className="text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full bg-purple-100 text-purple-700">
                  {q.source}
                </span>
              )}
            </div>
            <h2 className="font-display font-extrabold text-2xl text-slate-900 leading-tight mb-5" data-testid="question-prompt">{q.prompt}</h2>

            <div className="space-y-3">
              {q.options.map((opt, i) => {
                if (eliminated.includes(i)) return null;
                const sel = selected === i;
                let style = "bg-white border-slate-300";
                if (answered) {
                  if (i === q.correct_index) style = "bg-green-100 border-green-500 text-green-800";
                  else if (sel) style = "bg-red-100 border-red-500 text-red-800";
                  else style = "bg-white border-slate-200 opacity-60";
                } else if (sel) style = "bg-blue-100 border-blue-500 text-blue-800";
                return (
                  <button key={`${q.id}-${i}`}
                    onClick={() => !answered && setSelected(i)}
                    disabled={answered}
                    data-testid={`option-${i}`}
                    className={`w-full text-left px-4 py-4 rounded-2xl border-2 font-bold text-base transition-all relative ${style}`}
                  >
                    <span>{opt}</span>
                    {audienceStats && (
                      <div className="mt-2 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                        <div className="h-full bg-green-500" style={{ width: `${audienceStats[i]}%` }} />
                      </div>
                    )}
                    {audienceStats && <span className="absolute right-3 top-3 text-xs text-green-600 font-extrabold">{audienceStats[i]}%</span>}
                  </button>
                );
              })}
            </div>
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Powers bar */}
      <div className="fixed bottom-0 left-0 right-0">
        <div className="max-w-md mx-auto bg-white border-t-2 border-slate-900">
          {!answered && (
            <div className="px-4 pt-3 pb-1 flex gap-2 justify-between" data-testid="powers-bar">
              {POWERS.map((p) => {
                const used = powerUsed === p.id;
                const disabled = !!powerUsed || (user?.coins || 0) < POWER_COST;
                return (
                  <button key={p.id}
                    onClick={() => handleUsePower(p.id)}
                    disabled={disabled || used}
                    data-testid={`power-${p.id}`}
                    className={`flex-1 flex flex-col items-center gap-0.5 py-2 px-1 rounded-2xl border-2 transition-all
                      ${used ? "bg-slate-100 border-slate-300 opacity-40" :
                        disabled ? "bg-slate-50 border-slate-200 opacity-50" :
                        "bg-white border-slate-900 hover:translate-y-0.5"}`}
                    style={!disabled && !used ? { boxShadow: "0 3px 0 0 #0F172A" } : {}}
                  >
                    <p.icon className="w-5 h-5" strokeWidth={3} style={{ color: p.color }} />
                    <span className="text-[10px] font-extrabold uppercase">{p.name}</span>
                    <span className="text-[9px] font-extrabold text-yellow-600 flex items-center gap-0.5">
                      <Coins className="w-2.5 h-2.5" fill="currentColor" /> {POWER_COST}
                    </span>
                  </button>
                );
              })}
            </div>
          )}

          <div className={`p-4 ${answered ? (isCorrect ? "bg-green-50" : "bg-red-50") : ""}`}>
            {answered && (
              <motion.div initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} className="mb-3">
                <div className={`flex items-center gap-2 font-display font-extrabold text-lg ${isCorrect ? "text-green-700" : "text-red-700"}`}>
                  {isCorrect ? <Check className="w-6 h-6" strokeWidth={4} /> : <Heart className="w-6 h-6" strokeWidth={3} fill="currentColor" />}
                  {isCorrect ? "Boa! Acertou." : "Não foi dessa vez."}
                </div>
                {q.explanation && <p className="text-sm text-slate-700 font-bold mt-1">{q.explanation}</p>}
              </motion.div>
            )}
            {!answered ? (
              <button onClick={onCheck} disabled={selected == null}
                className="btn-tactile btn-primary-revisa w-full text-lg" data-testid="lesson-check-btn">
                Verificar
              </button>
            ) : (
              <button onClick={onNext} disabled={submitting}
                className={`btn-tactile w-full text-lg ${isCorrect ? "btn-primary-revisa" : "btn-secondary-revisa"}`}
                style={!isCorrect ? { background: "#EF4444", color: "white", borderColor: "#0F172A" } : {}}
                data-testid="lesson-next-btn">
                {submitting ? "Enviando…" : (idx + 1 < questions.length ? "Continuar" : "Finalizar")}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
