"""Script para carregar o novo seed reorganizado por conteúdo + dificuldade."""
import asyncio
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
from seed_data_v2 import SUBJECTS_SEED, CONTENT_BANK, ACHIEVEMENTS_SEED

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Mapeamento de nomes de nível para etiquetas
LEVEL_LABELS_MAP = {
    "basico": "Básico",
    "intermediario": "Médio",
    "avancado": "Avançado",
}

DIFFICULTY_COLORS = {
    "basico": "#22C55E",      # Verde
    "intermediario": "#F59E0B", # Amarelo
    "avancado": "#EF4444",    # Vermelho
}

async def load_new_structure():
    """Carrega a nova estrutura de conteúdo + dificuldade."""
    print("🚀 CARREGANDO NOVA ESTRUTURA (Conteúdo + Dificuldade)\n")
    
    # Limpa os dados antigos
    print("🗑️  Limpando dados antigos...")
    await db.subjects.delete_many({})
    await db.lessons.delete_many({})
    await db.questions.delete_many({})
    await db.achievements.delete_many({})
    print("✅ Dados antigos removidos\n")
    
    total_subjects = 0
    total_lessons = 0
    total_questions = 0
    
    # Itera por cada matéria
    for subject_idx, subject in enumerate(SUBJECTS_SEED):
        subject_id = str(uuid.uuid4())
        subject_doc = {"id": subject_id, "order": subject_idx, **subject}
        await db.subjects.insert_one(subject_doc)
        print(f"📚 {subject['name']}")
        
        total_subjects += 1
        content_bank = CONTENT_BANK.get(subject["name"], {})
        
        # Itera por cada CONTEÚDO (tema) da matéria
        lesson_order = 0
        for content_name, difficulties in sorted(content_bank.items()):
            
            # Para cada DIFICULDADE deste conteúdo
            for difficulty_level in ["basico", "intermediario", "avancado"]:
                questions = difficulties.get(difficulty_level, [])
                
                # Se não há questões neste nível, pula
                if not questions:
                    continue
                
                # Cria a lição (Conteúdo + Dificuldade)
                lesson_id = str(uuid.uuid4())
                difficulty_label = LEVEL_LABELS_MAP[difficulty_level]
                
                lesson_doc = {
                    "id": lesson_id,
                    "subject_id": subject_id,
                    "subject_name": subject["name"],
                    "content_name": content_name,  # Novo: nome do conteúdo/tema
                    "title": f"{content_name} — {difficulty_label}",  # Ex: "Aritmética Básica — Médio"
                    "description": f"{difficulty_label} em {content_name}",
                    "level": difficulty_level,  # Ainda mantém o nível para compatibilidade
                    "difficulty_color": DIFFICULTY_COLORS[difficulty_level],
                    "order": lesson_order,
                }
                await db.lessons.insert_one(lesson_doc)
                lesson_order += 1
                total_lessons += 1
                
                # Insere as questões da lição
                for q_idx, question in enumerate(questions):
                    question_doc = {
                        "id": str(uuid.uuid4()),
                        "lesson_id": lesson_id,
                        "content_name": content_name,
                        "difficulty": difficulty_level,
                        "order": q_idx,
                        **question,
                    }
                    await db.questions.insert_one(question_doc)
                    total_questions += 1
                
                print(f"  ├─ {content_name} — {difficulty_label} ({len(questions)} questões)")
        
        print()
    
    # Carrega achievements
    print("🏆 Criando conquistas...")
    for ach in ACHIEVEMENTS_SEED:
        await db.achievements.insert_one({"id": str(uuid.uuid4()), **ach})
    print(f"✅ {len(ACHIEVEMENTS_SEED)} conquistas criadas\n")
    
    # Estatísticas
    print("="*70)
    print("📊 NOVA ESTRUTURA CARREGADA:")
    print("="*70)
    print(f"  📚 Matérias:      {total_subjects}")
    print(f"  📖 Lições:        {total_lessons}")
    print(f"  ❓ Questões:      {total_questions}")
    print(f"  🏆 Conquistas:    {len(ACHIEVEMENTS_SEED)}")
    print("="*70)
    print("\n✨ Estrutura: Matéria → Conteúdo (Tema) → Lição com Dificuldade")
    print("   Exemplo: Matemática → Aritmética Básica → Lição 'Aritmética Básica - Médio'")
    print("\n🔄 Próximas ações:")
    print("  1. Reinicie o backend: python server.py")
    print("  2. Acesse o admin: http://localhost:3000/admin")
    print("  3. Vá para aba 'Matérias' e expanda uma matéria")
    print("  4. Verá lições organizadas por Conteúdo + Dificuldade!")

async def main():
    try:
        await load_new_structure()
    except Exception as e:
        print(f"\n❌ Erro ao carregar: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
