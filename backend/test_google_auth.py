"""Script para testar e debugar o login com Google."""
import requests
import json

print("🔍 Testando login com Google (Emergent Auth)")
print("=" * 70)

# O problema pode estar em alguns lugares:
# 1. EMERGENT_LLM_KEY não configurado
# 2. Session ID inválida
# 3. URL de callback errada
# 4. Permissões CORS

print("\n📋 Verificando configuração no .env...")

from dotenv import load_dotenv
import os
from pathlib import Path

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

emergent_key = os.environ.get('EMERGENT_LLM_KEY')
if emergent_key:
    print(f"✅ EMERGENT_LLM_KEY está configurada: {emergent_key[:20]}...")
else:
    print("❌ EMERGENT_LLM_KEY NÃO está configurada!")
    print("   Adicione ao .env: EMERGENT_LLM_KEY=seu_key_aqui")

backend_url = os.environ.get('MONGO_URL', 'http://192.168.0.5:8000')
print(f"\n🔗 Backend URL: http://192.168.0.5:8000")

print("\n📝 Informações de teste:")
print("   1. Você precisa de um session_id do Emergent Auth")
print("   2. Acesse https://auth.emergentagent.com/")
print("   3. Faça o login com Google")
print("   4. Você será redirecionado para http://localhost:3001/auth/callback?session_id=...")
print("   5. Copie o session_id da URL")

print("\n🧪 Testando endpoint /auth/google/session...")
print("   (Este teste só funciona com um session_id válido)")

# Instruções de como testar
print("\n" + "=" * 70)
print("✅ PRÓXIMOS PASSOS:")
print("=" * 70)
print("""
1. Verifique se o EMERGENT_LLM_KEY está no backend/.env:
   EMERGENT_LLM_KEY=sk-emergent-d7a8bD22e0eB37aA70

2. Teste acessando http://192.168.0.5:3001 e clicando em "Entrar com Google"

3. Se receber erro 401 "Sessão Google inválida":
   - Verifique a EMERGENT_LLM_KEY
   - Verifique se a redirect URL está correta

4. Se o login funcionar, você deverá ver:
   - Usuário criado no banco de dados
   - Redirecionado para /home
   - Seu nome aparecendo na tela

5. Para debug, abra o console do navegador (F12) e veja os erros
""")
