"""Script completo para carregar Matérias + Conteúdos + Dificuldades."""
import asyncio
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# MATÉRIAS
SUBJECTS_SEED = [
    {"name": "Matemática", "icon": "Calculator", "color": "#3B82F6", "description": "Funções, geometria, álgebra, trigonometria"},
    {"name": "Biologia", "icon": "Leaf", "color": "#86EFAC", "description": "Citologia, genética, ecologia, fisiologia"},
    {"name": "Geografia", "icon": "Globe", "color": "#F87171", "description": "Física, humana e geopolítica"},
    {"name": "História", "icon": "Book", "color": "#FBBF24", "description": "Eras históricase momentos marcantes"},
    {"name": "Português", "icon": "Type", "color": "#A78BFA", "description": "Gramática, literatura, interpretação"},
    {"name": "Química", "icon": "Beaker", "color": "#34D399", "description": "Elementos, reações, soluções"},
    {"name": "Física", "icon": "Lightbulb", "color": "#60A5FA", "description": "Mecânica, energia, ondas, luz"},
    {"name": "Literatura", "icon": "BookMarked", "color": "#F472B6", "description": "Movimentos literários e obras"},
    {"name": "Inglês", "icon": "Globe2", "color": "#FB923C", "description": "Idioma, gramática, conversação"},
]

# CONTEÚDOS por matéria
SUBJECTS_WITH_CONTENTS = {
    "Matemática": ["Aritmética Básica", "Geometria", "Trigonometria", "Álgebra", "Funções"],
    "Biologia": ["Citologia", "Genética", "Ecologia", "Fisiologia", "Evolução"],
    "Geografia": ["Geografia Física", "Geografia Humana", "Geopolítica", "Cartografia", "Climatologia"],
    "História": ["História Antiga", "História Medieval", "História Moderna", "História Contemporânea", "História do Brasil"],
    "Português": ["Gramática", "Literatura", "Produção de Texto", "Interpretação de Texto", "Ortografia"],
    "Química": ["Estrutura Atômica", "Reações Químicas", "Termoquímica", "Eletroquímica", "Cinética"],
    "Física": ["Mecânica", "Termologia", "Óptica", "Eletromagnetismo", "Ondas"],
    "Literatura": ["Prosa", "Poesia", "Teatro", "Modernismo", "Romantismo"],
    "Inglês": ["Vocabulário", "Gramática", "Listening", "Reading", "Writing"],
}

LEVELS = ["basico", "intermediario", "avancado", "enem", "fuvest"]

DIFFICULTY_LABELS = {
    "basico": "Básico",
    "intermediario": "Médio",
    "avancado": "Avançado",
    "enem": "ENEM",
    "fuvest": "FUVEST/USP",
}

# Cores por dificuldade
DIFFICULTY_COLORS = {
    "basico": "#22C55E",
    "intermediario": "#F59E0B",
    "avancado": "#EF4444",
    "enem": "#8B5CF6",
    "fuvest": "#EC4899",
}

async def load_complete_structure():
    """Carrega a estrutura completa: Matérias → Conteúdos → Lições (com Dificuldade)."""
    print("🚀 CARREGANDO ESTRUTURA COMPLETA\n")
    
    # Limpa tudo
    print("🗑️  Limpando dados antigos...")
    await db.subjects.delete_many({})
    await db.lessons.delete_many({})
    await db.questions.delete_many({})
    print("✅ Dados antigos removidos\n")
    
    total_subjects = 0
    total_lessons = 0
    total_questions = 0
    
    # 1. Carrega MATÉRIAS
    for subject_idx, subject in enumerate(SUBJECTS_SEED):
        subject_id = str(uuid.uuid4())
        subject_doc = {"id": subject_id, "order": subject_idx, "total_lessons": 0, **subject}
        await db.subjects.insert_one(subject_doc)
        total_subjects += 1
        
        subject_name = subject['name']
        contents = SUBJECTS_WITH_CONTENTS.get(subject_name, [f"{subject_name} Geral"])
        
        print(f"📚 {subject_name}")
        
        # 2. Para cada CONTEÚDO/TEMA da matéria
        lesson_order = 0
        for content_name in contents:
            
            # 3. Para cada DIFICULDADE do conteúdo
            for level in LEVELS:
                diff_label = DIFFICULTY_LABELS[level]
                title = f"{content_name} — {diff_label}"
                
                # Cria a LIÇÃO
                lesson_id = str(uuid.uuid4())
                lesson_doc = {
                    "id": lesson_id,
                    "subject_id": subject_id,
                    "subject_name": subject_name,
                    "content_name": content_name,
                    "title": title,
                    "description": f"{diff_label} em {content_name}",
                    "level": level,
                    "difficulty_color": DIFFICULTY_COLORS[level],
                    "order": lesson_order,
                }
                await db.lessons.insert_one(lesson_doc)
                lesson_order += 1
                total_lessons += 1
                
                # Cria 3 QUESTÕES por lição
                for q_idx in range(3):
                    question_doc = {
                        "id": str(uuid.uuid4()),
                        "lesson_id": lesson_id,
                        "content_name": content_name,
                        "level": level,
                        "difficulty": level,
                        "order": q_idx,
                        "prompt": f"[{diff_label}] {content_name} - Questão {q_idx + 1}",
                        "options": [
                            f"Alternativa A",
                            f"Alternativa B",
                            f"Alternativa C",
                            f"Alternativa D",
                        ],
                        "correct_index": q_idx % 4,
                        "explanation": f"Resposta correta: Alternativa {chr(65 + (q_idx % 4))}",
                        "source": f"{subject_name} - Seed v3",
                    }
                    await db.questions.insert_one(question_doc)
                    total_questions += 1
                
                print(f"  ├─ {content_name} — {diff_label} (3 Q)")
        
        # Atualiza total_lessons da matéria
        await db.subjects.update_one({"id": subject_id}, {"$set": {"total_lessons": lesson_order}})
        print()
    
    # RESUMO
    print("="*70)
    print("📊 ESTRUTURA CARREGADA COM SUCESSO:")
    print("="*70)
    print(f"  📚 Matérias:      {total_subjects}")
    print(f"  📖 Lições:        {total_lessons}")
    print(f"  ❓ Questões:      {total_questions}")
    print("="*70)
    print(f"\n✨ Estrutura por Matéria:")
    print(f"  • {len(SUBJECTS_SEED)} matérias")
    print(f"  • Média de 5 conteúdos por matéria")
    print(f"  • 5 níveis de dificuldade por conteúdo")
    print(f"  • Total: {total_subjects} × 5 × 5 = {total_lessons} lições")

async def main():
    try:
        await load_complete_structure()
        print("\n✅ Tudo pronto!")
        print("\n📝 PRÓXIMOS PASSOS:")
        print("  1. Limpe o cache do navegador (Ctrl+Shift+Delete)")
        print("  2. Acesse o admin: http://192.168.0.5:3000/admin")
        print("  3. Vá para aba 'Matérias' e expanda uma")
        print("  4. Verá todas as lições com conteúdo + dificuldade!")
    except Exception as e:
        print(f"\n❌ Erro: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
