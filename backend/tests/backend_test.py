"""REVISA backend regression tests."""
import os
import uuid
import pytest
import requests

BASE_URL = os.environ.get("REACT_APP_BACKEND_URL", "https://exam-drill-4.preview.emergentagent.com").rstrip("/")
API = f"{BASE_URL}/api"


@pytest.fixture(scope="session")
def session():
    s = requests.Session()
    s.headers.update({"Content-Type": "application/json"})
    return s


@pytest.fixture(scope="session")
def test_user(session):
    """Register a new test user for isolated tests."""
    email = f"test_{uuid.uuid4().hex[:8]}@revisa.com"
    password = "Test@12345"
    r = session.post(f"{API}/auth/register", json={"name": "Tester", "email": email, "password": password})
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


# ---------- Auth ----------
def test_register_duplicate(session, test_user):
    r = session.post(f"{API}/auth/register", json={
        "name": "Dup", "email": test_user["email"], "password": "whatever123"})
    assert r.status_code == 400


def test_login_success(session, test_user):
    r = session.post(f"{API}/auth/login", json={"email": test_user["email"], "password": test_user["password"]})
    assert r.status_code == 200
    assert "token" in r.json() and r.json()["user"]["email"] == test_user["email"]


def test_login_wrong_password(session, test_user):
    r = session.post(f"{API}/auth/login", json={"email": test_user["email"], "password": "wrong"})
    assert r.status_code == 401


def test_auth_me(session, auth_headers, test_user):
    r = session.get(f"{API}/auth/me", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert data["email"] == test_user["email"]
    assert data["lives"] == 5 and data["xp"] == 0


def test_auth_me_invalid_token(session):
    r = session.get(f"{API}/auth/me", headers={"Authorization": "Bearer garbage"})
    assert r.status_code == 401


# ---------- Subjects ----------
def test_list_subjects(session, auth_headers):
    r = session.get(f"{API}/subjects", headers=auth_headers)
    assert r.status_code == 200
    subjects = r.json()
    assert len(subjects) == 10
    s0 = subjects[0]
    for k in ["id", "name", "total_lessons", "completed_lessons", "progress"]:
        assert k in s0


def test_subject_lessons(session, auth_headers):
    subs = session.get(f"{API}/subjects", headers=auth_headers).json()
    # pick a subject with lessons seeded (Matemática)
    mat = next(s for s in subs if s["name"] == "Matemática")
    r = session.get(f"{API}/subjects/{mat['id']}/lessons", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert "subject" in data and "lessons" in data
    lessons = data["lessons"]
    assert len(lessons) >= 1
    assert lessons[0]["unlocked"] is True
    if len(lessons) > 1:
        assert lessons[1]["unlocked"] is False


def test_get_lesson_with_questions(session, auth_headers):
    subs = session.get(f"{API}/subjects", headers=auth_headers).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    lessons = session.get(f"{API}/subjects/{mat['id']}/lessons", headers=auth_headers).json()["lessons"]
    r = session.get(f"{API}/lessons/{lessons[0]['id']}", headers=auth_headers)
    assert r.status_code == 200
    data = r.json()
    assert len(data["questions"]) >= 3
    q = data["questions"][0]
    for k in ["id", "prompt", "options", "correct_index", "explanation"]:
        assert k in q


# ---------- Complete lesson & progression ----------
def test_complete_lesson_all_correct(session, auth_headers):
    subs = session.get(f"{API}/subjects", headers=auth_headers).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    lessons = session.get(f"{API}/subjects/{mat['id']}/lessons", headers=auth_headers).json()["lessons"]
    lesson_id = lessons[0]["id"]
    qs = session.get(f"{API}/lessons/{lesson_id}", headers=auth_headers).json()["questions"]
    answers = [{"question_id": q["id"], "selected_index": q["correct_index"]} for q in qs]
    r = session.post(f"{API}/lessons/complete", headers=auth_headers,
                     json={"lesson_id": lesson_id, "answers": answers})
    assert r.status_code == 200
    res = r.json()
    assert res["correct"] == len(qs)
    assert res["perfect"] is True
    assert res["xp_earned"] == len(qs) * 10 + 5
    assert res["new_streak"] >= 1
    ach_names = [a["name"] for a in res["new_achievements"]]
    assert "Primeiro passo" in ach_names
    assert "Perfeição" in ach_names


def test_complete_lesson_wrong_deducts_lives(session):
    # new isolated user
    email = f"wrong_{uuid.uuid4().hex[:8]}@revisa.com"
    reg = session.post(f"{API}/auth/register", json={"name": "W", "email": email, "password": "Test@12345"}).json()
    token = reg["token"]
    h = {"Authorization": f"Bearer {token}"}
    subs = session.get(f"{API}/subjects", headers=h).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    lessons = session.get(f"{API}/subjects/{mat['id']}/lessons", headers=h).json()["lessons"]
    qs = session.get(f"{API}/lessons/{lessons[0]['id']}", headers=h).json()["questions"]
    # pick wrong answers
    answers = [{"question_id": q["id"], "selected_index": (q["correct_index"] + 1) % len(q["options"])} for q in qs]
    r = session.post(f"{API}/lessons/complete", headers=h,
                     json={"lesson_id": lessons[0]["id"], "answers": answers})
    assert r.status_code == 200
    res = r.json()
    assert res["wrong"] == len(qs)
    assert res["new_lives"] < 5


# ---------- Achievements ----------
def test_list_achievements(session, auth_headers):
    r = session.get(f"{API}/achievements", headers=auth_headers)
    assert r.status_code == 200
    achs = r.json()
    assert len(achs) == 8
    assert all("unlocked" in a for a in achs)
    # After completing lesson perfectly, 'Primeiro passo' and 'Perfeição' should be unlocked
    unlocked = [a["name"] for a in achs if a["unlocked"]]
    assert "Primeiro passo" in unlocked


# ---------- Leaderboard ----------
def test_leaderboard(session, auth_headers, test_user):
    r = session.get(f"{API}/leaderboard", headers=auth_headers)
    assert r.status_code == 200
    users = r.json()
    assert len(users) >= 1
    # sorted by xp desc
    xps = [u["xp"] for u in users]
    assert xps == sorted(xps, reverse=True)
    me = [u for u in users if u.get("is_me")]
    assert len(me) == 1
    assert me[0]["rank"] >= 1


# ---------- Lives refill ----------
def test_lives_refill(session, auth_headers):
    r = session.post(f"{API}/lives/refill", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["lives"] == 5
    me = session.get(f"{API}/auth/me", headers=auth_headers).json()
    assert me["lives"] == 5


# ---------- AI Practice (real LLM call) ----------
def test_ai_practice_question(session, auth_headers):
    r = session.post(f"{API}/practice/ai", headers=auth_headers,
                     json={"subject": "Matemática", "difficulty": "medio"}, timeout=60)
    assert r.status_code == 200, r.text
    data = r.json()
    for k in ["id", "prompt", "options", "correct_index", "explanation"]:
        assert k in data
    assert isinstance(data["options"], list) and len(data["options"]) >= 2
    assert 0 <= data["correct_index"] < len(data["options"])
