"""Script para forçar o seed das matérias, lições e questões."""
import asyncio
import uuid
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
from seed_data import SUBJECTS_SEED, QUESTION_BANK, ACHIEVEMENTS_SEED, LEVELS as LEVEL_LABELS

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Mapeamento de nomes de nível
LEVEL_LABELS_MAP = {
    "basico": "Fundamental",
    "intermediario": "Médio Inicial",
    "avancado": "Médio Avançado",
    "enem": "ENEM",
    "fuvest": "FUVEST/USP",
}

async def force_seed():
    """Força o seed das matérias, lições e questões."""
    print("🚀 INICIANDO SEED FORÇADO...\n")
    
    # Limpa os dados antigos
    print("🗑️  Limpando dados antigos...")
    await db.subjects.delete_many({})
    await db.lessons.delete_many({})
    await db.questions.delete_many({})
    await db.achievements.delete_many({})
    print("✅ Dados antigos removidos\n")
    
    # Insere as matérias
    print("📚 Criando matérias...")
    for i, sub in enumerate(SUBJECTS_SEED):
        sub_id = str(uuid.uuid4())
        subject_doc = {"id": sub_id, "order": i, **sub}
        await db.subjects.insert_one(subject_doc)
        print(f"  ✅ {sub['name']}")
        
        # Insere lições para cada nível
        levels_for_sub = QUESTION_BANK.get(sub["name"], {})
        for j, level in enumerate(["basico", "intermediario", "avancado", "enem", "fuvest"]):
            qs = levels_for_sub.get(level, [])
            if not qs:
                continue
            
            lesson_id = str(uuid.uuid4())
            lesson_doc = {
                "id": lesson_id,
                "subject_id": sub_id,
                "subject_name": sub["name"],
                "title": f"{sub['name']} — {LEVEL_LABELS_MAP[level]}",
                "level": level,
                "order": j,
            }
            await db.lessons.insert_one(lesson_doc)
            
            # Insere questões para a lição
            for k, q in enumerate(qs):
                question_doc = {
                    "id": str(uuid.uuid4()),
                    "lesson_id": lesson_id,
                    "order": k,
                    **q,
                }
                await db.questions.insert_one(question_doc)
    
    print(f"\n✅ {len(SUBJECTS_SEED)} matérias criadas com lições e questões\n")
    
    # Insere as conquistas
    print("🏆 Criando conquistas...")
    for ach in ACHIEVEMENTS_SEED:
        await db.achievements.insert_one({"id": str(uuid.uuid4()), **ach})
    print(f"✅ {len(ACHIEVEMENTS_SEED)} conquistas criadas\n")
    
    # Estatísticas
    subjects_count = await db.subjects.count_documents({})
    lessons_count = await db.lessons.count_documents({})
    questions_count = await db.questions.count_documents({})
    achievements_count = await db.achievements.count_documents({})
    
    print("="*70)
    print("📊 ESTATÍSTICAS DO SEED:")
    print("="*70)
    print(f"  📚 Matérias:      {subjects_count}")
    print(f"  📖 Lições:        {lessons_count}")
    print(f"  ❓ Questões:      {questions_count}")
    print(f"  🏆 Conquistas:    {achievements_count}")
    print("="*70)
    print("\n✨ Seed concluído com sucesso!")
    print("\n🔄 Próximas ações:")
    print("  1. Acesse o painel admin: http://localhost:3000/admin")
    print("  2. Login: senha = revisa@admin2025")
    print("  3. Você deve ver todas as matérias na aba 'Matérias'")

async def main():
    try:
        await force_seed()
    except Exception as e:
        print(f"\n❌ Erro ao fazer seed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())
