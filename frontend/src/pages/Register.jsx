import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { toast } from "sonner";
import GoogleButton from "../components/GoogleButton";

export default function Register() {
  const { register } = useAuth();
  const nav = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (password.length < 6) { toast.error("Senha precisa ter 6+ caracteres"); return; }
    setBusy(true);
    try {
      await register(name, email, password);
      toast.success("Conta criada! Boa sorte 🚀");
      nav("/home");
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erro ao cadastrar");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <div className="max-w-md mx-auto w-full px-6 pt-10">
        <Link to="/" className="font-display font-extrabold text-2xl text-slate-900 tracking-tight">
          Revisa<span style={{ color: "#FF751F" }}>.</span>
        </Link>
        <h1 className="font-display font-extrabold text-4xl text-slate-900 mt-8 leading-none">Cria sua<br/>conta</h1>
        <p className="text-slate-600 font-bold mt-2">É grátis e leva 30 segundos.</p>

        <form onSubmit={submit} className="mt-8 space-y-4" data-testid="register-form">
          <div>
            <label className="text-xs font-extrabold uppercase tracking-widest text-slate-700">Nome</label>
            <input
              type="text" required value={name} onChange={(e) => setName(e.target.value)}
              className="w-full mt-1 px-4 py-3 bg-white border-2 border-slate-300 rounded-2xl font-bold focus:outline-none focus:border-violet-500"
              data-testid="register-name"
            />
          </div>
          <div>
            <label className="text-xs font-extrabold uppercase tracking-widest text-slate-700">E-mail</label>
            <input
              type="email" required value={email} onChange={(e) => setEmail(e.target.value)}
              className="w-full mt-1 px-4 py-3 bg-white border-2 border-slate-300 rounded-2xl font-bold focus:outline-none focus:border-violet-500"
              data-testid="register-email"
            />
          </div>
          <div>
            <label className="text-xs font-extrabold uppercase tracking-widest text-slate-700">Senha (6+ caracteres)</label>
            <input
              type="password" required minLength={6} value={password} onChange={(e) => setPassword(e.target.value)}
              className="w-full mt-1 px-4 py-3 bg-white border-2 border-slate-300 rounded-2xl font-bold focus:outline-none focus:border-violet-500"
              data-testid="register-password"
            />
          </div>
          <button type="submit" disabled={busy} className="btn-tactile btn-primary-revisa w-full text-lg" data-testid="register-submit">
            {busy ? "Criando…" : "Criar conta"}
          </button>
        </form>

        <div className="flex items-center gap-3 my-5">
          <div className="flex-1 h-px bg-slate-300" />
          <span className="text-xs uppercase tracking-widest font-extrabold text-slate-500">ou</span>
          <div className="flex-1 h-px bg-slate-300" />
        </div>
        <GoogleButton testId="register-google-btn" label="Cadastrar com Google" />

        <p className="mt-6 text-center text-slate-700 font-bold">
          Já tem conta?{" "}
          <Link to="/login" className="text-violet-600 underline-offset-4 hover:underline" data-testid="register-link-login">
            Entrar
          </Link>
        </p>
      </div>
    </div>
  );
}
