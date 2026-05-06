from fastapi import FastAPI, APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os, logging, bcrypt, jwt, uuid, random
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
LEVEL_RANK_REQUIRED = {"basico": "bronze", "intermediario": "prata", "avancado": "ouro", "pre_vestibular": "platina"}
LEVEL_LABELS = {"basico": "Básico (6º-9º)", "intermediario": "Intermediário", "avancado": "Avançado", "pre_vestibular": "Pré-Vestibular"}
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
    subject: str; difficulty: str = "medio"
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
        "xp": 0, "lives": 5, "streak": 0, "coins": 10, "last_active": None,
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
    stats = [random.randint(2, 18) for _ in range(n)]
    stats[correct] += random.randint(35, 55)
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
                "Crie questões de múltipla escolha em português. Retorne APENAS JSON, sem markdown.")
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        prompt = (f"Questão de {req.subject}, dificuldade {req.difficulty}, estilo ENEM/FUVEST. "
            'Retorne JSON: {"prompt":"...","options":["a","b","c","d"],"correct_index":0,"explanation":"..."}')
        response = await chat.send_message(UserMessage(text=prompt))
        text = response.strip().strip("`")
        if text.startswith("json"): text = text[4:].strip()
        data = json_lib.loads(text)
        return {"id": str(uuid.uuid4()), "prompt": data["prompt"], "options": data["options"],
                "correct_index": int(data["correct_index"]), "explanation": data.get("explanation", ""),
                "difficulty": req.difficulty}
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
SUBJECTS_SEED = [
    {"name": "Matemática", "icon": "Calculator",   "color": "#3B82F6", "description": "Funções, geometria, álgebra"},
    {"name": "Biologia",   "icon": "Leaf",         "color": "#86EFAC", "description": "Citologia, genética, ecologia"},
    {"name": "Geografia",  "icon": "Globe",        "color": "#A855F7", "description": "Física e humana"},
    {"name": "História",   "icon": "Landmark",     "color": "#EF4444", "description": "Brasil e mundo"},
    {"name": "Português",  "icon": "BookOpen",     "color": "#F97316", "description": "Gramática e interpretação"},
    {"name": "Química",    "icon": "FlaskConical", "color": "#84CC16", "description": "Orgânica e inorgânica"},
    {"name": "Física",     "icon": "Atom",         "color": "#1E40AF", "description": "Mecânica, ondas, eletricidade"},
    {"name": "Literatura", "icon": "BookMarked",   "color": "#EC4899", "description": "Movimentos literários"},
    {"name": "Inglês",     "icon": "Languages",    "color": "#FACC15", "description": "Reading e gramática"},
]

# Compact seed: each subject gets 4 lessons (one per level), each lesson 4 questions
def gen_questions(subject_name, level):
    """Returns list of 4 questions per (subject, level)."""
    bank = QUESTION_BANK.get(subject_name, {}).get(level, [])
    return bank

