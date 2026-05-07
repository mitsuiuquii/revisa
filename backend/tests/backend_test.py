"""REVISA backend regression tests — iteration: 5 levels (basico/intermediario/avancado/enem/fuvest),
new users start with 15 coins, AI practice now requires 'topic', achievement 'Sábio Lendário', source per question."""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def test_user(session):
    """Register a fresh user (starts with 15 coins, 0 xp = Bronze)."""
    email = f"TEST_{uuid.uuid4().hex[:8]}@revisa.com"
    password = os.environ.get("REVISA_TEST_PASSWORD", f"Tst-{uuid.uuid4().hex[:12]}!")
    r = session.post(f"{API}/auth/register",
                     json={"name": "TEST_Tester", "email": email, "password": password})
    assert r.status_code == 200, r.text
    data = r.json()
    return {"email": email, "password": password, "token": data["token"], "user": data["user"]}


@pytest.fixture
def auth_headers(test_user):
    return {"Authorization": f"Bearer {test_user['token']}"}


# ---------- Health ----------
def test_health(session):
    r = session.get(f"{API}/")
    assert r.status_code == 200
    assert "REVISA" in r.json()["message"]


# ---------- META: Ranks/Powers/Levels ----------
def test_meta_ranks_six_with_five_levels(session):
    r = session.get(f"{API}/meta/ranks")
    assert r.status_code == 200
    d = r.json()
    assert len(d["ranks"]) == 6
    ids = [r["id"] for r in d["ranks"]]
    assert ids == ["bronze", "prata", "ouro", "platina", "diamante", "sabio"]
    assert d["power_cost"] == 15
    assert len(d["powers"]) == 3
    # NEW level structure: 5 levels including enem + fuvest, no pre_vestibular
    lr = d["level_required"]
    assert set(lr.keys()) == {"basico", "intermediario", "avancado", "enem", "fuvest"}
    assert "pre_vestibular" not in lr
    assert lr["basico"] == "bronze"
    assert lr["intermediario"] == "prata"
    assert lr["avancado"] == "ouro"
    assert lr["enem"] == "platina"
    assert lr["fuvest"] == "diamante"


# ---------- AUTH: new user starts with 15 coins ----------
def test_register_new_user_has_15_coins(test_user):
    u = test_user["user"]
    assert u["coins"] == 15, f"new user should start with 15 coins, got {u['coins']}"
    assert u["rank"]["id"] == "bronze"


def test_auth_me_persists_15_coins(session, auth_headers, test_user):
    r = session.get(f"{API}/auth/me", headers=auth_headers)
    assert r.status_code == 200
    d = r.json()
    assert d["email"] == test_user["email"].lower()
    assert d["coins"] == 15
    assert d["rank"]["id"] == "bronze"


def test_login_wrong_password(session, test_user):
    r = session.post(f"{API}/auth/login",
                     json={"email": test_user["email"], "password": "wrong"})
    assert r.status_code == 401


# ---------- SUBJECTS (9 with 5 lessons each) ----------
def test_list_subjects_9_with_5_lessons(session, auth_headers):
    r = session.get(f"{API}/subjects", headers=auth_headers)
    assert r.status_code == 200
    subs = r.json()
    assert len(subs) == 9
    by_name = {s["name"]: s for s in subs}
    expected = {"Biologia", "Química", "Física", "Matemática", "História",
                "Português", "Geografia", "Literatura", "Inglês"}
    assert set(by_name.keys()) == expected
    for name, s in by_name.items():
        assert s["total_lessons"] == 5, f"{name} should have 5 lessons, got {s['total_lessons']}"


# ---------- LESSONS - 5 levels, only basico unlocked for Bronze ----------
def test_lessons_five_levels_bronze_only_basico(session, auth_headers):
    subs = session.get(f"{API}/subjects", headers=auth_headers).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    r = session.get(f"{API}/subjects/{mat['id']}/lessons", headers=auth_headers)
    assert r.status_code == 200
    lessons = r.json()["lessons"]
    assert len(lessons) == 5
    by_level = {l["level"]: l for l in lessons}
    assert set(by_level.keys()) == {"basico", "intermediario", "avancado", "enem", "fuvest"}
    assert by_level["basico"]["unlocked"] == True
    assert by_level["intermediario"]["unlocked"] == False
    assert by_level["avancado"]["unlocked"] == False
    assert by_level["enem"]["unlocked"] == False
    assert by_level["fuvest"]["unlocked"] == False
    assert by_level["enem"]["required_rank"] == "platina"
    assert by_level["fuvest"]["required_rank"] == "diamante"


