import { Link, Navigate } from "react-router-dom";
import { motion } from "framer-motion";
import { useAuth } from "../lib/auth";
import { Sparkles, Flame, Trophy } from "lucide-react";
import GoogleButton from "../components/GoogleButton";

const LOGO = "https://customer-assets.emergentagent.com/job_3deef2eb-e33c-4bae-ab9e-1ab16146e6a5/artifacts/durmzo7q_ChatGPT%20Image%206%20de%20mai.%20de%202026%2C%2008_15_49.png";

export default function Welcome() {
  const { user } = useAuth();
  if (user) return <Navigate to="/home" replace />;

  return (
    <div className="min-h-screen flex flex-col">
      <div className="max-w-md mx-auto w-full px-6 pt-10 pb-8 flex-1 flex flex-col">
        <motion.img
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ type: "spring", stiffness: 300, damping: 14 }}
          src={LOGO}
          alt="Revisa"
          className="w-48 mx-auto -mb-2"
          data-testid="welcome-logo"
        />
        <motion.h1
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.15 }}
          className="font-display font-extrabold text-4xl sm:text-5xl text-slate-900 text-center leading-none mt-2"
        >
          Revisa pra <span className="text-violet-500">arrasar</span><br/>no vestibular.
        </motion.h1>
        <motion.p
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.25 }}
          className="text-center text-slate-600 mt-4 font-bold"
        >
          Questões rapidinhas, XP, ofensiva e conquistas. Estuda 5 minutos por dia, sem chatice.
        </motion.p>

        <div className="grid grid-cols-3 gap-3 mt-8">
          {[
            { icon: Sparkles, label: "+500 questões", c: "bg-violet-100 text-violet-600" },
            { icon: Flame, label: "Ofensiva diária", c: "bg-orange-100 text-orange-600" },
            { icon: Trophy, label: "Conquistas", c: "bg-yellow-100 text-yellow-700" },
          ].map((f, i) => (
            <motion.div
              key={f.label}
              initial={{ y: 20, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: 0.35 + i * 0.08 }}
              className="tactile-card-soft p-3 text-center"
            >
              <div className={`w-10 h-10 rounded-2xl ${f.c} flex items-center justify-center mx-auto mb-1`}>
                <f.icon className="w-5 h-5" strokeWidth={3} />
              </div>
              <div className="text-xs font-extrabold text-slate-700">{f.label}</div>
            </motion.div>
          ))}
        </div>

        <div className="mt-auto pt-10 space-y-3">
          <GoogleButton testId="welcome-cta-google" label="Continuar com Google" />
          <Link to="/register" className="block">
            <button className="btn-tactile btn-primary-revisa w-full text-lg" data-testid="welcome-cta-register">
              Criar conta com e-mail
            </button>
          </Link>
          <Link to="/login" className="block text-center text-slate-700 font-bold text-sm pt-1">
            Já tenho conta
          </Link>
        </div>
      </div>
    </div>
  );
}
