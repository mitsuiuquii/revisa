import { Heart, Flame, Zap, Coins, HelpCircle } from "lucide-react";
import * as Icons from "lucide-react";
import { useAuth } from "../lib/auth";
import { motion, AnimatePresence } from "framer-motion";

export default function TopBar({ onHelp }) {
  const { user } = useAuth();
  if (!user) return null;
  const RankIcon = Icons[user.rank?.icon] || Icons.Medal;
  return (
    <header className="sticky top-0 z-30 backdrop-blur bg-white/85 border-b-2 border-slate-900">
      <div className="max-w-md mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2 min-w-0" data-testid="top-logo">
          <div className="font-display font-extrabold text-xl text-slate-900 tracking-tight shrink-0">
            Revisa<span style={{ color: "#FF751F" }}>.</span>
          </div>
          <div
            className="flex items-center gap-1 px-2 py-0.5 rounded-full border-2 border-slate-900 text-xs font-extrabold"
            style={{ background: user.rank?.color + "22", color: user.rank?.color }}
            data-testid="top-rank"
            title={`Patente ${user.rank?.name}`}
          >
            <RankIcon className="w-3.5 h-3.5" strokeWidth={3} />
            <span className="hidden sm:inline">{user.rank?.name}</span>
          </div>
        </div>
        <div className="flex items-center gap-2 font-display font-extrabold text-sm">
          <Stat icon={<Flame className="w-4 h-4" strokeWidth={3} />} value={user.streak} color="text-red-600" testid="top-streak" />
          <Stat icon={<Coins className="w-4 h-4" strokeWidth={3} fill="currentColor" />} value={user.coins} color="text-yellow-500" testid="top-coins" />
          <Stat icon={<Zap className="w-4 h-4" strokeWidth={3} fill="currentColor" />} value={user.xp} color="text-blue-600" testid="top-xp" />
          <Stat icon={<Heart className="w-4 h-4" strokeWidth={3} fill="currentColor" />} value={user.lives} color="text-red-500" testid="top-lives" />
          {onHelp && (
            <button onClick={onHelp} className="ml-1 p-1 hover:bg-slate-100 rounded-full" data-testid="top-help" title="Como funciona">
              <HelpCircle className="w-5 h-5 text-slate-500" strokeWidth={2.5} />
            </button>
          )}
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
        >
          {icon}
        </motion.span>
      </AnimatePresence>
      <span className="text-slate-900">{value}</span>
    </div>
  );
}
