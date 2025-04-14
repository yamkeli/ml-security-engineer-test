import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic_core import ValidationError
from app.schema.users import UserSignup, UserLogin
import app.core.auth.credential as auth

from app.main import get_db_manager
from app.core.db.database_manager import DatabaseManager

from app.schema.jwt import JWTAuthResult
from app.core.auth import jwt

from app.utils.utils import get_ip

auth_router = APIRouter()
logger = logging.getLogger(__name__)


@auth_router.post("/signup", status_code=201)
def user_signup(
    payload: UserSignup,
    request: Request,
    response: Response,
    database_manager: DatabaseManager = Depends(get_db_manager),
):
    try:
        # inputs are validated and sanitized through pydantic
        password = payload.password
        username = payload.username

        # check user existance
        user_exist = auth.check_username_exist(username, database_manager)
        if user_exist:
            ip = get_ip(request)
            logger.warn(f"{ip}: Existing username: {username} attempted sign up.")
            raise HTTPException(
                status.HTTP_409_CONFLICT, {"status": "Username already exists."}
            )

        # hash password
        password_hash = auth.hash_password(password)

        # save cred in db
        user_id = auth.store_credentials(username, password_hash, database_manager)

        logger.info(f"New Sign Up: {user_id} - {username}")

        # build and sign jwt
        jwt_token = jwt.build_jwt(user_id, username)

        # set httponly cookie
        response.set_cookie(
            key="session_token",
            value=jwt_token,
            httponly=True,  # Makes the cookie inaccessible to JavaScript
            secure=True,  # Ensures cookie is only sent over HTTPS
            samesite="Strict",  # For CSRF
        )

        return {"status": "Sign up successful", "username": username}

    except ValidationError as e:
        logger.error(f"Input validation failed: {e}")
        raise HTTPException(422, {"status": "Input validation failed"})

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(e)
        raise HTTPException(500, {"status": "An internal server error has occured."})


@auth_router.post("/login", status_code=200)
def user_login(
    payload: UserLogin,
    request: Request,
    response: Response,
    database_manager: DatabaseManager = Depends(get_db_manager),
    jwt_auth: JWTAuthResult = Depends(jwt.wrapped_verify_jwt),
):
    try:
        if all(jwt_auth.payload.model_dump().values()) and jwt_auth.error == None:
            return {"status": "Already Signed In"}

        username = payload.username
        password = payload.password

        # retrieve pw_hash
        user_id, username, password_hash = auth.retrieve_pass_hash(
            username, database_manager
        )
        if not user_id:
            ip = get_ip(request)
            logger.warning(f"{ip}: Attempted login with invalid username: {username}")
            raise HTTPException(404, {"status": "User not found"})

        # check password against hash
        try:
            auth.check_password(password_hash, password)

        except auth.VerificationError as e:
            ip = get_ip(request)
            logger.warning(f"{ip}: Wrong password login attempt: {username}")
            raise HTTPException(
                status.HTTP_401_UNAUTHORIZED, {"status": "Wrong password provided"}
            )

        # build and sign jwt
        jwt_token = jwt.build_jwt(user_id, username)

        # set httponly cookie
        response.set_cookie(
            key="session_token",
            value=jwt_token,
            httponly=True,  # Makes the cookie inaccessible to JavaScript
            secure=True,  # Ensures cookie is only sent over HTTPS
            samesite="Strict",  # For CSRF
        )

        logger.info(f"{username} logged in successfully.")

        return {"status": "Login Successful", "username": username}

    except ValidationError as e:
        logger.error(f"Input validation failed: {e}")
        raise HTTPException(422, {"status": "Input validation failed"})

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(e)
        raise HTTPException(500, {"status": "An internal server error has occured."})
