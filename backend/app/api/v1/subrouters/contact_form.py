import logging
from types import NoneType
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from pydantic_core import ValidationError

from app.main import get_db_manager
from app.core.db.database_manager import DatabaseManager

from app.core.auth import jwt
from app.core.auth.jwt import (
    ExpiredSignatureError,
    DecodeError,
    InvalidAlgorithmError,
    InvalidSignatureError,
)

from app.core.crypto import encrypt, decrypt

from app.core.contact import form_handling
from app.core.contact.form_handling import UniqueViolation

from app.schema.form import UserContactForm
from app.schema.jwt import JWTAuthResult

from app.utils.utils import get_ip

contact_router = APIRouter()
logger = logging.getLogger(__name__)


@contact_router.post("/submit", status_code=201)
def submit_form(
    payload: UserContactForm,
    request: Request,
    database_manager: DatabaseManager = Depends(get_db_manager),
    jwt_auth: JWTAuthResult = Depends(jwt.wrapped_verify_jwt),
):

    try:
        # jwt state check
        if not all(jwt_auth.payload.model_dump().values()):
            ip = get_ip(request)
            if isinstance(jwt_auth.error, ExpiredSignatureError):
                logger.warning(
                    f"{ip}: Expired token used by user_id: {jwt_auth.payload.sub}"
                )
                raise HTTPException(401, {"status": "Error in authenticating."})

            if isinstance(jwt_auth.error, DecodeError):
                logger.warning(f"{ip}: Token error user_id: {jwt_auth.payload.sub}")
                raise HTTPException(401, {"status": "Error in authenticating."})

            if isinstance(
                jwt_auth.error, (InvalidAlgorithmError, InvalidSignatureError)
            ):
                logger.warning(
                    f"{ip}: Invalid token used by user_id: {jwt_auth.payload.sub}"
                )
                raise HTTPException(401, {"status": "Error in authenticating."})

            if isinstance(jwt_auth.error, NoneType):
                logger.warning(f"{ip}: No token sent, user_id: {jwt_auth.payload.sub}")
                raise HTTPException(401, {"status": "Error in authenticating."})

        # payload content
        name = payload.name
        email = payload.email
        ssn = payload.ssn
        dob = payload.dob
        # from verified jwt
        user_id = jwt_auth.payload.sub

        # encrypt ssn, get encrypted ssn and encrypted dek
        ssn_enc, dek_enc = encrypt.encryption(ssn)
        try:
            form_handling.store_contact_info(
                name, dob, email, ssn_enc, dek_enc, user_id, database_manager
            )
        except UniqueViolation as e:
            ip = get_ip(request)
            logger.warning(f"{ip}: User_id {user_id} attempt to upload contact again.")
            raise HTTPException(409, {"status": "Contact info already uploaded."})

        logger.warning(f"User_id {user_id} succesfully uploaded contact info")
        return {"status": "Contact Info Uploaded"}

    except ValidationError as e:
        logger.error(f"Input validation failed: {e}")
        raise HTTPException(422, {"status": "Input validation failed"})

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(e)
        raise HTTPException(500, {"status": "An internal server error has occured."})


@contact_router.get("/load", status_code=200)
def load_contact_info(
    request: Request,
    database_manager: DatabaseManager = Depends(get_db_manager),
    jwt_auth: JWTAuthResult = Depends(jwt.wrapped_verify_jwt),
):
    try:
        # jwt state check
        if not all(jwt_auth.payload.model_dump().values()):
            ip = get_ip(request)
            if isinstance(jwt_auth.error, ExpiredSignatureError):
                logger.warning(
                    f"{ip}: Expired token used by user_id: {jwt_auth.payload.sub}"
                )
                raise HTTPException(401, {"status": "Error in authenticating."})

            if isinstance(jwt_auth.error, DecodeError):
                logger.warning(f"{ip}: Token error user_id: {jwt_auth.payload.sub}")
                raise HTTPException(401, {"status": "Error in authenticating."})

            if isinstance(
                jwt_auth.error, (InvalidAlgorithmError, InvalidSignatureError)
            ):
                logger.warning(
                    f"{ip}: Invalid token used by user_id: {jwt_auth.payload.sub}"
                )
                raise HTTPException(401, {"status": "Error in authenticating."})

            if isinstance(jwt_auth.error, NoneType):
                raise HTTPException(401, {"status": "Error in authenticating."})

        # from verified jwt
        user_id = jwt_auth.payload.sub

        # retrieve info
        name, email, dob, ssn_enc, dek_enc, user_id = form_handling.load_contact_info(
            user_id, database_manager
        )

        if not name:
            return None

        ssn = decrypt.decryption(bytes(ssn_enc), bytes(dek_enc))

        logger.info(f"User_id {user_id} loaded contact info.")

        return {"name": name, "email": email, "dob": dob, "ssn": ssn}

    except ValidationError as e:
        logger.error(f"Input validation failed: {e}")
        raise HTTPException(422, {"status": "Input validation failed"})

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(e)
        raise HTTPException(500, {"status": "An internal server error has occured."})
