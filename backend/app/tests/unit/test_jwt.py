from app.core.auth.credential import build_jwt, verify_jwt


def test_verify_jwt():
    token = build_jwt("e9c7c9ab-e3f7-4254-8ab2-2f3bb570b48c", "test1")
    assert verify_jwt(token)
