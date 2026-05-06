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

app = FastAPI(title="REVISA API")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

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
    if not u or not verify_password(data.password, u["password_hash"]):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    return {"token": create_token(u["id"]), "user": public_user(u)}

@api_router.get("/auth/me")
async def me(user=Depends(get_current_user)):
    return public_user(user)


# ============= META =============
@api_router.get("/meta/ranks")
async def meta_ranks():
    return {"ranks": RANKS, "level_required": LEVEL_RANK_REQUIRED, "level_labels": LEVEL_LABELS,
            "difficulty_xp": DIFFICULTY_XP, "powers": POWERS, "power_cost": POWER_COST}


# ============= SUBJECTS =============
@api_router.get("/subjects")
async def list_subjects(user=Depends(get_current_user)):
    subjects = await db.subjects.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    completed = set(user.get("completed_lessons", []))
    for s in subjects:
        lessons = await db.lessons.find({"subject_id": s["id"]}, {"_id": 0, "id": 1}).to_list(100)
        s["total_lessons"] = len(lessons)
        s["completed_lessons"] = sum(1 for l in lessons if l["id"] in completed)
        s["progress"] = int((s["completed_lessons"] / s["total_lessons"]) * 100) if s["total_lessons"] else 0
    return subjects

@api_router.get("/subjects/{subject_id}/lessons")
async def list_lessons(subject_id: str, user=Depends(get_current_user)):
    subject = await db.subjects.find_one({"id": subject_id}, {"_id": 0})
    if not subject: raise HTTPException(status_code=404, detail="Matéria não encontrada")
    lessons = await db.lessons.find({"subject_id": subject_id}, {"_id": 0}).sort("order", 1).to_list(100)
    completed = set(user.get("completed_lessons", []))
    user_rank = rank_for_xp(user.get("xp", 0))["id"]
    # Group by level, lessons unlock progressively within a level if level itself is unlocked
    for i, l in enumerate(lessons):
        l["completed"] = l["id"] in completed
        lvl_ok = level_unlocked(l.get("level", "basico"), user_rank)
        prev_done = i == 0 or lessons[i-1]["id"] in completed or lessons[i-1].get("level") != l.get("level")
        l["unlocked"] = lvl_ok and prev_done
        l["level_label"] = LEVEL_LABELS.get(l.get("level", "basico"), l.get("level"))
        l["required_rank"] = LEVEL_RANK_REQUIRED.get(l.get("level", "basico"), "bronze")
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
async def leaderboard(user=Depends(get_current_user)):
    users = await db.users.find({}, {"_id": 0, "id": 1, "name": 1, "xp": 1, "streak": 1, "avatar_color": 1, "coins": 1}).sort("xp", -1).limit(50).to_list(50)
    for i, u in enumerate(users):
        u["rank_position"] = i + 1
        u["is_me"] = u["id"] == user["id"]
        u["tier"] = rank_for_xp(u.get("xp", 0))
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
