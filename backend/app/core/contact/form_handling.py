from datetime import date
from pydantic import EmailStr
from app.core.db.database_manager import DatabaseManager


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

    database_manager.execute_query(query, params, return_result=False)
