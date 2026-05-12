from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os, logging, bcrypt, jwt, uuid, secrets
from pathlib import Path
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import datetime, timezone, timedelta, date

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]
JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGORITHM = "HS256"
EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')
ADMIN_SECRET = os.environ.get('ADMIN_SECRET', 'revisa@admin2025')

app = FastAPI(title="REVISA API")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Log inicial de verificação
logger.info(f"🚀 REVISA Backend iniciado")
logger.info(f"🔑 ADMIN_SECRET configurado: {'✓ Sim' if ADMIN_SECRET else '✗ Não'}")
logger.info(f"🔐 JWT_SECRET configurado: {'✓ Sim' if JWT_SECRET else '✗ Não'}")
logger.info(f"📊 DB_NAME: {os.environ.get('DB_NAME')}")

# ============= RANKS =============
RANKS = [
    {"id": "bronze",   "name": "Bronze",   "min_xp": 0,    "color": "#A16207", "icon": "Medal"},
    {"id": "prata",    "name": "Prata",    "min_xp": 200,  "color": "#94A3B8", "icon": "Award"},
    {"id": "ouro",     "name": "Ouro",     "min_xp": 600,  "color": "#EAB308", "icon": "Trophy"},
    {"id": "platina",  "name": "Platina",  "min_xp": 1500, "color": "#22D3EE", "icon": "Gem"},
    {"id": "diamante", "name": "Diamante", "min_xp": 3500, "color": "#60A5FA", "icon": "Diamond"},
    {"id": "sabio",    "name": "Sábio",    "min_xp": 7000, "color": "#A855F7", "icon": "Crown"},
]
LEVEL_RANK_REQUIRED = {"basico": "bronze", "intermediario": "prata", "avancado": "ouro", "enem": "platina", "fuvest": "diamante"}
LEVEL_LABELS = {"basico": "Fundamental", "intermediario": "Médio Inicial", "avancado": "Médio Avançado", "enem": "ENEM", "fuvest": "FUVEST/USP"}
DIFFICULTY_XP = {"facil": 5, "medio": 10, "dificil": 15}
POWER_COST = 15
POWERS = [
    {"id": "fifty_fifty", "name": "Universitários", "description": "Elimina 2 alternativas erradas", "icon": "Users", "color": "#3B82F6"},
    {"id": "skip",        "name": "Pular questão",  "description": "Pula sem penalizar XP",          "icon": "SkipForward", "color": "#F97316"},
    {"id": "audience",    "name": "Plateia",        "description": "Mostra estatística da plateia",  "icon": "BarChart3",   "color": "#22C55E"},
]

def rank_for_xp(xp: int):
    chosen = RANKS[0]
    for r in RANKS:
        if xp >= r["min_xp"]:
            chosen = r
    return chosen

def rank_index(rank_id: str) -> int:
    for i, r in enumerate(RANKS):
        if r["id"] == rank_id: return i
    return 0

def level_unlocked(level: str, user_rank_id: str) -> bool:
    needed = LEVEL_RANK_REQUIRED.get(level, "bronze")
    return rank_index(user_rank_id) >= rank_index(needed)


# ============= MODELS =============
class UserRegister(BaseModel):
    name: str; email: EmailStr; password: str
class UserLogin(BaseModel):
    email: EmailStr; password: str
class QuestionAnswer(BaseModel):
    question_id: str; selected_index: int
class CompleteLessonRequest(BaseModel):
    lesson_id: str; answers: List[QuestionAnswer]; power_used: Optional[str] = None
class AIQuestionRequest(BaseModel):
    subject: str; topic: str; difficulty: str = "medio"
class UsePowerRequest(BaseModel):
    power_id: str

# Admin models
class AdminCreateQuestion(BaseModel):
    lesson_id: str
    prompt: str
    options: List[str]
    correct_index: int
    explanation: str
    source: Optional[str] = None

class AdminUpdateQuestion(BaseModel):
    prompt: Optional[str] = None
    options: Optional[List[str]] = None
    correct_index: Optional[int] = None
    explanation: Optional[str] = None
    source: Optional[str] = None

