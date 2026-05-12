"""Script para testar os endpoints de admin para questões."""
import requests
import json

try:
    # Faz login como admin
    login_resp = requests.post(
        'http://192.168.0.5:8000/api/admin/login',
        json={'password': 'revisa@admin2025'},
        timeout=5
    )
    
    if login_resp.status_code != 200:
        print(f'Erro ao fazer login: {login_resp.status_code}')
        print(login_resp.text)
        exit(1)
    
    token = login_resp.json()['token']
    headers = {'Authorization': f'Bearer {token}'}
    
    print("✅ Admin login OK")
    print()
    
    # Pega as matérias
    subjects_resp = requests.get('http://192.168.0.5:8000/api/subjects')
    subjects = subjects_resp.json()
    
    if not subjects:
        print("❌ Nenhuma matéria encontrada")
        exit(1)
    
    subject = subjects[0]
    subject_id = subject['id']
    print(f"📚 Matéria selecionada: {subject['name']}")
    
    # Pega as lições
    lessons_resp = requests.get(f'http://192.168.0.5:8000/api/subjects/{subject_id}/lessons')
    lessons = lessons_resp.json()
    
    if not lessons:
        print("❌ Nenhuma lição encontrada")
        exit(1)
    
    lesson = lessons[0]
    lesson_id = lesson['id']
    print(f"📖 Lição selecionada: {lesson.get('title', 'sem título')}")
    print()
    
    # Testa o endpoint de listar questões
    print("🔍 Testando GET /admin/lessons/{lesson_id}/questions...")
    questions_resp = requests.get(
        f'http://192.168.0.5:8000/api/admin/lessons/{lesson_id}/questions',
        headers=headers,
        timeout=5
    )
    
    print(f"   Status: {questions_resp.status_code}")
    
    if questions_resp.status_code != 200:
        print(f"   ❌ Erro: {questions_resp.text}")
        exit(1)
    
    questions = questions_resp.json()
    print(f"   ✅ OK! Retornou {len(questions)} questões")
    
    if questions:
        q = questions[0]
        print(f"\n   Exemplo de questão:")
        print(f"     Pergunta: {q['prompt'][:60]}...")
        print(f"     Opções: {len(q['options'])}")
        print(f"     Resposta correta: {q['correct_index']}")
    
    print("\n✅ TODOS OS TESTES PASSARAM!")
    
except requests.exceptions.ConnectionError:
    print("❌ Erro de conexão. O backend está rodando em http://192.168.0.5:8000?")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
