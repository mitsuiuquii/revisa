import { NavLink } from "react-router-dom";
import { Home, Trophy, Medal, User, Sparkles } from "lucide-react";

const items = [
  { to: "/home", label: "Trilhas", icon: Home, testid: "nav-home" },
  { to: "/practice", label: "IA", icon: Sparkles, testid: "nav-practice" },
  { to: "/achievements", label: "Conquistas", icon: Medal, testid: "nav-achievements" },
  { to: "/leaderboard", label: "Ranking", icon: Trophy, testid: "nav-leaderboard" },
  { to: "/profile", label: "Perfil", icon: User, testid: "nav-profile" },
];

export default function BottomNav() {
  return (
    <nav className="fixed bottom-0 left-0 right-0 z-30 bg-white border-t-2 border-slate-900">
      <div className="max-w-md mx-auto px-2 py-2 flex justify-between items-stretch">
        {items.map((it) => (
          <NavLink
            key={it.to}
            to={it.to}
            data-testid={it.testid}
            className={({ isActive }) =>
              `flex-1 flex flex-col items-center gap-0.5 py-2 mx-0.5 rounded-2xl transition-colors ${
                isActive ? "bg-violet-500 text-white" : "text-slate-700 hover:bg-slate-100"
              }`
            }
          >
            <it.icon className="w-5 h-5" strokeWidth={2.8} />
            <span className="text-[11px] font-extrabold font-body uppercase tracking-wide">{it.label}</span>
          </NavLink>
        ))}
      </div>
    </nav>
  );
}