# ============= HELPERS =============
def hash_password(p): return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
def verify_password(p, h): return bcrypt.checkpw(p.encode(), h.encode())
def create_token(uid):
    return jwt.encode({"sub": uid, "exp": datetime.now(timezone.utc) + timedelta(days=30)}, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    try:
        uid = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM]).get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = await db.users.find_one({"id": uid}, {"_id": 0, "password_hash": 0})
    if not user: raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

def public_user(u: dict) -> dict:
    rank = rank_for_xp(u.get("xp", 0))
    return {
        "id": u["id"], "name": u["name"], "email": u["email"],
        "xp": u.get("xp", 0), "lives": u.get("lives", 5), "streak": u.get("streak", 0),
        "coins": u.get("coins", 0), "rank": rank,
        "last_active": u.get("last_active"),
        "completed_lessons": u.get("completed_lessons", []),
        "achievements": u.get("achievements", []),
        "avatar_color": u.get("avatar_color", "#8B5CF6"),
    }


# ============= AUTH =============
@api_router.post("/auth/register")
async def register(data: UserRegister):
    if await db.users.find_one({"email": data.email.lower()}):
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    uid = str(uuid.uuid4())
    colors = ["#8B5CF6", "#F97316", "#EAB308", "#22C55E", "#EF4444", "#3B82F6"]
    doc = {
        "id": uid, "name": data.name, "email": data.email.lower(),
        "password_hash": hash_password(data.password),
        "xp": 0, "lives": 5, "streak": 0, "coins": 15, "last_active": None,
        "completed_lessons": [], "achievements": [],
        "avatar_color": colors[hash(uid) % len(colors)],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(doc)
    return {"token": create_token(uid), "user": public_user(doc)}

@api_router.post("/auth/login")
async def login(data: UserLogin):
    u = await db.users.find_one({"email": data.email.lower()})
    if not u or not u.get("password_hash") or not verify_password(data.password, u["password_hash"]):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    return {"token": create_token(u["id"]), "user": public_user(u)}

@api_router.get("/auth/me")
async def me(user=Depends(get_current_user)):
    return public_user(user)


# ============= GOOGLE OAUTH (Emergent Managed) =============
import requests as _req

class GoogleSessionRequest(BaseModel):
    session_id: str

@api_router.post("/auth/google/session")
async def google_session(req: GoogleSessionRequest):
    """Exchange Emergent Auth session_id for our own JWT.
    Creates or updates the user and returns {token, user} like /auth/login."""
    logger.info(f"📱 Tentativa de login com Google - session_id: {req.session_id[:20]}...")
    
    try:
        r = _req.get(
            "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
            headers={"X-Session-ID": req.session_id},
            timeout=10,
        )
        logger.info(f"   Resposta Emergent: {r.status_code}")
        
        if r.status_code != 200:
            logger.error(f"   ❌ Erro: {r.text}")
            raise HTTPException(status_code=401, detail="Sessão Google inválida ou expirada")
        
        data = r.json()
        logger.info(f"   ✅ Dados recebidos: {data}")
    except _req.RequestException as e:
        logger.error(f"   ❌ Erro de conexão com Emergent: {e}")
        raise HTTPException(status_code=502, detail="Erro ao contatar servidor de autenticação")

    email = (data.get("email") or "").lower()
    name = data.get("name") or email.split("@")[0]
    picture = data.get("picture")
    
    if not email:
        logger.error("   ❌ Conta Google sem e-mail!")
        raise HTTPException(status_code=400, detail="Conta Google sem e-mail")

    logger.info(f"   👤 Usuário: {name} ({email})")
    
    user = await db.users.find_one({"email": email})
    if user:
        logger.info(f"   ✅ Usuário existente encontrado")
        updates = {"google_linked": True, "last_active": datetime.now(timezone.utc).isoformat()}
        if picture and not user.get("picture"):
            updates["picture"] = picture
        await db.users.update_one({"id": user["id"]}, {"$set": updates})
        user = await db.users.find_one({"id": user["id"]}, {"_id": 0, "password_hash": 0})
    else:
        logger.info(f"   🆕 Criando novo usuário")
        uid = str(uuid.uuid4())
        colors = ["#8B5CF6", "#F97316", "#EAB308", "#22C55E", "#EF4444", "#3B82F6"]
        user = {
            "id": uid, "name": name, "email": email,
            "password_hash": "",  # Google-only account (cannot login via /auth/login)
            "xp": 0, "lives": 5, "streak": 0, "coins": 15, "last_active": datetime.now(timezone.utc).isoformat(),
            "completed_lessons": [], "achievements": [],
            "avatar_color": colors[hash(uid) % len(colors)],
            "picture": picture, "google_linked": True,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        await db.users.insert_one(user)
        logger.info(f"   ✅ Usuário criado com sucesso")

    logger.info(f"   ✅ Login com Google concluído!")
    return {"token": create_token(user["id"]), "user": public_user(user)}


# ============= META =============
@api_router.get("/meta/ranks")
async def meta_ranks():
    return {"ranks": RANKS, "level_required": LEVEL_RANK_REQUIRED, "level_labels": LEVEL_LABELS,
            "difficulty_xp": DIFFICULTY_XP, "powers": POWERS, "power_cost": POWER_COST}


# ============= SUBJECTS =============
@api_router.get("/subjects")
async def list_subjects():
    subjects = await db.subjects.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    # Adiciona informações básicas de cada matéria
    for s in subjects:
        lessons = await db.lessons.find({"subject_id": s["id"]}, {"_id": 0, "id": 1}).to_list(100)
        s["total_lessons"] = len(lessons)
        s["completed_lessons"] = 0  # Sem usuário autenticado, 0 completadas
        s["progress"] = 0
    return subjects

@api_router.get("/subjects/{subject_id}/lessons")
async def list_lessons(subject_id: str, creds: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    subject = await db.subjects.find_one({"id": subject_id}, {"_id": 0})
    if not subject: 
        raise HTTPException(status_code=404, detail="Matéria não encontrada")
    
    # Tenta obter o usuário se autenticado
    user = None
    user_rank_id = "bronze"
    completed_lessons = set()
    
    if creds:
        try:
            uid = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM]).get("sub")
            user = await db.users.find_one({"id": uid}, {"_id": 0, "password_hash": 0})
            if user:
                user_rank_id = rank_for_xp(user.get("xp", 0))["id"]
                completed_lessons = set(user.get("completed_lessons", []))
        except jwt.PyJWTError:
            pass
    
    lessons = await db.lessons.find({"subject_id": subject_id}, {"_id": 0}).sort("order", 1).to_list(100)
    
    # Enriquece cada lição com informações
    for lesson in lessons:
        questions_count = await db.questions.count_documents({"lesson_id": lesson["id"]})
        lesson["questions_count"] = questions_count
        
        # Adiciona nível em português
        lesson["level_label"] = LEVEL_LABELS.get(lesson.get("level", "basico"), "Fundamental")
        lesson["required_rank"] = LEVEL_RANK_REQUIRED.get(lesson.get("level", "basico"), "bronze")
        
        # Adiciona status de desbloqueio e conclusão
        lesson["unlocked"] = level_unlocked(lesson.get("level", "basico"), user_rank_id)
        lesson["completed"] = lesson["id"] in completed_lessons
    
    return {"subject": subject, "lessons": lessons}

@api_router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str, user=Depends(get_current_user)):
    lesson = await db.lessons.find_one({"id": lesson_id}, {"_id": 0})
    if not lesson: raise HTTPException(status_code=404, detail="Lição não encontrada")
    user_rank = rank_for_xp(user.get("xp", 0))["id"]
    if not level_unlocked(lesson.get("level", "basico"), user_rank):
        raise HTTPException(status_code=403, detail=f"Lição requer patente {LEVEL_RANK_REQUIRED.get(lesson.get('level'), 'bronze').title()}")
    questions = await db.questions.find({"lesson_id": lesson_id}, {"_id": 0}).sort("order", 1).to_list(100)
    return {"lesson": lesson, "questions": questions}


