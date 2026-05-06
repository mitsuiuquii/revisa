from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import bcrypt
import jwt
import asyncio
from pathlib import Path
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta, date

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

JWT_SECRET = os.environ['JWT_SECRET']
JWT_ALGORITHM = "HS256"
JWT_EXPIRY_HOURS = 24 * 30

EMERGENT_LLM_KEY = os.environ.get('EMERGENT_LLM_KEY')

app = FastAPI(title="REVISA API")
api_router = APIRouter(prefix="/api")
security = HTTPBearer()


# ============= MODELS =============
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserPublic(BaseModel):
    id: str
    name: str
    email: str
    xp: int = 0
    lives: int = 5
    streak: int = 0
    last_active: Optional[str] = None
    completed_lessons: List[str] = []
    achievements: List[str] = []
    avatar_color: str = "#8B5CF6"

class AuthResponse(BaseModel):
    token: str
    user: UserPublic

class QuestionAnswer(BaseModel):
    question_id: str
    selected_index: int

class CompleteLessonRequest(BaseModel):
    lesson_id: str
    answers: List[QuestionAnswer]

class AIQuestionRequest(BaseModel):
    subject: str
    difficulty: str = "medio"


# ============= HELPERS =============
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

def create_token(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(creds: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(creds.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("sub")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token inválido")
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "password_hash": 0})
    if not user:
        raise HTTPException(status_code=401, detail="Usuário não encontrado")
    return user

def public_user(user: dict) -> UserPublic:
    return UserPublic(
        id=user["id"], name=user["name"], email=user["email"],
        xp=user.get("xp", 0), lives=user.get("lives", 5),
        streak=user.get("streak", 0), last_active=user.get("last_active"),
        completed_lessons=user.get("completed_lessons", []),
        achievements=user.get("achievements", []),
        avatar_color=user.get("avatar_color", "#8B5CF6"),
    )


# ============= AUTH =============
@api_router.post("/auth/register", response_model=AuthResponse)
async def register(data: UserRegister):
    existing = await db.users.find_one({"email": data.email.lower()})
    if existing:
        raise HTTPException(status_code=400, detail="E-mail já cadastrado")
    user_id = str(uuid.uuid4())
    colors = ["#8B5CF6", "#F97316", "#EAB308", "#22C55E", "#EF4444", "#3B82F6"]
    user_doc = {
        "id": user_id, "name": data.name, "email": data.email.lower(),
        "password_hash": hash_password(data.password),
        "xp": 0, "lives": 5, "streak": 0, "last_active": None,
        "completed_lessons": [], "achievements": [],
        "avatar_color": colors[hash(user_id) % len(colors)],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    await db.users.insert_one(user_doc)
    return AuthResponse(token=create_token(user_id), user=public_user(user_doc))

@api_router.post("/auth/login", response_model=AuthResponse)
async def login(data: UserLogin):
    user = await db.users.find_one({"email": data.email.lower()})
    if not user or not verify_password(data.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    return AuthResponse(token=create_token(user["id"]), user=public_user(user))

@api_router.get("/auth/me", response_model=UserPublic)
async def me(user=Depends(get_current_user)):
    return public_user(user)


# ============= SUBJECTS & LESSONS =============
@api_router.get("/subjects")
async def list_subjects(user=Depends(get_current_user)):
    subjects = await db.subjects.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    completed = set(user.get("completed_lessons", []))
    for s in subjects:
        lessons = await db.lessons.find({"subject_id": s["id"]}, {"_id": 0, "id": 1}).to_list(100)
        total = len(lessons)
        done = sum(1 for l in lessons if l["id"] in completed)
        s["total_lessons"] = total
        s["completed_lessons"] = done
        s["progress"] = int((done / total) * 100) if total else 0
    return subjects

@api_router.get("/subjects/{subject_id}/lessons")
async def list_lessons(subject_id: str, user=Depends(get_current_user)):
    subject = await db.subjects.find_one({"id": subject_id}, {"_id": 0})
    if not subject:
        raise HTTPException(status_code=404, detail="Matéria não encontrada")
    lessons = await db.lessons.find({"subject_id": subject_id}, {"_id": 0}).sort("order", 1).to_list(100)
    completed = set(user.get("completed_lessons", []))
    for i, l in enumerate(lessons):
        l["completed"] = l["id"] in completed
        # Lesson is unlocked if previous one completed (or first lesson)
        l["unlocked"] = i == 0 or lessons[i-1]["id"] in completed
    return {"subject": subject, "lessons": lessons}

@api_router.get("/lessons/{lesson_id}")
async def get_lesson(lesson_id: str, user=Depends(get_current_user)):
    lesson = await db.lessons.find_one({"id": lesson_id}, {"_id": 0})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lição não encontrada")
    questions = await db.questions.find({"lesson_id": lesson_id}, {"_id": 0}).sort("order", 1).to_list(100)
    # Don't expose correct_index to frontend - oh wait, we need it for instant feedback. 
    # We'll keep it; it's fine for an MVP educational app.
    return {"lesson": lesson, "questions": questions}

@api_router.post("/lessons/complete")
async def complete_lesson(req: CompleteLessonRequest, user=Depends(get_current_user)):
    lesson = await db.lessons.find_one({"id": req.lesson_id}, {"_id": 0})
    if not lesson:
        raise HTTPException(status_code=404, detail="Lição não encontrada")
    questions = await db.questions.find({"lesson_id": req.lesson_id}, {"_id": 0}).to_list(100)
    q_map = {q["id"]: q for q in questions}
    correct_count = 0
    wrong_count = 0
    for ans in req.answers:
        q = q_map.get(ans.question_id)
        if q and ans.selected_index == q["correct_index"]:
            correct_count += 1
        else:
            wrong_count += 1
    total = len(questions)
    xp_earned = correct_count * 10
    perfect = correct_count == total
    if perfect:
        xp_earned += 5

    # Streak update
    today = date.today().isoformat()
    last_active = user.get("last_active")
    new_streak = user.get("streak", 0)
    if last_active != today:
        if last_active:
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            new_streak = new_streak + 1 if last_active == yesterday else 1
        else:
            new_streak = 1

    # Lives update (deduct lives for wrong answers, min 0)
    new_lives = max(0, user.get("lives", 5) - wrong_count)

    completed_set = set(user.get("completed_lessons", []))
    is_first_completion = req.lesson_id not in completed_set
    if is_first_completion:
        completed_set.add(req.lesson_id)

    # Achievements
    achievements = list(user.get("achievements", []))
    new_achievements = []
    all_achievements = await db.achievements.find({}, {"_id": 0}).to_list(100)
    new_xp = user.get("xp", 0) + xp_earned
    new_completed_count = len(completed_set)
    
    for ach in all_achievements:
        if ach["id"] in achievements:
            continue
        unlocked = False
        atype = ach["type"]
        threshold = ach["threshold"]
        if atype == "lessons" and new_completed_count >= threshold:
            unlocked = True
        elif atype == "xp" and new_xp >= threshold:
            unlocked = True
        elif atype == "streak" and new_streak >= threshold:
            unlocked = True
        elif atype == "perfect" and perfect:
            unlocked = True
        if unlocked:
            achievements.append(ach["id"])
            new_achievements.append(ach)

    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {
            "xp": new_xp, "lives": new_lives, "streak": new_streak,
            "last_active": today, "completed_lessons": list(completed_set),
            "achievements": achievements,
        }}
    )
    return {
        "correct": correct_count, "wrong": wrong_count, "total": total,
        "xp_earned": xp_earned, "perfect": perfect,
        "new_xp": new_xp, "new_lives": new_lives, "new_streak": new_streak,
        "new_achievements": new_achievements,
    }


# ============= ACHIEVEMENTS =============
@api_router.get("/achievements")
async def list_achievements(user=Depends(get_current_user)):
    achievements = await db.achievements.find({}, {"_id": 0}).sort("order", 1).to_list(100)
    unlocked = set(user.get("achievements", []))
    for a in achievements:
        a["unlocked"] = a["id"] in unlocked
    return achievements


# ============= LEADERBOARD =============
@api_router.get("/leaderboard")
async def leaderboard(user=Depends(get_current_user)):
    users = await db.users.find({}, {"_id": 0, "id": 1, "name": 1, "xp": 1, "streak": 1, "avatar_color": 1}).sort("xp", -1).limit(50).to_list(50)
    for i, u in enumerate(users):
        u["rank"] = i + 1
        u["is_me"] = u["id"] == user["id"]
    return users


# ============= AI PRACTICE =============
@api_router.post("/practice/ai")
async def ai_question(req: AIQuestionRequest, user=Depends(get_current_user)):
    if not EMERGENT_LLM_KEY:
        raise HTTPException(status_code=503, detail="LLM não configurado")
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        import json as json_lib
        chat = LlmChat(
            api_key=EMERGENT_LLM_KEY,
            session_id=f"ai-{user['id']}-{uuid.uuid4()}",
            system_message=(
                "Você é um professor brasileiro especialista em vestibular (ENEM/FUVEST). "
                "Crie questões de múltipla escolha em português, exatamente como pedido. "
                "SEMPRE retorne APENAS JSON válido, sem markdown nem texto extra."
            ),
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        prompt = (
            f"Crie 1 questão de múltipla escolha sobre {req.subject}, dificuldade {req.difficulty}, "
            "para alunos de 12-18 anos preparando vestibular. "
            "Retorne JSON neste formato exato: "
            '{"prompt":"enunciado curto e claro","options":["a","b","c","d"],"correct_index":0,"explanation":"explicação curta"}'
        )
        response = await chat.send_message(UserMessage(text=prompt))
        text = response.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.startswith("json"):
                text = text[4:]
            text = text.strip()
        data = json_lib.loads(text)
        return {
            "id": str(uuid.uuid4()),
            "prompt": data["prompt"],
            "options": data["options"],
            "correct_index": int(data["correct_index"]),
            "explanation": data.get("explanation", ""),
        }
    except Exception as e:
        logger.exception("AI question error")
        raise HTTPException(status_code=500, detail=f"Erro ao gerar questão: {str(e)}")


# ============= LIVES REGEN =============
@api_router.post("/lives/refill")
async def refill_lives(user=Depends(get_current_user)):
    await db.users.update_one({"id": user["id"]}, {"$set": {"lives": 5}})
    return {"lives": 5}


# ============= HEALTH =============
@api_router.get("/")
async def root():
    return {"message": "REVISA API"}


# ============= SEED DATA =============
SUBJECTS_SEED = [
    {"name": "Matemática", "icon": "Calculator", "color": "#3B82F6", "description": "Funções, geometria, álgebra"},
    {"name": "Português", "icon": "BookOpen", "color": "#22C55E", "description": "Gramática e interpretação"},
    {"name": "História", "icon": "Landmark", "color": "#F97316", "description": "Brasil e mundo"},
    {"name": "Geografia", "icon": "Globe", "color": "#06B6D4", "description": "Física e humana"},
    {"name": "Biologia", "icon": "Leaf", "color": "#10B981", "description": "Vida e ecologia"},
    {"name": "Química", "icon": "FlaskConical", "color": "#8B5CF6", "description": "Orgânica e inorgânica"},
    {"name": "Física", "icon": "Atom", "color": "#EF4444", "description": "Mecânica e ondas"},
    {"name": "Literatura", "icon": "BookMarked", "color": "#EC4899", "description": "Movimentos literários"},
    {"name": "Inglês", "icon": "Languages", "color": "#EAB308", "description": "Reading e gramática"},
    {"name": "Redação", "icon": "PenLine", "color": "#64748B", "description": "Estrutura dissertativa"},
]

LESSONS_SEED = {
    "Matemática": [
        {"title": "Funções do 1º grau", "questions": [
            {"prompt": "Qual o valor de f(2) na função f(x) = 3x + 1?", "options": ["5", "6", "7", "8"], "correct_index": 2, "explanation": "f(2) = 3·2 + 1 = 7"},
            {"prompt": "A reta y = 2x − 4 intercepta o eixo X em qual ponto?", "options": ["(0, -4)", "(2, 0)", "(-2, 0)", "(4, 0)"], "correct_index": 1, "explanation": "Quando y = 0: 2x − 4 = 0 → x = 2"},
            {"prompt": "Qual o coeficiente angular da reta y = -3x + 5?", "options": ["5", "-3", "3", "-5"], "correct_index": 1, "explanation": "Na forma y = ax + b, a é o coeficiente angular"},
            {"prompt": "Se f(x) = 2x + 7, quanto vale f(0)?", "options": ["0", "2", "7", "9"], "correct_index": 2, "explanation": "f(0) = 2·0 + 7 = 7"},
            {"prompt": "Função crescente possui coeficiente angular:", "options": ["Negativo", "Zero", "Positivo", "Indefinido"], "correct_index": 2, "explanation": "Coeficiente angular > 0 indica crescimento"},
        ]},
        {"title": "Equações do 2º grau", "questions": [
            {"prompt": "As raízes de x² − 5x + 6 = 0 são:", "options": ["1 e 6", "2 e 3", "-2 e -3", "0 e 5"], "correct_index": 1, "explanation": "Por Bhaskara ou soma/produto: 2 e 3"},
            {"prompt": "Qual o discriminante de x² + 4x + 4 = 0?", "options": ["0", "4", "8", "16"], "correct_index": 0, "explanation": "Δ = b² − 4ac = 16 − 16 = 0"},
            {"prompt": "Quantas raízes reais tem x² + 1 = 0?", "options": ["0", "1", "2", "Infinitas"], "correct_index": 0, "explanation": "Δ = -4 < 0, não há raízes reais"},
            {"prompt": "Soma das raízes de x² − 7x + 10 = 0:", "options": ["7", "-7", "10", "3"], "correct_index": 0, "explanation": "Soma = -b/a = 7"},
            {"prompt": "Produto das raízes de x² − 2x − 8 = 0:", "options": ["-2", "8", "-8", "2"], "correct_index": 2, "explanation": "Produto = c/a = -8"},
        ]},
        {"title": "Geometria plana", "questions": [
            {"prompt": "A área de um quadrado de lado 5 é:", "options": ["10", "20", "25", "30"], "correct_index": 2, "explanation": "Área = lado² = 25"},
            {"prompt": "Soma dos ângulos internos de um triângulo:", "options": ["90°", "180°", "270°", "360°"], "correct_index": 1, "explanation": "Sempre 180°"},
            {"prompt": "Perímetro de retângulo 6×4 cm:", "options": ["10 cm", "20 cm", "24 cm", "12 cm"], "correct_index": 1, "explanation": "P = 2(6+4) = 20"},
            {"prompt": "Área do círculo de raio 3 (use π≈3,14):", "options": ["18,84", "28,26", "9,42", "6,28"], "correct_index": 1, "explanation": "A = πr² = 3,14·9 ≈ 28,26"},
            {"prompt": "Triângulo equilátero tem ângulos de:", "options": ["45°", "60°", "90°", "120°"], "correct_index": 1, "explanation": "Cada ângulo = 60°"},
        ]},
    ],
    "Português": [
        {"title": "Classes de palavras", "questions": [
            {"prompt": "Em 'O cachorro corre rápido', 'rápido' é:", "options": ["Substantivo", "Adjetivo", "Advérbio", "Verbo"], "correct_index": 2, "explanation": "Modifica o verbo 'corre' (modo)"},
            {"prompt": "A palavra 'felicidade' é um:", "options": ["Adjetivo", "Substantivo", "Verbo", "Pronome"], "correct_index": 1, "explanation": "Nomeia uma qualidade abstrata"},
            {"prompt": "'Eles vão à escola' — 'eles' é:", "options": ["Substantivo", "Pronome pessoal", "Adjetivo", "Numeral"], "correct_index": 1, "explanation": "Pronome pessoal do caso reto"},
            {"prompt": "Qual destas é uma conjunção?", "options": ["mas", "casa", "veloz", "três"], "correct_index": 0, "explanation": "Conjunção adversativa"},
            {"prompt": "'Bonito' é um(a):", "options": ["Substantivo", "Verbo", "Adjetivo", "Advérbio"], "correct_index": 2, "explanation": "Caracteriza um substantivo"},
        ]},
        {"title": "Crase", "questions": [
            {"prompt": "Marque a alternativa correta:", "options": ["Vou à escola", "Vou a escola", "Vou à a escola", "Vou as escola"], "correct_index": 0, "explanation": "Crase obrigatória antes de palavra feminina determinada"},
            {"prompt": "Quando NUNCA usamos crase?", "options": ["Antes de feminino", "Antes de verbo", "Antes de 'aquela'", "Em horas"], "correct_index": 1, "explanation": "Antes de verbo, nunca há crase"},
            {"prompt": "Está correto:", "options": ["Refiro-me à você", "Refiro-me a você", "Refiro-me às você", "Refiro-me a a você"], "correct_index": 1, "explanation": "Antes de pronome pessoal não há crase"},
            {"prompt": "Qual está com crase correta?", "options": ["Cheguei à Brasil", "Cheguei a Brasília", "Vou à Roma", "Daqui à pouco"], "correct_index": 1, "explanation": "Brasília aceita 'a' simples; locais sem artigo não recebem crase"},
            {"prompt": "Em 'Das 8 ___ 10h':", "options": ["a", "à", "ah", "há"], "correct_index": 1, "explanation": "Crase em horas determinadas"},
        ]},
    ],
    "História": [
        {"title": "Brasil Colônia", "questions": [
            {"prompt": "O Brasil foi descoberto em:", "options": ["1492", "1500", "1510", "1530"], "correct_index": 1, "explanation": "Pedro Álvares Cabral, 22 de abril de 1500"},
            {"prompt": "Capitanias hereditárias foram criadas por:", "options": ["D. João VI", "D. Pedro I", "D. João III", "Tomé de Sousa"], "correct_index": 2, "explanation": "Por D. João III em 1534"},
            {"prompt": "Principal produto da economia colonial inicial:", "options": ["Ouro", "Açúcar", "Café", "Borracha"], "correct_index": 1, "explanation": "Ciclo do açúcar no Nordeste"},
            {"prompt": "Inconfidência Mineira ocorreu em:", "options": ["1789", "1808", "1822", "1750"], "correct_index": 0, "explanation": "Movimento de 1789 contra a Coroa"},
            {"prompt": "Líder da Inconfidência Mineira:", "options": ["José Bonifácio", "Tiradentes", "D. Pedro II", "Zumbi"], "correct_index": 1, "explanation": "Joaquim José da Silva Xavier"},
        ]},
    ],
    "Geografia": [
        {"title": "Geografia do Brasil", "questions": [
            {"prompt": "Capital do Brasil:", "options": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador"], "correct_index": 2, "explanation": "Brasília, capital desde 1960"},
            {"prompt": "Maior bioma brasileiro:", "options": ["Cerrado", "Amazônia", "Caatinga", "Pantanal"], "correct_index": 1, "explanation": "Floresta Amazônica"},
            {"prompt": "Estado mais populoso do Brasil:", "options": ["RJ", "MG", "SP", "BA"], "correct_index": 2, "explanation": "São Paulo é o mais populoso"},
            {"prompt": "Rio mais extenso do Brasil:", "options": ["São Francisco", "Amazonas", "Paraná", "Tocantins"], "correct_index": 1, "explanation": "Rio Amazonas"},
            {"prompt": "Região com a Caatinga:", "options": ["Norte", "Nordeste", "Sul", "Sudeste"], "correct_index": 1, "explanation": "Bioma típico do sertão nordestino"},
        ]},
    ],
    "Biologia": [
        {"title": "Citologia", "questions": [
            {"prompt": "A 'usina de energia' da célula é:", "options": ["Núcleo", "Mitocôndria", "Ribossomo", "Lisossomo"], "correct_index": 1, "explanation": "Mitocôndrias produzem ATP"},
            {"prompt": "Onde ocorre a fotossíntese?", "options": ["Mitocôndria", "Cloroplasto", "Núcleo", "Vacúolo"], "correct_index": 1, "explanation": "Nos cloroplastos das células vegetais"},
            {"prompt": "Material genético está no:", "options": ["Citoplasma", "Núcleo", "Membrana", "Parede"], "correct_index": 1, "explanation": "DNA no núcleo (eucariotos)"},
            {"prompt": "Ribossomos produzem:", "options": ["Lipídios", "Proteínas", "ATP", "DNA"], "correct_index": 1, "explanation": "Síntese proteica"},
            {"prompt": "Célula vegetal tem, célula animal não:", "options": ["Mitocôndria", "Núcleo", "Parede celular", "Ribossomo"], "correct_index": 2, "explanation": "Parede celular de celulose"},
        ]},
    ],
    "Química": [
        {"title": "Tabela periódica", "questions": [
            {"prompt": "Símbolo do sódio:", "options": ["S", "So", "Na", "N"], "correct_index": 2, "explanation": "Na (do latim Natrium)"},
            {"prompt": "Número atômico do hidrogênio:", "options": ["0", "1", "2", "8"], "correct_index": 1, "explanation": "H tem Z=1"},
            {"prompt": "Gás nobre:", "options": ["O₂", "He", "Cl", "Na"], "correct_index": 1, "explanation": "Hélio é gás nobre"},
            {"prompt": "Família 1A são:", "options": ["Halogênios", "Metais alcalinos", "Gases nobres", "Calcogênios"], "correct_index": 1, "explanation": "Li, Na, K, Rb, Cs, Fr"},
            {"prompt": "Símbolo do ouro:", "options": ["Ag", "Au", "Or", "Go"], "correct_index": 1, "explanation": "Au (Aurum)"},
        ]},
    ],
    "Física": [
        {"title": "Cinemática", "questions": [
            {"prompt": "Velocidade média = ?", "options": ["d × t", "d / t", "t / d", "d + t"], "correct_index": 1, "explanation": "Vm = Δs / Δt"},
            {"prompt": "Unidade de velocidade no SI:", "options": ["km/h", "m/s", "cm/s", "mph"], "correct_index": 1, "explanation": "metros por segundo"},
            {"prompt": "Aceleração da gravidade ≈:", "options": ["5 m/s²", "9,8 m/s²", "20 m/s²", "100 m/s²"], "correct_index": 1, "explanation": "g ≈ 9,8 m/s²"},
            {"prompt": "MRU significa:", "options": ["Movimento Retilíneo Uniforme", "Movimento Rápido Único", "Massa Real Uniforme", "Maior Raio Útil"], "correct_index": 0, "explanation": "Velocidade constante"},
            {"prompt": "Em queda livre, desprezando o ar, todos os corpos:", "options": ["Caem com velocidades diferentes", "Caem com mesma aceleração", "Não caem", "Sobem"], "correct_index": 1, "explanation": "Aceleração g é a mesma"},
        ]},
    ],
    "Literatura": [
        {"title": "Movimentos literários", "questions": [
            {"prompt": "Machado de Assis pertence ao:", "options": ["Romantismo", "Realismo", "Modernismo", "Barroco"], "correct_index": 1, "explanation": "Mestre do Realismo brasileiro"},
            {"prompt": "Semana de Arte Moderna ocorreu em:", "options": ["1900", "1910", "1922", "1945"], "correct_index": 2, "explanation": "São Paulo, 1922"},
            {"prompt": "Autor de 'Os Sertões':", "options": ["Machado", "Euclides da Cunha", "Drummond", "Clarice"], "correct_index": 1, "explanation": "Euclides da Cunha (1902)"},
            {"prompt": "Iracema é obra de:", "options": ["José de Alencar", "Castro Alves", "Bilac", "Drummond"], "correct_index": 0, "explanation": "Romantismo indianista"},
            {"prompt": "Drummond foi:", "options": ["Romântico", "Modernista", "Barroco", "Árcade"], "correct_index": 1, "explanation": "Geração de 1930"},
        ]},
    ],
    "Inglês": [
        {"title": "Verb to be", "questions": [
            {"prompt": "I ___ a student.", "options": ["am", "is", "are", "be"], "correct_index": 0, "explanation": "I + am"},
            {"prompt": "She ___ happy.", "options": ["am", "is", "are", "be"], "correct_index": 1, "explanation": "She + is"},
            {"prompt": "They ___ from Brazil.", "options": ["am", "is", "are", "be"], "correct_index": 2, "explanation": "They + are"},
            {"prompt": "Past of 'is':", "options": ["was", "were", "been", "being"], "correct_index": 0, "explanation": "Singular passado: was"},
            {"prompt": "'You are' contraction:", "options": ["You's", "You're", "You're'", "Youre"], "correct_index": 1, "explanation": "you + are = you're"},
        ]},
    ],
    "Redação": [
        {"title": "Estrutura dissertativa", "questions": [
            {"prompt": "A estrutura básica de uma dissertação é:", "options": ["Início, fim", "Introdução, desenvolvimento, conclusão", "Tese, antítese", "Personagens, enredo"], "correct_index": 1, "explanation": "Modelo clássico"},
            {"prompt": "Tese é apresentada na:", "options": ["Conclusão", "Desenvolvimento", "Introdução", "Bibliografia"], "correct_index": 2, "explanation": "Posicionamento na introdução"},
            {"prompt": "ENEM exige proposta de intervenção em qual parte?", "options": ["Introdução", "Desenvolvimento", "Conclusão", "Título"], "correct_index": 2, "explanation": "Critério da Competência V"},
            {"prompt": "Tipo textual da redação ENEM:", "options": ["Narrativo", "Descritivo", "Dissertativo-argumentativo", "Injuntivo"], "correct_index": 2, "explanation": "Texto opinativo com argumentos"},
            {"prompt": "Conectivo de oposição:", "options": ["Portanto", "Entretanto", "Pois", "Assim"], "correct_index": 1, "explanation": "Adversativo"},
        ]},
    ],
}

ACHIEVEMENTS_SEED = [
    {"name": "Primeiro passo", "description": "Complete sua primeira lição", "icon": "Sparkles", "color": "#22C55E", "type": "lessons", "threshold": 1, "order": 1},
    {"name": "Aluno dedicado", "description": "Complete 5 lições", "icon": "BookOpen", "color": "#3B82F6", "type": "lessons", "threshold": 5, "order": 2},
    {"name": "Maratonista", "description": "Complete 15 lições", "icon": "Trophy", "color": "#EAB308", "type": "lessons", "threshold": 15, "order": 3},
    {"name": "Iniciando a chama", "description": "3 dias de ofensiva", "icon": "Flame", "color": "#F97316", "type": "streak", "threshold": 3, "order": 4},
    {"name": "Pegando fogo", "description": "7 dias de ofensiva", "icon": "Flame", "color": "#EF4444", "type": "streak", "threshold": 7, "order": 5},
    {"name": "100 XP", "description": "Acumule 100 de XP", "icon": "Zap", "color": "#EAB308", "type": "xp", "threshold": 100, "order": 6},
    {"name": "500 XP", "description": "Acumule 500 de XP", "icon": "Star", "color": "#8B5CF6", "type": "xp", "threshold": 500, "order": 7},
    {"name": "Perfeição", "description": "Complete uma lição sem erros", "icon": "Award", "color": "#22C55E", "type": "perfect", "threshold": 1, "order": 8},
]


@app.on_event("startup")
async def seed_database():
    if await db.subjects.count_documents({}) == 0:
        for i, sub in enumerate(SUBJECTS_SEED):
            sub_id = str(uuid.uuid4())
            await db.subjects.insert_one({"id": sub_id, "order": i, **sub})
            for j, lesson in enumerate(LESSONS_SEED.get(sub["name"], [])):
                lesson_id = str(uuid.uuid4())
                await db.lessons.insert_one({
                    "id": lesson_id, "subject_id": sub_id, "subject_name": sub["name"],
                    "title": lesson["title"], "order": j,
                })
                for k, q in enumerate(lesson["questions"]):
                    await db.questions.insert_one({
                        "id": str(uuid.uuid4()), "lesson_id": lesson_id,
                        "order": k, **q,
                    })
    if await db.achievements.count_documents({}) == 0:
        for ach in ACHIEVEMENTS_SEED:
            await db.achievements.insert_one({"id": str(uuid.uuid4()), **ach})


app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
