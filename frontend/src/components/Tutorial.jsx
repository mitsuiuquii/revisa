import { useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Zap, Coins, Heart, Flame, Trophy, Sparkles, Lock, Users, SkipForward, BarChart3 } from "lucide-react";

const STORAGE_KEY = "revisa_tutorial_seen";

export default function Tutorial({ open, onClose, forceFirstTime }) {
  const [step, setStep] = useState(0);
  const [internalOpen, setInternalOpen] = useState(false);

  useEffect(() => {
    if (forceFirstTime && !localStorage.getItem(STORAGE_KEY)) {
      setInternalOpen(true);
    }
  }, [forceFirstTime]);

  const isOpen = open || internalOpen;

  const finish = () => {
    localStorage.setItem(STORAGE_KEY, "1");
    setInternalOpen(false);
    setStep(0);
    onClose && onClose();
  };

  const steps = [
    {
      title: "Bem-vindo ao Revisa! 👋",
      body: "Um app pra você arrasar nas revisões do vestibular. Estilo ENEM e FUVEST, do básico ao avançado.",
      icon: Sparkles, color: "#8B5CF6",
    },
    {
      title: "Trilhas por matéria",
      body: "Cada matéria tem 4 níveis: Básico (6º-9º), Intermediário, Avançado e Pré-Vestibular. Você precisa subir de patente pra desbloquear níveis mais altos.",
      icon: Lock, color: "#3B82F6",
    },
    {
      title: "Patentes",
      body: "Acumule XP pra subir: Bronze → Prata → Ouro → Platina → Diamante → Sábio. Cada patente desbloqueia conteúdos novos.",
      icon: Trophy, color: "#EAB308",
    },
    {
      title: "XP, vidas e ofensiva",
      body: "Ganhe XP por questão (varia por dificuldade) + bônus se gabaritar. Vidas ❤️ caem quando você erra. Mantenha sua ofensiva 🔥 estudando todo dia!",
      icon: Zap, color: "#F97316",
    },
    {
      title: "Moedas 🪙",
      body: "Ganhe 1 moeda por acerto, +3 se gabaritar. Use as moedas pra comprar habilidades durante as lições.",
      icon: Coins, color: "#EAB308",
    },
    {
      title: "Habilidades especiais",
      body: "Custam 15 moedas e você só pode usar 1 por lição: Universitários (50/50), Pular Questão e Plateia (estatística).",
      icon: Users, color: "#22C55E",
    },
    {
      title: "Bora começar! 🚀",
      body: "Escolhe uma matéria e parte pra cima. Você consegue!",
      icon: Flame, color: "#EF4444",
    },
  ];

  if (!isOpen) return null;
  const s = steps[step];
  const Icon = s.icon;

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
        className="fixed inset-0 bg-slate-900/60 z-50 flex items-end sm:items-center justify-center p-4"
        onClick={finish}
      >
        <motion.div
          initial={{ y: 50, scale: 0.9, opacity: 0 }}
          animate={{ y: 0, scale: 1, opacity: 1 }}
          exit={{ y: 50, opacity: 0 }}
          transition={{ type: "spring", stiffness: 300, damping: 25 }}
          onClick={(e) => e.stopPropagation()}
          className="tactile-card w-full max-w-md p-6"
          data-testid="tutorial-modal"
        >
          <div className="flex justify-between items-center mb-4">
            <div className="flex gap-1">
              {steps.map((stepItem, i) => (
                <div key={stepItem.title} className={`h-1.5 rounded-full transition-all ${i === step ? "w-8 bg-violet-500" : i < step ? "w-4 bg-violet-300" : "w-4 bg-slate-200"}`} />
              ))}
            </div>
            <button onClick={finish} className="p-1 hover:bg-slate-100 rounded-full" data-testid="tutorial-close">
              <X className="w-5 h-5 text-slate-500" strokeWidth={3} />
            </button>
          </div>

          <div
            className="w-16 h-16 rounded-3xl flex items-center justify-center border-2 border-slate-900 mx-auto mb-4"
            style={{ background: s.color, color: "white" }}
          >
            <Icon className="w-8 h-8" strokeWidth={3} />
          </div>
          <h2 className="font-display font-extrabold text-2xl text-slate-900 text-center leading-tight">{s.title}</h2>
          <p className="text-slate-600 font-bold text-center mt-2">{s.body}</p>

          <div className="flex gap-2 mt-6">
            {step > 0 && (
              <button onClick={() => setStep(step - 1)} className="btn-tactile btn-secondary-revisa flex-1" data-testid="tutorial-prev">
                Voltar
              </button>
            )}
            {step < steps.length - 1 ? (
              <button onClick={() => setStep(step + 1)} className="btn-tactile btn-primary-revisa flex-1" data-testid="tutorial-next">
                Continuar
              </button>
            ) : (
              <button onClick={finish} className="btn-tactile btn-primary-revisa flex-1" data-testid="tutorial-finish">
                Vamos lá!
              </button>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
}
