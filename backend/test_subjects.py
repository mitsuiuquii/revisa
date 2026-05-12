"""Script para testar a API e debug das matérias."""
import asyncio
import json
from urllib.request import urlopen
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

async def test_database():
    """Testa os dados no banco de dados."""
    print("\n" + "="*70)
    print("🗄️  VERIFICANDO BANCO DE DADOS")
    print("="*70)
    
    subjects_count = await db.subjects.count_documents({})
    lessons_count = await db.lessons.count_documents({})
    questions_count = await db.questions.count_documents({})
    
    print(f"  📚 Matérias no banco:   {subjects_count}")
    print(f"  📖 Lições no banco:     {lessons_count}")
    print(f"  ❓ Questões no banco:   {questions_count}")
    
    if subjects_count > 0:
        print("\n  📋 Primeiras matérias:")
        async for subject in db.subjects.find({}, {"_id": 0}).limit(5):
            print(f"    • {subject.get('name')} (ID: {subject.get('id')[:8]}...)")
    
    return subjects_count

def test_api():
    """Testa a API do backend."""
    print("\n" + "="*70)
    print("🌐 TESTANDO API")
    print("="*70)
    
    backend_url = "http://localhost:8000"
    
    try:
        # Testa /subjects
        response = urlopen(f"{backend_url}/api/subjects", timeout=5)
        print(f"\n  GET /api/subjects")
        print(f"  Status Code: {response.status}")
        
        if response.status == 200:
            data = json.loads(response.read().decode())
            subjects = data if isinstance(data, list) else []
            print(f"  ✅ Retornou {len(subjects)} matérias")
            if subjects:
                print(f"\n  Primeiras matérias da API:")
                for subject in subjects[:3]:
                    print(f"    • {subject.get('name')} - {subject.get('description', 'sem descrição')}")
            return True
        else:
            print(f"  ❌ Erro: Status {response.status}")
            return False
    
    except Exception as e:
        print(f"\n  ❌ Erro: {e}")
        print(f"     Verifique se o backend está rodando em {backend_url}")
        return False

async def main():
    print("\n🔍 DEBUG - Verificando Matérias\n")
    
    # Testa banco de dados
    db_count = await test_database()
    
    # Testa API
    api_ok = test_api()
    
    print("\n" + "="*70)
    print("📊 RESUMO")
    print("="*70)
    
    if db_count > 0 and api_ok:
        print("✅ Tudo OK! Matérias estão no banco e na API")
        print("\n⚠️  Se o admin não está mostrando:")
        print("  1. Limpe o cache do navegador (Ctrl+Shift+Delete ou Cmd+Shift+Delete)")
        print("  2. Reinicie o frontend: npm start")
        print("  3. Acesse novamente: http://localhost:3000/admin")
    elif db_count > 0 and not api_ok:
        print("⚠️  Matérias estão no banco, mas API não está respondendo")
        print("  Verifique se o backend está rodando na porta 8000")
    else:
        print("❌ Nenhuma matéria encontrada no banco!")
        print("  Execute: python force_seed.py")
    
    print("="*70 + "\n")
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
