from fastapi import APIRouter, Depends, HTTPException, Response, status
from app.schema.users import UserSignup, UserLogin
import app.core.auth.credential as auth

from app.main import get_db_manager
from app.core.db.database_manager import DatabaseManager
from app.schema.jwt import JWTAuthResult

auth_router = APIRouter()


@auth_router.post("/signup", status_code=201)
def user_signup(
    payload: UserSignup, database_manager: DatabaseManager = Depends(get_db_manager)
):
    password = payload.password
    username = payload.username

    # check user existance
    user_exist = auth.check_username_exist(username, database_manager)
    if user_exist:
        raise HTTPException(
            status.HTTP_409_CONFLICT, {"status": "Username already exists."}
        )

    # hash password
    password_hash = auth.hash_password(password)

    # save cred in db
    user_id = auth.store_credentials(username, password_hash, database_manager)

    return {"status": "Sign up successful", "username": username}


@auth_router.post("/login", status_code=200)
def user_login(
    payload: UserLogin,
    response: Response,
    database_manager: DatabaseManager = Depends(get_db_manager),
    jwt_auth: JWTAuthResult = Depends(auth.wrapped_verify_jwt),
):
    if all(jwt_auth.payload.model_dump().values()) and jwt_auth.error == None:
        return {"status": "Already Signed In"}

    username = payload.username
    password = payload.password

    # retrieve pw_hash
    user_id, username, password_hash = auth.retrieve_pass_hash(
        username, database_manager
    )
    if not user_id:
        raise HTTPException(404, {"status": "User not found"})

    # check password against hash
    try:
        auth.check_password(password_hash, password)

    except auth.VerificationError as e:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, {"status": "Wrong password provided"}
        )

    # build and sign jwt
    jwt_token = auth.build_jwt(user_id, username)

    # set httponly cookie
    response.set_cookie(
        key="session_token",
        value=jwt_token,
        httponly=True,  # Makes the cookie inaccessible to JavaScript
        secure=True,  # Ensures cookie is only sent over HTTPS
        samesite="Strict",  # Or "Strict" / "None" depending on your use case
    )

    return {"status": "Login Successful", "username": username}