# ============= COMPLETE LESSON =============
@api_router.post("/lessons/complete")
async def complete_lesson(req: CompleteLessonRequest, user=Depends(get_current_user)):
    lesson = await db.lessons.find_one({"id": req.lesson_id}, {"_id": 0})
    if not lesson: raise HTTPException(status_code=404, detail="Lição não encontrada")
    questions = await db.questions.find({"lesson_id": req.lesson_id}, {"_id": 0}).to_list(100)
    q_map = {q["id"]: q for q in questions}

    correct = 0; wrong = 0; xp_earned = 0
    for ans in req.answers:
        q = q_map.get(ans.question_id)
        if not q: continue
        diff_xp = DIFFICULTY_XP.get(q.get("difficulty", "medio"), 10)
        if ans.selected_index == -1:  # skipped via power
            continue
        if ans.selected_index == q["correct_index"]:
            correct += 1
            xp_earned += diff_xp
        else:
            wrong += 1

    total = len(questions)
    accuracy = (correct / total) if total else 0
    if accuracy >= 1.0: xp_earned += 20  # gabarito bonus
    elif accuracy >= 0.8: xp_earned += 10
    elif accuracy >= 0.5: xp_earned += 5

    perfect = correct == total
    coins_earned = correct + (3 if perfect else 0)

    today = date.today().isoformat()
    last_active = user.get("last_active")
    new_streak = user.get("streak", 0)
    if last_active != today:
        if last_active:
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            new_streak = new_streak + 1 if last_active == yesterday else 1
        else:
            new_streak = 1

    new_lives = max(0, user.get("lives", 5) - wrong)
    completed_set = set(user.get("completed_lessons", []))
    if req.lesson_id not in completed_set:
        completed_set.add(req.lesson_id)

    new_xp = user.get("xp", 0) + xp_earned
    new_coins = user.get("coins", 0) + coins_earned
    old_rank = rank_for_xp(user.get("xp", 0))
    new_rank = rank_for_xp(new_xp)
    rank_up = new_rank["id"] != old_rank["id"]

    achievements = list(user.get("achievements", []))
    new_achievements = []
    for ach in await db.achievements.find({}, {"_id": 0}).to_list(100):
        if ach["id"] in achievements: continue
        t, th = ach["type"], ach["threshold"]
        unlocked = (
            (t == "lessons" and len(completed_set) >= th) or
            (t == "xp" and new_xp >= th) or
            (t == "streak" and new_streak >= th) or
            (t == "perfect" and perfect) or
            (t == "rank" and rank_index(new_rank["id"]) >= th)
        )
        if unlocked:
            achievements.append(ach["id"])
            new_achievements.append(ach)

    await db.users.update_one({"id": user["id"]}, {"$set": {
        "xp": new_xp, "lives": new_lives, "streak": new_streak, "coins": new_coins,
        "last_active": today, "completed_lessons": list(completed_set),
        "achievements": achievements,
    }})
    return {
        "correct": correct, "wrong": wrong, "total": total,
        "xp_earned": xp_earned, "coins_earned": coins_earned, "perfect": perfect,
        "accuracy": int(accuracy * 100),
        "new_xp": new_xp, "new_lives": new_lives, "new_streak": new_streak, "new_coins": new_coins,
        "new_achievements": new_achievements,
        "rank_up": rank_up, "new_rank": new_rank, "old_rank": old_rank,
    }