QUESTION_BANK = {
    "Matemática": {
        "basico": [
            {"prompt": "Quanto é 7 × 8?", "options": ["54", "56", "58", "64"], "correct_index": 1, "difficulty": "facil", "explanation": "7×8=56"},
            {"prompt": "Qual fração equivale a 0,5?", "options": ["1/4", "1/2", "1/3", "2/3"], "correct_index": 1, "difficulty": "facil", "explanation": "0,5 = 1/2"},
            {"prompt": "Resolva: 25 − 7 + 3", "options": ["15", "21", "23", "29"], "correct_index": 1, "difficulty": "facil", "explanation": "18+3=21"},
            {"prompt": "Quanto é 12² ?", "options": ["120", "144", "124", "168"], "correct_index": 1, "difficulty": "medio", "explanation": "12·12=144"},
        ],
        "intermediario": [
            {"prompt": "f(x)=2x+3, f(5)=?", "options": ["10","13","11","15"], "correct_index": 1, "difficulty": "medio", "explanation": "2·5+3=13"},
            {"prompt": "Raízes de x²−5x+6=0:", "options": ["1 e 6","2 e 3","-2 e -3","0 e 5"], "correct_index": 1, "difficulty": "medio", "explanation": "Soma=5, produto=6 → 2 e 3"},
            {"prompt": "Área de quadrado lado 7:", "options": ["14","21","49","56"], "correct_index": 2, "difficulty": "facil", "explanation": "7²=49"},
            {"prompt": "Razão entre 12 e 18:", "options": ["1/2","2/3","3/4","3/5"], "correct_index": 1, "difficulty": "medio", "explanation": "12/18 = 2/3"},
        ],
        "avancado": [
            {"prompt": "log₁₀(1000) = ?", "options": ["1","2","3","10"], "correct_index": 2, "difficulty": "medio", "explanation": "10³=1000"},
            {"prompt": "Sen(30°) =", "options": ["1/2","√3/2","√2/2","1"], "correct_index": 0, "difficulty": "medio", "explanation": "Valor notável"},
            {"prompt": "Solução de 2ˣ = 32:", "options": ["3","4","5","6"], "correct_index": 2, "difficulty": "dificil", "explanation": "2⁵=32"},
            {"prompt": "Derivada de x³:", "options": ["x²","3x²","3x","x⁴/4"], "correct_index": 1, "difficulty": "dificil", "explanation": "Regra da potência"},
        ],
        "pre_vestibular": [
            {"prompt": "(ENEM) Lim x→2 (x²−4)/(x−2):", "options": ["0","2","4","∞"], "correct_index": 2, "difficulty": "dificil", "explanation": "Fatora: (x+2)(x−2)/(x−2) → x+2 = 4"},
            {"prompt": "Combinação C(5,2):", "options": ["5","10","20","25"], "correct_index": 1, "difficulty": "dificil", "explanation": "5!/(2!3!)=10"},
            {"prompt": "Probabilidade de tirar par num dado:", "options": ["1/3","1/2","2/3","1/6"], "correct_index": 1, "difficulty": "medio", "explanation": "3/6 = 1/2"},
            {"prompt": "Integral de 2x dx:", "options": ["x²+C","2","x²/2","2x²"], "correct_index": 0, "difficulty": "dificil", "explanation": "∫2x = x² + C"},
        ],
    },
    "Biologia": {
        "basico": [
            {"prompt": "Unidade básica da vida:", "options": ["Átomo","Célula","Tecido","Órgão"], "correct_index": 1, "difficulty": "facil", "explanation": "A célula é a menor unidade viva"},
            {"prompt": "Onde ocorre a fotossíntese?", "options": ["Mitocôndria","Cloroplasto","Núcleo","Vacúolo"], "correct_index": 1, "difficulty": "facil", "explanation": "Nos cloroplastos"},
            {"prompt": "Mamíferos respiram por:", "options": ["Brânquias","Pele","Pulmões","Traqueias"], "correct_index": 2, "difficulty": "facil", "explanation": "Pulmões"},
            {"prompt": "Reino dos cogumelos:", "options": ["Plantae","Fungi","Animalia","Protista"], "correct_index": 1, "difficulty": "facil", "explanation": "Reino Fungi"},
        ],
        "intermediario": [
            {"prompt": "Material genético está no(a):", "options": ["Citoplasma","Núcleo","Membrana","Ribossomo"], "correct_index": 1, "difficulty": "medio", "explanation": "DNA no núcleo"},
            {"prompt": "ATP é produzido principalmente em:", "options": ["Lisossomo","Mitocôndria","Golgi","Vacúolo"], "correct_index": 1, "difficulty": "medio", "explanation": "Mitocôndria"},
            {"prompt": "Tipo sanguíneo doador universal:", "options": ["A","B","AB","O-"], "correct_index": 3, "difficulty": "medio", "explanation": "O- doa para todos"},
            {"prompt": "Cromossomos humanos somáticos:", "options": ["23","44","46","48"], "correct_index": 2, "difficulty": "medio", "explanation": "23 pares = 46"},
        ],
        "avancado": [
            {"prompt": "Síntese de proteínas ocorre nos:", "options": ["Cloroplastos","Ribossomos","Lisossomos","Vacúolos"], "correct_index": 1, "difficulty": "medio", "explanation": "Ribossomos traduzem mRNA"},
            {"prompt": "Mitose origina:", "options": ["4 gametas","2 células iguais","Meiose","Esporos"], "correct_index": 1, "difficulty": "medio", "explanation": "2 células-filhas idênticas"},
            {"prompt": "Lei de Mendel: proporção F2:", "options": ["1:1","3:1","9:3:3:1","2:1"], "correct_index": 1, "difficulty": "dificil", "explanation": "Mono-híbrido = 3:1"},
            {"prompt": "Vírus se reproduzem:", "options": ["Sozinhos","Por mitose","Em hospedeiro","Por meiose"], "correct_index": 2, "difficulty": "medio", "explanation": "Parasitas obrigatórios"},
        ],
        "pre_vestibular": [
            {"prompt": "(ENEM) Bioma com maior biodiversidade do Brasil:", "options": ["Cerrado","Caatinga","Amazônia","Pampa"], "correct_index": 2, "difficulty": "medio", "explanation": "Floresta Amazônica"},
            {"prompt": "Eutrofização causa:", "options": ["Mais peixes","Aumento de O₂","Morte de peixes","Mais luz"], "correct_index": 2, "difficulty": "dificil", "explanation": "Excesso de nutrientes consome O₂"},
            {"prompt": "Anabolismo:", "options": ["Quebra moléculas","Síntese","Respiração","Fermentação"], "correct_index": 1, "difficulty": "dificil", "explanation": "Síntese com gasto de energia"},
            {"prompt": "Hormônio do crescimento:", "options": ["Insulina","GH","Adrenalina","Tiroxina"], "correct_index": 1, "difficulty": "medio", "explanation": "GH (somatotrofina)"},
        ],
    },
    "Geografia": {
        "basico": [
            {"prompt": "Capital do Brasil:", "options": ["SP","RJ","Brasília","Salvador"], "correct_index": 2, "difficulty": "facil", "explanation": "Brasília desde 1960"},
            {"prompt": "Maior continente:", "options": ["África","Ásia","América","Europa"], "correct_index": 1, "difficulty": "facil", "explanation": "Ásia"},
            {"prompt": "Linha do Equador divide a Terra em:", "options": ["Leste/Oeste","Norte/Sul","4 partes","Tropical/Polar"], "correct_index": 1, "difficulty": "facil", "explanation": "Hemisférios N e S"},
            {"prompt": "Brasil possui quantos estados?", "options": ["24","25","26","27"], "correct_index": 2, "difficulty": "facil", "explanation": "26 + DF"},
        ],
        "intermediario": [
            {"prompt": "Bioma do sertão:", "options": ["Cerrado","Caatinga","Pantanal","Mata Atlântica"], "correct_index": 1, "difficulty": "medio", "explanation": "Caatinga é nordestina"},
            {"prompt": "Rio mais extenso do Brasil:", "options": ["São Francisco","Amazonas","Paraná","Tocantins"], "correct_index": 1, "difficulty": "facil", "explanation": "Amazonas"},
            {"prompt": "Movimento de translação dura:", "options": ["24h","30 dias","365 dias","100 anos"], "correct_index": 2, "difficulty": "facil", "explanation": "365,25 dias"},
            {"prompt": "Migração rural→urbana chama-se:", "options": ["Êxodo rural","Êxodo urbano","Imigração","Refluxo"], "correct_index": 0, "difficulty": "medio", "explanation": "Êxodo rural"},
        ],
        "avancado": [
            {"prompt": "Globalização refere-se a:", "options": ["Aquecimento","Integração mundial","Migração polar","Solo"], "correct_index": 1, "difficulty": "medio", "explanation": "Integração econômica/cultural global"},
            {"prompt": "ONU foi criada em:", "options": ["1918","1945","1960","1989"], "correct_index": 1, "difficulty": "medio", "explanation": "Após 2ª Guerra"},
            {"prompt": "BRICS inclui:", "options": ["Brasil, Rússia, Índia, China, África do Sul","só Europa","só Américas","UE"], "correct_index": 0, "difficulty": "medio", "explanation": "5 economias emergentes"},
            {"prompt": "Mercosul é bloco:", "options": ["Asiático","Sul-americano","Africano","Europeu"], "correct_index": 1, "difficulty": "medio", "explanation": "Brasil, Arg, Uru, Par"},
        ],
        "pre_vestibular": [
            {"prompt": "(ENEM) Efeito estufa intensificado é causado por:", "options": ["Vapor d'água","CO₂ e CH₄","Oxigênio","Hélio"], "correct_index": 1, "difficulty": "dificil", "explanation": "Gases de efeito estufa"},
            {"prompt": "IDH considera:", "options": ["Só PIB","Renda, educação, saúde","Religião","Política"], "correct_index": 1, "difficulty": "medio", "explanation": "Índice tridimensional"},
            {"prompt": "Maior produtor mundial de soja:", "options": ["EUA","Brasil","Argentina","China"], "correct_index": 1, "difficulty": "dificil", "explanation": "Brasil lidera desde 2020"},
            {"prompt": "Conflito histórico Israel-Palestina disputa:", "options": ["Petróleo","Território","Religião apenas","Águas"], "correct_index": 1, "difficulty": "dificil", "explanation": "Disputa territorial e religiosa"},
        ],
    },
    "História": {
        "basico": [
            {"prompt": "Brasil foi descoberto em:", "options": ["1492","1500","1530","1822"], "correct_index": 1, "difficulty": "facil", "explanation": "22/4/1500 por Cabral"},
            {"prompt": "Independência do Brasil:", "options": ["1500","1822","1889","1808"], "correct_index": 1, "difficulty": "facil", "explanation": "7/9/1822"},
            {"prompt": "Egito antigo construiu:", "options": ["Coliseu","Pirâmides","Muralha","Acrópole"], "correct_index": 1, "difficulty": "facil", "explanation": "Pirâmides de Gizé"},
            {"prompt": "Idade Média começa após queda de:", "options": ["Egito","Roma","Grécia","Persa"], "correct_index": 1, "difficulty": "facil", "explanation": "Império Romano (476)"},
        ],
        "intermediario": [
            {"prompt": "Capitanias hereditárias por:", "options": ["D. João VI","D. Pedro I","D. João III","Cabral"], "correct_index": 2, "difficulty": "medio", "explanation": "D. João III, 1534"},
            {"prompt": "Inconfidência Mineira:", "options": ["1789","1808","1822","1888"], "correct_index": 0, "difficulty": "medio", "explanation": "1789, contra a Coroa"},
            {"prompt": "Abolição da escravidão:", "options": ["1822","1850","1888","1900"], "correct_index": 2, "difficulty": "facil", "explanation": "Lei Áurea, 1888"},
            {"prompt": "Proclamação da República:", "options": ["1822","1889","1891","1930"], "correct_index": 1, "difficulty": "medio", "explanation": "15/11/1889"},
        ],
        "avancado": [
            {"prompt": "Era Vargas inicia em:", "options": ["1922","1930","1945","1964"], "correct_index": 1, "difficulty": "medio", "explanation": "Revolução de 1930"},
            {"prompt": "Ditadura militar brasileira:", "options": ["1930-1945","1945-1964","1964-1985","1985-2000"], "correct_index": 2, "difficulty": "medio", "explanation": "21 anos"},
            {"prompt": "Plano Real:", "options": ["1985","1988","1994","2002"], "correct_index": 2, "difficulty": "medio", "explanation": "FHC ministro, 1994"},
            {"prompt": "1ª Guerra Mundial:", "options": ["1900-1910","1914-1918","1939-1945","1950-1953"], "correct_index": 1, "difficulty": "medio", "explanation": "1914-1918"},
        ],
        "pre_vestibular": [
            {"prompt": "(FUVEST) Revolução Industrial começou na:", "options": ["França","Alemanha","Inglaterra","EUA"], "correct_index": 2, "difficulty": "medio", "explanation": "Inglaterra séc XVIII"},
            {"prompt": "Guerra Fria opôs:", "options": ["EUA × URSS","Brasil × Argentina","França × Inglaterra","Roma × Cartago"], "correct_index": 0, "difficulty": "medio", "explanation": "1947-1991"},
            {"prompt": "Iluminismo defendia:", "options": ["Absolutismo","Razão e direitos","Feudalismo","Teocracia"], "correct_index": 1, "difficulty": "dificil", "explanation": "Voltaire, Rousseau, Locke"},
            {"prompt": "Constituição cidadã brasileira:", "options": ["1824","1891","1934","1988"], "correct_index": 3, "difficulty": "medio", "explanation": "Constituição de 1988"},
        ],
    },
    "Português": {
        "basico": [
            {"prompt": "Plural de 'cidadão':", "options": ["cidadões","cidadãos","cidadães","cidadans"], "correct_index": 1, "difficulty": "facil", "explanation": "cidadãos"},
            {"prompt": "'Casa' é:", "options": ["Verbo","Adjetivo","Substantivo","Advérbio"], "correct_index": 2, "difficulty": "facil", "explanation": "Substantivo"},
            {"prompt": "Sujeito de 'O cão late':", "options": ["late","O cão","cão","-"], "correct_index": 1, "difficulty": "facil", "explanation": "Sujeito completo"},
            {"prompt": "Antônimo de 'feliz':", "options": ["alegre","triste","contente","bom"], "correct_index": 1, "difficulty": "facil", "explanation": "Triste"},
        ],
        "intermediario": [
            {"prompt": "Crase obrigatória em:", "options": ["Vou a escola","Vou à escola","Vou a casa","Refiro-me a você"], "correct_index": 1, "difficulty": "medio", "explanation": "à = a + a (artigo)"},
            {"prompt": "Predicado verbo-nominal possui:", "options": ["Só verbo","Só nome","Verbo + predicativo","Adjetivo"], "correct_index": 2, "difficulty": "medio", "explanation": "Verbo de ação + predicativo"},
            {"prompt": "Conjunção adversativa:", "options": ["e","mas","porque","logo"], "correct_index": 1, "difficulty": "medio", "explanation": "Mas, porém, contudo"},
            {"prompt": "'Onde' como pronome relativo refere-se a:", "options": ["Tempo","Lugar","Causa","Pessoa"], "correct_index": 1, "difficulty": "medio", "explanation": "Indica lugar"},
        ],
        "avancado": [
            {"prompt": "Figura: 'mar de gente':", "options": ["Metáfora","Hipérbole","Ironia","Metonímia"], "correct_index": 0, "difficulty": "medio", "explanation": "Metáfora"},
            {"prompt": "Oração subordinada substantiva subjetiva:", "options": ["É necessário que estudes","Sei que choveu","Casa que comprei","Choveu, embora frio"], "correct_index": 0, "difficulty": "dificil", "explanation": "Função de sujeito"},
            {"prompt": "'Houveram' está:", "options": ["Correto","Errado: 'houve'","Regional","Antigo"], "correct_index": 1, "difficulty": "dificil", "explanation": "Haver impessoal: houve"},
            {"prompt": "Pronome demonstrativo:", "options": ["meu","este","ele","quem"], "correct_index": 1, "difficulty": "facil", "explanation": "Este, esse, aquele"},
        ],
        "pre_vestibular": [
            {"prompt": "(ENEM) Variação linguística:", "options": ["Erro","Mudança natural da língua","Invenção","Estrangeirismo"], "correct_index": 1, "difficulty": "medio", "explanation": "Língua é viva e varia"},
            {"prompt": "Função da linguagem em poesia lírica:", "options": ["Referencial","Emotiva","Conativa","Metalinguística"], "correct_index": 1, "difficulty": "dificil", "explanation": "Foco no emissor"},
            {"prompt": "Concordância: 'Faz dois anos ___':", "options": ["fazem","faz","fizeram","fariam"], "correct_index": 1, "difficulty": "dificil", "explanation": "Verbo impessoal: faz"},
            {"prompt": "Coesão referencial usa:", "options": ["Pronomes","Adjetivos","Verbos","Vogais"], "correct_index": 0, "difficulty": "medio", "explanation": "Retomada por pronome"},
        ],
    },
    "Química": {
        "basico": [
            {"prompt": "Símbolo do hidrogênio:", "options": ["H","He","Hi","Hg"], "correct_index": 0, "difficulty": "facil", "explanation": "H"},
            {"prompt": "Água tem fórmula:", "options": ["CO₂","H₂O","NaCl","O₂"], "correct_index": 1, "difficulty": "facil", "explanation": "H₂O"},
            {"prompt": "Estado físico do gelo:", "options": ["Sólido","Líquido","Gasoso","Plasma"], "correct_index": 0, "difficulty": "facil", "explanation": "Sólido"},
            {"prompt": "Átomo é composto por:", "options": ["Só prótons","Prótons, nêutrons, elétrons","Só elétrons","Moléculas"], "correct_index": 1, "difficulty": "facil", "explanation": "p+, n⁰, e-"},
        ],
        "intermediario": [
            {"prompt": "pH neutro:", "options": ["0","7","14","-7"], "correct_index": 1, "difficulty": "facil", "explanation": "Neutro = 7"},
            {"prompt": "Família 1A (alcalinos):", "options": ["He, Ne","Li, Na, K","F, Cl","C, Si"], "correct_index": 1, "difficulty": "medio", "explanation": "Metais alcalinos"},
            {"prompt": "NaCl é ligação:", "options": ["Covalente","Iônica","Metálica","Hidrogênio"], "correct_index": 1, "difficulty": "medio", "explanation": "Sal: iônica"},
            {"prompt": "Mol contém ___ partículas:", "options": ["10²³","6,02×10²³","6,02×10¹⁰","10¹⁰"], "correct_index": 1, "difficulty": "medio", "explanation": "Avogadro"},
        ],
        "avancado": [
            {"prompt": "Função orgânica do etanol (CH₃CH₂OH):", "options": ["Ácido","Álcool","Éter","Cetona"], "correct_index": 1, "difficulty": "medio", "explanation": "Grupo OH = álcool"},
            {"prompt": "Reação exotérmica:", "options": ["Absorve calor","Libera calor","Não troca","Só luz"], "correct_index": 1, "difficulty": "medio", "explanation": "ΔH < 0"},
            {"prompt": "Isomeria de C₂H₆O:", "options": ["Etanol/Éter dimetílico","CO₂","Metano","Glicose"], "correct_index": 0, "difficulty": "dificil", "explanation": "Isômeros de função"},
            {"prompt": "Reação ácido-base produz:", "options": ["Sal e água","Apenas gás","Metal","Plástico"], "correct_index": 0, "difficulty": "medio", "explanation": "Neutralização"},
        ],
        "pre_vestibular": [
            {"prompt": "(FUVEST) Lei de Lavoisier:", "options": ["Conservação da massa","Energia","Eletricidade","Gravidade"], "correct_index": 0, "difficulty": "medio", "explanation": "Massa se conserva"},
            {"prompt": "Eletronegatividade maior:", "options": ["Na","Cl","K","Mg"], "correct_index": 1, "difficulty": "dificil", "explanation": "Cl entre os listados"},
            {"prompt": "Hibridização do C no metano:", "options": ["sp","sp²","sp³","p"], "correct_index": 2, "difficulty": "dificil", "explanation": "4 ligações simples"},
            {"prompt": "Concentração mol/L:", "options": ["g/L","mol/L","mol·L","mol/g"], "correct_index": 1, "difficulty": "medio", "explanation": "Molaridade"},
        ],
    },
    "Física": {
        "basico": [
            {"prompt": "Unidade de força:", "options": ["Joule","Newton","Watt","Pascal"], "correct_index": 1, "difficulty": "facil", "explanation": "N (kg·m/s²)"},
            {"prompt": "Velocidade média:", "options": ["d×t","d/t","t/d","d+t"], "correct_index": 1, "difficulty": "facil", "explanation": "Δs/Δt"},
            {"prompt": "g (Terra) ≈:", "options": ["5","9,8","20","100"], "correct_index": 1, "difficulty": "facil", "explanation": "9,8 m/s²"},
            {"prompt": "Peso = ?", "options": ["m","mg","ma","mv"], "correct_index": 1, "difficulty": "facil", "explanation": "P = m·g"},
        ],
        "intermediario": [
            {"prompt": "1ª Lei de Newton:", "options": ["F=ma","Inércia","Ação-reação","Gravidade"], "correct_index": 1, "difficulty": "medio", "explanation": "Inércia"},
            {"prompt": "Energia cinética:", "options": ["mgh","½mv²","mv","ma"], "correct_index": 1, "difficulty": "medio", "explanation": "Ec = ½mv²"},
            {"prompt": "Trabalho (J) =", "options": ["F·d","F/d","F+d","F²"], "correct_index": 0, "difficulty": "medio", "explanation": "W = F·d·cosθ"},
            {"prompt": "Som propaga-se em:", "options": ["Vácuo","Sólido/líquido/gás","Só ar","Só água"], "correct_index": 1, "difficulty": "facil", "explanation": "Precisa meio material"},
        ],
        "avancado": [
            {"prompt": "Lei de Ohm:", "options": ["V=R/I","V=RI","V=I/R","R=V·I"], "correct_index": 1, "difficulty": "medio", "explanation": "V = R·I"},
            {"prompt": "Comprimento de onda x freq:", "options": ["v=λf","v=λ/f","v=f/λ","v=λ+f"], "correct_index": 0, "difficulty": "medio", "explanation": "v = λ·f"},
            {"prompt": "Carga do elétron:", "options": ["+","-","Neutra","Variável"], "correct_index": 1, "difficulty": "facil", "explanation": "Negativa"},
            {"prompt": "Resistores em série soma:", "options": ["1/R","R total = R1+R2","R²","R/2"], "correct_index": 1, "difficulty": "medio", "explanation": "Somam-se"},
        ],
        "pre_vestibular": [
            {"prompt": "(ENEM) Energia potencial gravitacional:", "options": ["½mv²","mgh","Fd","ma"], "correct_index": 1, "difficulty": "medio", "explanation": "Ep = mgh"},
            {"prompt": "Efeito fotoelétrico foi explicado por:", "options": ["Newton","Einstein","Bohr","Maxwell"], "correct_index": 1, "difficulty": "dificil", "explanation": "Einstein, Nobel 1921"},
            {"prompt": "Lente que converge raios:", "options": ["Plana","Côncava","Convexa","Espelho"], "correct_index": 2, "difficulty": "medio", "explanation": "Lente convergente (convexa)"},
            {"prompt": "Velocidade da luz:", "options": ["3·10⁵ km/s","3·10⁸ m/s","Mesmo valor","Ambas A e B"], "correct_index": 3, "difficulty": "dificil", "explanation": "c ≈ 3·10⁸ m/s = 3·10⁵ km/s"},
        ],
    },
    "Literatura": {
        "basico": [
            {"prompt": "Gênero épico narra:", "options": ["Sentimentos","Heróis e feitos","Diálogos","Argumentos"], "correct_index": 1, "difficulty": "facil", "explanation": "Heróis"},
            {"prompt": "Quem escreveu 'Dom Casmurro'?", "options": ["Drummond","Machado","Alencar","Bilac"], "correct_index": 1, "difficulty": "facil", "explanation": "Machado de Assis"},
            {"prompt": "Soneto tem quantos versos:", "options": ["8","10","12","14"], "correct_index": 3, "difficulty": "facil", "explanation": "14 versos"},
            {"prompt": "Verso branco:", "options": ["Sem rima","Sem métrica","Em branco","Curto"], "correct_index": 0, "difficulty": "facil", "explanation": "Sem rima"},
        ],
        "intermediario": [
            {"prompt": "Iracema é de:", "options": ["Alencar","Castro Alves","Bilac","Drummond"], "correct_index": 0, "difficulty": "medio", "explanation": "Romantismo indianista"},
            {"prompt": "Olavo Bilac é:", "options": ["Romântico","Parnasiano","Modernista","Barroco"], "correct_index": 1, "difficulty": "medio", "explanation": "Príncipe dos poetas"},
            {"prompt": "Modernismo no Brasil começou em:", "options": ["1900","1922","1945","1964"], "correct_index": 1, "difficulty": "medio", "explanation": "Semana de 22"},
            {"prompt": "Drummond é da:", "options": ["1ª geração","2ª geração","3ª geração","Romantismo"], "correct_index": 1, "difficulty": "medio", "explanation": "Geração de 30"},
        ],
        "avancado": [
            {"prompt": "Realismo no Brasil:", "options": ["Sentimental","Crítico, social","Indianista","Religioso"], "correct_index": 1, "difficulty": "medio", "explanation": "Análise social"},
            {"prompt": "Clarice Lispector é:", "options": ["Romântica","Modernista 3ª","Parnasiana","Árcade"], "correct_index": 1, "difficulty": "medio", "explanation": "3ª geração modernista"},
            {"prompt": "'Vidas Secas' é de:", "options": ["Jorge Amado","Graciliano","Drummond","Machado"], "correct_index": 1, "difficulty": "medio", "explanation": "Graciliano Ramos, 1938"},
            {"prompt": "Barroco caracteriza-se por:", "options": ["Equilíbrio","Conflitos e antíteses","Razão pura","Indianismo"], "correct_index": 1, "difficulty": "dificil", "explanation": "Dualismo"},
        ],
        "pre_vestibular": [
            {"prompt": "(FUVEST) 'Os Sertões' é de:", "options": ["Machado","Euclides da Cunha","Drummond","Lispector"], "correct_index": 1, "difficulty": "dificil", "explanation": "Euclides, 1902"},
            {"prompt": "Concretismo enfatiza:", "options": ["Métrica","Forma visual","Personagens","Gramática"], "correct_index": 1, "difficulty": "dificil", "explanation": "Poesia visual"},
            {"prompt": "Guimarães Rosa escreveu:", "options": ["Capitães de Areia","Grande Sertão: Veredas","Memórias","Iracema"], "correct_index": 1, "difficulty": "medio", "explanation": "1956"},
            {"prompt": "Arcadismo busca:", "options": ["Cidade","Bucolismo","Guerra","Monarquia"], "correct_index": 1, "difficulty": "dificil", "explanation": "Vida no campo"},
        ],
    },
    "Inglês": {
        "basico": [
            {"prompt": "I ___ a student.", "options": ["am","is","are","be"], "correct_index": 0, "difficulty": "facil", "explanation": "I + am"},
            {"prompt": "She ___ tall.", "options": ["am","is","are","be"], "correct_index": 1, "difficulty": "facil", "explanation": "She + is"},
            {"prompt": "Past of 'go':", "options": ["goed","went","gone","going"], "correct_index": 1, "difficulty": "facil", "explanation": "Irregular: went"},
            {"prompt": "'Apple' significa:", "options": ["Banana","Maçã","Uva","Pera"], "correct_index": 1, "difficulty": "facil", "explanation": "Maçã"},
        ],
        "intermediario": [
            {"prompt": "Present continuous of 'eat':", "options": ["eat","eating","ate","eaten"], "correct_index": 1, "difficulty": "medio", "explanation": "is/are eating"},
            {"prompt": "Plural of 'child':", "options": ["childs","children","childes","child"], "correct_index": 1, "difficulty": "medio", "explanation": "Children (irregular)"},
            {"prompt": "If I ___ rich, I would travel.", "options": ["am","were","be","is"], "correct_index": 1, "difficulty": "medio", "explanation": "2nd conditional"},
            {"prompt": "'Beautiful' é:", "options": ["Verbo","Adjetivo","Advérbio","Substantivo"], "correct_index": 1, "difficulty": "facil", "explanation": "Adjective"},
        ],
        "avancado": [
            {"prompt": "Comparative of 'good':", "options": ["gooder","more good","better","best"], "correct_index": 2, "difficulty": "medio", "explanation": "Better"},
            {"prompt": "Passive voice of 'They build houses':", "options": ["Houses are built","Houses build","Houses being","Houses been"], "correct_index": 0, "difficulty": "medio", "explanation": "are + past participle"},
            {"prompt": "Phrasal: 'give up' significa:", "options": ["Aumentar","Desistir","Dar","Subir"], "correct_index": 1, "difficulty": "medio", "explanation": "Desistir"},
            {"prompt": "'Used to' indica:", "options": ["Hábito presente","Hábito passado","Futuro","Imperativo"], "correct_index": 1, "difficulty": "dificil", "explanation": "Hábitos passados"},
        ],
        "pre_vestibular": [
            {"prompt": "(ENEM) 'However' funciona como:", "options": ["Adição","Contraste","Causa","Conclusão"], "correct_index": 1, "difficulty": "medio", "explanation": "Conector de contraste"},
            {"prompt": "Reading: main idea de um texto chama-se:", "options": ["Detail","Gist","Quote","List"], "correct_index": 1, "difficulty": "dificil", "explanation": "Gist = ideia central"},
            {"prompt": "'Despite' é seguido por:", "options": ["Verbo","Substantivo/-ing","Adjetivo só","Advérbio"], "correct_index": 1, "difficulty": "dificil", "explanation": "Despite + noun/-ing"},
            {"prompt": "Modal 'must' indica:", "options": ["Possibilidade","Obrigação forte","Habilidade","Permissão"], "correct_index": 1, "difficulty": "medio", "explanation": "Strong obligation"},
        ],
    },
}

