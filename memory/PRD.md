# REVISA — Product Requirements Document

## Original Problem
Aplicativo educacional inspirado no Duolingo voltado para revisões de vestibular. Público: adolescentes 12-18 anos. Logo "REVISA" (navy + violet + rainbow bar). Cumprir a promessa de revisão com questões interativas e descontraídas.

## User Personas
- **Estudante de Ensino Médio (12-18 anos)** preparando vestibular (ENEM/FUVEST). Quer revisar de forma rápida, gamificada, no celular, em sessões curtas (5-10 min).

## User Choices (via ask_human)
- Matérias: todas as principais
- Questões: banco fixo + IA (Emergent LLM, claude-sonnet-4-5)
- Auth: e-mail/senha JWT (Google Auth deferido)
- Mecânicas: completas (vidas, XP, streak, conquistas)

## Architecture
- **Backend**: FastAPI + Motor + MongoDB. JWT auth (bcrypt). emergentintegrations for AI questions.
- **Frontend**: React 19 + React Router 7 + Tailwind + Framer Motion + canvas-confetti. Mobile-first (max-w-md).
- **Design**: Bricolage Grotesque (titulares) + Nunito (corpo); cards tácteis com border-2 e shadow offset; cores da marca (navy, violeta, laranja, amarelo, verde, vermelho).

## Implemented Features (Feb 2026)
- Auth (email/senha): /register, /login, JWT 30-dias, /api/auth/me
- 10 matérias seedadas com lições e ~50 questões pré-cadastradas
- Trilha de aprendizado estilo Duolingo (zig-zag, nós bloqueados/desbloqueados)
- Lição interativa: 5 questões, feedback instantâneo (verde/vermelho), explicações, confetti
- Sistema de XP + Ofensiva (streak diário, reset >1 dia) + Vidas (5 max, perdidas em erros, refill manual)
- 8 conquistas (lições, XP, ofensiva, perfeição) com desbloqueio automático
- Ranking (top 50 por XP)
- Perfil com estatísticas + logout
- Modo "Pratique com IA" (gera questões via Claude Sonnet 4.5 com EMERGENT_LLM_KEY)
- Toaster (sonner), animações Framer Motion, confetti em acertos
- Layout mobile-first com bottom nav fixo (Trilhas, IA, Conquistas, Ranking, Perfil)

## Backlog (P1)
- Login social Google (Emergent Managed Auth)
- Refill automático de vidas com timer (1 vida a cada 30min)
- Mais lições por matéria (apenas Matemática tem 3, Português 2, demais 1)
- Histórico de lições no perfil
- Compartilhar conquistas / convidar amigos
- Modo "tira-dúvidas" via IA
- Notificações push de ofensiva

## Backlog (P2)
- Editor de admin para criar matérias/lições
- Duelos entre usuários
- Loja de cosméticos com XP/gemas
- Modo offline / PWA
- Relatórios de desempenho por matéria

## Test Credentials
- email: teste@revisa.com / senha: teste123
