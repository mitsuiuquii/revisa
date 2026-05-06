"""REVISA backend regression tests - covers new ranks/coins/powers features."""
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
    """Register a fresh user (starts with 10 coins, 0 xp = Bronze)."""
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


# ---------- META: Ranks/Powers ----------
def test_meta_ranks(session):
    r = session.get(f"{API}/meta/ranks")
    assert r.status_code == 200
    d = r.json()
    assert len(d["ranks"]) == 6
    ids = [r["id"] for r in d["ranks"]]
    assert ids == ["bronze", "prata", "ouro", "platina", "diamante", "sabio"]
    # min_xp progression
    xps = [r["min_xp"] for r in d["ranks"]]
    assert xps == sorted(xps)
    assert xps[0] == 0 and xps[1] == 200
    # powers
    assert len(d["powers"]) == 3
    assert d["power_cost"] == 15
    pids = [p["id"] for p in d["powers"]]
    assert set(pids) == {"fifty_fifty", "skip", "audience"}
    # level_required mapping
    assert d["level_required"]["basico"] == "bronze"
    assert d["level_required"]["intermediario"] == "prata"
    assert d["level_required"]["avancado"] == "ouro"
    assert d["level_required"]["pre_vestibular"] == "platina"


# ---------- AUTH ----------
def test_register_returns_new_fields(test_user):
    u = test_user["user"]
    assert u["coins"] == 10
    assert u["rank"]["id"] == "bronze"
    assert u["rank"]["min_xp"] == 0
    assert u["rank"]["color"] == "#A16207"


def test_auth_me(session, auth_headers, test_user):
    r = session.get(f"{API}/auth/me", headers=auth_headers)
    assert r.status_code == 200
    d = r.json()
    assert d["email"] == test_user["email"].lower()
    assert "coins" in d and "rank" in d
    assert d["rank"]["id"] == "bronze"


def test_login_wrong_password(session, test_user):
    r = session.post(f"{API}/auth/login",
                     json={"email": test_user["email"], "password": "wrong"})
    assert r.status_code == 401


# ---------- SUBJECTS (9 with correct colors) ----------
def test_list_subjects_9_with_colors(session, auth_headers):
    r = session.get(f"{API}/subjects", headers=auth_headers)
    assert r.status_code == 200
    subs = r.json()
    assert len(subs) == 9
    by_name = {s["name"]: s for s in subs}
    expected_colors = {
        "Biologia": "#86EFAC",
        "Química": "#84CC16",
        "Física": "#1E40AF",
        "Matemática": "#3B82F6",
        "História": "#EF4444",
        "Português": "#F97316",
        "Geografia": "#A855F7",
        "Literatura": "#EC4899",
        "Inglês": "#FACC15",
    }
    for name, color in expected_colors.items():
        assert name in by_name, f"missing {name}"
        assert by_name[name]["color"] == color, f"{name} color mismatch"
        assert by_name[name]["total_lessons"] == 4, f"{name} should have 4 lessons"


# ---------- LESSONS - Locking by rank ----------
def test_lessons_bronze_only_basico_unlocked(session, auth_headers):
    subs = session.get(f"{API}/subjects", headers=auth_headers).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    r = session.get(f"{API}/subjects/{mat['id']}/lessons", headers=auth_headers)
    assert r.status_code == 200
    lessons = r.json()["lessons"]
    assert len(lessons) == 4
    # Bronze: only basico level should be unlocked (first lesson of basico)
    by_level = {l["level"]: l for l in lessons}
    assert by_level["basico"]["unlocked"] == True
    assert by_level["intermediario"]["unlocked"] == False
    assert by_level["avancado"]["unlocked"] == False
    assert by_level["pre_vestibular"]["unlocked"] == False
    # level_label and required_rank
    assert by_level["intermediario"]["required_rank"] == "prata"
    assert "Intermediário" in by_level["intermediario"]["level_label"]


