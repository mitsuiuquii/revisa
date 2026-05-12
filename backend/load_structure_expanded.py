"""Script para carregar a estrutura expandida com conteúdo + dificuldade para TODAS as matérias."""
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

# Definição expandida de CONTEÚDOS por matéria
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

async def generate_lesson_title(content: str, level: str, subject: str) -> tuple:
    """Gera um título e descrição para a lição."""
    diff_label = DIFFICULTY_LABELS.get(level, level)
    title = f"{content} — {diff_label}"
    description = f"{diff_label} em {content}"
    return title, description

async def load_expanded_structure():
    """Carrega a nova estrutura expandida com conteúdo + dificuldade."""
    print("🚀 CARREGANDO ESTRUTURA EXPANDIDA (Conteúdo + Dificuldade para TODAS as matérias)\n")
    
    # Limpa os dados antigos
    print("🗑️  Limpando dados antigos...")
    await db.subjects.delete_many({})
    await db.lessons.delete_many({})
    await db.questions.delete_many({})
    print("✅ Dados antigos removidos\n")
    
    total_subjects = 0
    total_lessons = 0
    total_questions = 0
    
    # Cores por dificuldade
    difficulty_colors = {
        "basico": "#22C55E",
        "intermediario": "#F59E0B",
        "avancado": "#EF4444",
        "enem": "#8B5CF6",
        "fuvest": "#EC4899",
    }
    
    # Carrega subjects do banco (que já existem)
    subjects = await db.subjects.find({}, {"_id": 0}).to_list(None)
    
    if not subjects:
        print("❌ Nenhuma matéria encontrada no banco!")
        return
    
    for subject in subjects:
        subject_name = subject.get("name")
        subject_id = subject.get("id")
        contents = SUBJECTS_WITH_CONTENTS.get(subject_name, [f"{subject_name} Geral"])
        
        print(f"📚 {subject_name}")
        
        total_subjects += 1
        
        # Para cada CONTEÚDO da matéria
        lesson_order = 0
        for content_name in contents:
            
            # Para cada DIFICULDADE deste conteúdo
            for level in LEVELS:
                # Gera título e descrição
                title, description = await generate_lesson_title(content_name, level, subject_name)
                
                # Cria a lição
                lesson_id = str(uuid.uuid4())
                difficulty_label = DIFFICULTY_LABELS[level]
                
                lesson_doc = {
                    "id": lesson_id,
                    "subject_id": subject_id,
                    "subject_name": subject_name,
                    "content_name": content_name,  # Nome do conteúdo/tema
                    "title": title,
                    "description": description,
                    "level": level,
                    "difficulty_color": difficulty_colors[level],
                    "order": lesson_order,
                }
                await db.lessons.insert_one(lesson_doc)
                lesson_order += 1
                total_lessons += 1
                
                # Cria 3 questões de placeholder para a lição
                for q_idx in range(3):
                    question_doc = {
                        "id": str(uuid.uuid4()),
                        "lesson_id": lesson_id,
                        "content_name": content_name,
                        "level": level,
                        "difficulty": level,
                        "order": q_idx,
                        "prompt": f"Questão {q_idx + 1} - {content_name} ({difficulty_label})",
                        "options": [
                            f"Opção A - {content_name} {q_idx + 1}",
                            f"Opção B - {content_name} {q_idx + 1}",
                            f"Opção C - {content_name} {q_idx + 1}",
                            f"Opção D - {content_name} {q_idx + 1}",
                        ],
                        "correct_index": q_idx % 4,
                        "explanation": f"Explicação para a questão {q_idx + 1} de {content_name}",
                        "source": f"SEED v2 - {subject_name}",
                    }
                    await db.questions.insert_one(question_doc)
                    total_questions += 1
                
                print(f"  ├─ {content_name} — {difficulty_label} (3 questões)")
        
        print()
    
    # Estatísticas
    print("="*70)
    print("📊 NOVA ESTRUTURA CARREGADA:")
    print("="*70)
    print(f"  📚 Matérias:      {total_subjects}")
    print(f"  📖 Lições:        {total_lessons}")
    print(f"  ❓ Questões:      {total_questions}")
    print("="*70)
    print("\n✨ Estrutura: Matéria → Conteúdo (Tema) → Lição com Dificuldade")
    print("   Exemplo: Matemática → Aritmética Básica → Lição 'Aritmética Básica - Médio'")
    print("\n🔄 Próximas ações:")
    print("  1. Verifique o admin: http://localhost:3000/admin")
    print("  2. Vá para aba 'Matérias' e expanda uma matéria")
    print("  3. Verá lições organizadas por Conteúdo + Dificuldade!")

async def main():
    try:
        await load_expanded_structure()
    except Exception as e:
        print(f"\n❌ Erro ao carregar: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
