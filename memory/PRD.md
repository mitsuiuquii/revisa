# REVISA — Product Requirements Document

## Original Problem
App educacional gamificado estilo Duolingo voltado a revisões de vestibular (ENEM/FUVEST). Público: 12-18 anos. Logo: navy + violet + barra arco-íris. Foco: questões interativas e descontraídas com revisões programadas.

## User Personas
- Estudantes 12-18 anos preparando vestibular. Querem revisar de forma rápida e gamificada no celular, em sessões curtas, com sensação de progresso.

## User Choices Confirmadas
- 9 matérias (Mat, Bio, Geo, His, Port, Quim, Fis, Lit, Ing) — Redação removida
- Banco de questões pré-cadastrado + IA (Emergent LLM, Claude Sonnet 4.5)
- Login email/senha JWT (Google deferido)
- Mecânicas Duolingo completas + patentes + moedas + powers Show do Milhão
- Trilhas básico → pré-vestibular com bloqueio por patente

## Architecture
- **Backend**: FastAPI + Motor + MongoDB; JWT auth (bcrypt); emergentintegrations p/ AI
- **Frontend**: React 19 + React Router 7 + Tailwind + Framer Motion + canvas-confetti; mobile-first (max-w-md)
- **Design**: Bricolage Grotesque + Nunito; cards tácteis com sombra offset; cores da marca

## Implemented (Feb 2026)
### Iteração 1 (MVP)
- Auth e-mail/senha + JWT 30 dias
- 10 matérias inicial + lições + ~50 questões + 8 conquistas
- Trilha Duolingo zig-zag, vidas/XP/streak
- Loja de IA (Pratique com IA)
- Ranking, conquistas, perfil, logout

### Iteração 2 (Gamificação Completa) ✅
- **9 matérias com cores corretas**: Mat #3B82F6, Bio #86EFAC, Geo #A855F7, His #EF4444, Port #F97316, Quim #84CC16, Fis #1E40AF, Lit #EC4899, Ing #FACC15
- **4 níveis de trilha por matéria**: Básico (6º-9º), Intermediário, Avançado, Pré-Vestibular — total 36 trilhas + 144+ questões marcadas com dificuldade
- **6 patentes**: Bronze (0) → Prata (200) → Ouro (600) → Platina (1500) → Diamante (3500) → Sábio (7000) — desbloqueiam níveis (basico=Bronze, intermed=Prata, avancado=Ouro, pre_vest=Platina)
- **XP variável**: 5/10/15 por dificuldade + bônus por % acerto (5/10/20)
- **Sistema de moedas**: 1/acerto + 3 bônus se gabaritar; novos users começam com 10 moedas
- **3 habilidades estilo Show do Milhão (15 moedas, 1 por lição)**:
  - Universitários (50/50)
  - Pular questão
  - Plateia (estatística com viés à correta)
- **Tutorial onboarding** (7 passos) automático no primeiro acesso, reabrir via "Como funciona?" / ícone help
- **TopBar enriquecido**: rank badge, moedas, XP, vidas, streak, help
- **Profile com ladder de patentes**
- **Rank-up banner** ao subir de patente

## Backlog
### P1
- Login social Google (Emergent Managed Auth)
- Mais questões por nível (atualmente ~4)
- Refill automático de vidas com timer
- Persistir power_used no backend para evitar reload-trick
- Esconder correct_index do GET /api/lessons/{id} (validação só server-side)
- Sons (acerto/erro/level-up)

### P2
- Modo "tira-dúvidas" via IA (chat com explicação detalhada)
- Duelos entre amigos (multiplayer simples)
- Histórico/estatísticas por matéria
- Notificações push de ofensiva
- PWA / modo offline

## Test Credentials
- email: teste@revisa.com / senha: teste123
