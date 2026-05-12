# 🔐 Guia de Testes - Google Login

## Status Atual
- ✅ Backend preparado com endpoint `/auth/google/session`
- ✅ Frontend melhorado com melhor tratamento de erros
- ✅ Painel admin agora exibe indicador de usuários Google
- 🟡 **FALTA TESTAR**: Fluxo completo de login com Google

## Teste Manual - Passo a Passo

### Pré-requisitos
- Backend rodando em `http://192.168.0.5:8000`
- Frontend rodando em `http://192.168.0.5:3001`
- MongoDB Atlas conectado
- EMERGENT_LLM_KEY configurado em `.env`

### Passos do Teste

#### 1️⃣ Verificar Configurações
```bash
# Verificar se EMERGENT_LLM_KEY está configurado
echo %EMERGENT_LLM_KEY%

# Verificar se backend está rodando
curl http://192.168.0.5:8000/health
# Esperado: status 200
```

#### 2️⃣ Acessar Frontend
1. Abra `http://192.168.0.5:3001` no navegador
2. Você deve ver a página de login com botão "Entrar com Google"
3. Abra o console do navegador (F12) para ver logs de debug

#### 3️⃣ Iniciar Fluxo de Google
1. Clique no botão "Entrar com Google"
2. **Esperado**: Você será redirecionado para `auth.emergentagent.com`
3. Faça login com sua conta Google
4. **Esperado**: Você será redirecionado de volta para a aplicação

#### 4️⃣ Monitorar Logs

**No Console do Navegador (F12)**:
```javascript
// Você deve ver logs como:
🔐 Enviando session_id para backend...
✅ Login bem-sucedido! Bem-vindo: [nome_do_usuario]
```

**No Terminal do Backend**:
```python
# Você deve ver logs como:
📱 Tentativa de login com Google - session_id: xxxxxxxxxx...
🔍 Validando sessão no Emergent...
✅ Login com Google concluído!
```

#### 5️⃣ Verificar Resultado

**No Navegador**:
- Você deve ser redirecionado para `/home`
- Um toast (notificação) deve aparecer: "✅ Login bem-sucedido! Bem-vindo: [seu_nome]"

**No Painel Admin**:
1. Acesse `http://192.168.0.5:3001/admin`
2. Vá para a aba "Usuários"
3. Você deve ver seu novo usuário com:
   - 📱 Ícone "G" no avatar (indicando Google)
   - "📱 Google •" antes do email
   - Status "✓ Conectado com Google" ao expandir

**No MongoDB**:
```javascript
db.users.findOne({email: "seu.email@gmail.com"})
// Deve retornar um documento com:
{
  name: "Seu Nome",
  email: "seu.email@gmail.com",
  google_linked: true,
  picture: "https://...", // URL da foto de perfil
  ...outros campos
}
```

## Possíveis Problemas

### ❌ "Redirecionamento não funcionou"
**Causa**: EMERGENT_LLM_KEY não configurado corretamente
**Solução**:
1. Verifique se `EMERGENT_LLM_KEY` está em `backend/.env`
2. Reinicie o backend: `python server.py`
3. Tente novamente

### ❌ "Erro ao conectar ao backend"
**Causa**: Backend não está rodando ou está em IP diferente
**Solução**:
1. Verifique IP com `ipconfig` (procure por IPv4 da rede local)
2. Atualize `frontend/.env`: `REACT_APP_BACKEND_URL=http://[IP]:8000`
3. Restart frontend: `npm start`

### ❌ "Usuário não aparece no painel admin"
**Causa**: Possível erro no registro do usuário
**Solução**:
1. Abra o console do navegador - veja exatamente qual erro apareceu
2. Verifique os logs do backend
3. Conecte ao MongoDB e verifique a coleção `users`

### ❌ "Foto de perfil não aparece"
**Causa**: Campo `picture` pode não ter sido salvo
**Solução**: Não é crítico, mas verifique no MongoDB se o campo existe

## Verificação Automatizada

```bash
# Verificar usuários do Google registrados
python backend/check_google_users.py
```

Esperado:
- Mostra total de usuários
- Lista usuários com `google_linked: true`
- Exibe últimos 5 usuários criados

## Checklist de Sucesso

- [ ] Consigo fazer login com Google
- [ ] Sou redirecionado para `/home`
- [ ] Vejo mensagem "Login bem-sucedido"
- [ ] Meu usuário aparece no painel admin
- [ ] Meu usuário tem indicador "📱 Google"
- [ ] Ao expandir, vejo "✓ Conectado com Google"
- [ ] No MongoDB, `google_linked: true`
- [ ] Consigo acessar lições e resolver questões

## Próximos Passos após Sucesso

1. ✅ Testar com múltiplas contas Google diferentes
2. ✅ Verificar se XP/Achievements funcionam normalmente
3. ✅ Teste de logout e login novamente
4. ✅ Validar se as lições aparecem corretamente

## Contato para Problemas

Se encontrar algo que não funciona:
1. Capturar screenshot do erro
2. Copiar logs do console (F12) e backend
3. Verificar documento desta data no MongoDB
4. Reportar com contexto completo
