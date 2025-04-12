import base64
import datetime
from typing import Literal
import uuid
from argon2 import PasswordHasher, Type
from argon2.exceptions import VerificationError
from fastapi import Request
import jwt
from jwt.exceptions import (
    InvalidSignatureError,
    ExpiredSignatureError,
    InvalidAlgorithmError,
    DecodeError,
)

from app.core.db.database_manager import DatabaseManager
from app.core.secrets.secrets_manager import get_jwt_key
from app.schema.jwt import JWTAuthResult


def hash_password(validated_password: str) -> str:
    hasher = PasswordHasher(time_cost=3, memory_cost=12288, parallelism=1, type=Type.ID)
    hashed_password = hasher.hash(validated_password)

    return hashed_password


def check_password(password_hash: str, validated_password: str) -> Literal[True]:
    try:
        hasher = PasswordHasher(
            time_cost=3, memory_cost=12288, parallelism=1, type=Type.ID
        )
        hasher.verify(password_hash, validated_password)

    except VerificationError as e:
        raise e

    except Exception as e:
        raise e

    return True


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


def check_username_exist(username: str, database_manager: DatabaseManager) -> bool:
    query = """SELECT EXISTS(SELECT 1 FROM "user" WHERE username=%s)"""

    params = [username]

    query_result = database_manager.execute_query(query, params)

    try:
        exist = query_result[0][0]
        return exist
    except:
        raise Exception


def store_credentials(
    username: str, password_hash: str, database_manager: DatabaseManager
) -> str:

    query = """INSERT INTO "user" (username, password_hash)
    VALUES (%(username)s, %(password_hash)s)
    RETURNING user_id"""

    params = {"username": username, "password_hash": password_hash}

    query_result = database_manager.execute_query(query, params)

    try:
        user_id = query_result[0][0]
        return user_id
    except:
        raise Exception


def retrieve_pass_hash(
    username: str, database_manager: DatabaseManager
) -> tuple[str, str, str]:
    query = """
    SELECT user_id, username, password_hash
    FROM "user"
    WHERE username = %s
    """

    params = [username]

    query_result = database_manager.execute_query(query, params)

    if query_result:
        return query_result[0]
    else:
        return ("", "", "")
