from app.core.auth.credential import hash_password, check_password, VerificationError
import pytest


def test_password_hashing():
    password = "0#0T$ZFc{2"

    hash = hash_password(password)

    assert hash != password
    assert check_password(hash, password)

    with pytest.raises(VerificationError):
        check_password(hash, "notthepassword")
