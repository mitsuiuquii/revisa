import { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../lib/auth";
import { api } from "../lib/api";
import { motion, AnimatePresence } from "framer-motion";
import { toast } from "sonner";
import {
  Users, Trophy, BookOpen, BarChart3, Search, LogOut,
  Trash2, RefreshCw, ShieldAlert, ChevronDown, ChevronUp,
  Zap, Heart, Flame, Coins, Medal, ArrowLeft, Eye, EyeOff,
} from "lucide-react";
import * as Icons from "lucide-react";

// ─── Admin credentials (hardcoded — troque conforme necessário) ───────────────
const ADMIN_PASSWORD = "revisa@admin2025";

// ─── Tab config ────────────────────────────────────────────────────────────────
const TABS = [
  { id: "users",     label: "Usuários",   icon: Users },
  { id: "stats",     label: "Estatísticas", icon: BarChart3 },
  { id: "subjects",  label: "Matérias",   icon: BookOpen },
  { id: "questions", label: "Questões",   icon: BookOpen },
  { id: "ranking",   label: "Ranking",    icon: Trophy },
];

// ─── Admin Login Screen ────────────────────────────────────────────────────────
function AdminLogin({ onLogin }) {
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setErr("");
    try {
      const { data } = await api.post("/admin/login", { password: ADMIN_PASSWORD });
      // Armazena o token JWT retornado pelo backend
      localStorage.setItem("revisa_token", data.token);
      sessionStorage.setItem("revisa_admin", "1");
      onLogin();
    } catch (err) {
      setErr("Acesso ao painel admin negado. Verifique as credenciais.");
      console.error("Admin login error:", err);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-6" style={{ background: "#0F172A" }}>
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="w-full max-w-sm"
      >
        <div className="text-center mb-8">
          <div className="w-16 h-16 rounded-3xl bg-violet-500 border-4 border-violet-300 flex items-center justify-center mx-auto mb-4">
            <ShieldAlert className="w-8 h-8 text-white" strokeWidth={2.5} />
          </div>
          <h1 className="font-display font-extrabold text-3xl text-white">Painel Admin</h1>
          <p className="text-slate-400 font-bold mt-1 text-sm">Acesso restrito — REVISA</p>
        </div>

        <form onSubmit={submit} className="space-y-4">
          <div>
            <label className="text-xs font-extrabold uppercase tracking-widest text-slate-400">Senha do Admin</label>
            <div className="relative mt-1">
              <input
                type={showPw ? "text" : "password"} 
                required 
                value={password}
                onChange={e => setPassword(e.target.value)}
                placeholder="••••••••"
                className="w-full px-4 py-3 bg-slate-800 border-2 border-slate-600 rounded-2xl font-bold text-white focus:outline-none focus:border-violet-500 pr-12"
                data-testid="admin-password"
              />
              <button type="button" onClick={() => setShowPw(!showPw)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white">
                {showPw ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
          </div>
          {err && <p className="text-red-400 font-bold text-sm text-center">{err}</p>}
          <button type="submit" disabled={busy}
            className="w-full py-3 rounded-2xl bg-violet-500 text-white font-extrabold text-lg border-b-4 border-violet-800 hover:bg-violet-400 active:border-b-0 active:translate-y-1 transition-all disabled:opacity-50"
            data-testid="admin-submit">
            {busy ? "Verificando…" : "Entrar como Admin"}
          </button>
        </form>
      </motion.div>
    </div>
  );
}

// ─── Stat Card ─────────────────────────────────────────────────────────────────
function StatCard({ label, value, icon: Icon, color }) {
  return (
    <div className="tactile-card p-4" style={{ borderColor: color + "66", boxShadow: `3px 3px 0 0 ${color}44` }}>
      <div className="flex items-center gap-2 mb-2">
        <div className="w-8 h-8 rounded-xl flex items-center justify-center" style={{ background: color + "22", color }}>
          <Icon className="w-4 h-4" strokeWidth={3} />
        </div>
        <span className="text-xs uppercase tracking-widest font-extrabold text-slate-500">{label}</span>
      </div>
      <div className="font-display font-extrabold text-3xl text-slate-900">{value}</div>
    </div>
  );
}

// ─── Users Tab ─────────────────────────────────────────────────────────────────
function UsersTab({ users, loading, onRefresh, onDeleteUser }) {
  const [search, setSearch] = useState("");
  const [expandedId, setExpandedId] = useState(null);

  const filtered = users.filter(u =>
    u.name?.toLowerCase().includes(search.toLowerCase()) ||
    u.email?.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="flex gap-3 mb-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" strokeWidth={2.5} />
          <input
            type="text" value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Buscar por nome ou e-mail…"
            className="w-full pl-9 pr-4 py-2.5 bg-white border-2 border-slate-300 rounded-2xl font-bold text-sm focus:outline-none focus:border-violet-500"
          />
        </div>
        <button onClick={onRefresh}
          className="px-4 py-2.5 bg-white border-2 border-slate-300 rounded-2xl font-extrabold text-slate-700 hover:border-violet-400 transition-colors flex items-center gap-2">
          <RefreshCw className="w-4 h-4" strokeWidth={2.5} />
        </button>
      </div>

      <p className="text-xs font-extrabold uppercase tracking-widest text-slate-500 mb-3">
        {filtered.length} usuário{filtered.length !== 1 ? "s" : ""}
      </p>

      {loading && <div className="text-center py-8 text-slate-500 font-bold">Carregando…</div>}

      <div className="space-y-2">
        {filtered.map((u, i) => {
          const expanded = expandedId === u.id;
          const RankIcon = Icons[u.rank?.icon] || Icons.Medal;
          return (
            <motion.div key={u.id}
              initial={{ y: 8, opacity: 0 }} animate={{ y: 0, opacity: 1 }}
              transition={{ delay: i * 0.02 }}
              className="tactile-card overflow-hidden"
            >
              <button
                onClick={() => setExpandedId(expanded ? null : u.id)}
                className="w-full p-4 flex items-center gap-3 text-left"
              >
                <div className="relative">
                  <div className="w-10 h-10 rounded-full flex items-center justify-center font-display font-extrabold text-white text-sm shrink-0"
                    style={{ background: u.avatar_color || "#8B5CF6" }}>
                    {u.picture ? (
                      <img src={u.picture} alt={u.name} className="w-full h-full rounded-full object-cover" />
                    ) : (
                      u.name?.[0]?.toUpperCase()
                    )}
                  </div>
                  {u.google_linked && (
                    <div className="absolute -bottom-1 -right-1 w-5 h-5 rounded-full bg-white border-2 border-blue-500 flex items-center justify-center">
                      <span className="text-xs font-bold text-blue-600">G</span>
                    </div>
                  )}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="font-display font-extrabold text-slate-900 truncate">{u.name}</div>
                  <div className="text-xs font-bold text-slate-500 truncate">
                    {u.google_linked ? "📱 Google • " : ""}{u.email}
                  </div>
                </div>
                <div className="flex items-center gap-2 shrink-0">
                  <span className="hidden sm:inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] uppercase font-extrabold"
                    style={{ background: (u.rank?.color || "#A16207") + "22", color: u.rank?.color || "#A16207" }}>
                    <RankIcon className="w-3 h-3" strokeWidth={3} />
                    {u.rank?.name}
                  </span>
                  <span className="font-display font-extrabold text-yellow-600 text-sm">{u.xp} XP</span>
                  {expanded ? <ChevronUp className="w-4 h-4 text-slate-400" /> : <ChevronDown className="w-4 h-4 text-slate-400" />}
                </div>
              </button>

              <AnimatePresence>
                {expanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.2 }}
                    className="overflow-hidden"
                  >
                    <div className="px-4 pb-4 border-t-2 border-slate-100 pt-3">
                      <div className="grid grid-cols-3 gap-2 mb-3">
                        {[
                          { label: "XP", value: u.xp, icon: Zap, color: "#EAB308" },
                          { label: "Vidas", value: u.lives, icon: Heart, color: "#EF4444" },
                          { label: "Ofensiva", value: u.streak, icon: Flame, color: "#F97316" },
                          { label: "Moedas", value: u.coins, icon: Coins, color: "#D97706" },
                          { label: "Lições", value: u.completed_lessons?.length || 0, icon: BookOpen, color: "#3B82F6" },
                          { label: "Conquistas", value: u.achievements?.length || 0, icon: Medal, color: "#8B5CF6" },
                        ].map(s => (
                          <div key={s.label} className="bg-slate-50 rounded-xl p-2 text-center border border-slate-200">
                            <div className="text-xs font-extrabold text-slate-500 mb-0.5">{s.label}</div>
                            <div className="font-display font-extrabold text-lg" style={{ color: s.color }}>{s.value}</div>
                          </div>
                        ))}
                      </div>
                      <div className="text-xs text-slate-500 font-bold mb-3">
                        Cadastro: {u.created_at ? new Date(u.created_at).toLocaleDateString("pt-BR") : "—"} ·
                        Último acesso: {u.last_active || "Nunca"}
                        {u.google_linked && (
                          <>
                            <br />
                            <span className="text-blue-600 font-bold">✓ Conectado com Google</span>
                          </>
                        )}
                      </div>
                      <button
                        onClick={() => onDeleteUser(u)}
                        className="flex items-center gap-2 px-3 py-2 rounded-xl bg-red-50 border-2 border-red-200 text-red-700 font-extrabold text-sm hover:bg-red-100 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" strokeWidth={2.5} /> Excluir usuário
                      </button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
}

// ─── Stats Tab ─────────────────────────────────────────────────────────────────
function StatsTab({ users, subjects }) {
  const totalXP = users.reduce((s, u) => s + (u.xp || 0), 0);
  const totalLessons = users.reduce((s, u) => s + (u.completed_lessons?.length || 0), 0);
  const avgXP = users.length ? Math.round(totalXP / users.length) : 0;
  const activeToday = users.filter(u => u.last_active === new Date().toISOString().split("T")[0]).length;

  const rankDist = {};
  users.forEach(u => {
    const r = u.rank?.name || "Bronze";
    rankDist[r] = (rankDist[r] || 0) + 1;
  });

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-3">
        <StatCard label="Total usuários" value={users.length} icon={Users} color="#8B5CF6" />
        <StatCard label="Ativos hoje" value={activeToday} icon={Flame} color="#F97316" />
        <StatCard label="XP total gerado" value={totalXP.toLocaleString("pt-BR")} icon={Zap} color="#EAB308" />
        <StatCard label="Média de XP" value={avgXP} icon={BarChart3} color="#3B82F6" />
        <StatCard label="Lições completas" value={totalLessons} icon={BookOpen} color="#22C55E" />
        <StatCard label="Matérias ativas" value={subjects.length} icon={Trophy} color="#EC4899" />
      </div>

      <div className="tactile-card p-5">
        <h3 className="font-display font-extrabold text-lg text-slate-900 mb-4">Distribuição de Patentes</h3>
        {Object.entries(rankDist).length === 0 && <p className="text-slate-500 font-bold text-sm">Nenhum dado ainda.</p>}
        <div className="space-y-2">
          {[
            { name: "Bronze", color: "#A16207" },
            { name: "Prata", color: "#94A3B8" },
            { name: "Ouro", color: "#EAB308" },
            { name: "Platina", color: "#22D3EE" },
            { name: "Diamante", color: "#60A5FA" },
            { name: "Sábio", color: "#A855F7" },
          ].map(r => {
            const count = rankDist[r.name] || 0;
            const pct = users.length ? Math.round((count / users.length) * 100) : 0;
            return (
              <div key={r.name} className="flex items-center gap-3">
                <span className="w-16 text-xs font-extrabold" style={{ color: r.color }}>{r.name}</span>
                <div className="flex-1 h-3 bg-slate-100 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${pct}%` }}
                    transition={{ duration: 0.6, delay: 0.1 }}
                    className="h-full rounded-full"
                    style={{ background: r.color }}
                  />
                </div>
                <span className="w-10 text-right text-xs font-extrabold text-slate-600">{count}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}

// ─── Subjects Tab ──────────────────────────────────────────────────────────────
function SubjectsTab({ subjects }) {
  const [expanded, setExpanded] = useState(null);
  const [lessons, setLessons] = useState({});
  const [loading, setLoading] = useState({});

  const toggleExpand = async (subjectId, subjectName) => {
    if (expanded === subjectId) {
      setExpanded(null);
      return;
    }
    
    // Se já carregou, só expande
    if (lessons[subjectId]) {
      setExpanded(subjectId);
      return;
    }
    
    // Carrega as lições
    setLoading(prev => ({ ...prev, [subjectId]: true }));
    try {
      const { data } = await api.get(`/subjects/${subjectId}/lessons`);
      setLessons(prev => ({ ...prev, [subjectId]: data }));
      setExpanded(subjectId);
    } catch (err) {
      toast.error(`Erro ao carregar lições de ${subjectName}`);
    } finally {
      setLoading(prev => ({ ...prev, [subjectId]: false }));
    }
  };

  return (
    <div className="space-y-3">
      {subjects.length === 0 && <p className="text-slate-500 font-bold text-center py-8">Nenhuma matéria cadastrada.</p>}
      {subjects.map((s, i) => {
        const Icon = Icons[s.icon] || Icons.BookOpen;
        const isExpanded = expanded === s.id;
        const subjectLessons = lessons[s.id] || [];
        const isLoading = loading[s.id];

        return (
          <motion.div key={s.id}
            initial={{ x: -10, opacity: 0 }} animate={{ x: 0, opacity: 1 }}
            transition={{ delay: i * 0.04 }}
          >
            {/* Header - Clicável */}
            <button
              onClick={() => toggleExpand(s.id, s.name)}
              className="tactile-card p-4 flex items-center gap-4 w-full hover:bg-slate-50 transition-colors"
            >
              <div className="w-12 h-12 rounded-2xl flex items-center justify-center border-2 border-slate-900 shrink-0"
                style={{ background: s.color, color: "white" }}>
                <Icon className="w-6 h-6" strokeWidth={2.8} />
              </div>
              <div className="flex-1 min-w-0 text-left">
                <div className="font-display font-extrabold text-slate-900">{s.name}</div>
                <div className="text-xs text-slate-500 font-bold truncate">{s.description}</div>
              </div>
              <div className="text-right shrink-0">
                <div className="font-display font-extrabold text-lg" style={{ color: s.color }}>{s.total_lessons || "—"}</div>
                <div className="text-[10px] uppercase tracking-widest font-extrabold text-slate-400">lições</div>
              </div>
              <div className="shrink-0">
                {isLoading ? (
                  <Zap className="w-5 h-5 text-slate-400 animate-spin" />
                ) : (
                  isExpanded ? <ChevronUp className="w-5 h-5 text-slate-600" /> : <ChevronDown className="w-5 h-5 text-slate-600" />
                )}
              </div>
            </button>

            {/* Expanded Content - Lições */}
            <AnimatePresence>
              {isExpanded && (
                <motion.div
                  initial={{ height: 0, opacity: 0 }}
                  animate={{ height: "auto", opacity: 1 }}
                  exit={{ height: 0, opacity: 0 }}
                  transition={{ duration: 0.2 }}
                  className="overflow-hidden"
                >
                  <div className="pl-16 pr-4 py-3 space-y-2 bg-slate-50 border-l-2 border-slate-200">
                    {isLoading ? (
                      <div className="text-center py-4 text-slate-500 font-bold">Carregando lições...</div>
                    ) : subjectLessons.length === 0 ? (
                      <p className="text-slate-500 font-bold text-sm">Nenhuma lição nesta matéria.</p>
                    ) : (
                      subjectLessons.map((lesson, j) => {
                        // Cores por dificuldade
                        const difficultyColors = {
                          basico: "#22C55E",
                          intermediario: "#F59E0B",
                          avancado: "#EF4444",
                        };
                        const diffColor = difficultyColors[lesson.level] || "#94A3B8";
                        const diffLabel = { basico: "Básico", intermediario: "Médio", avancado: "Avançado" }[lesson.level] || lesson.level;

                        return (
                          <motion.div key={lesson.id}
                            initial={{ x: -10, opacity: 0 }} animate={{ x: 0, opacity: 1 }}
                            transition={{ delay: j * 0.05 }}
                            className="p-3 bg-white rounded-xl border border-slate-200 hover:border-violet-300 hover:shadow-sm transition-all"
                          >
                            <div className="flex items-start justify-between gap-3">
                              <div className="flex-1">
                                <div className="font-bold text-slate-900 text-sm">{lesson.content_name && `${lesson.content_name} • `}{diffLabel}</div>
                                <div className="text-xs text-slate-600 mt-1 font-medium">{lesson.title || lesson.description}</div>
                                <div className="flex items-center gap-4 text-xs text-slate-500 mt-2 flex-wrap">
                                  <span className="flex items-center gap-1">
                                    <span className="inline-block w-2 h-2 rounded-full" style={{ background: diffColor }}></span>
                                    Dificuldade: <span className="font-bold" style={{ color: diffColor }}>{diffLabel}</span>
                                  </span>
                                  <span className="flex items-center gap-1">
                                    📚 <span className="font-bold text-slate-700">{lesson.questions_count || 0}</span> questões
                                  </span>
                                </div>
                              </div>
                              <div className="text-right shrink-0">
                                <div className="text-[11px] font-extrabold text-slate-400 uppercase tracking-wider">#{lesson.order + 1}</div>
                              </div>
                            </div>
                          </motion.div>
                        );
                      })
                    )}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.div>
        );
      })}
    </div>
  );
}


// ─── Questions Tab ─────────────────────────────────────────────────────────────
function QuestionsTab({ subjects }) {
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [selectedLesson, setSelectedLesson] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    prompt: "",
    options: ["", "", "", ""],
    correct_index: 0,
    explanation: "",
    source: "",
  });

  // Carrega lições quando seleciona matéria
  const handleSubjectChange = async (subjectId) => {
    setSelectedSubject(subjectId);
    setSelectedLesson(null);
    setQuestions([]);
    setShowForm(false);
    setLoading(true);
    try {
      const { data } = await api.get(`/subjects/${subjectId}/lessons`);
      setLessons(data);
    } catch (err) {
      toast.error("Erro ao carregar lições");
    } finally {
      setLoading(false);
    }
  };

  // Carrega questões quando seleciona lição
  const handleLessonChange = async (lessonId) => {
    setSelectedLesson(lessonId);
    setShowForm(false);
    setEditingId(null);
    setLoading(true);
    try {
      const { data } = await api.get(`/admin/lessons/${lessonId}/questions`);
      setQuestions(data);
    } catch (err) {
      toast.error("Erro ao carregar questões");
    } finally {
      setLoading(false);
    }
  };

  // Salva questão (criar ou editar)
  const handleSaveQuestion = async () => {
    if (!formData.prompt || !formData.options.some(o => o)) {
      toast.error("Preencha pelo menos a pergunta e uma opção");
      return;
    }

    try {
      if (editingId) {
        await api.put(`/admin/questions/${editingId}`, formData);
        toast.success("Questão atualizada!");
      } else {
        await api.post("/admin/questions", {
          lesson_id: selectedLesson,
          ...formData,
        });
        toast.success("Questão criada!");
      }
      setFormData({ prompt: "", options: ["", "", "", ""], correct_index: 0, explanation: "", source: "" });
      setShowForm(false);
      setEditingId(null);
      handleLessonChange(selectedLesson); // Recarrega
    } catch (err) {
      toast.error("Erro ao salvar questão");
    }
  };

  // Deleta questão
  const handleDeleteQuestion = async (questionId) => {
    if (!window.confirm("Deseja deletar essa questão?")) return;
    try {
      await api.delete(`/admin/questions/${questionId}`);
      toast.success("Questão deletada!");
      handleLessonChange(selectedLesson);
    } catch (err) {
      toast.error("Erro ao deletar questão");
    }
  };

  // Começa a editar questão
  const handleEditQuestion = (question) => {
    setFormData({
      prompt: question.prompt,
      options: question.options,
      correct_index: question.correct_index,
      explanation: question.explanation,
      source: question.source,
    });
    setEditingId(question.id);
    setShowForm(true);
  };

  const selectedSubjectObj = subjects.find(s => s.id === selectedSubject);
  const selectedLessonObj = lessons.find(l => l.id === selectedLesson);

  return (
    <div className="space-y-4">
      {/* Seleção de Matéria */}
      <div>
        <label className="block text-xs uppercase tracking-widest font-extrabold text-slate-500 mb-2">
          Matéria
        </label>
        <select
          value={selectedSubject || ""}
          onChange={(e) => handleSubjectChange(e.target.value)}
          className="w-full px-4 py-2.5 bg-white border-2 border-slate-300 rounded-xl font-bold text-sm focus:outline-none focus:border-violet-500"
        >
          <option value="">Selecione uma matéria...</option>
          {subjects.map(s => (
            <option key={s.id} value={s.id}>{s.name}</option>
          ))}
        </select>
      </div>

      {/* Seleção de Lição */}
      {selectedSubject && (
        <div>
          <label className="block text-xs uppercase tracking-widest font-extrabold text-slate-500 mb-2">
            Lição ({lessons.length})
          </label>
          <select
            value={selectedLesson || ""}
            onChange={(e) => handleLessonChange(e.target.value)}
            className="w-full px-4 py-2.5 bg-white border-2 border-slate-300 rounded-xl font-bold text-sm focus:outline-none focus:border-violet-500"
          >
            <option value="">Selecione uma lição...</option>
            {lessons.map(l => (
              <option key={l.id} value={l.id}>
                {l.content_name} — {l.title?.split("—")[1]?.trim()}
              </option>
            ))}
          </select>
        </div>
      )}

      {/* Info da lição selecionada */}
      {selectedLessonObj && (
        <div className="p-3 bg-violet-50 rounded-xl border-2 border-violet-200">
          <div className="text-sm font-bold text-slate-900">{selectedLessonObj.title}</div>
          <div className="text-xs text-slate-600">
            {questions.length} questões • {selectedLessonObj.description}
          </div>
        </div>
      )}

      {/* Botão criar questão */}
      {selectedLesson && !showForm && (
        <button
          onClick={() => {
            setFormData({ prompt: "", options: ["", "", "", ""], correct_index: 0, explanation: "", source: "" });
            setEditingId(null);
            setShowForm(true);
          }}
          className="w-full px-4 py-2.5 bg-violet-600 hover:bg-violet-700 text-white font-extrabold rounded-xl flex items-center justify-center gap-2 transition-colors"
        >
          <BookOpen className="w-4 h-4" /> Adicionar Questão
        </button>
      )}

      {/* Formulário de questão */}
      {showForm && (
        <motion.div
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: "auto", opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          className="p-4 bg-slate-50 rounded-xl border-2 border-slate-200 space-y-3 overflow-hidden"
        >
          <h3 className="font-bold text-slate-900">{editingId ? "Editar" : "Nova"} Questão</h3>
          
          {/* Pergunta */}
          <div>
            <label className="text-xs font-bold text-slate-600 mb-1 block">Pergunta</label>
            <textarea
              value={formData.prompt}
              onChange={(e) => setFormData({...formData, prompt: e.target.value})}
              placeholder="Digite a pergunta..."
              className="w-full px-3 py-2 border-2 border-slate-300 rounded-lg font-medium text-sm focus:outline-none focus:border-violet-500"
              rows="2"
            />
          </div>

          {/* Opções */}
          <div>
            <label className="text-xs font-bold text-slate-600 mb-1 block">Opções</label>
            {formData.options.map((opt, i) => (
              <div key={i} className="flex items-center gap-2 mb-2">
                <input
                  type="radio"
                  name="correct"
                  checked={formData.correct_index === i}
                  onChange={() => setFormData({...formData, correct_index: i})}
                  className="w-4 h-4"
                />
                <input
                  type="text"
                  value={opt}
                  onChange={(e) => {
                    const newOpts = [...formData.options];
                    newOpts[i] = e.target.value;
                    setFormData({...formData, options: newOpts});
                  }}
                  placeholder={`Opção ${String.fromCharCode(65+i)}`}
                  className="flex-1 px-3 py-2 border-2 border-slate-300 rounded-lg font-medium text-sm focus:outline-none focus:border-violet-500"
                />
              </div>
            ))}
          </div>

          {/* Explicação */}
          <div>
            <label className="text-xs font-bold text-slate-600 mb-1 block">Explicação</label>
            <textarea
              value={formData.explanation}
              onChange={(e) => setFormData({...formData, explanation: e.target.value})}
              placeholder="Por que a resposta está correta?"
              className="w-full px-3 py-2 border-2 border-slate-300 rounded-lg font-medium text-sm focus:outline-none focus:border-violet-500"
              rows="2"
            />
          </div>

          {/* Fonte */}
          <div>
            <label className="text-xs font-bold text-slate-600 mb-1 block">Fonte</label>
            <input
              type="text"
              value={formData.source}
              onChange={(e) => setFormData({...formData, source: e.target.value})}
              placeholder="Ex: ENEM 2020, FUVEST 2019..."
              className="w-full px-3 py-2 border-2 border-slate-300 rounded-lg font-medium text-sm focus:outline-none focus:border-violet-500"
            />
          </div>

          {/* Botões */}
          <div className="flex gap-2 pt-2">
            <button
              onClick={handleSaveQuestion}
              className="flex-1 px-3 py-2 bg-green-600 hover:bg-green-700 text-white font-bold rounded-lg transition-colors text-sm"
            >
              Salvar
            </button>
            <button
              onClick={() => {
                setShowForm(false);
                setEditingId(null);
              }}
              className="flex-1 px-3 py-2 bg-slate-300 hover:bg-slate-400 text-slate-900 font-bold rounded-lg transition-colors text-sm"
            >
              Cancelar
            </button>
          </div>
        </motion.div>
      )}

      {/* Lista de questões */}
      {selectedLesson && (
        <div className="space-y-2">
          {loading && <div className="text-center py-4 text-slate-500 font-bold">Carregando...</div>}
          {!loading && questions.length === 0 && (
            <div className="text-center py-8 text-slate-500 font-bold">Nenhuma questão nesta lição</div>
          )}
          {questions.map((q, i) => (
            <motion.div
              key={q.id}
              initial={{ y: 8, opacity: 0 }}
              animate={{ y: 0, opacity: 1 }}
              transition={{ delay: i * 0.05 }}
              className="p-3 bg-white rounded-xl border-2 border-slate-200 hover:border-violet-300 transition-all"
            >
              <div className="flex items-start justify-between gap-3 mb-2">
                <div className="flex-1">
                  <div className="font-bold text-slate-900 text-sm mb-1">{q.prompt}</div>
                  <div className="space-y-0.5">
                    {q.options.map((opt, idx) => (
                      <div
                        key={idx}
                        className={`text-xs px-2 py-1 rounded ${
                          idx === q.correct_index
                            ? "bg-green-100 text-green-700 font-bold"
                            : "bg-slate-100 text-slate-600"
                        }`}
                      >
                        {String.fromCharCode(65 + idx)}) {opt}
                      </div>
                    ))}
                  </div>
                  {q.explanation && (
                    <div className="text-xs text-slate-600 mt-1">
                      <span className="font-bold">Exp:</span> {q.explanation}
                    </div>
                  )}
                </div>
                <div className="flex gap-1 shrink-0">
                  <button
                    onClick={() => handleEditQuestion(q)}
                    className="p-1.5 bg-blue-50 hover:bg-blue-100 text-blue-600 rounded-lg transition-colors"
                  >
                    <Eye className="w-4 h-4" strokeWidth={2.5} />
                  </button>
                  <button
                    onClick={() => handleDeleteQuestion(q.id)}
                    className="p-1.5 bg-red-50 hover:bg-red-100 text-red-600 rounded-lg transition-colors"
                  >
                    <Trash2 className="w-4 h-4" strokeWidth={2.5} />
                  </button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}

// ─── Ranking Tab ───────────────────────────────────────────────────────────────
function RankingTab({ users }) {
  const sorted = [...users].sort((a, b) => (b.xp || 0) - (a.xp || 0)).slice(0, 20);
  return (
    <div className="space-y-2">
      {sorted.map((u, i) => {
        const RankIcon = Icons[u.rank?.icon] || Icons.Medal;
        const medal = i === 0 ? "#EAB308" : i === 1 ? "#94A3B8" : i === 2 ? "#F97316" : "#E2E8F0";
        return (
          <motion.div key={u.id}
            initial={{ x: -10, opacity: 0 }} animate={{ x: 0, opacity: 1 }}
            transition={{ delay: i * 0.03 }}
            className="tactile-card p-3 flex items-center gap-3"
          >
            <div className="w-8 h-8 rounded-xl flex items-center justify-center border-2 border-slate-900 font-display font-extrabold text-sm shrink-0"
              style={{ background: medal, color: i < 3 ? "white" : "#0F172A" }}>
              {i + 1}
            </div>
            <div className="w-9 h-9 rounded-full flex items-center justify-center font-display font-extrabold text-white text-sm shrink-0"
              style={{ background: u.avatar_color || "#8B5CF6" }}>
              {u.name?.[0]?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <div className="font-display font-extrabold text-slate-900 truncate">{u.name}</div>
              <div className="text-xs font-bold text-slate-500 truncate">{u.email}</div>
            </div>
            <div className="text-right shrink-0">
              <div className="font-display font-extrabold text-yellow-600">{u.xp} XP</div>
              <div className="inline-flex items-center gap-1 text-[10px] uppercase font-extrabold px-1.5 py-0.5 rounded-full"
                style={{ background: (u.rank?.color || "#A16207") + "22", color: u.rank?.color || "#A16207" }}>
                <RankIcon className="w-2.5 h-2.5" strokeWidth={3} />
                {u.rank?.name}
              </div>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}

// ─── Delete Confirm Modal ──────────────────────────────────────────────────────
function DeleteModal({ user, onConfirm, onCancel }) {
  return (
    <div className="fixed inset-0 bg-slate-900/60 z-50 flex items-center justify-center p-4">
      <motion.div
        initial={{ scale: 0.9, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        className="tactile-card w-full max-w-sm p-6"
      >
        <div className="w-14 h-14 rounded-3xl bg-red-100 border-2 border-slate-900 flex items-center justify-center mx-auto mb-4">
          <Trash2 className="w-7 h-7 text-red-600" strokeWidth={2.5} />
        </div>
        <h2 className="font-display font-extrabold text-xl text-slate-900 text-center">Excluir usuário?</h2>
        <p className="text-slate-600 font-bold text-center mt-2 text-sm">
          <strong>{user.name}</strong> ({user.email}) será removido permanentemente. Esta ação não pode ser desfeita.
        </p>
        <div className="flex gap-3 mt-6">
          <button onClick={onCancel} className="btn-tactile btn-secondary-revisa flex-1">Cancelar</button>
          <button onClick={onConfirm} className="flex-1 py-3 rounded-2xl bg-red-500 text-white font-extrabold border-b-4 border-red-800 hover:bg-red-400 active:translate-y-1 active:border-b-0 transition-all">
            Excluir
          </button>
        </div>
      </motion.div>
    </div>
  );
}

// ─── Main Admin Component ──────────────────────────────────────────────────────
export default function Admin() {
  const { logout } = useAuth();
  const nav = useNavigate();
  const [authed, setAuthed] = useState(!!sessionStorage.getItem("revisa_admin"));
  const [tab, setTab] = useState("users");
  const [users, setUsers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const fetchAll = useCallback(async () => {
    setLoading(true);
    try {
      // Debug: log do token
      const token = localStorage.getItem("revisa_token");
      console.log("🔐 Token armazenado:", token ? "✓ Sim" : "✗ Não");
      
      // Agora usa api (axios) com token JWT armazenado em localStorage
      const [usersRes, subsRes] = await Promise.allSettled([
        api.get("/admin/users"),
        api.get("/subjects"),
      ]);

      // Log dos resultados
      console.log("📊 Admin Users Response:", usersRes.status, usersRes.reason?.response?.status);
      console.log("📚 Subjects Response:", subsRes.status);

      if (usersRes.status === "fulfilled" && Array.isArray(usersRes.value.data)) {
        setUsers(usersRes.value.data);
        console.log("✓ Usuários carregados:", usersRes.value.data.length);
      } else {
        console.warn("⚠️ /admin/users falhou:", usersRes.reason?.response?.status, usersRes.reason?.response?.data?.detail);
        // Fallback: leaderboard
        try {
          const { data } = await api.get("/leaderboard");
          if (Array.isArray(data)) {
            setUsers(data);
            console.log("✓ Leaderboard carregado como fallback:", data.length);
          } else {
            setUsers([]);
            console.warn("⚠️ Leaderboard não retornou array");
          }
        } catch (err) {
          setUsers([]);
          console.error("✗ Erro ao carregar leaderboard:", err.response?.status);
          toast.error("Erro ao carregar usuários");
        }
      }

      if (subsRes.status === "fulfilled" && Array.isArray(subsRes.value.data)) {
        setSubjects(subsRes.value.data);
        console.log("✓ Matérias carregadas:", subsRes.value.data.length);
      } else {
        setSubjects([]);
        console.error("✗ Erro ao carregar matérias:", subsRes.reason?.response?.status);
      }
    } catch (err) {
      setUsers([]);
      setSubjects([]);
      toast.error("Erro ao carregar dados. Verifique sua autenticação.");
      console.error("Fetch error:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Sincroniza autenticação com token no localStorage (para recarregamentos de página)
  useEffect(() => {
    const hasToken = !!localStorage.getItem("revisa_token");
    if (hasToken && !authed) {
      setAuthed(true);
      sessionStorage.setItem("revisa_admin", "1");
    }
  }, []);

  useEffect(() => {
    if (authed) fetchAll();
  }, [authed, fetchAll]);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await api.delete(`/admin/users/${deleteTarget.id}`);
      setUsers(prev => prev.filter(u => u.id !== deleteTarget.id));
      toast.success(`Usuário ${deleteTarget.name} removido.`);
    } catch (err) {
      toast.error(err.response?.data?.detail || "Erro ao excluir.");
    } finally {
      setDeleteTarget(null);
    }
  };

  const handleAdminLogout = () => {
    // Limpa tanto o sessionStorage quanto o token JWT do localStorage
    sessionStorage.removeItem("revisa_admin");
    localStorage.removeItem("revisa_token");
    setAuthed(false);
  };

  if (!authed) return <AdminLogin onLogin={() => setAuthed(true)} />;

  return (
    <div className="min-h-screen" style={{ background: "#F8FAFC" }}>
      {/* Header */}
      <header className="sticky top-0 z-30 bg-white border-b-2 border-slate-900">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <button onClick={() => nav("/home")}
              className="p-2 rounded-xl hover:bg-slate-100 transition-colors">
              <ArrowLeft className="w-5 h-5 text-slate-600" strokeWidth={2.5} />
            </button>
            <div>
              <div className="font-display font-extrabold text-xl text-slate-900 leading-none">
                Painel Admin
              </div>
              <div className="text-xs text-slate-500 font-bold">REVISA · Área restrita</div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center gap-2 bg-violet-50 px-3 py-1.5 rounded-full border-2 border-violet-200">
              <ShieldAlert className="w-4 h-4 text-violet-600" strokeWidth={2.5} />
              <span className="text-xs font-extrabold text-violet-700">Admin</span>
            </div>
            <button onClick={handleAdminLogout}
              className="flex items-center gap-1.5 px-3 py-2 rounded-xl bg-slate-100 hover:bg-red-50 hover:text-red-600 transition-colors font-extrabold text-sm text-slate-700">
              <LogOut className="w-4 h-4" strokeWidth={2.5} />
              <span className="hidden sm:inline">Sair</span>
            </button>
          </div>
        </div>

        {/* Tab bar */}
        <div className="max-w-4xl mx-auto px-4 flex gap-1 pb-2 overflow-x-auto">
          {TABS.map(t => (
            <button key={t.id} onClick={() => setTab(t.id)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-2xl font-extrabold text-sm transition-all whitespace-nowrap ${
                tab === t.id
                  ? "bg-violet-500 text-white border-2 border-slate-900"
                  : "bg-white text-slate-600 border-2 border-slate-200 hover:border-slate-400"
              }`}
              data-testid={`admin-tab-${t.id}`}
            >
              <t.icon className="w-4 h-4" strokeWidth={2.5} />
              {t.label}
            </button>
          ))}
        </div>
      </header>

      {/* Content */}
      <main className="max-w-4xl mx-auto px-4 py-6">
        <AnimatePresence mode="wait">
          <motion.div
            key={tab}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.15 }}
          >
            {tab === "users" && (
              <UsersTab
                users={users} loading={loading}
                onRefresh={fetchAll}
                onDeleteUser={setDeleteTarget}
              />
            )}
            {tab === "stats" && <StatsTab users={users} subjects={subjects} />}
            {tab === "subjects" && <SubjectsTab subjects={subjects} />}
            {tab === "questions" && <QuestionsTab subjects={subjects} />}
            {tab === "ranking" && <RankingTab users={users} />}
          </motion.div>
        </AnimatePresence>
      </main>

      {/* Delete modal */}
      <AnimatePresence>
        {deleteTarget && (
          <DeleteModal
            user={deleteTarget}
            onConfirm={handleDelete}
            onCancel={() => setDeleteTarget(null)}
          />
        )}
      </AnimatePresence>
    </div>
  );
}