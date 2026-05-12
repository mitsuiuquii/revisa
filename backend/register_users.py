"""Script para registrar usuários em massa no banco de dados com dados realistas."""
import asyncio
import bcrypt
import uuid
import random
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Nomes brasileiros realistas
FIRST_NAMES = [
    "Alice", "Bruno", "Carla", "Diego", "Emília", "Felipe", "Gabriela", "Henrique",
    "Isabela", "João", "Karina", "Lucas", "Mariana", "Nicolas", "Olivia", "Paulo",
    "Quentin", "Rafaela", "Sofia", "Tomás", "Ursula", "Víctor", "Vanessa", "Wagner",
    "Xavier", "Yasmin", "Zé", "Ana", "Beatriz", "Carlos",
]

LAST_NAMES = [
    "Silva", "Santos", "Oliveira", "Costa", "Lima", "Pereira", "Gomes", "Martins",
    "Sousa", "Alves", "Fernandes", "Nunes", "Barbosa", "Machado", "Rocha", "Ribeiro",
    "Monteiro", "Carvalho", "Teixeira", "Ferreira", "Pinto", "Andrade", "Mendes", "Castro",
]

COLORS = [
    "#8B5CF6",  # Purple
    "#EC4899",  # Pink
    "#EF4444",  # Red
    "#F97316",  # Orange
    "#EAB308",  # Yellow
    "#22C55E",  # Green
    "#06B6D4",  # Cyan
    "#3B82F6",  # Blue
]

# Patentes disponíveis
RANKS = [
    {"id": "bronze", "name": "Bronze", "color": "#A16207", "icon": "Medal"},
    {"id": "prata", "name": "Prata", "color": "#94A3B8", "icon": "Award"},
    {"id": "ouro", "name": "Ouro", "color": "#EAB308", "icon": "Trophy"},
    {"id": "platina", "name": "Platina", "color": "#22D3EE", "icon": "Gem"},
    {"id": "diamante", "name": "Diamante", "color": "#60A5FA", "icon": "Diamond"},
    {"id": "sabio", "name": "Sábio", "color": "#A855F7", "icon": "Crown"},
]

def rank_for_xp(xp: int):
    """Retorna a patente baseada no XP."""
    for rank in reversed(RANKS):
        min_xp = {"bronze": 0, "prata": 200, "ouro": 600, "platina": 1500, "diamante": 3500, "sabio": 7000}.get(rank["id"], 0)
        if xp >= min_xp:
            return rank
    return RANKS[0]

async def generate_random_user(index: int):
    """Gera um usuário com dados realistas."""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    name = f"{first_name} {last_name}"
    email = f"user{index}@revisa.com.br"
    password = "senha123"
    
    # XP aleatório entre 0 e 8000
    xp = random.randint(0, 8000)
    rank = rank_for_xp(xp)
    avatar_color = random.choice(COLORS)
    
    # Hash da senha
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt).decode()
    
    # Histórico de lições completadas (aleatório)
    lessons = await db.lessons.find({}, {"_id": 0}).to_list(None)
    lessons_completed = [
        {
            "lesson_id": lesson["id"],
            "completed_at": "2026-05-07",
            "score": random.randint(60, 100),
        }
        for lesson in random.sample(lessons, min(random.randint(3, 10), len(lessons)))
    ]
    
    user_doc = {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "password_hash": hashed,
        "avatar_color": avatar_color,
        "xp": xp,
        "rank": rank,
        "lessons_completed": lessons_completed,
        "achievements": [],
        "created_at": "2026-05-07",
        "last_active": "2026-05-07",
    }
    
    return user_doc, name, email

async def register_users_bulk(quantity: int = 20):
    """Registra múltiplos usuários em massa."""
    print(f"🚀 Registrando {quantity} usuários em massa...\n")
    
    registered = 0
    skipped = 0
    
    for i in range(1, quantity + 1):
        user_doc, name, email = await generate_random_user(i)
        
        # Verifica se usuário já existe
        existing = await db.users.find_one({"email": email})
        if existing:
            skipped += 1
            continue
        
        await db.users.insert_one(user_doc)
        print(f"✅ [{i:2d}] {name:30s} - {email:25s} (XP: {user_doc['xp']:5d}, {user_doc['rank']['name']})")
        registered += 1
    
    print(f"\n✅ {registered} usuários registrados | ⏭️  {skipped} pulados")


async def list_users():
    """Lista todos os usuários registrados."""
    print("\n📋 Usuários no banco de dados:")
    print("-" * 60)
    async for user in db.users.find({}, {"_id": 0, "password_hash": 0}):
        print(f"  • {user['name']} - {user['email']} (XP: {user.get('xp', 0)})")
    print("-" * 60)

async def main():
    import sys
    
    # Aceita quantidade de usuários como argumento
    quantity = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    
    await register_users_bulk(quantity)
    await list_users()
    client.close()

if __name__ == "__main__":
    asyncio.run(main())
