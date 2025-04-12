from fastapi import Request

import datetime

from app.schema.jwt import JWTAuthResult
from app.core.secrets.secrets_manager import get_jwt_key
from app.schema.jwt import JWTAuthResult

import jwt
from jwt.exceptions import (
    DecodeError,
    ExpiredSignatureError,
    InvalidAlgorithmError,
    InvalidSignatureError,
)


def build_jwt(user_id: str, username: str) -> str:

    # Define the payload (claims)
    payload = {
        "sub": user_id,
        "name": username,
        "iat": datetime.datetime.utcnow(),  # Issued at
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(hours=1),  # Expires in 1 hour
    }

    SECRET_KEY = get_jwt_key()

    # Encode (sign) the token using HMAC-SHA256
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token


def verify_jwt(token: str) -> JWTAuthResult:
    SECRET_KEY = get_jwt_key()
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=["HS256"],
            options={"verify_exp": "verify_signature"},
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise DecodeError
        return JWTAuthResult(payload, None)
    except (
        DecodeError,
        ExpiredSignatureError,
        InvalidAlgorithmError,
        InvalidSignatureError,
    ) as e:
        return JWTAuthResult({"sub": "", "name": "", "iat": 0, "exp": 0}, error=e)


def wrapped_verify_jwt(request: Request) -> JWTAuthResult:
    token = request.cookies.get("session_token", None)
    if not token:
        return JWTAuthResult({"sub": "", "name": "", "iat": 0, "exp": 0}, DecodeError)
    return verify_jwt(token)