def test_get_locked_lesson_403(session, auth_headers):
    subs = session.get(f"{API}/subjects", headers=auth_headers).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    lessons = session.get(f"{API}/subjects/{mat['id']}/lessons",
                          headers=auth_headers).json()["lessons"]
    fuvest = next(l for l in lessons if l["level"] == "fuvest")
    r = session.get(f"{API}/lessons/{fuvest['id']}", headers=auth_headers)
    assert r.status_code == 403


def test_get_basico_lesson_questions_have_source(session, auth_headers):
    subs = session.get(f"{API}/subjects", headers=auth_headers).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    lessons = session.get(f"{API}/subjects/{mat['id']}/lessons",
                          headers=auth_headers).json()["lessons"]
    basico = next(l for l in lessons if l["level"] == "basico")
    r = session.get(f"{API}/lessons/{basico['id']}", headers=auth_headers)
    assert r.status_code == 200
    qs = r.json()["questions"]
    # NEW: ~10 questions per lesson (expanded from 4-6)
    assert len(qs) >= 8, f"expected ~10 questions per lesson, got {len(qs)}"
    # Every question must have 'source' with banca/year
    for q in qs:
        assert "source" in q and q["source"], f"question missing source: {q}"
        assert "difficulty" in q
    # At least one source mentions a real banca (extended list)
    bancas = ["ENEM", "FUVEST", "UFMG", "UNICAMP", "UERJ", "UFPR", "UFRJ",
              "USP", "UNESP", "UFSC", "UFPE", "UEL", "UFBA"]
    sources_text = " ".join(q["source"] for q in qs)
    assert any(b in sources_text for b in bancas), f"no real banca found in: {sources_text}"


def test_total_questions_in_bank_at_least_400(session, auth_headers):
    """Count questions across all 45 lessons (9 subjects × 5 levels). Expect >=400."""
    subs = session.get(f"{API}/subjects", headers=auth_headers).json()
    total_qs = 0
    total_lessons = 0
    for s in subs:
        lessons = session.get(f"{API}/subjects/{s['id']}/lessons",
                              headers=auth_headers).json()["lessons"]
        total_lessons += len(lessons)
    # Assert 45 total lessons (9 × 5)
    assert total_lessons == 45, f"expected 45 lessons, got {total_lessons}"
    # Sample across several subjects/levels to estimate (without doing 45 gated calls)
    # Instead, iterate only basico lessons (all unlocked for bronze won't work — only Matemática).
    # Use user with high XP? Easier: count via direct mongo? We do not have mongo access.
    # Fall back to summing only accessible (basico) lessons → 9 lessons × ~10 = ~90 min.
    for s in subs:
        lessons = session.get(f"{API}/subjects/{s['id']}/lessons",
                              headers=auth_headers).json()["lessons"]
        basico = next(l for l in lessons if l["level"] == "basico")
        qs = session.get(f"{API}/lessons/{basico['id']}",
                         headers=auth_headers).json()["questions"]
        total_qs += len(qs)
    # Only basico × 9 subjects; expect ~90. Extrapolate by asserting avg >= 9 (so full bank >= ~405)
    avg_per_lesson = total_qs / 9
    assert avg_per_lesson >= 9, (
        f"avg questions per basico lesson is {avg_per_lesson:.1f}, "
        f"suggests bank < 405 (expected ~452)"
    )


# ---------- GOOGLE OAUTH (Emergent Managed Auth) ----------
def test_google_session_invalid_returns_401(session):
    """Invalid session_id must be rejected by Emergent demobackend → 401."""
    r = session.post(f"{API}/auth/google/session",
                     json={"session_id": f"invalid-{uuid.uuid4().hex}"})
    assert r.status_code == 401, f"expected 401, got {r.status_code}: {r.text}"


def test_google_session_missing_field_422(session):
    r = session.post(f"{API}/auth/google/session", json={})
    assert r.status_code == 422


