from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def login():
    jwt_payload = {
        "username": "test",
        "password": "`0#0T$ZFc{2",
    }

    jwt_response = client.post("/api/v1/auth/login", json=jwt_payload)

    token = jwt_response.cookies.get("session_token")

    return token


token = login()

expired_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlOWM3YzlhYi1lM2Y3LTQyNTQtOGFiMi0yZjNiYjU3MGI0OGMiLCJuYW1lIjoidGVzdDEiLCJpYXQiOjE3NDQ0NzEzMjAsImV4cCI6MTc0NDQ3NDkyMH0.6xyx2JWNszylWDYKbYKQXe6UXWmCw4mqRiYX-ncRuPk"
bad_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlOWM3YzlhYi1lM2Y3LTQyNTQtOGFiMi0yZjNiYjU3MGI0OGMiLCJuYW1lIjoidGVzdDEiLCJpYXQiOjE3NDQ0NzEzMjAsImV4cCI6MTc0NDQ3NDkyMH0.6xyx2JWNszylWDYKbYKQXe6UXWmCw4mqRiYX-ncRukP"


def test_submit_already_exist():

    form_payload = {
        "name": "Test Tester",
        "dob": "1999-10-07",
        "email": "email@domain.com",
        "ssn": "123-45-6789",
    }
    client.cookies.set("session_token", token)
    form_response = client.post("/api/v1/form/submit", json=form_payload)

    assert form_response.status_code == 409


def test_submit_expired_jwt():
    form_payload = {
        "name": "Test Tester",
        "dob": "1999-10-07",
        "email": "email@domain.com",
        "ssn": "123-45-6789",
    }
    client.cookies.set("session_token", expired_token)
    form_response = client.post("/api/v1/form/submit", json=form_payload)

    assert form_response.status_code == 401
    assert form_response.json() == {"detail": {"status": "Token is expired."}}


def test_submit_bad_jwt():
    form_payload = {
        "name": "Test Tester",
        "dob": "1999-10-07",
        "email": "email@domain.com",
        "ssn": "123-45-6789",
    }
    client.cookies.set("session_token", bad_token)
    form_response = client.post("/api/v1/form/submit", json=form_payload)

    assert form_response.status_code == 400


def test_submit_bad_name():
    form_payload = {
        "name": "<scripts src=''>Tester",
        "dob": "1999-10-07",
        "email": "email@domain.com",
        "ssn": "123-45-6789",
    }
    client.cookies.set("session_token", token)
    form_response = client.post("/api/v1/form/submit", json=form_payload)

    assert form_response.status_code == 422


def test_submit_bad_dob():
    form_payload = {
        "name": "Test Tester",
        "dob": "Oct 7 1999",
        "email": "email@domain.com",
        "ssn": "123-45-6789",
    }
    client.cookies.set("session_token", token)
    form_response = client.post("/api/v1/form/submit", json=form_payload)

    assert form_response.status_code == 422


def test_submit_bad_email():
    form_payload = {
        "name": "Test Tester",
        "dob": "1999-10-07",
        "email": "<scripts src=''>@domain.com",
        "ssn": "123-45-6789",
    }
    client.cookies.set("session_token", token)
    form_response = client.post("/api/v1/form/submit", json=form_payload)

    assert form_response.status_code == 422


def test_submit_bad_ssn():
    form_payload = {
        "name": "Test Tester",
        "dob": "1999-10-07",
        "email": "email@domain.com",
        "ssn": "1234-5-6887",
    }
    client.cookies.set("session_token", token)
    form_response = client.post("/api/v1/form/submit", json=form_payload)

    assert form_response.status_code == 422


# ---load---
def test_load_form():
    client.cookies.set("session_token", token)
    form_response = client.get("/api/v1/form/load")

    assert form_response.status_code == 200
    required_keys = ("name", "email", "dob", "ssn")
    assert all(k in form_response.json() for k in required_keys)