# ============= POWERS =============
@api_router.post("/powers/use")
async def use_power(req: UsePowerRequest, user=Depends(get_current_user)):
    if req.power_id not in [p["id"] for p in POWERS]:
        raise HTTPException(status_code=400, detail="Habilidade inválida")
    if user.get("coins", 0) < POWER_COST:
        raise HTTPException(status_code=400, detail="Moedas insuficientes")
    new_coins = user.get("coins", 0) - POWER_COST
    await db.users.update_one({"id": user["id"]}, {"$set": {"coins": new_coins}})
    payload = {"power_id": req.power_id, "new_coins": new_coins}
    if req.power_id == "audience":
        # Caller will pass question via query? Use a separate endpoint instead.
        pass
    return payload

@api_router.get("/powers/audience/{question_id}")
async def audience_stats(question_id: str, user=Depends(get_current_user)):
    q = await db.questions.find_one({"id": question_id}, {"_id": 0})
    if not q: raise HTTPException(status_code=404, detail="Questão não encontrada")
    # Generate plausible audience: bias toward correct answer
    correct = q["correct_index"]
    n = len(q["options"])
    stats = [secrets.randbelow(17) + 2 for _ in range(n)]  # 2..18
    stats[correct] += secrets.randbelow(21) + 35           # +35..55
    s = sum(stats)
    pct = [round(x * 100 / s) for x in stats]
    diff = 100 - sum(pct)
    pct[correct] += diff  # rebalance
    return {"percentages": pct}


