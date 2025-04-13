from app.core.auth.jwt import verify_jwt
from app.core.auth.jwt import build_jwt


def test_verify_jwt():
    token = build_jwt("e9c7c9ab-e3f7-4254-8ab2-2f3bb570b48c", "test1")
    assert verify_jwt(token)