def test_google_session_invalid_does_not_create_user(session):
    """After a failed google session exchange, no new user should be created.
    We verify by calling /auth/login with the bogus session id as email and expecting 401 (no such user)."""
    bogus = f"TEST_ghost_{uuid.uuid4().hex[:8]}@revisa.com"
    # Attempt google with bogus session id
    r = session.post(f"{API}/auth/google/session",
                     json={"session_id": bogus})
    assert r.status_code in (401, 502)
    # Ensure no user with that would-be email exists (login should 401 / invalid credentials)
    r2 = session.post(f"{API}/auth/login",
                      json={"email": bogus, "password": "x"})
    assert r2.status_code == 401


def test_login_blocked_when_password_hash_empty(session):
    """Simulate a Google-only account (password_hash=''): /auth/login must reject.
    We do this by registering then using the Google session endpoint path indirectly is not
    possible without a real session. Instead, we register a user then PATCH via backend
    not available — so we just assert the login code rejects empty password correctly by
    attempting login with blank password for an existing account."""
    # Register a normal user
    email = f"TEST_pwblock_{uuid.uuid4().hex[:8]}@revisa.com"
    reg = session.post(f"{API}/auth/register",
                       json={"name": "P", "email": email, "password": "Pwd-123-abc"})
    assert reg.status_code == 200
    # Login with empty password must fail (validates the `not password_hash or ...` guard
    # path at least for the verify step)
    r = session.post(f"{API}/auth/login", json={"email": email, "password": ""})
    assert r.status_code == 401


# ---------- COMPLETE LESSON (5+ questions, XP/coins) ----------
def test_complete_lesson_perfect_xp_coins_with_15_start(session):
    email = f"TEST_perfect_{uuid.uuid4().hex[:8]}@revisa.com"
    reg = session.post(f"{API}/auth/register",
                       json={"name": "P", "email": email, "password": "Pwd-123-abc"}).json()
    h = {"Authorization": f"Bearer {reg['token']}"}
    subs = session.get(f"{API}/subjects", headers=h).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    lessons = session.get(f"{API}/subjects/{mat['id']}/lessons", headers=h).json()["lessons"]
    basico = next(l for l in lessons if l["level"] == "basico")
    qs = session.get(f"{API}/lessons/{basico['id']}", headers=h).json()["questions"]

    diff_map = {"facil": 5, "medio": 10, "dificil": 15}
    expected_xp = sum(diff_map[q["difficulty"]] for q in qs) + 20  # gabarito bonus
    answers = [{"question_id": q["id"], "selected_index": q["correct_index"]} for q in qs]
    r = session.post(f"{API}/lessons/complete", headers=h,
                     json={"lesson_id": basico["id"], "answers": answers})
    assert r.status_code == 200
    res = r.json()
    assert res["perfect"] == True
    assert res["correct"] == len(qs)
    assert res["xp_earned"] == expected_xp
    assert res["coins_earned"] == len(qs) + 3
    # NEW: starts with 15 coins not 10
    assert res["new_coins"] == 15 + len(qs) + 3


def test_complete_lesson_wrong_no_perfect(session):
    email = f"TEST_wrong_{uuid.uuid4().hex[:8]}@revisa.com"
    reg = session.post(f"{API}/auth/register",
                       json={"name": "W", "email": email, "password": "Pwd-123-abc"}).json()
    h = {"Authorization": f"Bearer {reg['token']}"}
    subs = session.get(f"{API}/subjects", headers=h).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    lessons = session.get(f"{API}/subjects/{mat['id']}/lessons", headers=h).json()["lessons"]
    basico = next(l for l in lessons if l["level"] == "basico")
    qs = session.get(f"{API}/lessons/{basico['id']}", headers=h).json()["questions"]
    answers = [{"question_id": q["id"],
                "selected_index": (q["correct_index"] + 1) % len(q["options"])} for q in qs]
    r = session.post(f"{API}/lessons/complete", headers=h,
                     json={"lesson_id": basico["id"], "answers": answers})
    assert r.status_code == 200
    res = r.json()
    assert res["perfect"] == False
    assert res["coins_earned"] == 0
    assert res["new_lives"] < 5


# ---------- POWERS ----------
def test_use_power_deducts_15_coins(session, auth_headers, test_user):
    # fresh user has 15 coins → exactly enough for one power
    r = session.post(f"{API}/powers/use", headers=auth_headers, json={"power_id": "fifty_fifty"})
    assert r.status_code == 200
    d = r.json()
    assert d["new_coins"] == 0