def test_get_locked_lesson_403(session, auth_headers):
    subs = session.get(f"{API}/subjects", headers=auth_headers).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    lessons = session.get(f"{API}/subjects/{mat['id']}/lessons",
                         headers=auth_headers).json()["lessons"]
    inter = next(l for l in lessons if l["level"] == "intermediario")
    r = session.get(f"{API}/lessons/{inter['id']}", headers=auth_headers)
    assert r.status_code == 403


def test_get_basico_lesson_with_questions(session, auth_headers):
    subs = session.get(f"{API}/subjects", headers=auth_headers).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    lessons = session.get(f"{API}/subjects/{mat['id']}/lessons",
                         headers=auth_headers).json()["lessons"]
    basico = next(l for l in lessons if l["level"] == "basico")
    r = session.get(f"{API}/lessons/{basico['id']}", headers=auth_headers)
    assert r.status_code == 200
    qs = r.json()["questions"]
    assert len(qs) >= 3
    assert all("difficulty" in q for q in qs)


# ---------- COMPLETE LESSON: XP per difficulty + bonus + coins ----------
def test_complete_lesson_perfect_xp_coins(session):
    # fresh user
    email = f"TEST_perfect_{uuid.uuid4().hex[:8]}@revisa.com"
    reg = session.post(f"{API}/auth/register",
                       json={"name": "P", "email": email, "password": "Pwd-123-abc"}).json()
    h = {"Authorization": f"Bearer {reg['token']}"}
    subs = session.get(f"{API}/subjects", headers=h).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    lessons = session.get(f"{API}/subjects/{mat['id']}/lessons", headers=h).json()["lessons"]
    basico = next(l for l in lessons if l["level"] == "basico")
    qs = session.get(f"{API}/lessons/{basico['id']}", headers=h).json()["questions"]

    # compute expected: facil=5, medio=10, dificil=15 + 20 (gabarito)
    diff_map = {"facil": 5, "medio": 10, "dificil": 15}
    expected_xp = sum(diff_map[q["difficulty"]] for q in qs) + 20
    answers = [{"question_id": q["id"], "selected_index": q["correct_index"]} for q in qs]
    r = session.post(f"{API}/lessons/complete", headers=h,
                     json={"lesson_id": basico["id"], "answers": answers})
    assert r.status_code == 200
    res = r.json()
    assert res["perfect"] == True
    assert res["correct"] == len(qs)
    assert res["xp_earned"] == expected_xp, f"xp {res['xp_earned']} vs expected {expected_xp}"
    # coins: 1 per correct + 3 perfect bonus
    assert res["coins_earned"] == len(qs) + 3
    assert res["new_coins"] == 10 + len(qs) + 3


def test_complete_lesson_wrong_deducts_lives_no_perfect_bonus(session):
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
    assert res["wrong"] == len(qs)
    assert res["new_lives"] < 5
    assert res["coins_earned"] == 0  # 0 correct, no bonus


def test_rank_up_bronze_to_prata(session):
    """User completes enough lessons to cross 200 XP -> rank up."""
    email = f"TEST_rankup_{uuid.uuid4().hex[:8]}@revisa.com"
    reg = session.post(f"{API}/auth/register",
                       json={"name": "R", "email": email, "password": "Pwd-123-abc"}).json()
    h = {"Authorization": f"Bearer {reg['token']}"}
    subs = session.get(f"{API}/subjects", headers=h).json()
    rank_up_seen = False
    total_xp = 0
    # iterate subjects -> basico lesson -> answer perfect, accumulate XP
    for s in subs:
        if total_xp >= 250:
            break
        lessons = session.get(f"{API}/subjects/{s['id']}/lessons", headers=h).json()["lessons"]
        basico = next((l for l in lessons if l["level"] == "basico"), None)
        if not basico:
            continue
        qs = session.get(f"{API}/lessons/{basico['id']}", headers=h).json()["questions"]
        answers = [{"question_id": q["id"], "selected_index": q["correct_index"]} for q in qs]
        r = session.post(f"{API}/lessons/complete", headers=h,
                         json={"lesson_id": basico["id"], "answers": answers})
        assert r.status_code == 200
        res = r.json()
        total_xp = res["new_xp"]
        if res.get("rank_up"):
            rank_up_seen = True
            assert res["new_rank"]["id"] == "prata"
            assert res["old_rank"]["id"] == "bronze"
            break
    assert rank_up_seen, f"No rank up after accumulating {total_xp} XP"