# ============= ACHIEVEMENTS / LEADERBOARD =============
@api_router.get("/achievements")
async def list_achievements(user=Depends(get_current_user)):
    items = await db.achievements.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    unlocked = set(user.get("achievements", []))
    for a in items:
        a["unlocked"] = a["id"] in unlocked
    return items

@api_router.get("/leaderboard")
async def leaderboard():
    users = await db.users.find({}, {"_id": 0, "id": 1, "name": 1, "xp": 1, "streak": 1, "avatar_color": 1, "rank": 1}).sort("xp", -1).limit(50).to_list(50)
    for i, u in enumerate(users):
        u["rank_position"] = i + 1
        # Calcula a patente se não existir
        if "rank" not in u or not u.get("rank"):
            u["rank"] = rank_for_xp(u.get("xp", 0))
    return users


# ============= AI =============
@api_router.post("/practice/ai")
async def ai_question(req: AIQuestionRequest, user=Depends(get_current_user)):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=503, detail="LLM não configurado")
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import json as json_lib
        chat = LlmChat(api_key=EMERGENT_LLM_KEY, session_id=f"ai-{user['id']}-{uuid.uuid4()}",
            system_message=("Você é um professor brasileiro de vestibular (ENEM/FUVEST). "
                "Crie questões de múltipla escolha em português, no estilo de provas reais. Retorne APENAS JSON, sem markdown.")
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        topic = (req.topic or "").strip() or "geral"
        prompt = (f"Gere 1 questão de {req.subject}, conteúdo específico: '{topic}', dificuldade {req.difficulty}, "
            "no estilo ENEM/FUVEST/UFMG. "
            'Retorne JSON: {"prompt":"...","options":["a","b","c","d"],"correct_index":0,"explanation":"..."}')
        response = await chat.send_message(UserMessage(text=prompt))
        text = response.strip().strip("`")
        if text.startswith("json"): text = text[4:].strip()
        data = json_lib.loads(text)
        return {"id": str(uuid.uuid4()), "prompt": data["prompt"], "options": data["options"],
                "correct_index": int(data["correct_index"]), "explanation": data.get("explanation", ""),
                "difficulty": req.difficulty, "source": f"IA · {req.subject} · {topic}"}
    except Exception as e:
        logger.exception("AI error")
        raise HTTPException(status_code=500, detail=f"Erro: {e}")


# ============= ADMIN =============
class AdminLogin(BaseModel):
    password: str

@api_router.post("/admin/login")
async def admin_login(data: AdminLogin):
    logger.info(f"🔑 Tentativa de login admin com senha...")
    logger.info(f"🔍 JWT_SECRET hash: {hash(JWT_SECRET)}, tamanho: {len(JWT_SECRET)}")
    logger.info(f"🔍 ADMIN_SECRET hash: {hash(ADMIN_SECRET)}, tamanho: {len(ADMIN_SECRET)}")
    logger.debug(f"🔍 Validando: senha recebida vs ADMIN_SECRET configurado")
    if data.password != ADMIN_SECRET:
        logger.warning(f"❌ Senha incorreta")
        raise HTTPException(status_code=401, detail="Senha de admin inválida")
    logger.info(f"✅ Senha correta! Gerando token admin...")
    logger.debug(f"🔐 Usando JWT_SECRET (primeiros 20 chars): {JWT_SECRET[:20]}...")
    token = jwt.encode(
        {"sub": "admin", "role": "admin", "exp": datetime.now(timezone.utc) + timedelta(hours=8)},
        JWT_SECRET, algorithm=JWT_ALGORITHM
    )
    logger.info(f"🔐 Token gerado com sucesso. Token (primeiros 50 chars): {token[:50]}...")
    return {"token": token}

async def require_admin(creds: HTTPAuthorizationCredentials = Depends(security)):
    try:
        logger.info(f"🔍 Decodificando token admin")
        logger.debug(f"🔍 JWT_SECRET usado para decodificar - hash: {hash(JWT_SECRET)}, tamanho: {len(JWT_SECRET)}")
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        role = payload.get("role")
        logger.info(f"🔐 Token recebido e decodificado com sucesso. Payload: {payload}")
        if role != "admin":
            logger.warning(f"⚠️ Acesso negado. Role esperada: 'admin', recebida: '{role}'")
            raise HTTPException(status_code=403, detail="Acesso negado - role inválida")
        logger.info(f"✅ Acesso admin concedido")
    except jwt.ExpiredSignatureError:
        logger.error("❌ Token expirado")
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.PyJWTError as e:
        logger.error(f"❌ Token inválido: {str(e)}")
        raise HTTPException(status_code=401, detail="Token de admin inválido")

@api_router.get("/admin/users")
async def admin_list_users(_=Depends(require_admin)):
    users = await db.users.find({}, {"_id": 0, "password_hash": 0}).sort("created_at", -1).to_list(1000)
    for u in users:
        rank = rank_for_xp(u.get("xp", 0))
        u["rank"] = rank
    return users

@api_router.delete("/admin/users/{user_id}")
async def admin_delete_user(user_id: str, _=Depends(require_admin)):
    result = await db.users.delete_one({"id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"ok": True}

@api_router.get("/admin/stats")
async def admin_stats(_=Depends(require_admin)):
    total_users = await db.users.count_documents({})
    total_lessons = await db.lessons.count_documents({})
    total_questions = await db.questions.count_documents({})
    today = date.today().isoformat()
    active_today = await db.users.count_documents({"last_active": today})
    pipeline = [{"$group": {"_id": None, "total_xp": {"$sum": "$xp"}, "avg_xp": {"$avg": "$xp"}}}]
    xp_data = await db.users.aggregate(pipeline).to_list(1)
    total_xp = int(xp_data[0]["total_xp"]) if xp_data else 0
    avg_xp = int(xp_data[0]["avg_xp"]) if xp_data else 0
    return {
        "total_users": total_users,
        "total_lessons": total_lessons,
        "total_questions": total_questions,
        "active_today": active_today,
        "total_xp": total_xp,
        "avg_xp": avg_xp,
    }

# ============= ADMIN QUESTIONS =============
@api_router.get("/admin/lessons/{lesson_id}/questions")
async def admin_list_questions(lesson_id: str, _=Depends(require_admin)):
    """Lista todas as questões de uma lição."""
    lesson = await db.lessons.find_one({"id": lesson_id}, {"_id": 0})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lição não encontrada")
    
    questions = await db.questions.find({"lesson_id": lesson_id}, {"_id": 0}).sort("order", 1).to_list(100)
    return questions

@api_router.post("/admin/questions")
async def admin_create_question(req: AdminCreateQuestion, _=Depends(require_admin)):
    """Cria uma nova questão em uma lição."""
    lesson = await db.lessons.find_one({"id": req.lesson_id}, {"_id": 0})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lição não encontrada")
    
    # Encontra a maior ordem atual
    last_question = await db.questions.find_one({"lesson_id": req.lesson_id}, sort=[("order", -1)], projection={"_id": 0})
    order = (last_question.get("order", -1) + 1) if last_question else 0
    
    question_doc = {
        "id": str(uuid.uuid4()),
        "lesson_id": req.lesson_id,
        "content_name": lesson.get("content_name"),
        "level": lesson.get("level"),
        "difficulty": lesson.get("level"),
        "order": order,
        "prompt": req.prompt,
        "options": req.options,
        "correct_index": req.correct_index,
        "explanation": req.explanation,
        "source": req.source or "Admin",
    }
    
    await db.questions.insert_one(question_doc)
    return question_doc

@api_router.put("/admin/questions/{question_id}")
async def admin_update_question(question_id: str, req: AdminUpdateQuestion, _=Depends(require_admin)):
    """Atualiza uma questão existente."""
    question = await db.questions.find_one({"id": question_id}, {"_id": 0})
    if not question:
        raise HTTPException(status_code=404, detail="Questão não encontrada")
    
    update_data = {}
    if req.prompt is not None:
        update_data["prompt"] = req.prompt
    if req.options is not None:
        update_data["options"] = req.options
    if req.correct_index is not None:
        update_data["correct_index"] = req.correct_index
    if req.explanation is not None:
        update_data["explanation"] = req.explanation
    if req.source is not None:
        update_data["source"] = req.source
    
    if update_data:
        await db.questions.update_one({"id": question_id}, {"$set": update_data})
    
    # Retorna a questão atualizada
    updated = await db.questions.find_one({"id": question_id}, {"_id": 0})
    return updated

@api_router.delete("/admin/questions/{question_id}")
async def admin_delete_question(question_id: str, _=Depends(require_admin)):
    """Deleta uma questão."""
    result = await db.questions.delete_one({"id": question_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Questão não encontrada")
    return {"ok": True}

@api_router.post("/lives/refill")
async def refill(user=Depends(get_current_user)):
    await db.users.update_one({"id": user["id"]}, {"$set": {"lives": 5}})
    return {"lives": 5}

@api_router.get("/")
async def root(): return {"message": "REVISA API"}


# ============= SEED =============
from seed_data import SUBJECTS_SEED, QUESTION_BANK, ACHIEVEMENTS_SEED, LEVELS as SEED_LEVELS


@app.on_event("startup")
async def seed_database():
    # Always reseed if subjects mismatch the new structure
    existing_subjects = await db.subjects.count_documents({})
    expected = len(SUBJECTS_SEED)
    needs_reseed = existing_subjects != expected
    if not needs_reseed:
        # Reseed if the new "fuvest" level isn't present (means old structure)
        has_fuvest = await db.lessons.find_one({"level": "fuvest"})
        if not has_fuvest:
            needs_reseed = True
        else:
            # Reseed if question count per lesson is too low (< 8 means old seed)
            total_qs = await db.questions.count_documents({})
            if total_qs < 300:
                needs_reseed = True
    if needs_reseed:
        await db.subjects.delete_many({})
        await db.lessons.delete_many({})
        await db.questions.delete_many({})
        for i, sub in enumerate(SUBJECTS_SEED):
            sub_id = str(uuid.uuid4())
            await db.subjects.insert_one({"id": sub_id, "order": i, **sub})
            levels_for_sub = QUESTION_BANK.get(sub["name"], {})
            for j, level in enumerate(SEED_LEVELS):
                qs = levels_for_sub.get(level, [])
                if not qs: continue
                lesson_id = str(uuid.uuid4())
                await db.lessons.insert_one({
                    "id": lesson_id, "subject_id": sub_id, "subject_name": sub["name"],
                    "title": f"{sub['name']} — {LEVEL_LABELS[level]}",
                    "level": level, "order": j,
                })
                for k, q in enumerate(qs):
                    await db.questions.insert_one({
                        "id": str(uuid.uuid4()), "lesson_id": lesson_id, "order": k, **q,
                    })
    if await db.achievements.count_documents({}) != len(ACHIEVEMENTS_SEED):
        await db.achievements.delete_many({})
        for ach in ACHIEVEMENTS_SEED:
            await db.achievements.insert_one({"id": str(uuid.uuid4()), **ach})


app.include_router(api_router)
app.add_middleware(CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"], allow_headers=["*"])

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
