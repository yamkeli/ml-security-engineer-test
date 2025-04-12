from fastapi import APIRouter, Depends, HTTPException, status
from app.schema.users import UserSignup
import app.core.auth.credential as auth

from app.main import get_db_manager
from app.core.db.database_manager import DatabaseManager

auth_router = APIRouter()


@auth_router.post("/signup", status_code=201)
def user_signup(
    payload: UserSignup, db_manager: DatabaseManager = Depends(get_db_manager)
):
    password = payload.password
    username = payload.username

    # check user existance
    user_exist = auth.check_username_exist(username, db_manager)
    if user_exist:
        raise HTTPException(
            status.HTTP_409_CONFLICT, {"status": "Username already exists."}
        )

    # hash password
    password_hash = auth.hash_password(password)

    # save cred in db
    user_id = auth.store_credentials(username, password_hash, db_manager)

    return {"status": "Sign up successful", "username": username}