# ---------- POWERS ----------
def test_use_power_deducts_coins(session, auth_headers, test_user):
    # ensure user has >= 15 coins (fresh user has 10) - register fresh user with 10 coins is too few
    # so use a user that completed a lesson first
    email = f"TEST_power_{uuid.uuid4().hex[:8]}@revisa.com"
    reg = session.post(f"{API}/auth/register",
                       json={"name": "PW", "email": email, "password": "Pwd-123-abc"}).json()
    h = {"Authorization": f"Bearer {reg['token']}"}
    # complete one perfect lesson to gain coins (4 + 3 = 7 -> total 17)
    subs = session.get(f"{API}/subjects", headers=h).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    lessons = session.get(f"{API}/subjects/{mat['id']}/lessons", headers=h).json()["lessons"]
    basico = next(l for l in lessons if l["level"] == "basico")
    qs = session.get(f"{API}/lessons/{basico['id']}", headers=h).json()["questions"]
    answers = [{"question_id": q["id"], "selected_index": q["correct_index"]} for q in qs]
    res = session.post(f"{API}/lessons/complete", headers=h,
                       json={"lesson_id": basico["id"], "answers": answers}).json()
    assert res["new_coins"] >= 15

    # use a power
    r = session.post(f"{API}/powers/use", headers=h, json={"power_id": "fifty_fifty"})
    assert r.status_code == 200
    d = r.json()
    assert d["new_coins"] == res["new_coins"] - 15


def test_use_power_invalid(session, auth_headers):
    r = session.post(f"{API}/powers/use", headers=auth_headers, json={"power_id": "nope"})
    assert r.status_code == 400


def test_use_power_insufficient_coins(session, auth_headers):
    # fresh user has 10 coins < 15
    r = session.post(f"{API}/powers/use", headers=auth_headers, json={"power_id": "skip"})
    assert r.status_code == 400


def test_audience_percentages(session, auth_headers):
    subs = session.get(f"{API}/subjects", headers=auth_headers).json()
    mat = next(s for s in subs if s["name"] == "Matemática")
    lessons = session.get(f"{API}/subjects/{mat['id']}/lessons",
                         headers=auth_headers).json()["lessons"]
    basico = next(l for l in lessons if l["level"] == "basico")
    qs = session.get(f"{API}/lessons/{basico['id']}", headers=auth_headers).json()["questions"]
    q = qs[0]
    r = session.get(f"{API}/powers/audience/{q['id']}", headers=auth_headers)
    assert r.status_code == 200
    pct = r.json()["percentages"]
    assert len(pct) == len(q["options"])
    assert sum(pct) == 100
    # bias toward correct
    assert pct[q["correct_index"]] == max(pct)


# ---------- LEADERBOARD ----------
def test_leaderboard_with_tier(session, auth_headers):
    r = session.get(f"{API}/leaderboard", headers=auth_headers)
    assert r.status_code == 200
    users = r.json()
    assert len(users) >= 1
    u0 = users[0]
    assert "tier" in u0 and "id" in u0["tier"]
    assert "rank_position" in u0
    xps = [u["xp"] for u in users]
    assert xps == sorted(xps, reverse=True)


# ---------- LIVES REFILL ----------
def test_lives_refill(session, auth_headers):
    r = session.post(f"{API}/lives/refill", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["lives"] == 5
