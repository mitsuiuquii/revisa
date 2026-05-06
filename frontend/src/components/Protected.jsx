import { Navigate } from "react-router-dom";
import { useAuth } from "../lib/auth";

export default function Protected({ children }) {
  const { user, loading } = useAuth();
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="font-display text-2xl text-slate-700">Carregando…</div>
      </div>
    );
  }
  if (!user) return <Navigate to="/login" replace />;
  return children;
}
