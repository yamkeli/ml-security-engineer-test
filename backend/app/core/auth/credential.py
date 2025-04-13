from typing import Literal

from argon2 import PasswordHasher, Type
from argon2.exceptions import VerificationError

from app.core.db.database_manager import DatabaseManager


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
