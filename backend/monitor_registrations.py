"""Script para monitorar novos registros em tempo real."""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
from pathlib import Path
import socket

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

def get_local_ip():
    """Obtém IP local da máquina."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

async def monitor_registrations():
    """Monitora novos registros em tempo real."""
    local_ip = get_local_ip()
    
    print("\n" + "="*70)
    print("📱 LINK DE COMPARTILHAMENTO PARA CADASTRO")
    print("="*70)
    print(f"\n🌐 Link local:  http://localhost:3000/register")
    print(f"🌐 Link rede:   http://{local_ip}:3000/register")
    print(f"\n📋 Compartilhe este link com pessoas para elas se cadastrarem!\n")
    print("="*70)
    print("⏳ Aguardando novos registros... (Ctrl+C para sair)\n")
    
    last_count = await db.users.count_documents({})
    registered_users = []
    
    try:
        while True:
            current_count = await db.users.count_documents({})
            
            if current_count > last_count:
                # Busca usuários novos
                diff = current_count - last_count
                new_users = await db.users.find(
                    {},
                    {"_id": 0, "password_hash": 0}
                ).sort("created_at", -1).to_list(diff)
                
                for user in new_users:
                    if user["email"] not in registered_users:
                        registered_users.append(user["email"])
                        xp = user.get("xp", 0)
                        rank = user.get("rank", {}).get("name", "Bronze")
                        print(f"✨ NOVO REGISTRO: {user['name']:25s} | {user['email']:30s} | XP: {xp:5d}")
                
                last_count = current_count
            
            await asyncio.sleep(2)  # Verifica a cada 2 segundos
    
    except KeyboardInterrupt:
        print("\n\n👋 Monitoramento encerrado!")
        print(f"📊 Total de usuários registrados: {last_count}")
        client.close()

if __name__ == "__main__":
    asyncio.run(monitor_registrations())
