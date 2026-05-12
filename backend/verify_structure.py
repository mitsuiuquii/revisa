"""Script para verificar a estrutura das lições no banco."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

async def verify():
    client = AsyncIOMotorClient(os.environ['MONGO_URL'])
    db = client[os.environ['DB_NAME']]
    
    subjects = await db.subjects.find({}, {"_id": 0}).to_list(None)
    
    print("="*70)
    print("📊 VERIFICAÇÃO DE ESTRUTURA")
    print("="*70)
    
    for subject in subjects:
        print(f"\n📚 {subject['name']}")
        lessons = await db.lessons.find({'subject_id': subject['id']}).sort('order', 1).to_list(None)
        print(f"   {len(lessons)} lições:")
        
        for lesson in lessons[:10]:  # Mostra no máximo 10
            qc = await db.questions.count_documents({'lesson_id': lesson['id']})
            content = lesson.get('content_name', 'N/A')
            level = lesson.get('level', 'N/A')
            title = lesson.get('title', 'N/A')
            print(f"     • {content} - {level} | {title} | {qc} questões")
        
        if len(lessons) > 10:
            print(f"     ... e mais {len(lessons) - 10}")
    
    print("\n" + "="*70)
    client.close()

if __name__ == "__main__":
    asyncio.run(verify())
