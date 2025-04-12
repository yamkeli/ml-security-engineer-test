from fastapi.testclient import TestClient
from app.main import app
import secrets

client = TestClient(app)


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
