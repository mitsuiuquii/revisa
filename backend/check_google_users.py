#!/usr/bin/env python3
"""
Script para verificar usuários do Google diretamente no MongoDB
"""
import asyncio
from motor.motor_asyncio import AsyncClient
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://cluster0.mongodb.net/?retryWrites=true&w=majority")

async def check_google_users():
    """Verifica usuários do Google no banco de dados"""
    print("\n" + "="*60)
    print("🔍 Verificando usuários do Google no MongoDB")
    print("="*60)
    
    try:
        # Conectar ao MongoDB
        client = AsyncClient(MONGODB_URL)
        db = client.revisa_db
        
        # Verificar colção de usuários
        count = await db.users.count_documents({})
        print(f"\n✅ Total de usuários no banco: {count}")
        
        # Buscar usuários do Google
        google_users = await db.users.find({"google_linked": True}).to_list(length=100)
        print(f"📱 Usuários com Google linkado: {len(google_users)}")
        
        if google_users:
            print("\nDetalhes dos usuários do Google:")
            for i, user in enumerate(google_users, 1):
                print(f"\n  {i}. {user.get('name')}")
                print(f"     Email: {user.get('email')}")
                print(f"     ID: {user.get('id')}")
                print(f"     Picture: {'✓' if user.get('picture') else '✗'}")
                print(f"     Created: {user.get('created_at')}")
                print(f"     Last Active: {user.get('last_active')}")
        else:
            print("\n⚠️  Nenhum usuário do Google registrado ainda")
            print("\nPróximos passos:")
            print("1. Acesse http://192.168.0.5:3001")
            print("2. Clique em 'Entrar com Google'")
            print("3. Complete o fluxo de login")
            print("4. Um novo usuário deve ser criado com google_linked=True")
        
        # Mostrar últimos usuários criados (independente do método)
        print("\n" + "-"*60)
        print("📋 Últimos 5 usuários criados (qualquer método):")
        recent = await db.users.find().sort("created_at", -1).limit(5).to_list(length=5)
        for i, user in enumerate(recent, 1):
            google_indicator = "📱 Google" if user.get("google_linked") else "📝 Manual"
            print(f"  {i}. {user.get('name')} ({google_indicator})")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Erro ao conectar: {e}")
        print("\nVerifique se a variável MONGODB_URL está configurada corretamente")
        print("Exemplo: mongodb+srv://username:password@cluster.mongodb.net/revisa_db")

if __name__ == "__main__":
    print("\n🔐 Verificador de Usuários Google")
    print("="*60)
    asyncio.run(check_google_users())