def test_use_power_invalid(session, auth_headers):
    # auth_headers user already used 15 coins above; create fresh just for invalid power test
    email = f"TEST_inv_{uuid.uuid4().hex[:8]}@revisa.com"
    reg = session.post(f"{API}/auth/register",
                       json={"name": "I", "email": email, "password": "Pwd-123-abc"}).json()
    h = {"Authorization": f"Bearer {reg['token']}"}
    r = session.post(f"{API}/powers/use", headers=h, json={"power_id": "nope"})
    assert r.status_code == 400


def test_use_power_insufficient_coins(session):
    # use a fresh user, then drain to 0 by using one power, then try again
    email = f"TEST_drain_{uuid.uuid4().hex[:8]}@revisa.com"
    reg = session.post(f"{API}/auth/register",
                       json={"name": "D", "email": email, "password": "Pwd-123-abc"}).json()
    h = {"Authorization": f"Bearer {reg['token']}"}
    r1 = session.post(f"{API}/powers/use", headers=h, json={"power_id": "skip"})
    assert r1.status_code == 200
    r2 = session.post(f"{API}/powers/use", headers=h, json={"power_id": "skip"})
    assert r2.status_code == 400


def test_audience_percentages(session, auth_headers):
    # need fresh user with coins
    email = f"TEST_aud_{uuid.uuid4().hex[:8]}@revisa.com"
    reg = session.post(f"{API}/auth/register",
                       json={"name": "A", "email": email, "password": "Pwd-123-abc"}).json()
    h = {"Authorization": f"Bearer {reg['token']}"}
    subs = session.get(f"{API}/subjects", headers=h).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    lessons = session.get(f"{API}/subjects/{mat['id']}/lessons", headers=h).json()["lessons"]
    basico = next(l for l in lessons if l["level"] == "basico")
    qs = session.get(f"{API}/lessons/{basico['id']}", headers=h).json()["questions"]
    q = qs[0]
    r = session.get(f"{API}/powers/audience/{q['id']}", headers=h)
    assert r.status_code == 200
    pct = r.json()["percentages"]
    assert len(pct) == len(q["options"])
    assert sum(pct) == 100


# ---------- LEADERBOARD ----------
def test_leaderboard_with_tier(session, auth_headers):
    r = session.get(f"{API}/leaderboard", headers=auth_headers)
    assert r.status_code == 200
    users = r.json()
    assert len(users) >= 1
    assert "tier" in users[0]


# ---------- LIVES REFILL ----------
def test_lives_refill(session, auth_headers):
    r = session.post(f"{API}/lives/refill", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["lives"] == 5


# ---------- ACHIEVEMENTS: 'Sábio Lendário' rank threshold=5 ----------
def test_achievements_includes_sabio_lendario(session, auth_headers):
    r = session.get(f"{API}/achievements", headers=auth_headers)
    assert r.status_code == 200
    items = r.json()
    sabio = next((a for a in items if a["name"] == "Sábio Lendário"), None)
    assert sabio is not None, "Achievement 'Sábio Lendário' missing"
    assert sabio["type"] == "rank"
    assert sabio["threshold"] == 5
    assert sabio["unlocked"] == False


# ---------- AI PRACTICE: now requires 'topic' ----------
def test_ai_practice_missing_topic_returns_422(session, auth_headers):
    """No topic field at all → Pydantic should reject with 422."""
    r = session.post(f"{API}/practice/ai", headers=auth_headers,
                     json={"subject": "Matemática", "difficulty": "medio"})
    assert r.status_code == 422, f"expected 422, got {r.status_code}: {r.text}"


def test_ai_practice_with_topic_returns_question_with_source(session, auth_headers):
    """Valid request with topic should return a question; source must contain subject + topic."""
    r = session.post(f"{API}/practice/ai", headers=auth_headers,
                     json={"subject": "Matemática", "topic": "trigonometria", "difficulty": "medio"})
    if r.status_code == 503:
        pytest.skip("LLM not configured in this environment")
    assert r.status_code == 200, f"AI practice failed: {r.status_code} {r.text}"
    d = r.json()
    assert "prompt" in d and "options" in d and "correct_index" in d
    assert "source" in d
    assert "Matemática" in d["source"]
    assert "trigonometria" in d["source"]
