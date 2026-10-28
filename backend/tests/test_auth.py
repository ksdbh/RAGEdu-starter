from fastapi.testclient import TestClient

from backend.app.main import app

client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_whoami_unauthenticated():
    r = client.get("/whoami")
    assert r.status_code == 401


def test_student_access_student_endpoint():
    headers = {"Authorization": "Bearer student_token"}
    r = client.get("/protected/student", headers=headers)
    assert r.status_code == 200
    assert "student" in r.json().get("message", "")


def test_student_denied_professor_endpoint():
    headers = {"Authorization": "Bearer student_token"}
    r = client.get("/protected/professor", headers=headers)
    assert r.status_code == 403


def test_professor_access_professor_endpoint():
    headers = {"Authorization": "Bearer prof_token"}
    r = client.get("/protected/professor", headers=headers)
    assert r.status_code == 200
    assert "professor" in r.json().get("message", "")


def test_protected_auth_with_token():
    headers = {"Authorization": "Bearer student_token"}
    r = client.get("/protected/auth", headers=headers)
    assert r.status_code == 200
    assert "authenticated" in r.json().get("message", "")


def test_greeting_anonymous_and_authenticated():
    r = client.get("/greeting")
    assert r.status_code == 200
    assert "anonymous" in r.json().get("message", "").lower()

    r2 = client.get("/greeting", headers={"Authorization": "Bearer student_token"})
    assert r2.status_code == 200
    assert "student" in r2.json().get("message", "")

    r3 = client.get("/greeting", headers={"Authorization": "Bearer prof_token"})
    assert r3.status_code == 200
    assert "professor" in r3.json().get("message", "")


def test_roles_are_token_derived_and_independent_of_request_order():
    for token, role in [("prof_token", "professor"), ("student_token", "student")] * 3:
        headers = {"Authorization": f"Bearer {token}"}
        identity = client.get("/whoami", headers=headers)
        assert identity.status_code == 200
        assert identity.json()["role"] == role
        assert identity.json()["username"]
        expected = 200 if role == "professor" else 403
        assert client.get("/protected/professor", headers=headers).status_code == expected


def test_invalid_authorization_cannot_access_protected_routes():
    for value in ["Bearer invalid", "Basic student_token", "Bearer"]:
        for route in ["/whoami", "/protected/auth", "/protected/student", "/protected/professor"]:
            assert client.get(route, headers={"Authorization": value}).status_code == 401
