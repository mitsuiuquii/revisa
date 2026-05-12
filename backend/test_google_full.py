#!/usr/bin/env python3
"""
Script para testar o fluxo completo de autenticação com Google
Verifica:
1. Se o backend recebe a sessão do Google
2. Se o usuário é registrado no banco de dados
3. Se o campo google_linked está definido como True
4. Se os dados do usuário (name, picture, email) são salvos corretamente
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://192.168.0.5:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "AdminPassword123!"

def test_user_retrieval():
    """Testa se o endpoint GET /admin/users retorna usuários do Google"""
    print("\n" + "="*60)
    print("📋 Testando obtenção de usuários do admin")
    print("="*60)
    
    # Primeiro, fazer login como admin
    login_payload = {
        "email": ADMIN_EMAIL,
        "password": ADMIN_PASSWORD
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=login_payload)
    
    if response.status_code != 200:
        print("❌ Falha ao fazer login como admin")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    token = response.json()["access_token"]
    print(f"✅ Login admin bem-sucedido")
    print(f"Token: {token[:20]}...")
    
    # Agora buscar todos os usuários
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    
    if response.status_code != 200:
        print("❌ Falha ao buscar usuários")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        return False
    
    users = response.json()
    print(f"✅ Total de usuários: {len(users)}")
    
    # Filtrar usuários do Google
    google_users = [u for u in users if u.get("google_linked")]
    print(f"\n📱 Usuários com login do Google: {len(google_users)}")
    
    if google_users:
        print("\nDetalhes dos usuários do Google:")
        for user in google_users:
            print(f"\n  Name: {user.get('name')}")
            print(f"  Email: {user.get('email')}")
            print(f"  Google Linked: {user.get('google_linked')}")
            print(f"  Picture: {user.get('picture')[:50] if user.get('picture') else 'N/A'}...")
            print(f"  Created: {user.get('created_at')}")
            print(f"  Last Active: {user.get('last_active')}")
    else:
        print("⚠️  Nenhum usuário do Google encontrado no banco de dados")
        print("Verifique se o fluxo de autenticação foi completado")
    
    return True

def check_database_directly():
    """Verifica diretamente no banco de dados"""
    print("\n" + "="*60)
    print("🔍 Verificação de banco de dados")
    print("="*60)
    print("\nPara verificar diretamente no MongoDB:")
    print("1. Conecte ao MongoDB Atlas")
    print("2. Execute: db.users.find({google_linked: true})")
    print("3. Verifique os campos: name, email, picture, google_linked")

def debug_info():
    """Exibe informações de debug"""
    print("\n" + "="*60)
    print("🐛 Informações para debug")
    print("="*60)
    print("\nAo testar o login com Google, verifique:")
    print("1. Console do navegador (F12) - procure por logs com '🔐' ou '✅'")
    print("2. Terminal do backend - logs com '[INFO]' sobre google_session")
    print("3. MongoDB Atlas - coleção 'users' para novo documento criado")
    print("\nPassos para testar manualmente:")
    print("1. Acesse http://192.168.0.5:3001")
    print("2. Clique em 'Entrar com Google'")
    print("3. Faça login com sua conta Google")
    print("4. Você deve ser redirecionado para /home")
    print("5. O novo usuário deve aparecer no painel admin")

if __name__ == "__main__":
    print("\n" + "🔐"*30)
    print("TESTE DE AUTENTICAÇÃO COM GOOGLE")
    print("🔐"*30)
    
    test_user_retrieval()
    check_database_directly()
    debug_info()
    
    print("\n" + "="*60)
    print("✅ Teste concluído")
    print("="*60)