ACHIEVEMENTS_SEED = [
    {"name": "Primeiro passo", "description": "Complete sua primeira lição", "icon": "Sparkles", "color": "#22C55E", "type": "lessons", "threshold": 1, "order": 1},
    {"name": "Aluno dedicado", "description": "Complete 5 lições", "icon": "BookOpen", "color": "#3B82F6", "type": "lessons", "threshold": 5, "order": 2},
    {"name": "Maratonista", "description": "Complete 15 lições", "icon": "Trophy", "color": "#EAB308", "type": "lessons", "threshold": 15, "order": 3},
    {"name": "Iniciando a chama", "description": "3 dias de ofensiva", "icon": "Flame", "color": "#F97316", "type": "streak", "threshold": 3, "order": 4},
    {"name": "Pegando fogo", "description": "7 dias de ofensiva", "icon": "Flame", "color": "#EF4444", "type": "streak", "threshold": 7, "order": 5},
    {"name": "100 XP", "description": "Acumule 100 XP", "icon": "Zap", "color": "#EAB308", "type": "xp", "threshold": 100, "order": 6},
    {"name": "500 XP", "description": "Acumule 500 XP", "icon": "Star", "color": "#8B5CF6", "type": "xp", "threshold": 500, "order": 7},
    {"name": "Perfeição", "description": "Complete uma lição sem erros", "icon": "Award", "color": "#22C55E", "type": "perfect", "threshold": 1, "order": 8},
    {"name": "Patente Prata", "description": "Alcance Prata", "icon": "Award", "color": "#94A3B8", "type": "rank", "threshold": 1, "order": 9},
    {"name": "Patente Ouro", "description": "Alcance Ouro", "icon": "Trophy", "color": "#EAB308", "type": "rank", "threshold": 2, "order": 10},
    {"name": "Patente Diamante", "description": "Alcance Diamante", "icon": "Diamond", "color": "#60A5FA", "type": "rank", "threshold": 4, "order": 11},
]


@app.on_event("startup")
async def seed_database():
    # Always reseed if subjects mismatch the new structure
    existing_subjects = await db.subjects.count_documents({})
    expected = len(SUBJECTS_SEED)
    needs_reseed = existing_subjects != expected
    if not needs_reseed:
        # check first subject color match
        first = await db.subjects.find_one({"name": "Biologia"}, {"_id": 0})
        if not first or first.get("color") != "#86EFAC":
            needs_reseed = True
    if needs_reseed:
        await db.subjects.delete_many({})
        await db.lessons.delete_many({})
        await db.questions.delete_many({})
        for i, sub in enumerate(SUBJECTS_SEED):
            sub_id = str(uuid.uuid4())
            await db.subjects.insert_one({"id": sub_id, "order": i, **sub})
            levels_for_sub = QUESTION_BANK.get(sub["name"], {})
            for j, level in enumerate(["basico", "intermediario", "avancado", "pre_vestibular"]):
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
