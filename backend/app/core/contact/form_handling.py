from datetime import date
from pydantic import EmailStr
from app.core.db.database_manager import DatabaseManager
from psycopg2.errors import UniqueViolation


def store_contact_info(
    name: str,
    dob: date,
    email: EmailStr,
    ssn_enc: bytes,
    dek_enc: bytes,
    user_id: str,
    database_manager: DatabaseManager,
):
    query = """INSERT INTO user_contact (name, email, dob, ssn_enc, dek_enc, user_id)
    VALUES (%(name)s, %(email)s, %(dob)s, %(ssn_enc)s, %(dek_enc)s, %(user_id)s)"""

    params = {
        "name": name,
        "email": email,
        "dob": dob,
        "ssn_enc": ssn_enc,
        "dek_enc": dek_enc,
        "user_id": user_id,
    }
    try:
        database_manager.execute_query(query, params, return_result=False)
    except UniqueViolation as e:
        raise e
    except Exception as e:
        raise e


def load_contact_info(
    user_id: str,
    database_manager: DatabaseManager,
):
    query = """SELECT name, email, dob, ssn_enc, dek_enc, user_id
    FROM user_contact
    WHERE user_id = %(user_id)s"""

    params = {"user_id": user_id}

    result = database_manager.execute_query(query, params)

    if result:
        return result[0]
    return ()
