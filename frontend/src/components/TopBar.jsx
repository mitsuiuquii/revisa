import { Heart, Flame, Zap } from "lucide-react";
import { useAuth } from "../lib/auth";
import { motion, AnimatePresence } from "framer-motion";

export default function TopBar() {
  const { user } = useAuth();
  if (!user) return null;
  return (
    <header className="sticky top-0 z-30 backdrop-blur bg-white/85 border-b-2 border-slate-900">
      <div className="max-w-md mx-auto px-5 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2" data-testid="top-logo">
          <div className="font-display font-extrabold text-2xl text-slate-900 tracking-tight">
            Revisa<span className="text-violet-500">.</span>
          </div>
        </div>
        <div className="flex items-center gap-3 font-display font-extrabold">
          <Stat icon={<Flame className="w-5 h-5" strokeWidth={3} />} value={user.streak} color="text-orange-500" testid="top-streak" />
          <Stat icon={<Zap className="w-5 h-5" strokeWidth={3} fill="currentColor" />} value={user.xp} color="text-yellow-500" testid="top-xp" />
          <Stat icon={<Heart className="w-5 h-5" strokeWidth={3} fill="currentColor" />} value={user.lives} color="text-red-500" testid="top-lives" />
        </div>
      </div>
    </header>
  );
}

function Stat({ icon, value, color, testid }) {
  return (
    <div className={`flex items-center gap-1 ${color}`} data-testid={testid}>
      <AnimatePresence mode="popLayout">
        <motion.span
          key={value}
          initial={{ scale: 0.6, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 1.2, opacity: 0 }}
          transition={{ type: "spring", stiffness: 400, damping: 12 }}
          className="text-base"
        >
          {icon}
        </motion.span>
      </AnimatePresence>
      <span className="text-base text-slate-900">{value}</span>
    </div>
  );
}
