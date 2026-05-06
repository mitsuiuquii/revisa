# REVISA — Product Requirements Document

## Original Problem
App educacional gamificado estilo Duolingo voltado a revisões de vestibular (ENEM/FUVEST). Público: 12-18 anos. Foco: questões interativas e descontraídas com revisões programadas.

## Architecture
- **Backend**: FastAPI + Motor + MongoDB; JWT (bcrypt); seed_data.py separado para banco de questões.
- **Frontend**: React 19 + Tailwind + Framer Motion; mobile-first (max-w-md). Bricolage Grotesque + Nunito.
- **AI**: Emergent LLM Key + Claude Sonnet 4.5 via emergentintegrations.

## Iterações Implementadas

### Iteração 1 — MVP
Auth, 10 matérias, lições, vidas/XP/streak, conquistas, ranking, perfil, IA básica.

### Iteração 2 — Gamificação Completa
9 matérias com cores corretas; 5 níveis de patente (Bronze→Sábio); XP por dificuldade; moedas; 3 powers (Universitários/Pular/Plateia, 15 moedas, 1/lição); tutorial onboarding; rank-up banner.

### Iteração 3 — Conteúdo Real + Refresh ✅
- **5 níveis por matéria**: Fundamental, Médio Inicial, Médio Avançado, ENEM, FUVEST/USP
- **45 trilhas + ~290 questões reais** (ENEM, FUVEST, UFMG, UNICAMP, UERJ, UFPR, UFRJ, USP) com fonte/ano em badge
- **Tutorial**: passo 6 renomeado para "Habilidades especiais" (sem "Show do Milhão")
- **AI Practice**: campo "conteúdo" obrigatório (matéria + tópico → questão personalizada)
- **15 moedas iniciais** (era 10) ao registrar
- **Conquista "Sábio Lendário"** (threshold rank=5)
- **Design refresh**: fundo gradiente radial colorido (violeta/laranja/verde/rosa, suave), cards de matéria com gradient sutil + sombra colorida no ícone, mantendo identidade neo-brutalist
- **Bug fixes prévios**: hardcoded test password → env, `is`→`==`, `random`→`secrets`, index keys → IDs

## Backlog
### P1
- Login social Google
- Mais questões por trilha (atualmente ~6 por nível)
- Refill automático de vidas com timer
- Persistir power_used no backend (anti-reload)
- Esconder correct_index do GET /api/lessons/{id}

### P2
- Modo Duelo entre amigos
- Histórico/estatísticas por matéria
- Notificações push de ofensiva
- PWA / modo offline
- Sons de acerto/erro/level-up

## Test Credentials
- email: teste@revisa.com / senha: teste123
