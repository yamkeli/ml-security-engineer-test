from fastapi.testclient import TestClient
from app.main import app
import secrets

client = TestClient(app)


# ---signup---
def generate_username():
    return "test" + secrets.token_hex(16)


def test_signup_good():
    payload = {
        "username": generate_username(),
        "password": "`0#0T$ZFc{2",
        "confirm_password": "`0#0T$ZFc{2",
    }
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 201


def test_signup_user_exist():
    payload = {
        "username": "test",
        "password": "`0#0T$ZFc{2",
        "confirm_password": "`0#0T$ZFc{2",
    }
    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 409


def test_signup_bad_password():
    payload = {
        "username": generate_username(),
        "password": "qwerty",
        "confirm_password": "qwerty",
    }

    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422


def test_signup_mismatch_password():
    payload = {
        "username": generate_username(),
        "password": "`0#0T$ZFc{2",
        "confirm_password": "`0#0T$ZFc{456",
    }

    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422


def test_signup_mismatch_password():
    payload = {
        "username": generate_username(),
        "password": "`0#0T$ZFc{2",
        "confirm_password": "`0#0T$ZFc{456",
    }

    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422


def test_signup_bad_username():
    payload = {
        "username": '" or ""="',
        "password": "`0#0T$ZFc{2",
        "confirm_password": "`0#0T$ZFc{2",
    }

    response = client.post("/api/v1/auth/signup", json=payload)
    assert response.status_code == 422


# ---login---
def test_login_good_no_header():
    payload = {
        "username": "test",
        "password": "`0#0T$ZFc{2",
    }

    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 200
    assert "session_token" in response.cookies


def test_login_good_expired_header():
    payload = {
        "username": "test",
        "password": "`0#0T$ZFc{2",
    }

    response = client.post(
        "/api/v1/auth/login",
        json=payload,
        cookies={
            "session_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlOWM3YzlhYi1lM2Y3LTQyNTQtOGFiMi0yZjNiYjU3MGI0OGMiLCJuYW1lIjoidGVzdDEiLCJpYXQiOjE3NDQ0NzEzMjAsImV4cCI6MTc0NDQ3NDkyMH0.6xyx2JWNszylWDYKbYKQXe6UXWmCw4mqRiYX-ncRuPk"
        },
    )
    assert response.status_code == 200


def test_login_good_with_header():
    payload = {
        "username": "test",
        "password": "`0#0T$ZFc{2",
    }

    jwt_response = client.post("/api/v1/auth/login", json=payload)

    token = jwt_response.cookies.get("session_token")
    payload = {
        "username": "test",
        "password": "`0#0T$ZFc{2",
    }
    client.cookies
    response = client.post(
        "/api/v1/auth/login",
        json=payload,
        cookies={"session_token": token},
    )

    assert response.status_code == 200


def test_login_wrong_password():
    payload = {
        "username": "test",
        "password": "`0#0T$ZFc{3",
    }

    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 401


def test_login_no_user():
    payload = {
        "username": "noexist",
        "password": "`0#0T$ZFc{2",
    }

    response = client.post("/api/v1/auth/login", json=payload)
    assert response.status_code == 404
